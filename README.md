# concrete-fhe-toolkit

`concrete-fhe-toolkit` is an unofficial helper package for
[Zama Concrete](https://docs.zama.ai/concrete). It provides reusable circuit
builders for common bounded integer operations on encrypted Concrete inputs.

The package focuses on small, explicit, integer-only FHE circuits:

- compare two encrypted integers
- compare-swap two encrypted integers
- sort encrypted integer arrays
- find encrypted-array min/max values
- find encrypted-array argmin/argmax indices
- perform bounded encrypted floor division with a table lookup
- perform bounded `numerator // (left * right)`

## Installation

```bash
pip install concrete-fhe-toolkit
```

To install the latest source directly from GitHub:

```bash
pip install git+https://github.com/ErkanIsikB/concrete-fhe-toolkit.git
```

Or clone the repository and install it locally:

```bash
git clone https://github.com/ErkanIsikB/concrete-fhe-toolkit.git
cd concrete-fhe-toolkit
pip install .
```

Concrete 2.11 supports Python 3.9 through 3.12 on Linux and macOS.

## Important Concept

The `compile_*` helpers compile Concrete circuits whose inputs are declared as
encrypted. For example, `compile_sort(...)` internally compiles with
`{"x": "encrypted"}`.

The `make_*` helpers return traceable Python functions that can be composed into
larger Concrete programs. They can also run on clear Python or NumPy values for
ordinary testing, but they are designed to be compiled into encrypted-input
Concrete circuits.

All operations use integer inputs. You must choose fixed input bounds when
compiling a circuit, and runtime inputs must stay inside those bounds.

## Quick Start

```python
import numpy as np

from concrete_fhe_toolkit import compile_argmin, compile_sort

values = np.array([12, 3, 7, 1, 15, 0, 4, 9], dtype=np.int64)

sort_circuit = compile_sort(size=8, min_value=0, max_value=15)
print(sort_circuit.encrypt_run_decrypt(values))
# [ 0  1  3  4  7  9 12 15]

argmin_circuit = compile_argmin(size=8, min_value=0, max_value=15)
print(argmin_circuit.encrypt_run_decrypt(values))
# 5
```

## Public API

Scalar arithmetic:

- `sign(x, y)`
- `compile_sign(min_value=-15, max_value=15, configuration=None)`
- `make_floor_divide(zero_result=0)`
- `compile_floor_divide(max_numerator, max_denominator, zero_result=0, configuration=None)`
- `make_floor_divide_by_product(zero_result=0)`
- `compile_floor_divide_by_product(max_numerator, max_left, max_right, zero_result=0, configuration=None)`

Array operations:

- `make_compare_swap(min_value=0, max_value=15)`
- `compile_compare_swap(min_value=0, max_value=15, configuration=None)`
- `make_sort(size, min_value=0, max_value=15, descending=False)`
- `compile_sort(size, min_value=0, max_value=15, descending=False, configuration=None)`
- `make_minimum(size, min_value=0, max_value=15)`
- `compile_minimum(size, min_value=0, max_value=15, configuration=None)`
- `make_maximum(size, min_value=0, max_value=15)`
- `compile_maximum(size, min_value=0, max_value=15, configuration=None)`
- `make_argmin(size, min_value=0, max_value=15, tie_break="first")`
- `compile_argmin(size, min_value=0, max_value=15, tie_break="first", configuration=None)`
- `make_argmax(size, min_value=0, max_value=15, tie_break="first")`
- `compile_argmax(size, min_value=0, max_value=15, tie_break="first", configuration=None)`

## Examples

### Sign Comparison

`compile_sign` returns `1` when `x > y`, `0` when `x == y`, and `-1` when
`x < y`.

```python
from concrete_fhe_toolkit import compile_sign

circuit = compile_sign(min_value=-20, max_value=20)

print(circuit.encrypt_run_decrypt(15, 3))
# 1

print(circuit.encrypt_run_decrypt(3, 15))
# -1

print(circuit.encrypt_run_decrypt(7, 7))
# 0
```

### Compare-Swap

`compile_compare_swap` returns two values in ascending order.

```python
from concrete_fhe_toolkit import compile_compare_swap

circuit = compile_compare_swap(min_value=0, max_value=15)

print(circuit.encrypt_run_decrypt(12, 3))
# (3, 12)
```

### Sort

`compile_sort` sorts a fixed-size encrypted array. The size must be a power of
two.

```python
import numpy as np

from concrete_fhe_toolkit import compile_sort

values = np.array([12, 3, 7, 1, 15, 0, 4, 9], dtype=np.int64)

ascending = compile_sort(size=8, min_value=0, max_value=15)
print(ascending.encrypt_run_decrypt(values))
# [ 0  1  3  4  7  9 12 15]

descending = compile_sort(size=8, min_value=0, max_value=15, descending=True)
print(descending.encrypt_run_decrypt(values))
# [15 12  9  7  4  3  1  0]
```

### Minimum and Maximum

`compile_minimum` and `compile_maximum` return the smallest or largest value in
a fixed-size encrypted array.

```python
import numpy as np

from concrete_fhe_toolkit import compile_maximum, compile_minimum

values = np.array([12, 5, 7, 2, 15, 9, 4, 14], dtype=np.int64)

minimum = compile_minimum(size=8, min_value=0, max_value=15)
print(minimum.encrypt_run_decrypt(values))
# 2

maximum = compile_maximum(size=8, min_value=0, max_value=15)
print(maximum.encrypt_run_decrypt(values))
# 15
```

### Argmin and Argmax

`compile_argmin` and `compile_argmax` return the index of the smallest or
largest value. By default, ties return the first matching index.

```python
import numpy as np

from concrete_fhe_toolkit import compile_argmax, compile_argmin

values = np.array([12, 5, 7, 1, 15, 9, 4, 14], dtype=np.int64)

argmin = compile_argmin(size=8, min_value=0, max_value=15)
print(argmin.encrypt_run_decrypt(values))
# 3

argmax = compile_argmax(size=8, min_value=0, max_value=15)
print(argmax.encrypt_run_decrypt(values))
# 4
```

Tie handling is explicit:

```python
import numpy as np

from concrete_fhe_toolkit import compile_argmin

values = np.array([4, 1, 1, 3], dtype=np.int64)

first = compile_argmin(size=4, min_value=0, max_value=4, tie_break="first")
print(first.encrypt_run_decrypt(values))
# 1

last = compile_argmin(size=4, min_value=0, max_value=4, tie_break="last")
print(last.encrypt_run_decrypt(values))
# 2
```

### Floor Division

Direct `x // y` does not compile when both values are encrypted in Concrete
2.11. This package implements bounded floor division with
`fhe.multivariate`.

```python
from concrete_fhe_toolkit import compile_floor_divide

circuit = compile_floor_divide(
    max_numerator=15,
    max_denominator=7,
    zero_result=-1,
)

print(circuit.encrypt_run_decrypt(15, 3))
# 5

print(circuit.encrypt_run_decrypt(15, 0))
# -1
```

`zero_result` is returned when the encrypted denominator is zero.

### Division by an Encrypted Product

`compile_floor_divide_by_product` computes
`numerator // (left * right)`.

```python
from concrete_fhe_toolkit import compile_floor_divide_by_product

circuit = compile_floor_divide_by_product(
    max_numerator=20,
    max_left=5,
    max_right=5,
    zero_result=-1,
)

print(circuit.encrypt_run_decrypt(20, 2, 5))
# 2

print(circuit.encrypt_run_decrypt(20, 0, 5))
# -1
```

### Composing `make_*` Helpers

Use `make_*` helpers when you want to build a larger Concrete function yourself.
When compiling manually, your inputset must cover the bounds you declared.

```python
import numpy as np
from concrete import fhe

from concrete_fhe_toolkit import make_minimum

minimum_of_four = make_minimum(size=4, min_value=0, max_value=15)
compiler = fhe.Compiler(minimum_of_four, {"x": "encrypted"})

inputset = [
    np.array([0, 0, 0, 0], dtype=np.int64),
    np.array([15, 15, 15, 15], dtype=np.int64),
    np.array([0, 15, 0, 15], dtype=np.int64),
    np.array([15, 0, 15, 0], dtype=np.int64),
]

circuit = compiler.compile(inputset)
print(circuit.encrypt_run_decrypt(np.array([8, 3, 12, 5], dtype=np.int64)))
# 3
```

For most use cases, prefer the `compile_*` helpers because they generate
boundary-aware inputsets automatically.

## Bounds and Limitations

- Inputs must stay inside the bounds used at compilation.
- Sorting requires a power-of-two array size.
- Min/max and argmin/argmax support any positive fixed size.
- Division helpers currently support nonnegative bounded inputs.
- Larger bounds increase table-lookup bit width and cost.
- Concrete supports integer inputs and outputs, not arbitrary floating point.
- FHE execution is probabilistic; choose Concrete error parameters appropriate
  for the application's risk.

## Notebook Examples

This package was derived from these Kaggle experiments:

- [Concrete min/max/index finding](https://www.kaggle.com/code/erkankbacak/concrete-minmax-index-finding)
- [All encrypted division operations](https://www.kaggle.com/code/erkankbacak/all-encrypted-division-operations)

Additional usage notebook:

- [concrete-fhe-toolkit-test](https://www.kaggle.com/code/erkankbacak/concrete-fhe-toolkit-test)

## License and Concrete Terms

The package's original code is available under the MIT License. MIT permits
commercial and private use, modification, and redistribution while requiring
the copyright and license notice to be preserved.

Concrete is a separate dependency with its own BSD-3-Clause-Clear license and
patent terms. This package does not change or grant rights under Concrete's
license. Review Zama's current licensing terms before commercial use.

This project is not affiliated with or endorsed by Zama.

## Author and Contributors

**Author and maintainer**

- Erkan Işık Bacak

**Contributors**

- Tolga Büyüktanır
- Didem Civelek
- Yusuf Emir Alakuş

**Organizational contributor**

- [AGRA Fintech Yazılım Çözümleri A.Ş.](https://www.agrafintech.com)
