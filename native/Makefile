CC = clang
CFLAGS = -std=c11 -O2 -Wall -Wextra -Werror

all: pusingcuk cuk_lexer.o cuk_parser.o

pusingcuk: pusingcuk.c
	$(CC) $(CFLAGS) pusingcuk.c -o pusingcuk -lm

cuk_lexer.o: cuk_lexer.c cuk_lexer.h
	$(CC) $(CFLAGS) -c cuk_lexer.c -o cuk_lexer.o

cuk_parser.o: cuk_parser.c cuk_parser.h cuk_lexer.h
	$(CC) $(CFLAGS) -c cuk_parser.c -o cuk_parser.o

clean:
	rm -f pusingcuk cuk_lexer.o cuk_parser.o
