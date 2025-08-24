"""Translation file loader with YAML support and validation."""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict, Set
from result import Result, Ok, Err

from .types_ import LocaleImpl, NameSpaceField
from .parse import parse
from .config import SlangConfig


class TranslationLoader:
    """Loads and validates translation files."""

    def __init__(self, config: SlangConfig, base_path: Path | None = None):
        self.config = config
        self.base_path = base_path or Path.cwd()
        self.translations_path = config.get_translations_path(self.base_path)

    def load_all_translations(self) -> Result[Dict[str, LocaleImpl], str]:
        """Load all translation files and validate consistency."""
        if not self.translations_path.exists():
            return Err(f"Translations directory '{self.translations_path}' does not exist")

        # Find all YAML files
        yaml_files = list(self.translations_path.glob("*.yml")) + list(
            self.translations_path.glob("*.yaml")
        )

        if not yaml_files:
            return Err(f"No YAML translation files found in '{self.translations_path}'")

        # Load each translation file
        translations: Dict[str, LocaleImpl] = {}
        main_keys: Set[str] = set()

        for yaml_file in yaml_files:
            # Extract language code from filename
            lang_code = yaml_file.stem

            # Load the YAML file
            load_result = self._load_yaml_file(yaml_file, lang_code)
            if load_result.is_err():
                return Err(f"Failed to load {yaml_file}: {load_result.err()}")

            locale_impl = load_result.unwrap()
            translations[lang_code] = locale_impl

            # Collect keys from main language
            if lang_code == self.config.main_language:
                main_keys = self._collect_keys(locale_impl)

        # Validate all translations have the same keys as main language
        if main_keys:
            validation_result = self._validate_translations(translations, main_keys)
            if validation_result.is_err():
                return Err(validation_result.err() or "Validation failed")

        if not translations:
            return Err("No translations loaded")

        # Ensure main language exists
        if self.config.main_language not in translations:
            return Err(f"Main language '{self.config.main_language}' not found in translations")

        return Ok(translations)

    def _load_yaml_file(self, file_path: Path, lang_code: str) -> Result[LocaleImpl, str]:
        """Load a single YAML translation file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)

            if content is None:
                content = {}

            if not isinstance(content, dict):
                return Err(
                    f"Translation file must contain a YAML object/dictionary, got {type(content).__name__}"
                )

            # Use existing parse function to convert to LocaleImpl
            return parse(content, lang_code)

        except yaml.YAMLError as e:
            return Err(f"YAML parsing error: {e}")
        except FileNotFoundError:
            return Err(f"File not found: {file_path}")
        except Exception as e:
            return Err(f"Unexpected error loading file: {e}")

    def _collect_keys(self, locale_impl: LocaleImpl) -> Set[str]:
        """Collect all translation keys from a locale implementation."""
        keys = set()
        if locale_impl.root:
            self._collect_keys_recursive(locale_impl.root, "", keys)
        return keys

    def _collect_keys_recursive(self, field, prefix: str, keys: Set[str]) -> None:
        """Recursively collect keys from a field."""
        if isinstance(field, NameSpaceField):
            for child_field in field.fields:
                field_name = f"{prefix}.{child_field.name}" if prefix else child_field.name
                if child_field.is_simple or child_field.is_complex:
                    keys.add(field_name)
                elif child_field.is_namespace:
                    self._collect_keys_recursive(child_field, field_name, keys)

    def _validate_translations(
        self, translations: Dict[str, LocaleImpl], main_keys: Set[str]
    ) -> Result[None, str]:
        """Validate that all translations have the same keys."""
        errors = []

        for lang_code, locale_impl in translations.items():
            if lang_code == self.config.main_language:
                continue

            lang_keys = self._collect_keys(locale_impl)

            # Check for missing keys
            missing_keys = main_keys - lang_keys
            if missing_keys:
                errors.append(f"Language '{lang_code}' is missing keys: {sorted(missing_keys)}")

            # Check for extra keys
            extra_keys = lang_keys - main_keys
            if extra_keys:
                errors.append(f"Language '{lang_code}' has extra keys: {sorted(extra_keys)}")

        if errors:
            return Err("Translation key validation failed:\n" + "\n".join(errors))

        return Ok(None)

    def get_available_languages(self) -> list[str]:
        """Get list of available language codes."""
        if not self.translations_path.exists():
            return []

        yaml_files = list(self.translations_path.glob("*.yml")) + list(
            self.translations_path.glob("*.yaml")
        )
        return [f.stem for f in yaml_files]
