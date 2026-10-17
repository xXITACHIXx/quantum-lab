"""solucionador/_modelo.py — Estructura de una solución paso a paso y utilidades de formato."""

from __future__ import annotations

from dataclasses import dataclass, field

from biblioteca._modelo import Paso


@dataclass(frozen=True)
class Solucion:
    """Resultado completo de un problema: ecuaciones, datos, pasos con sustitución numérica, resultados e interpretación."""
    titulo: str
    ecuaciones: tuple          # ((nombre, latex), ...)
    datos: tuple               # (latex, ...) magnitudes conocidas con su unidad
    pasos: tuple               # (Paso(texto, latex), ...): sustitución numérica con unidades
    resultados: tuple          # ((nombre, latex_con_unidad), ...)
    interpretacion: str
    avisos: tuple = ()
    valores: dict = field(default_factory=dict)   # valores numéricos en SI (para pruebas y para reutilizar)


def num(v: float, cifras: int = 4) -> str:
    """Número en LaTeX: decimal si es de tamaño moderado y notación científica si no (4 cifras significativas)."""
    if v == 0:
        return "0"
    if 1e-2 <= abs(v) < 1e5:
        s = f"{v:.{cifras}g}"
        if "e" not in s:
            return s
    mant, exp = f"{v:.{cifras - 1}e}".split("e")
    if "." in mant:
        mant = mant.rstrip("0").rstrip(".")
    return mant if int(exp) == 0 else rf"{mant}\times10^{{{int(exp)}}}"


def con_unidad(v: float, unidad: str, cifras: int = 4) -> str:
    return rf"{num(v, cifras)}\ \mathrm{{{unidad}}}" if unidad else num(v, cifras)


__all__ = ["Solucion", "Paso", "num", "con_unidad"]
