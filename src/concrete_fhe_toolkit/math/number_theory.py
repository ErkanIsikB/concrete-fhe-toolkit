"""Bounded number-theory functions for encrypted integers."""

from __future__ import annotations

import math
from typing import Optional

from concrete import fhe

from .._utils import validate_bounds, validate_integer
from ._lookup import (
    BinaryFunction,
    UnaryFunction,
    binary_values,
    compile_binary_lookup,
    compile_unary_lookup,
    make_binary_lookup,
    make_unary_lookup,
    unary_values,
)


def _binary_math_values(function, min_value: int, max_value: int) -> list[int]:
    minimum, maximum = validate_bounds(min_value, max_value)
    return binary_values(
        function,
        minimum,
        maximum,
        minimum,
        maximum,
    )


def _make_binary_math(function, min_value: int, max_value: int) -> BinaryFunction:
    minimum, maximum = validate_bounds(min_value, max_value)
    values = _binary_math_values(function, minimum, maximum)
    return make_binary_lookup(
        values,
        minimum,
        minimum,
        maximum - minimum + 1,
    )


def make_gcd(min_value: int = 0, max_value: int = 15) -> BinaryFunction:
    """Create math.gcd for two encrypted bounded integers."""
    return _make_binary_math(math.gcd, min_value, max_value)


def compile_gcd(
    min_value: int = 0,
    max_value: int = 15,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile math.gcd for two encrypted bounded integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = _binary_math_values(math.gcd, minimum, maximum)
    return compile_binary_lookup(
        "compile_gcd",
        values,
        minimum,
        maximum,
        minimum,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_lcm(min_value: int = 0, max_value: int = 15) -> BinaryFunction:
    """Create math.lcm for two encrypted bounded integers."""
    return _make_binary_math(math.lcm, min_value, max_value)


def compile_lcm(
    min_value: int = 0,
    max_value: int = 15,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile math.lcm for two encrypted bounded integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = _binary_math_values(math.lcm, minimum, maximum)
    return compile_binary_lookup(
        "compile_lcm",
        values,
        minimum,
        maximum,
        minimum,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_is_coprime(
    min_value: int = 0,
    max_value: int = 15,
) -> BinaryFunction:
    """Create a predicate returning 1 when gcd(left, right) == 1."""
    return _make_binary_math(
        lambda left, right: int(math.gcd(left, right) == 1),
        min_value,
        max_value,
    )


def compile_is_coprime(
    min_value: int = 0,
    max_value: int = 15,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile a predicate returning 1 for coprime encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = _binary_math_values(
        lambda left, right: int(math.gcd(left, right) == 1),
        minimum,
        maximum,
    )
    return compile_binary_lookup(
        "compile_is_coprime",
        values,
        minimum,
        maximum,
        minimum,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_is_divisible(
    min_numerator: int,
    max_numerator: int,
    min_denominator: int,
    max_denominator: int,
    *,
    zero_result: int = 0,
) -> BinaryFunction:
    """Create divisibility testing with explicit denominator-zero behavior."""
    zero = validate_integer("zero_result", zero_result)
    denominator_minimum, denominator_maximum = validate_bounds(
        min_denominator,
        max_denominator,
    )
    values = binary_values(
        lambda numerator, denominator: (
            zero if denominator == 0 else int(numerator % denominator == 0)
        ),
        min_numerator,
        max_numerator,
        denominator_minimum,
        denominator_maximum,
    )
    return make_binary_lookup(
        values,
        min_numerator,
        denominator_minimum,
        denominator_maximum - denominator_minimum + 1,
    )


def compile_is_divisible(
    min_numerator: int,
    max_numerator: int,
    min_denominator: int,
    max_denominator: int,
    *,
    zero_result: int = 0,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted divisibility testing."""
    zero = validate_integer("zero_result", zero_result)
    values = binary_values(
        lambda numerator, denominator: (
            zero if denominator == 0 else int(numerator % denominator == 0)
        ),
        min_numerator,
        max_numerator,
        min_denominator,
        max_denominator,
    )
    return compile_binary_lookup(
        "compile_is_divisible",
        values,
        min_numerator,
        max_numerator,
        min_denominator,
        max_denominator,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_isqrt(max_value: int) -> UnaryFunction:
    """Create math.isqrt for encrypted input in [0, max_value]."""
    maximum = validate_integer("max_value", max_value, minimum=0)
    values = unary_values(math.isqrt, 0, maximum)
    return make_unary_lookup(values, 0)


def compile_isqrt(
    max_value: int,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile math.isqrt for encrypted input in [0, max_value]."""
    maximum = validate_integer("max_value", max_value, minimum=0)
    values = unary_values(math.isqrt, 0, maximum)
    return compile_unary_lookup(
        "compile_isqrt",
        values,
        0,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_is_even(min_value: int = 0, max_value: int = 15) -> UnaryFunction:
    """Create a predicate returning 1 for even encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = unary_values(lambda value: int(value % 2 == 0), minimum, maximum)
    return make_unary_lookup(values, minimum)


def compile_is_even(
    min_value: int = 0,
    max_value: int = 15,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile a predicate returning 1 for even encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = unary_values(lambda value: int(value % 2 == 0), minimum, maximum)
    return compile_unary_lookup(
        "compile_is_even",
        values,
        minimum,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_is_odd(min_value: int = 0, max_value: int = 15) -> UnaryFunction:
    """Create a predicate returning 1 for odd encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = unary_values(lambda value: int(value % 2 != 0), minimum, maximum)
    return make_unary_lookup(values, minimum)


def compile_is_odd(
    min_value: int = 0,
    max_value: int = 15,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile a predicate returning 1 for odd encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = unary_values(lambda value: int(value % 2 != 0), minimum, maximum)
    return compile_unary_lookup(
        "compile_is_odd",
        values,
        minimum,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def _is_prime(value: int) -> int:
    if value < 2:
        return 0
    if value == 2:
        return 1
    if value % 2 == 0:
        return 0
    limit = math.isqrt(value)
    for divisor in range(3, limit + 1, 2):
        if value % divisor == 0:
            return 0
    return 1


def make_is_prime(min_value: int = 0, max_value: int = 100) -> UnaryFunction:
    """Create a predicate returning 1 for prime encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = unary_values(_is_prime, minimum, maximum)
    return make_unary_lookup(values, minimum)


def compile_is_prime(
    min_value: int = 0,
    max_value: int = 100,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile a predicate returning 1 for prime encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    values = unary_values(_is_prime, minimum, maximum)
    return compile_unary_lookup(
        "compile_is_prime",
        values,
        minimum,
        maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )
