"""Scaled fixed-point approximations of common transcendental functions."""

from __future__ import annotations

from typing import Callable, Literal, Optional
import math

from concrete import fhe

from .._utils import validate_bounds, validate_integer
from ._lookup import UnaryFunction, compile_unary_lookup, make_unary_lookup, unary_values

AngleUnit = Literal["radians", "degrees"]


def _validate_scale(name: str, value: int) -> int:
    return validate_integer(name, value, minimum=1)


def _angle(value: float, angle_unit: AngleUnit) -> float:
    if angle_unit == "radians":
        return value
    if angle_unit == "degrees":
        return math.radians(value)
    raise ValueError("angle_unit must be 'radians' or 'degrees'")


def _scaled_values(
    name: str,
    function: Callable[[float], float],
    min_input: int,
    max_input: int,
    *,
    input_scale: int,
    output_scale: int,
    invalid_result: Optional[int] = None,
    domain: Optional[Callable[[float], bool]] = None,
) -> list[int]:
    minimum, maximum = validate_bounds(min_input, max_input)
    source = _validate_scale("input_scale", input_scale)
    target = _validate_scale("output_scale", output_scale)
    if invalid_result is not None:
        invalid = validate_integer("invalid_result", invalid_result)
    else:
        invalid = None

    def compute(encoded: int) -> int:
        real_input = encoded / source
        if domain is not None and not domain(real_input):
            if invalid is None:
                raise ValueError(
                    f"{name} domain excludes encoded input {encoded}; "
                    "pass invalid_result to define encrypted-domain behavior"
                )
            return invalid

        try:
            real_output = function(real_input)
        except ValueError:
            if invalid is None:
                raise
            return invalid
        except OverflowError as error:
            raise ValueError(f"{name} output overflowed for input {encoded}") from error

        if not math.isfinite(real_output):
            if invalid is None:
                raise ValueError(f"{name} output is not finite for input {encoded}")
            return invalid
        return round(real_output * target)

    return unary_values(compute, minimum, maximum)


def _make_scaled_unary(
    name: str,
    function: Callable[[float], float],
    min_input: int,
    max_input: int,
    *,
    input_scale: int,
    output_scale: int,
    invalid_result: Optional[int] = None,
    domain: Optional[Callable[[float], bool]] = None,
) -> UnaryFunction:
    values = _scaled_values(
        name,
        function,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=domain,
    )
    return make_unary_lookup(values, min_input)


