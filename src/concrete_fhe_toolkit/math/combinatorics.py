"""Bounded combinatorial functions evaluated through encrypted indices."""

from __future__ import annotations

import math
from typing import Optional

from concrete import fhe

from .._utils import validate_integer
from ._lookup import (
    BinaryFunction,
    UnaryFunction,
    binary_values,
    compile_binary_lookup,
    compile_unary_lookup,
    make_binary_lookup,
    make_unary_lookup,
)


def _validate_maximum(name: str, value: int) -> int:
    return validate_integer(name, value, minimum=0)


def _factorials(max_n: int) -> list[int]:
    maximum = _validate_maximum("max_n", max_n)
    values = [1]
    for value in range(1, maximum + 1):
        values.append(values[-1] * value)
    return values


def _fibonacci_values(max_n: int) -> list[int]:
    maximum = _validate_maximum("max_n", max_n)
    if maximum == 0:
        return [0]

    values = [0, 1]
    for _ in range(2, maximum + 1):
        values.append(values[-1] + values[-2])
    return values


def make_factorial(max_n: int) -> UnaryFunction:
    """Create n! for an encrypted n in [0, max_n]."""
    values = _factorials(max_n)
    return make_unary_lookup(values, 0)


def compile_factorial(
    max_n: int,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile n! for an encrypted n in [0, max_n]."""
    maximum = _validate_maximum("max_n", max_n)
    values = _factorials(maximum)
    return compile_unary_lookup(
        "compile_factorial",
        values,
        0,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_fibonacci(max_n: int) -> UnaryFunction:
    """Create the nth Fibonacci number for encrypted n in [0, max_n]."""
    values = _fibonacci_values(max_n)
    return make_unary_lookup(values, 0)


def compile_fibonacci(
    max_n: int,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile the nth Fibonacci number for encrypted n in [0, max_n]."""
    maximum = _validate_maximum("max_n", max_n)
    values = _fibonacci_values(maximum)
    return compile_unary_lookup(
        "compile_fibonacci",
        values,
        0,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_power(base: int, max_exponent: int) -> UnaryFunction:
    """Create public-base exponentiation for an encrypted exponent."""
    normalized_base = validate_integer("base", base)
    maximum = _validate_maximum("max_exponent", max_exponent)
    values = [normalized_base**exponent for exponent in range(maximum + 1)]
    return make_unary_lookup(values, 0)


def compile_power(
    base: int,
    max_exponent: int,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile public-base exponentiation for an encrypted exponent."""
    normalized_base = validate_integer("base", base)
    maximum = _validate_maximum("max_exponent", max_exponent)
    values = [normalized_base**exponent for exponent in range(maximum + 1)]
    return compile_unary_lookup(
        "compile_power",
        values,
        0,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def _comb_value(n: int, r: int, invalid_result: int) -> int:
    return math.comb(n, r) if r <= n else invalid_result


def _perm_value(n: int, r: int, invalid_result: int) -> int:
    return math.perm(n, r) if r <= n else invalid_result


def _make_n_r_lookup(
    function,
    max_n: int,
    invalid_result: int,
) -> BinaryFunction:
    maximum = _validate_maximum("max_n", max_n)
    invalid = validate_integer("invalid_result", invalid_result)
    values = binary_values(
        lambda n, r: function(n, r, invalid),
        0,
        maximum,
        0,
        maximum,
    )
    return make_binary_lookup(values, 0, 0, maximum + 1)


def make_comb(max_n: int, *, invalid_result: int = 0) -> BinaryFunction:
    """Create math.comb(n, r), returning invalid_result when r > n."""
    return _make_n_r_lookup(_comb_value, max_n, invalid_result)


def compile_comb(
    max_n: int,
    *,
    invalid_result: int = 0,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile math.comb(n, r) for encrypted n and r in [0, max_n]."""
    maximum = _validate_maximum("max_n", max_n)
    invalid = validate_integer("invalid_result", invalid_result)
    values = binary_values(
        lambda n, r: _comb_value(n, r, invalid),
        0,
        maximum,
        0,
        maximum,
    )
    return compile_binary_lookup(
        "compile_comb",
        values,
        0,
        maximum,
        0,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_perm(max_n: int, *, invalid_result: int = 0) -> BinaryFunction:
    """Create math.perm(n, r), returning invalid_result when r > n."""
    return _make_n_r_lookup(_perm_value, max_n, invalid_result)


def compile_perm(
    max_n: int,
    *,
    invalid_result: int = 0,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile math.perm(n, r) for encrypted n and r in [0, max_n]."""
    maximum = _validate_maximum("max_n", max_n)
    invalid = validate_integer("invalid_result", invalid_result)
    values = binary_values(
        lambda n, r: _perm_value(n, r, invalid),
        0,
        maximum,
        0,
        maximum,
    )
    return compile_binary_lookup(
        "compile_perm",
        values,
        0,
        maximum,
        0,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


make_combinations = make_comb
compile_combinations = compile_comb
make_permutations = make_perm
compile_permutations = compile_perm
make_exponential = make_power
compile_exponential = compile_power
