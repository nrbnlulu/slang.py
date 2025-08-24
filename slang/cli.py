"""Command-line interface for Slang translation generator."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from . import generate_translations

app = typer.Typer(
    name="slang",
    help="🌍 Type-safe internationalization (i18n) for Python",
    no_args_is_help=True,
)

console = Console()


@app.command()
def generate(
    project_path: Optional[Path] = typer.Argument(
        None,
        help="Path to project root directory (defaults to current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (overrides config)",
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Watch for changes and regenerate automatically",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
) -> None:
    """Generate type-safe translation code from YAML files."""

    if project_path is None:
        project_path = Path.cwd()

    console.print(Panel.fit("🌍 Slang Translation Generator", style="bold blue"))

    if verbose:
        console.print(f"📁 Project path: {project_path}")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Generating translations...", total=None)

            result = generate_translations(project_path)

            if result.is_err():
                console.print(f"❌ [red]Error:[/red] {result.err()}")
                raise typer.Exit(1)

            progress.update(task, description="Writing output file...")

            generated_code, generated_file = result.unwrap()

            progress.remove_task(task)

        console.print("✅ [green]Success![/green] Generated translations saved to:")
        console.print(f"   📄 {generated_file}")

        if verbose:
            console.print("\n📊 Generation Stats:")
            lines = len(generated_code.split("\n"))
            console.print(f"   • Lines of code: {lines}")
            console.print(f"   • File size: {len(generated_code)} bytes")

        # Show usage example
        console.print("\n🎯 [bold]Usage Example:[/bold]")
        usage_code = """from <generate_dir>.translations import Languages, get_translations

# Get translations for English
t = get_translations(Languages.EN)
print(t.welcome)  # Type-safe access with autocomplete!"""

        syntax = Syntax(usage_code, "python", theme="monokai", line_numbers=False)
        console.print(syntax)

    except Exception as e:
        console.print(f"❌ [red]Unexpected error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def init(
    project_path: Optional[Path] = typer.Argument(
        None,
        help="Path to initialize slang project (defaults to current directory)",
    ),
    languages: list[str] = typer.Option(
        ["en", "es"],
        "--lang",
        "-l",
        help="Languages to initialize (default: en, es)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files",
    ),
) -> None:
    """Initialize a new slang project with example translation files."""

    if project_path is None:
        project_path = Path.cwd()

    console.print(Panel.fit("🚀 Initialize Slang Project", style="bold green"))

    # Create i18n directory
    i18n_dir = project_path / "i18n"
    i18n_dir.mkdir(exist_ok=True)

    # Example translations
    example_translations = {
        "en": {
            "welcome": "Welcome to our app!",
            "greeting": "Hello, {name}!",
            "nav": {"home": "Home", "about": "About", "contact": "Contact"},
            "messages": {
                "count(count: int)": "You have {count} messages",
                "empty": "No messages",
            },
        },
        "es": {
            "welcome": "¡Bienvenido a nuestra aplicación!",
            "greeting": "¡Hola, {name}!",
            "nav": {"home": "Inicio", "about": "Acerca de", "contact": "Contacto"},
            "messages": {
                "count(count: int)": "Tienes {count} mensajes",
                "empty": "No hay mensajes",
            },
        },
        "fr": {
            "welcome": "Bienvenue dans notre application !",
            "greeting": "Bonjour, {name} !",
            "nav": {"home": "Accueil", "about": "À propos", "contact": "Contact"},
            "messages": {
                "count(count: int)": "Vous avez {count} messages",
                "empty": "Aucun message",
            },
        },
    }

    import yaml

    created_files = []

    # Create translation files
    for lang in languages:
        lang_file = i18n_dir / f"{lang}.yml"

        if lang_file.exists() and not force:
            console.print(
                f"⚠️  [yellow]Skipping {lang_file} (already exists, use --force to overwrite)[/yellow]"
            )
            continue

        if lang in example_translations:
            translations = example_translations[lang]
        else:
            # Use English as template for unknown languages
            translations = example_translations["en"]

        with open(lang_file, "w") as f:
            yaml.dump(translations, f, default_flow_style=False, allow_unicode=True)

        created_files.append(lang_file)
        console.print(f"✅ Created {lang_file}")

    # Update or create pyproject.toml with slang config
    pyproject_path = project_path / "pyproject.toml"
    slang_config = """
[tool.slang]
output_dir = "generated"
translations_dir = "i18n"
main_language = "en"
"""

    if pyproject_path.exists():
        content = pyproject_path.read_text()
        if "[tool.slang]" not in content:
            content += slang_config
            pyproject_path.write_text(content)
            console.print(f"✅ Updated {pyproject_path} with slang configuration")
        else:
            console.print(f"⚠️  [yellow]{pyproject_path} already has slang configuration[/yellow]")
    else:
        pyproject_content = f"""[project]
name = "my-project"
version = "0.1.0"
description = "My internationalized project"
requires-python = ">=3.12"
dependencies = []
{slang_config}
"""
        pyproject_path.write_text(pyproject_content)
        console.print(f"✅ Created {pyproject_path}")

    # Summary
    console.print("\n🎉 [green]Project initialized successfully![/green]")
    console.print(f"📁 Translation files created in: {i18n_dir}")
    console.print(f"⚙️  Configuration added to: {pyproject_path}")

    console.print("\n🚀 [bold]Next steps:[/bold]")
    console.print("1. Edit your translation files in the i18n/ directory")
    console.print("2. Run: [cyan]slang generate[/cyan]")
    console.print(
        "3. Import and use: [cyan]from generated.translations import get_translations[/cyan]"
    )


