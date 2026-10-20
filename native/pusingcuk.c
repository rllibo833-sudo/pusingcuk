
#include <ctype.h>
#include <errno.h>
#include <math.h>
#include <limits.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

// TODO file I/O not yet in C, use Python ref.

#define NV 256
#define SZ 1024

typedef enum { NUM, STR, BOOL, LIST, RANGE, DICT, NIL } Type;
typedef struct Val Val;
typedef struct List List;
typedef struct Dict Dict;
struct Val { Type t; double n; int b; char s[SZ]; List *list; Dict *dict; double range_start, range_end, range_step; };
#define MAX_LIST_ITEMS 256
struct List { size_t len, capacity; Val *items; };
#define MAX_DICT_ITEMS 256
struct Dict { size_t len; Val keys[MAX_DICT_ITEMS]; Val values[MAX_DICT_ITEMS]; };
#define MAX_LIST_ALLOCATIONS 100000
static List *allocated_lists[MAX_LIST_ALLOCATIONS];
static size_t allocated_list_count;
static Dict *allocated_dicts[MAX_LIST_ALLOCATIONS];
static size_t allocated_dict_count;
typedef struct { char name[128]; Val v; } Var;
static Var vars[NV];
static int nvars, err, syntax_err, line_no;
/* Parse skipped logical operands without performing runtime effects. */
static int suppress_eval;
static const char *p;
#define MAX_FUNCTIONS 128
#define MAX_PARAMS 32
typedef struct { char name[128]; char params[MAX_PARAMS][128]; int param_count; int first_line; int end_line; } Function;
static Function functions[MAX_FUNCTIONS];
static int function_count, call_depth, returning;
static Val return_value;
static void format_number(double value, char *output, size_t output_size);
static int run_range(int first, int last);
static Val call_user_function(const char *name, Val *args, int argc);
static Val call_native_format_builtin(const char *name, Val *args, int argc, int *handled);

static void fail(const char *msg) {
    if (suppress_eval) return;
    if (!err) fprintf(stderr, "Kesalahan runtime: Baris %d: %s\n", line_no, msg);
    err = 1;
}
static void syntax_fail(const char *msg) {
    if (!err) {
        fprintf(stderr, "Kesalahan sintaks: Baris %d: %s\n", line_no, msg);
        syntax_err = 1;
    }
    err = 1;
}
static Val num(double x) { Val v={0}; v.t=NUM; v.n=x; return v; }
static Val checked_num(double x, const char *message) {
    if (!isfinite(x)) { fail(message); return num(0); }
    return num(x);
}
static Val checked_safe_integer(double x, const char *invalid_message, const char *unsafe_message) {
    if (!isfinite(x)) { fail(invalid_message); return num(0); }
    if (floor(x) == x && fabs(x) > 9007199254740991.0) {
        fail(unsafe_message);
        return num(0);
    }
    return num(x);
}
static List *new_list(void) {
    if (allocated_list_count >= MAX_LIST_ALLOCATIONS) {
        fail("batas alokasi list native terlampaui"); return NULL;
    }
    List *list = calloc(1, sizeof *list);
    if (!list) { fail("memori list habis"); return NULL; }
    allocated_lists[allocated_list_count++] = list;
    return list;
}
static Dict *new_dict(void) {
    if (allocated_dict_count >= MAX_LIST_ALLOCATIONS) {
        fail("batas alokasi kamus native terlampaui"); return NULL;
    }
    Dict *dict = calloc(1, sizeof *dict);
    if (!dict) { fail("memori kamus habis"); return NULL; }
    allocated_dicts[allocated_dict_count++] = dict;
    return dict;
}
static int append_list(List *list, Val value) {
    if (list->len >= MAX_LIST_ITEMS) {
        fail("list terlalu panjang"); return 0;
    }
    if (list->len == list->capacity) {
        size_t next = list->capacity ? list->capacity * 2 : 4;
        if (next > MAX_LIST_ITEMS) next = MAX_LIST_ITEMS;
        Val *items = realloc(list->items, next * sizeof *items);
        if (!items) { fail("memori list habis"); return 0; }
        list->items = items; list->capacity = next;
    }
    list->items[list->len++] = value;
    return 1;
}
static Val boolean(int x) { Val v={0}; v.t=BOOL; v.b=!!x; return v; }
static Val string(const char *s) {
    Val v={0}; v.t=STR; snprintf(v.s,sizeof v.s,"%s",s); return v;
}
static void ws(void) { while (*p && isspace((unsigned char)*p)) p++; }
static int take(const char *s) {
    ws(); size_t n=strlen(s);
    if (!strncmp(p,s,n)) { p+=n; return 1; }
    return 0;
}
static int word(const char *s) {
    static const struct { const char *alias, *canonical; } aliases[] = {
        {"jir", "hedeh"},
        {"adooh", "kampret"},
        {"gitu", "selesai"},
        {"inthiseco", "jancuk"},
        {"janggal", "bukan"},
        {"gas", "jancuk"},
        {"spill", "hedeh"},
        {"bestie", "lah"},
        {"valid", "benar"},
        {"zonk", "salah"},
        {"skip", "kampret"},
        {"kelar", "selesai"},
    };
    ws();
    size_t n = strlen(s);
    if (!strncmp(p, s, n) &&
        !isalnum((unsigned char)p[n]) && p[n] != '_') {
        p += n;
        return 1;
    }
    for (size_t i = 0; i < sizeof aliases / sizeof aliases[0]; i++) {
        size_t alias_len = strlen(aliases[i].alias);
        if (!strcmp(s, aliases[i].canonical) &&
            !strncmp(p, aliases[i].alias, alias_len) &&
            !isalnum((unsigned char)p[alias_len]) &&
            p[alias_len] != '_') {
            p += alias_len;
            return 1;
        }
    }
    return 0;
}
static int endline(void) { ws(); return !*p || *p=='\n' || *p=='\r' || *p=='#'; }
static double range_length(Val v);
static int truth(Val v) {
    if (v.t==NIL) return 0;
    if (v.t==BOOL) return v.b;
    if (v.t==NUM) return v.n!=0;
    if (v.t==LIST) return v.list && v.list->len != 0;
    if (v.t==DICT) return v.dict && v.dict->len != 0;
    if (v.t==RANGE) return range_length(v) != 0;
    return v.s[0]!=0;
}
static int equal_depth(Val a, Val b, unsigned depth) {
    if (a.t!=b.t) return 0;
    if (a.t==NIL) return 1;
    if (a.t==NUM) return a.n==b.n;
    if (a.t==BOOL) return a.b==b.b;
    if (a.t==RANGE) return a.range_start==b.range_start && a.range_end==b.range_end && a.range_step==b.range_step;
    if (a.t==LIST) {
        if (a.list==b.list) return 1;
        if (!a.list || !b.list || a.list->len!=b.list->len) return 0;
        /* Bound recursive comparison so cyclic or deeply nested lists cannot exhaust the C stack. */
        if (depth>=64) return 0;
        for (size_t i=0; i<a.list->len; i++)
            if (!equal_depth(a.list->items[i],b.list->items[i],depth+1)) return 0;
        return 1;
    }
    /* Dictionary equality remains identity-based until its language contract is specified. */
    if (a.t==DICT) return a.dict==b.dict;
    return !strcmp(a.s,b.s);
}
static int equal(Val a, Val b) {
    return equal_depth(a,b,0);
}
static int valid_dict_key(Val key) {
    if (key.t==STR || key.t==NUM || key.t==BOOL) return 1;
    fail("kunci kamus native harus teks, angka, atau boolean");
    return 0;
}
static int dict_set(Dict *dict, Val key, Val value) {
    if (!dict || !valid_dict_key(key)) return 0;
    for (size_t i=0; i<dict->len; i++) {
        if (equal(dict->keys[i],key)) { dict->values[i]=value; return 1; }
    }
    if (dict->len >= MAX_DICT_ITEMS) { fail("kamus terlalu besar"); return 0; }
    dict->keys[dict->len]=key;
    dict->values[dict->len]=value;
    dict->len++;
    return 1;
}
static Val dict_get(Dict *dict, Val key) {
    if (!dict || !valid_dict_key(key)) return num(0);
    for (size_t i=0; i<dict->len; i++)
        if (equal(dict->keys[i],key)) return dict->values[i];
    fail("kunci kamus tidak ditemukan");
    return num(0);
}
static Val dictval(Dict *d) {
    Val v={0}; v.t=DICT; v.dict=d; return v;
}
static Val expr(void);
static Val listval(List *l) {
    Val v = {0}; v.t = LIST; v.list = l; return v;
}
static Val rangeval(double start, double end, double step) {
    Val v = {0}; v.t = RANGE;
    v.range_start = start; v.range_end = end; v.range_step = step;
    return v;
}
static double range_length(Val v) {
    if (v.t != RANGE || v.range_step == 0) return 0;
    double distance = v.range_step > 0
        ? v.range_end - v.range_start : v.range_start - v.range_end;
    if (distance <= 0) return 0;
    return ceil(distance / fabs(v.range_step));
}
static int list_index(Val v, Val idx, size_t *out) {
    if (v.t != LIST || !v.list) {
        fail("nilai bukan list"); return 0;
    }
    if (idx.t != NUM || !isfinite(idx.n) || idx.n < 0 ||
        idx.n >= (double)v.list->len ||
        idx.n != trunc(idx.n)) {
        fail("indeks list di luar batas atau bukan bilangan bulat"); return 0;
    }
    *out = (size_t)idx.n; return 1;
}

