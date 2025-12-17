
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

import bpython
import lark
from lark import Lark, ast_utils, Transformer, v_args
from .assets import module_dir

ebnf_file = module_dir / 'paperwork.lark'
with ebnf_file.open('rt') as f:
    ebnf_definition = f.read()

llang = Lark(ebnf_definition, parser='lalr')

this_module = sys.modules[__name__]

def on_parse_error(e):
    # bpython.embed(locals(), banner="Post-Mortem Debugging:")
    pass

def parse(text):
    return llang.parse(
        text,
        on_error=on_parse_error,
    )

class _Ast(ast_utils.Ast):
    pass

class _Line(_Ast):
    pass

class _Instruction(_Line):
    pass

@dataclass
class Label(_Line):
    name: str

@dataclass
class InsGoto(_Instruction):
    label_name: str

@dataclass
class CodeBlock(_Ast, ast_utils.AsList):
    lines: List[_Line]

# @dataclass
# class LocationType(_Ast):
#     value: str

@dataclass
class InsMove(_Instruction):
    location_type: str
    location_identifier: str

@dataclass
class InsTake(_Instruction):
    parcel_type: str
    parcel_identifier: Optional[int] = None

@dataclass
class InsDrop(_Instruction):
    parcel_type: str
    parcel_identifier: Optional[int] = None

@dataclass
class TestSubject(_Ast):
    subject_type: str
    subject_property: str

@dataclass
class TestCondition(_Ast):
    test_subject: TestSubject
    test_value: Optional[int | str] = None

@dataclass
class InsWhen(_Instruction):
    test_condition: TestCondition
    instruction: _Instruction

    def __str__(self):
        return f"InsWhen(\ncondition={self.test_condition},\ninstruction={self.instruction})".replace('\n', '\n\t')

@v_args(meta=True)
class ToAst(Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.
    def _convert_id_lower(self, m, t):
        return t[0].value.lower()

    def _convert_int(self, m, t):
        return int(t[0].value)

    def _convert_string(self, m, t):
        return t[0].value

    location_identifier = _convert_id_lower
    location_type = _convert_id_lower
    parcel_type = _convert_id_lower
    parcel_identifier = _convert_int
    # INT = _convert_int

    label_name = _convert_string
    property_name = _convert_string
    # comment = _convert_string

    @v_args(inline=True)
    def start(self, x):
        # print(f"ast start: {x}, {a}, {kw}")
        return x

    def test_value(self, m, x):
        try:
            return int(x[0].value)
        except ValueError:
            return x[0].value

transformer = ast_utils.create_transformer(this_module, ToAst())

def tree_to_ast(tree):
    return transformer.transform(tree)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("program", type=Path)
    args = parser.parse_args()

    with args.program.open('rt') as f:
        ptree = parse(f.read())
        print(ptree.pretty())

    ast = tree_to_ast(ptree)
    for stmt in ast.lines:
        print(stmt)
