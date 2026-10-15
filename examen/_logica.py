"""
examen/_logica.py — Reglas del modo examen (sin Streamlit, probadas con pytest).

Selección reproducible de ejercicios, duración sugerida, nota sobre 5.0 y formato del tiempo restante.
"""

from __future__ import annotations

import random

ESCALA = 5.0                      # escala de calificación: 0.0 a 5.0
MINUTOS_POR_EJERCICIO = 10
MIN_EJERCICIOS, MAX_EJERCICIOS = 3, 12
MIN_MINUTOS, MAX_MINUTOS = 10, 240


def seleccionar(candidatos, n: int, semilla) -> list[str]:
    """`n` ids al azar entre los candidatos. La misma semilla y los mismos candidatos dan siempre el mismo examen."""
    base = sorted(candidatos)
    n = max(0, min(n, len(base)))
    return random.Random(str(semilla)).sample(base, n)


def duracion_sugerida(n: int) -> int:
    """Minutos sugeridos: 10 por ejercicio, en múltiplos de 5 y dentro de los límites del control."""
    return int(min(max(MINUTOS_POR_EJERCICIO * n, MIN_MINUTOS), MAX_MINUTOS))


def nota(fracciones) -> tuple[float, float]:
    """(nota sobre 5.0, porcentaje) con todos los ejercicios del mismo peso. Sin ejercicios: (0.0, 0.0)."""
    fracciones = list(fracciones)
    if not fracciones:
        return 0.0, 0.0
    media = sum(fracciones) / len(fracciones)
    return ESCALA * media, 100.0 * media


def restante(inicio: float, duracion: float, ahora: float) -> float:
    """Segundos que quedan (nunca negativos)."""
    return max(0.0, duracion - (ahora - inicio))


def formato_tiempo(segundos: float) -> str:
    """mm:ss, o h:mm:ss si pasa de una hora. El tiempo se redondea hacia arriba para no mostrar 00:00 antes de acabar."""
    s = int(-(-max(segundos, 0) // 1))
    h, resto = divmod(s, 3600)
    m, s = divmod(resto, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def veredicto(fraccion: float, respondidas: int) -> str:
    """Estado de un ejercicio en la corrección."""
    if fraccion >= 0.999:
        return "Correcto"
    if respondidas == 0:
        return "Sin responder"
    return "Parcial" if fraccion > 0 else "Incorrecto"