/* Move by UTF-8 code point so text indexing/iteration does not split characters. */
static size_t utf8_next(const char *s, size_t offset) {
    if (!s[offset]) return offset;
    size_t next = offset + 1;
    while (s[next] && (((unsigned char)s[next] & 0xC0) == 0x80)) next++;
    return next;
}
static int string_index(Val v, Val idx, size_t *start, size_t *end) {
    if (v.t != STR) { fail("nilai bukan teks"); return 0; }
    if (idx.t != NUM || !isfinite(idx.n) || idx.n < 0 || idx.n != trunc(idx.n)) {
        fail("indeks teks harus bilangan bulat nonnegatif"); return 0;
    }
    size_t offset = 0;
    for (size_t i = 0; v.s[offset]; i++) {
        size_t next = utf8_next(v.s, offset);
        if ((double)i == idx.n) { *start = offset; *end = next; return 1; }
        offset = next;
    }
    fail("indeks teks di luar batas");
    return 0;
}


static int is_builtin_name(const char *name) {
    static const char *const names[] = {
        "panjang", "teks", "bilangan", "desimal", "logika", "rentang",
        "mutlak", "minimum", "maksimum", "bulatkan", "akar", "bawah",
        "atas", "pangkat", "sinus", "kosinus", "jumlah", "rata_rata", "median", "logaritma", "log10", "json_teks", "json_baca", "html_aman", "csv_baris"
    };
    for (size_t i = 0; i < sizeof names / sizeof names[0]; i++)
        if (!strcmp(name, names[i])) return 1;
    return 0;
}

static int is_native_numeric_builtin(const char *name) {
    static const char *const names[] = {
        "mutlak", "minimum", "maksimum", "bulatkan", "akar", "bawah", "atas", "pangkat",
        "sinus", "kosinus", "jumlah", "rata_rata", "median", "logaritma", "log10"
    };
    for (size_t i = 0; i < sizeof names / sizeof names[0]; i++)
        if (!strcmp(name, names[i])) return 1;
    return 0;
}

static double round_ties_even(double value) {
    double lower = floor(value);
    double fraction = value - lower;
    if (fraction < 0.5) return lower;
    if (fraction > 0.5) return lower + 1.0;
    return fmod(fabs(lower), 2.0) == 0.0 ? lower : lower + 1.0;
}

static int is_native_conversion_builtin(const char *name) {
    return !strcmp(name, "teks") || !strcmp(name, "bilangan") ||
        !strcmp(name, "desimal") || !strcmp(name, "logika");
}

static Val call_native_conversion_builtin(const char *name, Val *args, int argc, int *handled) {
    *handled = is_native_conversion_builtin(name);
    if (!*handled) return num(0);
    if (argc != 1) {
        fail("built-in konversi membutuhkan tepat satu argumen");
        return num(0);
    }

    Val value = args[0];
    if (!strcmp(name, "logika")) return boolean(truth(value));

    if (!strcmp(name, "teks")) {
        if (value.t == STR) return value;
        if (value.t == BOOL) return string(value.b ? "okelah" : "tidak");
        if (value.t == NIL) return string("None");
        if (value.t == NUM && isfinite(value.n)) {
            char formatted[64];
            format_number(value.n, formatted, sizeof formatted);
            return string(formatted);
        }
        fail("teks() pada runtime native menerima teks, angka finite, boolean, atau None");
        return string("");
    }

    if (!strcmp(name, "bilangan")) {
        if (value.t == NUM && isfinite(value.n)) {
            double converted = trunc(value.n);
            if (fabs(converted) > 9007199254740991.0) {
                fail("bilangan() menolak integer di luar rentang aman lintas target");
                return num(0);
            }
            return num(converted);
        }
        if (value.t != STR) {
            fail("bilangan() membutuhkan teks integer atau angka non-boolean");
            return num(0);
        }
        errno = 0;
        char *end = NULL;
        long long parsed = strtoll(value.s, &end, 10);
        char *parse_end = end;
        while (end && isspace((unsigned char)*end)) end++;
        if (parse_end == value.s || !end || *end != '\0' || errno == ERANGE ||
            parsed > 9007199254740991LL || parsed < -9007199254740991LL) {
            fail("bilangan() menerima teks integer dalam rentang aman lintas target");
            return num(0);
        }
        return num((double)parsed);
    }

    if (!strcmp(name, "desimal")) {
        if (value.t == NUM && isfinite(value.n)) return value;
        if (value.t != STR) {
            fail("desimal() membutuhkan teks angka atau angka non-boolean");
            return num(0);
        }
        errno = 0;
        char *end = NULL;
        double parsed = strtod(value.s, &end);
        char *parse_end = end;
        while (end && isspace((unsigned char)*end)) end++;
        if (parse_end == value.s || !end || *end != '\0' || errno == ERANGE || !isfinite(parsed)) {
            fail("desimal() menerima teks angka finite");
            return num(0);
        }
        return num(parsed);
    }
    return num(0);
}

