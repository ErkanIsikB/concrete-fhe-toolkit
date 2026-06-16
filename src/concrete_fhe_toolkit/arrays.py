"""Fixed-size bounded array operations for Concrete FHE."""

from __future__ import annotations

from typing import Any, Callable, Literal, Optional

from concrete import fhe

from ._utils import (
    array_inputset,
    compile_function,
    positive_difference_lut,
    validate_bounds,
    validate_size,
)

TieBreak = Literal["first", "last"]
UnaryArrayFunction = Callable[[Any], Any]
BinaryScalarFunction = Callable[[Any, Any], Any]


def make_compare_swap(
    min_value: int = 0,
    max_value: int = 15,
) -> BinaryScalarFunction:
    """Create an ascending compare-swap function for bounded encrypted integers."""
    minimum, maximum = validate_bounds(min_value, max_value)
    span = maximum - minimum

    if span == 0:
        def compare_equal(x: Any, y: Any) -> Any:
            return x, y

        return compare_equal

    positive_difference = positive_difference_lut(span)

    def compare_swap(x: Any, y: Any) -> Any:
        positive = positive_difference[x - y + span]
        return x - positive, y + positive

    return compare_swap


def make_sort(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    descending: bool = False,
) -> UnaryArrayFunction:
    """Create a fixed-size bitonic sorting network."""
    size = validate_size(size, power_of_two=True)
    minimum, maximum = validate_bounds(min_value, max_value)
    compare_swap = make_compare_swap(minimum, maximum)

    def sort_values(x: Any) -> Any:
        values = [x[index] for index in range(size)]
        width = 2

        while width <= size:
            distance = width // 2
            while distance > 0:
                for left in range(size):
                    right = left ^ distance
                    if right <= left:
                        continue

                    low, high = compare_swap(values[left], values[right])
                    if left & width:
                        values[left], values[right] = high, low
                    else:
                        values[left], values[right] = low, high
                distance //= 2
            width *= 2

        if descending:
            values.reverse()
        return fhe.array(values)

    return sort_values


def _make_extreme(
    operation: Literal["min", "max"],
    size: int,
    min_value: int,
    max_value: int,
) -> UnaryArrayFunction:
    size = validate_size(size)
    minimum, maximum = validate_bounds(min_value, max_value)
    span = maximum - minimum

    if span == 0:
        def constant_extreme(x: Any) -> Any:
            return x[0]

        return constant_extreme

    positive_difference = positive_difference_lut(span)

    def extreme(x: Any) -> Any:
        layer = [x[index] for index in range(size)]
        while len(layer) > 1:
            next_layer = []
            for index in range(0, len(layer), 2):
                if index + 1 == len(layer):
                    next_layer.append(layer[index])
                    continue

                left = layer[index]
                right = layer[index + 1]
                positive = positive_difference[left - right + span]
                if operation == "min":
                    next_layer.append(left - positive)
                else:
                    next_layer.append(right + positive)
            layer = next_layer
        return layer[0]

    return extreme


def make_minimum(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
) -> UnaryArrayFunction:
    """Create a tournament reduction that returns the minimum value."""
    return _make_extreme("min", size, min_value, max_value)


def make_maximum(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
) -> UnaryArrayFunction:
    """Create a tournament reduction that returns the maximum value."""
    return _make_extreme("max", size, min_value, max_value)


def _validate_tie_break(tie_break: str) -> TieBreak:
    if tie_break not in {"first", "last"}:
        raise ValueError("tie_break must be 'first' or 'last'")
    return tie_break  # type: ignore[return-value]


