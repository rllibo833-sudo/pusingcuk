
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#define NV 256
#define SZ 1024

typedef enum { NUM, STR, BOOL, LIST, RANGE } Type;
typedef struct Val Val;
typedef struct List List;
struct Val { Type t; double n; int b; char s[SZ]; List *list; double range_start, range_end, range_step; };
#define MAX_LIST_ITEMS 256
struct List { size_t len, capacity; Val *items; };
#define MAX_LIST_ALLOCATIONS 100000
static List *allocated_lists[MAX_LIST_ALLOCATIONS];
static size_t allocated_list_count;
typedef struct { char name[128]; Val v; } Var;
static Var vars[NV];
static int nvars, err, line_no;
static const char *p;

static void fail(const char *msg) {
    if (!err) fprintf(stderr, "Kesalahan baris %d: %s\n", line_no, msg);
    err = 1;
}
static Val num(double x) { Val v={0}; v.t=NUM; v.n=x; return v; }
static List *new_list(void) {
    if (allocated_list_count >= MAX_LIST_ALLOCATIONS) {
        fail("batas alokasi list native terlampaui"); return NULL;
    }
    List *list = calloc(1, sizeof *list);
    if (!list) { fail("memori list habis"); return NULL; }
    allocated_lists[allocated_list_count++] = list;
    return list;
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
    if (v.t==BOOL) return v.b;
    if (v.t==NUM) return v.n!=0;
    if (v.t==LIST) return v.list && v.list->len != 0;
    if (v.t==RANGE) return range_length(v) != 0;
    return v.s[0]!=0;
}
static int equal(Val a, Val b) {
    if (a.t!=b.t) return 0;
    if (a.t==NUM) return a.n==b.n;
    if (a.t==BOOL) return a.b==b.b;
    if (a.t==RANGE) return a.range_start==b.range_start && a.range_end==b.range_end && a.range_step==b.range_step;
    if (a.t==LIST) return a.list==b.list;
    return !strcmp(a.s,b.s);
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


static Val primary(void) {
    ws();
    if (take("[")) {
        List *l = new_list();
        if (!l) return listval(NULL);
        if (!take("]")) {
            for (;;) {
                Val item = expr();
                if (err || !append_list(l, item)) return listval(l);
                if (take("]")) break;
                if (!take(",")) {
                    fail("koma atau ']' diharapkan"); return listval(l);
                }
            }
        }
        return listval(l);
    }

    ws();
    if (take("(")) {
        Val v=expr();
        if (!take(")")) fail("kurung tutup ')' diharapkan");
        return v;
    }
    if (*p=='"') {
        p++; char buf[SZ]; size_t n=0;
        while (*p && *p!='"' && *p!='\n' && *p!='\r') {
            char c=*p++;
            if (c=='\\') {
                if (!*p) { fail("escape string tidak lengkap"); break; }
                c=*p++;
                if (c=='n') c='\n'; else if (c=='t') c='\t';
                else if (c!='"' && c!='\\') { fail("escape string tidak dikenal"); }
            }
            if (n+1<SZ) buf[n++]=c; else fail("string terlalu panjang");
        }
        if (*p!='"') fail("string belum ditutup"); else p++;
        buf[n]=0; return string(buf);
    }
    if (isdigit((unsigned char)*p) || *p=='.') {
        char *e; double x=strtod(p,&e);
        if (e==p) { fail("angka tidak valid"); return num(0); }
        p=e; return num(x);
    }
    if (isalpha((unsigned char)*p) || *p=='_') {
        char name[128]; size_t n=0;
        while (isalnum((unsigned char)*p) || *p=='_') {
            if (n+1<sizeof name) name[n++]=*p;
            p++;
        }
        name[n]=0;
        if (!strcmp(name,"benar")) return boolean(1);
        if (!strcmp(name,"salah")) return boolean(0);
        if (take("(")) {
            Val args[3]; int argc = 0;
            if (!take(")")) {
                for (;;) {
                    if (argc >= 3) {
                        fail("fungsi native menerima maksimal tiga argumen");
                        return num(0);
                    }
                    args[argc++] = expr();
                    if (err) return num(0);
                    if (take(")")) break;
                    if (!take(",")) {
                        fail("koma atau ')' diharapkan dalam argumen fungsi");
                        return num(0);
                    }
                }
            }
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
                fail("panjang() menerima list, teks, atau rentang"); return num(0);
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
            fail("fungsi native belum didukung"); return num(0);
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
            if (!take("]")) fail("kurung siku tutup ']' diharapkan");
            if (value.t == STR) {
                size_t start=0, end=0;
                if (!string_index(value,idx,&start,&end)) return string("");
                char ch[SZ]; size_t len=end-start;
                memcpy(ch,value.s+start,len); ch[len]=0;
                return string(ch);
            }
            size_t at=0;
            if (!list_index(value,idx,&at)) return num(0);
            return value.list->items[at];
        }
        return value;
    }
    fail("ekspresi tidak valid"); return num(0);
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
            a=num(a.n*b.n);
        } else if (take("//")) {
            Val b=unary();
            if (a.t!=NUM || b.t!=NUM) { fail("'//' membutuhkan angka"); return num(0); }
            if (b.n==0) { fail("pembagian dengan nol"); return num(0); }
            a=num(floor(a.n/b.n));
        } else if (take("%")) {
            Val b=unary();
            if (a.t!=NUM || b.t!=NUM) { fail("'%' membutuhkan angka"); return num(0); }
            if (b.n==0) { fail("modulo dengan nol"); return num(0); }
            a=num(a.n-floor(a.n/b.n)*b.n);
        } else if (take("/")) {
            Val b=unary();
            if (a.t!=NUM || b.t!=NUM) { fail("'/' membutuhkan angka"); return num(0); }
            if (b.n==0) { fail("pembagian dengan nol"); return num(0); }
            a=num(a.n/b.n);
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
                if (strlen(a.s)+strlen(b.s)>=sizeof tmp) { fail("hasil string terlalu panjang"); return string(""); }
                snprintf(tmp,sizeof tmp,"%s%s",a.s,b.s); a=string(tmp);
            } else if (a.t==NUM && b.t==NUM) a=num(a.n+b.n);
            else { fail("'+' membutuhkan dua angka atau dua string"); return num(0); }
        } else if (take("-")) {
            Val b=mul();
            if (a.t!=NUM || b.t!=NUM) { fail("'-' membutuhkan angka"); return num(0); }
            a=num(a.n-b.n);
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
    while (word("dan")) { Val b=compare(); a=boolean(truth(a)&&truth(b)); }
    return a;
}
static Val expr(void) {
    Val a=and_expr();
    while (word("atau")) { Val b=and_expr(); a=boolean(truth(a)||truth(b)); }
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
static void printval(Val v) {
    if(v.t==BOOL) puts(v.b?"okelah":"tidak");
    else if(v.t==STR) puts(v.s);
    else if(v.t==LIST) printf("[list: %zu]\n", v.list ? v.list->len : 0);
    else if(v.t==RANGE) printf("[rentang: %.0f]\n", range_length(v));
    else if(isfinite(v.n) && v.n==(long long)v.n) printf("%lld\n",(long long)v.n);
    else printf("%.10g\n",v.n);
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
    line_no=start+1; fail("blok tidak ditutup dengan benar"); return -1;
}
static int run_range(int first,int last) {
    for(int i=first;i<last && !err;i++) {
        if(++steps>MAX_STEPS) {
            line_no=i+1; fail("batas 100000 langkah terlampaui"); break;
        }
        line_no=i+1; p=program_lines[i]; ws();
        if(endline()) continue;
        if(word("jancuk")) continue;
        if(word("selesai")) { if(word("jancuk") && first==0 && i==last-1) continue; fail("penutup blok tidak sesuai"); break; }

        if(word("njir")) {
            Val c=expr();
            if(!endline()) fail("karakter tambahan pada kondisi njir");
            int mid=-1, end=block_end(i,"njir",&mid);
            if(end<0) break;
            if(!err) {
                if(truth(c)) run_range(i+1,mid>=0?mid:end);
                else if(mid>=0) run_range(mid+1,end);
            }
            i=end;
        } else if(word("kampret")) {
            fail("kampret tanpa njir");
        } else if(word("untuk")) {
            char name[128] = {0};
            if (!identifier(name, sizeof name)) { fail("nama variabel perulangan diharapkan"); break; }
            if (!word("dalam")) { fail("kata 'dalam' diharapkan setelah nama perulangan"); break; }
            Val iterable = expr();
            if (!endline()) fail("karakter tambahan setelah koleksi perulangan");
            int mid=-1, end=block_end(i,"untuk",&mid);
            if (end<0) break;
            if (!err && iterable.t == LIST && iterable.list) {
                size_t count = iterable.list->len;
                if (count > MAX_ITER) { fail("list melebihi batas 10000 iterasi native"); }
                for (size_t j=0; j<count && !err; j++) {
                    if (++steps > MAX_STEPS) { fail("batas 100000 langkah terlampaui"); break; }
                    setvar(name, iterable.list->items[j]);
                    run_range(i+1,end);
                }
            } else if (!err && iterable.t == STR) {
                size_t offset=0;
                int iter=0;
                while (!err && iterable.s[offset]) {
                    if (++iter > MAX_ITER) { fail("batas 10000 iterasi teks terlampaui"); break; }
                    if (++steps > MAX_STEPS) { fail("batas 100000 langkah terlampaui"); break; }
                    size_t next=utf8_next(iterable.s,offset);
                    char ch[SZ]; size_t len=next-offset;
                    memcpy(ch,iterable.s+offset,len); ch[len]=0;
                    setvar(name,string(ch));
                    run_range(i+1,end);
                    offset=next;
                }
            } else if (!err && iterable.t == RANGE) {
                int iter=0;
                for (double x=iterable.range_start;
                     !err && (iterable.range_step > 0 ? x < iterable.range_end : x > iterable.range_end);
                     x += iterable.range_step) {
                    if (++iter > MAX_ITER) { fail("batas 10000 iterasi rentang() terlampaui"); break; }
                    if (++steps > MAX_STEPS) { fail("batas 100000 langkah terlampaui"); break; }
                    setvar(name, num(x));
                    run_range(i+1,end);
                }
            } else if (!err) {
                fail("perulangan native saat ini menerima list, teks, atau rentang()");
            }
            i=end;
        } else if(word("mumet")) {
            int mid=-1, end=block_end(i,"mumet",&mid);
            if(end<0) break;
            int iter=0;
            while(!err) {
                line_no=i+1; p=program_lines[i]; ws(); word("mumet");
                Val c=expr();
                if(!endline()) fail("karakter tambahan pada kondisi mumet");
                if(err || !truth(c)) break;
                if(++iter>MAX_ITER) {
                    fail("batas 10000 iterasi mumet terlampaui"); break;
                }
                run_range(i+1,end);
            }
            i=end;
        } else if(word("lah")) {
            char name[128]={0};
            if(!identifier(name,sizeof name)) fail("nama variabel diharapkan");
            if(!err && hasvar(name)) fail("variabel sudah dibuat");
            if(!take("=")) fail("tanda '=' diharapkan");
            Val v=expr();
            if(!endline()) fail("karakter tambahan setelah ekspresi");
            if(!err) setvar(name,v);
        } else if(word("tanya")) {
            char name[128]={0};
            if(!identifier(name,sizeof name)) fail("nama variabel input diharapkan");
            if(!err && hasvar(name)) fail("variabel input sudah dibuat");
            if(!take("=")) fail("tanda '=' diharapkan setelah nama input");
            Val prompt=expr();
            if(!endline()) fail("karakter tambahan setelah prompt input");
            if(!err && prompt.t!=STR) fail("prompt tanya harus berupa teks");
            if(!err) {
                char input[SZ];
                fputs(prompt.s,stdout);
                fflush(stdout);
                if(!fgets(input,sizeof input,stdin)) {
                    fail("gagal membaca input pengguna"); 
                } else {
                    size_t len=strlen(input);
                    if(len && input[len-1]=='\\n') input[--len]=0;
                    if(len && input[len-1]=='\\r') input[--len]=0;
                    if(len==sizeof input-1 && !feof(stdin)) {
                        int ch;
                        while((ch=getchar())!='\\n' && ch!=EOF) {}
                        fail("input terlalu panjang");
                    } else {
                        setvar(name,string(input));
                    }
                }
            }
        } else if(word("hedeh")) {
            Val v=expr();
            if(!endline()) fail("karakter tambahan setelah ekspresi");
            if(!err) printval(v);
        } else {
            char name[128]={0};
            if(!identifier(name,sizeof name)) fail("pernyataan belum didukung");
            else {
                int indexed=0; Val idx=num(0);
                if(take("[")) {
                    indexed=1; idx=expr();
                    if(!take("]")) fail("kurung siku tutup ']' diharapkan");
                }
                if(!take("=")) fail("tanda '=' diharapkan");
                else {
                    Val v=expr();
                    if(!endline()) fail("karakter tambahan setelah ekspresi");
                    if(!hasvar(name)) fail("variabel belum dibuat");
                    if(!err) for(int k=0;k<nvars;k++)
                        if(!strcmp(vars[k].name,name)) {
                            if(!indexed) vars[k].v=v;
                            else {
                                size_t at=0;
                                if(list_index(vars[k].v,idx,&at))
                                    vars[k].v.list->items[at]=v;
                            }
                            break;
                        }
                }
            }
        }
    }
    return !err;
}

int main(int argc,char **argv) {
    if(argc!=2) {
        fprintf(stderr,"Penggunaan: %s program.pusingcuk\n",argv[0]); return 2;
    }
    FILE *f=fopen(argv[1],"r");
    if(!f) { perror("Kesalahan membuka berkas"); return 2; }
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
    if(ferror(f)) { perror("Gagal membaca program"); fclose(f); return 2; }
    fclose(f);
    run_range(0,program_count);
    int result=err?1:0;
    for(int i=0;i<program_count;i++) free(program_lines[i]);
    for(size_t i=0;i<allocated_list_count;i++) {
        free(allocated_lists[i]->items);
        free(allocated_lists[i]);
    }
    return result;
}
