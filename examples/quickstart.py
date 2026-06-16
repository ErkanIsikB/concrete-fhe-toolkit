import numpy as np

from concrete_fhe_toolkit import compile_argmin, compile_sort


sort_circuit = compile_sort(size=8, min_value=0, max_value=15)
values = np.array([12, 3, 7, 1, 15, 0, 4, 9], dtype=np.int64)
print(sort_circuit.encrypt_run_decrypt(values))

argmin_circuit = compile_argmin(size=8, min_value=0, max_value=15)
print(argmin_circuit.encrypt_run_decrypt(values))
