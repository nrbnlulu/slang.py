"""Example usage of the Slang library for type-safe internationalization."""

from pathlib import Path
import tempfile
import yaml
import shutil
from slang import generate_translations

def create_example_project():
    """Create an example project with translation files."""
    # Get the example directory
    example_dir = Path(__file__).parent

    # Create i18n directory if it doesn't exist
    i18n_dir = example_dir / "i18n"
    i18n_dir.mkdir(exist_ok=True)

    # Create English translations
    en_translations = {
        "app": {
            "title": "My Awesome App",
            "version": "Version 1.0",
        },
        "welcome": "Welcome to our application!",
        "greeting": "Hello, {name}!",
        "user": {
            "profile": {
                "title": "User Profile",
                "edit": "Edit Profile",
                "save": "Save Changes"
            },
            "settings": {
                "title": "Settings",
                "language": "Language",
                "theme": "Theme"
            }
        },
        "messages": {
            "count(count: int)": "You have {count} messages",
            "empty": "No messages",
            "new": "New message from {sender}!"
        },
        "errors": {
            "not_found": "Item not found",
            "unauthorized": "Access denied",
            "server_error": "Server error occurred"
        }
    }

    # Create Spanish translations
    es_translations = {
        "app": {
            "title": "Mi Aplicación Increíble",
            "version": "Versión 1.0",
        },
        "welcome": "¡Bienvenido a nuestra aplicación!",
        "greeting": "¡Hola, {name}!",
        "user": {
            "profile": {
                "title": "Perfil de Usuario",
                "edit": "Editar Perfil",
                "save": "Guardar Cambios"
            },
            "settings": {
                "title": "Configuración",
                "language": "Idioma",
                "theme": "Tema"
            }
        },
        "messages": {
            "count(count: int)": "Tienes {count} mensajes",
            "empty": "No hay mensajes",
            "new": "¡Nuevo mensaje de {sender}!"
        },
        "errors": {
            "not_found": "Elemento no encontrado",
            "unauthorized": "Acceso denegado",
            "server_error": "Ocurrió un error del servidor"
        }
    }

    # Create French translations
    fr_translations = {
        "app": {
            "title": "Mon Application Géniale",
            "version": "Version 1.0",
        },
        "welcome": "Bienvenue dans notre application !",
        "greeting": "Bonjour, {name} !",
        "user": {
            "profile": {
                "title": "Profil Utilisateur",
                "edit": "Modifier le Profil",
                "save": "Sauvegarder les Modifications"
            },
            "settings": {
                "title": "Paramètres",
                "language": "Langue",
                "theme": "Thème"
            }
        },
        "messages": {
            "count(count: int)": "Vous avez {count} messages",
            "empty": "Aucun message",
            "new": "Nouveau message de {sender} !"
        },
        "errors": {
            "not_found": "Élément introuvable",
            "unauthorized": "Accès refusé",
            "server_error": "Erreur serveur survenue"
        }
    }

    # Write translation files
    with open(i18n_dir / "en.yml", "w") as f:
        yaml.dump(en_translations, f, default_flow_style=False, allow_unicode=True)

    with open(i18n_dir / "es.yml", "w") as f:
        yaml.dump(es_translations, f, default_flow_style=False, allow_unicode=True)

    with open(i18n_dir / "fr.yml", "w") as f:
        yaml.dump(fr_translations, f, default_flow_style=False, allow_unicode=True)

    # Update pyproject.toml with slang configuration
    pyproject_path = example_dir / "pyproject.toml"
    pyproject_content = '''[project]
name = "example"
version = "0.1.0"
description = "Slang library usage example"
readme = "README.md"
requires-python = ">=3.12, <4.0"
dependencies = []

[dependency-groups]
dev = [
    "slang",
]

[tool.uv.sources]
slang = { workspace = true }

[tool.slang]
output_dir = "generated"
translations_dir = "i18n"
main_language = "en"
'''

    with open(pyproject_path, "w") as f:
        f.write(pyproject_content)

    return example_dir

