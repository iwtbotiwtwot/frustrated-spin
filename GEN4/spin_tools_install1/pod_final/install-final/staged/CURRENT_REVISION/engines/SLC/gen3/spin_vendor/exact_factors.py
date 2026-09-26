"""Unchanged retained exact arithmetic definitions; see MANIFEST.json."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
import numpy as np
PRIMITIVE_ROOT = 3
class SLCX032ArithmeticError(ValueError): pass

def _weighted_edges(instance: Mapping[str, Any]) -> list[tuple[int, int, int]]:
    return [(int(u), int(v), int(coupling)) for u, v, coupling in instance["edges"]]

@dataclass(frozen=True)
class _Factor:
    scope: tuple[int, ...]
    values: np.ndarray

def _root_power_table(points: np.ndarray, maximum_power: int, prime: int) -> np.ndarray:
    table = np.empty((maximum_power + 1, len(points)), dtype=np.int64)
    table[0, :] = 1
    for exponent in range(1, maximum_power + 1):
        table[exponent, :] = (table[exponent - 1, :] * points) % prime
    return table

def _initial_factors(
    instance: Mapping[str, Any],
    points: np.ndarray,
    prime: int,
) -> list[_Factor]:
    maximum_power = max(
        [2 * abs(int(value)) for value in instance["fields"]]
        + [2 * abs(coupling) for _, _, coupling in _weighted_edges(instance)]
        + [0]
    )
    powers = _root_power_table(points, maximum_power, prime)
    factors: list[_Factor] = []
    for vertex, raw_field in enumerate(instance["fields"]):
        field = int(raw_field)
        exponents = []
        for bit in (0, 1):
            spin = 1 if bit else -1
            exponents.append(-field * spin + abs(field))
        values = np.stack([powers[exponent, :] for exponent in exponents], axis=0)
        factors.append(_Factor((vertex,), np.ascontiguousarray(values, dtype=np.int64)))
    for u, v, coupling in _weighted_edges(instance):
        exponents = []
        for assignment in range(4):
            left_spin = 1 if assignment & 1 else -1
            right_spin = 1 if assignment & 2 else -1
            exponents.append(-coupling * left_spin * right_spin + abs(coupling))
        values = np.stack([powers[exponent, :] for exponent in exponents], axis=0)
        factors.append(_Factor((u, v), np.ascontiguousarray(values, dtype=np.int64)))
    return factors

def _project_indices(assignments: np.ndarray, union_scope: tuple[int, ...], factor_scope: tuple[int, ...]) -> np.ndarray:
    positions = {vertex: index for index, vertex in enumerate(union_scope)}
    result = np.zeros(len(assignments), dtype=np.uint64)
    for factor_position, vertex in enumerate(factor_scope):
        result |= ((assignments >> positions[vertex]) & 1) << factor_position
    return result.astype(np.intp, copy=False)

def _zeta_points(prime: int, y_length: int, start: int, stop: int) -> np.ndarray:
    z_order = 2 * y_length
    if y_length <= 0 or y_length & (y_length - 1) or (prime - 1) % z_order:
        raise SLCX032ArithmeticError("prime does not support the required even-quotient root order")
    zeta = pow(PRIMITIVE_ROOT, (prime - 1) // z_order, prime)
    if pow(zeta, z_order, prime) != 1 or pow(zeta, z_order // 2, prime) == 1:
        raise SLCX032ArithmeticError("derived zeta lacks exact order 2L")
    omega = zeta * zeta % prime
    expected_omega = pow(PRIMITIVE_ROOT, (prime - 1) // y_length, prime)
    if omega != expected_omega:
        raise SLCX032ArithmeticError("zeta squared does not equal the canonical y root")
    return np.asarray([pow(zeta, index, prime) for index in range(start, stop)], dtype=np.int64)
