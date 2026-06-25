"""Shared lookup-table helpers and resource safeguards."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2
from typing import Any, Callable, Iterable, Optional, Sequence
import warnings

from concrete import fhe

from .._utils import compile_function, validate_bounds, validate_integer

UnaryFunction = Callable[[Any], Any]
BinaryFunction = Callable[[Any, Any], Any]


class FHECostWarning(UserWarning):
    """Warn that a lookup circuit may require substantial FHE resources."""


class LookupResourceError(ValueError):
    """Raised when a lookup requires explicit large-resource opt-in."""


@dataclass(frozen=True)
class LookupCost:
    """Static size indicators for a bounded lookup operation."""

    domain_size: int
    input_bit_width: int
    output_bit_width: int
    level: str


def _range_bit_width(minimum: int, maximum: int) -> int:
    if minimum >= 0:
        return max(1, maximum.bit_length())

    bits = 1
    while minimum < -(1 << (bits - 1)) or maximum > (1 << (bits - 1)) - 1:
        bits += 1
    return bits


def estimate_lookup_cost(
    domain_size: int,
    min_output: int,
    max_output: int,
) -> LookupCost:
    """Estimate lookup pressure from input-domain and output bit widths."""
    size = validate_integer("domain_size", domain_size, minimum=1)
    minimum, maximum = validate_bounds(min_output, max_output)
    input_bits = max(1, ceil(log2(size)))
    output_bits = _range_bit_width(minimum, maximum)

    if input_bits >= 10 or output_bits >= 28:
        level = "very-large"
    elif input_bits >= 8 or output_bits >= 20:
        level = "large"
    elif input_bits >= 7 or output_bits >= 12:
        level = "moderate"
    else:
        level = "small"

    return LookupCost(size, input_bits, output_bits, level)


def check_lookup_cost(
    name: str,
    values: Sequence[int],
    *,
    allow_large_lookup: bool,
) -> LookupCost:
    """Validate lookup outputs and require opt-in for very large circuits."""
    if not values:
        raise ValueError("lookup table must contain at least one value")

    normalized = [validate_integer("lookup output", value) for value in values]
    cost = estimate_lookup_cost(
        len(normalized),
        min(normalized),
        max(normalized),
    )
    message = (
        f"{name} uses a {cost.domain_size}-entry lookup with "
        f"{cost.input_bit_width}-bit indexing and "
        f"{cost.output_bit_width}-bit outputs. Concrete key generation and "
        "execution may require substantial memory and time."
    )

    if cost.level == "very-large" and not allow_large_lookup:
        raise LookupResourceError(
            f"{message} Pass allow_large_lookup=True to compile it explicitly."
        )

    if cost.level in {"large", "very-large"}:
        warnings.warn(message, FHECostWarning, stacklevel=3)

    return cost


def unary_values(
    function: Callable[[int], int],
    min_value: int,
    max_value: int,
) -> list[int]:
    """Evaluate an integer function over an inclusive bounded domain."""
    minimum, maximum = validate_bounds(min_value, max_value)
    return [
        validate_integer("lookup output", function(value))
        for value in range(minimum, maximum + 1)
    ]


def binary_values(
    function: Callable[[int, int], int],
    min_left: int,
    max_left: int,
    min_right: int,
    max_right: int,
) -> list[int]:
    """Flatten a bounded two-input integer function into row-major values."""
    left_minimum, left_maximum = validate_bounds(min_left, max_left)
    right_minimum, right_maximum = validate_bounds(min_right, max_right)
    return [
        validate_integer("lookup output", function(left, right))
        for left in range(left_minimum, left_maximum + 1)
        for right in range(right_minimum, right_maximum + 1)
    ]


def make_unary_lookup(values: Sequence[int], min_value: int) -> UnaryFunction:
    """Create a traceable unary lookup over values starting at min_value."""
    minimum = validate_integer("min_value", min_value)
    lookup = fhe.LookupTable(list(values))

    def operation(value: Any) -> Any:
        return lookup[value - minimum]

    return operation


def make_binary_lookup(
    values: Sequence[int],
    min_left: int,
    min_right: int,
    right_width: int,
) -> BinaryFunction:
    """Create a row-major traceable two-input lookup."""
    left_minimum = validate_integer("min_left", min_left)
    right_minimum = validate_integer("min_right", min_right)
    width = validate_integer("right_width", right_width, minimum=1)
    lookup = fhe.LookupTable(list(values))

    def operation(left: Any, right: Any) -> Any:
        index = (left - left_minimum) * width + (right - right_minimum)
        return lookup[index]

    return operation


def compile_unary_lookup(
    name: str,
    values: Sequence[int],
    min_value: int,
    max_value: int,
    *,
    allow_large_lookup: bool,
    configuration: Optional[fhe.Configuration],
) -> fhe.Circuit:
    """Compile a bounded unary lookup with resource checks."""
    minimum, maximum = validate_bounds(min_value, max_value)
    check_lookup_cost(name, values, allow_large_lookup=allow_large_lookup)
    operation = make_unary_lookup(values, minimum)
    return compile_function(
        operation,
        {"value": "encrypted"},
        list(range(minimum, maximum + 1)),
        configuration,
    )


def compile_binary_lookup(
    name: str,
    values: Sequence[int],
    min_left: int,
    max_left: int,
    min_right: int,
    max_right: int,
    *,
    allow_large_lookup: bool,
    configuration: Optional[fhe.Configuration],
) -> fhe.Circuit:
    """Compile a bounded row-major two-input lookup with resource checks."""
    left_minimum, left_maximum = validate_bounds(min_left, max_left)
    right_minimum, right_maximum = validate_bounds(min_right, max_right)
    width = right_maximum - right_minimum + 1
    check_lookup_cost(name, values, allow_large_lookup=allow_large_lookup)
    operation = make_binary_lookup(
        values,
        left_minimum,
        right_minimum,
        width,
    )
    inputset = [
        (left, right)
        for left in range(left_minimum, left_maximum + 1)
        for right in range(right_minimum, right_maximum + 1)
    ]
    return compile_function(
        operation,
        {"left": "encrypted", "right": "encrypted"},
        inputset,
        configuration,
    )


def combined_lookup_values(*tables: Iterable[int]) -> list[int]:
    """Combine output tables for one conservative resource-cost check."""
    return [validate_integer("lookup output", value) for table in tables for value in table]