static Val call_native_numeric_builtin(const char *name, Val *args, int argc, int *handled) {
    *handled = is_native_numeric_builtin(name);
    if (!*handled) return num(0);

    int expected = (!strcmp(name, "minimum") || !strcmp(name, "maksimum") || !strcmp(name, "pangkat")) ? 2 : 1;
    if (argc != expected) {
        fail("jumlah argumen built-in numerik tidak sesuai kontrak");
        return num(0);
    }
    if (!strcmp(name, "jumlah") || !strcmp(name, "rata_rata") || !strcmp(name, "median")) {
        const int is_sum = !strcmp(name, "jumlah");
        const int is_mean = !strcmp(name, "rata_rata");
        Val input = args[0];
        if (input.t != LIST || !input.list || (!is_sum && input.list->len == 0)) {
            if (is_sum) fail("jumlah() membutuhkan daftar angka finite");
            else if (is_mean) fail("rata_rata() membutuhkan daftar angka finite yang tidak kosong");
            else fail("median() membutuhkan daftar angka finite yang tidak kosong");
            return num(0);
        }
        double values[MAX_LIST_ITEMS];
        size_t count = input.list->len;
        for (size_t i = 0; i < count; i++) {
            Val item = input.list->items[i];
            if (item.t != NUM || !isfinite(item.n)) {
                if (is_sum) fail("jumlah() hanya menerima angka finite; boolean bukan angka");
                else if (is_mean) fail("rata_rata() hanya menerima angka finite; boolean bukan angka");
                else fail("median() hanya menerima angka finite; boolean bukan angka");
                return num(0);
            }
            if (fabs(item.n) > 9007199254740991.0) {
                if (is_sum) fail("jumlah() menolak angka di luar rentang aman lintas target");
                else if (is_mean) fail("rata_rata() menolak angka di luar rentang aman lintas target");
                else fail("median() menolak angka di luar rentang aman lintas target");
                return num(0);
            }
            values[i] = item.n;
        }
        if (is_sum) {
            double total = 0.0;
            for (size_t i = 0; i < count; i++) {
                total += values[i];
                if (!isfinite(total)) {
                    fail("jumlah() menghasilkan angka non-finite");
                    return num(0);
                }
                if (total == trunc(total) && fabs(total) > 9007199254740991.0) {
                    fail("jumlah() menghasilkan integer di luar rentang aman lintas target");
                    return num(0);
                }
            }
            return num(total);
        }
        if (is_mean) {
            double mean = 0.0;
            for (size_t i = 0; i < count; i++)
                mean += values[i] / (double)count;
            return checked_num(mean, "rata_rata() menghasilkan angka non-finite");
        }
        for (size_t i = 1; i < count; i++) {
            double value = values[i];
            size_t j = i;
            while (j > 0 && values[j - 1] > value) {
                values[j] = values[j - 1];
                j--;
            }
            values[j] = value;
        }
        if (count % 2 == 1)
            return checked_num(values[count / 2], "median() menghasilkan angka non-finite");
        return checked_num(
            values[count / 2 - 1] / 2.0 + values[count / 2] / 2.0,
            "median() menghasilkan angka non-finite");
    }

    for (int i = 0; i < argc; i++) {
        if (args[i].t != NUM || !isfinite(args[i].n)) {
            fail("built-in numerik membutuhkan argumen angka finite; boolean bukan angka");
            return num(0);
        }
    }

    if (!strcmp(name, "sinus"))
        return checked_num(sin(args[0].n), "sinus() menghasilkan angka non-finite");
    if (!strcmp(name, "kosinus"))
        return checked_num(cos(args[0].n), "kosinus() menghasilkan angka non-finite");
    if (!strcmp(name, "logaritma")) {
        if (args[0].n <= 0.0) { fail("logaritma() domain tidak valid: angka harus lebih besar dari nol"); return num(0); }
        return checked_num(log(args[0].n), "logaritma() menghasilkan angka non-finite");
    }
    if (!strcmp(name, "log10")) {
        if (args[0].n <= 0.0) { fail("log10() domain tidak valid: angka harus lebih besar dari nol"); return num(0); }
        return checked_num(log10(args[0].n), "log10() menghasilkan angka non-finite");
    }
    if (!strcmp(name, "mutlak"))
        return checked_num(fabs(args[0].n), "mutlak() menghasilkan angka tidak valid");
    if (!strcmp(name, "minimum"))
        return args[1].n < args[0].n ? args[1] : args[0];
    if (!strcmp(name, "maksimum"))
        return args[1].n > args[0].n ? args[1] : args[0];
    if (!strcmp(name, "bulatkan"))
        return checked_safe_integer(round_ties_even(args[0].n), "bulatkan: operasi angka non-finite", "bulatkan: hasil integer di luar rentang aman lintas target");
    if (!strcmp(name, "bawah"))
        return checked_safe_integer(floor(args[0].n), "bawah: operasi angka non-finite", "bawah: hasil integer di luar rentang aman lintas target");
    if (!strcmp(name, "atas"))
        return checked_safe_integer(ceil(args[0].n), "atas: operasi angka non-finite", "atas: hasil integer di luar rentang aman lintas target");
    if (!strcmp(name, "akar")) {
        if (args[0].n < 0.0) {
            fail("akar() domain tidak valid: angka harus non-negatif");
            return num(0);
        }
        return checked_num(sqrt(args[0].n), "akar() menghasilkan angka non-finite");
    }
    if (!strcmp(name, "pangkat")) {
        double base = args[0].n;
        double exponent = args[1].n;
        if ((base < 0.0 && trunc(exponent) != exponent) ||
            (base == 0.0 && exponent < 0.0)) {
            fail("pangkat() domain tidak valid");
            return num(0);
        }
        return checked_num(pow(base, exponent), "pangkat() menghasilkan angka non-finite");
    }
    return num(0);
}

