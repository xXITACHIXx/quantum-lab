"""
talleres/_modelo.py — Modelo de datos de los talleres: Datos, Parte, Pregunta, Taller y la calificación de una pregunta.

Un taller es una función `construir(datos) -> list[Pregunta]`: así cada intento puede usar valores distintos (otra molécula,
otro número cuántico) y el valor esperado y la solución se calculan con esos mismos valores.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from talleres._calificar import CASI, MAL, OK, VACIA, Resultado, evaluar, evaluar_opcion

NUM = "numerica"
OPC = "opcion"


def tex(x: float, cifras: int = 4) -> str:
    """Número para fórmulas LaTeX: 1.256\\times10^{12} para valores muy grandes o pequeños, decimal en los demás."""
    if x == 0:
        return "0"
    if abs(x) >= 1e5 or abs(x) < 1e-3:
        mant, exp = f"{x:.{cifras - 1}e}".split("e")
        mant = mant.rstrip("0").rstrip(".") if "." in mant else mant
        return rf"{mant}\times10^{{{int(exp)}}}"
    return f"{x:.{cifras}g}"


class Datos:
    """Origen de los valores de un intento: los del enunciado original o unos nuevos (semilla reproducible)."""

    def __init__(self, original: bool = True, semilla: str = "0"):
        self.original = original
        self.rng = random.Random(semilla)

    def elegir(self, original, alternativas):
        """El valor del taller original, o uno de `alternativas` (que incluye al original)."""
        alternativas = list(alternativas)
        return original if self.original else self.rng.choice(alternativas)


@dataclass(frozen=True)
class Parte:
    clave: str
    etiqueta: str                       # enunciado de la parte (Markdown con $…$)
    tipo: str = NUM
    esperado: float = 0.0               # NUM
    unidad: str = ""                    # NUM: se muestra junto al campo
    tol_rel: float = 0.02
    tol_abs: float = 0.0
    confusiones: tuple = ()             # NUM: ((factor, mensaje), …)
    opciones: tuple = ()                # OPC
    correcta: int = 0                   # OPC: índice
    peso: float = 1.0
    explicacion: str = ""               # por qué es la respuesta (Markdown)

    def respuesta_correcta(self) -> str:
        if self.tipo == OPC:
            return self.opciones[self.correcta]
        return f"{self.esperado:.4g} {self.unidad}".strip()


@dataclass(frozen=True)
class Pregunta:
    id: str
    enunciado: str                      # Markdown
    puntos: float
    partes: tuple
    solucion: str                       # Markdown con la solución completa
    tema: str = ""                      # id del tema del Centro de teoría relacionado
    nota: str = ""                      # aclaración sobre datos añadidos o lecturas del enunciado


@dataclass(frozen=True)
class Taller:
    id: str
    titulo: str
    resumen: str
    contenidos: tuple                   # temas que cubre (texto corto)
    construir: Callable = field(compare=False, default=None)
    variable: bool = True               # ¿admite «datos nuevos»?
    n_preguntas: int = 0                # se contrasta con construir() en las pruebas
    puntos: float = 0.0
    origen: str = "Basado en un taller de un semestre anterior; enunciados reescritos."


@dataclass(frozen=True)
class Calificacion:
    resultados: dict                    # clave de parte → Resultado
    puntos: float
    maximo: float

    @property
    def fraccion(self) -> float:
        return self.puntos / self.maximo if self.maximo else 0.0


def calificar(pregunta: Pregunta, respuestas: dict) -> Calificacion:
    """Califica las respuestas (clave de parte → texto u opción elegida). Cada parte aporta su peso proporcional."""
    total = sum(p.peso for p in pregunta.partes)
    resultados, ganado = {}, 0.0
    for p in pregunta.partes:
        r = respuestas.get(p.clave)
        if p.tipo == OPC:
            res = evaluar_opcion(r, p.correcta, p.opciones)
        else:
            res = evaluar(r, p.esperado, p.tol_rel, p.tol_abs, p.confusiones)
        resultados[p.clave] = res
        if res.estado == OK:
            ganado += p.peso
    return Calificacion(resultados, pregunta.puntos * ganado / total, pregunta.puntos)
