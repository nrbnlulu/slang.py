from __future__ import annotations
import abc
from dataclasses import dataclass
import dataclasses
import enum
from functools import cached_property
from typing import Callable, Iterable, TypeVar
from result import Result, Ok, Err


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


def _find_field_error(
    field: T_BaseField,
    other: BaseField,
    locale_name: str,
    custom_error_mapper: Callable[[T_BaseField], str],
) -> str:
    if field.name != other.name:
        return f"{locale_name}: Field {field.full_name} is not compatible with {other.full_name}."
    if not isinstance(other, field.__class__):
        return f"{locale_name}: Field {field.full_name} is a {field.__class__.__name__}, but should be {other.__class__.__name__}."
    return custom_error_mapper(field)


@dataclass(slots=True, kw_only=True)
class NameSpaceField(BaseField):
    fields: list[BaseField] = dataclasses.field(default_factory=list)

    @property
    def is_namespace(self) -> bool:
        return True
    
    def get_child_namespace_fields(self) -> list[NameSpaceField]:
        ret: list[NameSpaceField] = []
        for field in self.fields:
            if isinstance(field, NameSpaceField):
                ret.extend(field.get_child_namespace_fields())
                ret.append(field)
        return ret

    @property
    def class_name(self) -> str:
        full_name = self.full_name
        return full_name.replace(".", "_").capitalize()

    @property
    def proto_name(self) -> str:
        return f"{self.class_name}Proto"

    def get_field(self, name: str) -> BaseField:
        for field in self.fields:
            if field.name == name:
                return field
        raise ValueError(f"Field {name} is not defined in {self.full_name}.")
    
    def compatible(self, other: BaseField, current_locale: str) -> Result[None, str]:
        """Ensure that both of the namespaces has the same fields."""
        if isinstance(other, NameSpaceField):
            for field in self.fields:
                if any(
                    field.compatible(other_field, current_locale)
                    for other_field in other.fields
                ):
                    return Ok(None)

        def pretty_error(other: NameSpaceField) -> str:
            error_str = f"{current_locale}: {self.full_name} is not compatible with {other.full_name}. \n"
            error_str += "The following fields are missing:"
            for field in self.fields:
                if not any(
                    field.compatible(other_field, current_locale)
                    for other_field in other.fields
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

    def compatible(self, other: BaseField, current_locale: str) -> Result[None, str]:
        """Ensure that both of the fields are compatible."""
        if isinstance(other, SimpleField):
            if self.name == other.name:
                return Ok(None)
        return Err(
            _find_field_error(
                self,
                other,
                current_locale,
                lambda field: f"{current_locale}: Field {field.full_name} is not compatible with {other.name}.",
            )
        )


class ArgumentType(enum.Enum):
    INT = "int"
    STR = "str"
    FLOAT = "float"
    BOOL = "bool"

    @classmethod
    def from_string(cls, kind: str) -> ArgumentType:
        if kind == "int":
            return cls.INT
        if kind == "str":
            return cls.STR
        if kind == "float":
            return cls.FLOAT
        if kind == "bool":
            return cls.BOOL
        raise ValueError(f"Unknown argument kind: {kind}")

    @property
    def as_py(self) -> str:
        if self == ArgumentType.INT:
            return "int"
        if self == ArgumentType.STR:
            return "str"
        if self == ArgumentType.FLOAT:
            return "float"
        if self == ArgumentType.BOOL:
            return "bool"
        raise ValueError(f"Unknown argument kind: {self}")

@dataclass(slots=True, kw_only=True)
class ArgumentDefinition:
    name: str
    type: ArgumentType


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

    def compatible(self, other: BaseField, current_locale: str) -> Result[None, str]:
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

    def compatible(
        self, other: LocaleImpl, current_namespace: str
    ) -> Result[None, str]:
        """Ensure that both of the implementations has the same fields."""
        return self.get_root().compatible(other.get_root(), current_namespace)

    @property
    def all_namespace_fields(self) -> list[NameSpaceField]:
        ret: list[NameSpaceField] = []
        for field in self.get_root().fields:
            if isinstance(field, NameSpaceField):
                ret.extend(field.get_child_namespace_fields())
                ret.append(field)
        return ret
                
    

@dataclass(slots=True, kw_only=True)
class SlangCtx:
    ref_locale: LocaleImpl
    """Reference locale, all locales should match this one."""
    locales: list[LocaleImpl] = dataclasses.field(default_factory=list)
 