static Val primary(void) {
    ws();
    if (take("{")) {
        Dict *d = new_dict();
        if (!d) return dictval(NULL);
        if (!take("}")) {
            for (;;) {
                Val key = expr();
                if (!take(":")) { syntax_fail("tanda ':' diharapkan setelah kunci kamus"); return dictval(d); }
                Val value = expr();
                if (err || !dict_set(d,key,value)) return dictval(d);
                if (take("}")) break;
                if (!take(",")) { syntax_fail("koma atau '}' diharapkan dalam kamus"); return dictval(d); }
                if (take("}")) break;
            }
        }
        return dictval(d);
    }
    if (take("[")) {
        List *l = new_list();
        if (!l) return listval(NULL);
        if (!take("]")) {
            for (;;) {
                Val item = expr();
                if (err || !append_list(l, item)) return listval(l);
                if (take("]")) break;
                if (!take(",")) {
                    syntax_fail("koma atau ']' diharapkan"); return listval(l);
                }
            }
        }
        return listval(l);
    }

    ws();
    if (take("(")) {
        Val v=expr();
        if (!take(")")) syntax_fail("kurung tutup ')' diharapkan");
        return v;
    }
    if (*p=='"') {
        p++; char buf[SZ]; size_t n=0;
        while (*p && *p!='"' && *p!='\n' && *p!='\r') {
            char c=*p++;
            if (c=='\\') {
                if (!*p) { syntax_fail("escape string tidak lengkap"); break; }
                c=*p++;
                if (c=='n') c='\n'; else if (c=='t') c='\t';
                else if (c!='"' && c!='\\') { syntax_fail("escape string tidak dikenal"); }
            }
            if (n+1<SZ) buf[n++]=c; else fail("string terlalu panjang");
        }
        if (*p!='"') syntax_fail("string belum ditutup"); else p++;
        buf[n]=0; return string(buf);
    }
    if (isdigit((unsigned char)*p) || *p=='.') {
        char *e; double x=strtod(p,&e);
        if (e==p) { syntax_fail("angka tidak valid"); return num(0); }
        p=e; if (!isfinite(x)) { syntax_fail("angka desimal tidak valid atau terlalu besar"); return num(0); } return num(x);
    }
    if (isalpha((unsigned char)*p) || *p=='_') {
        char name[128]; size_t n=0;
        while (isalnum((unsigned char)*p) || *p=='_') {
            if (n+1<sizeof name) name[n++]=*p;
            p++;
        }
        name[n]=0;
        if (!strcmp(name,"benar") || !strcmp(name,"valid")) return boolean(1);
        if (!strcmp(name,"salah") || !strcmp(name,"zonk")) return boolean(0);
        if (take("(")) {
            Val args[MAX_PARAMS]; int argc = 0;
            if (!take(")")) {
                for (;;) {
                    if (argc >= MAX_PARAMS) {
                        syntax_fail("fungsi native menerima maksimal 32 argumen");
                        return num(0);
                    }
                    args[argc++] = expr();
                    if (err) return num(0);
                    if (take(")")) break;
                    if (!take(",")) {
                        syntax_fail("koma atau ')' diharapkan dalam argumen fungsi");
                        return num(0);
                    }
                }
            }
            if (suppress_eval) return num(0);
            if (!strcmp(name,"panjang")) {
                if (argc != 1) { fail("panjang() membutuhkan satu argumen"); return num(0); }
                if (args[0].t == LIST && args[0].list)
                    return num((double)args[0].list->len);
                if (args[0].t == STR) {
                    size_t count = 0;
                    for (const unsigned char *q=(const unsigned char *)args[0].s; *q; q++)
                        if ((*q & 0xC0) != 0x80) count++;
                    return num((double)count);
                }
                if (args[0].t == RANGE) return num(range_length(args[0]));
                if (args[0].t == DICT && args[0].dict) return num((double)args[0].dict->len);
                fail("panjang() menerima list, teks, kamus, atau rentang"); return num(0);
            }
            if (!strcmp(name,"rentang")) {
                if (argc < 1 || argc > 3) {
                    fail("rentang() menerima satu sampai tiga argumen"); return num(0);
                }
                double start = 0, end = 0, step = 1;
                if (argc == 1) end = args[0].n;
                else { start = args[0].n; end = args[1].n; }
                if (argc == 3) step = args[2].n;
                for (int i=0; i<argc; i++) {
                    if (args[i].t != NUM || !isfinite(args[i].n) ||
                        args[i].n != trunc(args[i].n)) {
                        fail("argumen rentang() harus bilangan bulat"); return num(0);
                    }
                }
                if (step == 0) { fail("langkah rentang() tidak boleh nol"); return num(0); }
                return rangeval(start, end, step);
            }
            int conversion_handled = 0;
            Val conversion_result = call_native_conversion_builtin(name, args, argc, &conversion_handled);
            if (conversion_handled) return conversion_result;
            int format_handled = 0;
            Val format_result = call_native_format_builtin(name, args, argc, &format_handled);
            if (format_handled) return format_result;
            int builtin_handled = 0;
            Val builtin_result = call_native_numeric_builtin(name, args, argc, &builtin_handled);
            if (builtin_handled) return builtin_result;
            if (is_builtin_name(name)) {
                fail("built-in ini belum didukung pada runtime native C");
                return num(0);
            }
            return call_user_function(name, args, argc);
        }
        if (suppress_eval) {
            if (take("[")) {
                (void)expr();
                if (!take("]")) syntax_fail("kurung siku tutup ']' diharapkan");
            }
            return num(0);
        }
        Val value = num(0);
        int found = 0;
        for (int i=0;i<nvars;i++)
            if (!strcmp(vars[i].name,name)) {
                value=vars[i].v; found=1; break;
            }
        if (!found) { fail("variabel belum dibuat"); return num(0); }
        if (take("[")) {
            Val idx=expr();
            if (!take("]")) syntax_fail("kurung siku tutup ']' diharapkan");
            if (value.t == STR) {
                size_t start=0, end=0;
                if (!string_index(value,idx,&start,&end)) return string("");
                char ch[SZ]; size_t len=end-start;
                memcpy(ch,value.s+start,len); ch[len]=0;
                return string(ch);
            }
            if (value.t == DICT) return dict_get(value.dict,idx);
            if (value.t == RANGE) {
                double length = range_length(value);
                if (idx.t != NUM || !isfinite(idx.n) || idx.n < 0 ||
                    idx.n != trunc(idx.n) || idx.n >= length) {
                    fail("indeks rentang di luar batas atau bukan bilangan bulat");
                    return num(0);
                }
                return checked_safe_integer(
                    value.range_start + idx.n * value.range_step,
                    "indeks rentang menghasilkan angka tidak valid",
                    "indeks rentang di luar rentang aman lintas target");
            }
            size_t at=0;
            if (!list_index(value,idx,&at)) return num(0);
            return value.list->items[at];
        }
        return value;
    }
    syntax_fail("ekspresi tidak valid"); return num(0);
}
static Val unary(void) {
    if (word("bukan")) return boolean(!truth(unary()));
    if (take("-")) {
        Val v=unary();
        if (v.t!=NUM) { fail("operator '-' membutuhkan angka"); return num(0); }
        return num(-v.n);
    }
    return primary();
}
static Val mul(void) {
    Val a=unary();
    for (;;) {
        if (take("*")) {
            Val b=unary();
            if (a.t!=NUM || b.t!=NUM) { fail("'*' membutuhkan angka"); return num(0); }
            a=checked_num(a.n*b.n,"hasil angka desimal terlalu besar atau tidak valid");
        } else if (take("//")) {
            Val b=unary();
            if (a.t!=NUM || b.t!=NUM) { fail("'//' membutuhkan angka"); return num(0); }
            if (b.n==0) { fail("pembagian dengan nol"); return num(0); }
            a=checked_num(floor(a.n/b.n),"hasil angka desimal terlalu besar atau tidak valid");
        } else if (take("%")) {
            Val b=unary();
            if (a.t!=NUM || b.t!=NUM) { fail("'%' membutuhkan angka"); return num(0); }
            if (b.n==0) { fail("modulo dengan nol"); return num(0); }
            a=checked_num(a.n-floor(a.n/b.n)*b.n,"hasil angka desimal terlalu besar atau tidak valid");
        } else if (take("/")) {
            Val b=unary();
            if (a.t!=NUM || b.t!=NUM) { fail("'/' membutuhkan angka"); return num(0); }
            if (b.n==0) { fail("pembagian dengan nol"); return num(0); }
            a=checked_num(a.n/b.n,"hasil angka desimal terlalu besar atau tidak valid");
        } else break;
    }
    return a;
}
static Val add(void) {
    Val a=mul();
    for (;;) {
        if (take("+")) {
            Val b=mul();
            if (a.t==STR && b.t==STR) {
                char tmp[SZ];
                size_t a_len = strlen(a.s), b_len = strlen(b.s);
                if (a_len + b_len >= sizeof tmp) {
                    fail("hasil string terlalu panjang"); return string("");
                }
                memcpy(tmp, a.s, a_len);
                memcpy(tmp + a_len, b.s, b_len + 1);
                a = string(tmp);
            } else if (a.t==NUM && b.t==NUM) a=checked_num(a.n+b.n,"hasil angka desimal terlalu besar atau tidak valid");
            else if (a.t==LIST && b.t==LIST) {
                List *combined = new_list();
                if (!combined) return listval(NULL);
                for (size_t i=0; a.list && i<a.list->len; i++)
                    if (!append_list(combined, a.list->items[i])) return listval(combined);
                for (size_t i=0; b.list && i<b.list->len; i++)
                    if (!append_list(combined, b.list->items[i])) return listval(combined);
                a = listval(combined);
            } else { fail("'+' membutuhkan dua angka, dua teks, atau dua daftar"); return num(0); }
        } else if (take("-")) {
            Val b=mul();
            if (a.t!=NUM || b.t!=NUM) { fail("'-' membutuhkan angka"); return num(0); }
            a=checked_num(a.n-b.n,"hasil angka desimal terlalu besar atau tidak valid");
        } else break;
    }
    return a;
}
static Val compare(void) {
    Val a=add();
    for (;;) {
        if (take("==")) { Val b=add(); a=boolean(equal(a,b)); }
        else if (take("!=")) { Val b=add(); a=boolean(!equal(a,b)); }
        else if (take("<=")) {
            Val b=add();
            if(a.t!=NUM||b.t!=NUM){fail("perbandingan membutuhkan angka");return boolean(0);}
            a=boolean(a.n<=b.n);
        } else if (take(">=")) {
            Val b=add();
            if(a.t!=NUM||b.t!=NUM){fail("perbandingan membutuhkan angka");return boolean(0);}
            a=boolean(a.n>=b.n);
        } else if (take("<")) {
            Val b=add();
            if(a.t!=NUM||b.t!=NUM){fail("perbandingan membutuhkan angka");return boolean(0);}
            a=boolean(a.n<b.n);
        } else if (take(">")) {
            Val b=add();
            if(a.t!=NUM||b.t!=NUM){fail("perbandingan membutuhkan angka");return boolean(0);}
            a=boolean(a.n>b.n);
        } else break;
    }
    return a;
}
static Val and_expr(void) {
    Val a=compare();
    while (word("dan")) {
        int previous = suppress_eval;
        suppress_eval = previous || !truth(a);
        Val b=compare();
        suppress_eval = previous;
        a=boolean(truth(a)&&truth(b));
    }
    return a;
}
static Val expr(void) {
    Val a=and_expr();
    while (word("atau")) {
        int previous = suppress_eval;
        suppress_eval = previous || truth(a);
        Val b=and_expr();
        suppress_eval = previous;
        a=boolean(truth(a)||truth(b));
    }
    return a;
}
static int identifier(char *out, size_t cap) {
    ws();
    if (!(isalpha((unsigned char)*p)||*p=='_')) return 0;
    size_t n=0;
    while (isalnum((unsigned char)*p)||*p=='_') {
        if(n+1<cap) out[n++]=*p;
        p++;
    }
    out[n]=0; return 1;
}
static int setvar(const char *name, Val v) {
    for(int i=0;i<nvars;i++) if(!strcmp(vars[i].name,name)){vars[i].v=v;return 1;}
    if(nvars>=NV){fail("jumlah variabel melampaui batas");return 0;}
    snprintf(vars[nvars].name,sizeof vars[nvars].name,"%s",name);
    vars[nvars++].v=v; return 1;
}
static void format_number(double value, char *output, size_t output_size) {
    char candidate[64];
    for (int precision = 1; precision <= 17; precision++) {
        int written = snprintf(candidate, sizeof candidate, "%.*g", precision, value);
        if (written < 0 || (size_t)written >= sizeof candidate) continue;
        char *end = NULL;
        double parsed = strtod(candidate, &end);
        if (end && *end == '\0' && parsed == value) {
            snprintf(output, output_size, "%s", candidate);
            return;
        }
    }
    snprintf(output, output_size, "%.17g", value);
}


