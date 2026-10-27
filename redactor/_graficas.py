"""
redactor/_graficas.py — Gráficas que construye el estudiante: funciones y = f(x) y tablas de datos
==================================================================================================

Las expresiones se leen con `redactor._expr` (lista blanca). Las figuras usan fondo blanco (se imprimen bien) y ejes rotulados
por quien las crea. Cualquier problema (variable sin valor, dominio complejo, datos insuficientes) se explica en español.

Tablas de datos: una fila por línea; columnas separadas por espacios, tabuladores o «;». La coma es decimal («1,5»); si la
línea no tiene espacios ni «;» y hay una sola coma, separa x de y («1,2»). Las líneas que empiezan con «#» se ignoran.
Una tercera columna opcional es la incertidumbre de y (barras de error).
"""

from __future__ import annotations

import math
import re

import numpy as np
import sympy as sp

from redactor._expr import ErrorExpresion, leer_expresion
from talleres._calificar import leer_numero

MAX_SERIES = 6
PUNTOS_CURVA = 800
MAX_FILAS_DATOS = 2000
COLORES = ("#1F3A93", "#B03A2E", "#1E8449", "#7D3C98", "#CA6F1E", "#117A8B")


class ErrorGrafica(ValueError):
    """No se pudo construir la gráfica; el mensaje explica por qué."""


def _plt():
    import matplotlib
    matplotlib.use("Agg", force=False)
    import matplotlib.pyplot as plt
    return plt


# ---------------------------------------------------------------------
# Constantes y funciones
# ---------------------------------------------------------------------
def leer_constantes(texto: str) -> dict[str, float]:
    """«a = 1e-9» (una por línea o separadas por «;») → {'a': 1e-9}."""
    salida = {}
    for linea in re.split(r"[\n;]", texto or ""):
        if not linea.strip():
            continue
        if linea.count("=") != 1:
            raise ErrorGrafica(f"Constante mal escrita: «{linea.strip()}». Usa el formato nombre = valor.")
        nombre, valor = (p.strip() for p in linea.split("="))
        try:
            simbolo = leer_expresion(nombre)
            if not isinstance(simbolo, sp.Symbol):
                raise ErrorGrafica(f"«{nombre}» no es un nombre de variable válido.")
            salida[simbolo.name] = leer_numero(valor)
        except ErrorExpresion as error:
            raise ErrorGrafica(f"Constante «{nombre}»: {error}") from None
        except ValueError as error:
            if isinstance(error, ErrorGrafica):
                raise
            raise ErrorGrafica(f"Valor de «{nombre}»: {error}") from None
    return salida


def evaluar_funciones(expresiones: str, variable: str, xmin: float, xmax: float, constantes: dict[str, float]):
    """[(etiqueta, x, y)] para cada línea de `expresiones`. y es NaN donde la función no es real o no está definida."""
    if not (math.isfinite(xmin) and math.isfinite(xmax)) or xmin >= xmax:
        raise ErrorGrafica("El intervalo debe cumplir xmin < xmax con valores finitos.")
    try:
        var = leer_expresion(variable)
    except ErrorExpresion as error:
        raise ErrorGrafica(f"Variable independiente: {error}") from None
    if not isinstance(var, sp.Symbol):
        raise ErrorGrafica("La variable independiente debe ser un nombre como x o t.")
    lineas = [ln.strip() for ln in (expresiones or "").splitlines() if ln.strip()]
    if not lineas:
        raise ErrorGrafica("Escribe al menos una expresión para graficar.")
    if len(lineas) > MAX_SERIES:
        raise ErrorGrafica(f"Se pueden graficar hasta {MAX_SERIES} curvas a la vez.")
    x = np.linspace(xmin, xmax, PUNTOS_CURVA)
    curvas = []
    for ln in lineas:
        etiqueta, texto = (ln.split("=", 1) if "=" in ln else (ln, ln))
        etiqueta, texto = etiqueta.strip(), texto.strip()
        try:
            expr = leer_expresion(texto)
        except ErrorExpresion as error:
            raise ErrorGrafica(f"«{ln}»: {error}") from None
        sin_valor = sorted(s.name for s in expr.free_symbols if s != var and s.name not in constantes)
        if sin_valor:
            raise ErrorGrafica(f"«{ln}»: falta el valor de {', '.join(sin_valor)}. Escríbelo en «Constantes» (por ejemplo {sin_valor[0]} = 1).")
        sustituciones = {s: constantes[s.name] for s in expr.free_symbols if s != var}
        f = sp.lambdify(var, expr.subs(sustituciones), modules="numpy")
        with np.errstate(all="ignore"):
            try:
                y = np.asarray(f(x), dtype=complex) * np.ones_like(x)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                raise ErrorGrafica(f"«{ln}»: no se pudo evaluar en ese intervalo.") from None
        real = np.where(np.abs(y.imag) <= 1e-9 * np.maximum(1.0, np.abs(y.real)), y.real, np.nan)
        real = np.where(np.isfinite(real), real, np.nan)
        if not np.isfinite(real).any():
            raise ErrorGrafica(f"«{ln}» no toma valores reales finitos en [{xmin:g}, {xmax:g}].")
        curvas.append((etiqueta, x, real))
    return curvas


