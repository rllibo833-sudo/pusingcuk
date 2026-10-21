#include "cuk_lexer.h"

#include <ctype.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define TOKEN_LIMIT 200000
#define TOKEN_TEXT_LIMIT 1048576

static const char *aliases[][2] = {
    {"jir","hedeh"},{"adooh","kampret"},{"gitu","selesai"},
    {"inthiseco","jancuk"},{"janggal","bukan"},{"gas","jancuk"},
    {"spill","hedeh"},{"bestie","lah"},{"valid","benar"},
    {"zonk","salah"},{"skip","kampret"},{"kelar","selesai"},
    {"bacot","hedeh"},{"bacrit","hedeh"},{"berak","hedeh"},
    {"berisik","hedeh"},{"bongkar","baca"},{"bongkar_json","baca_json"},
    {"cetak","hedeh"},{"crot","hedeh"},{"gas_api","kepo_internet"},
    {"gebber","hedeh"},{"gembor","hedeh"},{"impor","angkut"},
    {"jedor","hedeh"},{"keluarin","hedeh"},{"kepo","tanya"},
    {"kirim_gosip","kirim_api"},{"koar","hedeh"},{"muncrat","hedeh"},
    {"ngegas","hedeh"},{"nyalak","hedeh"},{"omong","hedeh"},
    {"parse_json","jadi_json"},{"print","hedeh"},{"sembur","hedeh"},
    {"semprot","hedeh"},{"senggol","hedeh"},{"simpen","tulis"},
    {"simpen_json","tulis_json"},{"stalking","kepo_internet"},
    {"suarakan","hedeh"},{"tampilkan","hedeh"},{"teriak","hedeh"},
    {"waktu","jam"}
};
static const char *keywords[] = {
    "jancuk","selesai","lah","hedeh","njir","kampret","mumet","untuk",
    "dalam","tanya","fungsi","balek","dan","atau","bukan","benar","salah",
    "coba","ketangkep","akhirnya","baca","baca_json","jadi_json","angkut",
    "kirim_api","kepo_internet","tulis","tulis_json","jam"
};

typedef struct {
    const char *src;
    size_t pos, line, col, len;
    CukTokenList *out;
} Scanner;