@app.command()
def validate(
    project_path: Optional[Path] = typer.Argument(
        None,
        help="Path to project root directory (defaults to current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Validate translation files for consistency."""

    if project_path is None:
        project_path = Path.cwd()

    console.print(Panel.fit("🔍 Validate Translation Files", style="bold yellow"))

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Validating translations...", total=None)

            result = generate_translations(project_path)
            progress.remove_task(task)

            if result.is_err():
                console.print("❌ [red]Validation failed:[/red]")
                console.print(f"   {result.err()}")
                raise typer.Exit(1)
            else:
                console.print("✅ [green]All translation files are valid![/green]")

    except Exception as e:
        console.print(f"❌ [red]Validation error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def info(
    project_path: Optional[Path] = typer.Argument(
        None,
        help="Path to project root directory (defaults to current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Show information about the slang project."""

    if project_path is None:
        project_path = Path.cwd()

    console.print(Panel.fit("ℹ️  Project Information", style="bold cyan"))

    from .config import SlangConfig

    try:
        config = SlangConfig.load_from_pyproject(project_path)

        console.print(f"📁 [bold]Project Path:[/bold] {project_path}")
        console.print(f"📂 [bold]Translations Dir:[/bold] {config.translations_dir}")
        console.print(f"📤 [bold]Output Dir:[/bold] {config.output_dir}")
        console.print(f"🌐 [bold]Main Language:[/bold] {config.main_language}")

        # Check for translation files
        i18n_dir = project_path / config.translations_dir
        if i18n_dir.exists():
            yaml_files = list(i18n_dir.glob("*.yml")) + list(i18n_dir.glob("*.yaml"))
            console.print("\n📄 [bold]Translation Files:[/bold]")
            for file in sorted(yaml_files):
                lang_code = file.stem
                console.print(f"   • {lang_code}: {file.name}")

            if not yaml_files:
                console.print("   [yellow]No translation files found[/yellow]")
        else:
            console.print(f"\n⚠️  [yellow]Translations directory not found: {i18n_dir}[/yellow]")

        # Check for generated code
        output_file = project_path / config.output_dir / "translations.py"
        if output_file.exists():
            console.print(f"\n✅ [bold]Generated Code:[/bold] {output_file}")
            stat = output_file.stat()
            from datetime import datetime

            modified = datetime.fromtimestamp(stat.st_mtime)
            console.print(f"   Last generated: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            console.print("\n📝 [bold]Generated Code:[/bold] [yellow]Not generated yet[/yellow]")
            console.print("   Run [cyan]slang generate[/cyan] to create it")

    except Exception as e:
        console.print(f"❌ [red]Error reading project info:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
