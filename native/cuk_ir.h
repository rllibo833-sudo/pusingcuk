#ifndef CUK_IR_H
#define CUK_IR_H
#include "cuk_parser.h"
#include <stdio.h>
int cuk_ir_write_json(FILE *out, const CukAst *root, const char *source_name);
#endif
