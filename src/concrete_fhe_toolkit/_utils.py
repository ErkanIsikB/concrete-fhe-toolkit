"""Internal validation and inputset helpers."""

from __future__ import annotations

from numbers import Integral
from typing import Any, List, Optional, Tuple

import numpy as np
from concrete import fhe


def validate_integer(name: str, value: int, minimum: Optional[int] = None) -> int:
    """Validate and normalize an integer argument."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer")

    normalized = int(value)
    if minimum is not None and normalized < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return normalized


def validate_bounds(min_value: int, max_value: int) -> Tuple[int, int]:
    """Validate inclusive integer bounds."""
    minimum = validate_integer("min_value", min_value)
    maximum = validate_integer("max_value", max_value)
    if minimum > maximum:
        raise ValueError("min_value must be less than or equal to max_value")
    return minimum, maximum


def validate_size(size: int, *, power_of_two: bool = False) -> int:
    """Validate a fixed circuit input size."""
    normalized = validate_integer("size", size, minimum=1)
    if power_of_two and normalized & (normalized - 1):
        raise ValueError("size must be a power of two")
    return normalized


def positive_difference_lut(span: int) -> fhe.LookupTable:
    """Return a LUT for max(value, 0), where value is in [-span, span]."""
    span = validate_integer("span", span, minimum=1)
    required_length = 2 * span + 1
    table_length = 1 << (required_length - 1).bit_length()
    values = [
        min(max(index - span, 0), span)
        for index in range(table_length)
    ]
    return fhe.LookupTable(values)


def array_inputset(size: int, min_value: int, max_value: int) -> List[np.ndarray]:
    """Create a compact inputset that includes all important array boundaries."""
    low = np.full(size, min_value, dtype=np.int64)
    high = np.full(size, max_value, dtype=np.int64)
    probes = []
    for index in range(size):
        high_probe = low.copy()
        high_probe[index] = max_value
        probes.append(high_probe)

        low_probe = high.copy()
        low_probe[index] = min_value
        probes.append(low_probe)

    alternating = np.array(
        [min_value if index % 2 == 0 else max_value for index in range(size)],
        dtype=np.int64,
    )
    reverse_alternating = alternating[::-1].copy()
    ramp = np.linspace(min_value, max_value, num=size, dtype=np.int64)
    reverse_ramp = ramp[::-1].copy()
    return [
        low,
        high,
        *probes,
        alternating,
        reverse_alternating,
        ramp,
        reverse_ramp,
    ]


def compile_function(
    function: Any,
    parameter_encryption: dict,
    inputset: list,
    configuration: Optional[fhe.Configuration],
) -> fhe.Circuit:
    """Compile a function while keeping configuration optional."""
    compiler = fhe.Compiler(function, parameter_encryption)
    if configuration is None:
        return compiler.compile(inputset)
    return compiler.compile(inputset, configuration=configuration)
