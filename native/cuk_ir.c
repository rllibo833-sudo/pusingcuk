#include "cuk_ir.h"
#include <stdio.h>
#include <string.h>
static void js(FILE*o,const char*s){fputc('"',o);for(const unsigned char*p=(const unsigned char*)(s?s:"");*p;p++){switch(*p){case '"':fputs("\\\"",o);break;case '\\':fputs("\\\\",o);break;case '\n':fputs("\\n",o);break;case '\r':fputs("\\r",o);break;case '\t':fputs("\\t",o);break;default:if(*p<32)fprintf(o,"\\u%04x",*p);else fputc(*p,o);}}fputc('"',o);}
static const char*kn(CukAstKind k){switch(k){case CUK_AST_PROGRAM:return"Program";case CUK_AST_DECLARE:return"Declare";case CUK_AST_PRINT:return"Print";case CUK_AST_LITERAL:return"Literal";case CUK_AST_VARIABLE:return"Variable";case CUK_AST_BINARY:return"Binary";case CUK_AST_UNARY:return"Unary";}return"Unknown";}
static void nj(FILE*o,const CukAst*n){fprintf(o,"{\"kind\":");js(o,kn(n->kind));fprintf(o,",\"line\":%zu,\"fields\":{",n->line);switch(n->kind){
case CUK_AST_PROGRAM:fputs("\"body\":[",o);for(size_t i=0;i<n->child_count;i++){if(i)fputc(',',o);nj(o,n->children[i]);}fputc(']',o);break;
case CUK_AST_DECLARE:fputs("\"name\":",o);js(o,n->text);fputs(",\"value\":",o);nj(o,n->children[0]);break;
case CUK_AST_PRINT:fputs("\"value\":",o);nj(o,n->children[0]);break;
case CUK_AST_LITERAL:fputs("\"value\":",o);if(n->text)js(o,n->text);else fprintf(o,"%lld",n->integer_value);break;
case CUK_AST_VARIABLE:fputs("\"name\":",o);js(o,n->text);break;
case CUK_AST_BINARY:fputs("\"left\":",o);nj(o,n->children[0]);fputs(",\"op\":",o);js(o,n->text);fputs(",\"right\":",o);nj(o,n->children[1]);break;
case CUK_AST_UNARY:fputs("\"op\":",o);js(o,n->text);fputs(",\"value\":",o);nj(o,n->children[0]);break;
}}
static void sm(FILE*o,const CukAst*n,const char*path){fprintf(o,"{\"path\":");js(o,path);fprintf(o,",\"line\":%zu}",n->line);if(n->kind==CUK_AST_PROGRAM){for(size_t i=0;i<n->child_count;i++){char p[256];snprintf(p,sizeof p,"%.200s.fields.body[%zu]",path,i);fputc(',',o);sm(o,n->children[i],p);}}else if(n->kind==CUK_AST_DECLARE||n->kind==CUK_AST_PRINT||n->kind==CUK_AST_UNARY){char p[256];snprintf(p,sizeof p,"%.200s.fields.value",path);fputc(',',o);sm(o,n->children[0],p);}else if(n->kind==CUK_AST_BINARY){char p[256];snprintf(p,sizeof p,"%.200s.fields.left",path);fputc(',',o);sm(o,n->children[0],p);snprintf(p,sizeof p,"%.200s.fields.right",path);fputc(',',o);sm(o,n->children[1],p);}}
static void flags(const CukAst*n,int*f){if(n->kind==CUK_AST_PRINT)f[1]=1;if(n->kind==CUK_AST_BINARY||n->kind==CUK_AST_UNARY)f[2]=1;if(n->kind==CUK_AST_DECLARE||n->kind==CUK_AST_VARIABLE)f[3]=1;for(size_t i=0;i<n->child_count;i++)flags(n->children[i],f);}
int cuk_ir_write_json(FILE*out,const CukAst*root,const char*source_name){if(!out||!root||root->kind!=CUK_AST_PROGRAM||!source_name||!*source_name||strchr(source_name,'/')||strchr(source_name,'\\')||!strcmp(source_name,".")||!strcmp(source_name,".."))return 0;int f[4]={1,0,0,0};flags(root,f);fputs("{\"format\":\"pusingcuk-ir\",\"ir_version\":1,\"language_version\":\"0.6-dev\",\"source_name\":",out);js(out,source_name);fputs(",\"features\":[",out);int comma=0;const char*names[]={"core","console-output","operators","variables"};const int order[]={1,0,2,3};for(size_t i=0;i<4;i++){int ix=order[i];if(f[ix]){if(comma)fputc(',',out);js(out,names[ix]);comma=1;}}fputs("],\"source_map\":[",out);sm(out,root,"$");fputs("],\"program\":",out);nj(out,root);fputs("}\n",out);return !ferror(out);}
