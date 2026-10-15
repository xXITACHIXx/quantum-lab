"""
formulario/_masas.py — Masas isotópicas de los núclidos que aparecen en los ejercicios y calculadora de masa reducida.

Masas atómicas en unidades de masa atómica unificada (u), de la evaluación AME2020; abundancias naturales (IUPAC, %) donde son
significativas. La masa del átomo incluye a sus electrones.
"""

from __future__ import annotations

from scipy import constants as sc

# símbolo: (masa en u, abundancia natural en %)
ISOTOPOS = {
    "¹H": (1.00782503223, 99.9885),
    "²H (D)": (2.01410177812, 0.0115),
    "⁶Li": (6.0151228874, 7.59),
    "⁷Li": (7.0160034366, 92.41),
    "¹²C": (12.0, 98.93),
    "¹³C": (13.00335483507, 1.07),
    "¹⁴N": (14.00307400443, 99.636),
    "¹⁶O": (15.99491461957, 99.757),
    "¹⁹F": (18.99840316273, 100.0),
    "²³Na": (22.989769282, 100.0),
    "³²S": (31.9720711744, 94.99),
    "³⁵Cl": (34.968852682, 75.76),
    "³⁷Cl": (36.965902602, 24.24),
    "⁷⁹Br": (78.9183376, 50.69),
    "⁸¹Br": (80.9162897, 49.31),
    "¹²⁷I": (126.904472, 100.0),
}
U_KG = sc.physical_constants["atomic mass constant"][0]


def masa_reducida(m1: float, m2: float) -> float:
    """μ = m₁m₂/(m₁ + m₂), en las mismas unidades que las masas."""
    if m1 <= 0 or m2 <= 0:
        raise ValueError("Las masas deben ser positivas.")
    return m1 * m2 / (m1 + m2)


def en_kg(masa_u: float) -> float:
    return masa_u * U_KG
