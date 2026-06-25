"""Bit-level LUT primitives for Concrete FHE arithmetic circuits.

All bit lists in this module are little-endian: index 0 is the least
significant bit. The primitives are intentionally tiny traceable building
blocks, so they can be used on clear bits for tests or on encrypted bit
expressions while compiling larger Concrete circuits.
"""

from __future__ import annotations

from typing import Any, Iterable

from concrete import fhe

from .._utils import validate_integer

BIT_NOT_LUT = fhe.LookupTable([1, 0])
BIT_AND_LUT = fhe.LookupTable([0, 0, 0, 1])
BIT_OR_LUT = fhe.LookupTable([0, 1, 1, 1])
BIT_XOR_LUT = fhe.LookupTable([0, 1, 1, 0])
FULL_ADDER_SUM_LUT = fhe.LookupTable([0, 1, 1, 0, 1, 0, 0, 1])
FULL_ADDER_CARRY_LUT = fhe.LookupTable([0, 0, 0, 1, 0, 1, 1, 1])
FULL_SUBTRACTOR_DIFF_LUT = fhe.LookupTable([0, 1, 1, 0, 1, 0, 0, 1])
FULL_SUBTRACTOR_BORROW_LUT = fhe.LookupTable([0, 1, 1, 1, 0, 0, 0, 1])
BIT_SELECT_LUT = fhe.LookupTable([0, 1, 0, 1, 0, 0, 1, 1])


def _bit_width(width: int) -> int:
    return validate_integer("width", width, minimum=1)


def bit_not(bit: Any) -> Any:
    """Return NOT(bit) for a bit expression."""
    return BIT_NOT_LUT[bit]


def bit_and(left: Any, right: Any) -> Any:
    """Return left AND right for bit expressions."""
    return BIT_AND_LUT[2 * left + right]


def bit_or(left: Any, right: Any) -> Any:
    """Return left OR right for bit expressions."""
    return BIT_OR_LUT[2 * left + right]


def bit_xor(left: Any, right: Any) -> Any:
    """Return left XOR right for bit expressions."""
    return BIT_XOR_LUT[2 * left + right]


def bit_select(control: Any, when_one: Any, when_zero: Any) -> Any:
    """Return when_one if control is 1, otherwise when_zero."""
    return BIT_SELECT_LUT[4 * control + 2 * when_one + when_zero]


def full_adder_bit(left: Any, right: Any, carry_in: Any) -> tuple[Any, Any]:
    """Return (sum_bit, carry_out) for one full-adder stage."""
    address = 4 * left + 2 * right + carry_in
    return FULL_ADDER_SUM_LUT[address], FULL_ADDER_CARRY_LUT[address]


def full_subtractor_bit(left: Any, right: Any, borrow_in: Any) -> tuple[Any, Any]:
    """Return (difference_bit, borrow_out) for one full-subtractor stage."""
    address = 4 * left + 2 * right + borrow_in
    return FULL_SUBTRACTOR_DIFF_LUT[address], FULL_SUBTRACTOR_BORROW_LUT[address]


def bit_or_many(bits: Iterable[Any]) -> Any:
    """Return the OR-reduction of a bit iterable."""
    result: Any = 0
    for bit in bits:
        result = bit_or(result, bit)
    return result


def integer_to_bits(value: Any, width: int) -> tuple[Any, ...]:
    """Return little-endian bits of an unsigned integer expression."""
    normalized_width = _bit_width(width)
    return tuple((value >> index) & 1 for index in range(normalized_width))


def bits_to_unsigned(bits: Iterable[Any]) -> Any:
    """Convert little-endian bits to an unsigned integer expression."""
    result: Any = 0
    for index, bit in enumerate(bits):
        result = result + bit * (1 << index)
    return result


def unsigned_to_bits(value: int, width: int) -> tuple[int, ...]:
    """Return little-endian bits of a clear unsigned integer constant."""
    normalized_width = _bit_width(width)
    normalized_value = validate_integer("value", value, minimum=0)
    if normalized_value >= (1 << normalized_width):
        raise ValueError("value does not fit in width bits")
    return tuple((normalized_value >> index) & 1 for index in range(normalized_width))


