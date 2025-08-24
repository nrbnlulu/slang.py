"""Configuration management for slang."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ImportError:
    tomllib = None
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        pass


@dataclass
class SlangConfig:
    """Configuration for slang translation generation."""

    output_dir: Path
    translations_dir: str = "translations"
    main_language: str = "en"

    @classmethod
    def load_from_pyproject(cls, start_path: Path | None = None) -> SlangConfig:
        """Load configuration from nearest pyproject.toml file."""
        default = cls(output_dir=Path("slang/gen"))
        if tomllib is None:
            return default

        pyproject_path = cls._find_pyproject_toml(start_path or Path.cwd())

        if pyproject_path is None:
            return default  # No pyproject.toml found, use defaults

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            slang_config = data.get("tool", {}).get("slang", {})
            return cls(
                output_dir=slang_config.get("output_dir", "slang/gen"),
                translations_dir=slang_config.get("translations_dir", "translations"),
                main_language=slang_config.get("main_language", "en"),
            )
        except Exception:
            # If we can't read the config, fall back to defaults rather than failing
            return cls()

    @staticmethod
    def _find_pyproject_toml(start_path: Path) -> Path | None:
        """Find the nearest pyproject.toml file by traversing up the directory tree."""
        current = start_path.resolve()

        while current != current.parent:
            pyproject_path = current / "pyproject.toml"
            if pyproject_path.exists():
                return pyproject_path
            current = current.parent

        return None

    def validate(self) -> None:
        """Validate the configuration."""
        if not self.main_language:
            raise ValueError("main_language cannot be empty")

        if not self.translations_dir:
            raise ValueError("translations_dir cannot be empty")

        if not self.output_dir:
            raise ValueError("output_dir cannot be empty")

    def get_translations_path(self, base_path: Path | None = None) -> Path:
        """Get the path to the translations directory."""
        if base_path is None:
            base_path = Path.cwd()
        return base_path / self.translations_dir

    def get_output_path(self, base_path: Path | None = None) -> Path:
        """Get the path to the output directory."""
        if base_path is None:
            base_path = Path.cwd()
        return base_path / self.output_dir
