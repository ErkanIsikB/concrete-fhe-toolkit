import os
import math

import pytest

from concrete_fhe_toolkit import math as fhe_math

pytestmark = [
    pytest.mark.fhe,
    pytest.mark.skipif(
        os.environ.get("RUN_FHE_MATH_TESTS") != "1",
        reason="set RUN_FHE_MATH_TESTS=1 to run real encrypted math tests",
    ),
]


def test_real_encrypted_math_execution():
    add = fhe_math.compile_add(-5, 5, -5, 5)
    assert int(add.encrypt_run_decrypt(-3, 5)) == 2

    multiply = fhe_math.compile_multiply(-5, 5, -5, 5)
    assert int(multiply.encrypt_run_decrypt(-4, 3)) == -12

    absolute = fhe_math.compile_absolute(-8, 8)
    assert int(absolute.encrypt_run_decrypt(-7)) == 7

    gcd = fhe_math.compile_gcd(0, 8)
    assert int(gcd.encrypt_run_decrypt(6, 4)) == 2

    comb = fhe_math.compile_comb(6)
    assert int(comb.encrypt_run_decrypt(6, 3)) == math.comb(6, 3)

    trunc = fhe_math.compile_trunc(-50, 50, scale=10)
    assert int(trunc.encrypt_run_decrypt(-37)) == -3

    sin = fhe_math.compile_sin(
        0,
        90,
        input_scale=1,
        output_scale=100,
        angle_unit="degrees",
    )
    assert int(sin.encrypt_run_decrypt(30)) == 50

    sigmoid = fhe_math.compile_sigmoid(-30, 30, input_scale=10, output_scale=1000)
    assert int(sigmoid.encrypt_run_decrypt(0)) == 500

    floor_divide = fhe_math.compile_unsigned_floor_divide(3, 2, zero_result=7)
    assert int(floor_divide.encrypt_run_decrypt(7, 3)) == 2
    assert int(floor_divide.encrypt_run_decrypt(7, 0)) == 7

    fixed_divide = fhe_math.compile_fixed_point_divide(3, 2, fractional_bits=2)
    assert int(fixed_divide.encrypt_run_decrypt(3, 2)) == 6
