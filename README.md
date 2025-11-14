# slang-py

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Type-safe internationalization (i18n) for Python** 🌍

Slang is a Python library that generates type-safe translation interfaces from YAML files, inspired by the popular [Dart Slang](https://pub.dev/packages/slang) package. It provides compile-time safety, IDE autocomplete, and automatic validation for your translation files.

## Features

- ✅ **Type Safety**: Full IDE autocomplete and type checking support
- 🌍 **Multi-language Support**: Support for unlimited languages
- 📁 **Nested Namespaces**: Organize translations hierarchically  
- 🔧 **Parameterized Translations**: Support for dynamic values with auto-detection
- ⚙️ **Simple Configuration**: Configure via `pyproject.toml`
- 🔍 **Automatic Validation**: Ensures consistency across all language files
- 🚀 **Zero Runtime Dependencies**: Generated code is self-contained
- 📝 **IDE Integration**: Full IntelliSense support in VSCode, PyCharm, etc.

## Quick Start

### 1. Installation

```bash
pip install slang-py
# or with uv
uv add slang-py
```

### 2. Create Translation Files

Create an `i18n/` directory with YAML files for each language:

**`i18n/en.yml`** (main language):
```yaml
welcome: "Welcome to our app!"
greeting: "Hello, {name}!"
auth:
  login:
    title: "Sign In"
    button: "Log In"
  register:
    title: "Create Account"
    button: "Sign Up"
messages:
  count(count: int): "You have {count} messages"
  empty: "No messages"
```

**`i18n/es.yml`**:
```yaml
welcome: "¡Bienvenido a nuestra aplicación!"
greeting: "¡Hola, {name}!"
auth:
  login:
    title: "Iniciar Sesión"
    button: "Entrar"
  register:
    title: "Crear Cuenta"
    button: "Registrarse"
messages:
  count(count: int): "Tienes {count} mensajes"
  empty: "No hay mensajes"
```

### 3. Configure Your Project

Add configuration to your `pyproject.toml`:

```toml
[tool.slang]
output_dir = "generated"           # Where to output generated code
translations_dir = "i18n"          # Where translation files are located
main_language = "en"              # Reference language for validation
```

### 4. Generate Type-Safe Code

```python
from slang import generate_translations
from pathlib import Path

# Generate translations
result = generate_translations(Path.cwd())
if result.is_err():
    print(f"Error: {result.err()}")
else:
    code, output_file = result.unwrap()
    print(f"Generated code saved to: {output_file}")
    # Code is already written to file, but you can also use it directly
```

### 5. Use Your Translations

```python
from generated.translations import Languages, get_translations

# Get English translations
t_en = get_translations(Languages.EN)
print(t_en.welcome)                    # "Welcome to our app!"
print(t_en.greeting(name="Alice"))     # "Hello, Alice!"
print(t_en.auth.login.title)           # "Sign In"
print(t_en.messages.count(count=5))   # "You have 5 messages"

# Get Spanish translations  
t_es = get_translations(Languages.ES)
print(t_es.welcome)                    # "¡Bienvenido a nuestra aplicación!"
print(t_es.greeting(name="María"))     # "¡Hola, María!"
```

## Translation File Format

### Simple Translations
```yaml
welcome: "Welcome!"
title: "My App"
```

### Nested Namespaces
```yaml
user:
  profile:
    title: "User Profile"
    edit: "Edit Profile"
  settings:
    theme: "Theme"
    language: "Language"
```

### Parameterized Translations

**Auto-detected** (using `{placeholder}` syntax):
```yaml
greeting: "Hello, {name}!"
welcome_back: "Welcome back, {name}! You have {count} messages."
```

**Explicit** (with type annotations):
```yaml
messages:
  count(count: int): "You have {count} messages"
  progress(current: int, total: int): "Progress: {current}/{total}"
  rating(stars: float): "Rating: {stars:.1f} stars"
```

### Supported Parameter Types
- `int`: Integer numbers
- `str`: String values (default for auto-detected)
- `float`: Floating-point numbers
- `bool`: Boolean values

## Configuration Options

Configure Slang in your `pyproject.toml`:

```toml
[tool.slang]
# Required
output_dir = "generated"           # Output directory for generated code
translations_dir = "i18n"          # Directory containing YAML files
main_language = "en"              # Reference language (must exist)

# Optional (future versions)
# namespace = "translations"        # Python module namespace
# class_prefix = "T"               # Prefix for generated classes
```

## API Reference

### `generate_translations(project_path: Path | None = None) -> Result[tuple[str, Path], str]`

Generates type-safe translation code from YAML files.

**Parameters:**
- `project_path`: Path to project root (defaults to current directory)

**Returns:**
- `Result[tuple[str, Path], str]`: Tuple of (generated Python code, output file path) or error message

**Example:**
```python
from slang import generate_translations
from pathlib import Path

result = generate_translations(Path("/path/to/project"))
if result.is_ok():
    code, output_file = result.unwrap()
    print(f"Generated {len(code)} lines to {output_file}")
else:
    print(f"Error: {result.err()}")
```

## Generated Code Structure

The generated code includes:

### `Languages` Enum
```python
from enum import Enum

class Languages(Enum):
    EN = "en"
    ES = "es"
    FR = "fr"
```

### Protocol Interfaces
```python
from typing import Protocol

class TranslationsProto(Protocol):
    @property
    def welcome(self) -> str: ...
    
    def greeting(self, name: str) -> str: ...
    
    @property
    def auth(self) -> AuthProto: ...
```

### Implementation Classes
```python
class Translations_en(TranslationsProto):
    @property
    def welcome(self) -> str:
        return "Welcome to our app!"
    
    def greeting(self, name: str) -> str:
        return "Hello, {name}!".format(name=name)
```

### Factory Function
```python
def get_translations(language: Languages) -> TranslationsProto:
    match language:
        case Languages.EN:
            return Translations_en()
        case Languages.ES:
            return Translations_es()
```

## Validation

Slang automatically validates that:

- ✅ All languages have the same translation keys
- ✅ Nested namespaces are consistent across languages  
- ✅ Parameterized translations have matching signatures
- ✅ No missing or extra keys in any language file

If validation fails, you'll get a detailed error message pointing to the issue.

## IDE Integration

Slang provides full IDE support:

- **Autocomplete**: IntelliSense for all translation keys
- **Type Checking**: Compile-time validation with mypy/pyright
- **Navigation**: Go-to-definition for translation keys
- **Refactoring**: Safe renaming across your codebase

## Development

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [Task](https://taskfile.dev/) runner

### Setup
```bash
git clone https://github.com/yourusername/slang-py.git
cd slang-py
uv sync
```

### Common Tasks
```bash
# Run tests
task test

# Run linting
task lint  

# Run example
cd example && uv run python main.py
```

### Project Structure
```
slang-py/
├── slang/              # Main library code
│   ├── __init__.py     # Public API
│   ├── codegen.py      # Code generation
│   ├── config.py       # Configuration handling
│   ├── loader.py       # Translation loading
│   ├── parse.py        # YAML parsing
│   └── types_.py       # Type definitions
├── tests/              # Test suite
├── example/            # Example usage
└── README.md           # This file
```

## Comparison with Other Solutions

| Feature | slang-py | gettext | babel | flufl.i18n |
|---------|----------|---------|--------|-----------|
| Type Safety | ✅ | ❌ | ❌ | ❌ |
| IDE Support | ✅ | ❌ | ❌ | ❌ |
| Nested Keys | ✅ | ❌ | ❌ | ❌ |
| Auto-validation | ✅ | ❌ | ❌ | ❌ |
| Zero Runtime Deps | ✅ | ❌ | ❌ | ❌ |
| YAML Support | ✅ | ❌ | ❌ | ❌ |

## Roadmap

- [ ] **CLI Tool**: Command-line interface for code generation
- [ ] **Watch Mode**: Automatic regeneration on file changes  
- [ ] **VS Code Extension**: Enhanced IDE integration
- [ ] **Pluralization**: ICU-style plural rules support
- [ ] **Interpolation**: Advanced template features
- [ ] **JSON Support**: Alternative to YAML format
- [ ] **Hot Reload**: Runtime translation updates

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality  
5. Run `task test` and `task lint`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Inspiration

This project is inspired by:
- [Dart Slang](https://pub.dev/packages/slang) - The original type-safe i18n solution
- [Flutter Intl](https://pub.dev/packages/intl) - Internationalization support
- [TypeScript i18n](https://github.com/i18next/react-i18next) - Type-safe translations

## Support

- 📖 **Documentation**: [Read the docs](https://slang-py.readthedocs.io) (coming soon)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/slang-py/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/slang-py/discussions)
- 📧 **Email**: support@slang-py.dev

---

Made with ❤️ by the Slang-py team. Star us on [GitHub](https://github.com/yourusername/slang-py)!