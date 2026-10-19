CC = clang
CFLAGS = -std=c11 -O2 -Wall -Wextra -Werror -D_POSIX_C_SOURCE=200809L

all: pusingcuk

pusingcuk: pusingcuk.c
	$(CC) $(CFLAGS) pusingcuk.c -o pusingcuk

cuk-bytecode-vm: bytecode_vm.c
	$(CC) $(CFLAGS) bytecode_vm.c -lm -o cuk-bytecode-vm

clean:
	rm -f pusingcuk cuk-bytecode-vm
