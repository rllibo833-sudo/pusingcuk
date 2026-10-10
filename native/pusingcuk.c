
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#define NV 256
#define SZ 1024

typedef enum { NUM, STR, BOOL, LIST } Type;
typedef struct Val Val;
typedef struct List List;
struct Val { Type t; double n; int b; char s[SZ]; List *list; };
#define MAX_LIST_ITEMS 256
struct List { size_t len; Val items[MAX_LIST_ITEMS]; };
typedef struct { char name[128]; Val v; } Var;
static Var vars[NV];
static int nvars, err, line_no;
static const char *p;

static void fail(const char *msg) {
    if (!err) fprintf(stderr, "Kesalahan baris %d: %s\n", line_no, msg);
    err = 1;
}
static Val num(double x) { Val v={0}; v.t=NUM; v.n=x; return v; }
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
static int truth(Val v) {
    if (v.t==BOOL) return v.b;
    if (v.t==NUM) return v.n!=0;
    return v.s[0]!=0;
}
static int equal(Val a, Val b) {
    if (a.t!=b.t) return 0;
    if (a.t==NUM) return a.n==b.n;
    if (a.t==BOOL) return a.b==b.b;
    return !strcmp(a.s,b.s);
}
static Val expr(void);
static Val listval(List *l) {
    Val v = {0}; v.t = LIST; v.list = l; return v;
}
static int list_index(Val v, Val idx, size_t *out) {
    if (v.t != LIST || !v.list) {
        fail("nilai bukan list"); return 0;
    }
    if (idx.t != NUM || idx.n < 0 ||
        idx.n >= (double)v.list->len ||
        idx.n != (double)(size_t)idx.n) {
        fail("indeks list di luar batas atau bukan bilangan bulat"); return 0;
    }
    *out = (size_t)idx.n; return 1;
}


static Val primary(void) {
    ws();
    if (take("[")) {
        List *l = calloc(1, sizeof *l);
        if (!l) { fail("memori list habis"); return listval(NULL); }
        if (!take("]")) {
            for (;;) {
                if (l->len >= MAX_LIST_ITEMS) {
                    fail("list terlalu panjang"); return listval(l);
                }
                l->items[l->len++] = expr();
                if (err) return listval(l);
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
            Val arg = expr();
            if (!take(")")) fail("kurung tutup ')' diharapkan");
            if (!strcmp(name,"panjang")) {
                if (arg.t != LIST || !arg.list) {
                    fail("panjang() membutuhkan list"); return num(0);
                }
                return num((double)arg.list->len);
            }
            fail("fungsi belum didukung"); return num(0);
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
    return result;
}
