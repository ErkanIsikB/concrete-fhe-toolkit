# concrete-fhe-toolkit documentation

This documentation explains how to use `concrete-fhe-toolkit` as a bounded
math helper library for Zama Concrete.

Start here if you are new to the package:

- [Bounds and costs](bounds-and-costs.md): how to choose bounds, why bounds are
  public, and how lookup cost guards work.
- [API reference](api-reference.md): what each user-facing function family does
  and how to call it.
- [Maintainer testing and release checks](testing-and-release.md): verification
  commands used before publishing.

## The three usage levels

Most users should start with the friendly operation names in
`concrete_fhe_toolkit.math`.

```python
from concrete_fhe_toolkit import math as fhe_math

circuit = fhe_math.gcd(min_value=0, max_value=8)
print(circuit.encrypt_run_decrypt(6, 4))
# 2
```

Each friendly operation compiles by default, and also exposes explicit builders:

```python
from concrete_fhe_toolkit import math as fhe_math

compiled = fhe_math.gcd.compile(min_value=0, max_value=8)
builder = fhe_math.gcd.make(min_value=0, max_value=8)
```

The older explicit names remain available:

```python
from concrete_fhe_toolkit import math as fhe_math

compiled = fhe_math.compile_gcd(min_value=0, max_value=8)
builder = fhe_math.make_gcd(min_value=0, max_value=8)
```

Use the friendly operation name for one-operation circuits. Use `.make(...)`
only when composing several operations into one larger Concrete circuit.

## What this package is, and is not

This package is not a replacement for Concrete. It is a layer of reusable,
bounded circuit builders for common encrypted integer and fixed-point patterns.

The package focuses on:

- scalar integer arithmetic and comparisons;
- array sorting, min/max, argmin/argmax;
- bounded integer math such as absolute value, GCD, LCM, factorial,
  combinations, primality, and integer square root;
- scaled-integer fixed-point helpers such as floor, ceil, round, rescale,
  `sin`, `cos`, `log`, `sqrt`, `erf`, `tanh`, and sigmoid;
- bit-level primitives and unsigned binary division for advanced circuits.

Concrete still controls compilation, parameter selection, encryption,
evaluation, and decryption. Inputs and outputs are integers. Floating-point
values are represented as scaled integers.

## Quick examples

### Integer GCD

```python
from concrete_fhe_toolkit import math as fhe_math

gcd = fhe_math.gcd(min_value=0, max_value=8)
print(gcd.encrypt_run_decrypt(6, 4))
# 2
```

### Fixed-point sine

```python
from concrete_fhe_toolkit import math as fhe_math

sin = fhe_math.sin(
    min_input=0,
    max_input=90,
    input_scale=1,
    output_scale=100,
    angle_unit="degrees",
)
print(sin.encrypt_run_decrypt(30))
# 50, representing 0.50
```

### Composing operations manually

```python
from concrete import fhe
from concrete_fhe_toolkit import math as fhe_math

absolute = fhe_math.absolute.make(-8, 8)
gcd = fhe_math.gcd.make(0, 8)

def program(x, y):
    return gcd(absolute(x), y)

compiler = fhe.Compiler(program, {"x": "encrypted", "y": "encrypted"})
circuit = compiler.compile([(x, y) for x in range(-8, 9) for y in range(9)])
print(circuit.encrypt_run_decrypt(-6, 4))
# 2
```

### Bit-level fixed-point division

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
