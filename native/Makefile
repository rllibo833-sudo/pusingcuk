CC = clang
CFLAGS = -std=c11 -O2 -Wall -Wextra -Werror

all: pusingcuk cuk_lexer.o

pusingcuk: pusingcuk.c
	$(CC) $(CFLAGS) pusingcuk.c -o pusingcuk -lm

cuk_lexer.o: cuk_lexer.c cuk_lexer.h
	$(CC) $(CFLAGS) -c cuk_lexer.c -o cuk_lexer.o

clean:
	rm -f pusingcuk cuk_lexer.o
