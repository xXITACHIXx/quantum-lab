"""
instrumentos.py — Instrumentos de medición y análisis reutilizables
===================================================================

Herramientas de lectura sobre los datos que YA calculó un simulador. Cada instrumento declara qué mide y qué no:

    · Cursor: lee el valor de una función calculada en una posición (interpolación lineal). NO es una medición
      experimental ni una trayectoria de la partícula.
    · Intervalo: integra la densidad de probabilidad entre dos posiciones (regla del trapecio) y la compara con la
      integral exacta cuando existe. La diferencia es **error numérico** del cálculo, no incertidumbre experimental.
    · Fotón entre niveles: ΔE → ν y λ de un fotón que cumpliría la conservación de la energía en la transición.
      Es un cálculo teórico del modelo; no predice intensidades ni reglas de selección.
    · Comparación: diferencia absoluta y relativa entre un valor de referencia y el calculado.

La parte numérica no usa Streamlit (se prueba con pytest); los paneles de interfaz están al final.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np
from scipy import constants as const

import quantum_lab_comun as qc

H = const.h          # J·s
C = const.c          # m/s


# =====================================================================
# Cálculo
# =====================================================================
def leer_valor(x, y, x0: float) -> float:
    """Valor de la función tabulada (x, y) en x0 por interpolación lineal. Lanza ValueError fuera del dominio."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.size < 2:
        raise ValueError("Las coordenadas y los valores deben tener la misma longitud (≥ 2).")
    if not math.isfinite(x0) or x0 < x[0] or x0 > x[-1]:
        raise ValueError(f"La posición {x0:g} está fuera del dominio [{x[0]:g}, {x[-1]:g}].")
    return float(np.interp(x0, x, y))


def probabilidad_intervalo(x, rho, x1: float, x2: float) -> float:
    """∫ρ dx entre x1 y x2 (regla del trapecio con los extremos interpolados). ρ es una densidad en 1/longitud."""
    x = np.asarray(x, dtype=float)
    rho = np.asarray(rho, dtype=float)
    if not (math.isfinite(x1) and math.isfinite(x2)) or x1 >= x2:
        raise ValueError("El intervalo debe cumplir x₁ < x₂.")
    if x1 < x[0] or x2 > x[-1]:
        raise ValueError(f"El intervalo [{x1:g}, {x2:g}] sale del dominio [{x[0]:g}, {x[-1]:g}].")
    dentro = (x > x1) & (x < x2)
    xs = np.concatenate(([x1], x[dentro], [x2]))
    ys = np.concatenate(([np.interp(x1, x, rho)], rho[dentro], [np.interp(x2, x, rho)]))
    return float(np.trapezoid(ys, xs))


def probabilidad_caja_exacta(n: int, a: float, x1: float, x2: float) -> float:
    """Integral exacta de |ψₙ|² = (2/a) sen²(nπx/a): [x/a − sen(2nπx/a)/(2nπ)] entre x1 y x2."""
    if n < 1 or a <= 0 or not 0 <= x1 < x2 <= a:
        raise ValueError("Se requiere n ≥ 1, a > 0 y 0 ≤ x₁ < x₂ ≤ a.")

    def primitiva(x):
        return x / a - math.sin(2 * n * math.pi * x / a) / (2 * n * math.pi)

    return primitiva(x2) - primitiva(x1)


def probabilidad_angular(densidad: Callable, theta1: float, theta2: float, phi1: float, phi2: float, n: int = 400) -> float:
    """∫∫ |Y|² senθ dθ dφ sobre la región [θ₁,θ₂]×[φ₁,φ₂] (regla del trapecio). `densidad(theta, phi)` en sr⁻¹."""
    if not all(math.isfinite(v) for v in (theta1, theta2, phi1, phi2)):
        raise ValueError("Los ángulos deben ser finitos.")
    if not (0 <= theta1 < theta2 <= math.pi):
        raise ValueError("Se requiere 0 ≤ θ₁ < θ₂ ≤ π.")
    if not phi1 < phi2:
        raise ValueError("Se requiere φ₁ < φ₂.")
    if phi2 - phi1 > 2 * math.pi + 1e-12:
        raise ValueError("El intervalo en φ no puede superar 2π.")
    th = np.linspace(theta1, theta2, n)
    ph = np.linspace(phi1, phi2, n)
    tt, pp = np.meshgrid(th, ph, indexing="ij")
    f = np.asarray(densidad(tt, pp), dtype=float) * np.sin(tt)
    return float(np.trapezoid(np.trapezoid(f, ph, axis=1), th))