#define JSON_MAX_DEPTH 64
#define JSON_MAX_SAFE_INTEGER 9007199254740991.0

typedef struct {
    const char *source;
    size_t pos;
    int valid;
} JsonParser;

static int format_append(char *out, size_t cap, size_t *used, const char *src, size_t n) {
    if (*used >= cap || n > cap - *used - 1) {
        fail("hasil built-in format melebihi batas buffer native");
        return 0;
    }
    memcpy(out + *used, src, n);
    *used += n;
    out[*used] = '\0';
    return 1;
}
static int format_char(char *out, size_t cap, size_t *used, char ch) {
    return format_append(out, cap, used, &ch, 1);
}
static int format_literal(char *out, size_t cap, size_t *used, const char *text) {
    return format_append(out, cap, used, text, strlen(text));
}
static int json_write_string(const char *value, char *out, size_t cap, size_t *used) {
    if (!format_char(out, cap, used, '"')) return 0;
    for (const unsigned char *q = (const unsigned char *)value; *q; q++) {
        char escaped[7];
        switch (*q) {
            case '"': if (!format_literal(out, cap, used, "\\\"")) return 0; break;
            case '\\': if (!format_literal(out, cap, used, "\\\\")) return 0; break;
            case '\b': if (!format_literal(out, cap, used, "\\b")) return 0; break;
            case '\f': if (!format_literal(out, cap, used, "\\f")) return 0; break;
            case '\n': if (!format_literal(out, cap, used, "\\n")) return 0; break;
            case '\r': if (!format_literal(out, cap, used, "\\r")) return 0; break;
            case '\t': if (!format_literal(out, cap, used, "\\t")) return 0; break;
            default:
                if (*q < 0x20) {
                    snprintf(escaped, sizeof escaped, "\\u%04x", (unsigned)*q);
                    if (!format_literal(out, cap, used, escaped)) return 0;
                } else if (!format_char(out, cap, used, (char)*q)) return 0;
        }
    }
    return format_char(out, cap, used, '"');
}
static int json_write_value(Val value, char *out, size_t cap, size_t *used, unsigned depth) {
    if (depth > JSON_MAX_DEPTH) { fail("JSON melebihi kedalaman maksimum"); return 0; }
    if (value.t == NIL) return format_literal(out, cap, used, "null");
    if (value.t == BOOL) return format_literal(out, cap, used, value.b ? "true" : "false");
    if (value.t == STR) return json_write_string(value.s, out, cap, used);
    if (value.t == NUM) {
        if (!isfinite(value.n)) { fail("json_teks() menolak angka non-finite"); return 0; }
        if (floor(value.n) == value.n && fabs(value.n) > JSON_MAX_SAFE_INTEGER) {
            fail("json_teks() menolak integer di luar rentang aman lintas target"); return 0;
        }
        char number[64];
        if (value.n == 0) snprintf(number, sizeof number, "0");
        else format_number(value.n, number, sizeof number);
        return format_literal(out, cap, used, number);
    }
    if (value.t == LIST) {
        if (!value.list) { fail("json_teks() menerima list tidak valid"); return 0; }
        if (!format_char(out, cap, used, '[')) return 0;
        for (size_t i = 0; i < value.list->len; i++) {
            if (i && !format_char(out, cap, used, ',')) return 0;
            if (!json_write_value(value.list->items[i], out, cap, used, depth + 1)) return 0;
        }
        return format_char(out, cap, used, ']');
    }
    if (value.t == DICT) {
        if (!value.dict) { fail("json_teks() menerima dictionary tidak valid"); return 0; }
        if (!format_char(out, cap, used, '{')) return 0;
        for (size_t i = 0; i < value.dict->len; i++) {
            Val key = value.dict->keys[i];
            if (key.t != STR) { fail("json_teks() hanya menerima kunci dictionary bertipe teks"); return 0; }
            if (i && !format_char(out, cap, used, ',')) return 0;
            if (!json_write_string(key.s, out, cap, used) ||
                !format_char(out, cap, used, ':') ||
                !json_write_value(value.dict->values[i], out, cap, used, depth + 1)) return 0;
        }
        return format_char(out, cap, used, '}');
    }
    fail("json_teks() menerima tipe nilai yang tidak didukung");
    return 0;
}
static void json_ws(JsonParser *jp) {
    while (jp->source[jp->pos] && isspace((unsigned char)jp->source[jp->pos])) jp->pos++;
}
static int json_hex(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}
static int json_hex4(JsonParser *jp, unsigned *out) {
    unsigned value = 0;
    for (int i = 0; i < 4; i++) {
        int h = json_hex(jp->source[jp->pos++]);
        if (h < 0) { jp->valid = 0; return 0; }
        value = (value << 4) | (unsigned)h;
    }
    *out = value;
    return 1;
}
static int json_utf8(char *out, size_t cap, size_t *used, unsigned cp) {
    char bytes[4]; size_t count;
    if (cp <= 0x7f) { bytes[0] = (char)cp; count = 1; }
    else if (cp <= 0x7ff) { bytes[0] = (char)(0xc0 | (cp >> 6)); bytes[1] = (char)(0x80 | (cp & 0x3f)); count = 2; }
    else if (cp <= 0xffff) { bytes[0] = (char)(0xe0 | (cp >> 12)); bytes[1] = (char)(0x80 | ((cp >> 6) & 0x3f)); bytes[2] = (char)(0x80 | (cp & 0x3f)); count = 3; }
    else if (cp <= 0x10ffff) { bytes[0] = (char)(0xf0 | (cp >> 18)); bytes[1] = (char)(0x80 | ((cp >> 12) & 0x3f)); bytes[2] = (char)(0x80 | ((cp >> 6) & 0x3f)); bytes[3] = (char)(0x80 | (cp & 0x3f)); count = 4; }
    else { return 0; }
    return format_append(out, cap, used, bytes, count);
}
static Val json_parse_value(JsonParser *jp, unsigned depth);
static Val json_parse_string(JsonParser *jp) {
    char out[SZ] = {0}; size_t used = 0;
    if (jp->source[jp->pos++] != '"') { jp->valid = 0; return string(""); }
    while (jp->source[jp->pos]) {
        unsigned char ch = (unsigned char)jp->source[jp->pos++];
        if (ch == '"') return string(out);
        if (ch < 0x20) { jp->valid = 0; return string(""); }
        if (ch != '\\') {
            if (!format_char(out, sizeof out, &used, (char)ch)) { jp->valid = 0; return string(""); }
            continue;
        }
        char esc = jp->source[jp->pos++];
        switch (esc) {
            case '"': case '\\': case '/':
                if (!format_char(out, sizeof out, &used, esc)) jp->valid = 0;
                break;
            case 'b': if (!format_char(out, sizeof out, &used, '\b')) jp->valid = 0; break;
            case 'f': if (!format_char(out, sizeof out, &used, '\f')) jp->valid = 0; break;
            case 'n': if (!format_char(out, sizeof out, &used, '\n')) jp->valid = 0; break;
            case 'r': if (!format_char(out, sizeof out, &used, '\r')) jp->valid = 0; break;
            case 't': if (!format_char(out, sizeof out, &used, '\t')) jp->valid = 0; break;
            case 'u': {
                unsigned cp;
                if (!json_hex4(jp, &cp)) return string("");
                if (cp >= 0xd800 && cp <= 0xdbff) {
                    if (jp->source[jp->pos] != '\\' || jp->source[jp->pos + 1] != 'u') { jp->valid = 0; return string(""); }
                    jp->pos += 2;
                    unsigned low;
                    if (!json_hex4(jp, &low) || low < 0xdc00 || low > 0xdfff) { jp->valid = 0; return string(""); }
                    cp = 0x10000 + ((cp - 0xd800) << 10) + (low - 0xdc00);
                } else if (cp >= 0xdc00 && cp <= 0xdfff) { jp->valid = 0; return string(""); }
                if (cp == 0 || !json_utf8(out, sizeof out, &used, cp)) { jp->valid = 0; return string(""); }
                break;
            }
            default: jp->valid = 0; return string("");
        }
        if (!jp->valid) return string("");
    }
    jp->valid = 0;
    return string("");
}
static Val json_parse_value(JsonParser *jp, unsigned depth) {
    json_ws(jp);
    if (depth > JSON_MAX_DEPTH) { jp->valid = 0; return num(0); }
    char ch = jp->source[jp->pos];
    if (ch == '"') return json_parse_string(jp);
    if (ch == '[') {
        jp->pos++;
        List *list = new_list();
        if (!list) { jp->valid = 0; return num(0); }
        json_ws(jp);
        if (jp->source[jp->pos] == ']') { jp->pos++; return listval(list); }
        for (;;) {
            Val item = json_parse_value(jp, depth + 1);
            if (!jp->valid || err || !append_list(list, item)) { jp->valid = 0; return num(0); }
            json_ws(jp);
            if (jp->source[jp->pos] == ']') { jp->pos++; return listval(list); }
            if (jp->source[jp->pos++] != ',') { jp->valid = 0; return num(0); }
            json_ws(jp);
        }
    }
    if (ch == '{') {
        jp->pos++;
        Dict *dict = new_dict();
        if (!dict) { jp->valid = 0; return num(0); }
        json_ws(jp);
        if (jp->source[jp->pos] == '}') { jp->pos++; return dictval(dict); }
        for (;;) {
            json_ws(jp);
            if (jp->source[jp->pos] != '"') { jp->valid = 0; return num(0); }
            Val key = json_parse_string(jp);
            json_ws(jp);
            if (!jp->valid || jp->source[jp->pos++] != ':') { jp->valid = 0; return num(0); }
            Val value = json_parse_value(jp, depth + 1);
            if (!jp->valid || err || !dict_set(dict, key, value)) { jp->valid = 0; return num(0); }
            json_ws(jp);
            if (jp->source[jp->pos] == '}') { jp->pos++; return dictval(dict); }
            if (jp->source[jp->pos++] != ',') { jp->valid = 0; return num(0); }
            json_ws(jp);
        }
    }
    if (!strncmp(jp->source + jp->pos, "true", 4)) { jp->pos += 4; return boolean(1); }
    if (!strncmp(jp->source + jp->pos, "false", 5)) { jp->pos += 5; return boolean(0); }
    if (!strncmp(jp->source + jp->pos, "null", 4)) { jp->pos += 4; Val v = {0}; v.t = NIL; return v; }
    size_t start = jp->pos;
    if (ch == '-') jp->pos++;
    if (jp->source[jp->pos] == '0') {
        jp->pos++;
        if (isdigit((unsigned char)jp->source[jp->pos])) { jp->valid = 0; return num(0); }
    } else if (jp->source[jp->pos] >= '1' && jp->source[jp->pos] <= '9') {
        while (isdigit((unsigned char)jp->source[jp->pos])) jp->pos++;
    } else { jp->valid = 0; return num(0); }
    if (jp->source[jp->pos] == '.') {
        jp->pos++;
        if (!isdigit((unsigned char)jp->source[jp->pos])) { jp->valid = 0; return num(0); }
        while (isdigit((unsigned char)jp->source[jp->pos])) jp->pos++;
    }
    if (jp->source[jp->pos] == 'e' || jp->source[jp->pos] == 'E') {
        jp->pos++;
        if (jp->source[jp->pos] == '+' || jp->source[jp->pos] == '-') jp->pos++;
        if (!isdigit((unsigned char)jp->source[jp->pos])) { jp->valid = 0; return num(0); }
        while (isdigit((unsigned char)jp->source[jp->pos])) jp->pos++;
    }
    size_t n = jp->pos - start;
    if (n == 0 || n >= 64) { jp->valid = 0; return num(0); }
    char token[64]; memcpy(token, jp->source + start, n); token[n] = '\0';
    errno = 0; char *end = NULL; double number = strtod(token, &end);
    if (!end || *end || !isfinite(number) ||
        (floor(number) == number && fabs(number) > JSON_MAX_SAFE_INTEGER)) {
        jp->valid = 0; return num(0);
    }
    return num(number);
}
static Val call_native_format_builtin(const char *name, Val *args, int argc, int *handled) {
    *handled = !strcmp(name, "json_teks") || !strcmp(name, "json_baca") ||
        !strcmp(name, "html_aman") || !strcmp(name, "csv_baris");
    if (!*handled) return num(0);
    if (argc != 1) { fail("built-in format membutuhkan tepat satu argumen"); return num(0); }
    Val value = args[0];
    if (!strcmp(name, "json_teks")) {
        char out[SZ] = {0}; size_t used = 0;
        if (!json_write_value(value, out, sizeof out, &used, 0)) return string("");
        return string(out);
    }
    if (!strcmp(name, "json_baca")) {
        if (value.t != STR) { fail("json_baca() membutuhkan teks JSON"); return num(0); }
        JsonParser jp = {value.s, 0, 1};
        Val parsed = json_parse_value(&jp, 0);
        json_ws(&jp);
        if (!jp.valid || err || jp.source[jp.pos] != '\0') {
            fail("json_baca() menerima teks JSON tidak valid atau nilai di luar batas kontrak");
            return num(0);
        }
        return parsed;
    }
    if (!strcmp(name, "html_aman")) {
        char source[SZ] = {0};
        if (value.t == STR) snprintf(source, sizeof source, "%s", value.s);
        else if (value.t == BOOL) snprintf(source, sizeof source, "%s", value.b ? "okelah" : "tidak");
        else if (value.t == NIL) snprintf(source, sizeof source, "None");
        else if (value.t == NUM && isfinite(value.n)) { if (value.n == 0) snprintf(source, sizeof source, "0"); else format_number(value.n, source, sizeof source); }
        else { fail("html_aman() membutuhkan nilai skalar"); return string(""); }
        char out[SZ] = {0}; size_t used = 0;
        for (const char *q = source; *q; q++) {
            const char *replacement = NULL;
            switch (*q) {
                case '&': replacement = "&amp;"; break;
                case '<': replacement = "&lt;"; break;
                case '>': replacement = "&gt;"; break;
                case '"': replacement = "&quot;"; break;
                case '\'': replacement = "&#x27;"; break;
                default: if (!format_char(out, sizeof out, &used, *q)) return string("");
            }
            if (replacement && !format_literal(out, sizeof out, &used, replacement)) return string("");
        }
        return string(out);
    }
    if (value.t != LIST || !value.list) { fail("csv_baris() membutuhkan daftar"); return string(""); }
    char out[SZ] = {0}; size_t used = 0;
    for (size_t i = 0; i < value.list->len; i++) {
        if (i && !format_char(out, sizeof out, &used, ',')) return string("");
        Val item = value.list->items[i]; char field[SZ] = {0};
        if (item.t == STR) snprintf(field, sizeof field, "%s", item.s);
        else if (item.t == BOOL) snprintf(field, sizeof field, "%s", item.b ? "okelah" : "tidak");
        else if (item.t == NIL) snprintf(field, sizeof field, "None");
        else if (item.t == NUM && isfinite(item.n)) {
            if (floor(item.n) == item.n && fabs(item.n) > JSON_MAX_SAFE_INTEGER) {
                fail("csv_baris() menolak integer di luar rentang aman"); return string("");
            }
            if (item.n == 0) snprintf(field, sizeof field, "0"); else format_number(item.n, field, sizeof field);
        } else { fail("csv_baris() hanya menerima nilai skalar"); return string(""); }
        int quote = strpbrk(field, ",\"\r\n") != NULL;
        if (quote && !format_char(out, sizeof out, &used, '"')) return string("");
        for (const char *q = field; *q; q++) {
            if (*q == '"' && quote && !format_char(out, sizeof out, &used, '"')) return string("");
            if (!format_char(out, sizeof out, &used, *q)) return string("");
        }
        if (quote && !format_char(out, sizeof out, &used, '"')) return string("");
    }
    return string(out);
}

