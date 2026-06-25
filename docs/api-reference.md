# API reference

This page describes the user-facing functions in `concrete-fhe-toolkit`.

For most functions there are three layers:

- friendly operation, for example `fhe_math.gcd(...)`, which compiles by
  default;
- explicit compiler, for example `fhe_math.compile_gcd(...)`;
- composable builder, for example `fhe_math.make_gcd(...)`.

Use the friendly operation or `compile_*` for normal use. Use `make_*` when
you are manually composing a larger Concrete function.

## Root package functions

Import from the package root:

```python
from concrete_fhe_toolkit import compile_sort
```

| Function | What it does | Main bounds |
| --- | --- | --- |
| `sign(x, y)` | Clear/traceable comparison returning `1`, `0`, or `-1` | Values must fit the circuit bounds when compiled |
| `compile_sign(min_value=-15, max_value=15)` | Compiles encrypted sign comparison | `min_value..max_value` for both inputs |
| `make_compare_swap(min_value=0, max_value=15)` | Builds a traceable two-value ascending sort step | Scalar range |
| `compile_compare_swap(min_value=0, max_value=15)` | Compiles encrypted compare-swap | Scalar range |
| `make_sort(size, min_value=0, max_value=15, descending=False)` | Builds a fixed-size sorting network | Array size and scalar range |
| `compile_sort(size, min_value=0, max_value=15, descending=False)` | Compiles encrypted array sort | Array size and scalar range |
| `make_minimum(size, min_value=0, max_value=15)` | Builds encrypted-array minimum | Array size and scalar range |
| `compile_minimum(size, min_value=0, max_value=15)` | Compiles encrypted-array minimum | Array size and scalar range |
| `make_maximum(size, min_value=0, max_value=15)` | Builds encrypted-array maximum | Array size and scalar range |
| `compile_maximum(size, min_value=0, max_value=15)` | Compiles encrypted-array maximum | Array size and scalar range |
| `make_argmin(size, min_value=0, max_value=15, tie_break="first")` | Builds index of minimum value | Array size and scalar range |
| `compile_argmin(size, min_value=0, max_value=15, tie_break="first")` | Compiles encrypted argmin | Array size and scalar range |
| `make_argmax(size, min_value=0, max_value=15, tie_break="first")` | Builds index of maximum value | Array size and scalar range |
| `compile_argmax(size, min_value=0, max_value=15, tie_break="first")` | Compiles encrypted argmax | Array size and scalar range |
| `make_floor_divide(zero_result=0)` | Builds bounded floor division using Concrete multivariate lookup | Inputset supplied by caller |
| `compile_floor_divide(max_numerator, max_denominator, zero_result=0)` | Compiles `numerator // denominator` for nonnegative inputs | `0..max_numerator`, `0..max_denominator` |
| `make_floor_divide_by_product(zero_result=0)` | Builds `numerator // (left * right)` | Inputset supplied by caller |
| `compile_floor_divide_by_product(max_numerator, max_left, max_right, zero_result=0)` | Compiles division by encrypted product | Nonnegative maxima |

Example:

```python
import numpy as np
from concrete_fhe_toolkit import compile_sort

values = np.array([12, 3, 7, 1], dtype=np.int64)
sort = compile_sort(size=4, min_value=0, max_value=15)
print(sort.encrypt_run_decrypt(values))
# [ 1  3  7 12]
```

## Math operation objects

Import the math subpackage:

```python
from concrete_fhe_toolkit import math as fhe_math
```

Each operation object supports:

```python
from concrete_fhe_toolkit import math as fhe_math

circuit = fhe_math.gcd(min_value=0, max_value=8)
circuit = fhe_math.gcd.compile(min_value=0, max_value=8)
function = fhe_math.gcd.make(min_value=0, max_value=8)
```

The friendly operation objects are:

