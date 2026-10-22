#include "cuk_parser.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {const CukTokenList*tokens;size_t pos;CukParseResult*out;} Parser;
static const CukToken*tok(Parser*p){size_t i=p->pos;if(i>=p->tokens->count)i=p->tokens->count-1;return&p->tokens->items[i];}
static int is(Parser*p,CukTokenKind k,const char*v){const CukToken*t=tok(p);return t->kind==k&&(!v||!strcmp(t->value,v));}
static const CukToken*take(Parser*p){const CukToken*t=tok(p);if(t->kind!=CUK_T_EOF)p->pos++;return t;}
static int need(Parser*p,CukTokenKind k,const char*v,const char*m){if(!is(p,k,v)){const CukToken*t=tok(p);snprintf(p->out->error,sizeof p->out->error,"%s (ditemukan '%s')",m,t->value);p->out->error_line=t->line;p->out->error_column=t->column;return 0;}take(p);return 1;}
static CukAst*node(CukAstKind k,size_t line){CukAst*n=calloc(1,sizeof*n);if(n){n->kind=k;n->line=line;}return n;}
static char*dupstr(const char*s){size_t n=strlen(s);char*p=malloc(n+1);if(p)memcpy(p,s,n+1);return p;}
static int child(CukAst*p,CukAst*c){CukAst**v=realloc(p->children,(p->child_count+1)*sizeof*v);if(!v)return 0;p->children=v;p->children[p->child_count++]=c;return 1;}
static int param(CukAst*n,const char*s){char**v=realloc(n->params,(n->param_count+1)*sizeof*v);if(!v)return 0;n->params=v;n->params[n->param_count]=dupstr(s);if(!n->params[n->param_count])return 0;n->param_count++;return 1;}
void cuk_ast_free(CukAst*n){if(!n)return;for(size_t i=0;i<n->child_count;i++)cuk_ast_free(n->children[i]);for(size_t i=0;i<n->param_count;i++)free(n->params[i]);free(n->params);free(n->children);free(n->text);free(n);}
static void skip_lines(Parser*p){while(is(p,CUK_T_NEWLINE,NULL))take(p);}
static CukAst*expr(Parser*p,int min);
static CukAst*primary(Parser*p){
 const CukToken*t=tok(p);CukAst*n=NULL;
 if(t->kind==CUK_T_INTEGER){take(p);errno=0;char*end=NULL;long long v=strtoll(t->value,&end,10);if(errno||!end||*end){snprintf(p->out->error,sizeof p->out->error,"integer di luar batas");p->out->error_line=t->line;p->out->error_column=t->column;return NULL;}n=node(CUK_AST_LITERAL,t->line);if(n)n->integer_value=v;return n;}
 if(t->kind==CUK_T_STRING){take(p);n=node(CUK_AST_LITERAL,t->line);if(n){n->text=dupstr(t->value);if(!n->text){cuk_ast_free(n);return NULL;}}return n;}
 if(t->kind==CUK_T_IDENT){
  take(p);
  if(is(p,CUK_T_PUNCTUATION,"(")){
   take(p);n=node(CUK_AST_CALL,t->line);if(!n)return NULL;n->text=dupstr(t->value);if(!n->text){cuk_ast_free(n);return NULL;}
   if(!is(p,CUK_T_PUNCTUATION,")"))for(;;){CukAst*a=expr(p,1);if(!a||!child(n,a)){cuk_ast_free(a);cuk_ast_free(n);return NULL;}if(!is(p,CUK_T_PUNCTUATION,","))break;take(p);if(is(p,CUK_T_PUNCTUATION,")")){snprintf(p->out->error,sizeof p->out->error,"argumen kosong setelah koma");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;cuk_ast_free(n);return NULL;}}
   if(!need(p,CUK_T_PUNCTUATION,")","pemanggilan fungsi belum ditutup")){cuk_ast_free(n);return NULL;}return n;
  }
  n=node(CUK_AST_VARIABLE,t->line);if(n){n->text=dupstr(t->value);if(!n->text){cuk_ast_free(n);return NULL;}}return n;
 }
 if(is(p,CUK_T_PUNCTUATION,"(")){take(p);n=expr(p,1);if(!n)return NULL;if(!need(p,CUK_T_PUNCTUATION,")","kurung ekspresi belum ditutup")){cuk_ast_free(n);return NULL;}return n;}
 if(is(p,CUK_T_OPERATOR,"-")||is(p,CUK_T_OPERATOR,"+")){take(p);CukAst*v=primary(p);if(!v)return NULL;if(t->value[0]=='+')return v;n=node(CUK_AST_UNARY,t->line);if(!n){cuk_ast_free(v);return NULL;}n->text=dupstr("-");if(!n->text){cuk_ast_free(n);cuk_ast_free(v);return NULL;}if(!child(n,v)){cuk_ast_free(n);cuk_ast_free(v);return NULL;}return n;}
 snprintf(p->out->error,sizeof p->out->error,"ekspresi bootstrap tidak didukung");p->out->error_line=t->line;p->out->error_column=t->column;return NULL;
}
static int prec(const char*op){if(!strcmp(op,"==")||!strcmp(op,"!=")||!strcmp(op,"<")||!strcmp(op,"<=")||!strcmp(op,">")||!strcmp(op,">="))return 1;if(!strcmp(op,"+")||!strcmp(op,"-"))return 2;if(!strcmp(op,"*")||!strcmp(op,"/")||!strcmp(op,"%")||!strcmp(op,"//"))return 3;return 0;}
static CukAst*expr(Parser*p,int min){CukAst*l=primary(p);if(!l)return NULL;while(is(p,CUK_T_OPERATOR,NULL)){const CukToken*op=tok(p);int q=prec(op->value);if(!q||q<min)break;take(p);CukAst*r=expr(p,q+1);if(!r){cuk_ast_free(l);return NULL;}CukAst*b=node(CUK_AST_BINARY,op->line);if(!b){cuk_ast_free(l);cuk_ast_free(r);return NULL;}b->text=dupstr(op->value);if(!b->text){cuk_ast_free(b);cuk_ast_free(l);cuk_ast_free(r);return NULL;}if(!child(b,l)){cuk_ast_free(b);cuk_ast_free(l);cuk_ast_free(r);return NULL;}if(!child(b,r)){cuk_ast_free(b);cuk_ast_free(r);return NULL;}l=b;}return l;}
static CukAst*statement(Parser*p,int in_function);
static CukAst*function(Parser*p){
 const CukToken*start=take(p);CukAst*n=node(CUK_AST_FUNCTION,start->line);if(!n)return NULL;
 const CukToken*name=tok(p);if(!need(p,CUK_T_IDENT,NULL,"'fungsi' harus diikuti nama fungsi"))goto bad;
 n->text=dupstr(name->value);if(!n->text)goto bad;
 if(!need(p,CUK_T_PUNCTUATION,"(","nama fungsi harus diikuti '('"))goto bad;
 if(!is(p,CUK_T_PUNCTUATION,")"))for(;;){
  const CukToken*arg=tok(p);if(!need(p,CUK_T_IDENT,NULL,"parameter fungsi harus berupa nama"))goto bad;
  for(size_t i=0;i<n->param_count;i++)if(!strcmp(n->params[i],arg->value)){snprintf(p->out->error,sizeof p->out->error,"parameter fungsi duplikat");p->out->error_line=arg->line;p->out->error_column=arg->column;goto bad;}
  if(!param(n,arg->value))goto bad;
  if(!is(p,CUK_T_PUNCTUATION,","))break;take(p);if(is(p,CUK_T_PUNCTUATION,")")){snprintf(p->out->error,sizeof p->out->error,"parameter kosong setelah koma");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;goto bad;}
 }
 if(!need(p,CUK_T_PUNCTUATION,")","daftar parameter belum ditutup"))goto bad;
 if(is(p,CUK_T_NEWLINE,NULL))skip_lines(p);else{snprintf(p->out->error,sizeof p->out->error,"baris baru wajib setelah deklarasi fungsi");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;goto bad;}
 while(!is(p,CUK_T_KEYWORD,"selesai")&&!is(p,CUK_T_EOF,NULL)){
  CukAst*s=statement(p,1);if(!s)goto bad;if(!child(n,s)){cuk_ast_free(s);goto bad;}
  if(is(p,CUK_T_NEWLINE,NULL))skip_lines(p);else if(!is(p,CUK_T_KEYWORD,"selesai")){snprintf(p->out->error,sizeof p->out->error,"harus ada baris baru antarpernyataan fungsi");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;goto bad;}
 }
 if(!need(p,CUK_T_KEYWORD,"selesai","fungsi harus ditutup dengan 'selesai fungsi'"))goto bad;
 if(!need(p,CUK_T_KEYWORD,"fungsi","penutup fungsi harus 'selesai fungsi'"))goto bad;
 return n;
bad:cuk_ast_free(n);return NULL;
}
static CukAst*conditional(Parser*p,int in_function){
 const CukToken*start=take(p);CukAst*n=node(CUK_AST_IF,start->line);if(!n)return NULL;
 CukAst*condition=expr(p,1);if(!condition)goto bad;
 if(!child(n,condition)){cuk_ast_free(condition);goto bad;}
 if(!is(p,CUK_T_NEWLINE,NULL)){snprintf(p->out->error,sizeof p->out->error,"baris baru wajib setelah kondisi njir");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;goto bad;}
 skip_lines(p);
 while(!is(p,CUK_T_KEYWORD,"kampret")&&!is(p,CUK_T_KEYWORD,"selesai")&&!is(p,CUK_T_EOF,NULL)){
  CukAst*s=statement(p,in_function);if(!s)goto bad;
  if(!child(n,s)){cuk_ast_free(s);goto bad;}
  n->then_count++;
  if(is(p,CUK_T_NEWLINE,NULL))skip_lines(p);
  else if(!is(p,CUK_T_KEYWORD,"kampret")&&!is(p,CUK_T_KEYWORD,"selesai")){
   snprintf(p->out->error,sizeof p->out->error,"harus ada baris baru antarpernyataan njir");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;goto bad;
  }
 }
 if(is(p,CUK_T_KEYWORD,"kampret")){
  take(p);
  if(!is(p,CUK_T_NEWLINE,NULL)){snprintf(p->out->error,sizeof p->out->error,"baris baru wajib setelah kampret");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;goto bad;}
  skip_lines(p);
  while(!is(p,CUK_T_KEYWORD,"selesai")&&!is(p,CUK_T_EOF,NULL)){
   CukAst*s=statement(p,in_function);if(!s)goto bad;
   if(!child(n,s)){cuk_ast_free(s);goto bad;}
   if(is(p,CUK_T_NEWLINE,NULL))skip_lines(p);
   else if(!is(p,CUK_T_KEYWORD,"selesai")){
    snprintf(p->out->error,sizeof p->out->error,"harus ada baris baru antarpernyataan kampret");p->out->error_line=tok(p)->line;p->out->error_column=tok(p)->column;goto bad;
   }
  }
 }
 if(!need(p,CUK_T_KEYWORD,"selesai","blok njir harus ditutup dengan 'selesai njir'"))goto bad;
 if(!need(p,CUK_T_KEYWORD,"njir","penutup kondisi harus 'selesai njir'"))goto bad;
 return n;
bad:cuk_ast_free(n);return NULL;
}
static CukAst*statement(Parser*p,int in_function){
 const CukToken*start=tok(p);CukAst*s=NULL;CukAst*v=NULL;
 if(is(p,CUK_T_KEYWORD,"njir"))return conditional(p,in_function);
 if(is(p,CUK_T_KEYWORD,"fungsi")){if(in_function){snprintf(p->out->error,sizeof p->out->error,"fungsi bersarang belum didukung");p->out->error_line=start->line;p->out->error_column=start->column;return NULL;}return function(p);}
 if(is(p,CUK_T_KEYWORD,"balek")){
  if(!in_function){snprintf(p->out->error,sizeof p->out->error,"'balek' hanya boleh di dalam fungsi");p->out->error_line=start->line;p->out->error_column=start->column;return NULL;}
  take(p);s=node(CUK_AST_RETURN,start->line);if(!s)return NULL;
  if(!is(p,CUK_T_NEWLINE,NULL)&&!is(p,CUK_T_KEYWORD,"selesai")&&!is(p,CUK_T_EOF,NULL)){v=expr(p,1);if(!v||!child(s,v)){cuk_ast_free(v);cuk_ast_free(s);return NULL;}}
  return s;
 }
 if(is(p,CUK_T_KEYWORD,"lah")){take(p);const CukToken*name=tok(p);if(!need(p,CUK_T_IDENT,NULL,"'lah' harus diikuti nama variabel"))return NULL;if(!need(p,CUK_T_OPERATOR,"=","deklarasi harus memakai '='"))return NULL;v=expr(p,1);if(!v)return NULL;s=node(CUK_AST_DECLARE,start->line);if(!s){cuk_ast_free(v);return NULL;}s->text=dupstr(name->value);if(!s->text||!child(s,v)){cuk_ast_free(s);cuk_ast_free(v);return NULL;}return s;}
 if(is(p,CUK_T_KEYWORD,"hedeh")){take(p);v=expr(p,1);if(!v)return NULL;s=node(CUK_AST_PRINT,start->line);if(!s){cuk_ast_free(v);return NULL;}if(!child(s,v)){cuk_ast_free(s);cuk_ast_free(v);return NULL;}return s;}
 if(is(p,CUK_T_IDENT,NULL)){const CukToken*name=take(p);if(!need(p,CUK_T_OPERATOR,"=","assignment harus memakai '='"))return NULL;v=expr(p,1);if(!v)return NULL;s=node(CUK_AST_ASSIGN,start->line);if(!s){cuk_ast_free(v);return NULL;}s->text=dupstr(name->value);if(!s->text||!child(s,v)){cuk_ast_free(s);cuk_ast_free(v);return NULL;}return s;}
 snprintf(p->out->error,sizeof p->out->error,"pernyataan belum didukung frontend bootstrap");p->out->error_line=start->line;p->out->error_column=start->column;return NULL;
}
int cuk_parse(const CukTokenList*tokens,CukParseResult*out){
 if(!tokens||!out||tokens->count==0)return 0;memset(out,0,sizeof*out);Parser p={tokens,0,out};skip_lines(&p);
 if(!need(&p,CUK_T_KEYWORD,"jancuk","program harus diawali 'jancuk'"))return 0;skip_lines(&p);
 CukAst*root=node(CUK_AST_PROGRAM,tok(&p)->line);if(!root)return 0;
 while(!is(&p,CUK_T_KEYWORD,"selesai")&&!is(&p,CUK_T_EOF,NULL)){
  CukAst*s=statement(&p,0);if(!s)goto fail;if(!child(root,s)){cuk_ast_free(s);goto fail;}
  if(is(&p,CUK_T_NEWLINE,NULL))skip_lines(&p);else if(!is(&p,CUK_T_KEYWORD,"selesai")){const CukToken*t=tok(&p);snprintf(out->error,sizeof out->error,"harus ada baris baru antarpernyataan");out->error_line=t->line;out->error_column=t->column;goto fail;}
 }
 if(!need(&p,CUK_T_KEYWORD,"selesai","program harus ditutup 'selesai'"))goto fail;
 if(!need(&p,CUK_T_KEYWORD,"jancuk","penutup harus 'selesai jancuk'"))goto fail;skip_lines(&p);
 if(!is(&p,CUK_T_EOF,NULL)){const CukToken*t=tok(&p);snprintf(out->error,sizeof out->error,"teks setelah penutup program");out->error_line=t->line;out->error_column=t->column;goto fail;}
 out->root=root;return 1;
fail:cuk_ast_free(root);return 0;
}
