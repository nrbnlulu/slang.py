import re
from typing import Any
from slang.types import SlangCtx
from .types import BaseField, NameSpaceField, SimpleField, ArgumentDefinition, ComplexField


def parse(input: dict[str, Any]) -> SlangCtx:
    ctx = SlangCtx()
    ctx.root = parse_namespace(ctx, input)

def parse_namespace(ctx: SlangCtx, input: dict[str, Any], name: str) -> NameSpaceField:
    ns: dict[str, BaseField] = {}
    for k, v in input.items():
        ns[k] = parse_entry(ctx, k, v)
    return NameSpaceField(name, ns)
complex_f_pattern = r'^(\w+)\((arg: (\w+))(, (\w+): (\w+))*\)$'

def parse_entry(ctx: SlangCtx, k: str, v: Any) -> BaseField:
    if match := re.match(complex_f_pattern, k):
        return parse_complex(ctx, match)
    if isinstance(v, dict):
        return parse_namespace(ctx, v, k)
    else:
        return SimpleField(k, v)


def parse_complex(ctx: SlangCtx, match: re.Match) -> ComplexField:
    name = match.group(1)
    args = []
    for i in range(2, len(match.groups()), 3):
        arg_name = match.group(i)
        arg_type = match.group(i + 1)
        args.append(ArgumentDefinition(arg_name, arg_type))
    return ComplexField(name, args)
    
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
parse(example)