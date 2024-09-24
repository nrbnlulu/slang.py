from minijinja import Environment

from slang.types_ import SlangCtx, LocaleImpl

macros = \
"""
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
from __future__ import annotations
from typing import Protocol

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
def error_callback(x):
    raise ValueError(x)
tem_env = Environment(templates={"translations_proto": base_tr_proto, "macros": macros})


def render_translations_proto(ctx: SlangCtx) -> str:
    return tem_env.render_template("translations_proto", locale=ctx.ref_locale)