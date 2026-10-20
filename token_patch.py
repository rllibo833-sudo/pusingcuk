import pathlib
txt=pathlib.Path("lexer.py").read_text()
txt=txt.replace(
"class Token:\n    def __init__(self, kind, value, baris, kolom):\n        self.kind = kind\n        self.value = value\n        self.baris = baris\n        self.kolom = kolom\n        self.type = kind",
"class Token:\n    def __init__(self, kind, value, baris, kolom):\n        self.kind = kind\n        self.value = value\n        self.baris = baris\n        self.kolom = kolom\n        self.line = baris\n        self.column = kolom\n        self.lineno = baris\n        self.type = kind\n    @property\n    def col(self):\n        return self.kolom"
)
pathlib.Path("lexer.py").write_text(txt)
print("patched")
