
import argparse
from pathlib import Path
from lark import Lark

ebnf_file = Path("./paperwork_lang/paperwork.lark")
with ebnf_file.open('rt') as f:
    ebnf_definition = f.read()

llang = Lark(ebnf_definition)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("program", type=Path)
    args = parser.parse_args()

    with args.program.open('rt') as f:
        ptree = llang.parse(f.read())
        print(ptree.pretty())