import json, os, re
from collections import namedtuple
Token = namedtuple('Token',['type','value','baris','kolom'])

CANONICAL = frozenset(["jancuk","selesai","lah","hedeh","njir","kampret","mumet","untuk","dalam","tanya","fungsi","balek","dan","atau","bukan","benar","salah","coba","ketangkep","akhirnya"])

BASE_ALIASES = {
 "jir":"hedeh","adooh":"kampret","gitu":"selesai","inthiseco":"jancuk","janggal":"bukan","gas":"jancuk","spill":"hedeh","bestie":"lah","valid":"benar","zonk":"salah","skip":"kampret","kelar":"selesai",
 "simpen":"tulis","bongkar":"baca","simpen_json":"tulis_json","bongkar_json":"baca_json","impor":"angkut","waktu":"jam","gas_api":"kepo_internet","stalking":"kepo_internet","kirim_gosip":"kirim_api","parse_json":"jadi_json","kepo":"tanya","cetak":"hedeh","tampilkan":"hedeh"
}

def _load_extra():
    p="library/kosakata.json"
    if not os.path.exists(p): return {}
    try:
        data=json.load(open(p,encoding="utf-8"))
        raw = data.get("keywords", data) if isinstance(data, dict) else []
        extra={}
        if isinstance(raw, list):
            for entry in raw:
                if not isinstance(entry, dict): continue
                w=entry.get("word")
                if not isinstance(w,str): continue
                # format baru: {"word": target, "aliases": [alias...]}
                for a in entry.get("aliases", []):
                    if isinstance(a,str) and a not in BASE_ALIASES:
                        extra[a]=w
                # format alias_of: {"word": alias, "alias_of": target}
                ao=entry.get("alias_of")
                if isinstance(ao,str) and w not in BASE_ALIASES:
                    extra[w]=ao
        elif isinstance(raw, dict):
            for k,v in raw.items():
                if isinstance(v,str) and k not in BASE_ALIASES:
                    if v in CANONICAL or v in set(BASE_ALIASES.values()):
                        extra[k]=v
        return extra
    except Exception as e:
        print(f"warn kosakata.json load fail: {e}")
        return {}

KEYWORD_ALIASES = {**BASE_ALIASES, **_load_extra()}
ALIASES = KEYWORD_ALIASES
KEYWORDS = CANONICAL
VOCAB = KEYWORD_ALIASES

SPEC=[('STRING',r'"[^"\n]*"|\'[^\']*\''),
 ('NUMBER',r'\d+(\.\d+)?'),('IDENT',r'[A-Za-z_][A-Za-z0-9_]*'),
 ('OP',r'==|!=|<=|>=|//|[+\-*/%=<>():,\[\]{}]'),
 ('NEWLINE',r'\n'),('SKIP',r'[ \t\r]+'),('COMMENT',r'#.*'),('MISMATCH',r'.'),]
RE=re.compile('|'.join(f'(?P<{n}>{r})' for n,r in SPEC))

def lex(src):
    out=[]; line=1; ls=0
    for m in RE.finditer(src):
        kind=m.lastgroup; val=m.group(); col=m.start()-ls+1
        if kind=='NEWLINE': line+=1; ls=m.end(); continue
        if kind in ('SKIP','COMMENT'): continue
        if kind=='MISMATCH': raise SyntaxError(f"ilegal {val!r} baris {line}")
        if kind=='IDENT':
            if val in KEYWORD_ALIASES:
                mapped=KEYWORD_ALIASES[val]
                if mapped in CANONICAL: out.append(Token('KEYWORD',mapped,line,col))
                else: out.append(Token('IDENT',mapped,line,col))
            elif val in CANONICAL: out.append(Token('KEYWORD',val,line,col))
            else: out.append(Token('IDENT',val,line,col))
        else: out.append(Token(kind,val,line,col))
    return out
