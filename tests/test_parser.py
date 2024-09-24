from slang.parse import parse
from slang.types_ import ArgumentDefinition, ArgumentType, ComplexField, NameSpaceField, SimpleField


def test_simple_field() -> None:
    example = {
        "simple": "Simple",
    }
    locale = parse(example, "heb").unwrap()
    field = locale.get_root().get_field("simple")
    assert field == SimpleField(name="simple", value="Simple", parent=locale.get_root())


def test_complex_field_all_field_types() -> None:
    example = {
        "complex(arg1: str, arg2: int, arg3: bool, arg4: float)": "Hello, {arg1}, {arg2}, {arg3}, {arg4}",
    }
    locale = parse(example, "heb").unwrap()
    field = locale.get_root().get_field("complex")
    assert field.name == "complex"
    assert isinstance(field, ComplexField)
    assert field.template == "Hello, {arg1}, {arg2}, {arg3}, {arg4}"
    assert len(field.arguments) == 4
    assert field.arguments[0] == ArgumentDefinition(name="arg1", type=ArgumentType.STR)
    assert field.arguments[1] == ArgumentDefinition(name="arg2", type=ArgumentType.INT)
    assert field.arguments[2] == ArgumentDefinition(name="arg3", type=ArgumentType.BOOL)
    assert field.arguments[3] == ArgumentDefinition(
        name="arg4", type=ArgumentType.FLOAT
    )

def test_namespace_field() -> None:
    example = {
        "namespace": {
            "simple": "Simple",
            "complex(arg1: str)": "Hello, {arg1}",
        },
    }
    locale = parse(example, "heb").unwrap()
    field = locale.get_root().get_field("namespace")
    assert isinstance(field, NameSpaceField)
    assert field.name == "namespace"
    inner_simple = field.get_field("simple")
    assert inner_simple == SimpleField(name="simple", value="Simple", parent=field)
    inner_complex = field.get_field("complex")
    assert inner_complex == ComplexField(
        name="complex",
        arguments=[ArgumentDefinition(name="arg1", type=ArgumentType.STR)],
        template="Hello, {arg1}",
        parent=field,
    )
    assert inner_simple.full_name == "Locale_heb.namespace.simple"