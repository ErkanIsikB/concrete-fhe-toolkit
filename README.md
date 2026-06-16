# concrete-fhe-toolkit

`concrete-fhe-toolkit` is an unofficial collection of bounded integer helpers
for [Zama Concrete](https://docs.zama.ai/concrete). It turns common notebook
patterns into reusable, validated circuit factories and compiler helpers.

## Included operations

- Sign comparison of two encrypted integers
- Ascending or descending bitonic sort
- Minimum and maximum reductions
- Argmin and argmax with explicit first/last tie handling
- Exact floor division through a multivariate table lookup
- Exact `numerator // (left * right)` through a multivariate table lookup

All operations use integer inputs. Array sizes and value bounds are fixed when a
circuit is compiled.

## Installation

```bash
pip install concrete-fhe-toolkit
```

Concrete 2.11 supports Python 3.9 through 3.12 on Linux and macOS.

## Quick start

```python
import numpy as np

from concrete_fhe_toolkit import compile_argmin, compile_sort

values = np.array([12, 3, 7, 1, 15, 0, 4, 9], dtype=np.int64)

sort_circuit = compile_sort(size=8, min_value=0, max_value=15)
sorted_values = sort_circuit.encrypt_run_decrypt(values)

argmin_circuit = compile_argmin(size=8, min_value=0, max_value=15)
minimum_index = argmin_circuit.encrypt_run_decrypt(values)
```

The default tie behavior for `compile_argmin` and `compile_argmax` is
`tie_break="first"`, matching NumPy's convention. Use `tie_break="last"` when
the final matching index is preferred.

## Division

Direct `x // y` does not compile when both `x` and `y` are encrypted in
Concrete 2.11. This package uses `fhe.multivariate` explicitly:

```python
from concrete_fhe_toolkit import compile_floor_divide

circuit = compile_floor_divide(
    max_numerator=15,
    max_denominator=7,
    zero_result=-1,
)

assert circuit.encrypt_run_decrypt(15, 3) == 5
assert circuit.encrypt_run_decrypt(15, 0) == -1
```

Multivariate table lookups become slower and may stop compiling as the combined
input bit width grows. Keep bounds as small as the application permits.

## Factories for custom circuits

The `make_*` functions return traceable functions that can be composed inside a
larger Concrete program:

```python
from concrete import fhe
from concrete_fhe_toolkit import make_minimum

minimum_of_four = make_minimum(size=4, min_value=-8, max_value=7)
compiler = fhe.Compiler(minimum_of_four, {"x": "encrypted"})
```

When compiling manually, the inputset must include the full declared bounds.
The `compile_*` helpers do this automatically. Incomplete inputsets can produce
an undersized output type and incorrect results.

## Important limits

- Inputs must stay inside the bounds used at compilation.
- Sorting requires a power-of-two array size.
- Min/max and argmin/argmax support any positive fixed size.
- Larger bounds increase table-lookup bit width and cost.
- Concrete supports integer inputs and outputs, not arbitrary floating point.
- FHE execution is probabilistic; choose Concrete error parameters appropriate
  for the application's risk.

## Notebook audit

This package was derived from these Kaggle experiments:

- [Concrete min/max/index finding](https://www.kaggle.com/code/erkankbacak/concrete-minmax-index-finding)
- [All encrypted division operations](https://www.kaggle.com/code/erkankbacak/all-encrypted-division-operations)

The audit corrected these notebook issues:

- A `compare_swap` cell ends in `return mn, mxdef`, so its displayed source is
  not consistent with the later successful output.
- The direct encrypted division cell has no output and does not compile on
  Concrete 2.11.
- The original argmax encoding selected the last duplicate maximum. The package
  makes tie handling explicit and defaults to the first index.
- Original lookup tables and value bounds were hard-coded to unsigned 4-bit
  values. The package validates and parameterizes the bounds.

## License and Concrete terms

The package's original code is available under the MIT License. MIT permits
commercial and private use, modification, and redistribution while requiring
the copyright and license notice to be preserved.

Concrete is a separate dependency with its own BSD-3-Clause-Clear license and
patent terms. This package does not change or grant rights under Concrete's
license. Review Zama's current licensing terms before commercial use.

This project is not affiliated with or endorsed by Zama.

## Author and contributors

**Author and maintainer**

- Erkan Işık Bacak

**Contributors**

- Tolga Büyüktanır
- Didem Civelek
- Yusuf Emir Alakuş

**Organizational contributor**

- [AGRA Fintech Yazılım Çözümleri A.Ş.](https://www.agrafintech.com)
