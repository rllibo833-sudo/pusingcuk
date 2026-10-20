import pathlib
p = pathlib.Path("SPEC.md").read_text()
if "koar2" not in p:
    p = p.replace("hedeh", "hedeh, koar2")
    pathlib.Path("SPEC.md").write_text(p)
    print("SPEC.md patched")
else:
    print("already has koar2")
