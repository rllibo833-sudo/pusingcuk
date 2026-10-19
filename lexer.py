import json
import os
import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'baris', 'kolom'])

CANONICAL = frozenset([
    "jancuk","selesai","lah","hedeh","njir","kampret",
    "mumet","untuk","dalam","tanya","fungsi","balek",
    "dan","atau","bukan","benar","salah","coba","ketangkep","akhirnya"
])

# 23 alias frozen 0.6-dev
BASE_ALIASES = {
    # inti 12
    "jir":"hedeh","adooh":"kampret","gitu":"selesai","inthiseco":"jancuk",
    "janggal":"bukan","gas":"jancuk","spill":"hedeh","bestie":"lah",
    "valid":"benar","zonk":"salah","skip":"kampret","kelar":"selesai",
    # api 11
    "simpen":"tulis","bongkar":"baca","simpen_json":"tulis_json",
    "bongkar_json":"baca_json","impor":"angkut","waktu":"jam",
    "gas_api":"kepo_internet","stalking":"kepo_internet",
    "kirim_gosip":"kirim_api","parse_json":"jadi_json","kepo":"tanya"
}

def _load_extra():
    path = "library/kosakata.json"
    if not os.path.exists(path):
        return {}
    try:
        data = json.load(open(path, encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        extra = {}
        allowed_values = CANONICAL | set(BASE_ALIASES.values())
        for k,v in data.items():
            if not isinstance(k, str) or not isinstance(v, str):
                continue
            if k in BASE_ALIASES:
                continue
            if v in allowed_values:
                extra[k] = v
        return extra
    except Exception:
        return {}

KEYWORD_ALIASES = {**BASE_ALIASES, **_load_extra()}
# FIX KRITIS: KEYWORDS cuma canonical, bukan values builtin
KEYWORDS = CANONICAL

TOKEN_SPEC = [
    ('STRING', r'"[^"\n]*"|\'[^\']*\''),
    ('NUMBER', r'\d+(\.\d+)?'),
    ('IDENT',  r'[A-Za-z_][A-Za-z0-9_]*'),
    ('OP',     r'==|!=|<=|>=|//|[+\-*/%=<>():,\[\]{}]'),
    ('NEWLINE',r'\n'),
    ('SKIP',   r'[ \t\r]+'),
    ('COMMENT',r'#.*'),
    ('MISMATCH',r'.'),
]

tok_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))

def lex(source):
    tokens = []
    line_num = 1
    line_start = 0
    for mo in tok_regex.finditer(source):
        kind = mo.lastgroup
        value = mo.group()
        col = mo.start() - line_start + 1
        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
            continue
        elif kind in ('SKIP','COMMENT'):
            continue
        elif kind == 'IDENT':
            mapped = KEYWORD_ALIASES.get(value, value)
            if mapped in CANONICAL:
                kind = 'KEYWORD'
                value = mapped
            else:
                # builtin alias -> value tetap builtin (IDENT)
                # cth: kirim_gosip -> kirim_api (IDENT)
                kind = 'KEYWORD' if value in CANONICAL or value in KEYWORD_ALIASES and KEYWORD_ALIASES[value] in CANONICAL and value in CANONICAL else 'IDENT'
                # simplifikasi: cek mapped
                if mapped in CANONICAL:
                    kind = 'KEYWORD'
                    value = mapped
                else:
                    # kalau alias API, kembalikan mapped sebagai IDENT
                    if value in KEYWORD_ALIASES:
                        kind = 'IDENT'
                        value = mapped
                    else:
                        kind = 'IDENT'
        elif kind == 'MISMATCH':
            raise SyntaxError(f"karakter ilegal {value!r} baris {line_num}")
        tokens.append(Token(kind, value, line_num, col))
    # second pass: ensure alias core mapped benar
    fixed = []
    for t in tokens:
        if t.type == 'IDENT' and t.value in KEYWORD_ALIASES:
            mapped = KEYWORD_ALIASES[t.value]
            if mapped in CANONICAL:
                fixed.append(Token('KEYWORD', mapped, t.baris, t.kolom))
            else:
                fixed.append(Token('IDENT', mapped, t.baris, t.kolom))
        else:
            fixed.append(t)
    return fixed
