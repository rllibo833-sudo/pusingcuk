"""Experimental standalone Go backend for the supported PusingCuk core subset."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from compiler.ir import from_source, validate


class GoBackendError(ValueError):
    """Source construct is outside the explicitly supported Go subset."""


SUPPORTED = {
    "Program", "Declare", "Assign", "IndexAssign", "Print", "If", "While",
    "For", "Function", "Return", "Literal", "Variable", "Unary", "Binary",
    "List", "Dict", "Index", "Call", "Expr",
}


RUNTIME = r'''package main

import (
    "fmt"
    "math"
    "os"
    "strconv"
    "strings"
    "unicode/utf8"
)

type PCError struct { Line int; Message string }
func pcFail(line int, message string) { panic(PCError{Line: line, Message: message}) }
func pcRecover() {
    if value := recover(); value != nil {
        if err, ok := value.(PCError); ok {
            fmt.Fprintf(os.Stderr, "Kesalahan runtime: Baris %d: %s\n", err.Line, err.Message)
        } else {
            fmt.Fprintf(os.Stderr, "Kesalahan runtime: %v\n", value)
        }
        os.Exit(1)
    }
}
var pcSteps = 0
func pcStep(line int) {
    pcSteps++
    if pcSteps > 50000 { pcFail(line, "batas eksekusi tercapai (50000 langkah)") }
}
type PCPair struct { Key any; Value any }
type PCDict struct { Entries []PCPair }
type PCRange struct { Values []any }
type PCFunction struct { Name string; Params []string; Closure *PCEnv }
type PCEnv struct { Parent *PCEnv; Values map[string]any }
func pcNewEnv(parent *PCEnv) *PCEnv { return &PCEnv{Parent: parent, Values: map[string]any{}} }
func (e *PCEnv) define(name string, value any, line int) {
    if _, exists := e.Values[name]; exists { pcFail(line, "variabel '"+name+"' sudah dibuat") }
    e.Values[name] = value
}
func (e *PCEnv) loopVar(name string, value any, line int) {
    if _, exists := e.Values[name]; exists { e.Values[name] = value; return }
    e.Values[name] = value
}
func (e *PCEnv) get(name string, line int) any {
    if value, ok := e.Values[name]; ok { return value }
    if e.Parent != nil { return e.Parent.get(name, line) }
    pcFail(line, "nama belum didefinisikan: "+name)
    return nil
}
func (e *PCEnv) set(name string, value any, line int) {
    if _, ok := e.Values[name]; ok { e.Values[name] = value; return }
    if e.Parent != nil { e.Parent.set(name, value, line); return }
    pcFail(line, "variabel belum didefinisikan: "+name)
}
func pcNumber(value any, name string, line int) float64 {
    number, ok := value.(float64)
    if !ok || math.IsNaN(number) || math.IsInf(number, 0) { pcFail(line, name+" membutuhkan angka finite") }
    return number
}
func pcSafe(name string, value float64, line int) float64 {
    if math.IsNaN(value) || math.IsInf(value, 0) { pcFail(line, name+": hasil angka non-finite") }
    if value == math.Trunc(value) && math.Abs(value) > 9007199254740991 { pcFail(line, name+": integer di luar rentang aman") }
    return value
}
func pcLiteral(value float64, line int) any {
    if math.IsNaN(value) || math.IsInf(value, 0) { pcFail(line, "angka non-finite") }
    if value == math.Trunc(value) && math.Abs(value) > 9007199254740991 { pcFail(line, "angka di luar rentang aman") }
    return value
}
func pcString(value any) string {
    switch v := value.(type) {
    case nil: return "None"
    case bool: if v { return "okelah" }; return "tidak"
    case string: return v
    case float64:
        if v == 0 { return "0" }
        if v == math.Trunc(v) && math.Abs(v) <= 9007199254740991 { return strconv.FormatInt(int64(v), 10) }
        return strconv.FormatFloat(v, 'g', -1, 64)
    case []any:
        parts := make([]string, len(v)); for i, item := range v { parts[i] = pcString(item) }
        return "[" + strings.Join(parts, ", ") + "]"
    case *PCRange:
        parts := make([]string, len(v.Values)); for i, item := range v.Values { parts[i] = pcString(item) }
        return "[" + strings.Join(parts, ", ") + "]"
    case *PCDict: return "[kamus]"
    case PCFunction: return "[fungsi]"
    default: return fmt.Sprint(value)
    }
}
func pcOut(value any) { fmt.Println(pcString(value)) }
func pcTruthy(value any) bool {
    switch v := value.(type) {
    case nil: return false
    case bool: return v
    case float64: return v != 0
    case string: return v != ""
    case []any: return len(v) > 0
    case *PCRange: return len(v.Values) > 0
    case *PCDict: return len(v.Entries) > 0
    default: return true
    }
}
func pcEq(left, right any) bool {
    switch a := left.(type) {
    case nil: return right == nil
    case bool: b, ok := right.(bool); return ok && a == b
    case float64: b, ok := right.(float64); return ok && a == b
    case string: b, ok := right.(string); return ok && a == b
    case []any:
        b, ok := right.([]any); if !ok || len(a) != len(b) { return false }
        for i := range a { if !pcEq(a[i], b[i]) { return false } }; return true
    case *PCRange:
        b, ok := right.(*PCRange); if !ok || len(a.Values) != len(b.Values) { return false }
        for i := range a.Values { if !pcEq(a.Values[i], b.Values[i]) { return false } }; return true
    case *PCDict: b, ok := right.(*PCDict); return ok && a == b
    case PCFunction: b, ok := right.(PCFunction); return ok && a.Name == b.Name && a.Closure == b.Closure
    default: return false
    }
}
func pcKeySupported(value any) bool {
    switch value.(type) { case string, bool, float64: return true; default: return false }
}
func (d *PCDict) get(key any, line int) any {
    if !pcKeySupported(key) { pcFail(line, "kunci kamus harus berupa teks, angka, atau boolean") }
    for _, pair := range d.Entries { if pcEq(pair.Key, key) { return pair.Value } }
    pcFail(line, "kunci kamus tidak ditemukan")
    return nil
}
func (d *PCDict) set(key, value any, line int) {
    if !pcKeySupported(key) { pcFail(line, "kunci kamus harus berupa teks, angka, atau boolean") }
    for i, pair := range d.Entries { if pcEq(pair.Key, key) { d.Entries[i].Value = value; return } }
    if len(d.Entries) >= 10000 { pcFail(line, "kamus melewati batas 10000 item") }
    d.Entries = append(d.Entries, PCPair{Key: key, Value: value})
}
func pcIndex(value any, index any, line int) any {
    switch v := value.(type) {
    case []any:
        raw := pcNumber(index, "indeks", line)
        if raw != math.Trunc(raw) || math.Abs(raw) > 9007199254740991 { pcFail(line, "indeks harus bilangan bulat") }
        i := int(raw); if i < 0 { i += len(v) }; if i < 0 || i >= len(v) { pcFail(line, "indeks di luar batas") }; return v[i]
    case string:
        raw := pcNumber(index, "indeks", line)
        if raw != math.Trunc(raw) || math.Abs(raw) > 9007199254740991 { pcFail(line, "indeks harus bilangan bulat") }
        chars := []rune(v); i := int(raw); if i < 0 { i += len(chars) }; if i < 0 || i >= len(chars) { pcFail(line, "indeks di luar batas") }; return string(chars[i])
    case *PCRange:
        raw := pcNumber(index, "indeks", line)
        if raw != math.Trunc(raw) || math.Abs(raw) > 9007199254740991 { pcFail(line, "indeks harus bilangan bulat") }
        i := int(raw); if i < 0 { pcFail(line, "indeks rentang harus bilangan bulat nonnegatif") }; if i >= len(v.Values) { pcFail(line, "indeks di luar batas") }; return v.Values[i]
    case *PCDict: return v.get(index, line)
    default: pcFail(line, "nilai tidak dapat diindeks")
    }
    return nil
}
func pcSetIndex(value any, index, next any, line int) {
    switch v := value.(type) {
    case []any:
        raw, ok := index.(float64); if !ok || raw != math.Trunc(raw) || math.Abs(raw) > 9007199254740991 { pcFail(line, "indeks harus bilangan bulat") }
        i := int(raw); if i < 0 { i += len(v) }; if i < 0 || i >= len(v) { pcFail(line, "indeks di luar batas") }; v[i] = next
    case *PCDict: v.set(index, next, line)
    default: pcFail(line, "assignment indeks hanya mendukung daftar dan kamus")
    }
}
func pcIter(value any, line int) []any {
    switch v := value.(type) {
    case []any: return v
    case *PCRange: return v.Values
    case string:
        chars := []rune(v); out := make([]any, len(chars)); for i, char := range chars { out[i] = string(char) }; return out
    case *PCDict:
        out := make([]any, len(v.Entries)); for i, pair := range v.Entries { out[i] = pair.Key }; return out
    default: pcFail(line, "nilai dalam untuk harus dapat diiterasi")
    }
    return nil
}
func pcRange(args []any, line int) *PCRange {
    if len(args) < 1 || len(args) > 3 { pcFail(line, "rentang() membutuhkan 1 sampai 3 argumen") }
    values := make([]int64, len(args))
    for i, arg := range args {
        number := pcNumber(arg, "rentang", line)
        if number != math.Trunc(number) || math.Abs(number) > 9007199254740991 { pcFail(line, "rentang() membutuhkan bilangan bulat aman") }
        values[i] = int64(number)
    }
    start, end, step := int64(0), values[0], int64(1)
    if len(values) >= 2 { start, end = values[0], values[1] }
    if len(values) == 3 { step = values[2] }
    if step == 0 { pcFail(line, "langkah rentang tidak boleh nol") }
    out := make([]any, 0)
    for n := start; (step > 0 && n < end) || (step < 0 && n > end); n += step {
        if len(out) >= 10000 { pcFail(line, "rentang melewati batas 10000 item") }
        out = append(out, float64(n))
    }
    return &PCRange{Values: out}
}
func pcAdd(a, b any, line int) any {
    switch x := a.(type) {
    case float64: y, ok := b.(float64); if !ok { pcFail(line, "operator + membutuhkan dua angka, dua teks, atau dua daftar") }; return pcSafe("operator +", x+y, line)
    case string: y, ok := b.(string); if !ok { pcFail(line, "operator + membutuhkan dua angka, dua teks, atau dua daftar") }; return x+y
    case []any: y, ok := b.([]any); if !ok { pcFail(line, "operator + membutuhkan dua angka, dua teks, atau dua daftar") }; out := append([]any{}, x...); return append(out, y...)
    default: pcFail(line, "operator + membutuhkan dua angka, dua teks, atau dua daftar")
    }
    return nil
}
func pcBinary(op string, a, b any, line int) any {
    if op == "+" { return pcAdd(a, b, line) }
    if op == "==" { return pcEq(a, b) }
    if op == "!=" { return !pcEq(a, b) }
    if op == "<" || op == "<=" || op == ">" || op == ">=" {
        if x, ok := a.(string); ok { y, yes := b.(string); if !yes { pcFail(line, "perbandingan membutuhkan tipe yang sama") }; switch op { case "<": return x < y; case "<=": return x <= y; case ">": return x > y; default: return x >= y } }
        x, y := pcNumber(a, "perbandingan", line), pcNumber(b, "perbandingan", line)
        switch op { case "<": return x < y; case "<=": return x <= y; case ">": return x > y; default: return x >= y }
    }
    x, y := pcNumber(a, "operator "+op, line), pcNumber(b, "operator "+op, line)
    switch op {
    case "-": return pcSafe("operator -", x-y, line)
    case "*":
        return pcSafe("operator *", x*y, line)
    case "/": if y == 0 { pcFail(line, "pembagian dengan nol") }; return pcSafe("operator /", x/y, line)
    case "//": if y == 0 { pcFail(line, "pembagian dengan nol") }; return pcSafe("operator //", math.Floor(x/y), line)
    case "%": if y == 0 { pcFail(line, "modulo dengan nol") }; return pcSafe("operator %", x-math.Floor(x/y)*y, line)
    default: pcFail(line, "operator tidak dikenal: "+op)
    }
    return nil
}
func pcUnary(op string, value any, line int) any {
    if op == "bukan" { return !pcTruthy(value) }
    if op == "-" { return pcSafe("operator unary -", -pcNumber(value, "operator unary -", line), line) }
    pcFail(line, "operator unary tidak dikenal: "+op); return nil
}
func pcAnd(left, right func() any) any { if !pcTruthy(left()) { return false }; return pcTruthy(right()) }
func pcOr(left, right func() any) any { if pcTruthy(left()) { return true }; return pcTruthy(right()) }
func pcArity(name string, args []any, min, max, line int) {
    if len(args) < min || len(args) > max { if min == max { pcFail(line, fmt.Sprintf("%s() membutuhkan %d argumen", name, min)) }; pcFail(line, fmt.Sprintf("%s() membutuhkan %d sampai %d argumen", name, min, max)) }
}
func pcCall(name string, args []any, env *PCEnv, line int) any {
    switch name {
    case "panjang":
        pcArity(name,args,1,1,line)
        switch v := args[0].(type) { case string: return float64(utf8.RuneCountInString(v)); case []any: return float64(len(v)); case *PCRange: return float64(len(v.Values)); case *PCDict: return float64(len(v.Entries)); default: pcFail(line,"panjang() membutuhkan teks, daftar, kamus, atau rentang") }
    case "rentang": return pcRange(args,line)
    case "teks": pcArity(name,args,1,1,line); return pcString(args[0])
    case "logika": pcArity(name,args,1,1,line); return pcTruthy(args[0])
    case "bilangan":
        pcArity(name,args,1,1,line)
        switch v := args[0].(type) {
        case float64: return pcSafe("bilangan",math.Trunc(v),line)
        case string: n,err:=strconv.ParseInt(strings.TrimSpace(v),10,64); if err!=nil || math.Abs(float64(n))>9007199254740991 { pcFail(line,"bilangan() nilai tidak valid") }; return float64(n)
        default: pcFail(line,"bilangan() membutuhkan angka atau teks integer")
        }
    case "desimal":
        pcArity(name,args,1,1,line)
        switch v:=args[0].(type) { case float64: return v; case string: n,err:=strconv.ParseFloat(strings.TrimSpace(v),64); if err!=nil || math.IsInf(n,0) || math.IsNaN(n) { pcFail(line,"desimal() nilai tidak valid") }; return n; default: pcFail(line,"desimal() membutuhkan angka atau teks angka") }
    case "mutlak": pcArity(name,args,1,1,line); return pcSafe("mutlak",math.Abs(pcNumber(args[0],name,line)),line)
    case "minimum","maksimum":
        pcArity(name,args,2,2,line); a,b:=pcNumber(args[0],name,line),pcNumber(args[1],name,line); if name=="minimum" { return math.Min(a,b) }; return math.Max(a,b)
    case "bulatkan":
        pcArity(name,args,1,1,line); n:=pcNumber(args[0],name,line); lo:=math.Floor(n); f:=n-lo; if f<0.5 { return pcSafe(name,lo,line) }; if f>0.5 { return pcSafe(name,lo+1,line) }; if math.Mod(lo,2)==0 { return pcSafe(name,lo,line) }; return pcSafe(name,lo+1,line)
    case "bawah","atas":
        pcArity(name,args,1,1,line); n:=pcNumber(args[0],name,line); if name=="bawah" { return pcSafe(name,math.Floor(n),line) }; return pcSafe(name,math.Ceil(n),line)
    case "akar":
        pcArity(name,args,1,1,line); n:=pcNumber(args[0],name,line); if n<0 { pcFail(line,"akar() domain tidak valid") }; return pcSafe(name,math.Sqrt(n),line)
    case "pangkat":
        pcArity(name,args,2,2,line); a,b:=pcNumber(args[0],name,line),pcNumber(args[1],name,line); if a<0 && b!=math.Trunc(b) || a==0 && b<0 { pcFail(line,"pangkat() domain tidak valid") }; return pcSafe(name,math.Pow(a,b),line)
    case "logaritma","log10":
        pcArity(name,args,1,1,line); n:=pcNumber(args[0],name,line); if n<=0 { pcFail(line,name+"() domain tidak valid") }; if name=="logaritma" { return pcSafe(name,math.Log(n),line) }; return pcSafe(name,math.Log10(n),line)
    case "sinus","kosinus":
        pcArity(name,args,1,1,line); n:=pcNumber(args[0],name,line); if name=="sinus" { return pcSafe(name,math.Sin(n),line) }; return pcSafe(name,math.Cos(n),line)
    case "jumlah":
        pcArity(name,args,1,1,line); values,ok:=args[0].([]any); if !ok { pcFail(line,"jumlah() membutuhkan daftar") }; total:=float64(0); for _,v:=range values { n:=pcNumber(v,name,line); if n==math.Trunc(n)&&math.Abs(n)>9007199254740991 { pcFail(line,"jumlah() integer input di luar rentang aman") }; total=pcSafe(name,total+n,line) }; return total
    case "rata_rata","median":
        pcArity(name,args,1,1,line); values,ok:=args[0].([]any); if !ok||len(values)==0 { pcFail(line,name+"() membutuhkan daftar tidak kosong") }; numbers:=make([]float64,len(values)); for i,v:=range values { n:=pcNumber(v,name,line); if n==math.Trunc(n)&&math.Abs(n)>9007199254740991 { pcFail(line,name+"() integer input di luar rentang aman") }; numbers[i]=n }
        if name=="rata_rata" { total:=float64(0); for _,n:=range numbers { total=pcSafe(name,total+n/float64(len(numbers)),line) }; return total }
        for i:=0;i<len(numbers);i++ { for j:=i+1;j<len(numbers);j++ { if numbers[j]<numbers[i] { numbers[i],numbers[j]=numbers[j],numbers[i] } } }
        mid:=len(numbers)/2; if len(numbers)%2==1 { return numbers[mid] }; return pcSafe(name,numbers[mid-1]/2+numbers[mid]/2,line)
    default:
        value:=env.get(name,line); fn,ok:=value.(PCFunction); if !ok { pcFail(line,"fungsi tidak dikenal: "+name) }; if len(args)!=len(fn.Params) { pcFail(line,fmt.Sprintf("%s() membutuhkan %d argumen",name,len(fn.Params))) }
        switch fn.Name {
__FUNCTION_DISPATCH__
        default: pcFail(line,"fungsi belum dipetakan: "+fn.Name)
        }
    }
    return nil
}
func pcProgram()
func main() { defer pcRecover(); pcProgram() }
'''


class GoBackend:
    def __init__(self):
        self.loop_id = 0
        self.function_names: set[str] = set()

    def expr(self, node: dict) -> str:
        kind, fields, line = node["kind"], node["fields"], node["line"]
        if kind == "Literal":
            value = fields["value"]
            if value is None: return "nil"
            if isinstance(value, bool): return "true" if value else "false"
            if isinstance(value, str): return json.dumps(value, ensure_ascii=False)
            if isinstance(value, (int, float)): return f"pcLiteral(float64({repr(value)}), {line})"
            raise GoBackendError(f"baris {line}: literal tidak didukung")
        if kind == "Variable": return f'env.get({json.dumps(fields["name"])}, {line})'
        if kind == "List": return "[]any{" + ", ".join(self.expr(x) for x in fields["items"]) + "}"
        if kind == "Dict":
            pairs = []
            for key, value in fields["items"]:
                pairs.append(f"PCPair{{Key: {self.expr(key)}, Value: {self.expr(value)}}}")
            return "&PCDict{Entries: []PCPair{" + ", ".join(pairs) + "}}"
        if kind == "Index": return f"pcIndex({self.expr(fields['collection'])}, {self.expr(fields['index'])}, {line})"
        if kind == "Unary": return f"pcUnary({json.dumps(fields['op'])}, {self.expr(fields['value'])}, {line})"
        if kind == "Binary":
            op = fields["op"]
            left, right = self.expr(fields["left"]), self.expr(fields["right"])
            if op == "dan": return f"pcAnd(func() any {{ return {left} }}, func() any {{ return {right} }})"
            if op == "atau": return f"pcOr(func() any {{ return {left} }}, func() any {{ return {right} }})"
            return f"pcBinary({json.dumps(op)}, {left}, {right}, {line})"
        if kind == "Call":
            args = ", ".join(self.expr(x) for x in fields["args"])
            return f'pcCall({json.dumps(fields["name"])}, []any{{{args}}}, env, {line})'
        raise GoBackendError(f"baris {line}: ekspresi belum didukung: {kind}")

    def block(self, nodes: list[dict], indent: str, in_function: bool = False) -> list[str]:
        out: list[str] = []
        for node in nodes:
            kind, fields, line = node["kind"], node["fields"], node["line"]
            if kind == "Function": continue
            out.append(indent + f"pcStep({line})")
            if kind == "Declare":
                out.append(indent + f'env.define({json.dumps(fields["name"])}, {self.expr(fields["value"])}, {line})')
            elif kind == "Assign":
                out.append(indent + f'env.set({json.dumps(fields["name"])}, {self.expr(fields["value"])}, {line})')
            elif kind == "Print":
                out.append(indent + f"pcOut({self.expr(fields['value'])})")
            elif kind == "Expr":
                out.append(indent + f"_ = {self.expr(fields['value'])}")
            elif kind == "IndexAssign":
                out.append(indent + f"pcSetIndex({self.expr(fields['collection'])}, {self.expr(fields['index'])}, {self.expr(fields['value'])}, {line})")
            elif kind == "If":
                out.append(indent + f"if pcTruthy({self.expr(fields['condition'])}) {{")
                out.extend(self.block(fields["then_body"], indent + "    ", in_function))
                if fields["else_body"]:
                    out.append(indent + "} else {")
                    out.extend(self.block(fields["else_body"], indent + "    ", in_function))
                out.append(indent + "}")
            elif kind == "While":
                out.append(indent + f"for pcTruthy({self.expr(fields['condition'])}) {{")
                out.append(indent + f"    pcStep({line})")
                out.extend(self.block(fields["body"], indent + "    ", in_function))
                out.append(indent + "}")
            elif kind == "For":
                self.loop_id += 1
                item = f"pcItem{self.loop_id}"
                out.append(indent + f"for _, {item} := range pcIter({self.expr(fields['iterable'])}, {line}) {{")
                out.append(indent + f"    pcStep({line})")
                out.append(indent + f'env.loopVar({json.dumps(fields["name"])}, {item}, {line})')
                out.extend(self.block(fields["body"], indent + "    ", in_function))
                out.append(indent + "}")
            elif kind == "Return":
                if not in_function: raise GoBackendError(f"baris {line}: balek hanya boleh di dalam fungsi")
                value = fields["value"]
                out.append(indent + ("return nil" if value is None else "return " + self.expr(value)))
            elif kind in {"Input", "Try"}:
                raise GoBackendError(f"baris {line}: fitur belum didukung backend Go: {kind}")
            else:
                raise GoBackendError(f"baris {line}: pernyataan belum didukung: {kind}")
        return out

    def generate(self, document: dict) -> str:
        validate(document)
        root = document["program"]
        body = root["fields"]["body"]
        functions = [item for item in body if item["kind"] == "Function"]
        for item in functions:
            name = item["fields"]["name"]
            if name in self.function_names: raise GoBackendError(f"baris {item['line']}: fungsi duplikat: {name}")
            self.function_names.add(name)
        unsupported = []
        stack = [root]
        while stack:
            item = stack.pop()
            if isinstance(item, dict) and "kind" in item:
                if item["kind"] not in SUPPORTED:
                    unsupported.append((item.get("line", 1), item["kind"]))
                stack.extend(item.get("fields", {}).values())
            elif isinstance(item, dict): stack.extend(item.values())
            elif isinstance(item, list): stack.extend(item)
        if unsupported:
            line, kind = unsupported[0]
            raise GoBackendError(f"baris {line}: node belum didukung backend Go: {kind}")

        dispatch = []
        function_code = []
        for item in functions:
            fields, line = item["fields"], item["line"]
            name, params = fields["name"], fields["params"]
            self.function_names.add(name)
            dispatch.append(f'        case {json.dumps(name)}: return pcFn_{name}(args, fn.Closure, line)')
            function_code.append(f'func pcFn_{name}(args []any, closure *PCEnv, callLine int) any {{')
            function_code.append(f'    if len(args) != {len(params)} {{ pcFail(callLine, {json.dumps(name + "() membutuhkan " + str(len(params)) + " argumen")}) }}')
            function_code.append('    env := pcNewEnv(closure)')
            for i, param in enumerate(params):
                function_code.append(f'    env.define({json.dumps(param)}, args[{i}], callLine)')
            function_code.extend(self.block(fields["body"], "    ", True))
            function_code.append("    return nil")
            function_code.append("}")
            function_code.append("")

        runtime = RUNTIME.replace("__FUNCTION_DISPATCH__", "\n".join(dispatch))
        runtime = runtime.replace("func pcProgram()\nfunc main()", "func pcProgram() {\n    env := pcNewEnv(nil)\n    _ = env\n" + "\n".join(
            f'    env.define({json.dumps(item["fields"]["name"])}, PCFunction{{Name: {json.dumps(item["fields"]["name"])}, Params: []string{{{", ".join(json.dumps(p) for p in item["fields"]["params"])}}}, Closure: env}}, {item["line"]})'
            for item in functions
        ) + "\n" + "\n".join(self.block([n for n in body if n["kind"] != "Function"], "    ")) + "\n}\nfunc main()")
        return runtime + "\n".join(function_code)


def generate(document: dict) -> str:
    return GoBackend().generate(document)


def compile_source(source: str, source_name: str = "<memory>") -> str:
    return generate(from_source(source, source_name))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compiler backend PusingCuk ke Go (subset eksperimental).")
    parser.add_argument("source", help="berkas sumber .cuk")
    parser.add_argument("-o", "--output", help="berkas keluaran .go; default stdout")
    args = parser.parse_args(argv)
    try:
        path = Path(args.source)
        result = compile_source(path.read_text(encoding="utf-8"), path.name)
        if args.output: Path(args.output).write_text(result, encoding="utf-8")
        else: sys.stdout.write(result)
        return 0
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as exc:
        print(f"kompilasi Go gagal: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
