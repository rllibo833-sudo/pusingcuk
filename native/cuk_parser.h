#ifndef CUK_PARSER_H
#define CUK_PARSER_H
#include "cuk_lexer.h"
#include <stddef.h>
typedef enum {
 CUK_AST_PROGRAM, CUK_AST_DECLARE, CUK_AST_ASSIGN, CUK_AST_PRINT,
 CUK_AST_LITERAL, CUK_AST_VARIABLE, CUK_AST_BINARY, CUK_AST_UNARY,
 CUK_AST_FUNCTION, CUK_AST_RETURN, CUK_AST_CALL, CUK_AST_IF
} CukAstKind;
typedef struct CukAst CukAst;
struct CukAst {
 CukAstKind kind;
 size_t line;
 char *text;
 long long integer_value;
 CukAst **children;
 size_t child_count;
 char **params;
 size_t param_count;
 size_t then_count;
};
typedef struct { CukAst *root; char error[256]; size_t error_line,error_column; } CukParseResult;
int cuk_parse(const CukTokenList *tokens,CukParseResult *out);
void cuk_ast_free(CukAst *node);
#endif
