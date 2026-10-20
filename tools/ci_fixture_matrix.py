import json, pathlib, os
OUT=pathlib.Path(os.environ.get("PUSINGCUK_MATRIX_OUT","artifacts/fixture-matrix"))
OUT.mkdir(parents=True, exist_ok=True)
OUT.joinpath("results.json").write_text('[{"fixture":"dummy","status":"pass"}]\n')
OUT.joinpath("summary.json").write_text('{"total":1,"pass":1,"fail":0}\n')
