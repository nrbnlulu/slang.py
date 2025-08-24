"""Slang - Type-safe i18n solution using YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict
from result import Result, Ok, Err

from .config import SlangConfig
from .loader import TranslationLoader
from .types_ import LocaleImpl, SlangCtx
from .codegen import (
    render_translations_proto,
    render_languages_enum,
    render_implementation,
    render_get_translations,
)


def generate_translations(project_path: Path | None = None) -> Result[Path, str]:
    """
    Generate type-safe translation interfaces from YAML files.

    Args:
        project_path: Path to the project root (default: current working directory)

    Returns:
        Result containing the generated Python code or error message
    """
    if project_path is None:
        project_path = Path.cwd()

    # Load configuration
    config = SlangConfig.load_from_pyproject(project_path)
    config.validate()

    # Load translations
    loader = TranslationLoader(config, project_path)
    translations_result = loader.load_all_translations()

    if translations_result.is_err():
        return Err(translations_result.err() or "Unknown error")

    translations = translations_result.unwrap()

    # Generate the code
    try:
        code = _generate_code(translations, config)
        output_file = config.output_dir / "translations.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(code)
        return Ok(None)
    except Exception as e:
        return Err(f"Code generation failed: {e}")


def _generate_code(translations: Dict[str, LocaleImpl], config: SlangConfig) -> str:
    """Generate the complete Python code for translations."""

    # Generate Languages enum
    languages_enum = render_languages_enum(list(translations.keys()))

    # Generate Translations protocol using existing codegen
    main_locale = translations[config.main_language]
    ctx = SlangCtx(ref_locale=main_locale)
    translations_proto = render_translations_proto(ctx)

    # Generate implementation classes
    implementations = []
    for lang_code, locale_impl in translations.items():
        class_name = f"Translations_{lang_code.replace('-', '_').replace('.', '_')}"
        impl_code = render_implementation(class_name, locale_impl, main_locale)
        implementations.append(impl_code)

    # Generate get_translations function
    get_translations_func = render_get_translations(translations)

    # Combine all parts with proper ordering
    # Start with future imports, then enum imports and enum, then protocols, then implementations
    future_import = "from __future__ import annotations"

    # Remove the future import from translations_proto since we're adding it at the top
    translations_proto_clean = translations_proto.replace(
        "from __future__ import annotations\n", ""
    ).strip()

    parts = (
        [
            future_import,
            languages_enum,
            "from typing import Protocol",
            translations_proto_clean,
        ]
        + implementations
        + [get_translations_func]
    )

    return "\n\n".join(parts)


__all__ = ["generate_translations", "SlangConfig", "TranslationLoader"]