def grafica_funcion(expresiones: str, variable: str, xmin: float, xmax: float, constantes: str,
                    titulo: str = "", xlabel: str = "", ylabel: str = ""):
    """Figura de Matplotlib (fondo blanco) con las curvas pedidas."""
    curvas = evaluar_funciones(expresiones, variable, xmin, xmax, leer_constantes(constantes))
    plt = _plt()
    with plt.style.context("default"):
        fig, ax = plt.subplots(figsize=(6.0, 3.4), facecolor="white")
        for i, (etiqueta, x, y) in enumerate(curvas):
            ax.plot(x, y, color=COLORES[i % len(COLORES)], lw=1.6, label=etiqueta)
        ax.axhline(0, color="#888888", lw=0.6)
        ax.set(xlabel=xlabel or variable, ylabel=ylabel, title=titulo)
        ax.grid(alpha=0.3)
        if len(curvas) > 1:
            ax.legend(fontsize=8)
        fig.tight_layout()
    return fig


# ---------------------------------------------------------------------
# Tablas de datos
# ---------------------------------------------------------------------
def leer_tabla(texto: str) -> np.ndarray:
    """Matriz (n × 2 o n × 3) con x, y y, si existe, la incertidumbre de y."""
    filas = []
    for k, linea in enumerate((texto or "").splitlines(), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if re.search(r"[\s;]", linea):
            celdas = [c for c in re.split(r"[\s;]+", linea) if c]
        elif linea.count(",") == 1:
            celdas = linea.split(",")
        else:
            celdas = [linea]
        if len(celdas) not in (2, 3):
            raise ErrorGrafica(f"Línea {k}: se esperaban 2 columnas (x, y) o 3 (x, y, incertidumbre) y hay {len(celdas)}.")
        try:
            filas.append([leer_numero(c) for c in celdas])
        except ValueError as error:
            raise ErrorGrafica(f"Línea {k}: {error}") from None
        if len(filas) > MAX_FILAS_DATOS:
            raise ErrorGrafica(f"Hay demasiadas filas (máximo {MAX_FILAS_DATOS}).")
    if len(filas) < 2:
        raise ErrorGrafica("Se necesitan al menos 2 puntos (x y) para graficar.")
    if len({len(f) for f in filas}) != 1:
        raise ErrorGrafica("Todas las filas deben tener el mismo número de columnas.")
    datos = np.array(filas, dtype=float)
    if datos.shape[1] == 3 and (datos[:, 2] < 0).any():
        raise ErrorGrafica("Las incertidumbres (tercera columna) no pueden ser negativas.")
    return datos


def ajuste_lineal(x, y) -> dict:
    """Recta de mínimos cuadrados y = m x + b, con R² y las incertidumbres estándar de m y b (n ≥ 3)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n = len(x)
    if n < 2:
        raise ErrorGrafica("El ajuste lineal necesita al menos 2 puntos.")
    sxx = float(np.sum((x - x.mean()) ** 2))
    if sxx == 0.0:
        raise ErrorGrafica("Todos los valores de x son iguales: no se puede ajustar una recta.")
    m = float(np.sum((x - x.mean()) * (y - y.mean())) / sxx)
    b = float(y.mean() - m * x.mean())
    residuos = y - (m * x + b)
    ss_res, ss_tot = float(np.sum(residuos**2)), float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 if ss_tot == 0.0 else 1.0 - ss_res / ss_tot
    salida = {"pendiente": m, "ordenada": b, "r2": r2, "n": n, "u_pendiente": None, "u_ordenada": None}
    if n >= 3:
        s2 = ss_res / (n - 2)
        salida["u_pendiente"] = math.sqrt(s2 / sxx)
        salida["u_ordenada"] = math.sqrt(s2 * (1.0 / n + x.mean() ** 2 / sxx))
    return salida


def grafica_datos(tabla: str, tipo: str = "puntos", titulo: str = "", xlabel: str = "", ylabel: str = ""):
    """(figura, ajuste o None). `tipo`: 'puntos', 'linea' o 'ajuste' (puntos con recta de mínimos cuadrados)."""
    if tipo not in ("puntos", "linea", "ajuste"):
        raise ErrorGrafica(f"Tipo de gráfica desconocido: {tipo!r}.")
    datos = leer_tabla(tabla)
    x, y = datos[:, 0], datos[:, 1]
    yerr = datos[:, 2] if datos.shape[1] == 3 else None
    plt = _plt()
    ajuste = None
    with plt.style.context("default"):
        fig, ax = plt.subplots(figsize=(6.0, 3.4), facecolor="white")
        if tipo == "linea":
            orden = np.argsort(x)
            ax.plot(x[orden], y[orden], "-o", color=COLORES[0], ms=4, lw=1.4)
            if yerr is not None:
                ax.errorbar(x[orden], y[orden], yerr=yerr[orden], fmt="none", ecolor=COLORES[0], capsize=3)
        else:
            if yerr is not None:
                ax.errorbar(x, y, yerr=yerr, fmt="o", color=COLORES[0], ms=4, capsize=3, label="datos")
            else:
                ax.plot(x, y, "o", color=COLORES[0], ms=4, label="datos")
        if tipo == "ajuste":
            ajuste = ajuste_lineal(x, y)
            xs = np.linspace(x.min(), x.max(), 100)
            ax.plot(xs, ajuste["pendiente"] * xs + ajuste["ordenada"], color=COLORES[1], lw=1.6,
                    label=f"y = {ajuste['pendiente']:.4g} x + {ajuste['ordenada']:.4g}  (R² = {ajuste['r2']:.4f})")
            ax.legend(fontsize=8)
        ax.set(xlabel=xlabel, ylabel=ylabel, title=titulo)
        ax.grid(alpha=0.3)
        fig.tight_layout()
    return fig, ajuste


def a_png(fig, dpi: int = 110) -> bytes:
    """Figura → PNG (y se cierra para no acumular figuras abiertas)."""
    import io
    plt = _plt()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
    plt.close(fig)
    return buf.getvalue()