static char peek(Scanner *s, size_t n) {
    return s->pos + n < s->len ? s->src[s->pos+n] : '\0';
}
static char advance(Scanner *s) {
    char c=peek(s,0);
    if (!c) return c;
    s->pos++;
    if (c=='\n') { s->line++; s->col=1; } else s->col++;
    return c;
}
static int append_token(Scanner *s, CukTokenKind kind, const char *value,
                        size_t length, size_t line, size_t col) {
    if (s->out->count >= TOKEN_LIMIT || length > TOKEN_TEXT_LIMIT) {
        snprintf(s->out->error,sizeof s->out->error,"batas lexer terlampaui");
        s->out->error_line=line; s->out->error_column=col; return 0;
    }
    CukToken *next=realloc(s->out->items,(s->out->count+1)*sizeof *next);
    if (!next) {
        snprintf(s->out->error,sizeof s->out->error,"memori lexer habis");
        s->out->error_line=line; s->out->error_column=col; return 0;
    }
    s->out->items=next;
    char *copy=malloc(length+1);
    if (!copy) {
        snprintf(s->out->error,sizeof s->out->error,"memori token habis");
        s->out->error_line=line; s->out->error_column=col; return 0;
    }
    memcpy(copy,value,length); copy[length]='\0';
    s->out->items[s->out->count++]=(CukToken){kind,copy,line,col};
    return 1;
}
static int ident_start(char c) {
    unsigned char u=(unsigned char)c;
    return (u>='A'&&u<='Z')||(u>='a'&&u<='z')||c=='_';
}
static int ident_char(char c) {
    return ident_start(c)||(c>='0'&&c<='9');
}
static const char *canonical(const char *word) {
    for (size_t i=0;i<sizeof aliases/sizeof aliases[0];i++)
        if (!strcmp(word,aliases[i][0])) return aliases[i][1];
    return word;
}
static int is_keyword(const char *word) {
    for (size_t i=0;i<sizeof keywords/sizeof keywords[0];i++)
        if (!strcmp(word,keywords[i])) return 1;
    for (size_t i=0;i<sizeof aliases/sizeof aliases[0];i++)
        if (!strcmp(word,aliases[i][0])) return 1;
    return 0;
}
static int scan_string(Scanner *s) {
    size_t line=s->line,col=s->col; char quote=advance(s);
    size_t cap=32,n=0; char *buf=malloc(cap);
    if (!buf) return 0;
    while (peek(s,0) && peek(s,0)!=quote) {
        char c=advance(s);
        if (c=='\n') goto unterminated;
        if (c=='\\') {
            c=advance(s);
            switch(c) {
                case 'n': c='\n'; break; case 't': c='\t'; break;
                case 'r': c='\r'; break; case '\\': case '"': case '\'': break;
                default:
                    snprintf(s->out->error,sizeof s->out->error,"escape tidak dikenal");
                    s->out->error_line=s->line; s->out->error_column=s->col;
                    free(buf); return 0;
            }
        }
        if (n+1>=cap) {
            if (cap>=TOKEN_TEXT_LIMIT) { free(buf); return 0; }
            size_t next=cap*2; if(next>TOKEN_TEXT_LIMIT) next=TOKEN_TEXT_LIMIT;
            char *grown=realloc(buf,next); if(!grown){free(buf);return 0;}
            buf=grown;cap=next;
        }
        buf[n++]=c;
    }
    if (peek(s,0)!=quote) goto unterminated;
    advance(s);
    int ok=append_token(s,CUK_T_STRING,buf,n,line,col); free(buf); return ok;
unterminated:
    snprintf(s->out->error,sizeof s->out->error,"string belum ditutup atau melewati baris");
    s->out->error_line=line; s->out->error_column=col; free(buf); return 0;
}
int cuk_lex(const char *source, CukTokenList *out) {
    if (!source||!out) return 0;
    memset(out,0,sizeof *out);
    Scanner s={source,0,1,1,strlen(source),out};
    while (peek(&s,0)) {
        char c=peek(&s,0);
        if(c==' '||c=='\t'||c=='\r'){advance(&s);continue;}
        size_t line=s.line,col=s.col,start=s.pos;
        if(c=='\n'){advance(&s);if(!append_token(&s,CUK_T_NEWLINE,"\\n",2,line,col))goto fail;continue;}
        if(c=='#'){while(peek(&s,0)&&peek(&s,0)!='\n')advance(&s);continue;}
        if(c=='"'||c=='\''){if(!scan_string(&s))goto fail;continue;}
        if(c>='0'&&c<='9') {
            while(peek(&s,0)>='0'&&peek(&s,0)<='9')advance(&s);
            CukTokenKind k=CUK_T_INTEGER;
            if(peek(&s,0)=='.'&&peek(&s,1)>='0'&&peek(&s,1)<='9') {
                k=CUK_T_FLOAT;advance(&s);
                while(peek(&s,0)>='0'&&peek(&s,0)<='9')advance(&s);
            }
            if(peek(&s,0)=='e'||peek(&s,0)=='E') {
                k=CUK_T_FLOAT;advance(&s);
                if(peek(&s,0)=='+'||peek(&s,0)=='-')advance(&s);
                if(!(peek(&s,0)>='0'&&peek(&s,0)<='9')) {
                    snprintf(out->error,sizeof out->error,"eksponen angka tidak valid");
                    out->error_line=line;out->error_column=col;goto fail;
                }
                while(peek(&s,0)>='0'&&peek(&s,0)<='9')advance(&s);
            }
            if(!append_token(&s,k,source+start,s.pos-start,line,col))goto fail;
            continue;
        }
        if(ident_start(c)) {
            advance(&s);while(ident_char(peek(&s,0)))advance(&s);
            size_t n=s.pos-start;char *raw=malloc(n+1);if(!raw)goto fail;
            memcpy(raw,source+start,n);raw[n]='\0';
            const char *canon=canonical(raw); CukTokenKind k=is_keyword(raw)||is_keyword(canon)?CUK_T_KEYWORD:CUK_T_IDENT;
            int ok=append_token(&s,k,canon,strlen(canon),line,col);free(raw);if(!ok)goto fail;
            continue;
        }
        if(strchr("+-*/%=<>",c)) {
            advance(&s);if((c=='='||c=='!'||c=='<'||c=='>')&&peek(&s,0)=='=')advance(&s);
            else if(c=='/'&&peek(&s,0)=='/')advance(&s);
            if(!append_token(&s,CUK_T_OPERATOR,source+start,s.pos-start,line,col))goto fail;
            continue;
        }
        if(strchr("()[],:{}.",c)) {
            advance(&s);if(!append_token(&s,CUK_T_PUNCTUATION,source+start,1,line,col))goto fail;continue;
        }
        snprintf(out->error,sizeof out->error,"karakter tidak dikenal: %c",c);
        out->error_line=line;out->error_column=col;goto fail;
    }
    if(!append_token(&s,CUK_T_EOF,"",0,s.line,s.col))goto fail;
    return 1;
fail:
    cuk_tokens_free(out);return 0;
}
void cuk_tokens_free(CukTokenList *tokens) {
    if(!tokens)return;
    for(size_t i=0;i<tokens->count;i++)free(tokens->items[i].value);
    free(tokens->items);memset(tokens,0,sizeof *tokens);
}
const char *cuk_token_kind_name(CukTokenKind kind) {
    switch(kind) {
        case CUK_T_EOF:return "EOF";case CUK_T_NEWLINE:return "NEWLINE";
        case CUK_T_IDENT:return "IDENT";case CUK_T_KEYWORD:return "KEYWORD";
        case CUK_T_INTEGER:return "INTEGER";case CUK_T_FLOAT:return "FLOAT";
        case CUK_T_STRING:return "STRING";case CUK_T_OPERATOR:return "OPERATOR";
        case CUK_T_PUNCTUATION:return "PUNCTUATION";case CUK_T_ERROR:return "ERROR";
    }
    return "UNKNOWN";
}
