# Bounds and costs

FHE circuits are compiled ahead of time. Concrete needs to know the possible
shape and value range of encrypted inputs during compilation. In this package,
those value ranges are called bounds.

Bounds are public application limits. They are not learned from encrypted data.

For example:

- if encrypted scores are percentages, use `min_value=0` and `max_value=100`;
- if encrypted balances are stored as cents and can range from `-100_000` to
  `100_000`, use those values as the bounds;
- if a fixed-point angle is stored in degrees from 0 to 90, use `min_input=0`,
  `max_input=90`, and `input_scale=1`.

Runtime inputs must stay inside the bounds used to compile the circuit.

## Common bound parameters

| Parameter | Used by | Meaning |
| --- | --- | --- |
| `min_value`, `max_value` | integer operations, comparisons, GCD/LCM, parity, primality | Inclusive integer input range |
| `min_left`, `max_left`, `min_right`, `max_right` | two-input arithmetic | Inclusive range for each side |
| `min_numerator`, `max_numerator`, `min_denominator`, `max_denominator` | modulo/division predicates | Inclusive numerator and denominator ranges |
| `min_input`, `max_input` | fixed-point and special functions | Inclusive range of the encrypted scaled integer |
| `max_n` | factorial, Fibonacci, combinations, permutations | Encrypted index range `0..max_n` |
| `scale` | floor, ceil, trunc, round | The encrypted integer `x` represents `x / scale` |
| `input_scale`, `output_scale` | special fixed-point functions | Input and output fixed-point scales |
| `numerator_width`, `denominator_width` | bit-level division | Unsigned scalar bit widths |
| `fractional_bits` | bit-level fixed-point division | Number of binary fractional output bits |

## Choosing good bounds

Use the smallest public range that is correct for your application.

Good:

```python
from concrete_fhe_toolkit import math as fhe_math

# Scores are known to be percentages.
circuit = fhe_math.is_prime(min_value=0, max_value=100)
```

Risky:

```python
from concrete_fhe_toolkit import math as fhe_math

# This may be much more expensive than needed.
circuit = fhe_math.is_prime(min_value=0, max_value=1_000_000)
```

Wider bounds are more flexible, but they often increase compile time, key size,
memory use, and execution time.

## Native arithmetic vs lookup helpers

Some helpers compile as native Concrete arithmetic:

- `compile_add`
- `compile_subtract`
- `compile_multiply`
- `compile_negate`
- `compile_square`
- comparisons such as `compile_less`

Other helpers use lookup tables over the declared domain:

- `absolute`
- `clamp`
- `modulo`
- `divmod`
- `factorial`
- `gcd`
- `lcm`
- `is_prime`
- fixed-point special functions such as `sin`, `log`, and `sqrt`

Lookup helpers are convenient and predictable, but cost grows with domain size
and output bit width.

## Large lookup guards

Some lookup helpers can become expensive very quickly. The package estimates
lookup pressure using:

- number of lookup entries;
- input index bit width;
- output bit width.

When the estimate is large enough, the helper emits `FHECostWarning`. When the
estimate is very large, it raises `LookupResourceError` unless you opt in:

```python
from concrete_fhe_toolkit import math as fhe_math

gcd = fhe_math.gcd(
    min_value=0,
    max_value=31,
    allow_large_lookup=True,
)
print(gcd.simulate(24, 18))
# 6
```

Opting in does not guarantee Concrete can find parameters for every machine and
every bound. It only says you intentionally accept the possible resource cost.

## Invalid mathematical inputs

Some functions have undefined inputs:

- `log`, `log2`, and `log10` are undefined for nonpositive values;
- `log1p` is undefined when `1 + x <= 0`;
- `sqrt` is undefined for negative values;
- modulo and division need an explicit denominator-zero policy.

If your bounds include invalid values, pass an explicit fallback:

```python
from concrete_fhe_toolkit import math as fhe_math

log2 = fhe_math.log2(
    min_input=0,
    max_input=16,
    invalid_result=-1,
)
print(log2.encrypt_run_decrypt(0))
# -1
```

For modulo/division-like helpers:

```python
from concrete_fhe_toolkit import math as fhe_math

modulo = fhe_math.modulo(
    min_numerator=0,
    max_numerator=20,
    min_denominator=0,
    max_denominator=10,
    zero_result=-1,
)
print(modulo.encrypt_run_decrypt(17, 0))
# -1
```

## Fixed-point scaling

Concrete works with integers. Fixed-point helpers represent real numbers as
scaled integers.

If `input_scale=100`, the encrypted integer `314` represents `3.14`.

If `output_scale=1000`, the output integer `841` represents `0.841`.

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

## Bit-level division bounds

`unsigned_floor_divide` and `fixed_point_divide` use bit widths instead of
lookup-table bounds.

```python
from concrete_fhe_toolkit import math as fhe_math

floor_divide = fhe_math.unsigned_floor_divide(
    numerator_width=8,
    denominator_width=8,
    zero_result=0,
)
print(floor_divide.encrypt_run_decrypt(100, 7))
# 14
```

The numerator must fit in `numerator_width` unsigned bits. The denominator must
fit in `denominator_width` unsigned bits. Division by zero returns
`zero_result`.

For fixed-point division:

```python
from concrete_fhe_toolkit import math as fhe_math

divide = fhe_math.fixed_point_divide(
    numerator_width=8,
    denominator_width=8,
    fractional_bits=8,
)
print(divide.encrypt_run_decrypt(1, 3))
# 85, representing floor((1 / 3) * 256)
```

The fixed-point result is an integer scaled by `2 ** fractional_bits`.
