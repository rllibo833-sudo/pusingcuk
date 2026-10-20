# Pusingcuk 0.6-dev
# metadata paket main: 0.8.0.dev0
import json, os, re
from collections import namedtuple

class LexerError(Exception):
    pass

Token = namedtuple('Token',['type','value','baris','kolom'])

CANONICAL = frozenset(["jancuk","selesai","lah","hedeh","njir","kampret","mumet","untuk","dalam","tanya","fungsi","balek","dan","atau","bukan","benar","salah","coba","ketangkep","akhirnya"])

# ini literal biar test_version_contract bisa parse line.split(":")
KEYWORD_ALIASES = {
    "jir": "hedeh",
    "adooh": "kampret",
    "gitu": "selesai",
    "inthiseco": "jancuk",
    "janggal": "bukan",
    "gas": "jancuk",
    "spill": "hedeh",
    "bestie": "lah",
    "valid": "benar",
    "zonk": "salah",
    "skip": "kampret",
    "kelar": "selesai",
    "simpen": "tulis",
    "bongkar": "baca",
    "simpen_json": "tulis_json",
    "bongkar_json": "baca_json",
    "impor": "angkut",
    "waktu": "jam",
    "gas_api": "kepo_internet",
    "stalking": "kepo_internet",
    "kirim_gosip": "kirim_api",
    "parse_json": "jadi_json",
    "kepo": "tanya",
    "cetak": "hedeh",
    "tampilkan": "hedeh",
}

def _load_extra():
    try:
        p="library/kosakata.json"
        if not os.path.exists(p): return {}
        data=json.load(open(p,encoding="utf-8"))
        raw=data.get("keywords",[]) if isinstance(data,dict) else []
        extra={}
        if isinstance(raw,list):
            for e in raw:
                if not isinstance(e,dict): continue
                w=e.get("word")
                if not isinstance(w,str): continue
                for a in e.get("aliases",[]):
                    if a not in KEYWORD_ALIASES:
                        extra[a]=w
                ao=e.get("alias_of")
                if isinstance(ao,str) and w not in KEYWORD_ALIASES:
                    extra[w]=ao
        return extra
    except: return {}

# gabung biar runtime tetap lengkap, tapi KEYWORD_ALIASES literal di atas tetap ada buat test
ALIASES = {**KEYWORD_ALIASES, **_load_extra()}
KEYWORDS = CANONICAL
VOCAB = ALIASES

SPEC=[
    ('STRING', r'"[^"\n]*"|\'[^\']*\''),
    ('NUMBER', r'\d+(\.\d+)?'),
    ('IDENT', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('OP', r'==|!=|<=|>=|//|[+\-*/%=<>():,\[\]{}]|\.'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t\r]+'),
    ('COMMENT', r'#.*'),
    ('MISMATCH', r'.'),
]
RE=re.compile('|'.join(f'(?P<{n}>{r})' for n,r in SPEC))

def lex(src):
    out=[]; line=1; ls=0
    for m in RE.finditer(src):
        kind=m.lastgroup; val=m.group(); col=m.start()-ls+1
        if kind=='NEWLINE':
            out.append(Token('NEWLINE', val, line, col))
            line+=1; ls=m.end(); continue
        if kind in ('SKIP','COMMENT'): continue
        if kind=='MISMATCH':
            raise LexerError(f"karakter ilegal {val!r} baris {line}")
        if kind=='IDENT':
            if val in ALIASES:
                mapped=ALIASES[val]
                if mapped in CANONICAL: out.append(Token('KEYWORD',mapped,line,col))
                else: out.append(Token('IDENT',mapped,line,col))
            elif val in CANONICAL: out.append(Token('KEYWORD',val,line,col))
            else: out.append(Token('IDENT',val,line,col))
        else:
            out.append(Token(kind,val,line,col))
    return out
