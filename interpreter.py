from lexer import lex, LexerError
from parser import parse
from evaluator import Evaluator

def run(src, filename="<input>"):
    toks=lex(src)
    tree=parse(toks, filename=filename)
    ev=Evaluator()
    return ev.eval(tree)

def main():
    import sys
    src=sys.stdin.read()
    print(run(src))

if __name__=="__main__":
    main()
