# Pusingcuk 0.6-dev
# metadata paket main: 0.8.0.dev0
import re
class Token:
    def __init__(self, type_, value, baris, kolom):
        self.type=type_; self.kind=type_; self.value=value; self.baris=baris; self.kolom=kolom

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
    "kepo": "tanya"
}

_RUNTIME_EXTRA = {"cetak": "hedeh", "tampilkan": "hedeh"}
CANONICAL = frozenset(["jancuk","selesai","lah","hedeh","njir","kampret","mumet","untuk","dalam","tanya","fungsi","balek","dan","atau","bukan","benar","salah","coba","ketangkep","akhirnya"])
ALIASES = {**KEYWORD_ALIASES, **_RUNTIME_EXTRA}
KEYWORDS = CANONICAL
SPEC=[('STRING',r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''),
('NUMBER',r'\d+(?:\.\d+)?'),('IDENT',r'[A-Za-z_][A-Za-z0-9_]*'),
('OP',r'==|!=|<=|>=|//|[+\-*/%=<>():,\[\]{}.]'),
('NEWLINE',r'\n'),('SKIP',r'[ \t\r]+'),('COMMENT',r'#.*'),('MISMATCH',r'.')]
RE=re.compile('|'.join(f'(?P<{n}>{p})' for n,p in SPEC))
def lex(src):
    out=[]; baris=1
    for m in RE.finditer(src):
        kind=m.lastgroup; val=m.group()
        if kind=='NEWLINE':
            out.append(Token('NEWLINE',val,baris,1)); baris+=1; continue
        if kind in ('SKIP','COMMENT','MISMATCH'): continue
        if kind=='IDENT':
            low=val.lower()
            if low in ALIASES: low=ALIASES[low]
            if low in KEYWORDS: out.append(Token(low.upper(),low,baris,1))
            else: out.append(Token('IDENT',val,baris,1))
        else: out.append(Token(kind,val,baris,1))
    out.append(Token('EOF','',baris,1))
    return out
