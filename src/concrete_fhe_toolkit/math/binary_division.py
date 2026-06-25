"""Binary restoring division helpers for Concrete FHE circuits."""

from __future__ import annotations

from typing import Any, Iterable, Optional

from concrete import fhe

from .._utils import compile_function, validate_integer
from .bits import (
    bit_not,
    bit_or_many,
    bit_select,
    bits_to_unsigned,
    full_subtractor_bit,
    integer_to_bits,
    unsigned_to_bits,
)


def _validate_width(name: str, value: int) -> int:
    return validate_integer(name, value, minimum=1)


def _validate_fractional_bits(value: int) -> int:
    return validate_integer("fractional_bits", value, minimum=0)


def _validate_zero_result(zero_result: int, quotient_width: int) -> int:
    normalized = validate_integer("zero_result", zero_result, minimum=0)
    if normalized >= (1 << quotient_width):
        raise ValueError("zero_result does not fit in quotient_width bits")
    return normalized


def _as_nonempty_bits(name: str, bits: Iterable[Any]) -> tuple[Any, ...]:
    normalized = tuple(bits)
    if not normalized:
        raise ValueError(f"{name} must contain at least one bit")
    return normalized


def _restoring_divide_bits(
    numerator_bits: tuple[Any, ...],
    denominator_bits: tuple[Any, ...],
    quotient_width: int,
) -> tuple[Any, ...]:
    remainder: list[Any] = [0] * (quotient_width + 1)
    quotient: list[Any] = [0] * quotient_width
    padded_denominator = (
        list(denominator_bits) + [0] * (quotient_width + 1)
    )[: quotient_width + 1]
    padded_numerator = (
        list(numerator_bits) + [0] * quotient_width
    )[:quotient_width]

    for index in range(quotient_width - 1, -1, -1):
        remainder = [padded_numerator[index]] + remainder[:quotient_width]
        difference: list[Any] = [0] * (quotient_width + 1)
        borrow: Any = 0

        for bit_index in range(quotient_width + 1):
            difference[bit_index], borrow = full_subtractor_bit(
                remainder[bit_index],
                padded_denominator[bit_index],
                borrow,
            )

        no_borrow = bit_not(borrow)
        quotient[index] = no_borrow
        remainder = [
            bit_select(no_borrow, difference[bit_index], remainder[bit_index])
            for bit_index in range(quotient_width + 1)
        ]

    return tuple(quotient)


def unsigned_divide_bits(
    numerator_bits: Iterable[Any],
    denominator_bits: Iterable[Any],
    *,
    quotient_width: int | None = None,
    zero_result: int = 0,
) -> tuple[Any, ...]:
    """Return little-endian quotient bits for unsigned floor division.

    Division by zero returns the clear fallback encoded by `zero_result`.
    """
    numerator = _as_nonempty_bits("numerator_bits", numerator_bits)
    denominator = _as_nonempty_bits("denominator_bits", denominator_bits)
    width = (
        len(numerator)
        if quotient_width is None
        else _validate_width("quotient_width", quotient_width)
    )
    if len(numerator) > width:
        raise ValueError("quotient_width must be at least len(numerator_bits)")
    zero = _validate_zero_result(zero_result, width)

    quotient = _restoring_divide_bits(numerator, denominator, width)
    denominator_nonzero = bit_or_many(denominator)
    fallback = unsigned_to_bits(zero, width)
    return tuple(
        bit_select(denominator_nonzero, quotient[index], fallback[index])
        for index in range(width)
    )


def fixed_point_divide_bits(
    numerator_bits: Iterable[Any],
    denominator_bits: Iterable[Any],
    *,
    fractional_bits: int,
    quotient_width: int | None = None,
    zero_result: int = 0,
) -> tuple[Any, ...]:
    """Return quotient bits for floor((numerator << fractional_bits) / denominator)."""
    numerator = _as_nonempty_bits("numerator_bits", numerator_bits)
    fraction = _validate_fractional_bits(fractional_bits)
    shifted_numerator = (0,) * fraction + numerator
    width = (
        len(shifted_numerator)
        if quotient_width is None
        else _validate_width("quotient_width", quotient_width)
    )
    if len(shifted_numerator) > width:
        raise ValueError(
            "quotient_width must be at least len(numerator_bits) + fractional_bits"
        )
    return unsigned_divide_bits(
        shifted_numerator,
        denominator_bits,
        quotient_width=width,
        zero_result=zero_result,
    )


