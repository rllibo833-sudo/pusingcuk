CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra
LDLIBS ?= -lm
NATIVE_BIN ?= $(CURDIR)/pusingcuk-native
VERSION ?= 0.7.1
PREFIX ?= /usr/local
DESTDIR ?=

.PHONY: native run-native test-native test-cli version install package

version:
	@printf '%s\n' '$(VERSION)'

native:
	$(CC) $(CFLAGS) -DPUSINGCUK_VERSION='"$(VERSION)"' native/pusingcuk.c $(LDLIBS) -o "$(NATIVE_BIN)"

run-native: native
	@test -n "$(FILE)" || (echo "Gunakan: make run-native FILE=program.pusingcuk" >&2; exit 2)
	"$(NATIVE_BIN)" "$(FILE)"

install: native
	install -d "$(DESTDIR)$(PREFIX)/bin"
	install -m 755 "$(NATIVE_BIN)" "$(DESTDIR)$(PREFIX)/bin/pusingcuk-native"

package: test-native
	@command -v git >/dev/null 2>&1 || (echo "git diperlukan untuk membuat source package" >&2; exit 2)
	@mkdir -p dist
	git archive --format=tar.gz --prefix="pusingcuk-$(VERSION)/" --output="dist/pusingcuk-$(VERSION)-source.tar.gz" HEAD
	@printf 'Paket sumber dibuat: dist/pusingcuk-%s-source.tar.gz\n' '$(VERSION)'

test-cli: native
	@test "$$($(NATIVE_BIN) --version)" = "Pusingcuk native $(VERSION)"
	@$(NATIVE_BIN) --help | grep -q -- '--version'
	@if $(NATIVE_BIN) >/dev/null 2>&1; then echo 'runtime tanpa argumen seharusnya gagal' >&2; exit 1; else status=$$?; test "$$status" -eq 2; fi
	@if $(NATIVE_BIN) --opsi-tidak-ada >/dev/null 2>&1; then echo 'opsi tidak dikenal seharusnya gagal' >&2; exit 1; else status=$?; test "$status" -eq 2; fi
	@set -eu; syntax_log="$(mktemp)"; missing_log="$(mktemp)"; trap 'rm -f "$syntax_log" "$missing_log"' EXIT; \
	if $(NATIVE_BIN) tests/conformance/malformed_expression.pusingcuk >/dev/null 2>"$syntax_log"; then echo 'sintaks rusak seharusnya gagal' >&2; exit 1; else status=$?; test "$status" -eq 2; fi; \
	grep -q '^Kesalahan sintaks:' "$syntax_log"; \
	missing="$(CURDIR)/.pusingcuk-missing-cli-test"; test ! -e "$missing"; \
	if $(NATIVE_BIN) "$missing" >/dev/null 2>"$missing_log"; then echo 'berkas hilang seharusnya gagal' >&2; exit 1; else status=$?; test "$status" -eq 3; fi; \
	grep -q 'berkas tidak ditemukan' "$missing_log"

