from __future__ import annotations
import abc
from dataclasses import dataclass
from typing import Callable, TypeVar, override
from result import Result, Ok,Err

@dataclass(slots=True, kw_only=True)
class BaseField(abc.ABC):
    """Field in a record type."""
    name: str
    parent: BaseField | None = None

    @property
    def full_name(self) -> str:
        if self.parent is not None:
            return f"{self.parent.full_name}.{self.name}"
        return self.name

    @property
    def is_simple(self) -> bool:
        return False

    @property
    def is_namespace(self) -> bool:
        return False

    @property
    def is_complex(self) -> bool:
        return False

    @abc.abstractmethod
    def compatible(self, other: BaseField, current_locale: str) -> Result[None, str]:
        """Ensure that both of the fields are compatible."""
        pass

T_BaseField = TypeVar("T_BaseField", bound=BaseField)

def _find_field_error(field: T_BaseField, other: BaseField, locale_name: str, custom_error_mapper: Callable[[T_BaseField], str]) -> str:
  
    if field.name != other.name:
        return f"{locale_name}: Field {field.full_name} is not compatible with {other.full_name}."
    if not isinstance(other, field.__class__):
        return f"{locale_name}: Field {field.full_name} is a {field.__class__.__name__}, but should be {other.__class__.__name__}."
    return custom_error_mapper(field)

@dataclass(slots=True, kw_only=True)
class NameSpaceField(BaseField):
    words: dict[str, BaseField]

    def compatible(self, other: BaseField, current_locale: str)-> Result[None, str]:
        """Ensure that both of the namespaces has the same fields."""
        if isinstance(other, NameSpaceField):
            for field in self.words.values():
                if any(
                    field.compatible(other_field, current_locale)
                    for other_field in other.words.values()
                ):
                    return Ok(None)
        
        def pretty_error(other: NameSpaceField) -> str:
            error_str = f"{current_locale}: {self.full_name} is not compatible with {other.full_name}. \n"
            error_str += "The following fields are missing:"
            for field in self.words.values():
                if not any(
                    field.compatible(other_field, current_locale) for other_field in other.words.values()
                ):
                    error_str += f"\n{field.full_name}"
            return error_str
        return Err(_find_field_error(self, other, current_locale, pretty_error))


@dataclass(slots=True, kw_only=True)
class SimpleField(BaseField):
    value: str

    @property
    def is_simple(self) -> bool:
        return True

    def compatible(self, other: BaseField, current_locale: str)-> Result[None, str]:
        """Ensure that both of the fields are compatible."""
        if isinstance(other, SimpleField):
            if self.name == other.name:
                return Ok(None)
        return Err(_find_field_error(self, other, current_locale, lambda field: f"{current_locale}: Field {field.full_name} is not compatible with {other.name}."))

@dataclass(slots=True, kw_only=True)
class ArgumentDefinition:
    name: str
    type: int | str | float | bool


@dataclass(slots=True, kw_only=True)
class ComplexField(BaseField):
    """Field which needs to render a string using arguments."""

    arguments: list[ArgumentDefinition]
    template: str

    @property
    def is_complex(self) -> bool:
        return True
    def get_argument(self, name: str) -> ArgumentDefinition:
        for arg in self.arguments:
            if arg.name == name:
                return arg
        raise ValueError(f"Argument {name} is not defined in {self.full_name}.")
    def compatible(self, other: BaseField, current_locale: str)-> Result[None, str]:
        if (
            isinstance(other, ComplexField)
            and self.name == other.name
            and self.arguments == other.arguments
        ):
            return Ok(None)
        def pretty_error(other: ComplexField) -> str:
            error_str = f"{current_locale}: {self.full_name} arguments is not compatible with {other.full_name}. \n"
            for arg in self.arguments:
                if arg not in other.arguments:
                    other_arg = other.get_argument(arg.name)
                    error_str += f"\n`{arg.name}: {arg.type}` != `{other_arg.name}: {other_arg.type}`"
            return error_str
        return Err(_find_field_error(self, other, current_locale, pretty_error))


@dataclass(slots=True, kw_only=True)
class LocaleImpl:
    """Context for a type checker."""

    name: str
    root: NameSpaceField | None = None

    def get_root(self) -> NameSpaceField:
        if self.root is None:
            raise ValueError("Root field is not defined.")
        return self.root

    def compatible(self, other: LocaleImpl, current_namespace: str) -> Result[None, str]:
        """Ensure that both of the implementations has the same fields."""
        return self.get_root().compatible(other.get_root(), current_namespace)


@dataclass(slots=True, kw_only=True)
class SlangCtx:
    ref_locale: LocaleImpl
    """Reference locale, all locales should match this one."""
    locales: list[LocaleImpl]
