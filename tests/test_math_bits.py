from itertools import product

from concrete_fhe_toolkit import math as fhe_math


def _bits_to_int(bits):
    return sum(int(bit) << index for index, bit in enumerate(bits))


def _bits_to_signed(bits):
    value = _bits_to_int(bits)
    if bits and int(bits[-1]):
        value -= 1 << len(bits)
    return value


def _unsigned_bits(value, width):
    return tuple((value >> index) & 1 for index in range(width))


def test_bit_lut_primitives_clear():
    for bit in (0, 1):
        assert int(fhe_math.bit_not(bit)) == 1 - bit
        assert int(fhe_math.bnot(bit)) == 1 - bit

    for left, right in product((0, 1), repeat=2):
        assert int(fhe_math.bit_and(left, right)) == (left & right)
        assert int(fhe_math.bit_or(left, right)) == (left | right)
        assert int(fhe_math.bit_xor(left, right)) == (left ^ right)
        assert int(fhe_math.band(left, right)) == (left & right)
        assert int(fhe_math.bor(left, right)) == (left | right)
        assert int(fhe_math.bxor(left, right)) == (left ^ right)

    for control, when_one, when_zero in product((0, 1), repeat=3):
        expected = when_one if control else when_zero
        assert int(fhe_math.bit_select(control, when_one, when_zero)) == expected
        assert int(fhe_math.bsel(control, when_one, when_zero)) == expected


def test_full_adder_and_subtractor_bits_clear():
    for left, right, carry in product((0, 1), repeat=3):
        result_bit, carry_out = fhe_math.full_adder_bit(left, right, carry)
        expected = left + right + carry
        assert int(result_bit) == expected & 1
        assert int(carry_out) == int(expected >= 2)

        alias_result_bit, alias_carry_out = fhe_math.fadd_bit(left, right, carry)
        assert int(alias_result_bit) == expected & 1
        assert int(alias_carry_out) == int(expected >= 2)

    for left, right, borrow in product((0, 1), repeat=3):
        result_bit, borrow_out = fhe_math.full_subtractor_bit(left, right, borrow)
        expected = left - right - borrow
        assert int(result_bit) == (expected % 2)
        assert int(borrow_out) == int(expected < 0)

        alias_result_bit, alias_borrow_out = fhe_math.fsub_bit(left, right, borrow)
        assert int(alias_result_bit) == (expected % 2)
        assert int(alias_borrow_out) == int(expected < 0)


def test_bit_conversion_helpers_clear():
    assert fhe_math.unsigned_to_bits(13, 5) == (1, 0, 1, 1, 0)
    assert fhe_math.twos_complement_bits(-3, 4) == (1, 0, 1, 1)
    assert _bits_to_int(fhe_math.integer_to_bits(13, 5)) == 13
    assert int(fhe_math.bits_to_unsigned((1, 0, 1, 1))) == 13


def test_signed_bit_helpers_clear():
    for magnitude, sign in product(range(8), (0, 1)):
        magnitude_bits = _unsigned_bits(magnitude, 3)
        result = fhe_math.sign_magnitude_to_twos_complement_bits(
            magnitude_bits,
            sign,
        )
        expected = -magnitude if sign else magnitude
        assert _bits_to_signed(result) == expected

    for left in range(-4, 4):
        for right in range(-4, 4):
            left_bits = fhe_math.twos_complement_bits(left, 4)
            right_bits = fhe_math.twos_complement_bits(right, 4)
            result = fhe_math.twos_complement_add_bits(left_bits, right_bits, 5)
            assert _bits_to_signed(result) == left + right

    for value in range(-4, 4):
        value_bits = fhe_math.twos_complement_bits(value, 4)
        result = fhe_math.twos_complement_multiply_by_constant_bits(
            value_bits,
            3,
            6,
        )
        assert _bits_to_signed(result) == value * 3


def test_unsigned_divide_bits_clear():
    for numerator in range(16):
        for denominator in range(8):
            result = fhe_math.unsigned_divide_bits(
                _unsigned_bits(numerator, 4),
                _unsigned_bits(denominator, 3),
                zero_result=15,
            )
            expected = 15 if denominator == 0 else numerator // denominator
            assert _bits_to_int(result) == expected


def test_fixed_point_divide_bits_clear():
    for numerator in range(16):
        for denominator in range(1, 8):
            result = fhe_math.fixed_point_divide_bits(
                _unsigned_bits(numerator, 4),
                _unsigned_bits(denominator, 3),
                fractional_bits=3,
            )
            assert _bits_to_int(result) == (numerator << 3) // denominator


def test_scalar_division_builders_clear():
    floor_divide = fhe_math.make_unsigned_floor_divide(4, 3, zero_result=15)
    fixed_divide = fhe_math.make_fixed_point_divide(4, 3, fractional_bits=3)

    for numerator in range(16):
        for denominator in range(8):
            expected = 15 if denominator == 0 else numerator // denominator
            assert int(floor_divide(numerator, denominator)) == expected

    for numerator in range(16):
        for denominator in range(1, 8):
            expected = (numerator << 3) // denominator
            assert int(fixed_divide(numerator, denominator)) == expected


def test_friendly_operations_compile_by_default_and_expose_make():
    gcd = fhe_math.gcd(0, 6)
    assert int(gcd.simulate(6, 4)) == 2

    gcd_function = fhe_math.gcd.make(0, 6)
    assert int(gcd_function(6, 4)) == 2
    assert fhe_math.gcd.compile is fhe_math.compile_gcd

    sine = fhe_math.sin(
        0,
        90,
        input_scale=1,
        output_scale=100,
        angle_unit="degrees",
    )
    assert int(sine.simulate(30)) == 50
