#include "cuk_ir.h"
#include <ctype.h>
#include <string.h>

static void json_string(FILE *o,const char *s) {
    fputc('"',o);
    for(const unsigned char *p=(const unsigned char *)(s?s:"");*p;p++) {
        switch(*p) {
        case '"': fputs("\\\"",o); break;
        case '\\': fputs("\\\\",o); break;
        case '\n': fputs("\\n",o); break;
        case '\r': fputs("\\r",o); break;
        case '\t': fputs("\\t",o); break;
        default: if(*p<32)fprintf(o,"\\u%04x",*p);else fputc(*p,o);
        }
    }
    fputc('"',o);
}
static const char *kind_name(CukAstKind k) {
    switch(k) {
    case CUK_AST_PROGRAM:return "Program";case CUK_AST_DECLARE:return "Declare";
    case CUK_AST_PRINT:return "Print";case CUK_AST_LITERAL:return "Literal";
    case CUK_AST_VARIABLE:return "Variable";case CUK_AST_BINARY:return "Binary";
    }
    return "Unknown";
}
static void node_json(FILE *o,const CukAst *n) {
    fprintf(o,"{\"kind\":");json_string(o,kind_name(n->kind));
    fprintf(o,",\"line\":%zu,\"fields\":{",n->line);
    switch(n->kind) {
    case CUK_AST_PROGRAM:
        fputs("\"body\":[",o);
        for(size_t i=0;i<n->child_count;i++){if(i)fputc(',',o);node_json(o,n->children[i]);}
        fputs("]",o);break;
    case CUK_AST_DECLARE:
        fputs("\"name\":",o);json_string(o,n->text);
        fputs(",\"value\":",o);node_json(o,n->children[0]);break;
    case CUK_AST_PRINT:
        fputs("\"value\":",o);node_json(o,n->children[0]);break;
    case CUK_AST_LITERAL:
        fputs("\"value\":",o);
        if(n->text)json_string(o,n->text);else fprintf(o,"%lld",n->integer_value);
        break;
    case CUK_AST_VARIABLE:
        fputs("\"name\":",o);json_string(o,n->text);break;
    case CUK_AST_BINARY:
        fputs("\"left\":",o);node_json(o,n->children[0]);
        fputs(",\"op\":",o);json_string(o,n->text);
        fputs(",\"right\":",o);node_json(o,n->children[1]);break;
    }
    fputs("}}",o);
}
static void source_map(FILE *o,const CukAst *n,const char *path) {
    fprintf(o,"{\"path\":");json_string(o,path);
    fprintf(o,",\"line\":%zu}",n->line);
    if(n->kind==CUK_AST_PROGRAM) {
        for(size_t i=0;i<n->child_count;i++) {
            char child[256];snprintf(child,sizeof child,"%.200s.fields.body[%zu]",path,i);
            fputc(',',o);source_map(o,n->children[i],child);
        }
    } else if(n->kind==CUK_AST_DECLARE) {
        char child[256];snprintf(child,sizeof child,"%.200s.fields.value",path);
        fputc(',',o);source_map(o,n->children[0],child);
    } else if(n->kind==CUK_AST_PRINT) {
        char child[256];snprintf(child,sizeof child,"%.200s.fields.value",path);
        fputc(',',o);source_map(o,n->children[0],child);
    } else if(n->kind==CUK_AST_BINARY) {
        char child[256];snprintf(child,sizeof child,"%.200s.fields.left",path);
        fputc(',',o);source_map(o,n->children[0],child);
        snprintf(child,sizeof child,"%.200s.fields.right",path);
        fputc(',',o);source_map(o,n->children[1],child);
    }
}
static int has_kind(const CukAst *n,CukAstKind k) {
    if(n->kind==k)return 1;
    for(size_t i=0;i<n->child_count;i++)if(has_kind(n->children[i],k))return 1;
    return 0;
}
int cuk_ir_write_json(FILE *out,const CukAst *root,const char *source_name) {
    if(!out||!root||root->kind!=CUK_AST_PROGRAM||!source_name||!*source_name||
       strchr(source_name,'/')||strchr(source_name,'\\')||!strcmp(source_name,".")||!strcmp(source_name,".."))return 0;
    fputs("{\"format\":\"pusingcuk-ir\",\"ir_version\":1,\"language_version\":\"0.6-dev\",\"source_name\":",out);
    json_string(out,source_name);fputs(",\"features\":[",out);
    int comma=0;
    if(has_kind(root,CUK_AST_PRINT)){fputs("\"console-output\"",out);comma=1;}
    if(comma)fputc(44,out);fputs("\"core\"",out);comma=1;
    if(has_kind(root,CUK_AST_BINARY)){if(comma)fputc(44,out);fputs("\"operators\"",out);comma=1;}
    if(has_kind(root,CUK_AST_DECLARE)||has_kind(root,CUK_AST_VARIABLE)){if(comma)fputc(44,out);fputs("\"variables\"",out);}
    fputs("],\"source_map\":[",out);source_map(out,root,"$.program");
    fputs("],\"program\":",out);node_json(out,root);fputs("}\n",out);
    return !ferror(out);
}
