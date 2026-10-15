"""
verificacion.py — Página «Verificación»
=======================================

Compara cada simulador con una referencia INDEPENDIENTE de su propio código:

    · Diagonalización numérica del hamiltoniano (caja y oscilador): se resuelve H·ψ = E·ψ en una malla con
      scipy.linalg.eigh_tridiagonal, sin usar la fórmula de Eₙ.
    · Derivadas en diferencias finitas (armónicos esféricos): se comprueba L²Y = ħ²l(l+1)Y aplicando el
      operador angular a Y, sin usar el número l(l+1).
    · Integrales numéricas (⟨r⟩ del hidrógeno, ⟨x²⟩ del oscilador, normalizaciones y ortogonalidad).
    · Fórmulas cerradas y valores tabulados escritos aparte (CODATA 2018), con la fuente indicada.

La física es pura (NumPy/SciPy); la interfaz (Streamlit) está al final y solo presenta la tabla.
También se usa desde pytest: `casos_de_verificacion()` devuelve una lista de diccionarios.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from scipy.linalg import eigh_tridiagonal

import efecto_fotoelectrico as foto
import modelo_bohr as bohr
import oscilador_armonico as osc
import particula_caja as caja
import particula_esfera as esf
import principio_incertidumbre as inc
import quantum_lab_comun as qc
from quantum_lab_comun import HBAR, M_E, E_CARGA

# ---------------------------------------------------------------------
# 1. FÍSICA (referencias independientes)
# ---------------------------------------------------------------------
TOL_EXACTA = 1e-10         # fórmulas cerradas frente a fórmulas cerradas
TOL_TABLA = 2e-6           # valores tabulados con 7 cifras
TOL_NUMERICA = 1e-4        # diagonalización, diferencias finitas y cuadraturas


def energias_caja_numericas(a: float, masa: float, k: int = 3, n_puntos: int = 2000) -> np.ndarray:
    """Primeros `k` autovalores de H = −ħ²/(2m) d²/dx² en (0, a) con ψ = 0 en los extremos (diferencias finitas)."""
    h = a / (n_puntos + 1)
    diagonal = np.full(n_puntos, HBAR ** 2 / (masa * h ** 2))
    fuera = np.full(n_puntos - 1, -HBAR ** 2 / (2 * masa * h ** 2))
    return eigh_tridiagonal(diagonal, fuera, select="i", select_range=(0, k - 1), eigvals_only=True)


def energias_oscilador_numericas(k: int = 4, extension: float = 12.0, n_puntos: int = 4001) -> np.ndarray:
    """Primeros `k` autovalores de H/(ħω) = −½ d²/dξ² + ½ ξ² (adimensional, diferencias finitas)."""
    xi = np.linspace(-extension, extension, n_puntos)
    h = xi[1] - xi[0]
    return eigh_tridiagonal(1.0 / h ** 2 + 0.5 * xi ** 2, np.full(n_puntos - 1, -0.5 / h ** 2),
                            select="i", select_range=(0, k - 1), eigvals_only=True)


def autovalor_l2_numerico(l: int, m: int, theta: float = 0.7, phi: float = 0.3, h: float = 1e-3) -> float:
    """
    L²Y/(ħ²Y) = −[∂θ²Y + cotθ ∂θY + ∂φ²Y / sin²θ] / Y, con las derivadas por diferencias finitas centradas.
    Si Y es autofunción de L², el cociente es l(l+1) en cualquier punto.
    """
    def Y(t, p):
        return complex(esf.armonico_esferico(l, m, t, p))
    y0 = Y(theta, phi)
    dt = (Y(theta + h, phi) - Y(theta - h, phi)) / (2 * h)
    dtt = (Y(theta + h, phi) - 2 * y0 + Y(theta - h, phi)) / h ** 2
    dpp = (Y(theta, phi + h) - 2 * y0 + Y(theta, phi - h)) / h ** 2
    return float(np.real(-(dtt + dt / np.tan(theta) + dpp / np.sin(theta) ** 2) / y0))


def r_medio_numerico(n: int, l: int, r_max_a0: float = 80.0, puntos: int = 200001) -> float:
    """⟨r⟩ = ∫ r³ R_nl² dr por la regla del trapecio (independiente de la fórmula (a/2)[3n² − l(l+1)])."""
    r = np.linspace(0.0, r_max_a0 * bohr.A0, puntos)
    R = bohr.radial_hidrogeno(r, n, l)
    return float(np.trapezoid(r ** 3 * R ** 2, r) if hasattr(np, "trapezoid") else np.trapz(r ** 3 * R ** 2, r))


def _trapecio(y, x) -> float:
    return float(np.trapezoid(y, x) if hasattr(np, "trapezoid") else np.trapz(y, x))


def _fila(sistema, caso, magnitud, unidad, simulador, referencia, metodo, tolerancia):
    simulador, referencia = float(simulador), float(referencia)
    error = abs(simulador - referencia) / abs(referencia) if referencia != 0 else abs(simulador - referencia)
    return {"sistema": sistema, "caso": caso, "magnitud": magnitud, "unidad": unidad, "simulador": simulador,
            "referencia": referencia, "metodo": metodo, "error": error, "tolerancia": tolerancia,
            "ok": bool(error <= tolerancia)}


def casos_de_verificacion() -> list[dict]:
    """Lista de comparaciones simulador ↔ referencia. Cada elemento incluye error relativo, tolerancia y `ok`."""
    f = []
    # ---- Partícula en una caja: electrón, a = 1 nm
    a = 1e-9
    num = energias_caja_numericas(a, M_E, 3)
    S = "Partícula en una caja"
    caso = "electrón, a = 1 nm"
    f.append(_fila(S, caso + ", n = 1", "Energía E₁", "eV", caja.energia_nivel(1, a, M_E) / E_CARGA, 0.3760302,
                   "valor tabulado (CODATA 2018)", TOL_TABLA))
    f.append(_fila(S, caso + ", n = 1", "Energía E₁", "eV", caja.energia_nivel(1, a, M_E) / E_CARGA, num[0] / E_CARGA,
                   "diagonalización de H (2000 puntos)", TOL_NUMERICA))
    f.append(_fila(S, caso + ", n = 3", "Cociente E₃/E₁", "", caja.energia_nivel(3, a, M_E) / caja.energia_nivel(1, a, M_E),
                   num[2] / num[0], "diagonalización de H (2000 puntos)", TOL_NUMERICA))
    f.append(_fila(S, caso + ", n = 1", "Longitud de onda λ", "nm", caja.longitud_onda_de_broglie(1, a) * 1e9, 2.0,
                   "fórmula cerrada λ = 2a/n", TOL_EXACTA))
    x = caja.malla_caja(a, 20001)
    f.append(_fila(S, caso + ", n = 3", "Normalización ∫|ψ|²dx", "", _trapecio(caja.funcion_onda(x, 3, a) ** 2, x), 1.0,
                   "integral numérica (trapecio)", TOL_NUMERICA))

    # ---- Oscilador armónico: electrón, ω = 1e15 rad/s
    S = "Oscilador armónico"
    omega = 1e15
    caso = "electrón, ω = 10¹⁵ rad/s"
    en = energias_oscilador_numericas(4)
    f.append(_fila(S, caso + ", n = 0", "Energía E₀ = ħω/2", "eV", osc.energia_teorica(0, omega) / E_CARGA, 0.3291060,
                   "valor tabulado (CODATA 2018)", TOL_TABLA))
    f.append(_fila(S, caso + ", n = 2", "Cociente E₂/(ħω)", "", osc.energia_teorica(2, omega) / (HBAR * omega), en[2],
                   "diagonalización de H (4001 puntos)", TOL_NUMERICA))
    f.append(_fila(S, caso, "Longitud característica x₀", "nm", osc.longitud_caracteristica(M_E, omega) * 1e9, 0.3402464,
                   "valor tabulado (CODATA 2018)", TOL_TABLA))
    x0 = osc.longitud_caracteristica(M_E, omega)
    xs = np.linspace(-12 * x0, 12 * x0, 40001)
    psi = osc.psi_oscilador(xs, 2, M_E, omega)
    f.append(_fila(S, caso + ", n = 2", "⟨x²⟩/x₀²", "", osc.valores_esperados(xs, psi)[1] / x0 ** 2, 2.5,
                   "integral numérica; esperado (n + ½)", TOL_NUMERICA))
    dpsi = osc.derivada_analitica(xs, 2, M_E, omega)
    t_medio = osc.integrar(xs, osc.densidad_energia_cinetica(dpsi, M_E))
    f.append(_fila(S, caso + ", n = 2", "⟨T⟩/E (virial)", "", t_medio / osc.energia_teorica(2, omega), 0.5,
                   "teorema del virial: ⟨T⟩ = E/2", TOL_NUMERICA))

    # ---- Partícula en una esfera
    S = "Partícula en una esfera"
    f.append(_fila(S, "l = 2, m = 1", "L²/ħ²", "", autovalor_l2_numerico(2, 1), 6.0,
                   "operador angular por diferencias finitas; esperado l(l+1)", 1e-5))
    f.append(_fila(S, "l = 5, m = −3", "L²/ħ²", "", autovalor_l2_numerico(5, -3), 30.0,
                   "operador angular por diferencias finitas; esperado l(l+1)", 1e-5))
    f.append(_fila(S, "l = 2, m = 1", "∫|Y|² dΩ", "", abs(esf.integral_solapamiento(2, 1, 2, 1)), 1.0,
                   "cuadratura de Gauss–Legendre", TOL_EXACTA))
    f.append(_fila(S, "Y₂¹ y Y₂⁰", "|⟨Y₂¹|Y₂⁰⟩|", "", abs(esf.integral_solapamiento(2, 1, 2, 0)), 0.0,
                   "ortogonalidad: debe ser 0 (error absoluto)", TOL_EXACTA))
    R = 1e-9
    f.append(_fila(S, "n = 1, l = 0, R = 1 nm, m = mₑ", "Energía confinada", "eV",
                   esf.energia_confinada(1, 0, R, M_E) / E_CARGA, np.pi ** 2 * HBAR ** 2 / (2 * M_E * R ** 2) / E_CARGA,
                   "fórmula cerrada (cero de j₀ = π)", TOL_EXACTA))
    f.append(_fila(S, "n = 1, l = 1, R = 1 nm, m = mₑ", "Energía confinada", "eV",
                   esf.energia_confinada(1, 1, R, M_E) / E_CARGA,
                   4.493409457909064 ** 2 * HBAR ** 2 / (2 * M_E * R ** 2) / E_CARGA,
                   "primer cero de j₁ tabulado (4.4934094579)", 1e-9))

    # ---- Efecto fotoeléctrico
    S = "Efecto fotoeléctrico"
    f.append(_fila(S, "λ = 400 nm", "Energía del fotón hν", "eV", float(foto.energia_foton_ev(foto.C / 400e-9)),
                   1239.841984 / 400, "hc = 1239.841984 eV·nm", TOL_TABLA))
    f.append(_fila(S, "Φ = 2.28 eV", "Longitud de onda umbral λ₀", "nm", foto.longitud_umbral_nm(2.28),
                   1239.841984 / 2.28, "hc = 1239.841984 eV·nm", TOL_TABLA))
    f.append(_fila(S, "λ = 300 nm, Φ = 2.28 eV", "Energía cinética máxima", "eV",
                   float(foto.energia_cinetica_maxima(foto.C / 300e-9, 2.28)), 1239.841984 / 300 - 2.28,
                   "ecuación de Einstein con hc tabulado", TOL_TABLA))

    # ---- Átomo de hidrógeno (modelo de Bohr y átomo cuántico)
    S = "Átomo de hidrógeno"
    f.append(_fila(S, "n = 1, masa nuclear infinita", "Energía E₁", "eV", float(bohr.energia_nivel(1, "H")), -13.605693,
                   "valor tabulado (CODATA 2018)", TOL_TABLA))
    f.append(_fila(S, "n = 3", "Cociente E₃/E₁", "", float(bohr.energia_nivel(3) / bohr.energia_nivel(1)), 1 / 9,
                   "fórmula cerrada 1/n²", TOL_EXACTA))
    f.append(_fila(S, "n = 2", "Radio de la órbita r₂/a₀", "", float(bohr.radio_orbita(2) / bohr.A0), 4.0,
                   "fórmula cerrada n²", TOL_EXACTA))
    r_h = 10973731.568 / (1 + 1 / 1836.15267343)
    f.append(_fila(S, "3 → 2 (Hα)", "Longitud de onda en el vacío", "nm", bohr.longitud_rydberg(3, 2, "H") * 1e9,
                   36 / (5 * r_h) * 1e9, "fórmula de Rydberg con masa reducida", 1e-7))
    f.append(_fila(S, "2p (n = 2, l = 1)", "⟨r⟩/a₀", "", bohr.r_medio(2, 1) / bohr.A0, r_medio_numerico(2, 1) / bohr.A0,
                   "integral numérica de r³R²", TOL_NUMERICA))
    f.append(_fila(S, "3d (n = 3, l = 2)", "⟨r⟩/a₀", "", bohr.r_medio(3, 2) / bohr.A0, r_medio_numerico(3, 2) / bohr.A0,
                   "integral numérica de r³R²", TOL_NUMERICA))

    # ---- Principio de incertidumbre
    S = "Principio de incertidumbre"
    for tipo, kw, valor, tol, texto in (("gaussiano", {}, 0.5, 1e-6, "mínimo de Heisenberg ħ/2"),
                                        ("chirp", {"beta": 2.0}, 0.5 * np.sqrt(5), 1e-6, "½√(1 + β²)"),
                                        ("sech", {}, np.pi / 6, 1e-6, "πħ/6"),
                                        ("triangular", {}, np.sqrt(0.3), 1e-3, "√0.3 ħ (FFT: la esquina limita la precisión)")):
        p = inc.validar_paquete(tipo, 1.0, 0.0, **kw)
        d = inc.calcular_paquete(p)
        f.append(_fila(S, f"paquete {tipo}, σ = 1 nm", "Δx·Δp/ħ", "", d["producto"], valor,
                       "cálculo por FFT frente a " + texto, tol))
    return f


def resumen(casos: list[dict]) -> dict:
    """Número de comparaciones superadas, error relativo máximo y lista de fallos."""
    return {"total": len(casos), "ok": sum(c["ok"] for c in casos),
            "error_max": max(c["error"] for c in casos), "fallos": [c for c in casos if not c["ok"]]}


# ---------------------------------------------------------------------
# 2. VALORES PARA CONTRASTAR CON LOS NOTEBOOKS DE COLAB
# ---------------------------------------------------------------------
def valores_colab() -> list[tuple]:
    """(sistema, parámetros a escribir en Colab, magnitud, valor calculado aquí, unidad)."""
    a, omega = 1e-9, 1e15
    return [
        ("Caja 1D", "electrón, L = 1 nm, n = 1", "Energía E₁", f"{caja.energia_nivel(1, a, M_E) / E_CARGA:.6g}", "eV"),
        ("Caja 1D", "electrón, L = 1 nm, n = 1", "Longitud de onda λ", f"{caja.longitud_onda_de_broglie(1, a) * 1e9:.6g}", "nm"),
        ("Oscilador", "electrón, ω = 1e15 rad/s, n = 0", "ħω", f"{HBAR * omega / E_CARGA:.6g}", "eV"),
        ("Oscilador", "electrón, ω = 1e15 rad/s, n = 0", "Energía E₀", f"{osc.energia_teorica(0, omega) / E_CARGA:.6g}", "eV"),
        ("Oscilador", "electrón, ω = 1e15 rad/s, n = 0", "x₀", f"{osc.longitud_caracteristica(M_E, omega) * 1e9:.6g}", "nm"),
        ("Esfera", "l = 2, m = 1 (orbital complejo)", "L²", "6", "ħ²"),
        ("Esfera", "l = 2, m = 1 (orbital complejo)", "L_z", "1", "ħ"),
    ]


VALORES_PREDETERMINADOS = [
    ("Caja 1D", "Longitud a = 1 nm · masa = 1 mₑ · n = 1 · superposición n = 1 y 2 con coeficientes iguales"),
    ("Oscilador", "Masa = 1 mₑ · ω = 10¹⁵ rad/s · n = 0"),
    ("Esfera", "R = 1 nm · masa = 1 mₑ · l = 2 · m = 1 · orbital complejo · densidad |Y|² · lóbulos · α = 0.4 · 90 puntos en θ"),
]


# ---------------------------------------------------------------------
# 3. INTERFAZ STREAMLIT
# ---------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _casos_cacheados() -> list[dict]:
    return casos_de_verificacion()


def _formato(valor: float) -> str:
    return qc.cientifico(valor, 8) if valor != 0 and (abs(valor) < 1e-3 or abs(valor) >= 1e6) else f"{valor:.8g}"


def ejecutar_pruebas() -> qc.RegistroPruebas:
    """Una prueba por comparación (se usa en pytest y en la pestaña de pruebas globales)."""
    reg = qc.RegistroPruebas("Verificación")
    for c in casos_de_verificacion():
        reg.comprobar(f"{c['sistema']} · {c['magnitud']} ({c['caso']})", c["ok"],
                    f"simulador {_formato(c['simulador'])} · referencia {_formato(c['referencia'])} · "
                    f"error {c['error']:.1e} (tolerancia {c['tolerancia']:.0e})")
    return reg


def interfaz() -> None:
    qc.encabezado_pagina("Verificación", "Verificación frente a referencias independientes",
                         "Cada resultado del laboratorio se compara con otra forma de obtenerlo: diagonalizar el "
                         "hamiltoniano, derivar numéricamente, integrar o usar un valor tabulado.")
    casos = _casos_cacheados()
    r = resumen(casos)
    qc.metricas([("Comparaciones superadas", f"{r['ok']} / {r['total']}"),
                 ("Error relativo máximo", qc.cientifico(r["error_max"], 2)),
                 ("Sistemas verificados", f"{len({c['sistema'] for c in casos})}"),
                 ("Fuente de las constantes", "CODATA 2018")])
    if r["fallos"]:
        qc.error(f"{len(r['fallos'])} comparaciones fuera de tolerancia: revisar la tabla.")
    else:
        qc.nota("Todas las comparaciones están dentro de su tolerancia. La tolerancia depende del método: las "
                "fórmulas cerradas se comparan a 10⁻¹⁰; las diagonalizaciones y las integrales numéricas, a 10⁻⁴ "
                "(error de discretización).")

    qc.seccion("Comparación detallada")
    filtro = st.multiselect("Sistemas", sorted({c["sistema"] for c in casos}), key="ver_filtro",
                            placeholder="Todos los sistemas")
    vistos = [c for c in casos if not filtro or c["sistema"] in filtro]
    qc.tabla_libre([{"Estado": "Correcto" if c["ok"] else "FUERA DE TOLERANCIA", "Sistema": c["sistema"], "Caso": c["caso"], "Magnitud": c["magnitud"], "Unidad": c["unidad"],
                     "Simulador": _formato(c["simulador"]), "Referencia": _formato(c["referencia"]),
                     "Error relativo": f"{c['error']:.2e}", "Tolerancia": f"{c['tolerancia']:.0e}",
                     "Método de la referencia": c["metodo"]}
                    for c in vistos],
                   numericas=("Simulador", "Referencia", "Error relativo", "Tolerancia"),
                   archivo="verificacion_quantum_lab.csv")

    qc.seccion("Contraste con los notebooks de Google Colab")
    st.markdown("Los notebooks de Colab son una **implementación independiente** de la misma física. Escribir estos "
                "parámetros en los dos y compara: las cifras que ambos muestran deben coincidir.")
    qc.tabla_libre([{"Sistema": s, "Parámetros": p, "Magnitud": m, "Valor": v, "Unidad": u}
                    for s, p, m, v, u in valores_colab()],
                   numericas=("Valor",), archivo="valores_para_comparar_con_colab.csv")
    with st.expander("Valores iniciales que comparten la web y los notebooks", expanded=False):
        qc.tabla_libre([{"Sistema": s, "Valores por defecto": v} for s, v in VALORES_PREDETERMINADOS])
        st.markdown("Las diferencias que **no** son errores: la web limita algunos rangos (por ejemplo n ≤ 200 en la "
                    "caja) y rechaza lo que se sale, mientras que los notebooks aceptan cualquier valor y explican "
                    "su validez física; la web usa tema oscuro y los notebooks fondo claro.")
    with st.expander("Cómo se calcula cada referencia", expanded=False):
        st.markdown(
            "- **Diagonalización**: se discretiza H = −ħ²/(2m) d²/dx² (+ V) en una malla y se obtienen sus autovalores con "
            "`scipy.linalg.eigh_tridiagonal`. No interviene la fórmula de Eₙ, así que es una comprobación real.\n"
            "- **Operador angular**: se aplica −[∂θ² + cotθ ∂θ + ∂φ²/sin²θ] a Yₗᵐ con diferencias finitas centradas; "
            "el cociente con Yₗᵐ debe valer l(l+1).\n"
            "- **Integrales**: normalizaciones, ⟨x²⟩, ⟨T⟩ y ⟨r⟩ se calculan con la regla del trapecio y la cuadratura de "
            "Gauss–Legendre, sin usar las fórmulas cerradas de cada simulador.\n"
            "- **Valores tabulados**: constantes CODATA 2018 con siete cifras (por eso su tolerancia es 2×10⁻⁶).\n"
            "- **Principio de incertidumbre**: Δx y Δp salen de la FFT de ψ y se comparan con el valor exacto de cada "
            "tipo de paquete.")


if __name__ == "__main__":
    reg = ejecutar_pruebas()
    reg.imprimir()
