# Changelog

## 0.2.0 - 2026-06-23

- Add the `concrete_fhe_toolkit.math` subpackage for Python-math-style bounded
  encrypted integer and fixed-point helpers.
- Add native arithmetic, comparison, scalar multiplication, absolute value,
  clamp, modulo, divmod, and closeness helpers.
- Add combinatorics helpers for factorial, Fibonacci, public-base powers,
  combinations, and permutations.
- Add number-theory helpers for GCD, LCM, coprime/divisibility predicates,
  integer square root, parity, and primality.
- Add fixed-point floor, ceil, truncation, rounding, rescaling, trigonometric,
  logarithmic, square-root, error-function, hyperbolic, and sigmoid helpers.
- Add friendly bounded operation objects such as `math.gcd(...)` and
  `math.sin(...)` that compile by default while exposing `.make(...)` and
  `.compile(...)` for advanced usage.
- Add bit-level LUT primitives, two's-complement helpers, unsigned restoring
  division, and fixed-point binary division helpers.
- Add dedicated documentation pages for bounds/costs, API usage, and
  pre-release testing checks.
- Add large lookup cost warnings and `allow_large_lookup=True` opt-in guards.
- Add exhaustive cleartext tests, compiler-simulation tests, and opt-in real
  encrypted math smoke tests for the new math API.

## 0.1.3 - 2026-06-18

- Promote the package development status from Alpha to Beta.

## 0.1.2 - 2026-06-16

- Add GitHub repository and example notebook links to package metadata.
- Clarify that README bounds are public application limits, not values learned
  from encrypted arrays.

## 0.1.1 - 2026-06-15

- Remove references to unrelated encryption libraries from package metadata.
- Add contributor and company acknowledgements.

## 0.1.0 - 2026-06-09

- Add bounded compare-swap, sorting, min/max, and argmin/argmax operations.
- Add safe multivariate floor division and division by an encrypted product.
- Add compiler helpers with boundary-complete inputsets.
- Add cleartext, compiler simulation, and opt-in encrypted smoke tests.