static void printval(Val v) {
    if(v.t==NIL) puts("tidak ada");
    else if(v.t==BOOL) puts(v.b?"okelah":"tidak");
    else if(v.t==STR) puts(v.s);
    else if(v.t==LIST) printf("[list: %zu]\n", v.list ? v.list->len : 0);
    else if(v.t==DICT) printf("[kamus: %zu]\n", v.dict ? v.dict->len : 0);
    else if(v.t==RANGE) printf("[rentang: %.0f]\n", range_length(v));
    else if(isfinite(v.n) && fabs(v.n) <= 9007199254740991.0 && v.n==trunc(v.n)) printf("%lld\n",(long long)v.n);
    else {
        char formatted[64];
        format_number(v.n, formatted, sizeof formatted);
        puts(formatted);
    }
}

#define MAX_LINES 20000
#define MAX_STEPS 100000
#define MAX_ITER 10000
static char *program_lines[MAX_LINES];
static int program_count, steps;

static int hasvar(const char *name) {
    for (int i=0;i<nvars;i++)
        if (!strcmp(vars[i].name,name)) return 1;
    return 0;
}
static int line_word(int i,const char *kw) {
    if (i<0 || i>=program_count) return 0;
    const char *save=p; p=program_lines[i]; ws();
    int yes=word(kw); p=save; return yes;
}
static int line_close(int i,const char *kw) {
    if (!line_word(i,"selesai")) return 0;
    const char *save=p; p=program_lines[i]; ws(); word("selesai");
    int yes=word(kw); ws();
    yes=yes && (!*p || *p=='#' || *p=='\n' || *p=='\r');
    p=save; return yes;
}
static int block_end(int start,const char *kind,int *middle) {
    int depth=0, split=-1;
    for(int i=start+1;i<program_count;i++) {
        if(line_word(i,kind)) depth++;
        if(line_close(i,kind)) {
            if(depth==0) { *middle=split; return i; }
            depth--;
        }
        if(!strcmp(kind,"njir") && depth==0 && split<0 &&
           line_word(i,"kampret")) split=i;
    }
    line_no=program_count > 0 ? program_count : start + 1; syntax_fail("blok tidak ditutup dengan benar"); return -1;
}
static int register_function(int header, int end) {
    const char *saved_p = p;
    int saved_line = line_no;
    p = program_lines[header];
    line_no = header + 1;
    if (!word("fungsi")) { p = saved_p; line_no = saved_line; return 0; }
    char name[128] = {0};
    if (!identifier(name, sizeof name) || !take("(")) {
        syntax_fail("deklarasi fungsi harus berbentuk fungsi nama(parameter)");
        p = saved_p; line_no = saved_line; return 0;
    }
    if (is_builtin_name(name)) {
        fail("nama fungsi bawaan tidak boleh digunakan ulang");
        p = saved_p; line_no = saved_line; return 0;
    }
    for (int i = 0; i < function_count; i++) {
        if (!strcmp(functions[i].name, name)) {
            fail("fungsi sudah dibuat"); p = saved_p; line_no = saved_line; return 0;
        }
    }
    if (function_count >= MAX_FUNCTIONS) {
        fail("jumlah fungsi native melampaui batas"); p = saved_p; line_no = saved_line; return 0;
    }
    Function fn = {0};
    snprintf(fn.name, sizeof fn.name, "%s", name);
    if (!take(")")) {
        for (;;) {
            if (fn.param_count >= MAX_PARAMS) {
                fail("fungsi native maksimal memiliki 32 parameter");
                p = saved_p; line_no = saved_line; return 0;
            }
            char param[128] = {0};
            if (!identifier(param, sizeof param)) {
                syntax_fail("nama parameter fungsi diharapkan");
                p = saved_p; line_no = saved_line; return 0;
            }
            for (int j = 0; j < fn.param_count; j++) {
                if (!strcmp(fn.params[j], param)) {
                    fail("nama parameter fungsi tidak boleh duplikat");
                    p = saved_p; line_no = saved_line; return 0;
                }
            }
            snprintf(fn.params[fn.param_count++], sizeof fn.params[0], "%s", param);
            if (take(")")) break;
            if (!take(",")) {
                syntax_fail("koma atau ')' diharapkan dalam parameter fungsi");
                p = saved_p; line_no = saved_line; return 0;
            }
        }
    }
    if (!endline()) {
        syntax_fail("karakter tambahan setelah deklarasi fungsi");
        p = saved_p; line_no = saved_line; return 0;
    }
    fn.first_line = header + 1;
    fn.end_line = end;
    functions[function_count++] = fn;
    p = saved_p; line_no = saved_line;
    return 1;
}

