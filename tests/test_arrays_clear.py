from itertools import product

import numpy as np
import pytest

from concrete_fhe_toolkit import (
    make_argmax,
    make_argmin,
    make_compare_swap,
    make_maximum,
    make_minimum,
    make_sort,
)


def test_compare_swap_exhaustive():
    compare_swap = make_compare_swap(-2, 3)

    for left, right in product(range(-2, 4), repeat=2):
        assert tuple(compare_swap(left, right)) == (
            min(left, right),
            max(left, right),
        )


@pytest.mark.parametrize("descending", [False, True])
def test_sort_exhaustive(descending):
    sort_values = make_sort(4, -2, 2, descending=descending)

    for values in product(range(-2, 3), repeat=4):
        actual = sort_values(np.array(values, dtype=np.int64))
        expected = sorted(values, reverse=descending)
        assert np.array_equal(actual, expected)


def test_minimum_and_maximum_support_odd_sizes():
    values = np.array([3, -2, 7, -2, 4], dtype=np.int64)

    assert int(make_minimum(5, -2, 7)(values)) == -2
    assert int(make_maximum(5, -2, 7)(values)) == 7


@pytest.mark.parametrize(
    ("factory", "tie_break", "expected"),
    [
        (make_argmin, "first", 1),
        (make_argmin, "last", 2),
        (make_argmax, "first", 0),
        (make_argmax, "last", 4),
    ],
)
def test_arg_extrema_have_explicit_tie_behavior(factory, tie_break, expected):
    values = np.array([3, 1, 1, 2, 3], dtype=np.int64)
    function = factory(5, 1, 3, tie_break=tie_break)

    assert int(function(values)) == expected


def test_arg_extrema_support_single_element_arrays():
    values = np.array([-4], dtype=np.int64)

    assert int(make_argmin(1, -4, -4)(values)) == 0
    assert int(make_argmax(1, -4, -4)(values)) == 0


def test_invalid_arguments_are_rejected():
    with pytest.raises(ValueError, match="power of two"):
        make_sort(3)

    with pytest.raises(ValueError, match="min_value"):
        make_minimum(4, 3, 2)

    with pytest.raises(ValueError, match="tie_break"):
        make_argmin(4, tie_break="middle")
