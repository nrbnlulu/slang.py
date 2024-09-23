import re
from typing import Any
from slang.types_ import SlangCtx
from slang.types_ import BaseField, NameSpaceField, SimpleField, ArgumentDefinition, ComplexField


def parse(input: dict[str, Any]) -> SlangCtx:
    ctx = SlangCtx()
    ctx.root = parse_namespace(ctx, input, "root")
    return ctx

def parse_namespace(ctx: SlangCtx, input: dict[str, Any], name: str) -> NameSpaceField:
    ns: dict[str, BaseField] = {}
    for k, v in input.items():
        ns[k] = parse_entry(ctx, k, v)
    return NameSpaceField(name, ns)
complex_f_pattern = r'^(\w+)\((\w+: \w+)(, \w+: \w+)*\)$'

def parse_entry(ctx: SlangCtx, k: str, v: Any) -> BaseField:
    if match := re.match(complex_f_pattern, k):
        return parse_complex(ctx, match, v)
    if isinstance(v, dict):
        return parse_namespace(ctx, v, k)
    else:
        return SimpleField(k, v)


def parse_complex(ctx: SlangCtx, match: re.Match, v: str) -> ComplexField:
    name = match.group(1)
    args: list[ArgumentDefinition] = []
    for i in range(2, len(match.groups())):
        arg_name, arg_type = match.group(i).replace(" ", "").split(":")
        args.append(ArgumentDefinition(arg_name, arg_type))
    return ComplexField(name, args, template=v)
    
example = {
    'name(family: str)': 'John {family}',
    'age': 30,
    'address': {
        'street': '123 Main St',
        'city': 'Springfield',
        'state': 'IL',
        'zip': 62701
    },
    'phone': '555-1234',
    'email': "fdsaf@fadsf.com"
}
print(parse(example))