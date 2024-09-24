from pathlib import Path
from slang.codegen import render_translations_proto
from slang.parse import parse
from slang.types_ import SimpleField, SlangCtx

def write_to_tmp(content) -> None:
    (Path(__file__).parent / "tmp.py").write_text(content)


def test_simple_field_proto(snapshot) -> None:
    example = {
        "simple": "Simple",
    }
    locale = parse(example, "heb").unwrap()
    assert snapshot == render_translations_proto(SlangCtx(ref_locale=locale))
    

def test_complex_field_proto(snapshot) -> None:
    example = {
        "complex(arg1: str, arg2: int, arg3: bool, arg4: float)": "Hello, {arg1}, {arg2}, {arg3}, {arg4}",
    }
    locale = parse(example, "heb").unwrap()
    assert snapshot == render_translations_proto(SlangCtx(ref_locale=locale))


def test_namespace_field_proto(snapshot) -> None:
    example = {
        "namespace": {
            "simple": "Simple",
            "complex(arg1: str)": "Hello, {arg1}",
        },
    }
    locale = parse(example, "heb").unwrap()
    write_to_tmp(render_translations_proto(SlangCtx(ref_locale=locale)))
    assert snapshot == render_translations_proto(SlangCtx(ref_locale=locale))