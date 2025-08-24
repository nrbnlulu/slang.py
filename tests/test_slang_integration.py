"""Integration tests for slang with temporary project setups."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from slang import generate_translations
from slang.config import SlangConfig


class TestSlangIntegration:
    """Test slang with complete temporary project setups."""

    def create_temp_project(
        self,
        tmp_path: Path,
        config: dict | None = None,
        translations: dict[str, dict] | None = None,
    ) -> Path:
        """Create a temporary project with pyproject.toml and translation files."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Create pyproject.toml
        pyproject_content: dict[str, Any] = {
            "project": {"name": "test-project", "version": "0.1.0"}
        }

        if config:
            pyproject_content["tool"] = {"slang": config}

        with open(project_dir / "pyproject.toml", "wb") as f:
            import tomli_w

            tomli_w.dump(pyproject_content, f)

        # Create translations if provided
        if translations:
            config_obj = SlangConfig()
            if config:
                config_obj.output_dir = config.get("output_dir", "slang/gen")
                config_obj.translations_dir = config.get(
                    "translations_dir", "translations"
                )
                config_obj.main_language = config.get("main_language", "en")

            translations_dir = project_dir / config_obj.translations_dir
            translations_dir.mkdir(parents=True)

            for lang_code, content in translations.items():
                translation_file = translations_dir / f"{lang_code}.yml"
                with open(translation_file, "w") as f:
                    yaml.dump(content, f, default_flow_style=False, allow_unicode=True)

        return project_dir

    def test_basic_translation_generation(self, tmp_path):
        """Test basic translation generation with default config."""
        translations = {
            "en": {
                "hello": "Hello",
                "goodbye": "Goodbye",
                "welcome": "Welcome {name}!",
            },
            "es": {
                "hello": "Hola",
                "goodbye": "Adiós",
                "welcome": "¡Bienvenido {name}!",
            },
        }

        project_dir = self.create_temp_project(tmp_path, translations=translations)

        result = generate_translations(project_dir)
        assert result.is_ok(), f"Generation failed: {result.err()}"

        code = result.unwrap()

        # Check that the generated code contains expected elements
        assert "class Languages(Enum)" in code
        assert 'EN = "en"' in code
        assert 'ES = "es"' in code
        assert "class TranslationsProto(Protocol)" in code
        assert "def get_translations(language: Languages)" in code
        assert "class Translations_en(TranslationsProto)" in code
        assert "class Translations_es(TranslationsProto)" in code

    def test_custom_config(self, tmp_path):
        """Test with custom configuration."""
        config = {
            "output_dir": "generated/i18n",
            "translations_dir": "locales",
            "main_language": "fr",
        }

        translations = {
            "fr": {"bonjour": "Bonjour", "au_revoir": "Au revoir"},
            "en": {"bonjour": "Hello", "au_revoir": "Goodbye"},
        }

        project_dir = self.create_temp_project(
            tmp_path, config=config, translations=translations
        )

        result = generate_translations(project_dir)
        assert result.is_ok()

        code = result.unwrap()
        assert 'FR = "fr"' in code
        assert 'EN = "en"' in code

    def test_nested_translations(self, tmp_path):
        """Test nested translation structures."""
        translations = {
            "en": {
                "auth": {
                    "login": {"title": "Log In", "button": "Sign In"},
                    "register": {"title": "Sign Up", "button": "Create Account"},
                },
                "home": {"welcome": "Welcome back, {username}!"},
            },
            "es": {
                "auth": {
                    "login": {"title": "Iniciar Sesión", "button": "Entrar"},
                    "register": {"title": "Registrarse", "button": "Crear Cuenta"},
                },
                "home": {"welcome": "¡Bienvenido de nuevo, {username}!"},
            },
        }

        project_dir = self.create_temp_project(tmp_path, translations=translations)

        result = generate_translations(project_dir)
        assert result.is_ok()

    def test_missing_keys_validation(self, tmp_path):
        """Test that missing keys in secondary languages are caught."""
        translations = {
            "en": {"hello": "Hello", "goodbye": "Goodbye", "welcome": "Welcome"},
            "es": {
                "hello": "Hola",
                # "goodbye" is missing
                "welcome": "Bienvenido",
            },
        }

        project_dir = self.create_temp_project(tmp_path, translations=translations)

        result = generate_translations(project_dir)
        assert result.is_err()
        error_msg = result.err()
        assert error_msg is not None
        assert "missing keys" in error_msg.lower()
        assert "goodbye" in error_msg

    def test_extra_keys_validation(self, tmp_path):
        """Test that extra keys in secondary languages are caught."""
        translations = {
            "en": {"hello": "Hello", "goodbye": "Goodbye"},
            "es": {
                "hello": "Hola",
                "goodbye": "Adiós",
                "extra_key": "Extra",  # This shouldn't be here
            },
        }

        project_dir = self.create_temp_project(tmp_path, translations=translations)

        result = generate_translations(project_dir)
        assert result.is_err()
        error_msg = result.err()
        assert error_msg is not None
        assert "extra keys" in error_msg.lower()
        assert "extra_key" in error_msg

    def test_missing_main_language(self, tmp_path):
        """Test error when main language file is missing."""
        config = {"main_language": "fr"}
        translations = {
            "en": {"hello": "Hello"},
            "es": {"hello": "Hola"},
            # fr is missing
        }

        project_dir = self.create_temp_project(
            tmp_path, config=config, translations=translations
        )

        result = generate_translations(project_dir)
        assert result.is_err()
        error_msg = result.err()
        assert error_msg is not None
        assert "Main language 'fr' not found" in error_msg

    def test_no_translations_directory(self, tmp_path):
        """Test error when translations directory doesn't exist."""
        project_dir = self.create_temp_project(tmp_path)

        result = generate_translations(project_dir)
        assert result.is_err()
        error_msg = result.err()
        assert error_msg is not None
        assert "does not exist" in error_msg

    def test_empty_translations_directory(self, tmp_path):
        """Test error when translations directory is empty."""
        project_dir = self.create_temp_project(tmp_path)
        (project_dir / "translations").mkdir()

        result = generate_translations(project_dir)
        assert result.is_err()
        error_msg = result.err()
        assert error_msg is not None
        assert "No YAML translation files found" in error_msg

    def test_invalid_yaml(self, tmp_path):
        """Test error handling for invalid YAML files."""
        project_dir = self.create_temp_project(tmp_path)
        translations_dir = project_dir / "translations"
        translations_dir.mkdir()

        # Create invalid YAML file
        with open(translations_dir / "en.yml", "w") as f:
            f.write("invalid: yaml: content: [\n")  # Broken YAML

        result = generate_translations(project_dir)
        assert result.is_err()
        error_msg = result.err()
        assert error_msg is not None
        assert "YAML parsing error" in error_msg

    def test_complex_field_parameters(self, tmp_path):
        """Test complex fields with parameters."""
        translations = {
            "en": {
                "greet(name: str, age: int)": "Hello {name}, you are {age} years old!",
                "items(count: int)": "You have {count} items",
            },
            "es": {
                "greet(name: str, age: int)": "¡Hola {name}, tienes {age} años!",
                "items(count: int)": "Tienes {count} elementos",
            },
        }

        project_dir = self.create_temp_project(tmp_path, translations=translations)

        result = generate_translations(project_dir)
        assert result.is_ok()

        code = result.unwrap()
        # Check that parameter types are preserved
        assert "name: str, age: int" in code
        assert "count: int" in code

    def test_language_code_normalization(self, tmp_path):
        """Test that language codes with special characters are normalized properly."""
        config = {"main_language": "en-US"}
        translations = {
            "en-US": {"hello": "Hello (US)"},
            "zh-CN": {"hello": "你好"},
            "pt-BR": {"hello": "Olá (Brasil)"},
        }

        project_dir = self.create_temp_project(
            tmp_path, config=config, translations=translations
        )

        result = generate_translations(project_dir)
        assert result.is_ok()

        code = result.unwrap()
        # Check normalized enum names
        assert 'EN_US = "en-US"' in code
        assert 'ZH_CN = "zh-CN"' in code
        assert 'PT_BR = "pt-BR"' in code
        # Check normalized class names
        assert "class Translations_en_US" in code
        assert "class Translations_zh_CN" in code
        assert "class Translations_pt_BR" in code

    def test_config_loading_from_parent_directory(self, tmp_path):
        """Test that config is found in parent directories."""
        # Create nested project structure
        root_dir = tmp_path / "project_root"
        root_dir.mkdir()

        # pyproject.toml in root
        config = {"main_language": "de", "translations_dir": "i18n"}

        pyproject_content: dict[str, Any] = {
            "project": {"name": "test", "version": "0.1.0"},
            "tool": {"slang": config},
        }

        with open(root_dir / "pyproject.toml", "wb") as f:
            import tomli_w

            tomli_w.dump(pyproject_content, f)

        # Translations in subdirectory
        i18n_dir = root_dir / "i18n"
        i18n_dir.mkdir()

        translations = {"de": {"hallo": "Hallo Welt"}, "en": {"hallo": "Hello World"}}

        for lang, content in translations.items():
            with open(i18n_dir / f"{lang}.yml", "w") as f:
                yaml.dump(content, f)

        # Run from subdirectory
        sub_dir = root_dir / "src"
        sub_dir.mkdir()

        result = generate_translations(root_dir)
        assert result.is_ok()

    def test_no_config_uses_defaults(self, tmp_path):
        """Test that missing config file uses sensible defaults."""
        project_dir = tmp_path / "no_config_project"
        project_dir.mkdir()

        # No pyproject.toml file
        translations_dir = project_dir / "translations"  # default
        translations_dir.mkdir()

        translations = {
            "en": {"test": "Test"},  # default main language
            "fr": {"test": "Test"},
        }

        for lang, content in translations.items():
            with open(translations_dir / f"{lang}.yml", "w") as f:
                yaml.dump(content, f)

        result = generate_translations(project_dir)
        assert result.is_ok()

    def test_generated_code_structure(self, tmp_path):
        """Test the structure and content of generated code."""
        translations = {
            "en": {
                "simple": "Simple text",
                "complex(name: str)": "Hello {name}!",
                "nested": {"title": "Nested Title", "content": "Nested Content"},
            }
        }

        project_dir = self.create_temp_project(tmp_path, translations=translations)

        result = generate_translations(project_dir)
        assert result.is_ok()

        code = result.unwrap()

        # Verify structure
        lines = code.split("\n")

        # Should have imports
        assert any("from enum import Enum" in line for line in lines)

        # Should have Languages enum
        enum_section = False
        for line in lines:
            if "class Languages(Enum)" in line:
                enum_section = True
            if enum_section and 'EN = "en"' in line:
                break
        else:
            pytest.fail("Languages enum not found properly")

        # Should have protocol
        assert any("class TranslationsProto(Protocol)" in line for line in lines)

        # Should have implementation
        assert any("class Translations_en(TranslationsProto)" in line for line in lines)

        # Should have get_translations function
        assert any(
            "def get_translations(language: Languages)" in line for line in lines
        )
