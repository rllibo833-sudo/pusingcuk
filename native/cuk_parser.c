#include "cuk_parser.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const CukTokenList *tokens;
    size_t pos;
    CukParseResult *out;
} Parser;

static const CukToken *tok(Parser *p) {
    size_t i=p->pos;
    if(i>=p->tokens->count)i=p->tokens->count-1;
    return &p->tokens->items[i];
}
static int is(Parser *p,CukTokenKind kind,const char *value) {
    const CukToken *t=tok(p);
    return t->kind==kind && (!value || !strcmp(t->value,value));
}
static const CukToken *take(Parser *p) {
    const CukToken *t=tok(p);
    if(t->kind!=CUK_T_EOF)p->pos++;
    return t;
}
static int need(Parser *p,CukTokenKind kind,const char *value,const char *message) {
    if(!is(p,kind,value)) {
        const CukToken *t=tok(p);
        snprintf(p->out->error,sizeof p->out->error,"%s (ditemukan '%s')",message,t->value);
        p->out->error_line=t->line;p->out->error_column=t->column;return 0;
    }
    take(p);return 1;
}
static CukAst *new_node(CukAstKind kind,size_t line) {
    CukAst *n=calloc(1,sizeof *n);if(n){n->kind=kind;n->line=line;}return n;
}
static char *copy_text(const char *s) {
    size_t n=strlen(s);char *p=malloc(n+1);if(p)memcpy(p,s,n+1);return p;
}
static int add_child(CukAst *parent,CukAst *child) {
    CukAst **p=realloc(parent->children,(parent->child_count+1)*sizeof *p);
    if(!p)return 0;
    parent->children=p;parent->children[parent->child_count++]=child;return 1;
}
void cuk_ast_free(CukAst *n) {
    if(!n)return;
    for(size_t i=0;i<n->child_count;i++)cuk_ast_free(n->children[i]);
    free(n->children);free(n->text);free(n);
}
static void skip_lines(Parser *p) { while(is(p,CUK_T_NEWLINE,NULL))take(p); }

static CukAst *expression(Parser *p);
static CukAst *primary(Parser *p) {
    const CukToken *t=tok(p); CukAst *n=NULL;
    if(t->kind==CUK_T_INTEGER) {
        take(p);n=new_node(CUK_AST_LITERAL,t->line);
        if(n)n->integer_value=strtoll(t->value,NULL,10);
        return n;
    }
    if(t->kind==CUK_T_STRING) {
        take(p);n=new_node(CUK_AST_LITERAL,t->line);
        if(n){n->text=copy_text(t->value);if(!n->text){cuk_ast_free(n);return NULL;}}
        return n;
    }
    if(t->kind==CUK_T_IDENT) {
        take(p);n=new_node(CUK_AST_VARIABLE,t->line);
        if(n){n->text=copy_text(t->value);if(!n->text){cuk_ast_free(n);return NULL;}}
        return n;
    }
    snprintf(p->out->error,sizeof p->out->error,"ekspresi bootstrap tidak didukung");
    p->out->error_line=t->line;p->out->error_column=t->column;return NULL;
}
static CukAst *expression(Parser *p) {
    CukAst *left=primary(p);if(!left)return NULL;
    while(is(p,CUK_T_OPERATOR,"+")) {
        const CukToken *op=take(p);CukAst *right=primary(p);
        if(!right){cuk_ast_free(left);return NULL;}
        CukAst *bin=new_node(CUK_AST_BINARY,op->line);
        if(!bin){cuk_ast_free(left);cuk_ast_free(right);return NULL;}
        bin->text=copy_text("+");
        if(!bin->text){cuk_ast_free(bin);cuk_ast_free(left);cuk_ast_free(right);return NULL;}
        if(!add_child(bin,left)){cuk_ast_free(bin);cuk_ast_free(left);cuk_ast_free(right);return NULL;}
        if(!add_child(bin,right)){cuk_ast_free(bin);cuk_ast_free(right);return NULL;}
        left=bin;
    }
    return left;
}
int cuk_parse(const CukTokenList *tokens,CukParseResult *out) {
    if(!tokens||!out||tokens->count==0)return 0;
    memset(out,0,sizeof *out);Parser p={tokens,0,out};
    skip_lines(&p);
    if(!need(&p,CUK_T_KEYWORD,"jancuk","program harus diawali 'jancuk'"))return 0;
    skip_lines(&p);
    CukAst *root=new_node(CUK_AST_PROGRAM,1);if(!root)return 0;
    while(!is(&p,CUK_T_KEYWORD,"selesai")&&!is(&p,CUK_T_EOF,NULL)) {
        const CukToken *start=tok(&p);CukAst *stmt=NULL;
        if(is(&p,CUK_T_KEYWORD,"lah")) {
            take(&p);const CukToken *name=tok(&p);
            if(!need(&p,CUK_T_IDENT,NULL,"'lah' harus diikuti nama variabel"))goto fail;
            if(!need(&p,CUK_T_OPERATOR,"=","deklarasi harus memakai '='"))goto fail;
            CukAst *value=expression(&p);if(!value)goto fail;
            stmt=new_node(CUK_AST_DECLARE,start->line);
            if(!stmt){cuk_ast_free(value);goto fail;}
            stmt->text=copy_text(name->value);
            if(!stmt->text){cuk_ast_free(stmt);cuk_ast_free(value);goto fail;}
            if(!add_child(stmt,value)){cuk_ast_free(stmt);cuk_ast_free(value);goto fail;}
        } else if(is(&p,CUK_T_KEYWORD,"hedeh")) {
            take(&p);CukAst *value=expression(&p);if(!value)goto fail;
            stmt=new_node(CUK_AST_PRINT,start->line);
            if(!stmt){cuk_ast_free(value);goto fail;}
            if(!add_child(stmt,value)){cuk_ast_free(stmt);cuk_ast_free(value);goto fail;}
        } else {
            snprintf(out->error,sizeof out->error,"pernyataan belum didukung frontend bootstrap");
            out->error_line=start->line;out->error_column=start->column;goto fail;
        }
        if(!add_child(root,stmt)){cuk_ast_free(stmt);goto fail;}
        if(is(&p,CUK_T_NEWLINE,NULL))skip_lines(&p);
        else if(!is(&p,CUK_T_KEYWORD,"selesai")) {
            const CukToken *t=tok(&p);
            snprintf(out->error,sizeof out->error,"harus ada baris baru antarpernyataan");
            out->error_line=t->line;out->error_column=t->column;goto fail;
        }
    }
    if(!need(&p,CUK_T_KEYWORD,"selesai","program harus ditutup 'selesai'"))goto fail;
    if(!need(&p,CUK_T_KEYWORD,"jancuk","penutup harus 'selesai jancuk'"))goto fail;
    skip_lines(&p);
    if(!is(&p,CUK_T_EOF,NULL)) {
        const CukToken *t=tok(&p);snprintf(out->error,sizeof out->error,"teks setelah penutup program");
        out->error_line=t->line;out->error_column=t->column;goto fail;
    }
    out->root=root;return 1;
fail:
    cuk_ast_free(root);return 0;
}
