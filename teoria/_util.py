"""
teoria/_util.py — utilidades compartidas por los módulos de teoría (figuras y constantes).
"""

import matplotlib.pyplot as plt
from scipy import constants as const

import quantum_lab_comun as qc

H = const.h
HBAR = const.hbar
C = const.c
KB = const.k
EV = const.e
ME = const.m_e
SIGMA = const.sigma
COL = qc.COLORES


def figura(ancho: float = 9.0, alto: float = 4.2, filas: int = 1, columnas: int = 1):
    """Figura con el estilo del laboratorio (el tema de Matplotlib ya lo fija quantum_lab_comun)."""
    fig, ejes = plt.subplots(filas, columnas, figsize=(ancho, alto), constrained_layout=True)
    return fig, ejes


def dibujar(fig, archivo: str | None = None) -> None:
    qc.mostrar_pyplot(fig, archivo=archivo)


def cifras(x: float, n: int = 4) -> str:
    """Número con n cifras significativas (notación científica cuando conviene)."""
    return f"{x:.{n}g}"