| Operation | What it computes |
| --- | --- |
| `absolute` / `abs` | Absolute value |
| `clamp` | Clamp value into `[min_value, max_value]` |
| `modulo` | `numerator % denominator` with denominator-zero fallback |
| `divmod` | `(numerator // denominator, numerator % denominator)` with denominator-zero fallbacks |
| `is_close` | Integer absolute-tolerance predicate |
| `factorial` | `n!` for encrypted `n` |
| `fibonacci` | nth Fibonacci number for encrypted `n` |
| `power` | Public-base exponentiation with encrypted exponent |
| `comb` / `combinations` | `math.comb(n, r)` with invalid fallback for `r > n` |
| `perm` / `permutations` | `math.perm(n, r)` with invalid fallback for `r > n` |
| `gcd` | Greatest common divisor |
| `lcm` | Least common multiple |
| `is_coprime` | `gcd(left, right) == 1` |
| `is_divisible` | `numerator % denominator == 0` with denominator-zero fallback |
| `isqrt` | Integer square root |
| `is_even` | Even predicate |
| `is_odd` | Odd predicate |
| `is_prime` | Primality predicate |
| `floor` | Fixed-point floor |
| `ceil` | Fixed-point ceil |
| `trunc` | Fixed-point truncation toward zero |
| `round` | Fixed-point rounding using Python's ties-to-even rule |
| `floor_ceil` | Pair `(floor(x), ceil(x))` |
| `rescale` | Convert one fixed-point scale to another |
| `sin`, `cos`, `tan` | Fixed-point trigonometric approximations |
| `exp`, `expm1` | Fixed-point exponential functions |
| `log`, `log1p`, `log2`, `log10` | Fixed-point logarithms with invalid-domain policy |
| `sqrt` | Fixed-point square root with invalid-domain policy |
| `erf`, `erfc` | Fixed-point error functions |
| `tanh`, `sinh`, `cosh` | Fixed-point hyperbolic functions |
| `sigmoid` | Fixed-point logistic sigmoid |
| `unsigned_floor_divide` | Bit-level unsigned integer division |
| `fixed_point_divide` | Bit-level unsigned fixed-point division |

## Basic integer operations

These simple functions are traceable and can be used inside manual Concrete
programs:

| Function | Computes |
| --- | --- |
| `add(left, right)` | `left + right` |
| `subtract(left, right)` / `compile_sub` alias | `left - right` |
| `multiply(left, right)` | `left * right` |
| `negate(value)` | `-value` |
| `square(value)` | `value * value` |
| `equal(left, right)` | `left == right` as `0` or `1` |
| `not_equal(left, right)` | `left != right` as `0` or `1` |
| `less(left, right)` | `left < right` as `0` or `1` |
| `less_equal(left, right)` | `left <= right` as `0` or `1` |
| `greater(left, right)` | `left > right` as `0` or `1` |
| `greater_equal(left, right)` | `left >= right` as `0` or `1` |
| `make_scalar_multiply(multiplier)` | Returns a traceable `value * multiplier` function |

Compiler helpers:

- `compile_add(min_left=0, max_left=15, min_right=0, max_right=15)`
- `compile_subtract(min_left=0, max_left=15, min_right=0, max_right=15)`
- `compile_multiply(min_left=0, max_left=15, min_right=0, max_right=15)`
- `compile_negate(min_value=-15, max_value=15)`
- `compile_square(min_value=-15, max_value=15)`
- `compile_scalar_multiply(min_value, max_value, multiplier)`
- `compile_equal(min_value=-15, max_value=15)`
- `compile_not_equal(min_value=-15, max_value=15)`
- `compile_less(min_value=-15, max_value=15)`
- `compile_less_equal(min_value=-15, max_value=15)`
- `compile_greater(min_value=-15, max_value=15)`
- `compile_greater_equal(min_value=-15, max_value=15)`
- `compile_is_close(min_value, max_value, absolute_tolerance=...)`

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

add = fhe_math.compile_add(min_left=-5, max_left=5, min_right=-5, max_right=5)
print(add.encrypt_run_decrypt(-3, 5))
# 2
```

## Bounded lookup integer helpers

### Absolute value

```python
from concrete_fhe_toolkit import math as fhe_math

absolute = fhe_math.absolute(min_value=-8, max_value=8)
print(absolute.encrypt_run_decrypt(-7))
# 7
```

Aliases:

- `absolute`
- `abs`
- `make_absolute`
- `make_abs`
- `compile_absolute`
- `compile_abs`

### Clamp

```python
from concrete_fhe_toolkit import math as fhe_math

clamp = fhe_math.clamp(
    min_input=-10,
    max_input=10,
    min_value=-3,
    max_value=4,
)
print(clamp.encrypt_run_decrypt(8))
# 4
```

### Modulo

```python
from concrete_fhe_toolkit import math as fhe_math

modulo = fhe_math.modulo(
    min_numerator=0,
    max_numerator=20,
    min_denominator=0,
    max_denominator=10,
    zero_result=-1,
)
print(modulo.encrypt_run_decrypt(17, 5))
# 2
```

### Divmod

```python
from concrete_fhe_toolkit import math as fhe_math

