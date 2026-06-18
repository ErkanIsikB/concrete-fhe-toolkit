"""Bounded integer helpers for Concrete FHE."""

from .arithmetic import (
    compile_floor_divide,
    compile_floor_divide_by_product,
    compile_sign,
    make_floor_divide,
    make_floor_divide_by_product,
    sign,
)
from .arrays import (
    compile_argmax,
    compile_argmin,
    compile_compare_swap,
    compile_maximum,
    compile_minimum,
    compile_sort,
    make_argmax,
    make_argmin,
    make_compare_swap,
    make_maximum,
    make_minimum,
    make_sort,
)

__all__ = [
    "compile_argmax",
    "compile_argmin",
    "compile_compare_swap",
    "compile_floor_divide",
    "compile_floor_divide_by_product",
    "compile_maximum",
    "compile_minimum",
    "compile_sign",
    "compile_sort",
    "make_argmax",
    "make_argmin",
    "make_compare_swap",
    "make_floor_divide",
    "make_floor_divide_by_product",
    "make_maximum",
    "make_minimum",
    "make_sort",
    "sign",
]

__version__ = "0.1.3"
