import numpy as np

from concrete_fhe_toolkit import (
    compile_argmax,
    compile_argmin,
    compile_compare_swap,
    compile_floor_divide,
    compile_floor_divide_by_product,
    compile_maximum,
    compile_minimum,
    compile_sign,
    compile_sort,
)


def test_sign_compiles_and_simulates():
    circuit = compile_sign(-7, 7)

    assert int(circuit.simulate(7, -3)) == 1
    assert int(circuit.simulate(-3, 7)) == -1
    assert int(circuit.simulate(4, 4)) == 0


def test_sign_bounds_do_not_need_to_include_zero():
    circuit = compile_sign(10, 20)

    assert int(circuit.simulate(20, 10)) == 1
    assert int(circuit.simulate(10, 20)) == -1
    assert int(circuit.simulate(15, 15)) == 0


def test_compare_swap_compiles_and_simulates():
    circuit = compile_compare_swap(-2, 3)

    assert tuple(circuit.simulate(3, -2)) == (-2, 3)
    assert tuple(circuit.simulate(-1, 2)) == (-1, 2)


def test_sort_compiles_and_simulates():
    circuit = compile_sort(4, -2, 3)
    descending_circuit = compile_sort(4, -2, 3, descending=True)
    sample = np.array([3, -2, 1, 0], dtype=np.int64)

    assert np.array_equal(circuit.simulate(sample), [-2, 0, 1, 3])
    assert np.array_equal(descending_circuit.simulate(sample), [3, 1, 0, -2])


def test_reductions_compile_and_simulate():
    sample = np.array([2, -1, 3, -1, 0], dtype=np.int64)

    minimum = compile_minimum(5, -1, 3)
    maximum = compile_maximum(5, -1, 3)
    argmin = compile_argmin(5, -1, 3)
    argmax = compile_argmax(5, -1, 3)
    last_argmin = compile_argmin(5, -1, 3, tie_break="last")
    last_argmax = compile_argmax(5, -1, 3, tie_break="last")

    assert int(minimum.simulate(sample)) == -1
    assert int(maximum.simulate(sample)) == 3
    assert int(argmin.simulate(sample)) == 1
    assert int(argmax.simulate(sample)) == 2
    assert int(last_argmin.simulate(sample)) == 3

    duplicate_maximum = np.array([3, -1, 2, -1, 3], dtype=np.int64)
    assert int(last_argmax.simulate(duplicate_maximum)) == 4


def test_floor_divide_compiles_and_simulates():
    circuit = compile_floor_divide(7, 7, zero_result=-1)

    assert int(circuit.simulate(7, 1)) == 7
    assert int(circuit.simulate(7, 3)) == 2
    assert int(circuit.simulate(7, 0)) == -1


def test_floor_divide_by_product_compiles_and_simulates():
    circuit = compile_floor_divide_by_product(7, 3, 3, zero_result=-1)

    assert int(circuit.simulate(6, 2, 3)) == 1
    assert int(circuit.simulate(7, 1, 1)) == 7
    assert int(circuit.simulate(7, 0, 1)) == -1
