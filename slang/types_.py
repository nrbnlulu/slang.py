from __future__ import annotations
import abc
from dataclasses import dataclass

@dataclass(slots=True)
class BaseField(abc.ABC):
    """Field in a record type."""
    name: str

    @property
    def is_simple(self) -> bool:
        return False

    @property
    def is_namespace(self) -> bool:
        return False
    
    @property
    def is_complex(self) -> bool:
        return False
    

@dataclass(slots=True)
class NameSpaceField(BaseField):
    words: dict[str, BaseField]

@dataclass(slots=True)
class SimpleField(BaseField):
    value: str

    @property
    def is_simple(self) -> bool:
        return True


@dataclass(slots=True)
class ArgumentDefinition:
    name: str
    type: int | str | float | bool


@dataclass(slots=True)
class ComplexField(BaseField):
    """Field which needs to render a string using arguments."""

    arguments: list[ArgumentDefinition]
    template: str

    @property
    def is_complex(self) -> bool:
        return True


@dataclass(slots=True)
class SlangCtx:
    """Context for a type checker."""
    root: NameSpaceField | None = None
