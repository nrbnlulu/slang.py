"""Demo script showing slang code generation."""
from __future__ import annotations

import tempfile
import yaml
from pathlib import Path

from slang import generate_translations


def main():
    """Demonstrate slang code generation."""
    print("🌐 Slang Translation Generator Demo")
    print("=" * 40)

    # Create a temporary project
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "demo_project"
        project_dir.mkdir()

        # Create pyproject.toml
        pyproject_content = """[project]
name = "demo-project"
version = "0.1.0"

[tool.slang]
output_dir = "generated"
translations_dir = "i18n"
main_language = "en"
"""

        with open(project_dir / "pyproject.toml", "w") as f:
            f.write(pyproject_content)

        # Create translations directory
        i18n_dir = project_dir / "i18n"
        i18n_dir.mkdir()

        # Create English translations
        en_translations = {
            "welcome": "Welcome to our app!",
            "greeting": "Hello, {name}!",
            "auth": {
                "login": {
                    "title": "Sign In",
                    "button": "Log In",
                    "forgot_password": "Forgot Password?"
                },
                "register": {
                    "title": "Create Account",
                    "button": "Sign Up"
                }
            },
            "items": {
                "count(count: int)": "You have {count} items",
                "empty": "No items found"
            }
        }

        # Create Spanish translations
        es_translations = {
            "welcome": "¡Bienvenido a nuestra aplicación!",
            "greeting": "¡Hola, {name}!",
            "auth": {
                "login": {
                    "title": "Iniciar Sesión",
                    "button": "Entrar",
                    "forgot_password": "¿Olvidaste tu contraseña?"
                },
                "register": {
                    "title": "Crear Cuenta",
                    "button": "Registrarse"
                }
            },
            "items": {
                "count(count: int)": "Tienes {count} elementos",
                "empty": "No se encontraron elementos"
            }
        }

        # Write translation files
        with open(i18n_dir / "en.yml", "w") as f:
            yaml.dump(en_translations, f, default_flow_style=False, allow_unicode=True)

        with open(i18n_dir / "es.yml", "w") as f:
            yaml.dump(es_translations, f, default_flow_style=False, allow_unicode=True)

        print("📁 Created demo project structure:")
        print(f"   {project_dir}/")
        print("   ├── pyproject.toml")
        print("   └── i18n/")
        print("       ├── en.yml")
        print("       └── es.yml")
        print()

        print("📝 Translation file contents:")
        print("English (en.yml):")
        with open(i18n_dir / "en.yml", "r") as f:
            content = f.read()
            for line in content.split('\n')[:10]:  # Show first 10 lines
                print(f"   {line}")
        print("   ...")
        print()

        # Generate code
        print("⚡ Generating type-safe Python code...")
        result = generate_translations(project_dir)

        if result.is_err():
            print(f"❌ Error: {result.err()}")
            return

        generated_code = result.unwrap()
        print("✅ Code generation successful!")
        print()

        print("📄 Generated Python code:")
        print("-" * 60)
        print(generated_code)
        print("-" * 60)

        print()
        print("🎯 Usage example:")
        print("```python")
        print("from generated_translations import Languages, get_translations")
        print()
        print("# Get English translations")
        print("t_en = get_translations(Languages.EN)")
        print('print(t_en.welcome)  # "Welcome to our app!"')
        print('print(t_en.greeting(name="Alice"))  # "Hello, Alice!"')
        print('print(t_en.auth.login.title)  # "Sign In"')
        print('print(t_en.items.count(count=5))  # "You have 5 items"')
        print()
        print("# Get Spanish translations")
        print("t_es = get_translations(Languages.ES)")
        print('print(t_es.welcome)  # "¡Bienvenido a nuestra aplicación!"')
        print('print(t_es.greeting(name="Alice"))  # "¡Hola, Alice!"')
        print('print(t_es.auth.login.title)  # "Iniciar Sesión"')
        print('print(t_es.items.count(count=5))  # "Tienes 5 elementos"')
        print("```")

        print()
        print("✨ Features demonstrated:")
        print("• 🌍 Multiple language support (EN, ES)")
        print("• 🎯 Type-safe translation access")
        print("• 📁 Nested namespace support (auth.login.title)")
        print("• 🔧 Parameterized translations (greeting, items.count)")
        print("• ⚙️  Configurable via pyproject.toml")
        print("• 🔍 Automatic validation (missing/extra keys)")


if __name__ == "__main__":
    main()
