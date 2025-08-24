import re
from typing import Any
from slang.types_ import ArgumentType, LocaleImpl
from slang.types_ import (
    BaseField,
    NameSpaceField,
    SimpleField,
    ArgumentDefinition,
    ComplexField,
)
from result import Result, Ok


def parse(
    input: dict[str, Any], name: str, origin_ctx: LocaleImpl | None = None
) -> Result[LocaleImpl, str]:
    ctx = LocaleImpl(name=name)
    ctx.root = parse_namespace(ctx, input, f"Locale_{name}")
    if origin_ctx is None:
        return Ok(ctx)
    return origin_ctx.compatible(ctx, name).map(lambda _: ctx)


def parse_namespace(
    ctx: LocaleImpl,
    input: dict[str, Any],
    name: str,
    parent: NameSpaceField | None = None,
) -> NameSpaceField:
    ret = NameSpaceField(name=name, parent=parent)
    for k, v in input.items():
        ret.fields.append(parse_entry(ctx, k, v, parent=ret))
    return ret


complex_f_pattern = re.compile(r"^(\w+)\((.*)\)$")
placeholder_pattern = re.compile(r"\{(\w+)\}")


def parse_entry(ctx: LocaleImpl, k: str, v: Any, parent: NameSpaceField | None = None) -> BaseField:
    if match := complex_f_pattern.fullmatch(k):
        return parse_complex(ctx, match, v, parent=parent)
    if isinstance(v, dict):
        return parse_namespace(ctx, v, k, parent=parent)
    elif isinstance(v, str):
        # Check for auto-detected placeholders in the template
        placeholders = placeholder_pattern.findall(v)
        if placeholders:
            return parse_auto_complex(ctx, k, v, placeholders, parent=parent)
        else:
            return SimpleField(name=k, value=v, parent=parent)
    else:
        return SimpleField(name=k, value=v, parent=parent)


def parse_complex(
    ctx: LocaleImpl, match: re.Match, v: str, parent: NameSpaceField | None = None
) -> ComplexField:
    groups = match.groups()
    name = groups[0]
    args: list[ArgumentDefinition] = []
    args_matches: list[tuple[str, str]] = re.findall(r"(\w+):(\s?\w+)", groups[1])
    for arg_match in args_matches:
        arg_name, arg_type_raw = arg_match
        arg_type = ArgumentType.from_string(arg_type_raw.strip())
        args.append(ArgumentDefinition(name=arg_name.strip(), type=arg_type))
    return ComplexField(name=name, arguments=args, template=v, parent=parent)


def parse_auto_complex(
    ctx: LocaleImpl,
    name: str,
    template: str,
    placeholders: list[str],
    parent: NameSpaceField | None = None,
) -> ComplexField:
    """Parse a complex field with auto-detected placeholders."""
    args: list[ArgumentDefinition] = []
    # Auto-detect argument types (default to string for simplicity)
    for placeholder in set(placeholders):  # Use set to avoid duplicates
        args.append(ArgumentDefinition(name=placeholder, type=ArgumentType.STR))
    return ComplexField(name=name, arguments=args, template=template, parent=parent)