divmod_circuit = fhe_math.divmod(
    min_numerator=0,
    max_numerator=20,
    min_denominator=0,
    max_denominator=10,
    zero_quotient=-1,
    zero_remainder=-1,
)
print(divmod_circuit.encrypt_run_decrypt(17, 5))
# (3, 2)
```

### Is close

```python
from concrete_fhe_toolkit import math as fhe_math

is_close = fhe_math.is_close(min_value=-10, max_value=10, absolute_tolerance=2)
print(is_close.encrypt_run_decrypt(7, 9))
# 1
```

## Combinatorics

| Operation | Bounds | Invalid policy |
| --- | --- | --- |
| `factorial(max_n)` | encrypted `n` in `0..max_n` | no invalid input inside bounds |
| `fibonacci(max_n)` | encrypted `n` in `0..max_n` | no invalid input inside bounds |
| `power(base, max_exponent)` | encrypted exponent in `0..max_exponent` | base is public |
| `comb(max_n, invalid_result=0)` | encrypted `n` and `r` in `0..max_n` | returns `invalid_result` when `r > n` |
| `perm(max_n, invalid_result=0)` | encrypted `n` and `r` in `0..max_n` | returns `invalid_result` when `r > n` |

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

factorial = fhe_math.factorial(max_n=7)
print(factorial.encrypt_run_decrypt(5))
# 120

comb = fhe_math.comb(max_n=6, invalid_result=0)
print(comb.encrypt_run_decrypt(6, 3))
# 20
```

Aliases:

- `combinations` is an alias of `comb`
- `permutations` is an alias of `perm`
- `compile_exponential` / `make_exponential` are aliases for public-base
  exponentiation helpers

## Number theory

| Operation | Computes | Bounds |
| --- | --- | --- |
| `gcd(min_value=0, max_value=15)` | `math.gcd(left, right)` | both inputs in `min_value..max_value` |
| `lcm(min_value=0, max_value=15)` | `math.lcm(left, right)` | both inputs in `min_value..max_value` |
| `is_coprime(min_value=0, max_value=15)` | `gcd(left, right) == 1` | both inputs in `min_value..max_value` |
| `is_divisible(min_numerator, max_numerator, min_denominator, max_denominator, zero_result=0)` | divisibility predicate | numerator and denominator ranges |
| `isqrt(max_value)` | `math.isqrt(value)` | input in `0..max_value` |
| `is_even(min_value=0, max_value=15)` | even predicate | input range |
| `is_odd(min_value=0, max_value=15)` | odd predicate | input range |
| `is_prime(min_value=0, max_value=100)` | primality predicate | input range |

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

gcd = fhe_math.gcd(min_value=0, max_value=8)
print(gcd.encrypt_run_decrypt(6, 4))
# 2

prime = fhe_math.is_prime(min_value=0, max_value=40)
print(prime.encrypt_run_decrypt(37))
# 1
```

## Fixed-point helpers

These helpers interpret an encrypted integer as a scaled value.

| Operation | Computes |
| --- | --- |
| `floor(min_input, max_input, scale=10)` | `floor(value / scale)` |
| `ceil(min_input, max_input, scale=10)` | `ceil(value / scale)` |
| `trunc(min_input, max_input, scale=10)` | truncation toward zero |
| `round(min_input, max_input, scale=10)` | Python-style rounding |
| `floor_ceil(min_input, max_input, scale=10)` | `(floor(value / scale), ceil(value / scale))` |
| `rescale(min_input, max_input, input_scale, output_scale, rounding="nearest")` | convert between fixed-point scales |

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

trunc = fhe_math.trunc(min_input=-50, max_input=50, scale=10)
print(trunc.encrypt_run_decrypt(-37))
# -3

rescale = fhe_math.rescale(
    min_input=0,
    max_input=100,
    input_scale=10,
    output_scale=100,
)
print(rescale.encrypt_run_decrypt(15))
# 150, representing 1.50
```

Rounding modes for `rescale`:

- `"nearest"`
- `"floor"`
- `"ceil"`
- `"trunc"`

## Special fixed-point functions

These helpers approximate real-valued math functions by lookup over bounded
scaled integers. Outputs are integers scaled by `output_scale`.

| Operation | Default input interpretation | Notes |
| --- | --- | --- |
| `sin`, `cos` | radians scaled by 100, or degrees with `angle_unit="degrees"` | Use `input_scale` and `output_scale` |
| `tan` | radians scaled by 100, or degrees with `angle_unit="degrees"` | Avoid bounds near singularities |
| `exp`, `expm1` | input scaled by 10 | Output scaled by `output_scale` |
| `log`, `log1p`, `log2`, `log10` | scaled or integer inputs depending on helper defaults | Use `invalid_result` if bounds include invalid values |
| `sqrt` | input scaled by 100 by default | Use `invalid_result` if bounds include negatives |
| `erf`, `erfc` | input scaled by 10 | Output scaled by `output_scale` |
| `tanh`, `sinh`, `cosh` | input scaled by 10 | Output scaled by `output_scale` |
| `sigmoid` | input scaled by 10 | Output scaled by `output_scale` |

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

