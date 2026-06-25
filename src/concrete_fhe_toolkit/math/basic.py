"""Basic bounded scalar operations for encrypted integers."""

from __future__ import annotations

from typing import Any, Callable, Optional

from concrete import fhe

from .._utils import compile_function, validate_bounds, validate_integer
from ._lookup import (
    BinaryFunction,
    binary_values,
    check_lookup_cost,
    compile_binary_lookup,
    compile_unary_lookup,
    make_binary_lookup,
    make_unary_lookup,
    unary_values,
)

UnaryFunction = Callable[[Any], Any]


def add(left: Any, right: Any) -> Any:
    """Return left + right."""
    return left + right


def subtract(left: Any, right: Any) -> Any:
    """Return left - right."""
    return left - right


def multiply(left: Any, right: Any) -> Any:
    """Return left * right."""
    return left * right


def negate(value: Any) -> Any:
    """Return -value."""
    return -value


def square(value: Any) -> Any:
    """Return value squared."""
    return value * value


def equal(left: Any, right: Any) -> Any:
    """Return 1 when left equals right, otherwise 0."""
    return left == right


def not_equal(left: Any, right: Any) -> Any:
    """Return 1 when left differs from right, otherwise 0."""
    return left != right


def less(left: Any, right: Any) -> Any:
    """Return 1 when left is less than right, otherwise 0."""
    return left < right


def less_equal(left: Any, right: Any) -> Any:
    """Return 1 when left is less than or equal to right."""
    return left <= right


def greater(left: Any, right: Any) -> Any:
    """Return 1 when left is greater than right, otherwise 0."""
    return left > right


def greater_equal(left: Any, right: Any) -> Any:
    """Return 1 when left is greater than or equal to right."""
    return left >= right


def make_scalar_multiply(multiplier: int) -> UnaryFunction:
    """Create multiplication by a public integer constant."""
    normalized = validate_integer("multiplier", multiplier)

    def scalar_multiply(value: Any) -> Any:
        return value * normalized

    return scalar_multiply


def make_is_close(absolute_tolerance: int) -> BinaryFunction:
    """Create an integer closeness predicate using a public tolerance."""
    tolerance = validate_integer(
        "absolute_tolerance",
        absolute_tolerance,
        minimum=0,
    )

    def is_close(left: Any, right: Any) -> Any:
        difference = left - right
        return (difference >= -tolerance) * (difference <= tolerance)

    return is_close


def _binary_inputset(
    min_left: int,
    max_left: int,
    min_right: int,
    max_right: int,
) -> list[tuple[int, int]]:
    left_minimum, left_maximum = validate_bounds(min_left, max_left)
    right_minimum, right_maximum = validate_bounds(min_right, max_right)
    return [
        (left_minimum, right_minimum),
        (left_minimum, right_maximum),
        (left_maximum, right_minimum),
        (left_maximum, right_maximum),
    ]


def _compile_binary_native(
    function: BinaryFunction,
    min_left: int,
    max_left: int,
    min_right: int,
    max_right: int,
    configuration: Optional[fhe.Configuration],
) -> fhe.Circuit:
    inputset = _binary_inputset(min_left, max_left, min_right, max_right)
    return compile_function(
        function,
        {"left": "encrypted", "right": "encrypted"},
        inputset,
        configuration,
    )


