# Slang Library Example

This example demonstrates how to use the Slang library to generate type-safe internationalization (i18n) code for Python applications.

## Overview

Slang is a Python library that generates type-safe translation interfaces from YAML files, similar to the popular Dart Slang package. It provides:

- ✅ **Type Safety**: Full IDE autocomplete and type checking
- 🌍 **Multi-language Support**: Support for any number of languages
- 📁 **Nested Namespaces**: Organize translations hierarchically
- 🔧 **Parameterized Translations**: Support for dynamic values
- ⚙️ **Auto-detection**: Automatic detection of parameterized fields
- 🔍 **Validation**: Ensures all languages have consistent translation keys

## Project Structure

```
example/
├── pyproject.toml          # Project configuration with slang settings
├── main.py                 # Example usage demonstration
├── i18n/                   # Translation files directory
│   ├── en.yml             # English translations (main language)
│   ├── es.yml             # Spanish translations
│   └── fr.yml             # French translations
└── generated/             # Auto-generated translation code
    └── translations.py    # Type-safe translation classes
```

## Configuration

The `pyproject.toml` file includes Slang configuration:

```toml
[tool.slang]
output_dir = "generated"        # Where to output generated code
translations_dir = "i18n"       # Where translation YAML files are located
main_language = "en"           # Reference language for validation
```

## Translation Files

Translation files use YAML format and support:

### Simple Translations
```yaml
welcome: "Welcome to our app!"
```

### Nested Namespaces
```yaml
user:
  profile:
    title: "User Profile"
    edit: "Edit Profile"
```

### Parameterized Translations

Auto-detected (using `{placeholder}` syntax):
```yaml
greeting: "Hello, {name}!"
```

Explicit (with type annotations):
```yaml
messages:
  count(count: int): "You have {count} messages"
```

## Running the Example

1. **Install dependencies:**
   ```bash
   cd example
   uv sync
   ```

2. **Run the example:**
   ```bash
   uv run python main.py
   ```

This will:
- Create the translation files in `i18n/`
- Generate type-safe Python code
- Demonstrate usage with all three languages
- Save generated code to `generated/translations.py`

## Generated Code Usage

After running the example, you can use the generated translations like this:

```python
from generated.translations import Languages, get_translations

# Get English translations
t_en = get_translations(Languages.EN)
print(t_en.welcome)                    # "Welcome to our application!"
print(t_en.greeting(name="Alice"))     # "Hello, Alice!"
print(t_en.app.title)                  # "My Awesome App"
print(t_en.user.profile.title)        # "User Profile"
print(t_en.messages.count(count=5))   # "You have 5 messages"

# Get Spanish translations
t_es = get_translations(Languages.ES)
print(t_es.welcome)                    # "¡Bienvenido a nuestra aplicación!"
print(t_es.greeting(name="María"))     # "¡Hola, María!"

# Get French translations
t_fr = get_translations(Languages.FR)
print(t_fr.welcome)                    # "Bienvenue dans notre application !"
```

## Features Demonstrated

- **Multiple Languages**: English, Spanish, and French translations
- **Type Safety**: Full IDE support with autocomplete and type checking
- **Nested Namespaces**: Hierarchical organization (`user.profile.title`)
- **Auto-detected Parameters**: Automatic detection of `{placeholder}` syntax
- **Explicit Parameters**: Type-annotated parameters for complex cases
- **Validation**: Ensures all languages have matching translation keys
- **Code Generation**: Produces clean, readable Python code

## Integration in Your Project

To use Slang in your own project:

1. Add Slang as a dependency
2. Create translation YAML files
3. Configure `pyproject.toml` with `[tool.slang]` settings
4. Generate translations and import the generated code
5. Use type-safe translations throughout your application

The generated code is completely self-contained and doesn't require the Slang library at runtime.