def make_unsigned_floor_divide(
    numerator_width: int,
    denominator_width: int,
    *,
    quotient_width: int | None = None,
    zero_result: int = 0,
) -> Any:
    """Create unsigned encrypted floor division from scalar integer inputs."""
    n_width = _validate_width("numerator_width", numerator_width)
    d_width = _validate_width("denominator_width", denominator_width)
    q_width = (
        n_width
        if quotient_width is None
        else _validate_width("quotient_width", quotient_width)
    )
    if q_width < n_width:
        raise ValueError("quotient_width must be at least numerator_width")
    zero = _validate_zero_result(zero_result, q_width)

    def divide(numerator: Any, denominator: Any) -> Any:
        numerator_bits = integer_to_bits(numerator, n_width)
        denominator_bits = integer_to_bits(denominator, d_width)
        quotient_bits = unsigned_divide_bits(
            numerator_bits,
            denominator_bits,
            quotient_width=q_width,
            zero_result=zero,
        )
        return bits_to_unsigned(quotient_bits)

    return divide


def make_fixed_point_divide(
    numerator_width: int,
    denominator_width: int,
    *,
    fractional_bits: int,
    quotient_width: int | None = None,
    zero_result: int = 0,
) -> Any:
    """Create fixed-point unsigned division from scalar integer inputs."""
    n_width = _validate_width("numerator_width", numerator_width)
    d_width = _validate_width("denominator_width", denominator_width)
    fraction = _validate_fractional_bits(fractional_bits)
    default_width = n_width + fraction
    q_width = (
        default_width
        if quotient_width is None
        else _validate_width("quotient_width", quotient_width)
    )
    if q_width < default_width:
        raise ValueError(
            "quotient_width must be at least numerator_width + fractional_bits"
        )
    zero = _validate_zero_result(zero_result, q_width)

    def divide(numerator: Any, denominator: Any) -> Any:
        numerator_bits = integer_to_bits(numerator, n_width)
        denominator_bits = integer_to_bits(denominator, d_width)
        quotient_bits = fixed_point_divide_bits(
            numerator_bits,
            denominator_bits,
            fractional_bits=fraction,
            quotient_width=q_width,
            zero_result=zero,
        )
        return bits_to_unsigned(quotient_bits)

    return divide


def _division_inputset(
    numerator_width: int,
    denominator_width: int,
) -> list[tuple[int, int]]:
    numerator_maximum = (1 << numerator_width) - 1
    denominator_maximum = (1 << denominator_width) - 1
    samples: set[tuple[int, int]] = {
        (0, 0),
        (0, 1),
        (numerator_maximum, 0),
        (numerator_maximum, 1),
        (numerator_maximum, denominator_maximum),
    }

    for bit_index in range(numerator_width):
        value = 1 << bit_index
        samples.add((value, 1))
        samples.add((value, denominator_maximum))

    for bit_index in range(denominator_width):
        value = 1 << bit_index
        samples.add((0, value))
        samples.add((numerator_maximum, value))

    return sorted(samples)


def compile_unsigned_floor_divide(
    numerator_width: int,
    denominator_width: int,
    *,
    quotient_width: int | None = None,
    zero_result: int = 0,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile unsigned floor division using a bit-level restoring circuit."""
    n_width = _validate_width("numerator_width", numerator_width)
    d_width = _validate_width("denominator_width", denominator_width)
    function = make_unsigned_floor_divide(
        n_width,
        d_width,
        quotient_width=quotient_width,
        zero_result=zero_result,
    )
    return compile_function(
        function,
        {"numerator": "encrypted", "denominator": "encrypted"},
        _division_inputset(n_width, d_width),
        configuration,
    )


def compile_fixed_point_divide(
    numerator_width: int,
    denominator_width: int,
    *,
    fractional_bits: int,
    quotient_width: int | None = None,
    zero_result: int = 0,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile fixed-point unsigned division using a bit-level circuit."""
    n_width = _validate_width("numerator_width", numerator_width)
    d_width = _validate_width("denominator_width", denominator_width)
    function = make_fixed_point_divide(
        n_width,
        d_width,
        fractional_bits=fractional_bits,
        quotient_width=quotient_width,
        zero_result=zero_result,
    )
    return compile_function(
        function,
        {"numerator": "encrypted", "denominator": "encrypted"},
        _division_inputset(n_width, d_width),
        configuration,
    )