def twos_complement_bits(value: int, width: int) -> tuple[int, ...]:
    """Return little-endian two's-complement bits for a clear signed integer."""
    normalized_width = _bit_width(width)
    normalized_value = validate_integer("value", value)
    minimum = -(1 << (normalized_width - 1))
    maximum = (1 << (normalized_width - 1)) - 1
    if not minimum <= normalized_value <= maximum:
        raise ValueError(f"value must fit in signed {normalized_width}-bit range")
    if normalized_value < 0:
        normalized_value = (1 << normalized_width) + normalized_value
    return tuple((normalized_value >> index) & 1 for index in range(normalized_width))


def sign_magnitude_to_twos_complement_bits(
    magnitude_bits: Iterable[Any],
    sign_bit: Any,
    width: int | None = None,
) -> tuple[Any, ...]:
    """Convert sign-magnitude bits to two's-complement bits.

    The output width is one bit wider than the magnitude width so the sign can
    be represented safely.
    """
    bits = tuple(magnitude_bits)
    if not bits:
        raise ValueError("magnitude_bits must contain at least one bit")
    normalized_width = len(bits) if width is None else _bit_width(width)
    if len(bits) < normalized_width:
        bits = bits + (0,) * (normalized_width - len(bits))
    elif len(bits) > normalized_width:
        raise ValueError("magnitude_bits is longer than width")

    flipped = tuple(bit_xor(bit, sign_bit) for bit in bits)
    output: list[Any] = []
    carry = sign_bit
    for bit in flipped:
        result_bit, carry = full_adder_bit(bit, 0, carry)
        output.append(result_bit)
    output.append(sign_bit)

    magnitude_nonzero = bit_or_many(bits)
    return tuple(bit_select(magnitude_nonzero, bit, 0) for bit in output)


def twos_complement_add_bits(
    left_bits: Iterable[Any],
    right_bits: Iterable[Any],
    width: int,
) -> tuple[Any, ...]:
    """Add two two's-complement bit lists modulo 2**width."""
    normalized_width = _bit_width(width)
    left = tuple(left_bits)
    right = tuple(right_bits)
    left_sign = left[-1] if left else 0
    right_sign = right[-1] if right else 0
    result: list[Any] = []
    carry: Any = 0
    for index in range(normalized_width):
        left_bit = left[index] if index < len(left) else left_sign
        right_bit = right[index] if index < len(right) else right_sign
        result_bit, carry = full_adder_bit(left_bit, right_bit, carry)
        result.append(result_bit)
    return tuple(result)


def twos_complement_multiply_by_constant_bits(
    signed_bits: Iterable[Any],
    multiplier: int,
    output_width: int,
) -> tuple[Any, ...]:
    """Multiply two's-complement bits by a nonnegative clear integer."""
    bits = tuple(signed_bits)
    if not bits:
        raise ValueError("signed_bits must contain at least one bit")
    normalized_multiplier = validate_integer("multiplier", multiplier, minimum=0)
    normalized_output_width = _bit_width(output_width)
    sign_bit = bits[-1]
    result: tuple[Any, ...] = (0,) * normalized_output_width

    for shift in range(normalized_multiplier.bit_length()):
        if (normalized_multiplier >> shift) & 1:
            shifted = (
                (0,) * shift
                + tuple(
                    bits[index] if index < len(bits) else sign_bit
                    for index in range(normalized_output_width - shift)
                )
            )[:normalized_output_width]
            result = twos_complement_add_bits(
                result,
                shifted,
                normalized_output_width,
            )

    return result


# Short aliases for users who prefer classic bit-circuit notation.
bnot = bit_not
band = bit_and
bor = bit_or
bxor = bit_xor
bsel = bit_select
fadd_bit = full_adder_bit
fsub_bit = full_subtractor_bit
