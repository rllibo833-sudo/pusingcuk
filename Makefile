CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra
LDLIBS ?= -lm
NATIVE_BIN ?= /tmp/pusingcuk-native

.PHONY: native run-native test-native

native:
	$(CC) $(CFLAGS) native/pusingcuk.c $(LDLIBS) -o "$(NATIVE_BIN)"

run-native: native
	@test -n "$(FILE)" || (echo "Gunakan: make run-native FILE=program.pusingcuk" >&2; exit 2)
	"$(NATIVE_BIN)" "$(FILE)"

test-native: native
	@actual="$$($(NATIVE_BIN) tests/native/slang_aliases.pusingcuk)"; expected="$$(printf 'Pusingcuk native\ntidak\ncabang utama\nadooh aktif')"; test "$$actual" = "$$expected"
