from fractions import Fraction
from itertools import product
import math

import pytest

from concrete_fhe_toolkit import math as fhe_math
from concrete_fhe_toolkit.math import FHECostWarning, LookupResourceError


def test_native_basic_math_compiles_and_simulates():
    add = fhe_math.compile_add(-3, 4, -2, 5)
    subtract = fhe_math.compile_subtract(-3, 4, -2, 5)
    multiply = fhe_math.compile_multiply(-3, 4, -2, 5)
    negate = fhe_math.compile_negate(-4, 4)
    square = fhe_math.compile_square(-4, 4)
    scalar = fhe_math.compile_scalar_multiply(-3, 4, -5)

    for left, right in product(range(-3, 5), range(-2, 6)):
        assert int(add.simulate(left, right)) == left + right
        assert int(subtract.simulate(left, right)) == left - right
        assert int(multiply.simulate(left, right)) == left * right

    for value in range(-4, 5):
        assert int(negate.simulate(value)) == -value
        assert int(square.simulate(value)) == value * value

    for value in range(-3, 5):
        assert int(scalar.simulate(value)) == value * -5


def test_predicates_compile_and_simulate():
    circuits = [
        (fhe_math.compile_equal(-3, 3), lambda a, b: int(a == b)),
        (fhe_math.compile_not_equal(-3, 3), lambda a, b: int(a != b)),
        (fhe_math.compile_less(-3, 3), lambda a, b: int(a < b)),
        (fhe_math.compile_less_equal(-3, 3), lambda a, b: int(a <= b)),
        (fhe_math.compile_greater(-3, 3), lambda a, b: int(a > b)),
        (fhe_math.compile_greater_equal(-3, 3), lambda a, b: int(a >= b)),
        (
            fhe_math.compile_is_close(-3, 3, absolute_tolerance=1),
            lambda a, b: int(abs(a - b) <= 1),
        ),
    ]

    for circuit, expected in circuits:
        for left, right in product(range(-3, 4), repeat=2):
            assert int(circuit.simulate(left, right)) == expected(left, right)


def test_lookup_basic_math_compiles_and_simulates():
    absolute = fhe_math.compile_absolute(-6, 6)
    clamp = fhe_math.compile_clamp(-6, 6, -2, 3)
    modulo = fhe_math.compile_modulo(-6, 6, -3, 3, zero_result=-99)
    quotient_and_remainder = fhe_math.compile_divmod(
        -6,
        6,
        -3,
        3,
        zero_quotient=-100,
        zero_remainder=-99,
    )

    for value in range(-6, 7):
        assert int(absolute.simulate(value)) == abs(value)
        assert int(clamp.simulate(value)) == max(-2, min(value, 3))

    for numerator, denominator in product(range(-6, 7), range(-3, 4)):
        expected_modulo = -99 if denominator == 0 else numerator % denominator
        assert int(modulo.simulate(numerator, denominator)) == expected_modulo

        expected_divmod = (
            (-100, -99)
            if denominator == 0
            else divmod(numerator, denominator)
        )
        assert tuple(
            int(part)
            for part in quotient_and_remainder.simulate(numerator, denominator)
        ) == expected_divmod


def test_combinatorics_compile_and_simulate():
    factorial = fhe_math.compile_factorial(7)
    fibonacci = fhe_math.compile_fibonacci(10)
    power = fhe_math.compile_power(-2, 6)
    comb = fhe_math.compile_comb(6, invalid_result=-1)
    perm = fhe_math.compile_perm(6, invalid_result=-1)

    fib_values = [0, 1]
    for _ in range(2, 11):
        fib_values.append(fib_values[-1] + fib_values[-2])

    for value in range(8):
        assert int(factorial.simulate(value)) == math.factorial(value)

    for value in range(11):
        assert int(fibonacci.simulate(value)) == fib_values[value]

    for value in range(7):
        assert int(power.simulate(value)) == (-2) ** value

    for n, r in product(range(7), repeat=2):
        assert int(comb.simulate(n, r)) == (math.comb(n, r) if r <= n else -1)
        assert int(perm.simulate(n, r)) == (math.perm(n, r) if r <= n else -1)


