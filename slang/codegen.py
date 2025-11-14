from minijinja import Environment
from typing import Dict

from slang.types_ import SlangCtx, LocaleImpl

macros = """
{% macro render_field_signature(field, return_stmt) -%}
{% if field.is_simple -%}
    @property
    def {{ field.name }}(self) -> str:
        {{ return_stmt }}
{% elif field.is_complex -%}
    def {{ field.name }}(self,
    {%- for arg in field.arguments -%}
        {{ arg.name }}: {{ arg.type.as_py }}{% if not loop.last %}, {% endif %}
    {%- endfor -%}
    ) -> str:
        {{ return_stmt }}
{% elif field.is_namespace %}
    @property
    def {{ field.name }}(self) -> {{ field.proto_name }}:
        {{ return_stmt }}
{% endif -%}
{%- endmacro %}
"""

base_tr_proto = """
{%- from "macros" import render_field_signature %}

{% for ns_field in locale.all_namespace_fields -%}
class {{ ns_field.proto_name }}(Protocol):

    {% for field in ns_field.fields -%}
    {{ render_field_signature(field, "raise NotImplementedError()") }}
    {% endfor %}
{% endfor -%}


class TranslationsProto(Protocol):
    {% for ns_field in locale.get_root().fields -%}
    {{ render_field_signature(ns_field, "raise NotImplementedError()") }}
    {% endfor %}

"""

languages_enum_template = """class Languages(Enum):
    \"\"\"Available languages for translations.\"\"\"
{% for enum_name, lang_code in languages %}
    {{ enum_name }} = "{{ lang_code }}"
{% endfor %}
"""

implementation_template = """
class {{ class_name }}({{ base_class }}):
{% if methods %}
{% for method in methods %}
{{ method }}
{% endfor %}
{% else %}
    pass
{% endif %}
"""

get_translations_template = """
def get_translations(language: Languages) -> TranslationsProto:
    \"\"\"Get translations for the specified language.

    Args:
        language: The language to get translations for

    Returns:
        Translations instance for the specified language
    \"\"\"
    match language:
{% for enum_name, class_name in language_mappings %}
        case Languages.{{ enum_name }}:
            return {{ class_name }}()
{% endfor %}

    raise ValueError(f"Unsupported language: {language}")
"""


def error_callback(x):
    raise ValueError(x)


tem_env = Environment(
    templates={
        "translations_proto": base_tr_proto,
        "macros": macros,
        "languages_enum": languages_enum_template,
        "implementation": implementation_template,
        "get_translations": get_translations_template,
    }
)


def render_translations_proto(ctx: SlangCtx) -> str:
    return tem_env.render_template("translations_proto", locale=ctx.ref_locale)


def render_languages_enum(languages: list[str]) -> str:
    """Render the Languages enum."""
    # Transform language codes to valid Python enum names
    enum_languages = []
    for lang_code in sorted(languages):
        enum_name = lang_code.replace("-", "_").replace(".", "_").upper()
        enum_languages.append((enum_name, lang_code))

    return tem_env.render_template("languages_enum", languages=enum_languages)


def render_implementation(class_name: str, locale_impl: LocaleImpl, ref_locale: LocaleImpl) -> str:
    """Render implementation classes for a locale using reference locale protocols."""
    from .types_ import SimpleField, ComplexField, NameSpaceField

    all_classes = []

    # Generate all nested namespace implementation classes first
    # Map current locale fields to reference locale fields for protocol names
    # Use relative path (without locale prefix) for matching across languages
    def get_relative_path(full_name: str) -> str:
        # Convert "Locale_en.app.settings" to "app.settings"
        if "." in full_name:
            return ".".join(full_name.split(".")[1:])
        else:
            # Handle case where it's just "Locale_en" -> ""
            return ""

    ref_ns_fields_map = {
        get_relative_path(ns.full_name): ns for ns in ref_locale.all_namespace_fields
    }

    for ns_field in locale_impl.all_namespace_fields:
        relative_path = get_relative_path(ns_field.full_name)
        ref_ns_field = ref_ns_fields_map.get(relative_path)
        if not ref_ns_field:
            continue  # Skip if not found in reference locale
        methods = []
        for field in ns_field.fields:
            if field.is_simple and isinstance(field, SimpleField):
                method = f"""    @property
    def {field.name}(self) -> str:
        return {repr(field.value)}"""
                methods.append(method)
            elif field.is_complex and isinstance(field, ComplexField):
                args = ", ".join(f"{arg.name}: {arg.type.as_py}" for arg in field.arguments)
                # Generate template substitution code
                format_args = ", ".join(f"{arg.name}={arg.name}" for arg in field.arguments)
                method = f"""    def {field.name}(self, {args}) -> str:
        return {repr(field.template)}.format({format_args})"""
                methods.append(method)
            elif field.is_namespace and isinstance(field, NameSpaceField):
                # Find corresponding reference field for protocol name
                ref_field = None
                for ref_field_candidate in ref_ns_field.fields:
                    if ref_field_candidate.name == field.name and isinstance(
                        ref_field_candidate, NameSpaceField
                    ):
                        ref_field = ref_field_candidate
                        break
                if ref_field:
                    method = f"""    @property
    def {field.name}(self) -> {ref_field.proto_name}:
        return {field.class_name}()"""
                    methods.append(method)

        ns_class = tem_env.render_template(
            "implementation",
            class_name=ns_field.class_name,
            methods=methods,
            base_class=ref_ns_field.proto_name,
        )
        all_classes.append(ns_class)

    # Generate the main implementation class
    methods = []
    ref_root_fields_map = {f.name: f for f in ref_locale.get_root().fields}

    if locale_impl.root:
        for field in locale_impl.root.fields:
            if field.is_simple and isinstance(field, SimpleField):
                method = f"""    @property
    def {field.name}(self) -> str:
        return {repr(field.value)}"""
                methods.append(method)
            elif field.is_complex and isinstance(field, ComplexField):
                args = ", ".join(f"{arg.name}: {arg.type.as_py}" for arg in field.arguments)
                # Generate template substitution code
                format_args = ", ".join(f"{arg.name}={arg.name}" for arg in field.arguments)
                method = f"""    def {field.name}(self, {args}) -> str:
        return {repr(field.template)}.format({format_args})"""
                methods.append(method)
            elif field.is_namespace and isinstance(field, NameSpaceField):
                # Use reference locale protocol name
                ref_field = ref_root_fields_map.get(field.name)
                if ref_field and isinstance(ref_field, NameSpaceField):
                    method = f"""    @property
    def {field.name}(self) -> {ref_field.proto_name}:
        return {field.class_name}()"""
                    methods.append(method)

    main_class = tem_env.render_template(
        "implementation",
        class_name=class_name,
        methods=methods,
        base_class="TranslationsProto",
    )
    all_classes.append(main_class)

    return "\n\n".join(all_classes)


def render_get_translations(translations: Dict[str, LocaleImpl]) -> str:
    """Render the get_translations function."""
    language_mappings = []
    for lang_code in translations.keys():
        enum_name = lang_code.replace("-", "_").replace(".", "_").upper()
        class_name = f"Translations_{lang_code.replace('-', '_').replace('.', '_')}"
        language_mappings.append((enum_name, class_name))

    return tem_env.render_template("get_translations", language_mappings=language_mappings)