test-native: native test-cli
	@set -eu; \
	actual="$$($(NATIVE_BIN) tests/native/slang_aliases.pusingcuk)"; \
	expected="$$(printf 'Pusingcuk native\ntidak\ncabang utama\nadooh aktif')"; \
	test "$$actual" = "$$expected"; \
	actual="$$($(NATIVE_BIN) tests/native/for_range.pusingcuk)"; \
	expected="$$(printf '2\n4\n6\n1\n3\n3\n2\n1')"; \
	test "$$actual" = "$$expected"; \
	actual="$$(printf 'Budi\n' | $(NATIVE_BIN) tests/native/strings_input.pusingcuk)"; \
	expected="$$(printf 'a\n🌾\nG\ne\nn\n \nZ\nNama? Halo, Budi')"; \
	test "$$actual" = "$$expected"; \
	actual="$$($(NATIVE_BIN) tests/native/dictionaries.pusingcuk)"; \
	expected="$$(printf 'Budi\n20\n21\nsatu\nya\n5\nnama\numur\n1\nokelah\nstatus\nkamus terisi\nkamus kosong')"; \
	if [ "$$actual" != "$$expected" ]; then printf "%s\\n" "$$actual" > $(CURDIR)/pusingcuk-dict.actual; printf "%s\\n" "$$expected" > $(CURDIR)/pusingcuk-dict.expected; diff -u $(CURDIR)/pusingcuk-dict.expected $(CURDIR)/pusingcuk-dict.actual; exit 1; fi; \
	if $(NATIVE_BIN) tests/native/dictionary_missing_key.pusingcuk >/dev/null 2>&1; then \
		echo 'kunci kamus yang tidak ada seharusnya gagal' >&2; exit 1; \
	fi; \
	if $(NATIVE_BIN) tests/native/dictionary_invalid_key.pusingcuk >/dev/null 2>&1; then \
		echo 'kunci kamus tak didukung seharusnya gagal' >&2; exit 1; \
	fi; \
	if $(NATIVE_BIN) tests/native/range_zero_step.pusingcuk >/dev/null 2>&1; then \
		echo 'rentang dengan langkah nol seharusnya gagal' >&2; exit 1; \
	fi; \
	if $(NATIVE_BIN) tests/native/string_index_out_of_range.pusingcuk >/dev/null 2>&1; then \
		echo 'indeks teks di luar batas seharusnya gagal' >&2; exit 1; \
	fi; \
	$(NATIVE_BIN) examples/native/rekap_anggaran.pusingcuk > $(CURDIR)/pusingcuk-budget.out; \
	grep -q 'Status: anggaran aman' $(CURDIR)/pusingcuk-budget.out; \
	grep -q '^1200000$$' $(CURDIR)/pusingcuk-budget.out; \
	grep -q '^1300000$$' $(CURDIR)/pusingcuk-budget.out; \
	$(NATIVE_BIN) tests/native/list_reallocation.pusingcuk > $(CURDIR)/pusingcuk-list-reallocation.out; \
	printf '1\n' > $(CURDIR)/pusingcuk-list-reallocation.expected; \
	diff -u $(CURDIR)/pusingcuk-list-reallocation.expected $(CURDIR)/pusingcuk-list-reallocation.out; \
	actual="$$($(NATIVE_BIN) tests/native/functions.pusingcuk)"; \
	expected="$$(printf '5\n120\n3\n9')"; \
	if [ "$$actual" != "$$expected" ]; then printf "fungsi actual=[%s] expected=[%s]\\n" "$$actual" "$$expected" >&2; exit 1; fi; \
	actual="$$($(NATIVE_BIN) tests/native/nested_functions.pusingcuk)"; \
	expected="$$(printf '11\n10')"; \
	test "$$actual" = "$$expected"; \
	actual="$$($(NATIVE_BIN) tests/native/dictionary_key_types.pusingcuk)"; \
	expected="$$(printf 'angka\nboolean\n2\ntidak')"; \
	test "$$actual" = "$$expected"; \
	if $(NATIVE_BIN) tests/native/function_wrong_arity.pusingcuk >/dev/null 2>&1; then \
		echo 'pemanggilan fungsi dengan jumlah argumen salah seharusnya gagal' >&2; exit 1; \
	fi
	if $(NATIVE_BIN) tests/native/numeric_overflow.pusingcuk >/dev/null 2>&1; then \
		echo 'operasi angka overflow seharusnya gagal' >&2; exit 1; \
	fi; \
	if $(NATIVE_BIN) tests/native/numeric_non_finite_literal.pusingcuk >/dev/null 2>&1; then \
		echo 'literal angka non-finite seharusnya gagal' >&2; exit 1; \
	fi; \
	$(NATIVE_BIN) tests/native/numeric_large_finite.pusingcuk > $(CURDIR)/pusingcuk-numeric-large.out; \
	grep -qx '1e+308' $(CURDIR)/pusingcuk-numeric-large.out
	@if $(NATIVE_BIN) tests/native/string_concat_overflow.pusingcuk >/dev/null 2>&1; then \
		echo 'penggabungan string melebihi batas seharusnya gagal' >&2; exit 1; \
	fi
	@if $(NATIVE_BIN) tests/native/list_overflow.pusingcuk >/dev/null 2>&1; then \
		echo 'list melebihi 256 item seharusnya gagal' >&2; exit 1; \
	fi
	@if $(NATIVE_BIN) tests/native/dictionary_overflow.pusingcuk >/dev/null 2>&1; then \
		echo 'kamus melebihi 256 entri seharusnya gagal' >&2; exit 1; \
	fi
	@$(NATIVE_BIN) tests/native/string_concat_limit.pusingcuk > $(CURDIR)/pusingcuk-string-limit.out
	@wc -c < $(CURDIR)/pusingcuk-string-limit.out | grep -qx '1024'
	@rm -f $(CURDIR)/pusingcuk-string-limit.out