static int function_registered_at(int header, int end) {
    for (int i = 0; i < function_count; i++)
        if (functions[i].first_line == header + 1 && functions[i].end_line == end)
            return 1;
    return 0;
}

static int run_range(int first,int last) {
    for(int i=first;i<last && !err && !returning;i++) {
        if(++steps>MAX_STEPS) {
            line_no=i+1; fail("batas 100000 langkah terlampaui"); break;
        }
        line_no=i+1; p=program_lines[i]; ws();
        if(endline()) continue;
        if(word("jancuk")) continue;
        if(word("selesai")) { if(word("jancuk") && first==0 && i==last-1) continue; syntax_fail("penutup blok tidak sesuai"); break; }

        if(word("njir")) {
            Val c=expr();
            if(!endline()) syntax_fail("karakter tambahan pada kondisi njir");
            int mid=-1, end=block_end(i,"njir",&mid);
            if(end<0) break;
            if(!err) {
                if(truth(c)) run_range(i+1,mid>=0?mid:end);
                else if(mid>=0) run_range(mid+1,end);
            }
            i=end;
        } else if(word("kampret")) {
            syntax_fail("kampret tanpa njir");
        } else if(word("untuk")) {
            char name[128] = {0};
            if (!identifier(name, sizeof name)) { syntax_fail("nama variabel perulangan diharapkan"); break; }
            if (!word("dalam")) { syntax_fail("kata 'dalam' diharapkan setelah nama perulangan"); break; }
            Val iterable = expr();
            if (!endline()) syntax_fail("karakter tambahan setelah koleksi perulangan");
            int mid=-1, end=block_end(i,"untuk",&mid);
            if (end<0) break;
            if (!err && iterable.t == LIST && iterable.list) {
                size_t count = iterable.list->len;
                if (count > MAX_ITER) { fail("list melebihi batas 10000 iterasi native"); }
                for (size_t j=0; j<count && !err && !returning; j++) {
                    if (++steps > MAX_STEPS) { fail("batas 100000 langkah terlampaui"); break; }
                    setvar(name, iterable.list->items[j]);
                    run_range(i+1,end);
                }
            } else if (!err && iterable.t == STR) {
                size_t offset=0;
                int iter=0;
                while (!err && !returning && iterable.s[offset]) {
                    if (++iter > MAX_ITER) { fail("batas 10000 iterasi teks terlampaui"); break; }
                    if (++steps > MAX_STEPS) { fail("batas 100000 langkah terlampaui"); break; }
                    size_t next=utf8_next(iterable.s,offset);
                    char ch[SZ]; size_t len=next-offset;
                    memcpy(ch,iterable.s+offset,len); ch[len]=0;
                    setvar(name,string(ch));
                    run_range(i+1,end);
                    offset=next;
                }
            } else if (!err && iterable.t == DICT && iterable.dict) {
                size_t count=iterable.dict->len;
                if (count > MAX_ITER) fail("kamus melebihi batas 10000 iterasi native");
                for (size_t j=0; j<count && !err && !returning; j++) {
                    if (++steps > MAX_STEPS) { fail("batas 100000 langkah terlampaui"); break; }
                    setvar(name, iterable.dict->keys[j]);
                    run_range(i+1,end);
                }
            } else if (!err && iterable.t == RANGE) {
                int iter=0;
                for (double x=iterable.range_start;
                     !err && !returning && (iterable.range_step > 0 ? x < iterable.range_end : x > iterable.range_end);
                     x += iterable.range_step) {
                    if (++iter > MAX_ITER) { fail("batas 10000 iterasi rentang() terlampaui"); break; }
                    if (++steps > MAX_STEPS) { fail("batas 100000 langkah terlampaui"); break; }
                    setvar(name, num(x));
                    run_range(i+1,end);
                }
            } else if (!err) {
                fail("perulangan native menerima list, teks, kamus, atau rentang()");
            }
            i=end;
        } else if(word("fungsi")) {
            int mid=-1, end=block_end(i,"fungsi",&mid);
            if(end<0) break;
            if(!function_registered_at(i,end) && !register_function(i,end)) break;
            i=end;
        } else if(word("balek")) {
            if(call_depth <= 0) { fail("balek hanya boleh di dalam fungsi"); break; }
            Val v=expr();
            if(!endline()) syntax_fail("karakter tambahan setelah nilai balek");
            if(!err) { return_value=v; returning=1; }
        } else if(word("mumet")) {
            int mid=-1, end=block_end(i,"mumet",&mid);
            if(end<0) break;
            int iter=0;
            while(!err && !returning) {
                line_no=i+1; p=program_lines[i]; ws(); word("mumet");
                Val c=expr();
                if(!endline()) syntax_fail("karakter tambahan pada kondisi mumet");
                if(err || !truth(c)) break;
                if(++iter>MAX_ITER) {
                    fail("batas 10000 iterasi mumet terlampaui"); break;
                }
                run_range(i+1,end);
            }
            i=end;
        } else if(word("lah")) {
            char name[128]={0};
            if(!identifier(name,sizeof name)) syntax_fail("nama variabel diharapkan");
            if(!err && hasvar(name)) fail("variabel sudah dibuat");
            if(!take("=")) syntax_fail("tanda '=' diharapkan");
            Val v=expr();
            if(!endline()) syntax_fail("karakter tambahan setelah ekspresi");
            if(!err) setvar(name,v);
        } else if(word("tanya")) {
            char name[128]={0};
            if(!identifier(name,sizeof name)) syntax_fail("nama variabel input diharapkan");
            if(!err && hasvar(name)) fail("variabel input sudah dibuat");
            if(!take("=")) syntax_fail("tanda '=' diharapkan setelah nama input");
            Val prompt=expr();
            if(!endline()) syntax_fail("karakter tambahan setelah prompt input");
            if(!err && prompt.t!=STR) fail("prompt tanya harus berupa teks");
            if(!err) {
                char input[SZ];
                fputs(prompt.s,stdout);
                fflush(stdout);
                if(!fgets(input,sizeof input,stdin)) {
                    fail("gagal membaca input pengguna"); 
                } else {
                    size_t len=strlen(input);
                    if(len && input[len-1]=='\n') input[--len]=0;
                    if(len && input[len-1]=='\r') input[--len]=0;
                    if(len==sizeof input-1 && !feof(stdin)) {
                        int ch;
                        while((ch=getchar())!='\n' && ch!=EOF) {}
                        fail("input terlalu panjang");
                    } else {
                        setvar(name,string(input));
                    }
                }
            }
        } else if(word("hedeh")) {
            Val v=expr();
            if(!endline()) syntax_fail("karakter tambahan setelah ekspresi");
            if(!err) printval(v);
        } else {
            char name[128]={0};
            if(!identifier(name,sizeof name)) syntax_fail("pernyataan belum didukung");
            else {
                int indexed=0; Val idx=num(0);
                if(take("[")) {
                    indexed=1; idx=expr();
                    if(!take("]")) syntax_fail("kurung siku tutup ']' diharapkan");
                }
                if(!take("=")) syntax_fail("tanda '=' diharapkan");
                else {
                    Val v=expr();
                    if(!endline()) syntax_fail("karakter tambahan setelah ekspresi");
                    if(!hasvar(name)) fail("variabel belum dibuat");
                    if(!err) for(int k=0;k<nvars;k++)
                        if(!strcmp(vars[k].name,name)) {
                            if(!indexed) vars[k].v=v;
                            else {
                                if (vars[k].v.t == DICT) {
                                    dict_set(vars[k].v.dict,idx,v);
                                } else {
                                    size_t at=0;
                                    if(list_index(vars[k].v,idx,&at))
                                        vars[k].v.list->items[at]=v;
                                }
                            }
                            break;
                        }
                }
            }
        }
    }
    return !err;
}

