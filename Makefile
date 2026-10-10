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
	@set -eu; \
	actual="$$($(NATIVE_BIN) tests/native/slang_aliases.pusingcuk)"; \
	expected="$$(printf 'Pusingcuk native\ntidak\ncabang utama\nadooh aktif')"; \
	test "$$actual" = "$$expected"; \
	actual="$$($(NATIVE_BIN) tests/native/for_range.pusingcuk)"; \
	expected="$$(printf '2\n4\n6\n1\n3\n3\n2\n1')"; \
	test "$$actual" = "$$expected"; \
	if $(NATIVE_BIN) tests/native/range_zero_step.pusingcuk >/dev/null 2>&1; then \
		echo 'rentang dengan langkah nol seharusnya gagal' >&2; exit 1; \
	fi; \
	actual="$$($(NATIVE_BIN) tests/native/list_reallocation.pusingcuk)"; \
	test "$actual" = "1"
