"""Portable C11 source backend for the explicitly supported Pusingcuk subset."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from compiler.ir import from_source, validate

class CBackendError(ValueError):
    """Source uses a feature outside the current C backend subset."""

C_RUNTIME = r'''#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
static unsigned int pc_call_depth = 0;
static const char *pc_concat(const char *a, const char *b) {
    size_t na = strlen(a), nb = strlen(b);
    if (na > SIZE_MAX - nb - 1) { fputs("Pusingcuk C backend: string too large\\n", stderr); exit(EXIT_FAILURE); }
    char *out = (char *)malloc(na + nb + 1);
    if (!out) { fputs("Pusingcuk C backend: out of memory\\n", stderr); exit(EXIT_FAILURE); }
    memcpy(out, a, na); memcpy(out + na, b, nb + 1);
    return out;
}
static void pc_overflow(void) { fputs("Pusingcuk C backend: integer overflow\n", stderr); exit(EXIT_FAILURE); }
static void pc_division_by_zero(void) { fputs("Pusingcuk C backend: division by zero\n", stderr); exit(EXIT_FAILURE); }
void pc_loop_limit(void) { fputs("Pusingcuk C backend: loop iteration limit reached\n", stderr); exit(EXIT_FAILURE); }
void pc_call_enter(void) { if (pc_call_depth >= 100) { fputs("Pusingcuk C backend: function call depth limit reached\n", stderr); exit(EXIT_FAILURE); } pc_call_depth++; }
void pc_call_leave(void) { if (pc_call_depth > 0) pc_call_depth--; }
void pc_missing_return(void) { fputs("Pusingcuk C backend: function ended without balek\n", stderr); exit(EXIT_FAILURE); }
int64_t pc_add(int64_t a, int64_t b) {
    if ((b > 0 && a > INT64_MAX - b) || (b < 0 && a < INT64_MIN - b)) pc_overflow();
    return a + b;
}
int64_t pc_sub(int64_t a, int64_t b) {
    if ((b > 0 && a < INT64_MIN + b) || (b < 0 && a > INT64_MAX + b)) pc_overflow();
    return a - b;
}
int64_t pc_mul(int64_t a, int64_t b) {
    if (a > 0) { if ((b > 0 && a > INT64_MAX / b) || (b < 0 && b < INT64_MIN / a)) pc_overflow(); }
    else if (a < 0) { if ((b > 0 && a < INT64_MIN / b) || (b < 0 && a < INT64_MAX / b)) pc_overflow(); }
    return a * b;
}
int64_t pc_floor_div(int64_t a, int64_t b) {
    if (b == 0) pc_division_by_zero();
    if (a == INT64_MIN && b == -1) pc_overflow();
    int64_t q = a / b, r = a % b;
    if (r != 0 && ((r < 0) != (b < 0))) q--;
    return q;
}
int64_t pc_mod(int64_t a, int64_t b) {
    if (b == 0) pc_division_by_zero();
    if (a == INT64_MIN && b == -1) return 0;
    int64_t r = a % b;
    if (r != 0 && ((r < 0) != (b < 0))) r += b;
    return r;
}
'''
SUPPORTED_NODES = {"Program","Declare","Assign","Print","If","While","Function","Return","Literal","Variable","Unary","Binary","Call"}

def _node(kind, fields, line):
    if not isinstance(fields, dict) or not isinstance(line, int): raise CBackendError("node IR tidak valid")
    if kind not in SUPPORTED_NODES: raise CBackendError(f"fitur {kind} belum didukung backend C subset")
    return {"kind":kind,"fields":fields,"line":line}

def generate(document: dict) -> str:
    validate(document)
    program = document["program"]
    if program["kind"] != "Program": raise CBackendError("root IR harus Program")
    body = program["fields"].get("body")
    if not isinstance(body, list): raise CBackendError("Program.body tidak valid")
    functions = {}
    for st in body:
        if st.get("kind") != "Function": continue
        f, line = st.get("fields",{}), st.get("line",1)
        name, params = f.get("name"), f.get("params")
        if not isinstance(name,str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",name): raise CBackendError(f"baris {line}: nama fungsi tidak valid")
        if name in ("panjang","rentang") or name in functions: raise CBackendError(f"baris {line}: nama fungsi {name!r} sudah digunakan")
        if not isinstance(params,list) or any(not isinstance(p,str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",p) for p in params) or len(set(params)) != len(params):
            raise CBackendError(f"baris {line}: parameter fungsi tidak valid")
        functions[name]=st
    next_id=0
    def expression(n,names,types):
        kind, f, line=n.get("kind"),n.get("fields"),n.get("line"); _node(kind,f,line)
        if kind=="Literal":
            v=f.get("value")
            if isinstance(v, str):
                if any(ord(ch) < 32 and ch not in "\\n\\r\\t\\b\\f" for ch in v):
                    raise CBackendError(f"baris {line}: teks berisi karakter kontrol yang belum didukung backend C")
                return (json.dumps(v, ensure_ascii=False), "str")
            if type(v) is bool: return ("INT64_C(1)" if v else "INT64_C(0)","bool")
            if type(v) is int and 0<=v<=9223372036854775807: return (f"INT64_C({v})","int")
            raise CBackendError(f"baris {line}: literal belum didukung backend C")
        if kind=="Variable":
            name=f.get("name")
            if name not in names: raise CBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
            return names[name],types[name]
        if kind=="Call":
            name,args=f.get("name"),f.get("args")
            if name not in functions: raise CBackendError(f"baris {line}: fungsi {name!r} tidak dikenal atau belum didukung")
            params=functions[name]["fields"]["params"]
            if len(args)!=len(params): raise CBackendError(f"baris {line}: fungsi {name!r} membutuhkan {len(params)} argumen")
            rendered=[]
            for arg in args:
                value,typ=expression(arg,names,types)
                if typ!="int": raise CBackendError(f"baris {line}: parameter fungsi C subset harus integer")
                rendered.append(f"(int64_t)({value})")
            return f"pc_fn_{name}({', '.join(rendered)})","int"
        if kind=="Unary":
            value,typ=expression(f.get("value"),names,types); op=f.get("op")
            if op=="-":
                if typ!="int": raise CBackendError(f"baris {line}: unary minus hanya mendukung integer")
                return f"pc_sub(INT64_C(0), ({value}))","int"
            if op=="bukan": return f"(!({value}))","bool"
            raise CBackendError(f"baris {line}: operator unary {op!r} belum didukung")
        if kind=="Binary":
            op=f.get("op"); left,lt=expression(f.get("left"),names,types); right,rt=expression(f.get("right"),names,types)
            if op == "+" and lt == rt == "str":
                return f"pc_concat(({left}), ({right}))", "str"
            if op in {"+","-","*","//","%"}:
                if lt!="int" or rt!="int": raise CBackendError(f"baris {line}: operator {op!r} hanya mendukung operand integer")
                helper={"+":"pc_add","-":"pc_sub","*":"pc_mul","//":"pc_floor_div","%":"pc_mod"}[op]
                return f"{helper}(({left}), ({right}))","int"
            if op in {"dan","atau"}: return f"((({left}) != 0) {'&&' if op=='dan' else '||'} (({right}) != 0))","bool"
            if op in {"==","!="}:
                if lt!=rt: return f"(((void)({left})), ((void)({right})), {'INT64_C(0)' if op=='==' else 'INT64_C(1)'})","bool"
                return f"(({left}) {op} ({right}))","bool"
            if op in {"<","<=",">",">="}:
                if lt!="int" or rt!="int": raise CBackendError(f"baris {line}: perbandingan urutan hanya mendukung integer")
                return f"(({left}) {op} ({right}))","bool"
            raise CBackendError(f"baris {line}: operator {op!r} belum didukung backend C")
        raise CBackendError(f"baris {line}: ekspresi {kind!r} belum didukung backend C")
    def statements(nodes,names,types,indent="    ",in_function=False,in_loop=False):
        nonlocal next_id
        out=[]
        for st in nodes:
            kind,f,line=st.get("kind"),st.get("fields"),st.get("line"); _node(kind,f,line)
            if kind=="Function": raise CBackendError(f"baris {line}: fungsi hanya boleh didefinisikan di tingkat teratas")
            if kind=="Declare":
                name=f.get("name")
                if not isinstance(name,str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",name): raise CBackendError(f"baris {line}: nama variabel tidak valid")
                if name in names: raise CBackendError(f"baris {line}: variabel {name!r} sudah dideklarasikan")
                if in_loop: raise CBackendError(f"baris {line}: deklarasi lah di dalam loop belum didukung; deklarasikan sebelum loop")
                value,typ=expression(f.get("value"),names,types); cname=f"pc_v_{next_id}"; next_id+=1
                names[name],types[name]=cname,typ
                declaration = f"const char *{cname} = {value};" if typ == "str" else f"int64_t {cname} = (int64_t)({value});"
                out.extend([f"{indent}{declaration}",f"{indent}(void){cname};"])
            elif kind=="Assign":
                name=f.get("name")
                if name not in names: raise CBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
                value,typ=expression(f.get("value"),names,types)
                if typ!=types[name]: raise CBackendError(f"baris {line}: backend C subset tidak mendukung perubahan tipe variabel {name!r}")
                rendered = value if typ == "str" else f"(int64_t)({value})"
                out.append(f"{indent}{names[name]} = {rendered};")
            elif kind=="Print":
                value,typ=expression(f.get("value"),names,types)
                if typ=="bool": out.append(f'{indent}if (printf("%s\\n", ({value}) ? "okelah" : "tidak") < 0) return EXIT_FAILURE;')
                elif typ=="str": out.append(f'{indent}if (printf("%s\\n", {value}) < 0) return EXIT_FAILURE;')
                else: out.append(f'{indent}if (printf("%" PRId64 "\\n", (int64_t)({value})) < 0) return EXIT_FAILURE;')
            elif kind=="If":
                cond,_=expression(f.get("condition"),names,types); out.append(f"{indent}if (({cond}) != 0) {{")
                yes=statements(f.get("then_body",[]),dict(names),dict(types),indent+"    ",in_function,in_loop); out.extend(yes or [indent+"    (void)0;"])
                no_body=f.get("else_body",[])
                if no_body:
                    out.append(f"{indent}}} else {{"); no=statements(no_body,dict(names),dict(types),indent+"    ",in_function,in_loop); out.extend(no or [indent+"    (void)0;"])
                out.append(f"{indent}}}")
            elif kind=="While":
                cond,_=expression(f.get("condition"),names,types); loop_id=next_id; next_id+=1
                out.extend([f"{indent}unsigned int pc_loop_{loop_id} = 0;",f"{indent}while (({cond}) != 0) {{",f"{indent}    if (pc_loop_{loop_id}++ >= 10000U) pc_loop_limit();"])
                nested=statements(f.get("body",[]),dict(names),dict(types),indent+"    ",in_function,True); out.extend(nested or [indent+"    (void)0;"]); out.append(f"{indent}}}")
            elif kind=="Return":
                if not in_function: raise CBackendError(f"baris {line}: balek hanya boleh di dalam fungsi")
                if f.get("value") is None: raise CBackendError(f"baris {line}: balek pada backend C subset membutuhkan nilai integer")
                value,typ=expression(f["value"],names,types)
                if typ!="int": raise CBackendError(f"baris {line}: balek pada backend C subset hanya mendukung integer")
                ret_id=next_id; next_id+=1
                out.extend([f"{indent}int64_t pc_ret_{ret_id} = (int64_t)({value});",f"{indent}pc_call_leave();",f"{indent}return pc_ret_{ret_id};"])
            else: raise CBackendError(f"baris {line}: pernyataan {kind!r} belum didukung backend C")
        return out
    prototypes=[]; definitions=[]
    for name,st in functions.items():
        f,line=st["fields"],st["line"]; params=f["params"]; sig=", ".join(f"int64_t pc_arg_{i}" for i in range(len(params))) or "void"
        prototypes.append(f"static int64_t pc_fn_{name}({sig});")
        names={p:f"pc_arg_{i}" for i,p in enumerate(params)}; types={p:"int" for p in params}
        body_lines=[f"    (void)pc_arg_{i};" for i in range(len(params))] + statements(f["body"],names,types,"    ",True,False)
        definitions.append(f"static int64_t pc_fn_{name}({sig}) {{\n    pc_call_enter();\n"+("\n".join(body_lines) if body_lines else "    (void)0;")+"\n    pc_call_leave();\n    pc_missing_return();\n    return INT64_C(0);\n}")
    main_lines=[f"    (void)&pc_fn_{name};" for name in functions] + statements([s for s in body if s.get("kind")!="Function"],{}, {})
    return C_RUNTIME+"\n"+"\n".join(prototypes)+"\n"+"\n".join(definitions)+"\nint main(void) {\n"+("\n".join(main_lines) if main_lines else "    (void)0;")+"\n    return EXIT_SUCCESS;\n}\n"

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description="Kompilasi subset Pusingcuk menjadi source C11.")
    parser.add_argument("source",help="berkas sumber .pusingcuk"); parser.add_argument("-o","--output",help="berkas source C tujuan; default stdout")
    args=parser.parse_args(argv)
    try:
        path=Path(args.source); output=generate(from_source(path.read_text(encoding="utf-8"),path.name))
        if args.output: Path(args.output).write_text(output,encoding="utf-8")
        else: sys.stdout.write(output)
        return 0
    except (OSError,UnicodeError,ValueError,TypeError) as exc:
        print(f"Kesalahan backend C: {exc}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
