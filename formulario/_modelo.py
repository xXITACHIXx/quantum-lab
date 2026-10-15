"""
formulario/_modelo.py — Estructuras del formulario: una fórmula, un bloque temático y una sección.

Cada fórmula puede traer un `contraste`: una función sin argumentos que devuelve (valor calculado con la propia expresión, valor de
referencia independiente). Las pruebas comprueban que ambos coincidan dentro de `tol`, de modo que lo escrito en pantalla no sea
solo texto sino una expresión verificada numéricamente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Formula:
    nombre: str
    latex: str                                   # expresión en LaTeX (sin delimitadores)
    nota: str = ""                               # definición de los símbolos, unidades y condiciones de validez (Markdown)
    contraste: Callable | None = None            # () -> (calculado, referencia)
    tol: float = 1e-6                            # tolerancia relativa del contraste


@dataclass(frozen=True)
class Bloque:
    titulo: str
    formulas: tuple


@dataclass(frozen=True)
class Seccion:
    id: str                                      # id del tema (Centro de teoría) o «matematicas»
    titulo: str
    resumen: str
    bloques: tuple
    teoria: str = ""                             # id del tema del Centro de teoría que la explica ("" si no hay)

    def todas(self) -> list[Formula]:
        return [f for b in self.bloques for f in b.formulas]


def F(nombre: str, latex: str, nota: str = "", contraste: Callable | None = None, tol: float = 1e-6) -> Formula:
    return Formula(nombre, latex, nota, contraste, tol)
