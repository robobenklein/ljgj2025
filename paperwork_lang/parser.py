
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

import lark
from lark import Lark, ast_utils, Transformer, v_args
from .assets import module_dir

ebnf_file = module_dir / 'paperwork.lark'
with ebnf_file.open('rt') as f:
    ebnf_definition = f.read()

llang = Lark(ebnf_definition)

this_module = sys.modules[__name__]

def parse(text):
    return llang.parse(text)

class _Ast(ast_utils.Ast):
    pass

class _Line(_Ast):
    pass

class _Instruction(_Line):
    pass

@dataclass
class Comment(_Line):
    comment_text: str

@dataclass
class Label(_Line):
    name: str

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

class ToAst(Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.
    def _convert_id_lower(self, t):
        return t[0].value.lower()
    
    def _convert_int(self, t):
        return int(t[0].value)

    location_identifier = _convert_id_lower
    location_type = _convert_id_lower
    parcel_type = _convert_id_lower
    parcel_identifier = _convert_int

    def label_name(self, t):
        return t[0].value

    def comment_text(self, s):
        t[0].value

    @v_args(inline=True)
    def start(self, x):
        # print(f"ast start: {x}, {a}, {kw}")
        return x


transformer = ast_utils.create_transformer(this_module, ToAst())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("program", type=Path)
    args = parser.parse_args()

    with args.program.open('rt') as f:
        ptree = llang.parse(f.read())
        print(ptree.pretty())
    
    ast = transformer.transform(ptree)
    for stmt in ast.lines:
        print(stmt)