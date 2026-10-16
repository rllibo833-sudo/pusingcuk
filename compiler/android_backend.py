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
    inputs = []

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
        if kind == "Unary":
            op, value = f["op"], expression(f["value"])
            if op == "-": return f"pcNeg({value})"
            if op in ("!", "tidak"): return f"!pcTruthy({value})"
            raise AndroidBackendError(f"baris {line}: operator unary {op!r} belum didukung")
        if kind == "List":
            values = ", ".join(expression(item) for item in f["items"])
            return f"pcList({values})" if values else "new java.util.ArrayList<>()"
        if kind == "Dict":
            pairs = []
            for pair in f["items"]:
                if not isinstance(pair, list) or len(pair) != 2:
                    raise AndroidBackendError(f"baris {line}: bentuk kamus IR tidak valid")
                pairs.extend((expression(pair[0]), expression(pair[1])))
            return f"pcMapOf({', '.join(pairs)})" if pairs else "new java.util.LinkedHashMap<>()"
        if kind == "Index":
            return f"pcGet({expression(f['collection'])}, {expression(f['index'])})"
        if kind == "Binary":
            op = f["op"]; a, b = expression(f["left"]), expression(f["right"])
            if op == "+": return f"pcAdd({a}, {b})"
            if op in ("-", "*", "/", "//", "%"):
                return f"pc{ {'-':'Sub','*':'Mul','/':'Div','//':'FloorDiv','%':'Mod'}[op] }({a}, {b})"
            if op in ("==", "!="):
                eq = f"java.util.Objects.equals({a}, {b})"
                return eq if op == "==" else f"!({eq})"
            if op in ("<", "<=", ">", ">="): return f"pcCompare({a}, {b}, {json.dumps(op)})"
            if op in ("dan", "atau"):
                return f"Boolean.valueOf({'pcTruthy(' + a + ') && pcTruthy(' + b + ')' if op == 'dan' else 'pcTruthy(' + a + ') || pcTruthy(' + b + ')'})"
            raise AndroidBackendError(f"baris {line}: operator {op!r} belum didukung")
        if kind == "Call":
            name, args = f["name"], [expression(arg) for arg in f["args"]]
            builtins = {"teks": ("pcText", 1), "panjang": ("pcLength", 1),
                        "bilangan": ("pcInteger", 1), "desimal": ("pcNum", 1)}
            if name in builtins and len(args) == builtins[name][1]:
                return f"{builtins[name][0]}({', '.join(args)})"
        raise AndroidBackendError(f"baris {line}: ekspresi {kind!r} belum didukung Android")

    def walk_statements(items):
        for item in items:
            kind, fields = item["kind"], item["fields"]
            if kind == "Declare":
                name = fields["name"]
                if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                    raise AndroidBackendError(f"baris {item.get('line', 0)}: nama variabel tidak valid")
                if name in variables:
                    raise AndroidBackendError(f"baris {item.get('line', 0)}: deklarasi variabel {name!r} duplikat")
                variables[name] = "pcv_" + name
            elif kind == "Input":
                name = fields["name"]
                prompt = fields["prompt"]
                if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                    raise AndroidBackendError(f"baris {item.get('line', 0)}: nama input tidak valid")
                if name in variables:
                    raise AndroidBackendError(f"baris {item.get('line', 0)}: nama input {name!r} bertabrakan dengan variabel")
                if not isinstance(prompt, dict) or prompt.get("kind") != "Literal" or not isinstance(prompt.get("fields", {}).get("value"), str):
                    raise AndroidBackendError(f"baris {item.get('line', 0)}: prompt input Android harus berupa teks literal")
                variables[name] = "pcv_" + name
                inputs.append({"name": name, "prompt": prompt["fields"]["value"]})
            elif kind == "If":
                walk_statements(fields["then_body"])
                walk_statements(fields["else_body"])
            elif kind == "While":
                walk_statements(fields["body"])
            elif kind == "For":
                name = fields["name"]
                if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                    raise AndroidBackendError(f"baris {item.get('line', 0)}: nama iterasi tidak valid")
                if name in variables:
                    raise AndroidBackendError(f"baris {item.get('line', 0)}: nama iterasi {name!r} bertabrakan dengan variabel")
                variables[name] = "pcv_" + name
                walk_statements(fields["body"])

    walk_statements(document["program"]["fields"]["body"])
    for target in variables.values():
        lines.append(f"            Object {target} = null;")

    def emit(items, indent="            "):
        for node in items:
            kind, f, line = node["kind"], node["fields"], node.get("line", 0)
            if kind == "Input":
                pass  # Values are read from generated native fields before execution.
            elif kind == "Declare":
                lines.append(f"{indent}{variables[f['name']]} = {expression(f['value'])};")
            elif kind == "Assign":
                name = f["name"]
                if name not in variables:
                    raise AndroidBackendError(f"baris {line}: variabel {name!r} belum dideklarasikan")
                lines.append(f"{indent}{variables[name]} = {expression(f['value'])};")
            elif kind == "Print":
                lines.append(f"{indent}output.append(pcText({expression(f['value'])})).append('\\n');")
            elif kind == "If":
                lines.append(f"{indent}if (pcTruthy({expression(f['condition'])})) {{")
                emit(f["then_body"], indent + "    ")
                if f["else_body"]:
                    lines.append(f"{indent}}} else {{")
                    emit(f["else_body"], indent + "    ")
                lines.append(f"{indent}}}")
            elif kind == "While":
                lines.append(f"{indent}while (pcTruthy({expression(f['condition'])})) {{")
                emit(f["body"], indent + "    ")
                lines.append(f"{indent}}}")
            elif kind == "For":
                name = variables[f["name"]]
                loop_id = emit.loop_id
                emit.loop_id += 1
                item_name = f"pcLoopItem{loop_id}"
                lines.append(f"{indent}for (Object {item_name} : pcIterable({expression(f['iterable'])})) {{")
                lines.append(f"{indent}    {name} = {item_name};")
                emit(f["body"], indent + "    ")
                lines.append(f"{indent}}}")
            elif kind == "IndexAssign":
                lines.append(f"{indent}pcSet({expression(f['collection'])}, {expression(f['index'])}, {expression(f['value'])});")
            else:
                raise AndroidBackendError(f"baris {line}: pernyataan {kind!r} belum didukung Android; tidak ada fallback")

    emit.loop_id = 0
    emit(document["program"]["fields"]["body"])
    input_fields_add = "\n".join(f"        inputFields.add(input{i});" for i in range(len(inputs)))
    input_assignments = "\n".join(f"            {variables[item['name']]} = inputFields.get({i}).getText().toString();" for i, item in enumerate(inputs))
    input_ui = "\n".join(f"        EditText input{i} = new EditText(this); input{i}.setSingleLine(true); input{i}.setHint({json.dumps(item['prompt'], ensure_ascii=True)}); layout.addView(input{i});" for i, item in enumerate(inputs))
    body = "\n".join(lines) or '            output.append("Program .cuk kosong");'
    return f'''package {package_name};
import android.app.Activity;
import android.os.Bundle;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.EditText;
import android.widget.Button;
import android.widget.LinearLayout;
import java.util.Objects;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class {class_name} extends Activity {{
    @Override public void onCreate(Bundle state) {{
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int pad = (int)(16 * getResources().getDisplayMetrics().density);
        layout.setPadding(pad, pad, pad, pad);
{input_ui}
{input_fields_add}
        Button run = new Button(this);
        run.setText("Jalankan");
        layout.addView(run);
        TextView screen = new TextView(this);
        screen.setTextSize(16);
        screen.setTextIsSelectable(true);
        ScrollView scroll = new ScrollView(this);
        scroll.addView(screen);
        layout.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(layout);
        run.setOnClickListener(view -> {{
            StringBuilder output = new StringBuilder();
            try {{
{body}
{input_assignments}
            }} catch (RuntimeException error) {{
                output.append("Kesalahan .cuk: ").append(error.getMessage());
            }}
            screen.setText(output.toString());
        }});
    }}
    private static boolean pcTruthy(Object value) {{
        if (value == null || Boolean.FALSE.equals(value)) return false;
        if (value instanceof Number) return ((Number)value).doubleValue() != 0.0;
        if (value instanceof String) return !((String)value).isEmpty();
        return true;
    }}
    private static Object pcNeg(Object value) {{ return pcFinite(-pcNum(value)); }}
    private static List<Object> pcList(Object... values) {{
        List<Object> result = new ArrayList<>();
        java.util.Collections.addAll(result, values);
        return result;
    }}
    private static Map<Object,Object> pcMap() {{ return new LinkedHashMap<>(); }}
    private static Object pcPut(Map<Object,Object> map, Object key, Object value) {{ map.put(key, value); return value; }}
    private static Map<Object,Object> pcMapOf(Object... ignored) {{
        Map<Object,Object> result = new LinkedHashMap<>();
        for (int i = 0; i + 1 < ignored.length; i += 2) result.put(ignored[i], ignored[i + 1]);
        return result;
    }}
    private static Object pcGet(Object collection, Object key) {{
        if (collection instanceof List && key instanceof Number) {{
            int i = ((Number)key).intValue(); List<?> list = (List<?>)collection;
            if (i < 0 || i >= list.size()) throw new IndexOutOfBoundsException("indeks di luar batas");
            return list.get(i);
        }}
        if (collection instanceof String && key instanceof Number) {{
            int i = ((Number)key).intValue(); String value = (String)collection;
            if (i < 0 || i >= value.length()) throw new IndexOutOfBoundsException("indeks di luar batas");
            return String.valueOf(value.charAt(i));
        }}
        if (collection instanceof Map) {{
            Map<?,?> map = (Map<?,?>)collection;
            if (!map.containsKey(key)) throw new IllegalArgumentException("kunci kamus tidak ditemukan");
            return map.get(key);
        }}
        throw new IllegalArgumentException("nilai tidak dapat diindeks");
    }}
    @SuppressWarnings("unchecked")
    private static Object pcSet(Object collection, Object key, Object value) {{
        if (collection instanceof List && key instanceof Number) {{
            int i = ((Number)key).intValue(); List<Object> list = (List<Object>)collection;
            if (i < 0 || i >= list.size()) throw new IndexOutOfBoundsException("indeks di luar batas");
            list.set(i, value); return value;
        }}
        if (collection instanceof Map) {{ ((Map<Object,Object>)collection).put(key, value); return value; }}
        throw new IllegalArgumentException("target indeks tidak dapat diubah");
    }}
    private static Iterable<?> pcIterable(Object value) {{
        if (value instanceof Iterable) return (Iterable<?>)value;
        if (value instanceof Map) return ((Map<?,?>)value).keySet();
        if (value instanceof String) {{
            List<String> chars = new ArrayList<>();
            for (int i = 0; i < ((String)value).length(); i++) chars.add(String.valueOf(((String)value).charAt(i)));
            return chars;
        }}
        throw new IllegalArgumentException("nilai tidak dapat diulang");
    }}
    private static int pcLength(Object value) {{
        if (value instanceof String) return ((String)value).length();
        if (value instanceof List) return ((List<?>)value).size();
        if (value instanceof Map) return ((Map<?,?>)value).size();
        throw new IllegalArgumentException("panjang() membutuhkan teks, daftar, atau kamus");
    }}
    private static Long pcInteger(Object value) {{
        if (value instanceof Number) return Long.valueOf(((Number)value).longValue());
        if (value instanceof String) return Long.valueOf(Long.parseLong(((String)value).trim()));
        throw new IllegalArgumentException("bilangan() membutuhkan angka atau teks integer");
    }}
    private static double pcNum(Object x) {{
        if (x instanceof Number) {{
            double value = ((Number)x).doubleValue();
            if (Double.isFinite(value)) return value;
            throw new ArithmeticException("operasi angka non-finite");
        }}
        throw new IllegalArgumentException("operasi membutuhkan angka");
    }}
    private static Object pcAdd(Object a, Object b) {{
        if (a instanceof String && b instanceof String) return (String)a + (String)b;
        return pcFinite(pcNum(a) + pcNum(b));
    }}
    private static Object pcSub(Object a, Object b) {{ return pcFinite(pcNum(a) - pcNum(b)); }}
    private static Object pcMul(Object a, Object b) {{ return pcFinite(pcNum(a) * pcNum(b)); }}
    private static Object pcDiv(Object a, Object b) {{
        double divisor = pcNum(b);
        if (divisor == 0.0) throw new ArithmeticException("pembagian dengan nol");
        return pcFinite(pcNum(a) / divisor);
    }}
    private static Object pcFloorDiv(Object a, Object b) {{ return pcFinite(Math.floor(pcNum(a) / pcNum(b))); }}
    private static Object pcMod(Object a, Object b) {{
        double divisor = pcNum(b); if (divisor == 0.0) throw new ArithmeticException("modulo dengan nol");
        return pcFinite(((pcNum(a) % divisor) + divisor) % divisor);
    }}
    private static Double pcFinite(double value) {{
        if (!Double.isFinite(value)) throw new ArithmeticException("operasi angka non-finite");
        return Double.valueOf(value);
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
        if (v instanceof Double) {
            double number = ((Double)v).doubleValue();
            // Never cast an out-of-range or non-finite double to long for display.
            if (Double.isFinite(number) && number == Math.rint(number)
                    && Math.abs(number) <= 9007199254740991.0)
                return Long.toString((long) number);
        }
        return String.valueOf(v);
    }}
}}
'''
