from itertools import product

from concrete_fhe_toolkit import (
    make_floor_divide,
    make_floor_divide_by_product,
    sign,
)


def test_sign_exhaustive():
    for left, right in product(range(-5, 6), repeat=2):
        expected = (left > right) - (left < right)
        assert int(sign(left, right)) == expected


def test_floor_divide_exhaustive():
    floor_divide = make_floor_divide(zero_result=-1)

    for numerator, denominator in product(range(8), repeat=2):
        expected = -1 if denominator == 0 else numerator // denominator
        assert int(floor_divide(numerator, denominator)) == expected


def test_floor_divide_by_product_exhaustive():
    floor_divide = make_floor_divide_by_product(zero_result=-1)

    for numerator, left, right in product(range(5), repeat=3):
        denominator = left * right
        expected = -1 if denominator == 0 else numerator // denominator
        assert int(floor_divide(numerator, left, right)) == expected
