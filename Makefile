CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra
LDLIBS ?= -lm
NATIVE_BIN ?= $(CURDIR)/pusingcuk-native
BOOTSTRAP_BIN ?= $(CURDIR)/pusingcuk-bootstrap
VERSION ?= 0.8.0.dev0
LANGUAGE_VERSION ?= 0.6-dev
PREFIX ?= /usr/local
DESTDIR ?=

.PHONY: native run-native native-bootstrap run-native-bootstrap test test-native test-cli test-registered-rules version language-version install package

version:
	@printf '%s\n' '$(VERSION)'

language-version:
	@printf '%s\n' '$(LANGUAGE_VERSION)'

test:
	python -m unittest discover -s tests -v
	python tools/conformance.py
	$(MAKE) test-native

native:
	$(CC) $(CFLAGS) -DPUSINGCUK_VERSION='"$(VERSION)"' native/pusingcuk.c $(LDLIBS) -o "$(NATIVE_BIN)"

run-native: native
	@test -n "$(FILE)" || (echo "Gunakan: make run-native FILE=program.cuk" >&2; exit 2)
	"$(NATIVE_BIN)" "$(FILE)"

# Native source frontend: .cuk -> native lexer/parser/AST -> IR v1 JSON.
native-bootstrap:
	$(CC) $(CFLAGS) native/pusingcuk_bootstrap.c native/cuk_lexer.c native/cuk_parser.c native/cuk_ir.c -o "$(BOOTSTRAP_BIN)"

run-native-bootstrap: native-bootstrap
	@test -n "$(FILE)" || (echo "Gunakan: make run-native-bootstrap FILE=program.cuk" >&2; exit 2)
	"$(BOOTSTRAP_BIN)" "$(FILE)"

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
	@actual="$$(printf 'jancuk\nhedeh 123\nselesai jancuk\n' | $(NATIVE_BIN) -)"; test "$$actual" = "123"
	@if $(NATIVE_BIN) >/dev/null 2>&1; then echo 'runtime tanpa argumen seharusnya gagal' >&2; exit 1; else status=$$?; test "$$status" -eq 2; fi
	@if $(NATIVE_BIN) --opsi-tidak-ada >/dev/null 2>&1; then echo 'opsi tidak dikenal seharusnya gagal' >&2; exit 1; else status=$$?; test "$$status" -eq 2; fi
	@set -eu; syntax_log=".pusingcuk-syntax-test.log"; missing_log=".pusingcuk-missing-test.log"; rm -f "$syntax_log" "$missing_log"; trap 'rm -f "$syntax_log" "$missing_log"' EXIT; \
	if $(NATIVE_BIN) tests/conformance/malformed_expression.pusingcuk >/dev/null 2>"$$syntax_log"; then echo 'sintaks rusak seharusnya gagal' >&2; exit 1; else status=$$?; test "$$status" -eq 2; fi; \
	grep -q '^Kesalahan sintaks:' "$$syntax_log"; \
	missing="$(CURDIR)/.pusingcuk-missing-cli-test"; test ! -e "$$missing"; \
	if $(NATIVE_BIN) "$$missing" >/dev/null 2>"$$missing_log"; then echo 'berkas hilang seharusnya gagal' >&2; exit 1; else status=$$?; test "$$status" -eq 3; fi; \
	grep -q 'berkas tidak ditemukan' "$$missing_log"

