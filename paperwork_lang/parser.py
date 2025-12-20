
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
    # stoopid but easier than fighting with Lark/LALR for another few hours:
    if not text.endswith('\n'):
        text += '\n'
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
    subject_type: str # TODO: Need to handle when we carry multiple things
    subject_property: str

    def __str__(self):
        return f"TestSubject(\nsubject_type={self.subject_type}\nsubject_property={self.subject_property})".replace('\n', '\n\t')

@dataclass
class TestCondition(_Ast):
    test_subject: TestSubject
    test_value: Optional[int | str] = None

    def __str__(self):
        return f"TestCondition(\ntest_subject={self.test_subject}\ntest_value={self.test_value})".replace('\n', '\n\t')

@dataclass
class InsWhen(_Instruction):
    test_condition: TestCondition
    #instruction: _Instruction # TODO: We can assume the next line is the instruction

    def __str__(self):
        return f"InsWhen(\ntest_condition={self.test_condition})".replace('\n', '\n\t')
        #return f"InsWhen(\ntest_condition={self.test_condition},\ninstruction={self.instruction})".replace('\n', '\n\t')

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

    assert parse("move desk a")
    assert parse("# I am a comment!")
