# Start Here — PusingCuk Contributor Guide

You do not need to be a professional programmer to help. Start with a small example, documentation improvement, or reproducible bug report.

## Ways to contribute

### 1. Write a .cuk example
Add a practical example—such as a calculator, grade tracker, quiz, or budget—to `examples/name.cuk`. Check its syntax with:

```sh
python pusingcuk_new.py --check examples/name.cuk
```

### 2. Improve documentation
Help clarify or translate the docs and dictionaries. Do not change the language specification or target-support claims without evidence.

### 3. Report a bug
Include the smallest reproducing program, exact command, actual output, expected output, and version/target. Avoid reports that only say “it does not work.”

### 4. Propose vocabulary
Slang aliases are discussed through issues labeled `spec-discussion`. Do not add keywords or aliases directly without a decision consistent with `SPEC.md`.

### 5. Check the playground
Try https://rllibo833-sudo.github.io/pusingcuk/playground.html. The playground is experimental; its runtime must not be confused with the native runtime.

## Contribution workflow from a phone

1. Open https://github.com/rllibo833-sudo/pusingcuk.
2. Navigate to the relevant file or directory.
3. For code changes, use a fork/branch according to the repository contribution rules.
4. Run the available checks or provide a reproducible case for review.
5. Explain the reason for the change and state exactly what was verified.

## Do not do these without discussion

- Change language semantics or add keywords/aliases.
- Claim backend compatibility without fixtures.
- Add network dependencies to features intended to work locally.
- Manually alter reported results to make them look green.
- Treat a green CI run as proof that every target is production-ready.

## A useful bug report

- **Reproducer:** the smallest possible .cuk program.
- **Command:** the full command used.
- **Actual:** observed output or diagnostic.
- **Expected:** intended behavior.
- **Target:** reference interpreter, native C, VM, or another backend.
