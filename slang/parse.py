import re
from typing import Any
from slang.types_ import LocaleImpl
from slang.types_ import (
    BaseField,
    NameSpaceField,
    SimpleField,
    ArgumentDefinition,
    ComplexField,
)
from result import Result


def parse(input: dict[str, Any], origin_ctx: LocaleImpl, name: str) -> Result[LocaleImpl, str]:
    ctx = LocaleImpl(name=name)
    ctx.root = parse_namespace(ctx, input, "root")
    if not origin_ctx.compatible(ctx):
        return Err("The new locale is not compatible with the existing one.")


def parse_namespace(
    ctx: LocaleImpl, input: dict[str, Any], name: str
) -> NameSpaceField:
    ns: dict[str, BaseField] = {}
    for k, v in input.items():
        ns[k] = parse_entry(ctx, k, v)
    return NameSpaceField(name, ns)


complex_f_pattern = r"^(\w+)\((\w+: \w+)(, \w+: \w+)*\)$"


def parse_entry(ctx: LocaleImpl, k: str, v: Any) -> BaseField:
    if match := re.match(complex_f_pattern, k):
        return parse_complex(ctx, match, v)
    if isinstance(v, dict):
        return parse_namespace(ctx, v, k)
    else:
        return SimpleField(k, v)


def parse_complex(ctx: LocaleImpl, match: re.Match, v: str) -> ComplexField:
    name = match.group(1)
    args: list[ArgumentDefinition] = []
    for i in range(2, len(match.groups())):
        arg_name, arg_type = match.group(i).replace(" ", "").split(":")
        args.append(ArgumentDefinition(arg_name, arg_type))
    return ComplexField(name, args, template=v)
