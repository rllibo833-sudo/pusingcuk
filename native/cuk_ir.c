#include "cuk_ir.h"
#include <stdio.h>
#include <string.h>
static void js(FILE*o,const char*s){fputc('"',o);for(const unsigned char*p=(const unsigned char*)(s?s:"");*p;p++){switch(*p){case '"':fputs("\\\"",o);break;case '\\':fputs("\\\\",o);break;case '\n':fputs("\\n",o);break;case '\r':fputs("\\r",o);break;case '\t':fputs("\\t",o);break;default:if(*p<32)fprintf(o,"\\u%04x",*p);else fputc(*p,o);}}fputc('"',o);}
static const char*kn(CukAstKind k){switch(k){case CUK_AST_PROGRAM:return"Program";case CUK_AST_DECLARE:return"Declare";case CUK_AST_ASSIGN:return"Assign";case CUK_AST_PRINT:return"Print";case CUK_AST_LITERAL:return"Literal";case CUK_AST_VARIABLE:return"Variable";case CUK_AST_BINARY:return"Binary";case CUK_AST_UNARY:return"Unary";case CUK_AST_FUNCTION:return"Function";case CUK_AST_RETURN:return"Return";case CUK_AST_CALL:return"Call";}return"Unknown";}
static void nj(FILE*o,const CukAst*n){
 fprintf(o,"{\"kind\":");js(o,kn(n->kind));fprintf(o,",\"line\":%zu,\"fields\":{",n->line);
 switch(n->kind){
 case CUK_AST_PROGRAM:fputs("\"body\":[",o);for(size_t i=0;i<n->child_count;i++){if(i)fputc(',',o);nj(o,n->children[i]);}fputc(']',o);break;
 case CUK_AST_DECLARE:case CUK_AST_ASSIGN:fputs("\"name\":",o);js(o,n->text);fputs(",\"value\":",o);nj(o,n->children[0]);break;
 case CUK_AST_PRINT:fputs("\"value\":",o);nj(o,n->children[0]);break;
 case CUK_AST_LITERAL:fputs("\"value\":",o);if(n->text)js(o,n->text);else fprintf(o,"%lld",n->integer_value);break;
 case CUK_AST_VARIABLE:fputs("\"name\":",o);js(o,n->text);break;
 case CUK_AST_BINARY:fputs("\"left\":",o);nj(o,n->children[0]);fputs(",\"op\":",o);js(o,n->text);fputs(",\"right\":",o);nj(o,n->children[1]);break;
 case CUK_AST_UNARY:fputs("\"op\":",o);js(o,n->text);fputs(",\"value\":",o);nj(o,n->children[0]);break;
 case CUK_AST_FUNCTION:fputs("\"name\":",o);js(o,n->text);fputs(",\"params\":[",o);for(size_t i=0;i<n->param_count;i++){if(i)fputc(',',o);js(o,n->params[i]);}fputs("],\"body\":[",o);for(size_t i=0;i<n->child_count;i++){if(i)fputc(',',o);nj(o,n->children[i]);}fputc(']',o);break;
 case CUK_AST_RETURN:fputs("\"value\":",o);if(n->child_count)nj(o,n->children[0]);else fputs("null",o);break;
 case CUK_AST_CALL:fputs("\"name\":",o);js(o,n->text);fputs(",\"args\":[",o);for(size_t i=0;i<n->child_count;i++){if(i)fputc(',',o);nj(o,n->children[i]);}fputc(']',o);break;
 }
 fputs("}}",o);
}
static void sm_entry(FILE*o,const CukAst*n,const char*path,int*comma){
 if(*comma)fputc(',',o);*comma=1;fprintf(o,"{\"path\":");js(o,path);fprintf(o,",\"line\":%zu}",n->line);
 if(n->kind==CUK_AST_PROGRAM||n->kind==CUK_AST_FUNCTION){for(size_t i=0;i<n->child_count;i++){char p[256];snprintf(p,sizeof p,"%.200s.fields.body[%zu]",path,i);sm_entry(o,n->children[i],p,comma);}}
 else if(n->kind==CUK_AST_DECLARE||n->kind==CUK_AST_ASSIGN||n->kind==CUK_AST_PRINT||n->kind==CUK_AST_UNARY||(n->kind==CUK_AST_RETURN&&n->child_count)){char p[256];snprintf(p,sizeof p,"%.200s.fields.value",path);sm_entry(o,n->children[0],p,comma);}
 else if(n->kind==CUK_AST_BINARY){char p[256];snprintf(p,sizeof p,"%.200s.fields.left",path);sm_entry(o,n->children[0],p,comma);snprintf(p,sizeof p,"%.200s.fields.right",path);sm_entry(o,n->children[1],p,comma);}
 else if(n->kind==CUK_AST_CALL){for(size_t i=0;i<n->child_count;i++){char p[256];snprintf(p,sizeof p,"%.200s.fields.args[%zu]",path,i);sm_entry(o,n->children[i],p,comma);}}
}
static void flags(const CukAst*n,int*f){if(n->kind==CUK_AST_PRINT)f[1]=1;if(n->kind==CUK_AST_BINARY||n->kind==CUK_AST_UNARY)f[2]=1;if(n->kind==CUK_AST_DECLARE||n->kind==CUK_AST_ASSIGN||n->kind==CUK_AST_VARIABLE)f[3]=1;if(n->kind==CUK_AST_FUNCTION||n->kind==CUK_AST_RETURN)f[4]=1;if(n->kind==CUK_AST_CALL)f[5]=1;for(size_t i=0;i<n->child_count;i++)flags(n->children[i],f);}
int cuk_ir_write_json(FILE*out,const CukAst*root,const char*source_name){
 if(!out||!root||root->kind!=CUK_AST_PROGRAM||!source_name||!*source_name||strchr(source_name,'/')||strchr(source_name,'\\')||!strcmp(source_name,".")||!strcmp(source_name,".."))return 0;
 int f[6]={1,0,0,0,0,0};flags(root,f);
 fputs("{\"format\":\"pusingcuk-ir\",\"ir_version\":1,\"language_version\":\"0.6-dev\",\"source_name\":",out);js(out,source_name);
 fputs(",\"features\":[",out);int comma=0;const char*names[]={"core","console-output","operators","variables","functions","calls"};const int order[]={5,1,0,4,2,3};
 for(size_t i=0;i<6;i++){int ix=order[i];if(f[ix]){if(comma)fputc(',',out);js(out,names[ix]);comma=1;}}
 fputs("],\"source_map\":[",out);int sm_comma=0;sm_entry(out,root,"$",&sm_comma);fputs("],\"program\":",out);nj(out,root);fputs("}\n",out);return !ferror(out);
}