sin = fhe_math.sin(
    min_input=0,
    max_input=90,
    input_scale=1,
    output_scale=1000,
    angle_unit="degrees",
)
print(sin.encrypt_run_decrypt(30))
# 500, representing 0.500
```

Invalid-domain example:

```python
from concrete_fhe_toolkit import math as fhe_math

sqrt = fhe_math.sqrt(
    min_input=-10,
    max_input=100,
    input_scale=10,
    output_scale=100,
    invalid_result=-1,
)
print(sqrt.encrypt_run_decrypt(-3))
# -1
```

## Bit-level helpers

Bit lists are little-endian: index 0 is the least significant bit.

| Function | Computes |
| --- | --- |
| `bit_not(bit)` / `bnot` | bit NOT |
| `bit_and(left, right)` / `band` | bit AND |
| `bit_or(left, right)` / `bor` | bit OR |
| `bit_xor(left, right)` / `bxor` | bit XOR |
| `bit_select(control, when_one, when_zero)` / `bsel` | choose one bit based on control |
| `full_adder_bit(left, right, carry_in)` / `fadd_bit` | one full-adder stage |
| `full_subtractor_bit(left, right, borrow_in)` / `fsub_bit` | one full-subtractor stage |
| `bit_or_many(bits)` | OR-reduce bit iterable |
| `integer_to_bits(value, width)` | traceable unsigned integer-to-bits conversion |
| `bits_to_unsigned(bits)` | little-endian bits to unsigned integer |
| `unsigned_to_bits(value, width)` | clear unsigned integer to bits |
| `twos_complement_bits(value, width)` | clear signed integer to two's-complement bits |
| `sign_magnitude_to_twos_complement_bits(magnitude_bits, sign_bit, width=None)` | sign-magnitude to two's-complement bits |
| `twos_complement_add_bits(left_bits, right_bits, width)` | two's-complement addition modulo `2 ** width` |
| `twos_complement_multiply_by_constant_bits(signed_bits, multiplier, output_width)` | multiply signed bits by a nonnegative public constant |

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

print(fhe_math.unsigned_to_bits(13, 5))
# (1, 0, 1, 1, 0)

print(fhe_math.bits_to_unsigned((1, 0, 1, 1)))
# 13
```

## Bit-level division

These helpers use a restoring binary division circuit. They support unsigned
scalar inputs that fit in the declared bit widths.

| Operation | Computes | Output scale |
| --- | --- | --- |
| `unsigned_floor_divide(numerator_width, denominator_width, quotient_width=None, zero_result=0)` | `numerator // denominator` | integer |
| `fixed_point_divide(numerator_width, denominator_width, fractional_bits, quotient_width=None, zero_result=0)` | `floor((numerator << fractional_bits) / denominator)` | `2 ** fractional_bits` |
| `unsigned_divide_bits(numerator_bits, denominator_bits, quotient_width=None, zero_result=0)` | quotient bits | bits |
| `fixed_point_divide_bits(numerator_bits, denominator_bits, fractional_bits, quotient_width=None, zero_result=0)` | fixed-point quotient bits | bits |

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

floor_divide = fhe_math.unsigned_floor_divide(
    numerator_width=8,
    denominator_width=8,
    zero_result=0,
)
print(floor_divide.encrypt_run_decrypt(100, 7))
# 14

fixed_divide = fhe_math.fixed_point_divide(
    numerator_width=8,
    denominator_width=8,
    fractional_bits=8,
)
print(fixed_divide.encrypt_run_decrypt(1, 3))
# 85, representing floor((1 / 3) * 256)
```

## Resource helpers

| Name | Purpose |
| --- | --- |
| `estimate_lookup_cost(domain_size, min_output, max_output)` | Static lookup pressure estimate |
| `LookupCost` | Dataclass returned by `estimate_lookup_cost` |
| `FHECostWarning` | Warning for large lookup estimates |
| `LookupResourceError` | Error requiring `allow_large_lookup=True` for very large estimates |

Example:

```python
from concrete_fhe_toolkit import math as fhe_math

cost = fhe_math.estimate_lookup_cost(
    domain_size=32,
    min_output=0,
    max_output=1_000_000,
)
print(cost.level)
```