def test_number_theory_compile_and_simulate():
    gcd = fhe_math.compile_gcd(-6, 6)
    lcm = fhe_math.compile_lcm(-6, 6)
    coprime = fhe_math.compile_is_coprime(-6, 6)
    divisible = fhe_math.compile_is_divisible(-6, 6, -3, 3, zero_result=-1)
    isqrt = fhe_math.compile_isqrt(40)
    even = fhe_math.compile_is_even(-10, 10)
    odd = fhe_math.compile_is_odd(-10, 10)
    prime = fhe_math.compile_is_prime(-5, 40)

    for left, right in product(range(-6, 7), repeat=2):
        assert int(gcd.simulate(left, right)) == math.gcd(left, right)
        assert int(lcm.simulate(left, right)) == math.lcm(left, right)
        assert int(coprime.simulate(left, right)) == int(math.gcd(left, right) == 1)

    for numerator, denominator in product(range(-6, 7), range(-3, 4)):
        expected = -1 if denominator == 0 else int(numerator % denominator == 0)
        assert int(divisible.simulate(numerator, denominator)) == expected

    for value in range(41):
        assert int(isqrt.simulate(value)) == math.isqrt(value)

    for value in range(-10, 11):
        assert int(even.simulate(value)) == int(value % 2 == 0)
        assert int(odd.simulate(value)) == int(value % 2 != 0)

    for value in range(-5, 41):
        expected = value >= 2 and all(
            value % divisor
            for divisor in range(2, math.isqrt(value) + 1)
        )
        assert int(prime.simulate(value)) == int(expected)


def test_fixed_point_compile_and_simulate():
    floor = fhe_math.compile_floor(-45, 45, scale=10)
    ceil = fhe_math.compile_ceil(-45, 45, scale=10)
    trunc = fhe_math.compile_trunc(-45, 45, scale=10)
    rounded = fhe_math.compile_round(-45, 45, scale=10)
    floor_ceil = fhe_math.compile_floor_ceil(-45, 45, scale=10)
    rescale = fhe_math.compile_rescale(
        -20,
        20,
        input_scale=10,
        output_scale=100,
    )

    for value in range(-45, 46):
        assert int(floor.simulate(value)) == math.floor(value / 10)
        assert int(ceil.simulate(value)) == math.ceil(value / 10)
        assert int(trunc.simulate(value)) == math.trunc(value / 10)
        assert int(rounded.simulate(value)) == round(Fraction(value, 10))
        assert tuple(int(part) for part in floor_ceil.simulate(value)) == (
            math.floor(value / 10),
            math.ceil(value / 10),
        )

    for value in range(-20, 21):
        assert int(rescale.simulate(value)) == round(Fraction(value * 100, 10))


def test_bit_level_division_compiles_and_simulates():
    floor_divide = fhe_math.compile_unsigned_floor_divide(
        numerator_width=4,
        denominator_width=3,
        zero_result=15,
    )
    fixed_divide = fhe_math.compile_fixed_point_divide(
        numerator_width=4,
        denominator_width=3,
        fractional_bits=3,
    )

    for numerator in range(16):
        for denominator in range(8):
            expected = 15 if denominator == 0 else numerator // denominator
            assert int(floor_divide.simulate(numerator, denominator)) == expected

    for numerator in range(16):
        for denominator in range(1, 8):
            expected = (numerator << 3) // denominator
            assert int(fixed_divide.simulate(numerator, denominator)) == expected


def test_special_functions_compile_and_simulate():
    circuits = [
        (
            fhe_math.compile_sin(0, 90, input_scale=1, output_scale=1000, angle_unit="degrees"),
            range(0, 91, 5),
            lambda value: round(math.sin(math.radians(value)) * 1000),
        ),
        (
            fhe_math.compile_cos(0, 90, input_scale=1, output_scale=1000, angle_unit="degrees"),
            range(0, 91, 5),
            lambda value: round(math.cos(math.radians(value)) * 1000),
        ),
        (
            fhe_math.compile_tanh(-30, 30, input_scale=10, output_scale=1000),
            range(-30, 31),
            lambda value: round(math.tanh(value / 10) * 1000),
        ),
        (
            fhe_math.compile_sigmoid(-30, 30, input_scale=10, output_scale=1000),
            range(-30, 31),
            lambda value: round((1 / (1 + math.exp(-(value / 10)))) * 1000),
        ),
        (
            fhe_math.compile_log2(1, 32, input_scale=1, output_scale=100),
            range(1, 33),
            lambda value: round(math.log2(value) * 100),
        ),
        (
            fhe_math.compile_sqrt(0, 100, input_scale=10, output_scale=100),
            range(0, 101),
            lambda value: round(math.sqrt(value / 10) * 100),
        ),
        (
            fhe_math.compile_erf(-20, 20, input_scale=10, output_scale=100),
            range(-20, 21),
            lambda value: round(math.erf(value / 10) * 100),
        ),
    ]

    for circuit, domain, expected in circuits:
        for value in domain:
            assert int(circuit.simulate(value)) == expected(value)


def test_large_lookup_requires_explicit_opt_in():
    with pytest.raises(LookupResourceError):
        fhe_math.compile_gcd(0, 31)

    with pytest.warns(FHECostWarning):
        fhe_math.compile_gcd(0, 31, allow_large_lookup=True)

    with pytest.warns(FHECostWarning):
        fhe_math.compile_factorial(10)
