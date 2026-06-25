from fractions import Fraction
from itertools import product
import math

import pytest

from concrete_fhe_toolkit import math as fhe_math


def test_basic_native_operations_clear():
    for left, right in product(range(-4, 5), repeat=2):
        assert int(fhe_math.add(left, right)) == left + right
        assert int(fhe_math.subtract(left, right)) == left - right
        assert int(fhe_math.multiply(left, right)) == left * right
        assert int(fhe_math.equal(left, right)) == int(left == right)
        assert int(fhe_math.not_equal(left, right)) == int(left != right)
        assert int(fhe_math.less(left, right)) == int(left < right)
        assert int(fhe_math.less_equal(left, right)) == int(left <= right)
        assert int(fhe_math.greater(left, right)) == int(left > right)
        assert int(fhe_math.greater_equal(left, right)) == int(left >= right)

    for value in range(-8, 9):
        assert int(fhe_math.negate(value)) == -value
        assert int(fhe_math.square(value)) == value * value
        assert int(fhe_math.make_scalar_multiply(-3)(value)) == value * -3


def test_basic_lookup_operations_clear():
    absolute = fhe_math.make_absolute(-7, 7)
    clamp = fhe_math.make_clamp(-10, 10, -3, 4)
    modulo = fhe_math.make_modulo(-7, 7, -4, 4, zero_result=-99)
    quotient_and_remainder = fhe_math.make_divmod(
        -7,
        7,
        -4,
        4,
        zero_quotient=-100,
        zero_remainder=-99,
    )
    close = fhe_math.make_is_close(2)

    for value in range(-7, 8):
        assert int(absolute(value)) == abs(value)

    for value in range(-10, 11):
        assert int(clamp(value)) == max(-3, min(value, 4))

    for numerator, denominator in product(range(-7, 8), range(-4, 5)):
        if denominator == 0:
            assert int(modulo(numerator, denominator)) == -99
            assert tuple(
                int(part)
                for part in quotient_and_remainder(numerator, denominator)
            ) == (-100, -99)
        else:
            assert int(modulo(numerator, denominator)) == numerator % denominator
            assert tuple(
                int(part)
                for part in quotient_and_remainder(numerator, denominator)
            ) == divmod(numerator, denominator)

    for left, right in product(range(-5, 6), repeat=2):
        assert int(close(left, right)) == int(abs(left - right) <= 2)


def test_combinatorics_clear():
    factorial = fhe_math.make_factorial(8)
    fibonacci = fhe_math.make_fibonacci(12)
    power = fhe_math.make_power(-2, 8)
    comb = fhe_math.make_comb(7, invalid_result=-1)
    perm = fhe_math.make_perm(7, invalid_result=-1)

    fib_values = [0, 1]
    for _ in range(2, 13):
        fib_values.append(fib_values[-1] + fib_values[-2])

    for value in range(9):
        assert int(factorial(value)) == math.factorial(value)

    for value in range(13):
        assert int(fibonacci(value)) == fib_values[value]

    for value in range(9):
        assert int(power(value)) == (-2) ** value

    for n, r in product(range(8), repeat=2):
        assert int(comb(n, r)) == (math.comb(n, r) if r <= n else -1)
        assert int(perm(n, r)) == (math.perm(n, r) if r <= n else -1)


def test_number_theory_clear():
    gcd = fhe_math.make_gcd(-8, 8)
    lcm = fhe_math.make_lcm(-8, 8)
    coprime = fhe_math.make_is_coprime(-8, 8)
    divisible = fhe_math.make_is_divisible(-8, 8, -5, 5, zero_result=-1)
    isqrt = fhe_math.make_isqrt(40)
    even = fhe_math.make_is_even(-10, 10)
    odd = fhe_math.make_is_odd(-10, 10)
    prime = fhe_math.make_is_prime(-5, 40)

    for left, right in product(range(-8, 9), repeat=2):
        assert int(gcd(left, right)) == math.gcd(left, right)
        assert int(lcm(left, right)) == math.lcm(left, right)
        assert int(coprime(left, right)) == int(math.gcd(left, right) == 1)

    for numerator, denominator in product(range(-8, 9), range(-5, 6)):
        expected = -1 if denominator == 0 else int(numerator % denominator == 0)
        assert int(divisible(numerator, denominator)) == expected

    for value in range(41):
        assert int(isqrt(value)) == math.isqrt(value)

    for value in range(-10, 11):
        assert int(even(value)) == int(value % 2 == 0)
        assert int(odd(value)) == int(value % 2 != 0)

    for value in range(-5, 41):
        expected = value >= 2 and all(
            value % divisor
            for divisor in range(2, math.isqrt(value) + 1)
        )
        assert int(prime(value)) == int(expected)


def test_fixed_point_clear():
    floor = fhe_math.make_floor(-45, 45, scale=10)
    ceil = fhe_math.make_ceil(-45, 45, scale=10)
    trunc = fhe_math.make_trunc(-45, 45, scale=10)
    rounded = fhe_math.make_round(-45, 45, scale=10)
    floor_ceil = fhe_math.make_floor_ceil(-45, 45, scale=10)
    rescale = fhe_math.make_rescale(
        -20,
        20,
        input_scale=10,
        output_scale=100,
        rounding="nearest",
    )

    for value in range(-45, 46):
        assert int(floor(value)) == math.floor(value / 10)
        assert int(ceil(value)) == math.ceil(value / 10)
        assert int(trunc(value)) == math.trunc(value / 10)
        assert int(rounded(value)) == round(Fraction(value, 10))
        assert tuple(int(part) for part in floor_ceil(value)) == (
            math.floor(value / 10),
            math.ceil(value / 10),
        )

    for value in range(-20, 21):
        assert int(rescale(value)) == round(Fraction(value * 100, 10))


def test_special_functions_clear():
    sin = fhe_math.make_sin(0, 90, input_scale=1, output_scale=1000, angle_unit="degrees")
    cos = fhe_math.make_cos(0, 90, input_scale=1, output_scale=1000, angle_unit="degrees")
    tanh = fhe_math.make_tanh(-30, 30, input_scale=10, output_scale=1000)
    sigmoid = fhe_math.make_sigmoid(-30, 30, input_scale=10, output_scale=1000)
    erf = fhe_math.make_erf(-20, 20, input_scale=10, output_scale=100)
    log2 = fhe_math.make_log2(1, 32, input_scale=1, output_scale=100)
    sqrt = fhe_math.make_sqrt(0, 100, input_scale=10, output_scale=100)

    for degrees in range(0, 91, 5):
        assert int(sin(degrees)) == round(math.sin(math.radians(degrees)) * 1000)
        assert int(cos(degrees)) == round(math.cos(math.radians(degrees)) * 1000)

    for value in range(-30, 31):
        assert int(tanh(value)) == round(math.tanh(value / 10) * 1000)
        expected_sigmoid = round((1 / (1 + math.exp(-(value / 10)))) * 1000)
        assert int(sigmoid(value)) == expected_sigmoid

    for value in range(-20, 21):
        assert int(erf(value)) == round(math.erf(value / 10) * 100)

    for value in range(1, 33):
        assert int(log2(value)) == round(math.log2(value) * 100)

    for value in range(101):
        assert int(sqrt(value)) == round(math.sqrt(value / 10) * 100)


def test_special_domain_policy_is_explicit():
    with pytest.raises(ValueError, match="invalid_result"):
        fhe_math.make_log2(0, 5)

    log2 = fhe_math.make_log2(0, 5, invalid_result=-1)
    assert int(log2(0)) == -1
    assert int(log2(4)) == 200
