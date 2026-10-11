/* PusingCuk PVM v1 assembler; portable C11. */
#include <ctype.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX_LINE 4096
#define MAX_PAYLOAD 2048
typedef enum { OP_HEDEH=1,OP_LAH,OP_NJIR,OP_KAMPRET,OP_MUMET,OP_FOR,OP_TANYA,OP_FUNGSI,OP_BALEK,OP_BUKA,OP_NGINTIP,OP_CORET,OP_TUTUP,OP_GEROMBOLAN,OP_PETIK,OP_CEMPLUNGIN,OP_PANJANG,OP_SENGGOL,OP_BEDAH } Opcode;
typedef struct Node { uint8_t op; unsigned line; char payload[MAX_PAYLOAD]; struct Node *next; } Node;
static char *trim(char*s){while(isspace((unsigned char)*s))s++;size_t n=strlen(s);while(n&&isspace((unsigned char)s[n-1]))s[--n]=0;return s;}
static int starts(const char*s,const char*p){size_t n=strlen(p);return !strncmp(s,p,n)&&(s[n]==0||isspace((unsigned char)s[n]));}
static int add(Node**h,Node**t,uint8_t op,unsigned ln,const char*p){Node*n=calloc(1,sizeof*n);if(!n)return 0;n->op=op;n->line=ln;if(p)snprintf(n->payload,sizeof n->payload,"%s",p);if(*t)(*t)->next=n;else *h=n;*t=n;return 1;}
static void android_path(char*p,size_t cap){size_t n=strlen(p);if(n<2||!((p[0]=='"'&&p[n-1]=='"')||(p[0]=='\''&&p[n-1]=='\'')))return;char raw[MAX_PAYLOAD];memcpy(raw,p+1,n-2);raw[n-2]=0;if(raw[0]=='~'&&raw[1]=='/'){const char*home=getenv("HOME");if(!home||!*home)home="/data/data/com.termux/files/home";char joined[MAX_PAYLOAD];snprintf(joined,sizeof joined,"%s/%s",home,raw+2);snprintf(p,cap,"\"%s\"",joined);}else if(!strncmp(raw,"/data/data/com.termux/files/home",32))snprintf(p,cap,"\"%s\"",raw);}
static int parse(Node**h,Node**t,char*line,unsigned ln){const char*s=trim(line);if(!*s||*s=='#'||!strcmp(s,"jancuk")||!strcmp(s,"selesai jancuk"))return 1;
struct R{const char*w;uint8_t op;}r[]={{"hedeh",OP_HEDEH},{"lah",OP_LAH},{"njir",OP_NJIR},{"kampret",OP_KAMPRET},{"mumet",OP_MUMET},{"untuk",OP_FOR},{"tanya",OP_TANYA},{"fungsi",OP_FUNGSI},{"balek",OP_BALEK},{"buka",OP_BUKA},{"ngintip",OP_NGINTIP},{"coret",OP_CORET},{"selesai",OP_TUTUP},{"gerombolan",OP_GEROMBOLAN},{"petik",OP_PETIK},{"cemplungin",OP_CEMPLUNGIN},{"panjang",OP_PANJANG},{"senggol",OP_SENGGOL},{"bedah",OP_BEDAH}};
for(size_t i=0;i<sizeof r/sizeof*r;i++)if(starts(s,r[i].w)){const char*a=s+strlen(r[i].w);while(isspace((unsigned char)*a))a++;if(r[i].op==OP_TUTUP&&starts(a,"jancuk"))return 1;char p[MAX_PAYLOAD];snprintf(p,sizeof p,"%s",a);if(r[i].op==OP_BUKA)android_path(p,sizeof p);return add(h,t,r[i].op,ln,p);}
const char*eq=strchr(s,'=');if(eq&&(eq==s||eq[-1]!='=')&&eq[1]!='=')return add(h,t,OP_LAH,ln,s);
fprintf(stderr,"pvm: baris %u: sintaks tidak dikenal\n",ln);return 0;}
static int u32(FILE*f,uint32_t n){unsigned char b[4]={(unsigned char)n,(unsigned char)(n>>8),(unsigned char)(n>>16),(unsigned char)(n>>24)};return fwrite(b,1,4,f)==4;}
int main(int argc,char**argv){if(argc<2||argc>3){fprintf(stderr,"Pakai: %s input.cuk [output.pvm]\n",argv[0]);return 2;}FILE*in=fopen(argv[1],"rb");if(!in){fprintf(stderr,"%s: %s\n",argv[1],strerror(errno));return 1;}Node*h=NULL,*t=NULL;char line[MAX_LINE];unsigned ln=0;int ok=1;while(fgets(line,sizeof line,in)){ln++;if(!strchr(line,'\n')&&!feof(in)){fprintf(stderr,"pvm: baris %u terlalu panjang\n",ln);ok=0;break;}if(!parse(&h,&t,line,ln)){ok=0;break;}}if(ferror(in))ok=0;fclose(in);const char*outname=argc==3?argv[2]:"program.pvm";if(ok){FILE*out=fopen(outname,"wb");if(!out){fprintf(stderr,"%s: %s\n",outname,strerror(errno));ok=0;}else{const unsigned char hdr[6]={'P','V','M','1',1,0};ok=fwrite(hdr,1,6,out)==6;for(Node*n=h;ok&&n;n=n->next){size_t z=strlen(n->payload);if(z>MAX_PAYLOAD||fputc(n->op,out)==EOF||!u32(out,(uint32_t)z)||fwrite(n->payload,1,z,out)!=z)ok=0;}if(fclose(out))ok=0;if(ok)printf("PVM: %s -> %s (%u baris sumber)\n",argv[1],outname,ln);}}while(h){Node*n=h->next;free(h);h=n;}return ok?0:1;}
