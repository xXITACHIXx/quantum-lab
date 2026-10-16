"""
particula_caja.py — QUANTUM LAB · Simulador 1: partícula en una caja 1D
=======================================================================

Modelo: partícula de masa m en un pozo de potencial infinito de longitud a.

    V(x) = 0   (0 < x < a)          V(x) = ∞   (fuera)

    ψ_n(x) = √(2/a) sin(nπx/a)      E_n = n²π²ħ²/(2 m a²)      ρ_n = |ψ_n|²

Superposición dependiente del tiempo:

    Ψ(x,t) = Σ_n c_n ψ_n(x) exp(-i E_n t/ħ)        ρ(x,t) = |Ψ(x,t)|²

La densidad se calcula SIEMPRE a partir de la función de onda total (nunca
sumando densidades individuales); el término de interferencia se obtiene por
diferencia con la suma incoherente Σ|c_n|²|ψ_n|².

Tiempo adimensional:  τ = E₁ t/ħ.  Como E_n = n² E₁, la fase de cada estado
es exactamente exp(-i n² τ) (sin errores de cancelación) y toda superposición
vuelve a su forma inicial en τ = 2π (reaparición cuántica).

Estructura del archivo
    1. Física pura (NumPy/SciPy; no dibuja ni usa Streamlit)
    2. Figuras (Matplotlib y Plotly)
    3. Pruebas numéricas
    4. Interfaz Streamlit
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import streamlit as st
from scipy.signal import find_peaks

import quantum_lab_comun as qc
from quantum_lab_comun import HBAR, M_E, E_CARGA, E_HARTREE, COLORES

# =====================================================================
# 1. FÍSICA
# =====================================================================
N_MAX = 200               # número cuántico máximo permitido
PUNTOS_MIN = 200
PUNTOS_MAX = 20000
PUNTOS_POR_N = 20         # puntos mínimos por unidad de n para resolver las oscilaciones
ESTADOS_MAX = 20          # filas de la tabla de superposición (la «lista rápida» admite hasta N_MAX estados)


@dataclass(frozen=True)
class ParametrosCaja:
    """Parámetros ya validados y convertidos a SI."""
    n: int
    longitud: float       # a [m]
    masa: float           # m [kg]
    sistema: str
    puntos: int


def validar_parametros_caja(n, longitud_usuario, masa_usuario, sistema, puntos) -> ParametrosCaja:
    """
    Valida los datos de la interfaz y los convierte a SI.

    Longitud: nm (modo SI) o a₀ (modo atómico). Masa: siempre en unidades de mₑ.
    Lanza ValueError con un mensaje comprensible si algún dato no es válido.
    """
    n = qc.entero_en_rango(n, "El número cuántico n", 1, N_MAX)
    puntos = qc.entero_en_rango(puntos, "El número de puntos", PUNTOS_MIN, PUNTOS_MAX)
    unidades = qc.obtener_unidades(sistema)
    longitud = qc.positivo_finito(longitud_usuario, "La longitud de la caja a") * unidades["factor_longitud"]
    masa = qc.positivo_finito(masa_usuario, "La masa m") * M_E
    if puntos < PUNTOS_POR_N * n:
        raise ValueError(
            f"Con n = {n} se necesitan al menos {PUNTOS_POR_N * n} puntos para resolver las "
            f"oscilaciones (hay {puntos}). Aumentar el número de puntos o reduce n.")
    return ParametrosCaja(n, longitud, masa, sistema, puntos)


def malla_caja(a: float, puntos: int) -> np.ndarray:
    """Malla uniforme sobre [0, a] con los extremos incluidos (donde ψ = 0)."""
    return np.linspace(0.0, a, int(puntos))


def funcion_onda(x, n: int, a: float):
    """ψ_n(x) = √(2/a) sin(nπx/a)   [m^(-1/2)]."""
    return np.sqrt(2.0 / a) * np.sin(n * np.pi * np.asarray(x) / a)


def energia_nivel(n: int, a: float, masa: float) -> float:
    """E_n = n²π²ħ²/(2ma²)   [J]."""
    return (n ** 2 * np.pi ** 2 * HBAR ** 2) / (2.0 * masa * a ** 2)


def momento_estado(n: int, a: float) -> float:
    """|p_n| = nπħ/a   [kg·m/s]  (módulo del momento de cada onda viajera componente)."""
    return n * np.pi * HBAR / a


def longitud_onda_de_broglie(n: int, a: float) -> float:
    """
    λ_n = h/|p_n| = 2a/n.

    Interpretación: ψ_n es una onda estacionaria, superposición de dos ondas
    viajeras con momentos +p_n y −p_n; λ_n es la longitud de onda de cada una.
    No describe una trayectoria clásica. Dentro de la caja caben n/2 de ellas.
    """
    return 2.0 * a / n


def integrar(x, y) -> float:
    """Regla del trapecio (compatible con NumPy antiguo y moderno)."""
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def normalizacion_numerica(x, psi) -> float:
    """∫|ψ|² dx (debe valer 1)."""
    return integrar(x, np.abs(psi) ** 2)


def nodos_interiores(n: int, a: float) -> np.ndarray:
    """Los n−1 nodos interiores: x_k = k a/n, k = 1…n−1."""
    return np.arange(1, n) * a / n


def maximos_probabilidad(n: int, a: float) -> np.ndarray:
    """Los n máximos de |ψ_n|²: x_k = (2k−1) a/(2n), k = 1…n."""
    return (2.0 * np.arange(1, n + 1) - 1.0) * a / (2.0 * n)


def calcular_estado_individual(p: ParametrosCaja) -> dict:
    """Todos los datos físicos de un estado estacionario (sin dibujar nada)."""
    x = malla_caja(p.longitud, p.puntos)
    psi = funcion_onda(x, p.n, p.longitud)
    niveles = np.arange(1, max(7, p.n + 3))
    return {
        "x": x, "psi": psi, "rho": psi ** 2,
        "energia": energia_nivel(p.n, p.longitud, p.masa),
        "niveles": niveles,
        "energias_niveles": np.array([energia_nivel(k, p.longitud, p.masa) for k in niveles]),
        "nodos": nodos_interiores(p.n, p.longitud),
        "maximos": maximos_probabilidad(p.n, p.longitud),
        "lambda_db": longitud_onda_de_broglie(p.n, p.longitud),
        "momento": momento_estado(p.n, p.longitud),
        "norma": normalizacion_numerica(x, psi),
    }


# ---------------------------------------------------------------------
# Superposición de estados
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class Superposicion:
    numeros: np.ndarray          # números cuánticos n_i (enteros distintos)
    coeficientes: np.ndarray     # c_i complejos (normalizados si `normalizada`)
    norma_original: float        # √Σ|c_i|² ANTES de normalizar
    normalizada: bool


def construir_superposicion(numeros, coeficientes_complejos, normalizar: bool = True) -> Superposicion:
    """
    Valida y (opcionalmente) normaliza una superposición.

    Normalizar significa dividir todos los c_n entre √Σ|c_n|²; así Σ|c_n|² = 1
    y ∫|Ψ|²dx = 1 en todo instante (la evolución temporal conserva la norma).
    """
    numeros = np.asarray(numeros)
    if numeros.size == 0:
        raise ValueError("Seleccionar al menos un estado.")
    if numeros.size > N_MAX:
        raise ValueError(f"Se admiten como máximo {N_MAX} estados distintos (n = 1 … {N_MAX}).")
    enteros = np.array([qc.entero_en_rango(v, "Cada número cuántico n", 1, N_MAX) for v in numeros])
    if len(np.unique(enteros)) != len(enteros):
        raise ValueError("No repitas el mismo número cuántico: suma los coeficientes en un único estado.")
    c = np.asarray(coeficientes_complejos, dtype=complex)
    if c.shape != enteros.shape:
        raise ValueError("Debe haber un coeficiente por cada número cuántico.")
    if not np.all(np.isfinite(c)):
        raise ValueError("Los coeficientes deben ser finitos.")
    norma = float(np.sqrt(np.sum(np.abs(c) ** 2)))
    if norma == 0.0:
        raise ValueError("Al menos un coeficiente debe ser distinto de cero.")
    if normalizar:
        c = c / norma
    return Superposicion(enteros, c, norma, bool(normalizar))


def coeficientes_desde_amplitud_fase(amplitudes, fases) -> np.ndarray:
    """c_n = A_n exp(iφ_n)  (fases en radianes; A_n ≥ 0)."""
    amplitudes = np.asarray(amplitudes, dtype=float)
    fases = np.asarray(fases, dtype=float)
    if np.any(amplitudes < 0):
        raise ValueError("Las amplitudes no pueden ser negativas (usa la fase para el signo).")
    return amplitudes * np.exp(1j * fases)


def coeficientes_desde_re_im(partes_reales, partes_imaginarias) -> np.ndarray:
    """c_n = Re + i·Im."""
    return np.asarray(partes_reales, dtype=float) + 1j * np.asarray(partes_imaginarias, dtype=float)


def leer_lista_estados(texto: str) -> tuple[list[int], np.ndarray]:
    """
    Interpreta la «lista rápida» de una superposición. Un estado por elemento, separados por «;» o por líneas:

        n:A        coeficiente real A (amplitud) con fase 0
        n:A:φ      cₙ = A·e^{iφ}, con φ en radianes

    Se aceptan comas decimales (2,5) y notación científica (1e-3). Devuelve (números n, coeficientes complejos).
    """
    import re
    numeros, amplitudes, fases = [], [], []
    for k, item in enumerate((t.strip() for t in re.split(r"[;\n]+", texto or "")), 1):
        if not item:
            continue
        partes = [p.strip() for p in item.split(":")]
        if len(partes) > 3 or not partes[0]:
            raise ValueError(f"Elemento {k} de la lista («{item}»): usa el formato n:A  o  n:A:φ.")
        partes += ["1", "0"][len(partes) - 1:]
        try:
            n = float(partes[0].replace(",", "."))
            A = float((partes[1] or "1").replace(",", "."))
            fase = float((partes[2] or "0").replace(",", "."))
        except ValueError:
            raise ValueError(f"Elemento {k} de la lista («{item}»): n, A y φ deben ser números.")
        if n != int(n):
            raise ValueError(f"Elemento {k} de la lista: n debe ser entero (recibido: {partes[0]}).")
        numeros.append(int(n))
        amplitudes.append(A)
        fases.append(fase)
    if not numeros:
        raise ValueError("La lista rápida está vacía.")
    # una amplitud negativa equivale a sumar π a la fase
    amplitudes = np.asarray(amplitudes, dtype=float)
    fases = np.asarray(fases, dtype=float) + np.where(amplitudes < 0, np.pi, 0.0)
    return numeros, coeficientes_desde_amplitud_fase(np.abs(amplitudes), fases)


def todos_reales(coeficientes, tolerancia: float = 1e-12) -> bool:
    return bool(np.all(np.abs(np.imag(coeficientes)) <= tolerancia * max(1.0, np.max(np.abs(coeficientes)))))


def descripcion_normalizacion(sup: Superposicion) -> str:
    """Texto que explica exactamente qué operación se ha realizado."""
    if sup.normalizada:
        return (f"Se normalizaron los coeficientes: se dividió cada cₙ entre √Σ|cₙ|² = "
                f"{sup.norma_original:.6f}. Ahora Σ|cₙ|² = 1 y ∫|Ψ|²dx = 1 en todo instante.")
    return (f"Normalización desactivada: Σ|cₙ|² = {sup.norma_original ** 2:.6f}. En este caso "
            f"∫|Ψ|²dx = Σ|cₙ|² ≠ 1 y |Ψ|² no es una densidad de probabilidad normalizada.")


def tiempo_desde_tau(tau: float, a: float, masa: float) -> float:
    """t = ħτ/E₁   [s]."""
    return HBAR * tau / energia_nivel(1, a, masa)


def _base_estacionaria(x, numeros, a) -> np.ndarray:
    """Matriz (k, N) con ψ_n(x) para cada n de la lista."""
    ns = np.asarray(numeros, dtype=float)[:, None]
    return np.sqrt(2.0 / a) * np.sin(ns * np.pi * np.asarray(x)[None, :] / a)


def terminos_temporales(x, numeros, coeficientes, a: float, tau: float) -> np.ndarray:
    """Matriz (k, N) con los sumandos c_n ψ_n(x) e^{-i n² τ}  (E_n t/ħ = n² τ)."""
    fases = np.exp(-1j * np.asarray(numeros, dtype=float) ** 2 * tau)
    return (np.asarray(coeficientes) * fases)[:, None] * _base_estacionaria(x, numeros, a)


def onda_total(x, numeros, coeficientes, a: float, tau: float) -> np.ndarray:
    """Ψ(x,t) = Σ c_n ψ_n(x) e^{-iE_n t/ħ}."""
    return np.sum(terminos_temporales(x, numeros, coeficientes, a, tau), axis=0)


def densidades_superposicion(x, numeros, coeficientes, a: float, tau: float):
    """
    Devuelve (ρ_total, ρ_incoherente, ρ_interferencia).

      ρ_total = |Ψ|²                      ← la densidad física
      ρ_incoherente = Σ |c_n|² |ψ_n|²    ← lo que saldría (erróneamente) sumando densidades
      ρ_interferencia = ρ_total − ρ_incoherente
    """
    rho_total = np.abs(onda_total(x, numeros, coeficientes, a, tau)) ** 2
    base = _base_estacionaria(x, numeros, a)
    rho_incoherente = (np.abs(np.asarray(coeficientes)) ** 2) @ (base ** 2)
    return rho_total, rho_incoherente, rho_total - rho_incoherente


def probabilidad_region(x, rho, fraccion_inicio: float, fraccion_fin: float) -> float:
    """
    Probabilidad de encontrar la partícula en [fraccion_inicio·a, fraccion_fin·a].

    Se interpola ρ en los límites exactos para no perder el tramo entre el
    límite y el punto de malla más cercano.
    """
    if not (0.0 <= fraccion_inicio < fraccion_fin <= 1.0):
        raise ValueError("La región debe cumplir 0 ≤ inicio < fin ≤ 1 (fracciones de a).")
    x_ini, x_fin = fraccion_inicio * x[-1], fraccion_fin * x[-1]
    interior = (x > x_ini) & (x < x_fin)
    xs = np.concatenate(([x_ini], x[interior], [x_fin]))
    return integrar(xs, np.interp(xs, x, rho))


def posicion_media(x, rho) -> float:
    """⟨x⟩ = ∫xρ dx / ∫ρ dx."""
    return integrar(x, x * rho) / integrar(x, rho)


def energia_media_e_incertidumbre(numeros, coeficientes, a: float, masa: float):
    """⟨E⟩ y ΔE de la superposición (independientes del tiempo: la energía se conserva)."""
    pesos = np.abs(np.asarray(coeficientes)) ** 2
    pesos = pesos / pesos.sum()
    energias = np.array([energia_nivel(int(k), a, masa) for k in numeros])
    media = float(np.sum(pesos * energias))
    varianza = float(np.sum(pesos * energias ** 2) - media ** 2)
    return media, float(np.sqrt(max(varianza, 0.0)))


def extremos_densidad(x, rho, prominencia_relativa: float = 1e-3, umbral_nodo: float = 0.01):
    """
    Máximos locales (regiones de probabilidad elevada) y mínimos locales de ρ.

    Un mínimo se considera NODO verdadero si ρ_min ≤ umbral_nodo·ρ_max; en una
    superposición con energías distintas ρ suele no anularse del todo.
    Los extremos x = 0 y x = a (donde ρ = 0 por la frontera) no se cuentan.
    """
    rho_max = float(np.max(rho))
    if rho_max <= 0:
        return np.array([]), np.array([]), np.array([], dtype=bool)
    prominencia = prominencia_relativa * rho_max
    i_max, _ = find_peaks(rho, prominence=prominencia)
    i_min, _ = find_peaks(-rho, prominence=prominencia)
    return x[i_max], x[i_min], rho[i_min] <= umbral_nodo * rho_max


def regiones_alta_probabilidad(x, rho, fraccion: float = 0.75) -> list[tuple[float, float]]:
    """Intervalos (x_ini, x_fin) donde ρ ≥ fracción·ρ_max."""
    mascara = np.concatenate(([False], rho >= fraccion * np.max(rho), [False]))
    cambios = np.diff(mascara.astype(int))
    inicios = np.flatnonzero(cambios == 1)
    finales = np.flatnonzero(cambios == -1) - 1
    return [(float(x[i]), float(x[j])) for i, j in zip(inicios, finales)]


def variacion_temporal_maxima(x, numeros, coeficientes, a: float, taus) -> float:
    """
    max_τ max_x |ρ(x,τ) − ρ(x,0)| · a   (adimensional).
    Vale ≈ 0 para un estado estacionario y > 0 si hay interferencia temporal.
    """
    rho0 = np.abs(onda_total(x, numeros, coeficientes, a, 0.0)) ** 2
    variacion = max(np.max(np.abs(np.abs(onda_total(x, numeros, coeficientes, a, t)) ** 2 - rho0))
                    for t in taus)
    return float(variacion * a)


def calcular_superposicion(p: ParametrosCaja, sup: Superposicion, tau: float,
                           region: tuple[float, float]) -> dict:
    """Todos los datos de una superposición en el instante τ (sin dibujar)."""
    a = p.longitud
    x = malla_caja(a, p.puntos)
    terminos = terminos_temporales(x, sup.numeros, sup.coeficientes, a, tau)
    psi = np.sum(terminos, axis=0)
    rho, rho_inc, rho_int = densidades_superposicion(x, sup.numeros, sup.coeficientes, a, tau)
    x_max, x_min, nodal = extremos_densidad(x, rho)
    e_media, delta_e = energia_media_e_incertidumbre(sup.numeros, sup.coeficientes, a, p.masa)
    return {
        "x": x, "psi": psi, "rho": rho, "rho_inc": rho_inc, "rho_int": rho_int,
        "terminos": terminos, "tau": tau, "tiempo": tiempo_desde_tau(tau, a, p.masa),
        "suma_c2": float(np.sum(np.abs(sup.coeficientes) ** 2)),
        "norma_espacial": integrar(x, rho),
        "prob_region": probabilidad_region(x, rho, *region),
        "x_media": posicion_media(x, rho),
        "e_media": e_media, "delta_e": delta_e,
        "x_max": x_max, "x_min": x_min, "nodal": nodal,
        "regiones": regiones_alta_probabilidad(x, rho),
    }


def serie_temporal(p: ParametrosCaja, sup: Superposicion, n_cuadros: int, puntos: int = 500):
    """
    Calcula Re Ψ, Im Ψ y ρ para `n_cuadros` instantes τ ∈ [0, 2π) (un periodo
    completo de reaparición). Devuelve (x, taus, re, im, rho) con forma (cuadros, puntos).
    """
    x = malla_caja(p.longitud, puntos)
    taus = np.linspace(0.0, 2.0 * np.pi, n_cuadros, endpoint=False)
    psi = np.array([onda_total(x, sup.numeros, sup.coeficientes, p.longitud, t) for t in taus])
    return x, taus, psi.real, psi.imag, np.abs(psi) ** 2


def parametros_experimento() -> tuple[list[int], np.ndarray]:
    """Experimento recomendado: n = 1, n = 2 y superposición 1+2 con coeficientes iguales."""
    return [1, 2], np.array([1.0, 1.0]) / np.sqrt(2.0)


# =====================================================================
# 2. FIGURAS
# =====================================================================
def _etiquetas_unidades(sistema: str) -> dict:
    u = qc.obtener_unidades(sistema)
    return {"u": u, "fx": u["factor_longitud"], "fe": u["factor_energia"],
            "L": u["nombre_longitud"], "Ltex": u["nombre_longitud_tex"],
            "E": u["nombre_energia"]}


def figura_estado_individual(d: dict, p: ParametrosCaja):
    """Cuatro paneles coordinados del estado estacionario."""
    import matplotlib.pyplot as plt
    et = _etiquetas_unidades(p.sistema)
    fx, fe, L, Ltex, U = et["fx"], et["fe"], et["L"], et["Ltex"], et["E"]
    n = p.n
    x_vis = d["x"] / fx
    psi_vis = d["psi"] * np.sqrt(fx)
    rho_vis = d["rho"] * fx
    e_vis = d["energia"] / fe
    nodos_vis = d["nodos"] / fx
    maximos_vis = d["maximos"] / fx

    fig, ejes = qc.rejilla(2, 2, (14, 9.4), constrained_layout=True)
    # Márgenes explícitos entre paneles: los títulos y las etiquetas del eje x de la fila de arriba no deben tocar los de abajo.
    fig.get_layout_engine().set(h_pad=0.16, w_pad=0.12, hspace=0.12, wspace=0.08)
    fig.suptitle(f"Partícula en una caja 1D — estado n = {n}", fontsize=17, fontweight="bold")

    # Panel 1: función de onda (lóbulos positivo/negativo sombreados)
    ax = ejes[0, 0]
    ax.fill_between(x_vis, psi_vis, 0, where=psi_vis >= 0, color=COLORES["onda"], alpha=0.18)
    ax.fill_between(x_vis, psi_vis, 0, where=psi_vis < 0, color=COLORES["energia"], alpha=0.18)
    ax.plot(x_vis, psi_vis, color=COLORES["onda"], lw=2.4, label=rf"$\psi_{{{n}}}(x)$")
    ax.axhline(0, color="white", lw=0.8, alpha=0.5)
    ax.set_title("Función de onda")
    ax.set_xlabel(f"x [{L}]")
    ax.set_ylabel(rf"$\psi_n(x)\ [{Ltex}^{{-1/2}}]$")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    # Panel 2: densidad, nodos, máximos y número cuántico
    ax = ejes[0, 1]
    ax.plot(x_vis, rho_vis, color=COLORES["densidad"], lw=2.4,
            label=rf"$|\psi_{{{n}}}(x)|^2$")
    ax.fill_between(x_vis, rho_vis, color=COLORES["densidad"], alpha=0.12)
    if len(nodos_vis):
        ax.scatter(nodos_vis, np.zeros_like(nodos_vis), color=COLORES["energia"], s=55,
                   zorder=5, label=f"Nodos interiores ({n - 1})")
    ax.scatter(maximos_vis, np.interp(maximos_vis, x_vis, rho_vis), marker="*", s=130,
               color=COLORES["interferencia"], zorder=6, label=f"Máximos de probabilidad ({n})")
    ax.text(0.02, 0.96, f"n = {n}\n{n - 1} nodos\n{n} máximos", transform=ax.transAxes,
            va="top", fontsize=10, fontweight="bold", color=COLORES["texto"],
            bbox=dict(boxstyle="round,pad=0.4", fc=COLORES["fondo"], ec=COLORES["rejilla"]))
    ax.set_title("Densidad de probabilidad")
    ax.set_xlabel(f"x [{L}]")
    ax.set_ylabel(rf"$|\psi_n(x)|^2\ [{Ltex}^{{-1}}]$")
    ax.set_ylim(-0.04 * rho_vis.max(), 1.55 * rho_vis.max())      # espacio arriba para la leyenda y el recuadro de n
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    # Panel 3: potencial y nivel energético
    ax = ejes[1, 0]
    techo = 1.4 * e_vis
    ax.plot([x_vis[0], x_vis[-1]], [0, 0], color=COLORES["potencial"], lw=4,
            label=r"$V=0$ dentro de la caja")
    for borde in (x_vis[0], x_vis[-1]):
        ax.plot([borde, borde], [0, techo], color=COLORES["potencial"], lw=5)
    ax.text(x_vis[0], techo * 0.93, r" $V\to\infty$", color=COLORES["potencial"], va="top")
    ax.text(x_vis[-1], techo * 0.93, r"$V\to\infty$ ", color=COLORES["potencial"], va="top", ha="right")
    ax.hlines(e_vis, x_vis[0], x_vis[-1], color=COLORES["energia"], lw=2.4, linestyle="--",
              label=rf"$E_{{{n}}}$")
    ax.plot(x_vis, e_vis + 0.28 * e_vis * rho_vis / rho_vis.max(), color=COLORES["densidad"],
            lw=1.3, alpha=0.9, label=r"$|\psi_n|^2$ (escala arbitraria)")
    ax.set_ylim(0, techo)
    ax.set_title("Potencial y nivel energético")
    ax.set_xlabel(f"x [{L}]")
    ax.set_ylabel(f"Energía [{U}]")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")

    # Panel 4: diagrama de niveles
    ax = ejes[1, 1]
    energias = d["energias_niveles"] / fe
    for nivel, en in zip(d["niveles"], energias):
        actual = nivel == n
        color = COLORES["energia"] if actual else COLORES["gris"]
        ax.hlines(en, 0.2, 0.8, color=color, lw=4 if actual else 1.6)
        if nivel % 2 == 1:
            ax.text(0.84, en, f"n={nivel}", va="center", ha="left", color=color, fontsize=9)
        else:
            ax.text(0.16, en, f"n={nivel}", va="center", ha="right", color=color, fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, energias.max() * 1.08)
    ax.set_xticks([])
    ax.set_title(r"Diagrama de niveles  ($E_n \propto n^2$)")
    ax.set_ylabel(f"Energía [{U}]")
    ax.grid(axis="y", alpha=0.3)
    return fig


def figura_superposicion(d: dict, p: ParametrosCaja, sup: Superposicion, region: tuple[float, float],
                         comparar_individuales: bool, mostrar_extremos: bool):
    """Re Ψ, Im Ψ y |Ψ|² en un instante τ concreto."""
    import matplotlib.pyplot as plt
    et = _etiquetas_unidades(p.sistema)
    fx, L, Ltex = et["fx"], et["L"], et["Ltex"]
    x_vis = d["x"] / fx
    amp_max = 1.12 * np.sqrt(fx) * max(np.max(np.abs(d["psi"])),
                                       np.max(np.abs(d["terminos"])) if comparar_individuales else 0.0,
                                       1e-300)

    fig, ejes = qc.rejilla(1, 3, (17.5, 5.4), constrained_layout=True)
    fig.suptitle(rf"Superposición de estados {[int(k) for k in sup.numeros]} — "
                 rf"$\tau = E_1 t/\hbar$ = {d['tau']:.3f}", fontsize=15, fontweight="bold")

    ax = ejes[0]
    ax.plot(x_vis, d["psi"].real * np.sqrt(fx), color=COLORES["onda"], lw=2.4,
            label=r"$\mathrm{Re}\,\Psi$")
    if comparar_individuales:
        for k, term in zip(sup.numeros, d["terminos"]):
            ax.plot(x_vis, term.real * np.sqrt(fx), ls="--", lw=1.3, alpha=0.7,
                    label=rf"$\mathrm{{Re}}[c_{{{int(k)}}}\psi_{{{int(k)}}}e^{{-iE_{{{int(k)}}}t/\hbar}}]$")
    ax.axhline(0, color="white", lw=0.8, alpha=0.5)
    ax.set_ylim(-amp_max, amp_max)
    ax.set_title(r"Parte real de $\Psi(x,t)$")
    ax.set_xlabel(f"x [{L}]")
    ax.set_ylabel(rf"$\Psi\ [{Ltex}^{{-1/2}}]$")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    ax = ejes[1]
    ax.plot(x_vis, d["psi"].imag * np.sqrt(fx), color=COLORES["interferencia"], lw=2.4,
            label=r"$\mathrm{Im}\,\Psi$")
    ax.axhline(0, color="white", lw=0.8, alpha=0.5)
    ax.set_ylim(-amp_max, amp_max)
    ax.set_title(r"Parte imaginaria de $\Psi(x,t)$")
    ax.set_xlabel(f"x [{L}]")
    ax.set_ylabel(rf"$\Psi\ [{Ltex}^{{-1/2}}]$")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    ax = ejes[2]
    rho_vis = d["rho"] * fx
    ax.plot(x_vis, rho_vis, color=COLORES["densidad"], lw=2.6, label=r"$|\Psi(x,t)|^2$")
    ax.fill_between(x_vis, rho_vis, color=COLORES["densidad"], alpha=0.10)
    ax.axvspan(region[0] * x_vis[-1], region[1] * x_vis[-1], color=COLORES["interferencia"], alpha=0.12,
               label=f"Región integrada (P = {d['prob_region']:.4f})")
    if comparar_individuales:
        for k, c in zip(sup.numeros, sup.coeficientes):
            ax.plot(x_vis, abs(c) ** 2 * funcion_onda(d["x"], int(k), p.longitud) ** 2 * fx,
                    ls=":", lw=1.3, alpha=0.8, label=rf"$|c_{{{int(k)}}}|^2|\psi_{{{int(k)}}}|^2$")
        ax.plot(x_vis, d["rho_inc"] * fx, color="white", ls="--", lw=1.2, alpha=0.8,
                label=r"suma incoherente $\sum|c_n|^2|\psi_n|^2$")
        ax.plot(x_vis, d["rho_int"] * fx, color=COLORES["energia"], lw=1.4, alpha=0.9,
                label=r"término de interferencia")
    if mostrar_extremos:
        for ini, fin in d["regiones"]:
            ax.axvspan(ini / fx, fin / fx, ymin=0, ymax=0.04, color=COLORES["interferencia"], alpha=0.9)
        if len(d["x_max"]):
            ax.scatter(d["x_max"] / fx, np.interp(d["x_max"], d["x"], d["rho"]) * fx, marker="*", s=110,
                       color=COLORES["interferencia"], zorder=6, label="Máximos locales")
        if len(d["x_min"]):
            y_min = np.interp(d["x_min"], d["x"], d["rho"]) * fx
            vistos_nodo = d["nodal"]
            if np.any(vistos_nodo):
                ax.scatter(d["x_min"][vistos_nodo] / fx, y_min[vistos_nodo], s=55, color=COLORES["energia"],
                           zorder=6, label="Nodos (ρ ≈ 0)")
            if np.any(~vistos_nodo):
                ax.scatter(d["x_min"][~vistos_nodo] / fx, y_min[~vistos_nodo], s=40, facecolors="none",
                           edgecolors=COLORES["energia"], zorder=6, label="Mínimos locales (ρ > 0)")
    ax.set_ylim(bottom=-0.02 * rho_vis.max(), top=1.35 * rho_vis.max())
    ax.set_title("Densidad de probabilidad total")
    ax.set_xlabel(f"x [{L}]")
    ax.set_ylabel(rf"$|\Psi|^2\ [{Ltex}^{{-1}}]$")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=7.5)
    return fig


def figura_animacion_superposicion(x_vis, taus, re, im, rho, nombre_longitud: str,
                                   etiquetas_tiempo: list[str]):
    """
    Animación de Plotly (Re Ψ, Im Ψ y |Ψ|²) para un periodo completo τ ∈ [0, 2π).
    Los arrays ya vienen en unidades de visualización.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.09,
                        subplot_titles=("Función de onda compleja Ψ(x,t)", "Densidad |Ψ(x,t)|²"))
    fig.add_trace(go.Scatter(x=x_vis, y=re[0], name="Re Ψ", line=dict(color=COLORES["onda"], width=3)), 1, 1)
    fig.add_trace(go.Scatter(x=x_vis, y=im[0], name="Im Ψ",
                             line=dict(color=COLORES["interferencia"], width=3)), 1, 1)
    fig.add_trace(go.Scatter(x=x_vis, y=rho[0], name="|Ψ|²", fill="tozeroy",
                             line=dict(color=COLORES["densidad"], width=3),
                             fillcolor="rgba(255,176,0,0.15)"), 1, 2)
    nombres = [str(i) for i in range(len(taus))]
    fig.frames = [go.Frame(name=nombres[i], traces=[0, 1, 2],
                           data=[go.Scatter(y=re[i]), go.Scatter(y=im[i]), go.Scatter(y=rho[i])])
                  for i in range(len(taus))]
    amp = 1.1 * max(np.max(np.abs(re)), np.max(np.abs(im)))
    fig.update_yaxes(range=[-amp, amp], title_text="Ψ (unidades de visualización)", row=1, col=1)
    fig.update_yaxes(range=[0, 1.12 * np.max(rho)], title_text="|Ψ|²", row=1, col=2)
    fig.update_xaxes(title_text=f"x [{nombre_longitud}]")
    qc.aplicar_tema_plotly(fig, altura=500)
    qc.agregar_animacion(fig, nombres, etiquetas_tiempo, duracion_ms=70)
    return fig