def compile_add(
    min_left: int = 0,
    max_left: int = 15,
    min_right: int = 0,
    max_right: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted integer addition over inclusive bounds."""
    return _compile_binary_native(
        add,
        min_left,
        max_left,
        min_right,
        max_right,
        configuration,
    )


def compile_subtract(
    min_left: int = 0,
    max_left: int = 15,
    min_right: int = 0,
    max_right: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted integer subtraction over inclusive bounds."""
    return _compile_binary_native(
        subtract,
        min_left,
        max_left,
        min_right,
        max_right,
        configuration,
    )


def compile_multiply(
    min_left: int = 0,
    max_left: int = 15,
    min_right: int = 0,
    max_right: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted integer multiplication over inclusive bounds."""
    return _compile_binary_native(
        multiply,
        min_left,
        max_left,
        min_right,
        max_right,
        configuration,
    )


def compile_negate(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted integer negation."""
    minimum, maximum = validate_bounds(min_value, max_value)
    return compile_function(
        negate,
        {"value": "encrypted"},
        [minimum, maximum],
        configuration,
    )


def compile_square(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted integer squaring."""
    minimum, maximum = validate_bounds(min_value, max_value)
    inputset = [minimum, maximum]
    if minimum <= 0 <= maximum:
        inputset.append(0)
    return compile_function(
        square,
        {"value": "encrypted"},
        inputset,
        configuration,
    )


def compile_scalar_multiply(
    min_value: int,
    max_value: int,
    multiplier: int,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile multiplication by a public integer constant."""
    minimum, maximum = validate_bounds(min_value, max_value)
    function = make_scalar_multiply(multiplier)
    return compile_function(
        function,
        {"value": "encrypted"},
        [minimum, maximum],
        configuration,
    )


def _compile_predicate(
    function: BinaryFunction,
    min_value: int,
    max_value: int,
    configuration: Optional[fhe.Configuration],
) -> fhe.Circuit:
    minimum, maximum = validate_bounds(min_value, max_value)
    inputset = [
        (minimum, minimum),
        (minimum, maximum),
        (maximum, minimum),
        (maximum, maximum),
    ]
    if minimum < maximum:
        inputset.append((minimum, minimum + 1))
    return compile_function(
        function,
        {"left": "encrypted", "right": "encrypted"},
        inputset,
        configuration,
    )


def compile_equal(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted equality."""
    return _compile_predicate(equal, min_value, max_value, configuration)


def compile_not_equal(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted inequality."""
    return _compile_predicate(not_equal, min_value, max_value, configuration)


def compile_less(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted less-than comparison."""
    return _compile_predicate(less, min_value, max_value, configuration)


def compile_less_equal(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted less-than-or-equal comparison."""
    return _compile_predicate(less_equal, min_value, max_value, configuration)


def compile_greater(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted greater-than comparison."""
    return _compile_predicate(greater, min_value, max_value, configuration)


def compile_greater_equal(
    min_value: int = -15,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted greater-than-or-equal comparison."""
    return _compile_predicate(greater_equal, min_value, max_value, configuration)


def compile_is_close(
    min_value: int,
    max_value: int,
    *,
    absolute_tolerance: int,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile encrypted integer closeness with an absolute tolerance."""
    function = make_is_close(absolute_tolerance)
    return _compile_predicate(function, min_value, max_value, configuration)


def make_absolute(min_value: int, max_value: int) -> UnaryFunction:
    """Create an absolute-value lookup over inclusive signed bounds."""
    values = unary_values(abs, min_value, max_value)
    return make_unary_lookup(values, min_value)


def compile_absolute(
    min_value: int,
    max_value: int,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile absolute value over inclusive signed bounds."""
    values = unary_values(abs, min_value, max_value)
    return compile_unary_lookup(
        "compile_absolute",
        values,
        min_value,
        max_value,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_clamp(
    min_input: int,
    max_input: int,
    min_value: int,
    max_value: int,
) -> UnaryFunction:
    """Create a lookup that clamps input into [min_value, max_value]."""
    input_minimum, input_maximum = validate_bounds(min_input, max_input)
    clamp_minimum, clamp_maximum = validate_bounds(min_value, max_value)
    values = unary_values(
        lambda value: max(clamp_minimum, min(value, clamp_maximum)),
        input_minimum,
        input_maximum,
    )
    return make_unary_lookup(values, input_minimum)


def compile_clamp(
    min_input: int,
    max_input: int,
    min_value: int,
    max_value: int,
    *,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile clamping of an encrypted integer into public bounds."""
    input_minimum, input_maximum = validate_bounds(min_input, max_input)
    clamp_minimum, clamp_maximum = validate_bounds(min_value, max_value)
    values = unary_values(
        lambda value: max(clamp_minimum, min(value, clamp_maximum)),
        input_minimum,
        input_maximum,
    )
    return compile_unary_lookup(
        "compile_clamp",
        values,
        input_minimum,
        input_maximum,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_modulo(
    min_numerator: int,
    max_numerator: int,
    min_denominator: int,
    max_denominator: int,
    *,
    zero_result: int = 0,
) -> BinaryFunction:
    """Create Python-style modulo with an explicit zero-denominator result."""
    zero = validate_integer("zero_result", zero_result)
    values = binary_values(
        lambda numerator, denominator: (
            zero if denominator == 0 else numerator % denominator
        ),
        min_numerator,
        max_numerator,
        min_denominator,
        max_denominator,
    )
    denominator_minimum, denominator_maximum = validate_bounds(
        min_denominator,
        max_denominator,
    )
    return make_binary_lookup(
        values,
        min_numerator,
        denominator_minimum,
        denominator_maximum - denominator_minimum + 1,
    )


def compile_modulo(
    min_numerator: int,
    max_numerator: int,
    min_denominator: int,
    max_denominator: int,
    *,
    zero_result: int = 0,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile Python-style modulo with an explicit zero-denominator result."""
    zero = validate_integer("zero_result", zero_result)
    values = binary_values(
        lambda numerator, denominator: (
            zero if denominator == 0 else numerator % denominator
        ),
        min_numerator,
        max_numerator,
        min_denominator,
        max_denominator,
    )
    return compile_binary_lookup(
        "compile_modulo",
        values,
        min_numerator,
        max_numerator,
        min_denominator,
        max_denominator,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_divmod(
    min_numerator: int,
    max_numerator: int,
    min_denominator: int,
    max_denominator: int,
    *,
    zero_quotient: int = 0,
    zero_remainder: int = 0,
) -> BinaryFunction:
    """Create quotient-and-remainder lookup with explicit zero behavior."""
    zero_q = validate_integer("zero_quotient", zero_quotient)
    zero_r = validate_integer("zero_remainder", zero_remainder)
    denominator_minimum, denominator_maximum = validate_bounds(
        min_denominator,
        max_denominator,
    )
    quotient_values = binary_values(
        lambda numerator, denominator: (
            zero_q if denominator == 0 else numerator // denominator
        ),
        min_numerator,
        max_numerator,
        denominator_minimum,
        denominator_maximum,
    )
    remainder_values = binary_values(
        lambda numerator, denominator: (
            zero_r if denominator == 0 else numerator % denominator
        ),
        min_numerator,
        max_numerator,
        denominator_minimum,
        denominator_maximum,
    )
    width = denominator_maximum - denominator_minimum + 1
    quotient = make_binary_lookup(
        quotient_values,
        min_numerator,
        denominator_minimum,
        width,
    )
    remainder = make_binary_lookup(
        remainder_values,
        min_numerator,
        denominator_minimum,
        width,
    )

    def quotient_and_remainder(numerator: Any, denominator: Any) -> Any:
        return quotient(numerator, denominator), remainder(numerator, denominator)

    return quotient_and_remainder


def compile_divmod(
    min_numerator: int,
    max_numerator: int,
    min_denominator: int,
    max_denominator: int,
    *,
    zero_quotient: int = 0,
    zero_remainder: int = 0,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile quotient and remainder with explicit zero-denominator behavior."""
    function = make_divmod(
        min_numerator,
        max_numerator,
        min_denominator,
        max_denominator,
        zero_quotient=zero_quotient,
        zero_remainder=zero_remainder,
    )
    numerator_minimum, numerator_maximum = validate_bounds(
        min_numerator,
        max_numerator,
    )
    denominator_minimum, denominator_maximum = validate_bounds(
        min_denominator,
        max_denominator,
    )
    quotient_values = binary_values(
        lambda numerator, denominator: (
            zero_quotient if denominator == 0 else numerator // denominator
        ),
        numerator_minimum,
        numerator_maximum,
        denominator_minimum,
        denominator_maximum,
    )
    remainder_values = binary_values(
        lambda numerator, denominator: (
            zero_remainder if denominator == 0 else numerator % denominator
        ),
        numerator_minimum,
        numerator_maximum,
        denominator_minimum,
        denominator_maximum,
    )
    check_lookup_cost(
        "compile_divmod quotient",
        quotient_values,
        allow_large_lookup=allow_large_lookup,
    )
    check_lookup_cost(
        "compile_divmod remainder",
        remainder_values,
        allow_large_lookup=allow_large_lookup,
    )
    inputset = [
        (numerator, denominator)
        for numerator in range(numerator_minimum, numerator_maximum + 1)
        for denominator in range(denominator_minimum, denominator_maximum + 1)
    ]
    return compile_function(
        function,
        {"numerator": "encrypted", "denominator": "encrypted"},
        inputset,
        configuration,
    )


compile_abs = compile_absolute
make_abs = make_absolute
compile_sub = compile_subtract
compile_scalar_mul = compile_scalar_multiply
