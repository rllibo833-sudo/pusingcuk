#ifndef CUK_LEXER_H
#define CUK_LEXER_H

#include <stddef.h>

typedef enum {
    CUK_T_EOF, CUK_T_NEWLINE, CUK_T_IDENT, CUK_T_KEYWORD,
    CUK_T_INTEGER, CUK_T_FLOAT, CUK_T_STRING, CUK_T_OPERATOR,
    CUK_T_PUNCTUATION, CUK_T_ERROR
} CukTokenKind;

typedef struct {
    CukTokenKind kind;
    char *value;
    size_t line;
    size_t column;
} CukToken;

typedef struct {
    CukToken *items;
    size_t count;
    char error[256];
    size_t error_line;
    size_t error_column;
} CukTokenList;

/* Lexes source into owned tokens. Returns 1 on success, 0 on lexical error. */
int cuk_lex(const char *source, CukTokenList *out);
void cuk_tokens_free(CukTokenList *tokens);
const char *cuk_token_kind_name(CukTokenKind kind);

#endif
