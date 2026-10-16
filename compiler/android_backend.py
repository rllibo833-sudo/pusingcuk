"""Android Activity backend for a small, explicit .cuk subset."""
import json
import re
from compiler.ir import validate


class AndroidBackendError(ValueError):
    """Unsupported construct in the Android target."""


def generate(document, package_name="org.pusingcuk.generated",
             class_name="CukGeneratedActivity"):
    validate(document)
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*", package_name):
        raise AndroidBackendError("nama package tidak valid")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", class_name):
        raise AndroidBackendError("nama class tidak valid")
    variables, lines = {}, []

    def expression(node):
        kind, f, line = node["kind"], node["fields"], node.get("line", 0)
        if kind == "Literal":
            v = f["value"]
            if v is None: return "null"
            if isinstance(v, bool): return f"Boolean.valueOf({str(v).lower()})"
            if isinstance(v, int):
                if abs(v) > 9007199254740991: raise AndroidBackendError(f"baris {line}: integer di luar rentang aman")
                return f"Long.valueOf({v}L)"
            if isinstance(v, float): return f"Double.valueOf({json.dumps(v)})"
            if isinstance(v, str): return json.dumps(v, ensure_ascii=True)
            raise AndroidBackendError(f"baris {line}: literal tidak didukung")
        if kind == "Variable":
            name = f["name"]
            if name not in variables: raise AndroidBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
            return variables[name]
        if kind == "Binary":
            op = f["op"]; a, b = expression(f["left"]), expression(f["right"])
            if op == "+": return f"pcAdd({a}, {b})"
            if op in ("-", "*", "/"):
                return f"pc{ {'-':'Sub','*':'Mul','/':'Div'}[op] }({a}, {b})"
            if op in ("==", "!="):
                eq = f"java.util.Objects.equals({a}, {b})"
                return eq if op == "==" else f"!({eq})"
            if op in ("<", "<=", ">", ">="): return f"pcCompare({a}, {b}, {json.dumps(op)})"
            raise AndroidBackendError(f"baris {line}: operator {op!r} belum didukung")
        if kind == "Call" and f["name"] == "teks" and len(f["args"]) == 1:
            return f"pcText({expression(f['args'][0])})"
        raise AndroidBackendError(f"baris {line}: ekspresi {kind!r} belum didukung Android")

    for node in document["program"]["fields"]["body"]:
        kind, f, line = node["kind"], node["fields"], node.get("line", 0)
        if kind == "Declare":
            name = f["name"]
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or name in variables:
                raise AndroidBackendError(f"baris {line}: nama variabel tidak valid/duplikat")
            target = "pcv_" + name
            value = expression(f["value"])
            variables[name] = target
            lines.append(f"            Object {target} = {value};")
        elif kind == "Assign":
            name = f["name"]
            if name not in variables: raise AndroidBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
            lines.append(f"            {variables[name]} = {expression(f['value'])};")
        elif kind == "Print":
            lines.append(f"            output.append(pcText({expression(f['value'])})).append('\\n');")
        else:
            raise AndroidBackendError(f"baris {line}: pernyataan {kind!r} belum didukung Android; tidak ada fallback")
    body = "\n".join(lines) or '            output.append("Program .cuk kosong");'
    return f'''package {package_name};
import android.app.Activity;
import android.os.Bundle;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.Objects;

public final class {class_name} extends Activity {{
    @Override public void onCreate(Bundle state) {{
        super.onCreate(state);
        StringBuilder output = new StringBuilder();
        TextView screen = new TextView(this);
        screen.setTextSize(16);
        screen.setTextIsSelectable(true);
        ScrollView scroll = new ScrollView(this);
        scroll.addView(screen);
        setContentView(scroll);
        try {{
{body}
            screen.setText(output.toString());
        }} catch (RuntimeException error) {{
            screen.setText(output.toString() + "\\nKesalahan .cuk: " + error.getMessage());
        }}
    }}
    private static double pcNum(Object x) {{
        if (x instanceof Number) return ((Number)x).doubleValue();
        throw new IllegalArgumentException("operasi membutuhkan angka");
    }}
    private static Object pcAdd(Object a, Object b) {{
        if (a instanceof String && b instanceof String) return (String)a + (String)b;
        return Double.valueOf(pcNum(a) + pcNum(b));
    }}
    private static Object pcSub(Object a, Object b) {{ return Double.valueOf(pcNum(a) - pcNum(b)); }}
    private static Object pcMul(Object a, Object b) {{ return Double.valueOf(pcNum(a) * pcNum(b)); }}
    private static Object pcDiv(Object a, Object b) {{
        if (pcNum(b) == 0.0) throw new ArithmeticException("pembagian dengan nol");
        return Double.valueOf(pcNum(a) / pcNum(b));
    }}
    private static boolean pcCompare(Object a, Object b, String op) {{
        int c;
        if (a instanceof Number && b instanceof Number) c = Double.compare(pcNum(a), pcNum(b));
        else if (a instanceof String && b instanceof String) c = ((String)a).compareTo((String)b);
        else throw new IllegalArgumentException("perbandingan membutuhkan tipe sejenis");
        switch (op) {{ case "<": return c < 0; case "<=": return c <= 0; case ">": return c > 0; default: return c >= 0; }}
    }}
    private static String pcText(Object v) {{
        if (v == null) return "None";
        if (Boolean.TRUE.equals(v)) return "okelah";
        if (Boolean.FALSE.equals(v)) return "tidak";
        if (v instanceof Double && ((Double)v).doubleValue() == Math.rint(((Double)v).doubleValue()))
            return Long.toString(((Double)v).longValue());
        return String.valueOf(v);
    }}
}}
'''