def demonstrate_generated_code():
    """Generate and demonstrate the translation code."""
    # Create the example project structure
    project_dir = create_example_project()

    print("🌐 Slang Translation Example")
    print("=" * 50)
    print()

    # Generate translations
    print("📁 Project structure:")
    print(f"   {project_dir.name}/")
    print("   ├── pyproject.toml")
    print("   └── i18n/")
    print("       ├── en.yml")
    print("       ├── es.yml")
    print("       └── fr.yml")
    print()

    print("⚡ Generating type-safe translations...")
    result = generate_translations(project_dir)

    if result.is_err():
        print(f"❌ Error: {result.err()}")
        return

    generated_code = result.unwrap()
    print("✅ Code generation successful!")
    print()

    # Write generated code to a file
    output_dir = project_dir / "generated"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "translations.py"
    with open(output_file, "w") as f:
        f.write(generated_code)

    print(f"📄 Generated code saved to: {output_file}")
    print()

    # Demonstrate usage
    print("🎯 Usage Example:")
    print("-" * 30)

    # Execute the generated code in a temporary context
    exec_globals = {}
    exec(generated_code, exec_globals)

    Languages = exec_globals['Languages']
    get_translations = exec_globals['get_translations']

    # English examples
    print("# English translations:")
    t_en = get_translations(Languages.EN)
    print(f't_en = get_translations(Languages.EN)')
    print(f'print(t_en.welcome)')
    print(f'  # "{t_en.welcome}"')
    print()

    print(f'print(t_en.greeting(name="Alice"))')
    print(f'  # "{t_en.greeting(name="Alice")}"')
    print()

    print(f'print(t_en.app.title)')
    print(f'  # "{t_en.app.title}"')
    print()

    print(f'print(t_en.user.profile.title)')
    print(f'  # "{t_en.user.profile.title}"')
    print()

    print(f'print(t_en.messages.count(count=5))')
    print(f'  # "{t_en.messages.count(count=5)}"')
    print()

    print(f'print(t_en.messages.new(sender="Bob"))')
    print(f'  # "{t_en.messages.new(sender="Bob")}"')
    print()

    # Spanish examples
    print("# Spanish translations:")
    t_es = get_translations(Languages.ES)
    print(f't_es = get_translations(Languages.ES)')
    print(f'print(t_es.welcome)')
    print(f'  # "{t_es.welcome}"')
    print()

    print(f'print(t_es.greeting(name="María"))')
    print(f'  # "{t_es.greeting(name="María")}"')
    print()

    print(f'print(t_es.user.settings.language)')
    print(f'  # "{t_es.user.settings.language}"')
    print()

    print(f'print(t_es.messages.count(count=3))')
    print(f'  # "{t_es.messages.count(count=3)}"')
    print()

    # French examples
    print("# French translations:")
    t_fr = get_translations(Languages.FR)
    print(f't_fr = get_translations(Languages.FR)')
    print(f'print(t_fr.welcome)')
    print(f'  # "{t_fr.welcome}"')
    print()

    print(f'print(t_fr.greeting(name="Pierre"))')
    print(f'  # "{t_fr.greeting(name="Pierre")}"')
    print()

    print(f'print(t_fr.errors.not_found)')
    print(f'  # "{t_fr.errors.not_found}"')
    print()

    print("✨ Features demonstrated:")
    print("• 🌍 Multi-language support (EN, ES, FR)")
    print("• 🎯 Type-safe translation access")
    print("• 📁 Nested namespaces (app.title, user.profile.title)")
    print("• 🔧 Auto-detected parameterized translations (greeting)")
    print("• 🔧 Explicit parameterized translations (messages.count)")
    print("• ⚙️  Configuration via pyproject.toml")
    print("• 🔍 Translation key validation across languages")
    print("• 📝 IDE autocomplete and type checking support")

def main():
    """Main example function."""
    try:
        demonstrate_generated_code()
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