def figura_experimento(x_vis, rho1, rho2, rho12_t, rho12_0, taus, nombre_longitud: str,
                       etiquetas_tiempo: list[str]):
    """Estado n=1, estado n=2 y superposición 1+2: solo la última evoluciona."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.07, shared_yaxes=True,
                        subplot_titles=("Estado n = 1 (estacionario)", "Estado n = 2 (estacionario)",
                                        "Superposición n = 1 y n = 2"))
    fig.add_trace(go.Scatter(x=x_vis, y=rho1, name="|ψ₁|²", fill="tozeroy",
                             line=dict(color=COLORES["onda"], width=3), fillcolor="rgba(0,212,255,0.15)"), 1, 1)
    fig.add_trace(go.Scatter(x=x_vis, y=rho2, name="|ψ₂|²", fill="tozeroy",
                             line=dict(color=COLORES["potencial"], width=3), fillcolor="rgba(139,92,246,0.15)"), 1, 2)
    fig.add_trace(go.Scatter(x=x_vis, y=rho12_t[0], name="|Ψ(x,t)|²", fill="tozeroy",
                             line=dict(color=COLORES["densidad"], width=3), fillcolor="rgba(255,176,0,0.15)"), 1, 3)
    fig.add_trace(go.Scatter(x=x_vis, y=rho12_0, name="|Ψ(x,0)|² (referencia)",
                             line=dict(color="white", width=1.5, dash="dot")), 1, 3)
    nombres = [str(i) for i in range(len(taus))]
    fig.frames = [go.Frame(name=nombres[i], traces=[2], data=[go.Scatter(y=rho12_t[i])])
                  for i in range(len(taus))]
    tope = 1.12 * max(np.max(rho1), np.max(rho2), np.max(rho12_t))
    fig.update_yaxes(range=[0, tope])
    fig.update_yaxes(title_text="|Ψ|² (unidades de visualización)", row=1, col=1)
    fig.update_xaxes(title_text=f"x [{nombre_longitud}]")
    qc.aplicar_tema_plotly(fig, altura=470)
    qc.agregar_animacion(fig, nombres, etiquetas_tiempo, duracion_ms=70)
    return fig


# =====================================================================
# 3. PRUEBAS NUMÉRICAS
# =====================================================================
def ejecutar_pruebas() -> qc.RegistroPruebas:
    """Pruebas de física, de la superposición y de la validación de entradas."""
    r = qc.RegistroPruebas("Partícula en una caja 1D")
    a, masa = 1.0e-9, M_E
    x = np.linspace(0.0, a, 5000)

    # --- Condiciones de frontera. ψ tiene dimensiones (m^-1/2): se compara la
    #     cantidad adimensional ψ·√a (una tolerancia absoluta sobre ψ no tiene sentido).
    peor = max(max(abs(funcion_onda(x[0], n, a)), abs(funcion_onda(x[-1], n, a))) * np.sqrt(a)
               for n in range(1, 21))
    r.comprobar("ψ_n(0) = ψ_n(a) = 0 (n = 1…20)", peor < 1e-12, f"máx |ψ·√a| en los bordes = {peor:.2e}")

    # --- Normalización
    err = max(abs(normalizacion_numerica(x, funcion_onda(x, n, a)) - 1.0) for n in range(1, 21))
    r.comprobar("∫|ψ_n|² dx = 1 (n = 1…20)", err < 1e-6, f"máx |∫−1| = {err:.2e}")

    # --- Energías
    e1 = energia_nivel(1, a, masa)
    err = max(abs(energia_nivel(n, a, masa) / e1 / n ** 2 - 1.0) for n in range(1, 30))
    r.comprobar("E_n ∝ n²", err < 1e-12, f"máx |E_n/(n²E₁) − 1| = {err:.2e}")
    r.comprobar("E ∝ 1/a²  (E(a)/E(2a) = 4)",
                abs(energia_nivel(1, a, masa) / energia_nivel(1, 2 * a, masa) - 4.0) < 1e-12)
    r.comprobar("E ∝ 1/m  (E(m)/E(2m) = 2)",
                abs(energia_nivel(1, a, masa) / energia_nivel(1, a, 2 * masa) - 2.0) < 1e-12)
    r.comprobar("Valor absoluto: electrón en 1 nm → E₁ = 0.376 eV",
                abs(e1 / E_CARGA - 0.376030) < 1e-4, f"E₁ = {e1 / E_CARGA:.6f} eV")
    r.comprobar("Unidades atómicas: a = a₀, m = mₑ → E₁ = π²/2 Eₕ",
                abs(energia_nivel(1, qc.A0, M_E) / E_HARTREE - np.pi ** 2 / 2) < 1e-9)
    r.comprobar("De Broglie: λ_n·|p_n| = h",
                abs(longitud_onda_de_broglie(3, a) * momento_estado(3, a) / qc.H_PLANCK - 1.0) < 1e-12)

    # --- Nodos y máximos
    nodos, maximos = nodos_interiores(5, a), maximos_probabilidad(5, a)
    r.comprobar("n−1 nodos interiores donde ψ = 0",
                len(nodos) == 4 and np.max(np.abs(funcion_onda(nodos, 5, a))) * np.sqrt(a) < 1e-12)
    r.comprobar("n máximos de |ψ|² con valor 2/a",
                len(maximos) == 5 and np.allclose(funcion_onda(maximos, 5, a) ** 2 * a, 2.0))

    # --- Coeficientes
    sup = construir_superposicion([1, 2, 3], coeficientes_desde_amplitud_fase([1, 1, 0.5], [0, np.pi / 3, -np.pi / 4]))
    r.comprobar("Σ|c_n|² = 1 tras normalizar", abs(np.sum(np.abs(sup.coeficientes) ** 2) - 1.0) < 1e-12)
    sin_norm = construir_superposicion([1, 2], [3.0, 4.0], normalizar=False)
    r.comprobar("Sin normalizar se conservan los coeficientes (norma 5)",
                abs(sin_norm.norma_original - 5.0) < 1e-12 and np.allclose(sin_norm.coeficientes, [3, 4]))

    # --- Superposición: |Ψ|² calculada desde la función de onda total
    c12 = construir_superposicion(*parametros_experimento())
    psi_t = onda_total(x, c12.numeros, c12.coeficientes, a, 0.75)
    rho_t, rho_inc, rho_int = densidades_superposicion(x, c12.numeros, c12.coeficientes, a, 0.75)
    r.comprobar("ρ = |Ψ|² (calculada con la función de onda total)", np.allclose(rho_t, np.abs(psi_t) ** 2))
    r.comprobar("∫|Ψ|² dx = 1", abs(integrar(x, rho_t) - 1.0) < 1e-6)
    r.comprobar("|Ψ|² ≠ Σ|c_n|²|ψ_n|² (hay interferencia)", np.max(np.abs(rho_int)) * a > 1e-3,
                f"máx |interferencia|·a = {np.max(np.abs(rho_int)) * a:.3f}")
    r.comprobar("La interferencia integra a 0 (ortogonalidad)", abs(integrar(x, rho_int)) < 1e-6,
                f"∫ interferencia = {integrar(x, rho_int):.2e}")

    # --- Evolución temporal
    c123 = construir_superposicion([1, 2, 3], [1.0, 0.7, 0.4])
    normas = [integrar(x, np.abs(onda_total(x, c123.numeros, c123.coeficientes, a, t)) ** 2)
              for t in np.linspace(0, 2 * np.pi, 9)]
    r.comprobar("La norma se conserva en el tiempo", np.max(np.abs(np.array(normas) - 1)) < 1e-6)
    r.comprobar("Reaparición: Ψ(τ = 2π) = Ψ(τ = 0)",
                np.allclose(onda_total(x, c123.numeros, c123.coeficientes, a, 2 * np.pi) * np.sqrt(a),
                            onda_total(x, c123.numeros, c123.coeficientes, a, 0.0) * np.sqrt(a), atol=1e-9))
    rho_a = np.abs(onda_total(x, c12.numeros, c12.coeficientes, a, 0.0)) ** 2
    rho_b = np.abs(onda_total(x, c12.numeros, c12.coeficientes, a, 2 * np.pi / 3)) ** 2
    r.comprobar("Densidad de (1+2) periódica con Δτ = 2π/3", np.allclose(rho_a * a, rho_b * a, atol=1e-9))
    taus = np.linspace(0, 2 * np.pi, 25)
    estac = construir_superposicion([2], [1.0])
    v_est = variacion_temporal_maxima(x, estac.numeros, estac.coeficientes, a, taus)
    v_sup = variacion_temporal_maxima(x, c12.numeros, c12.coeficientes, a, taus)
    r.comprobar("Estado estacionario: ρ no cambia con el tiempo", v_est < 1e-9, f"variación = {v_est:.2e}")
    r.comprobar("Superposición 1+2: ρ sí cambia con el tiempo", v_sup > 0.5, f"variación = {v_sup:.3f}")
    e_med, de = energia_media_e_incertidumbre(c12.numeros, c12.coeficientes, a, masa)
    r.comprobar("⟨E⟩ = (E₁+E₂)/2 para coeficientes iguales", abs(e_med / ((e1 + 4 * e1) / 2) - 1) < 1e-12)

    # --- Probabilidad por regiones
    rho1 = funcion_onda(x, 1, a) ** 2
    r.comprobar("P(0, a) = 1", abs(probabilidad_region(x, rho1, 0.0, 1.0) - 1.0) < 1e-6)
    r.comprobar("P(a/4, 3a/4) = 1/2 + 1/π (n = 1)",
                abs(probabilidad_region(x, rho1, 0.25, 0.75) - (0.5 + 1 / np.pi)) < 1e-6)
    xg = np.linspace(0.0, a, 201)
    exacta = (0.789 - 0.123) - (np.sin(2 * np.pi * 0.789) - np.sin(2 * np.pi * 0.123)) / (2 * np.pi)
    r.comprobar("Límites fuera de la malla (interpolación exacta)",
                abs(probabilidad_region(xg, funcion_onda(xg, 1, a) ** 2, 0.123, 0.789) - exacta) < 1e-4)

    # --- Extremos de ρ
    x_max, x_min, nodal = extremos_densidad(x, funcion_onda(x, 4, a) ** 2)
    r.comprobar("ρ de n = 4: 4 máximos y 3 nodos detectados", len(x_max) == 4 and len(x_min) == 3 and bool(nodal.all()))

    # --- Validación de entradas
    v = validar_parametros_caja
    # --- Lista rápida de estados (cantidad de estados libre hasta N_MAX)
    ns_l, c_l = leer_lista_estados("1:1; 2:0.5; 7:-0.3\n12:0.2:1,57")
    r.comprobar("Lista rápida: lee n, amplitud y fase (comas decimales, líneas y «;»)",
                ns_l == [1, 2, 7, 12] and abs(c_l[2] + 0.3) < 1e-12 and abs(np.angle(c_l[3]) - 1.57) < 1e-12,
                f"n = {ns_l}")
    ns50 = list(range(1, 51))
    sup50 = construir_superposicion(ns50, leer_lista_estados("; ".join(f"{k}:{1 / k}" for k in ns50))[1])
    x50 = malla_caja(a, 4000)
    rho50 = np.abs(onda_total(x50, sup50.numeros, sup50.coeficientes, a, 0.37)) ** 2
    r.comprobar("Superposición de 50 estados: Σ|cₙ|² = 1 y ∫|Ψ|²dx = 1",
                abs(np.sum(np.abs(sup50.coeficientes) ** 2) - 1) < 1e-12 and abs(integrar(x50, rho50) - 1) < 1e-5,
                f"∫|Ψ|²dx = {integrar(x50, rho50):.8f}")
    r.comprobar_error("Lista rápida: rechaza n no entero", leer_lista_estados, "2.5:1")
    r.comprobar_error("Lista rápida: rechaza formato incorrecto", leer_lista_estados, "1:2:3:4")
    r.comprobar_error("Lista rápida: rechaza texto no numérico", leer_lista_estados, "a:1")
    r.comprobar_error("Lista rápida: rechaza lista vacía", leer_lista_estados, " ; ")

    r.comprobar_error("Rechaza n = 0", v, 0, 1.0, 1.0, "SI", 1000)
    r.comprobar_error("Rechaza n no entero (2.5)", v, 2.5, 1.0, 1.0, "SI", 1000)
    r.comprobar_error("Rechaza longitud negativa", v, 1, -1.0, 1.0, "SI", 1000)
    r.comprobar_error("Rechaza masa nula", v, 1, 1.0, 0.0, "SI", 1000)
    r.comprobar_error("Rechaza sistema de unidades desconocido", v, 1, 1.0, 1.0, "CGS", 1000)
    r.comprobar_error("Rechaza puntos insuficientes para n grande", v, 100, 1.0, 1.0, "SI", 1000)
    r.comprobar_error("Rechaza estados repetidos", construir_superposicion, [1, 1], [1.0, 1.0])
    r.comprobar_error("Rechaza coeficientes todos nulos", construir_superposicion, [1, 2], [0.0, 0.0])
    r.comprobar_error("Rechaza región invertida", probabilidad_region, x, rho1, 0.7, 0.2)
    return r


# =====================================================================
# 4. INTERFAZ (Streamlit)
# =====================================================================
PREFIJO = "caja_"
VALORES_INICIALES = {
    "caja_n": 1, "caja_longitud": 1.0, "caja_masa": 1.0, "caja_sistema": "SI", "caja_puntos": 1500,
    "caja_sup_cantidad": 2, "caja_sup_modo": "Amplitud y fase", "caja_sup_normalizar": True,
    "caja_sup_comparar": False, "caja_sup_extremos": True, "caja_sup_tau": 0.0,
    "caja_sup_region": (0.25, 0.75), "caja_sup_lista": "",
}
for _i in range(1, ESTADOS_MAX + 1):
    VALORES_INICIALES.update({f"caja_sup_n{_i}": _i, f"caja_sup_A{_i}": 1.0, f"caja_sup_fase{_i}": 0.0,
                              f"caja_sup_re{_i}": 1.0, f"caja_sup_im{_i}": 0.0})

DEMOS = {
    "Electrón en 1 nm — estado fundamental": {"caja_n": 1, "caja_longitud": 1.0, "caja_masa": 1.0,
                                              "caja_sistema": "SI", "caja_puntos": 1500},
    "Electrón en 1 nm — estado excitado n = 5": {"caja_n": 5, "caja_longitud": 1.0, "caja_masa": 1.0,
                                                 "caja_sistema": "SI", "caja_puntos": 1500},
    "Unidades atómicas — a = 10 a₀, n = 3": {"caja_n": 3, "caja_longitud": 10.0, "caja_masa": 1.0,
                                             "caja_sistema": "Atómicas", "caja_puntos": 1500},
    "Protón en 10 fm (escala nuclear)": {"caja_n": 1, "caja_longitud": 1e-5, "caja_masa": 1836.15267343,
                                         "caja_sistema": "SI", "caja_puntos": 1500},
}
EXPERIMENTO_EN_SUPERPOSICION = {
    "caja_sup_cantidad": 2, "caja_sup_modo": "Amplitud y fase", "caja_sup_normalizar": True,
    "caja_sup_n1": 1, "caja_sup_n2": 2, "caja_sup_A1": 1.0, "caja_sup_A2": 1.0,
    "caja_sup_fase1": 0.0, "caja_sup_fase2": 0.0, "caja_sup_tau": 0.0,
}


# ---------------------------------------------------------------------
# Guía de práctica y autoevaluación
# ---------------------------------------------------------------------
GUIA = [
    {"titulo": "La energía crece como n²",
     "objetivo": "Comprobar la cuantización Eₙ = n²E₁.",
     "pasos": ["Cargar la configuración (electrón en una caja de 1 nm, n = 1).", "Registrar E₁.",
               "Cambiar n a 2, 3 y 4 y registrar cada energía.", "Calcular los cocientes Eₙ/E₁."],
     "pregunta": "Antes de medir: si n se duplica, ¿cuánto cambia la energía?",
     "resultado": "Los cocientes son 1 : 4 : 9 : 16. Con a = 1 nm y la masa del electrón, E₁ ≈ 0.376 eV. "
                  "Los niveles se separan cada vez más, a diferencia del oscilador (equiespaciado).",
     "pestana": "Estado individual", "config": {"caja_n": 1, "caja_longitud": 1.0, "caja_masa": 1.0,
                                                "caja_sistema": "SI", "caja_puntos": 1500}},
    {"titulo": "Confinamiento y energía de punto cero",
     "objetivo": "Medir cómo depende E₁ del tamaño de la caja.",
     "pasos": ["Cargar la configuración (a = 1 nm, n = 1).", "Registrar E₁.", "Cambiar a a 2 nm y después a 0.5 nm."],
     "pregunta": "¿Qué ocurre con la energía mínima al hacer la caja más pequeña? ¿Puede ser cero?",
     "resultado": "E ∝ 1/a²: con 2 nm la energía se divide por 4 (≈ 0.094 eV) y con 0.5 nm se multiplica por 4 "
                  "(≈ 1.50 eV). Nunca es cero: confinar la partícula exige una incertidumbre en el momento "
                  "(Δx·Δp ≳ ħ), y por tanto energía cinética.",
     "pestana": "Estado individual", "config": {"caja_n": 1, "caja_longitud": 1.0, "caja_masa": 1.0, "caja_sistema": "SI"}},
    {"titulo": "Nodos y longitud de onda de De Broglie",
     "objetivo": "Relacionar n con el número de nodos y con λ.",
     "pasos": ["Cargar la configuración (n = 4).", "Contar los nodos interiores en la gráfica de |ψ|².",
               "Registrar λ y compararla con a."],
     "pregunta": "¿Cuántos nodos tiene el estado n = 4? ¿Cuántas semilongitudes de onda caben en la caja?",
     "resultado": "Tiene n − 1 = 3 nodos interiores (en a/4, a/2 y 3a/4) y caben n = 4 semilongitudes de onda: "
                  "λ = 2a/n = 0.5 nm para a = 1 nm.",
     "pestana": "Estado individual", "config": {"caja_n": 4, "caja_longitud": 1.0}},
    {"titulo": "Interferencia de dos estados",
     "objetivo": "Ver que la densidad de una superposición se mueve y medir la probabilidad en media caja.",
     "pasos": ["Cargar la configuración (estados 1 y 2 con el mismo peso, región [0, 0.5]a).",
               "Registrar P en [0, 0.5a] para τ = 0.", "Mover τ hasta ≈ 1.05 (= π/3) y registrar de nuevo.",
               "Reproducir la animación."],
     "pregunta": "¿Puede la probabilidad de estar en la mitad izquierda ser distinta de 50 %? ¿Cambiar con el tiempo?",
     "resultado": "Sí: en τ = 0 vale ≈ 92.4 % (= ½ + 4/(3π)) porque la interferencia concentra la densidad a la "
                  "izquierda; en τ = π/3 pasa a ≈ 7.6 %. La densidad oscila de un lado a otro con periodo Δτ = 2π/3. "
                  "Con un solo estado siempre sería 50 %.",
     "pestana": "Superposición e interferencia",
     "config": {"caja_sup_cantidad": 2, "caja_sup_modo": "Amplitud y fase", "caja_sup_normalizar": True,
                "caja_sup_n1": 1, "caja_sup_n2": 2, "caja_sup_A1": 1.0, "caja_sup_A2": 1.0,
                "caja_sup_fase1": 0.0, "caja_sup_fase2": 0.0, "caja_sup_tau": 0.0, "caja_sup_region": (0.0, 0.5)}},
    {"titulo": "Reaparición cuántica",
     "objetivo": "Comprobar que cualquier superposición vuelve a su forma inicial.",
     "pasos": ["Cargar la configuración (estados 1, 2 y 3).", "Observar |Ψ|² en τ = 0.",
               "Llevar τ a 3.14 (= π) y después al final, τ = 2π."],
     "pregunta": "¿Por qué el estado vuelve a ser exactamente el mismo en τ = 2π?",
     "resultado": "Porque Eₙ = n²E₁: todas las fases e^(−in²τ) valen 1 a la vez cuando τ = 2π. En τ = π las fases valen "
                  "(−1)ⁿ y, como ψₙ(a − x) = (−1)ⁿ⁺¹ψₙ(x), la densidad aparece reflejada respecto al centro de la caja.",
     "pestana": "Superposición e interferencia",
     "config": {"caja_sup_cantidad": 3, "caja_sup_modo": "Amplitud y fase", "caja_sup_normalizar": True,
                "caja_sup_n1": 1, "caja_sup_n2": 2, "caja_sup_n3": 3, "caja_sup_A1": 1.0, "caja_sup_A2": 1.0,
                "caja_sup_A3": 1.0, "caja_sup_fase1": 0.0, "caja_sup_fase2": 0.0, "caja_sup_fase3": 0.0,
                "caja_sup_tau": 0.0}},
]

PREGUNTAS = [
    {"enunciado": "Si la caja mide a y el estado es n = 3, ¿cuántos nodos interiores tiene ψ₃?",
     "opciones": ["0", "2", "3", "6"], "correcta": 1,
     "explicacion": "El estado n tiene n − 1 nodos interiores: ψ₃ se anula en a/3 y 2a/3."},
    {"enunciado": "¿Qué le ocurre a la energía del estado fundamental si se duplica la longitud de la caja?",
     "opciones": ["Se duplica", "No cambia", "Se divide por 2", "Se divide por 4"], "correcta": 3,
     "explicacion": "Eₙ = n²π²ħ²/(2ma²) ∝ 1/a²."},
    {"enunciado": "¿Por qué la energía mínima de la partícula en la caja no puede ser cero?",
     "opciones": ["Porque la caja tiene paredes de energía infinita",
                  "Porque confinarla en un tamaño a exige un momento no nulo (principio de incertidumbre)",
                  "Porque la masa nunca es cero", "Sí puede ser cero si n = 0"], "correcta": 1,
     "explicacion": "n = 0 daría ψ = 0 (no normalizable). La energía de punto cero E₁ > 0 refleja Δx·Δp ≳ ħ."},
    {"enunciado": "En un estado estacionario ψₙ e^(−iEₙt/ħ), la densidad |Ψ|²…",
     "opciones": ["oscila con frecuencia Eₙ/h", "no cambia con el tiempo", "se desplaza hacia una pared",
                  "se anula periódicamente"], "correcta": 1,
     "explicacion": "La fase global tiene módulo 1, así que |Ψ|² = |ψₙ|² en todo instante."},
    {"enunciado": "Para una superposición de ψ₁ y ψ₂, ¿cómo se obtiene la densidad de probabilidad?",
     "opciones": ["|c₁|²|ψ₁|² + |c₂|²|ψ₂|²", "|c₁ψ₁e^(−iE₁t/ħ) + c₂ψ₂e^(−iE₂t/ħ)|²",
                  "|ψ₁|² · |ψ₂|²", "(|ψ₁|² + |ψ₂|²)/2"], "correcta": 1,
     "explicacion": "Hay que sumar primero las funciones de onda y después elevar al cuadrado: así aparece el término "
                    "de interferencia, que depende de las fases y del tiempo."},
    {"enunciado": "La longitud de onda de De Broglie del estado n en una caja de longitud a es…",
     "opciones": ["a/n", "2a/n", "na/2", "2πa/n"], "correcta": 1,
     "explicacion": "Caben n semilongitudes de onda en la caja: n·λ/2 = a ⇒ λ = 2a/n."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("caja_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _sub(i: int) -> str:
    return str(i).translate(_SUB)


def _leer_parametros_fisicos():
    """Panel de parámetros comunes a todas las pestañas. Devuelve ParametrosCaja o None si hay error."""
    with st.container(border=True):
        qc.seccion("Parámetros del sistema")
        c1, c2, c3, c4 = st.columns(4)
        sistema = c1.radio("Sistema de unidades", ["SI", "Atómicas"], key="caja_sistema", horizontal=True,
                           help="SI: a en nm, energías en eV. Atómicas: a en a₀, energías en Eₕ. La masa siempre en mₑ.")
        u = qc.obtener_unidades(sistema)
        longitud = c2.number_input(f"Longitud de la caja a [{u['nombre_longitud']}]", min_value=0.0, step=0.1,
                                   format="%.6g", key="caja_longitud")
        masa = c3.number_input("Masa m [mₑ]", min_value=0.0, step=0.1, format="%.6g", key="caja_masa",
                               help="Masa en unidades de la masa del electrón. Protón ≈ 1836.15.")
        puntos = c4.slider("Puntos de la malla", PUNTOS_MIN, 10000, step=100, key="caja_puntos",
                           help="Se necesitan al menos 20·n puntos para resolver bien las oscilaciones.")
        qc.pie_de_parametros(DEMOS, "caja_demo", _aplicar_demo, VALORES_INICIALES, "caja_reset")
    try:
        # Se validan a, m, unidades y puntos (con n = 1); n se valida en cada pestaña.
        return validar_parametros_caja(1, longitud, masa, sistema, puntos)
    except ValueError as error:
        qc.error(error)
        return None


def _pestana_individual(p_base: ParametrosCaja):
    c1, _, _, _ = st.columns(4)
    n = c1.number_input("Número cuántico n", min_value=1, max_value=N_MAX, step=1, key="caja_n")
    try:
        p = validar_parametros_caja(n, st.session_state["caja_longitud"], st.session_state["caja_masa"],
                                    st.session_state["caja_sistema"], st.session_state["caja_puntos"])
    except ValueError as error:
        qc.error(error)
        return
    d = calcular_estado_individual(p)
    u = qc.obtener_unidades(p.sistema)
    fx, L, U = u["factor_longitud"], u["nombre_longitud"], u["nombre_energia"]

    qc.seccion("Resultados")
    qc.metricas([
        (f"Energía E{_sub(p.n)} [{U}]", qc.cientifico(d["energia"] / u["factor_energia"], 5),
         qc.texto_energia(d["energia"], p.sistema)),
        (f"Longitud de onda λ [{L}]", f"{d['lambda_db'] / fx:.5g}", "λ = h/|p| = 2a/n"),
        ("Nodos interiores", f"{p.n - 1}", "Puntos interiores con ψ = 0. El estado n tiene n − 1."),
        ("Normalización ∫|ψ|²dx", f"{d['norma']:.10f}", f"Desviación respecto de 1: {d['norma'] - 1:+.1e}"),
    ])
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_estado_individual(d, p), archivo=f"caja_estado_n{p.n}.png")
    qc.exportar_datos({"x [m]": d["x"], "psi [m^-1/2]": d["psi"], "rho = |psi|^2 [1/m]": d["rho"],
                       "V [J]": np.zeros_like(d["x"]), "E_n [J]": np.full_like(d["x"], d["energia"])},
                      f"caja_datos_n{p.n}.csv")

    with st.expander("Valores numéricos detallados", expanded=False):
        nodos_txt = "ninguno" if p.n == 1 else ", ".join(f"{v / fx:.5g}" for v in d["nodos"])
        max_txt = ", ".join(f"{v / fx:.5g}" for v in d["maximos"])
        qc.tabla([
            ("Número cuántico n", f"{p.n}", ""),
            ("Energía Eₙ", qc.cientifico(d["energia"] / u["factor_energia"], 8), U),
            ("Energía Eₙ", qc.cientifico(d["energia"], 8), "J"),
            ("Momento |pₙ| = nπħ/a", qc.cientifico(d["momento"], 6), "kg·m/s"),
            ("Longitud de onda de De Broglie 2a/n", f"{d['lambda_db'] / fx:.8g}", L),
            ("Semilongitudes de onda en la caja", f"{p.n}", ""),
            ("Nodos interiores", nodos_txt, L, f"{p.n - 1} nodos"),
            ("Máximos de |ψ|²", max_txt, L, f"{p.n} máximos"),
            ("Normalización numérica ∫|ψ|²dx", f"{d['norma']:.12f}", "", f"error {abs(d['norma'] - 1):.2e}"),
        ], archivo=f"caja_valores_n{p.n}.csv")
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- Un **estado estacionario** tiene energía definida; su densidad |ψₙ|² **no cambia con el tiempo**: "
            "solo evoluciona la fase global e^(−iEₙt/ħ).\n"
            "- Los **nodos** son puntos interiores donde la probabilidad de encontrar la partícula es nula; "
            "el estado n tiene exactamente n − 1.\n"
            "- La **longitud de onda de De Broglie** λₙ = h/|pₙ| = 2a/n es la de cada onda viajera (+p y −p) "
            "cuya superposición forma la onda estacionaria. **No** es una trayectoria clásica.\n"
            "- La energía crece como n² y como 1/a²: confinar más la partícula la hace más energética "
            "(energía de punto cero E₁ > 0, consecuencia del principio de incertidumbre).")


def _leer_superposicion():
    """Rejilla de estados a superponer (una fila por estado). Devuelve (numeros, coeficientes)."""
    lista = st.text_area("Lista rápida de estados (opcional, hasta 200)", key="caja_sup_lista", height=68,
                         placeholder="1:1; 2:0.5; 7:-0.3; 12:0.2:1.57",
                         help="Un estado por elemento, separados por «;» o por líneas. Formato n:A (fase 0) o n:A:φ "
                              "(φ en radianes): cₙ = A·e^{iφ}. Si no está vacía, sustituye a la tabla.")
    if lista.strip():
        st.caption("Se usa la lista rápida; la tabla de abajo está desactivada mientras la lista no esté vacía.")
        return leer_lista_estados(lista)
    c1, c2, c3, _ = st.columns(4, vertical_alignment="bottom")
    cantidad = c1.number_input("Número de estados a superponer", min_value=1, max_value=ESTADOS_MAX, step=1, key="caja_sup_cantidad",
                               help=f"Cuántos estados se superponen (1 a {ESTADOS_MAX}). Para más, usar la lista rápida (hasta {N_MAX}).")
    modo = c2.radio("Coeficientes cₙ", ["Amplitud y fase", "Parte real e imaginaria"], key="caja_sup_modo",
                    help="cₙ = Aₙ·e^{iφₙ}  o  cₙ = Re + i·Im")
    c3.toggle("Normalizar coeficientes", key="caja_sup_normalizar",
              help="Divide cada cₙ entre √Σ|cₙ|² para que Σ|cₙ|² = 1.")
    amplitud_fase = modo == "Amplitud y fase"
    anchos = [0.7, 1.0, 2.0, 2.0]
    cab = st.columns(anchos)
    for col, texto in zip(cab, ["Estado", "Número cuántico n",
                                "Amplitud Aₙ" if amplitud_fase else "Parte real Re cₙ",
                                "Fase φₙ [rad]" if amplitud_fase else "Parte imaginaria Im cₙ"]):
        col.caption(texto)
    numeros, amplitudes, fases, res, ims = [], [], [], [], []
    for i in range(1, cantidad + 1):
        f0, f1, f2, f3 = st.columns(anchos, vertical_alignment="center")
        f0.markdown(f"**ψ{_sub(i)}**")
        numeros.append(f1.number_input(f"n{i}", min_value=1, max_value=N_MAX, step=1, key=f"caja_sup_n{i}",
                                       label_visibility="collapsed"))
        if amplitud_fase:
            amplitudes.append(f2.number_input(f"A{i}", min_value=0.0, step=0.05, format="%.4f", key=f"caja_sup_A{i}",
                                              label_visibility="collapsed"))
            fases.append(f3.number_input(f"φ{i}", min_value=-100.0, max_value=100.0, step=0.1, format="%.4f",
                                         key=f"caja_sup_fase{i}", label_visibility="collapsed"))
        else:
            res.append(f2.number_input(f"Re c{i}", step=0.1, format="%.4f", key=f"caja_sup_re{i}",
                                       label_visibility="collapsed"))
            ims.append(f3.number_input(f"Im c{i}", step=0.1, format="%.4f", key=f"caja_sup_im{i}",
                                       label_visibility="collapsed"))
    coef = coeficientes_desde_amplitud_fase(amplitudes, fases) if amplitud_fase else coeficientes_desde_re_im(res, ims)
    return numeros, coef


@st.cache_data(show_spinner="Calculando la animación…", max_entries=12)
def _animacion_cacheada(numeros, coef_re, coef_im, longitud, masa, sistema, n_cuadros):
    """Construye (y guarda en caché) la figura animada de una superposición."""
    p = ParametrosCaja(1, longitud, masa, sistema, 500)
    sup = construir_superposicion(list(numeros), np.array(coef_re) + 1j * np.array(coef_im), normalizar=False)
    x, taus, re, im, rho = serie_temporal(p, sup, n_cuadros, 500)
    et = _etiquetas_unidades(sistema)
    u = et["u"]
    etiquetas = [f"τ = {t:.2f} (t = {tiempo_desde_tau(t, longitud, masa) / u['factor_tiempo']:.3g} {u['nombre_tiempo']})"
                 for t in taus]
    return figura_animacion_superposicion(x / et["fx"], taus, re * np.sqrt(et["fx"]), im * np.sqrt(et["fx"]),
                                          rho * et["fx"], et["L"], etiquetas)


@st.cache_data(show_spinner="Calculando el experimento…", max_entries=8)
def _experimento_cacheado(longitud, masa, sistema, n_cuadros):
    p = ParametrosCaja(1, longitud, masa, sistema, 500)
    numeros, coef = parametros_experimento()
    sup12 = construir_superposicion(numeros, coef)
    x, taus, _, _, rho12 = serie_temporal(p, sup12, n_cuadros, 500)
    et = _etiquetas_unidades(sistema)
    u = et["u"]
    rho1 = funcion_onda(x, 1, longitud) ** 2 * et["fx"]
    rho2 = funcion_onda(x, 2, longitud) ** 2 * et["fx"]
    etiquetas = [f"τ = {t:.2f} (t = {tiempo_desde_tau(t, longitud, masa) / u['factor_tiempo']:.3g} {u['nombre_tiempo']})"
                 for t in taus]
    return figura_experimento(x / et["fx"], rho1, rho2, rho12 * et["fx"], rho12[0] * et["fx"], taus, et["L"],
                              etiquetas)


def _pestana_superposicion(p_base: ParametrosCaja):
    with st.container(border=True):
        qc.seccion("Estados superpuestos")
        try:
            numeros, coef_crudos = _leer_superposicion()
        except ValueError as error:
            numeros, coef_crudos = None, None
            qc.error(error)
        qc.seccion("Tiempo y análisis")
        t1, t2 = st.columns(2)
        tau = t1.slider("Tiempo adimensional τ = E₁t/ħ", 0.0, float(2 * np.pi), step=0.01, format="%.3f",
                        key="caja_sup_tau", help="τ = 2π es un periodo completo de reaparición.")
        region = t2.slider("Región de integración [fracción de a]", 0.0, 1.0, step=0.01, key="caja_sup_region")
        o1, o2 = st.columns(2)
        comparar = o1.toggle("Mostrar densidades individuales", key="caja_sup_comparar")
        extremos = o2.toggle("Marcar máximos, mínimos y zonas de alta probabilidad", key="caja_sup_extremos")
    if numeros is None:
        return
    normalizar = st.session_state["caja_sup_normalizar"]
    try:
        p = ParametrosCaja(1, p_base.longitud, p_base.masa, p_base.sistema, p_base.puntos)
        if region[0] >= region[1]:
            raise ValueError("En la región, el inicio debe ser menor que el fin.")
        sup = construir_superposicion(numeros, coef_crudos, normalizar)
        if p_base.puntos < PUNTOS_POR_N * int(np.max(sup.numeros)):
            raise ValueError(f"Con n = {int(np.max(sup.numeros))} se necesitan al menos "
                             f"{PUNTOS_POR_N * int(np.max(sup.numeros))} puntos en la malla.")
        d = calcular_superposicion(p, sup, tau, region)
    except ValueError as error:
        qc.error(error)
        return
    u = qc.obtener_unidades(p.sistema)
    fe, U = u["factor_energia"], u["nombre_energia"]

    texto = "**Normalización.** " + descripcion_normalizacion(sup)
    if todos_reales(sup.coeficientes) and len(sup.numeros) > 1:
        texto += ("  \n**Coeficientes reales.** Equivale a elegir la fase inicial de cada estado (φₙ = 0 o π): es "
                  "una elección de condiciones iniciales, no una restricción física general.")
    qc.nota(texto)

    qc.seccion("Resultados en el instante seleccionado")
    qc.metricas([
        ("Σ|cₙ|²", f"{d['suma_c2']:.8f}"),
        ("∫|Ψ|² dx", f"{d['norma_espacial']:.8f}"),
        (f"P en [{region[0]:.2f}a, {region[1]:.2f}a]", f"{d['prob_region']:.6f}"),
        (r"$\langle x\rangle / a$", f"{d['x_media'] / p.longitud:.5f}"),
        (rf"$\langle E\rangle$ [{U}]", f"{d['e_media'] / fe:.5g}"),
        (f"ΔE [{U}]", f"{d['delta_e'] / fe:.5g}"),
        (f"t [{u['nombre_tiempo']}]", f"{d['tiempo'] / u['factor_tiempo']:.5g}"),
        ("Máximos / mínimos de ρ", f"{len(d['x_max'])} / {len(d['x_min'])}"),
    ])
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_superposicion(d, p, sup, region, comparar, extremos), archivo="caja_superposicion.png")
    qc.exportar_datos({"x [m]": d["x"], "Psi [m^-1/2]": d["psi"], "rho = |Psi|^2 [1/m]": d["rho"]},
                      "caja_superposicion_datos.csv", "Descargar Ψ y |Ψ|² en este instante (CSV)")
    if len(d["x_min"]) and not np.any(d["nodal"]):
        st.caption("Los mínimos locales de ρ no llegan a cero: en una superposición de energías distintas la "
                   "densidad generalmente no tiene nodos verdaderos (a diferencia de un estado estacionario).")
    if extremos and d["regiones"]:
        txt = ", ".join(f"[{i / u['factor_longitud']:.4g}, {f / u['factor_longitud']:.4g}]" for i, f in d["regiones"])
        st.caption(f"Regiones de probabilidad elevada (ρ ≥ 75 % del máximo) en {u['nombre_longitud']}: {txt}")

    qc.seccion("Coeficientes")
    qc.tabla_libre([{"n": int(k), "cₙ": f"{c.real:+.4f} {c.imag:+.4f}i", "|cₙ|²": f"{abs(c) ** 2:.6f}",
                     "arg cₙ [rad]": f"{np.angle(c):+.4f}",
                     f"Eₙ [{U}]": f"{energia_nivel(int(k), p.longitud, p.masa) / fe:.6g}"}
                    for k, c in zip(sup.numeros, sup.coeficientes)],
                   numericas=("n", "cₙ", "|cₙ|²", "arg cₙ [rad]", f"Eₙ [{U}]"), archivo="caja_coeficientes.csv")

    with st.expander("Animación temporal de la interferencia (un periodo completo)", expanded=True):
        st.caption("Pulsar «Reproducir». La animación se ejecuta en el navegador y no bloquea la aplicación. "
                   "Se muestra la función de onda compleja (Re y Im) y la densidad |Ψ|².")
        try:
            figura = _animacion_cacheada(tuple(int(k) for k in sup.numeros),
                                         tuple(float(c.real) for c in sup.coeficientes),
                                         tuple(float(c.imag) for c in sup.coeficientes),
                                         p.longitud, p.masa, p.sistema, 72)
            qc.mostrar_plotly(figura, clave="caja_anim_sup", archivo="caja_animacion.html")
        except ValueError as error:
            qc.error(error)


def _pestana_experimento(p_base: ParametrosCaja):
    c1, _, c3 = st.columns([3, 0.2, 1], vertical_alignment="center")
    c1.markdown("Comparar el estado **n = 1**, el estado **n = 2** y la **superposición 1 + 2** con coeficientes "
                "iguales (c₁ = c₂ = 1/√2). Pulsar «Reproducir» para ver evolucionar el tiempo.")
    c3.button("Abrir en «Superposición»", on_click=qc.fijar_estado, args=(EXPERIMENTO_EN_SUPERPOSICION,),
              icon=":material/open_in_new:", width="stretch", key="caja_exp_cargar")
    qc.seccion("Visualización")
    figura = _experimento_cacheado(p_base.longitud, p_base.masa, p_base.sistema, 72)
    qc.mostrar_plotly(figura, clave="caja_anim_exp", archivo="caja_experimento.html")

    a = p_base.longitud
    x = malla_caja(a, 2000)
    numeros, coef = parametros_experimento()
    taus = np.linspace(0.0, 2 * np.pi, 49)
    filas = []
    for nombre, ns in (("Estado n = 1", [1]), ("Estado n = 2", [2]), ("Superposición 1 + 2", numeros)):
        s = construir_superposicion(ns, coef if len(ns) == 2 else [1.0])
        filas.append((nombre, f"{variacion_temporal_maxima(x, s.numeros, s.coeficientes, a, taus):.4g}", "",
                      "estacionario" if len(ns) == 1 else "evoluciona"))
    qc.seccion("Comprobación numérica")
    qc.tabla(filas, encabezados=("Sistema", "Variación máxima de ρ·a en un periodo", "", "Comportamiento"),
             archivo="caja_experimento.csv")
    with st.expander("Interpretación física", expanded=True):
        st.markdown(
            "- Un **estado estacionario** conserva su densidad: la variación es ≈ 0 (solo gira la fase global).\n"
            "- En la **superposición de energías distintas** aparece el término de interferencia "
            "2·Re[c₁*c₂ ψ₁ψ₂ e^{−i(E₂−E₁)t/ħ}], que oscila con frecuencia (E₂−E₁)/ħ: "
            "la densidad se mueve de un lado a otro de la caja con periodo Δτ = 2π/3.\n"
            "- Si ambos estados tuvieran la misma energía no habría evolución; la interferencia depende de las "
            "diferencias de energía, no de las energías absolutas.")


def interfaz() -> None:
    """Página completa del simulador 1 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 01", "Partícula en una caja unidimensional",
                         "Pozo de potencial infinito: estados estacionarios, niveles de energía, "
                         "superposición e interferencia cuántica.")
    qc.enlace_teoria("caja")
    qc.ficha_simulador(
        "Relacionar el número cuántico n con la energía, los nodos y la forma de ψ, y observar la interferencia "
        "de una superposición de estados.",
        r"\begin{gathered}\psi_n(x)=\sqrt{\tfrac{2}{a}}\,\sin\!\left(\tfrac{n\pi x}{a}\right)\\[4pt]"
        r"E_n=\dfrac{n^2\pi^2\hbar^2}{2ma^2}\end{gathered}",
        [("n", "número cuántico, entero ≥ 1"), ("a", "longitud de la caja"), ("m", "masa de la partícula"),
         ("E", "energía del estado")],
        "Pozo infinito unidimensional, estados estacionarios exactos; resultados numéricos calculados, "
        "sin aproximaciones adicionales.")
    p_base = _leer_parametros_fisicos()
    if p_base is None:
        return
    tabs = st.tabs(["Estado individual", "Superposición e interferencia", "Experimento 1, 2 y 1 + 2", "Guía de práctica",
                    "Autoevaluación", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_individual(p_base)
    with tabs[1]:
        _pestana_superposicion(p_base)
    with tabs[2]:
        _pestana_experimento(p_base)
    with tabs[3]:
        qc.guia_practica(GUIA, "caja")
    with tabs[4]:
        qc.autoevaluacion(PREGUNTAS, "caja")
    with tabs[5]:
        qc.boton_pruebas(ejecutar_pruebas, "caja_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Partícula en una caja", ":material/science:", "particula_caja.py")
