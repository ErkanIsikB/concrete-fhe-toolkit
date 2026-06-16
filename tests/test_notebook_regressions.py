import os

import numpy as np
import pytest

from concrete_fhe_toolkit import (
    compile_argmax,
    compile_argmin,
    compile_floor_divide_by_product,
    compile_maximum,
    compile_minimum,
    compile_sort,
)

pytestmark = [
    pytest.mark.fhe,
    pytest.mark.skipif(
        os.environ.get("RUN_FHE_NOTEBOOK_TESTS") != "1",
        reason="set RUN_FHE_NOTEBOOK_TESTS=1 to run notebook-sized FHE tests",
    ),
]


def test_notebook_sized_encrypted_regressions():
    sort_values = np.array([12, 3, 7, 1, 15, 0, 4, 9], dtype=np.int64)
    extrema_values = np.array([12, 5, 7, 1, 15, 9, 4, 14], dtype=np.int64)

    sort_circuit = compile_sort(8, 0, 15)
    assert np.array_equal(
        sort_circuit.encrypt_run_decrypt(sort_values),
        [0, 1, 3, 4, 7, 9, 12, 15],
    )

    minimum_circuit = compile_minimum(8, 0, 15)
    maximum_circuit = compile_maximum(8, 0, 15)
    assert int(minimum_circuit.encrypt_run_decrypt(extrema_values)) == 1
    assert int(maximum_circuit.encrypt_run_decrypt(extrema_values)) == 15

    argmin_circuit = compile_argmin(8, 0, 15)
    argmax_circuit = compile_argmax(8, 0, 15)
    assert int(argmin_circuit.encrypt_run_decrypt(extrema_values)) == 3
    assert int(argmax_circuit.encrypt_run_decrypt(extrema_values)) == 4

    division_circuit = compile_floor_divide_by_product(15, 5, 5, zero_result=-1)
    assert int(division_circuit.encrypt_run_decrypt(6, 2, 3)) == 1
    assert int(division_circuit.encrypt_run_decrypt(15, 0, 3)) == -1