static int register_top_level_functions(void) {
    int depth = 0;
    for (int i = 0; i < program_count && !err; i++) {
        if (depth == 0 && line_word(i, "fungsi")) {
            int middle = -1;
            int end = block_end(i, "fungsi", &middle);
            if (end < 0 || !register_function(i, end)) return 0;
            i = end;
            continue;
        }
        if (line_word(i, "njir") || line_word(i, "mumet") || line_word(i, "untuk")) {
            depth++;
        } else if (depth > 0 &&
                   (line_close(i, "njir") || line_close(i, "mumet") || line_close(i, "untuk"))) {
            depth--;
        }
    }
    return !err;
}

static Val call_user_function(const char *name, Val *args, int argc) {
    Function *fn = NULL;
    for (int i = 0; i < function_count; i++) {
        if (!strcmp(functions[i].name, name)) { fn = &functions[i]; break; }
    }
    if (!fn) { fail("fungsi native tidak dikenal"); return (Val){.t=NIL}; }
    if (argc != fn->param_count) { fail("jumlah argumen fungsi tidak sesuai"); return (Val){.t=NIL}; }
    if (call_depth >= 100) { fail("batas kedalaman pemanggilan fungsi tercapai"); return (Val){.t=NIL}; }

    const char *saved_p = p;
    int saved_line = line_no;
    Var *saved_vars = malloc(sizeof vars);
    if (!saved_vars) { fail("memori scope fungsi habis"); return (Val){.t=NIL}; }
    memcpy(saved_vars, vars, sizeof vars);
    int saved_nvars = nvars;
    int saved_returning = returning;
    Val saved_return_value = return_value;

    nvars = 0;
    returning = 0;
    return_value = (Val){.t=NIL};
    for (int i = 0; i < argc && !err; i++) setvar(fn->params[i], args[i]);
    call_depth++;
    if (!err) run_range(fn->first_line, fn->end_line);
    call_depth--;

    Val result = returning ? return_value : (Val){.t=NIL};
    memcpy(vars, saved_vars, sizeof vars);
    free(saved_vars);
    nvars = saved_nvars;
    returning = saved_returning;
    return_value = saved_return_value;
    p = saved_p;
    line_no = saved_line;
    return result;
}


#ifndef PUSINGCUK_VERSION
#define PUSINGCUK_VERSION "0.8.0.dev0"
#endif

static void print_usage(FILE *out, const char *program) {
    fprintf(out,
        "Pusingcuk native %s\n"
        "Penggunaan: %s [opsi]\n"
        "           %s <program.cuk>\n"
        "           (ekstensi .pusingcuk tetap diterima)\n\n"
        "Opsi:\n"
        "  -h, --help       Tampilkan bantuan\n"
        "  -v, --version    Tampilkan versi runtime\n",
        PUSINGCUK_VERSION, program, program);
}

int main(int argc,char **argv) {
    if (argc == 2 && (!strcmp(argv[1], "--version") || !strcmp(argv[1], "-v"))) {
        printf("Pusingcuk native %s\n", PUSINGCUK_VERSION);
        return 0;
    }
    if (argc == 2 && (!strcmp(argv[1], "--help") || !strcmp(argv[1], "-h"))) {
        print_usage(stdout, argv[0]);
        return 0;
    }
    if(argc!=2) {
        print_usage(stderr, argv[0]);
        return 2;
    }
    if (argv[1][0] == '-' && strcmp(argv[1], "-")) {
        fprintf(stderr, "Opsi tidak dikenal: %s\n", argv[1]);
        print_usage(stderr, argv[0]);
        return 2;
    }
    FILE *f=fopen(argv[1],"r");
    if(!f) {
        if (errno == ENOENT) {
            fprintf(stderr, "Kesalahan: berkas tidak ditemukan: %s\n", argv[1]);
            return 3;
        }
        fprintf(stderr, "Kesalahan membaca berkas: %s: %s\n", argv[1], strerror(errno));
        return 1;
    }
    char buf[4096];
    while(fgets(buf,sizeof buf,f)) {
        if(program_count>=MAX_LINES) {
            fprintf(stderr,"Program terlalu panjang\n"); fclose(f); return 2;
        }
        size_t n=strlen(buf);
        program_lines[program_count]=malloc(n+1);
        if(!program_lines[program_count]) { fclose(f); return 2; }
        memcpy(program_lines[program_count++],buf,n+1);
    }
    if(ferror(f)) { perror("Kesalahan membaca program"); fclose(f); return 1; }
    fclose(f);
    if (register_top_level_functions()) run_range(0,program_count);
    int result=syntax_err?2:(err?1:0);
    for(int i=0;i<program_count;i++) free(program_lines[i]);
    for(size_t i=0;i<allocated_list_count;i++) {
        free(allocated_lists[i]->items);
        free(allocated_lists[i]);
    }
    for(size_t i=0;i<allocated_dict_count;i++) free(allocated_dicts[i]);
    return result;
}
