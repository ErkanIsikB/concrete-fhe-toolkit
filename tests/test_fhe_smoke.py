import os

import numpy as np
import pytest

from concrete_fhe_toolkit import (
    compile_argmin,
    compile_floor_divide,
    compile_sign,
    compile_sort,
)

pytestmark = [
    pytest.mark.fhe,
    pytest.mark.skipif(
        os.environ.get("RUN_FHE_TESTS") != "1",
        reason="set RUN_FHE_TESTS=1 to run real encrypted execution",
    ),
]


def test_real_encrypted_execution():
    sign_circuit = compile_sign(-3, 3)
    assert int(sign_circuit.encrypt_run_decrypt(3, -1)) == 1

    sort_circuit = compile_sort(4, 0, 3)
    sample = np.array([3, 0, 2, 1], dtype=np.int64)
    assert np.array_equal(sort_circuit.encrypt_run_decrypt(sample), [0, 1, 2, 3])

    argmin_circuit = compile_argmin(4, 0, 3)
    sample = np.array([2, 1, 1, 3], dtype=np.int64)
    assert int(argmin_circuit.encrypt_run_decrypt(sample)) == 1

    divide_circuit = compile_floor_divide(7, 7, zero_result=-1)
    assert int(divide_circuit.encrypt_run_decrypt(7, 3)) == 2
    assert int(divide_circuit.encrypt_run_decrypt(7, 0)) == -1
