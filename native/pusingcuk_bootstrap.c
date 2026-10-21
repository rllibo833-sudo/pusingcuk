#include "cuk_lexer.h"
#include "cuk_parser.h"
#include "cuk_ir.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define SOURCE_LIMIT (8u * 1024u * 1024u)
static char *read_source(const char *path) {
 FILE *f=fopen(path,"rb"); if(!f){perror(path);return NULL;}
 if(fseek(f,0,SEEK_END)!=0){fclose(f);return NULL;} long z=ftell(f);
 if(z<0||(unsigned long)z>SOURCE_LIMIT){fprintf(stderr,"ukuran source tidak valid/melewati batas\n");fclose(f);return NULL;}
 rewind(f); char *s=malloc((size_t)z+1); if(!s){fclose(f);return NULL;}
 size_t n=fread(s,1,(size_t)z,f); if(n!=(size_t)z||ferror(f)){fprintf(stderr,"gagal membaca source lengkap\n");free(s);fclose(f);return NULL;}
 s[n]='\0'; fclose(f); if(memchr(s,'\0',n)){fprintf(stderr,"source mengandung byte NUL\n");free(s);return NULL;} return s;
}
int main(int argc,char **argv) {
 if(argc!=2){fprintf(stderr,"Pemakaian: %s berkas.cuk (IR v1 ke stdout)\n",argv[0]);return 2;}
 char *src=read_source(argv[1]); if(!src)return 1;
 CukTokenList ts={0}; CukParseResult p={0}; int ok=cuk_lex(src,&ts);
 if(!ok)fprintf(stderr,"Kesalahan lexer baris %zu kolom %zu: %s\n",ts.error_line,ts.error_column,ts.error);
 if(ok){ok=cuk_parse(&ts,&p);if(!ok)fprintf(stderr,"Kesalahan parser baris %zu kolom %zu: %s\n",p.error_line,p.error_column,p.error);}
 if(ok){const char *name=strrchr(argv[1],'/');name=name?name+1:argv[1];ok=cuk_ir_write_json(stdout,p.root,name);if(!ok)fprintf(stderr,"Gagal menulis IR v1\n");}
 cuk_ast_free(p.root);cuk_tokens_free(&ts);free(src);return ok?0:1;
}
