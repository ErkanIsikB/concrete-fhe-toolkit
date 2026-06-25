# Maintainer testing and release checks

This page records the maintainer checks to run before publishing a release.
End users do not need these commands to use the package.

Publishing to GitHub or PyPI should happen only after explicit approval.

The examples below use `python`. If you work inside a virtual environment,
replace it with that environment's interpreter.

## Normal test suite

```bash
python -m pytest -q
```

This runs cleartext tests and compiler/simulation tests. Expensive encrypted
smoke tests are skipped unless their environment variables are set.

## Real encrypted smoke tests

Run the package's original encrypted smoke test:

```bash
RUN_FHE_TESTS=1 python -m pytest -q tests/test_fhe_smoke.py
```

Run the math encrypted smoke test:

```bash
RUN_FHE_MATH_TESTS=1 python -m pytest -q tests/test_math_fhe_smoke.py
```

Run notebook-sized encrypted regressions:

```bash
RUN_FHE_NOTEBOOK_TESTS=1 python -m pytest -q tests/test_notebook_regressions.py
```

## Build artifacts

```bash
python -m build
```

Expected artifacts:

- `dist/concrete_fhe_toolkit-0.2.0-py3-none-any.whl`
- `dist/concrete_fhe_toolkit-0.2.0.tar.gz`

## Validate package metadata

```bash
python -m twine check dist/concrete_fhe_toolkit-0.2.0*
```

Both wheel and source distribution should pass.

## Fresh install sanity

Use Python 3.9 through 3.12 because Concrete 2.11 does not support newer
Python versions.

```bash
python -m venv /tmp/cfhe020-check
/tmp/cfhe020-check/bin/python -m pip install dist/concrete_fhe_toolkit-0.2.0-py3-none-any.whl
```

Then run a small installed-artifact sanity check:

```bash
/tmp/cfhe020-check/bin/python - <<'PY'
from concrete_fhe_toolkit import __version__, math as fhe_math

print(__version__)
print(len(fhe_math.__all__))
print(int(fhe_math.gcd(0, 8).simulate(6, 4)))
print(int(fhe_math.gcd.make(0, 8)(6, 4)))
print(int(fhe_math.unsigned_floor_divide(4, 3, zero_result=15).simulate(13, 3)))
print(int(fhe_math.fixed_point_divide(4, 3, fractional_bits=3).simulate(1, 3)))
PY
```

## What the tests cover

The suite checks:

- root arithmetic and array helpers;
- cleartext behavior of math helpers;
- exhaustive small-domain checks for bounded lookup helpers;
- compiler/simulation behavior for representative bounds;
- division-by-zero fallback behavior;
- fixed-point scaling behavior;
- large lookup warnings and opt-in guards;
- bit-level LUT primitives;
- unsigned and fixed-point binary division over small exhaustive domains;
- real encrypted execution for representative functions.

No test suite can exhaust every possible bound because users can choose
arbitrarily large domains. The package tests correctness over representative
bounded domains and separately tests resource guards for larger lookups.