def comparar(calculado: float, referencia: float) -> dict:
    """Diferencia absoluta y relativa entre el valor calculado y uno de referencia (≠ 0)."""
    if not (math.isfinite(calculado) and math.isfinite(referencia)):
        raise ValueError("Los valores deben ser finitos.")
    if referencia == 0:
        raise ValueError("La referencia no puede ser cero para calcular una diferencia relativa.")
    d = calculado - referencia
    return {"absoluta": d, "relativa": d / abs(referencia)}


def foton_entre_niveles(energia_inicial_j: float, energia_final_j: float) -> dict:
    """
    Fotón asociado a una transición: |ΔE| = hν = hc/λ. Emisión si E_inicial > E_final; absorción si es menor.
    Devuelve energía (J y eV), frecuencia (Hz), longitud de onda (m y nm) y región espectral.
    """
    if not (math.isfinite(energia_inicial_j) and math.isfinite(energia_final_j)):
        raise ValueError("Las energías deben ser finitas.")
    de = energia_final_j - energia_inicial_j
    if de == 0:
        raise ValueError("Los niveles inicial y final deben ser distintos: una transición requiere un cambio de energía.")
    e = abs(de)
    nu = e / H
    lam = C / nu
    return {"tipo": "Emisión" if de < 0 else "Absorción", "energia_j": e, "energia_ev": e / qc.E_CARGA,
            "frecuencia": nu, "longitud_m": lam, "longitud_nm": lam * 1e9, "region": qc.region_espectral(lam * 1e9)}


# =====================================================================
# Interfaz
# =====================================================================
def panel_fotones(energia_nivel_j: Callable[[int], float], prefijo: str, n_max: int, n_ini: int = 3, n_fin: int = 1) -> None:
    """Instrumento «Fotón entre niveles» para cualquier sistema con niveles discretos (energía en julios)."""
    import streamlit as st

    st.markdown("**Qué mide:** la energía, la frecuencia y la longitud de onda de un fotón que cumpliría la "
                "conservación de la energía entre dos niveles. **Qué no mide:** la probabilidad ni la intensidad "
                "de la transición, ni si está permitida por las reglas de selección.")
    c1, c2, c3 = st.columns(3)
    ni = c1.number_input("Nivel inicial", 1, n_max, n_ini, 1, key=f"{prefijo}_foton_ni")
    nf = c2.number_input("Nivel final", 1, n_max, n_fin, 1, key=f"{prefijo}_foton_nf")
    ref = c3.number_input("λ de referencia [nm] (opcional)", 0.0, 1e9, 0.0, key=f"{prefijo}_foton_ref",
                          help="Si la indicas, se muestra la diferencia entre el cálculo y tu valor. 0 = sin comparación.")
    try:
        f = foton_entre_niveles(energia_nivel_j(int(ni)), energia_nivel_j(int(nf)))
    except ValueError as error:
        qc.error(error)
        return
    qc.metricas([("Tipo", f["tipo"], f"n = {int(ni)} → {int(nf)}"),
                 ("Energía del fotón [eV]", qc.cientifico(f["energia_ev"], 6), qc.cientifico(f["energia_j"], 6) + " J"),
                 ("Frecuencia ν [Hz]", qc.cientifico(f["frecuencia"], 6), "ν = |ΔE|/h"),
                 ("Longitud de onda λ [nm]", qc.cientifico(f["longitud_nm"], 6), f["region"])], columnas=4)
    st.latex(rf"\lambda=\dfrac{{hc}}{{|\Delta E|}}={qc.cientifico(f['longitud_nm'], 6)}\ \mathrm{{nm}}")
    if ref > 0:
        c = comparar(f["longitud_nm"], ref)
        st.info(f"Diferencia con la referencia: {c['absoluta']:+.6g} nm ({c['relativa'] * 100:+.4g} %). "
                "Es la diferencia entre dos valores, no una incertidumbre experimental.", icon=":material/compare_arrows:")