def _make_arg_extreme(
    operation: Literal["min", "max"],
    size: int,
    min_value: int,
    max_value: int,
    tie_break: str,
) -> UnaryArrayFunction:
    size = validate_size(size)
    minimum, maximum = validate_bounds(min_value, max_value)
    normalized_tie_break = _validate_tie_break(tie_break)

    if size == 1:
        def only_index(x: Any) -> Any:
            return x[0] - x[0]

        return only_index

    value_span = maximum - minimum
    encoded_span = value_span * size + size - 1
    positive_difference = positive_difference_lut(encoded_span)

    direct_rank = (
        (operation == "min" and normalized_tie_break == "first")
        or (operation == "max" and normalized_tie_break == "last")
    )

    extraction_length = 1 << encoded_span.bit_length()
    extraction_values = []
    for encoded in range(extraction_length):
        rank = min(encoded, encoded_span) % size
        extraction_values.append(rank if direct_rank else size - 1 - rank)
    extract_index = fhe.LookupTable(extraction_values)

    def arg_extreme(x: Any) -> Any:
        layer = []
        for index in range(size):
            rank = index if direct_rank else size - 1 - index
            layer.append((x[index] - minimum) * size + rank)

        while len(layer) > 1:
            next_layer = []
            for index in range(0, len(layer), 2):
                if index + 1 == len(layer):
                    next_layer.append(layer[index])
                    continue

                left = layer[index]
                right = layer[index + 1]
                positive = positive_difference[left - right + encoded_span]
                if operation == "min":
                    next_layer.append(left - positive)
                else:
                    next_layer.append(right + positive)
            layer = next_layer

        return extract_index[layer[0]]

    return arg_extreme


def make_argmin(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    tie_break: TieBreak = "first",
) -> UnaryArrayFunction:
    """Create an argmin reduction with deterministic tie handling."""
    return _make_arg_extreme("min", size, min_value, max_value, tie_break)


def make_argmax(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    tie_break: TieBreak = "first",
) -> UnaryArrayFunction:
    """Create an argmax reduction with deterministic tie handling."""
    return _make_arg_extreme("max", size, min_value, max_value, tie_break)


def compile_compare_swap(
    min_value: int = 0,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile an ascending compare-swap circuit."""
    minimum, maximum = validate_bounds(min_value, max_value)
    function = make_compare_swap(minimum, maximum)
    inputset = [
        (minimum, minimum),
        (minimum, maximum),
        (maximum, minimum),
        (maximum, maximum),
    ]
    return compile_function(
        function,
        {"x": "encrypted", "y": "encrypted"},
        inputset,
        configuration,
    )


def _compile_array_function(
    function: UnaryArrayFunction,
    size: int,
    min_value: int,
    max_value: int,
    configuration: Optional[fhe.Configuration],
) -> fhe.Circuit:
    inputset = array_inputset(size, min_value, max_value)
    return compile_function(function, {"x": "encrypted"}, inputset, configuration)


def compile_sort(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    descending: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile a fixed-size bitonic sorting circuit."""
    size = validate_size(size, power_of_two=True)
    minimum, maximum = validate_bounds(min_value, max_value)
    function = make_sort(
        size,
        minimum,
        maximum,
        descending=descending,
    )
    return _compile_array_function(function, size, minimum, maximum, configuration)


def compile_minimum(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile a minimum reduction circuit."""
    size = validate_size(size)
    minimum, maximum = validate_bounds(min_value, max_value)
    function = make_minimum(size, minimum, maximum)
    return _compile_array_function(function, size, minimum, maximum, configuration)


def compile_maximum(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile a maximum reduction circuit."""
    size = validate_size(size)
    minimum, maximum = validate_bounds(min_value, max_value)
    function = make_maximum(size, minimum, maximum)
    return _compile_array_function(function, size, minimum, maximum, configuration)


def compile_argmin(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    tie_break: TieBreak = "first",
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile an argmin reduction circuit."""
    size = validate_size(size)
    minimum, maximum = validate_bounds(min_value, max_value)
    function = make_argmin(
        size,
        minimum,
        maximum,
        tie_break=tie_break,
    )
    return _compile_array_function(function, size, minimum, maximum, configuration)


def compile_argmax(
    size: int,
    min_value: int = 0,
    max_value: int = 15,
    *,
    tie_break: TieBreak = "first",
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile an argmax reduction circuit."""
    size = validate_size(size)
    minimum, maximum = validate_bounds(min_value, max_value)
    function = make_argmax(
        size,
        minimum,
        maximum,
        tie_break=tie_break,
    )
    return _compile_array_function(function, size, minimum, maximum, configuration)