test-native: native test-cli test-registered-rules
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
	if [ "$$actual" != "$$expected" ]; then printf "%s\n" "$$actual" > $(CURDIR)/pusingcuk-dict.actual; printf "%s\n" "$$expected" > $(CURDIR)/pusingcuk-dict.expected; diff -u $(CURDIR)/pusingcuk-dict.expected $(CURDIR)/pusingcuk-dict.actual; exit 1; fi; \
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
	grep -q 'Status: AMAN - target tabungan tercapai' $(CURDIR)/pusingcuk-budget.out; \
	grep -q '^965000$$' $(CURDIR)/pusingcuk-budget.out; \
	grep -q '^1215000$$' $(CURDIR)/pusingcuk-budget.out; \
	$(NATIVE_BIN) tests/native/list_reallocation.pusingcuk > $(CURDIR)/pusingcuk-list-reallocation.out; \
	printf '1\n' > $(CURDIR)/pusingcuk-list-reallocation.expected; \
	diff -u $(CURDIR)/pusingcuk-list-reallocation.expected $(CURDIR)/pusingcuk-list-reallocation.out; \
	actual="$$($(NATIVE_BIN) tests/native/functions.pusingcuk)"; \
	expected="$$(printf '5\n120\n3\n9')"; \
	if [ "$$actual" != "$$expected" ]; then printf "fungsi actual=[%s] expected=[%s]\n" "$$actual" "$$expected" >&2; exit 1; fi; \
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

	@actual="$$($(NATIVE_BIN) examples/core/anggaran_threshold.cuk)"; \
	 expected="$$(printf 'DALAM_BATAS\nDALAM_BATAS\nPERLU_PERSETUJUAN\nINPUT_TIDAK_VALID\nINPUT_TIDAK_VALID')"; \
	 test "$$actual" = "$$expected"

	@actual="$$($(NATIVE_BIN) tests/native/conversions.cuk)"; \
	 expected="$$(printf '42\nokelah\ntidak\n42\n-3\n2.5\ntidak\nokelah')"; \
	 test "$$actual" = "$$expected"
	@if $(NATIVE_BIN) tests/native/conversions_invalid_integer.cuk >/dev/null 2>&1; then echo 'bilangan("3.0") seharusnya gagal' >&2; exit 1; fi
	@if $(NATIVE_BIN) tests/native/conversions_empty_number.cuk >/dev/null 2>&1; then echo 'desimal teks kosong/whitespace seharusnya gagal' >&2; exit 1; fi
	@if $(NATIVE_BIN) tests/native/conversions_non_finite_decimal.cuk >/dev/null 2>&1; then echo 'desimal teks non-finite seharusnya gagal' >&2; exit 1; fi
	@set -eu; \
	 actual="$$(printf '0\n1000000\n' | $(NATIVE_BIN) examples/core/anggaran_threshold_service.cuk)"; \
	 test "$$actual" = "DALAM_BATAS"; \
	 actual="$$(printf '1000000\n1000000\n' | $(NATIVE_BIN) examples/core/anggaran_threshold_service.cuk)"; \
	 test "$$actual" = "DALAM_BATAS"; \
	 actual="$$(printf '1000001\n1000000\n' | $(NATIVE_BIN) examples/core/anggaran_threshold_service.cuk)"; \
	 test "$$actual" = "PERLU_PERSETUJUAN"; \
	 actual="$$(printf '%s\n' '-1' '1000000' | $(NATIVE_BIN) examples/core/anggaran_threshold_service.cuk)"; \
	 test "$$actual" = "INPUT_TIDAK_VALID"; \
	 actual="$$(printf '250000\n-1\n' | $(NATIVE_BIN) examples/core/anggaran_threshold_service.cuk)"; \
	 test "$$actual" = "INPUT_TIDAK_VALID"

# Shared fixture cases for the pure operations.priority-triage.v1 rule.
# This native gate uses the same source artifact and expected outputs as the Python regression.
test-registered-rules: native
	@set -eu; \
	check_case() { \
		urgency="$$1"; impact="$$2"; expected="$$3"; \
		actual="$$(printf '%s\n%s\n' "$$urgency" "$$impact" | "$(NATIVE_BIN)" examples/core/priority_triage.cuk)"; \
		if [ "$$actual" != "$$expected" ]; then \
			printf 'priority triage mismatch input=(%s,%s) expected=[%s] actual=[%s]\n' "$$urgency" "$$impact" "$$expected" "$$actual" >&2; exit 1; \
		fi; \
	}; \
	check_case 5 5 P1_SEGERA; \
	check_case 4 4 P1_SEGERA; \
	check_case 3 4 P2_DAMPAK_TINGGI; \
	check_case 1 5 P2_DAMPAK_TINGGI; \
	check_case 4 3 P3_MENDESAK; \
	check_case 5 1 P3_MENDESAK; \
	check_case 3 3 P4_RUTIN; \
	check_case 1 1 P4_RUTIN; \
	check_case 0 4 INPUT_TIDAK_VALID; \
	check_case 6 4 INPUT_TIDAK_VALID; \
	check_case 4 0 INPUT_TIDAK_VALID; \
	check_case 4 6 INPUT_TIDAK_VALID; \
	echo 'PASS: operations.priority-triage.v1 (12 native cases)'
