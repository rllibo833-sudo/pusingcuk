from lexer import lex
from parser import parse
from evaluator import Evaluator

def run(src, filename="<input>"):
    toks=lex(src)
    tree=parse(toks, filename=filename)
    ev=Evaluator()
    # coba semua nama yang mungkin
    for name in ("eval", "evaluate", "run_module", "block", "run"):
        if hasattr(ev, name):
            fn=getattr(ev, name)
            try:
                if name=="block":
                    env={}
                    ev.block(tree, env, 0, True)
                    return env
                if name=="run_module":
                    # block adalah entry point utama
                    env={}
                    try:
                        ev.block(tree, env, 0, True)
                    except Exception as e:
                        raise e
                    return env
                return fn(tree)
            except TypeError:
                continue
    raise AttributeError(f"Evaluator gak punya eval/evaluate, methods: {[x for x in dir(ev) if not x.startswith('_')][:20]}")

def main():
    import sys
    src=sys.stdin.read()
    print(run(src))

if __name__=="__main__":
    main()