def _compile_scaled_unary(
    name: str,
    function: Callable[[float], float],
    min_input: int,
    max_input: int,
    *,
    input_scale: int,
    output_scale: int,
    invalid_result: Optional[int],
    domain: Optional[Callable[[float], bool]],
    allow_large_lookup: bool,
    configuration: Optional[fhe.Configuration],
) -> fhe.Circuit:
    values = _scaled_values(
        name,
        function,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=domain,
    )
    return compile_unary_lookup(
        name,
        values,
        min_input,
        max_input,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_sin(
    min_input: int = 0,
    max_input: int = 628,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    angle_unit: AngleUnit = "radians",
) -> UnaryFunction:
    """Create scaled sin for encrypted fixed-point angles."""
    return _make_scaled_unary(
        "make_sin",
        lambda value: math.sin(_angle(value, angle_unit)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_sin(
    min_input: int = 0,
    max_input: int = 628,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    angle_unit: AngleUnit = "radians",
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled sin for encrypted fixed-point angles."""
    return _compile_scaled_unary(
        "compile_sin",
        lambda value: math.sin(_angle(value, angle_unit)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_cos(
    min_input: int = 0,
    max_input: int = 628,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    angle_unit: AngleUnit = "radians",
) -> UnaryFunction:
    """Create scaled cos for encrypted fixed-point angles."""
    return _make_scaled_unary(
        "make_cos",
        lambda value: math.cos(_angle(value, angle_unit)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_cos(
    min_input: int = 0,
    max_input: int = 628,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    angle_unit: AngleUnit = "radians",
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled cos for encrypted fixed-point angles."""
    return _compile_scaled_unary(
        "compile_cos",
        lambda value: math.cos(_angle(value, angle_unit)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_tan(
    min_input: int = -100,
    max_input: int = 100,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    angle_unit: AngleUnit = "radians",
) -> UnaryFunction:
    """Create scaled tan for encrypted fixed-point angles."""
    return _make_scaled_unary(
        "make_tan",
        lambda value: math.tan(_angle(value, angle_unit)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_tan(
    min_input: int = -100,
    max_input: int = 100,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    angle_unit: AngleUnit = "radians",
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled tan for encrypted fixed-point angles."""
    return _compile_scaled_unary(
        "compile_tan",
        lambda value: math.tan(_angle(value, angle_unit)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_exp(
    min_input: int = -50,
    max_input: int = 50,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
) -> UnaryFunction:
    """Create scaled exp for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_exp",
        math.exp,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_exp(
    min_input: int = -50,
    max_input: int = 50,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled exp for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_exp",
        math.exp,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_expm1(
    min_input: int = -50,
    max_input: int = 50,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
) -> UnaryFunction:
    """Create scaled expm1 for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_expm1",
        math.expm1,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_expm1(
    min_input: int = -50,
    max_input: int = 50,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled expm1 for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_expm1",
        math.expm1,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_log(
    min_input: int = 1,
    max_input: int = 1000,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    invalid_result: Optional[int] = None,
) -> UnaryFunction:
    """Create scaled natural log; invalid_result handles x <= 0 if needed."""
    return _make_scaled_unary(
        "make_log",
        math.log,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > 0,
    )


def compile_log(
    min_input: int = 1,
    max_input: int = 1000,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    invalid_result: Optional[int] = None,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled natural log; invalid_result handles x <= 0 if needed."""
    return _compile_scaled_unary(
        "compile_log",
        math.log,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > 0,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_log2(
    min_input: int = 1,
    max_input: int = 1024,
    *,
    input_scale: int = 1,
    output_scale: int = 100,
    invalid_result: Optional[int] = None,
) -> UnaryFunction:
    """Create scaled log2; invalid_result handles x <= 0 if needed."""
    return _make_scaled_unary(
        "make_log2",
        math.log2,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > 0,
    )


def compile_log2(
    min_input: int = 1,
    max_input: int = 1024,
    *,
    input_scale: int = 1,
    output_scale: int = 100,
    invalid_result: Optional[int] = None,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled log2; invalid_result handles x <= 0 if needed."""
    return _compile_scaled_unary(
        "compile_log2",
        math.log2,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > 0,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_log10(
    min_input: int = 1,
    max_input: int = 1000,
    *,
    input_scale: int = 1,
    output_scale: int = 100,
    invalid_result: Optional[int] = None,
) -> UnaryFunction:
    """Create scaled log10; invalid_result handles x <= 0 if needed."""
    return _make_scaled_unary(
        "make_log10",
        math.log10,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > 0,
    )


def compile_log10(
    min_input: int = 1,
    max_input: int = 1000,
    *,
    input_scale: int = 1,
    output_scale: int = 100,
    invalid_result: Optional[int] = None,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled log10; invalid_result handles x <= 0 if needed."""
    return _compile_scaled_unary(
        "compile_log10",
        math.log10,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > 0,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_log1p(
    min_input: int = 0,
    max_input: int = 1000,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    invalid_result: Optional[int] = None,
) -> UnaryFunction:
    """Create scaled log1p; invalid_result handles x <= -1 if needed."""
    return _make_scaled_unary(
        "make_log1p",
        math.log1p,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > -1,
    )


def compile_log1p(
    min_input: int = 0,
    max_input: int = 1000,
    *,
    input_scale: int = 100,
    output_scale: int = 1000,
    invalid_result: Optional[int] = None,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled log1p; invalid_result handles x <= -1 if needed."""
    return _compile_scaled_unary(
        "compile_log1p",
        math.log1p,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value > -1,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_sqrt(
    min_input: int = 0,
    max_input: int = 1000,
    *,
    input_scale: int = 100,
    output_scale: int = 100,
    invalid_result: Optional[int] = None,
) -> UnaryFunction:
    """Create scaled square root; invalid_result handles x < 0 if needed."""
    return _make_scaled_unary(
        "make_sqrt",
        math.sqrt,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value >= 0,
    )


def compile_sqrt(
    min_input: int = 0,
    max_input: int = 1000,
    *,
    input_scale: int = 100,
    output_scale: int = 100,
    invalid_result: Optional[int] = None,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled square root; invalid_result handles x < 0 if needed."""
    return _compile_scaled_unary(
        "compile_sqrt",
        math.sqrt,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=invalid_result,
        domain=lambda value: value >= 0,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_erf(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
) -> UnaryFunction:
    """Create scaled erf for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_erf",
        math.erf,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_erf(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled erf for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_erf",
        math.erf,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_erfc(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
) -> UnaryFunction:
    """Create scaled erfc for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_erfc",
        math.erfc,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_erfc(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled erfc for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_erfc",
        math.erfc,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_tanh(
    min_input: int = -40,
    max_input: int = 40,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
) -> UnaryFunction:
    """Create scaled tanh for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_tanh",
        math.tanh,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_tanh(
    min_input: int = -40,
    max_input: int = 40,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled tanh for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_tanh",
        math.tanh,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_sinh(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
) -> UnaryFunction:
    """Create scaled sinh for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_sinh",
        math.sinh,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_sinh(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled sinh for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_sinh",
        math.sinh,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_cosh(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
) -> UnaryFunction:
    """Create scaled cosh for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_cosh",
        math.cosh,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_cosh(
    min_input: int = -30,
    max_input: int = 30,
    *,
    input_scale: int = 10,
    output_scale: int = 100,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled cosh for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_cosh",
        math.cosh,
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )


def make_sigmoid(
    min_input: int = -60,
    max_input: int = 60,
    *,
    input_scale: int = 10,
    output_scale: int = 1000,
) -> UnaryFunction:
    """Create scaled logistic sigmoid for encrypted fixed-point inputs."""
    return _make_scaled_unary(
        "make_sigmoid",
        lambda value: 1 / (1 + math.exp(-value)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
    )


def compile_sigmoid(
    min_input: int = -60,
    max_input: int = 60,
    *,
    input_scale: int = 10,
    output_scale: int = 1000,
    allow_large_lookup: bool = False,
    configuration: Optional[fhe.Configuration] = None,
) -> fhe.Circuit:
    """Compile scaled logistic sigmoid for encrypted fixed-point inputs."""
    return _compile_scaled_unary(
        "compile_sigmoid",
        lambda value: 1 / (1 + math.exp(-value)),
        min_input,
        max_input,
        input_scale=input_scale,
        output_scale=output_scale,
        invalid_result=None,
        domain=None,
        allow_large_lookup=allow_large_lookup,
        configuration=configuration,
    )
