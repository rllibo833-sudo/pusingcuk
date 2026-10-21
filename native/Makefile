CC = clang
CFLAGS = -std=c11 -O2 -Wall -Wextra -Werror -Wno-misleading-indentation
BOOTSTRAP_OBJECTS = cuk_lexer.o cuk_parser.o cuk_ir.o

all: pusingcuk pusingcuk_bootstrap

pusingcuk: pusingcuk.c
	$(CC) $(CFLAGS) pusingcuk.c -o pusingcuk -lm

pusingcuk_bootstrap: pusingcuk_bootstrap.c $(BOOTSTRAP_OBJECTS)
	$(CC) $(CFLAGS) pusingcuk_bootstrap.c $(BOOTSTRAP_OBJECTS) -o pusingcuk_bootstrap

cuk_lexer.o: cuk_lexer.c cuk_lexer.h
	$(CC) $(CFLAGS) -c cuk_lexer.c -o cuk_lexer.o

cuk_parser.o: cuk_parser.c cuk_parser.h cuk_lexer.h
	$(CC) $(CFLAGS) -c cuk_parser.c -o cuk_parser.o

cuk_ir.o: cuk_ir.c cuk_ir.h cuk_parser.h
	$(CC) $(CFLAGS) -c cuk_ir.c -o cuk_ir.o

clean:
	rm -f pusingcuk pusingcuk_bootstrap $(BOOTSTRAP_OBJECTS)
