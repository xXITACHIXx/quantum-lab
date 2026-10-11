"""
modelo_bohr.py — QUANTUM LAB · Simulador 05: átomo de hidrógeno según el modelo de Bohr
========================================================================================

Adaptado del simulador de consola «Modelo_Bohr_Simulacion.ipynb» al formato de QUANTUM LAB.

Modelo de Bohr para un átomo de un solo electrón (H, He⁺, Li²⁺) con carga nuclear Z:

    Eₙ  = −Z² · Ry / n²                    Ry = 13.605693 eV (núcleo infinitamente pesado)
    rₙ  = n² a₀ / Z                        vₙ = Z α c / n          Lₙ = n ħ
    E_fotón = |E_f − E_i| = hν = hc/λ
    Rydberg:  1/λ = R_M · Z² · |1/n_f² − 1/n_i²|,   R_M = R∞ / (1 + mₑ/M)

Corrección de masa reducida: el núcleo no está quieto; ambas partículas giran en torno al centro de masas.
Basta sustituir mₑ por μ = mₑM/(mₑ + M): las energías se multiplican por μ/mₑ (≈ 0.99946 para el hidrógeno).
El cuaderno original comparaba E = −13.6/n² con la constante de Rydberg del hidrógeno; la pequeña
diferencia que aparecía (≈ 0.05 %) se debe precisamente a esta corrección (y al redondeo de 13.6).

Estructura: 1. Física · 2. Figuras · 3. Pruebas · 4. Interfaz Streamlit
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import streamlit as st
from scipy import constants as const

import quantum_lab_comun as qc
from quantum_lab_comun import COLORES

# =====================================================================
# 1. FÍSICA
# =====================================================================
H = const.h
HBAR = const.hbar
C = const.c
E = const.e
M_E = const.m_e
RY_EV = const.physical_constants["Rydberg constant times hc in eV"][0]     # 13.605693… eV
R_INF = const.physical_constants["Rydberg constant"][0]                  # 1.0973731…e7 1/m
A0 = const.physical_constants["Bohr radius"][0]
ALFA = const.fine_structure

# Átomos de un electrón: (Z, masa del núcleo [kg], nombre)
NUCLEOS = {
    "H": (1, const.m_p, "Hidrógeno (H)"),
    "He+": (2, const.physical_constants["alpha particle mass"][0], "Ion helio (He⁺)"),
    "Li2+": (3, 7.0160034366 * const.atomic_mass - 3 * M_E, "Ion litio (Li²⁺)"),
}
N_MAX = 50
SERIES = {1: ("Lyman", "ultravioleta"), 2: ("Balmer", "visible y ultravioleta cercano"), 3: ("Paschen", "infrarrojo"),
          4: ("Brackett", "infrarrojo"), 5: ("Pfund", "infrarrojo"), 6: ("Humphreys", "infrarrojo")}


def factor_masa_reducida(nucleo: str) -> float:
    """μ/mₑ = 1/(1 + mₑ/M)."""
    return 1.0 / (1.0 + M_E / NUCLEOS[nucleo][1])


def constante_rydberg(nucleo: str) -> float:
    """R_M = R∞·μ/mₑ  [1/m]  (la que se mide en los espectros reales)."""
    return R_INF * factor_masa_reducida(nucleo)


def energia_nivel(n, nucleo: str = "H", masa_reducida: bool = False):
    """Eₙ = −Z²·Ry·(μ/mₑ)/n²  [eV]."""
    z = NUCLEOS[nucleo][0]
    f = factor_masa_reducida(nucleo) if masa_reducida else 1.0
    return -z ** 2 * RY_EV * f / np.asarray(n, dtype=float) ** 2


def radio_orbita(n, nucleo: str = "H", masa_reducida: bool = False):
    """rₙ = n² a₀ / Z  (·mₑ/μ con masa reducida)  [m]."""
    z = NUCLEOS[nucleo][0]
    f = factor_masa_reducida(nucleo) if masa_reducida else 1.0
    return np.asarray(n, dtype=float) ** 2 * A0 / (z * f)


def velocidad_orbita(n, nucleo: str = "H"):
    """vₙ = Z α c / n  [m/s]."""
    return NUCLEOS[nucleo][0] * ALFA * C / np.asarray(n, dtype=float)


def identificar_serie(n_final: int, nucleo: str = "H") -> tuple[str, str]:
    if nucleo == "H" and n_final in SERIES:
        return SERIES[n_final]
    nombre = SERIES[n_final][0] if n_final in SERIES else f"nivel final {n_final}"
    return (f"análoga a {nombre}" if nucleo != "H" else nombre), "depende de Z"


def longitud_rydberg(n_inicial: int, n_final: int, nucleo: str = "H") -> float:
    """1/λ = R_M Z² |1/n_f² − 1/n_i²|  [m]."""
    z = NUCLEOS[nucleo][0]
    return 1.0 / (constante_rydberg(nucleo) * z ** 2 * abs(1.0 / n_final ** 2 - 1.0 / n_inicial ** 2))


def validar_transicion(n_inicial, n_final, nucleo="H") -> tuple[int, int, str]:
    ni = qc.entero_en_rango(n_inicial, "El nivel inicial", 1, N_MAX)
    nf = qc.entero_en_rango(n_final, "El nivel final", 1, N_MAX)
    if ni == nf:
        raise ValueError("Los niveles inicial y final deben ser distintos: una transición requiere un cambio de nivel.")
    if nucleo not in NUCLEOS:
        raise ValueError(f"Átomo desconocido: {nucleo!r}.")
    return ni, nf, nucleo


@dataclass(frozen=True)
class Transicion:
    n_inicial: int
    n_final: int
    nucleo: str
    masa_reducida: bool


def calcular_transicion(t: Transicion) -> dict:
    """Energías, fotón, comprobación con Rydberg y magnitudes de las órbitas de Bohr."""
    ei = float(energia_nivel(t.n_inicial, t.nucleo, t.masa_reducida))
    ef = float(energia_nivel(t.n_final, t.nucleo, t.masa_reducida))
    de = ef - ei
    e_foton = abs(de)
    nu = e_foton * E / H
    lam = C / nu
    lam_ryd = longitud_rydberg(t.n_inicial, t.n_final, t.nucleo)
    serie, region_serie = identificar_serie(t.n_final, t.nucleo)
    return {
        "ei": ei, "ef": ef, "delta_e": de, "e_foton_ev": e_foton, "e_foton_j": e_foton * E,
        "frecuencia": nu, "longitud_m": lam, "longitud_nm": lam * 1e9,
        "longitud_rydberg_nm": lam_ryd * 1e9, "diferencia_rel": abs(lam - lam_ryd) / lam_ryd,
        "tipo": "Emisión" if t.n_inicial > t.n_final else "Absorción",
        "region": qc.region_espectral(lam * 1e9), "serie": serie, "region_serie": region_serie,
        "ri": float(radio_orbita(t.n_inicial, t.nucleo, t.masa_reducida)),
        "rf": float(radio_orbita(t.n_final, t.nucleo, t.masa_reducida)),
        "vi": float(velocidad_orbita(t.n_inicial, t.nucleo)), "vf": float(velocidad_orbita(t.n_final, t.nucleo)),
        "energia_ionizacion": -float(energia_nivel(min(t.n_inicial, t.n_final), t.nucleo, t.masa_reducida)),
    }


def calcular_serie(n_final: int, n_max: int, nucleo: str = "H", masa_reducida: bool = False) -> dict:
    """Líneas de emisión nᵢ → n_f para nᵢ = n_f+1 … n_max y el límite de la serie (nᵢ → ∞)."""
    nf = qc.entero_en_rango(n_final, "El nivel final", 1, 20)
    nmax = qc.entero_en_rango(n_max, "El nivel inicial máximo", nf + 1, N_MAX)
    ns = np.arange(nf + 1, nmax + 1)
    e_foton = np.abs(energia_nivel(nf, nucleo, masa_reducida) - energia_nivel(ns, nucleo, masa_reducida))
    lam_nm = H * C / (e_foton * E) * 1e9
    limite = H * C / (abs(float(energia_nivel(nf, nucleo, masa_reducida))) * E) * 1e9
    serie, region = identificar_serie(nf, nucleo)
    return {"n_final": nf, "n_inicial": ns, "lambda_nm": lam_nm, "limite_nm": limite, "serie": serie, "region": region}


# =====================================================================
# 2. FIGURAS
# =====================================================================
def _banda_visible(ax, y0, y1, log=False):
    """Pinta el arcoíris del visible (380–750 nm) como fondo entre y0 e y1."""
    lams = np.linspace(380, 750, 300)
    from matplotlib.colors import to_rgb
    colores = np.array([[to_rgb(qc.color_longitud_onda(l))] for l in lams]).transpose(1, 0, 2)
    ax.imshow(colores, extent=[380, 750, y0, y1], aspect="auto", alpha=0.28, zorder=0)


def figura_transicion(t: Transicion, d: dict, n_max: int, escala_real: bool):
    """Diagrama de niveles con la transición y órbitas de Bohr a escala (r ∝ n²)."""
    fig, (ax, ax2) = qc.rejilla(1, 2, (16, 7.2), constrained_layout=True, gridspec_kw={"width_ratios": [1.25, 1]}) \
        if not qc.modo_compacto() else qc.rejilla(1, 2, (16, 7.2), constrained_layout=True)
    niveles = np.arange(1, n_max + 1)
    energias = energia_nivel(niveles, t.nucleo, t.masa_reducida)
    y = energias if escala_real else niveles.astype(float)
    y_ion = 0.0 if escala_real else n_max + 1.4
    color = COLORES["energia"] if d["tipo"] == "Emisión" else COLORES["cinetica"]
    # En escala real los niveles altos se amontonan cerca de E = 0: solo se rotulan los que tienen sitio
    # (separación mínima del 4.5 % del rango vertical), y siempre los de la transición.
    hueco = 0.045 * (0.0 - float(y.min())) if escala_real else 0.0
    rotulados = {t.n_inicial, t.n_final}
    ultimo = None
    for n, yy in zip(niveles, y):
        if n in rotulados:
            continue
        cerca_de_destacado = any(abs(yy - y[k - 1]) < hueco for k in (t.n_inicial, t.n_final))
        if not cerca_de_destacado and (ultimo is None or abs(yy - ultimo) >= hueco):
            rotulados.add(n)
            ultimo = yy
    for n, yy, en in zip(niveles, y, energias):
        destacado = n in (t.n_inicial, t.n_final)
        ax.hlines(yy, 0.0, 1.0, color=color if destacado else COLORES["gris"], lw=2.6 if destacado else 1.3)
        if n not in rotulados:
            continue
        ax.text(-0.04, yy, f"n = {n}", ha="right", va="center", fontsize=10,
                color="white" if destacado else COLORES["gris"], fontweight="bold" if destacado else None)
        ax.text(1.04, yy, f"{en:.4f} eV", ha="left", va="center", fontsize=9, color=COLORES["gris"])
    ax.axhline(y_ion, color=COLORES["potencial"], ls="--", lw=1.2)
    ax.text(1.04, y_ion, "ionización (E = 0)", ha="left", va="bottom", fontsize=9, color=COLORES["potencial"])
    yi = y[t.n_inicial - 1]
    yf = y[t.n_final - 1]
    ax.annotate("", xy=(0.5, yf), xytext=(0.5, yi),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=3, mutation_scale=22))
    foton = qc.color_longitud_onda(d["longitud_nm"], fuera="#FFFFFF")
    ax.text(0.56, (yi + yf) / 2, f"{d['tipo']}  {t.n_inicial} → {t.n_final}\n"
                                 f"hν = {d['e_foton_ev']:.4f} eV\nλ = {d['longitud_nm']:.2f} nm",
            va="center", fontsize=10, color="white",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=COLORES["panel"], edgecolor=foton, lw=2))
    ax.set_xlim(-0.35, 1.55)
    margen = (y.max() - y.min()) * 0.06 if escala_real else 0.6
    ax.set_ylim(y.min() - margen, (y_ion + margen) if escala_real else y_ion + 0.8)
    ax.set_xticks([])
    if escala_real:
        ax.set_ylabel("energía [eV]")
    else:
        ax.set_yticks([])
    for lado in ("top", "right", "bottom") + (() if escala_real else ("left",)):
        ax.spines[lado].set_visible(False)
    ax.set_title("Niveles de energía " + ("(escala real)" if escala_real else "(esquema: espaciado uniforme)"))

    # Órbitas a escala
    n_orb = min(n_max, 8)
    radios = radio_orbita(np.arange(1, n_orb + 1), t.nucleo, t.masa_reducida) / A0
    th = np.linspace(0, 2 * np.pi, 400)
    for n, r in enumerate(radios, 1):
        destacado = n in (t.n_inicial, t.n_final)
        ax2.plot(r * np.cos(th), r * np.sin(th), color=color if destacado else COLORES["gris"],
                 lw=2 if destacado else 0.8, ls="--" if n == t.n_inicial else "-", alpha=1 if destacado else 0.6)
    ax2.plot(0, 0, "o", color=COLORES["energia"], ms=7)
    for n, simbolo in ((t.n_inicial, "o"), (t.n_final, "o")):
        if n <= n_orb:
            r = radios[n - 1]
            ax2.plot(r * np.cos(np.pi / 4), r * np.sin(np.pi / 4), simbolo, ms=8,
                     color=COLORES["onda"], mfc=COLORES["onda"] if n == t.n_final else "none", mew=2)
    lim = radios[-1] * 1.08
    ax2.set_xlim(-lim, lim)
    ax2.set_ylim(-lim, lim)
    ax2.set_aspect("equal")
    ax2.set_xlabel("x [a₀]")
    ax2.set_ylabel("y [a₀]")
    ax2.grid(alpha=0.25)
    fuera = [n for n in (t.n_inicial, t.n_final) if n > n_orb]
    ax2.set_title("Órbitas de Bohr a escala (rₙ = n²a₀/Z)" + (f" · n = {fuera} fuera de la vista" if fuera else ""))
    return fig


def figura_serie(s: dict):
    """λ frente a nᵢ con el límite de la serie, y las líneas sobre el eje de longitudes de onda."""
    fig, (ax, ax2) = qc.rejilla(2, 1, (13, 8.2), constrained_layout=True, gridspec_kw={"height_ratios": [2.2, 1]})
    ns, lam = s["n_inicial"], s["lambda_nm"]
    ax.plot(ns, lam, "o-", color=COLORES["potencial"], mfc=COLORES["panel"], mec=COLORES["potencial"], ms=8, mew=2, lw=2)
    ax.axhline(s["limite_nm"], color=COLORES["energia"], ls="--", lw=1.4)
    ax.text(ns[-1], s["limite_nm"], f"límite de la serie (nᵢ → ∞): {s['limite_nm']:.2f} nm", ha="right", va="bottom",
            color=COLORES["energia"], fontsize=9.5)
    if len(ns) <= 20:
        for x, yv in zip(ns, lam):
            ax.annotate(f"{yv:.1f}", (x, yv), textcoords="offset points", xytext=(6, 6), fontsize=8.5, color=COLORES["gris"])
        ax.set_xticks(ns)
    ax.set_xlabel("nivel inicial nᵢ")
    ax.set_ylabel("λ [nm]")
    ax.set_title(f"Serie de {s['serie']} ($n_f$ = {s['n_final']}) · {s['region']}")
    ax.grid(alpha=0.3)
    lo, hi = min(lam.min(), s["limite_nm"]) * 0.93, lam.max() * 1.05
    _banda_visible(ax2, 0, 1)
    for l in lam:
        ax2.axvline(l, color=qc.color_longitud_onda(l, fuera="#E6EAF5"), lw=2)
    ax2.axvline(s["limite_nm"], color=COLORES["energia"], ls="--", lw=1.2)
    ax2.set_xlim(lo, hi)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.set_xlabel("longitud de onda λ [nm]  (franja de color: región visible)")
    ax2.set_title("Líneas de emisión de la serie")
    return fig


def figura_espectro(nucleo: str, masa_reducida: bool, n_max: int = 9):
    """Todas las series n_f = 1…5 sobre un eje logarítmico de longitudes de onda."""
    fig, ax = qc.rejilla(1, 1, (14, 5.4), constrained_layout=True)
    _banda_visible(ax, 0.4, 5.6)
    for fila, nf in enumerate(range(1, 6), 1):
        s = calcular_serie(nf, max(n_max, nf + 2), nucleo, masa_reducida)
        for l in s["lambda_nm"]:
            ax.plot([l, l], [fila - 0.35, fila + 0.35], color=qc.color_longitud_onda(l, fuera="#E6EAF5"), lw=1.6)
        ax.plot([s["limite_nm"]] * 2, [fila - 0.4, fila + 0.4], color=COLORES["energia"], ls=":", lw=1.2)
        ax.text(s["lambda_nm"].max() * 1.06, fila, s["serie"], va="center", fontsize=9.5, color=COLORES["gris"])
    ax.set_xscale("log")
    ax.set_xlim(H * C / (abs(float(energia_nivel(1, nucleo, masa_reducida))) * E) * 1e9 * 0.85, 9.5e3)
    ax.set_ylim(0.4, 5.6)
    ax.set_yticks(range(1, 6))
    ax.set_yticklabels([f"$n_f$ = {k}" for k in range(1, 6)])
    ax.set_xlabel("longitud de onda λ [nm] (escala logarítmica)")
    ax.set_title(f"Espectro de emisión de {NUCLEOS[nucleo][2]} · líneas punteadas: límites de serie")
    ax.grid(alpha=0.25, which="both", axis="x")
    return fig


# =====================================================================
# 3. PRUEBAS NUMÉRICAS
# =====================================================================
def ejecutar_pruebas() -> qc.RegistroPruebas:
    r = qc.RegistroPruebas("Modelo de Bohr")
    r.comprobar("E₁ = −13.6057 eV (núcleo infinito)", abs(float(energia_nivel(1)) + 13.605693) < 1e-5,
                f"{float(energia_nivel(1)):.6f} eV")
    r.comprobar("E₁ con masa reducida = −13.5983 eV (= −13.6057 · μ/mₑ)", abs(float(energia_nivel(1, "H", True)) + 13.598287) < 1e-5,
                f"{float(energia_nivel(1, 'H', True)):.6f} eV")
    r.comprobar("Eₙ ∝ 1/n² (E₂ = E₁/4, E₃ = E₁/9)",
                np.allclose(energia_nivel([2, 3]) / energia_nivel(1), [1 / 4, 1 / 9], rtol=1e-14))
    r.comprobar("He⁺: E₁ = −54.42 eV (Z² = 4)", abs(float(energia_nivel(1, "He+")) / float(energia_nivel(1)) - 4) < 1e-14)
    ha = calcular_transicion(Transicion(3, 2, "H", True))
    r.comprobar("Hα (3 → 2) = 656.47 nm en el vacío (con masa reducida)", abs(ha["longitud_nm"] - 656.47) < 0.01,
                f"{ha['longitud_nm']:.3f} nm")
    r.comprobar("Hα es emisión, roja y de la serie de Balmer",
                ha["tipo"] == "Emisión" and ha["region"] == "Visible (rojo)" and ha["serie"] == "Balmer")
    la = calcular_transicion(Transicion(2, 1, "H", True))
    r.comprobar("Lyman α (2 → 1) = 121.57 nm, ultravioleta", abs(la["longitud_nm"] - 121.567) < 0.01 and la["region"] == "Ultravioleta",
                f"{la['longitud_nm']:.3f} nm")
    s = calcular_serie(2, 30, "H", True)
    r.comprobar("Límite de Balmer = 364.71 nm", abs(s["limite_nm"] - 364.705) < 0.01, f"{s['limite_nm']:.3f} nm")
    r.comprobar("En una serie λ disminuye con nᵢ y tiende al límite",
                np.all(np.diff(s["lambda_nm"]) < 0) and s["lambda_nm"][-1] > s["limite_nm"]
                and abs(s["lambda_nm"][-1] - s["limite_nm"]) / s["limite_nm"] < 0.01)
    r.comprobar("Con masa reducida, Bohr = Rydberg (diferencia < 10⁻¹⁰)", ha["diferencia_rel"] < 1e-10, f"{ha['diferencia_rel']:.1e}")
    sin = calcular_transicion(Transicion(3, 2, "H", False))
    r.comprobar("Sin masa reducida la diferencia es mₑ/m_p ≈ 5.4×10⁻⁴", abs(sin["diferencia_rel"] - M_E / const.m_p) < 1e-6,
                f"{sin['diferencia_rel']:.3e}")
    ab = calcular_transicion(Transicion(2, 3, "H", True))
    r.comprobar("Absorción 2 → 3: ΔE > 0 y misma λ que la emisión 3 → 2",
                ab["tipo"] == "Absorción" and ab["delta_e"] > 0 and abs(ab["longitud_nm"] - ha["longitud_nm"]) < 1e-9)
    r.comprobar("Emisión: ΔE del átomo < 0", ha["delta_e"] < 0)
    r.comprobar("E_fotón = hν = hc/λ", abs(ha["e_foton_j"] - H * ha["frecuencia"]) / ha["e_foton_j"] < 1e-14
                and abs(ha["frecuencia"] * ha["longitud_m"] - C) / C < 1e-14)
    r.comprobar("r₁ = a₀, rₙ = n²a₀ (H, núcleo infinito)", abs(float(radio_orbita(1)) - A0) < 1e-22
                and abs(float(radio_orbita(3)) / A0 - 9) < 1e-12)
    r.comprobar("v₁ = αc ≈ 2.19×10⁶ m/s", abs(float(velocidad_orbita(1)) - 2.1877e6) / 2.1877e6 < 1e-4)
    r.comprobar("Paschen α (4 → 3) en el infrarrojo", calcular_transicion(Transicion(4, 3, "H", True))["region"] == "Infrarrojo")
    r.comprobar("He⁺ 4 → 2 ≈ Hβ/4 (Z² = 4)… salvo la masa reducida",
                abs(calcular_transicion(Transicion(4, 2, "He+", False))["longitud_nm"] * 4
                    - calcular_transicion(Transicion(4, 2, "H", False))["longitud_nm"]) < 1e-9)
    r.comprobar_error("Rechaza nᵢ = n_f", validar_transicion, 2, 2)
    r.comprobar_error("Rechaza n < 1", validar_transicion, 0, 2)
    r.comprobar_error("Rechaza n no entero", validar_transicion, 2.5, 1)
    r.comprobar_error(f"Rechaza n > {N_MAX}", validar_transicion, N_MAX + 1, 1)
    r.comprobar_error("Rechaza átomo desconocido", validar_transicion, 3, 2, "U92+")
    r.comprobar_error("Serie: rechaza nᵢ máximo ≤ n_f", calcular_serie, 3, 3)
    return r


# =====================================================================
# 4. INTERFAZ (Streamlit)
# =====================================================================
VALORES_INICIALES = {
    "bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2, "bohr_mu": True, "bohr_escala": "real", "bohr_nmax": 6,
    "bohr_serie_nf": 2, "bohr_serie_nmax": 12,
}
DEMOS = {
    "Hα: 3 → 2 (rojo, Balmer)": {"bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2},
    "Lyman α: 2 → 1 (ultravioleta)": {"bohr_nucleo": "H", "bohr_ni": 2, "bohr_nf": 1},
    "Absorción desde el fundamental: 1 → 4": {"bohr_nucleo": "H", "bohr_ni": 1, "bohr_nf": 4},
    "Paschen α: 4 → 3 (infrarrojo)": {"bohr_nucleo": "H", "bohr_ni": 4, "bohr_nf": 3},
    "He⁺: 4 → 3 (Z = 2)": {"bohr_nucleo": "He+", "bohr_ni": 4, "bohr_nf": 3},
}

GUIA = [
    {"titulo": "Las líneas visibles del hidrógeno",
     "objetivo": "Identificar las cuatro líneas de Balmer que se ven con un espectroscopio.",
     "pasos": ["Carga la configuración ($n_f$ = 2, nᵢ hasta 6).", "Anota λ para nᵢ = 3, 4, 5 y 6 y su color.",
               "Sube nᵢ máximo a 30 y observa el límite de la serie."],
     "pregunta": "¿Por qué las líneas se juntan hacia longitudes de onda cortas?",
     "resultado": "Hα 656.5 nm (rojo), Hβ 486.3 nm (azul verdoso), Hγ 434.2 nm y Hδ 410.3 nm (violeta). Al subir nᵢ "
                  "los niveles se acercan entre sí (Eₙ ∝ −1/n²), así que las energías de los fotones tienden a "
                  "Ry/4 y las λ se acumulan en el límite de la serie, 364.7 nm (ya en el ultravioleta).",
     "pestana": "Serie espectral", "config": {"bohr_nucleo": "H", "bohr_serie_nf": 2, "bohr_serie_nmax": 6, "bohr_mu": True}},
    {"titulo": "Emisión y absorción",
     "objetivo": "Comparar una transición con su inversa.",
     "pasos": ["Carga la configuración (3 → 2).", "Anota ΔE y λ.", "Intercambia los niveles (2 → 3)."],
     "pregunta": "¿Qué cambia y qué se conserva al invertir la transición?",
     "resultado": "Cambia el signo de ΔE del átomo (pierde energía al emitir, la gana al absorber) y el sentido de la "
                  "flecha; la energía y la longitud de onda del fotón son idénticas (656.47 nm). Por eso un gas frío "
                  "absorbe exactamente las mismas líneas que emite caliente.",
     "pestana": "Transición", "config": {"bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2}},
    {"titulo": "Corrección de masa reducida",
     "objetivo": "Explicar la pequeña diferencia entre Bohr y la fórmula de Rydberg medida.",
     "pasos": ["Carga la configuración (3 → 2, sin masa reducida).", "Anota la diferencia Bohr–Rydberg.",
               "Activa «Corrección de masa reducida» y vuelve a mirarla."],
     "pregunta": "¿De dónde sale una diferencia de ≈ 0.05 %?",
     "resultado": "Sin corrección la diferencia es ≈ 5.4×10⁻⁴ = mₑ/m_p: el modelo supone el núcleo inmóvil. Con la "
                  "masa reducida μ = mₑm_p/(mₑ + m_p) ambos cálculos coinciden (diferencia < 10⁻¹⁰). Este efecto "
                  "permitió descubrir el deuterio en 1932.",
     "pestana": "Transición", "config": {"bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2, "bohr_mu": False}},
    {"titulo": "Iones hidrogenoides",
     "objetivo": "Ver el efecto de la carga nuclear Z.",
     "pasos": ["Carga la configuración (He⁺, 4 → 2).", "Compara λ con la de Hβ (4 → 2 en el hidrógeno).",
               "Mira el radio de las órbitas."],
     "pregunta": "¿Cómo escalan las energías, las longitudes de onda y los radios con Z?",
     "resultado": "Eₙ ∝ Z², así que λ ∝ 1/Z²: la línea 4 → 2 del He⁺ (≈ 121.5 nm) es casi exactamente Hβ/4, y "
                  "coincide casi con Lyman α del hidrógeno (la diferencia viene de la masa reducida, base de la "
                  "«serie de Pickering»). Los radios rₙ = n²a₀/Z son la mitad.",
     "pestana": "Transición", "config": {"bohr_nucleo": "He+", "bohr_ni": 4, "bohr_nf": 2, "bohr_mu": True}},
]

PREGUNTAS = [
    {"enunciado": "En el modelo de Bohr, la energía del nivel n del hidrógeno es…",
     "opciones": ["−13.6 n² eV", "−13.6/n eV", "−13.6/n² eV", "+13.6/n² eV"], "correcta": 2,
     "explicacion": "Eₙ = −13.6 eV/n². El signo negativo indica un estado ligado; E = 0 es la ionización."},
    {"enunciado": "Cuando el electrón pasa de n = 3 a n = 2…",
     "opciones": ["el átomo absorbe un fotón de 656 nm", "el átomo emite un fotón de 656 nm",
                  "el átomo emite un electrón", "no ocurre nada observable"], "correcta": 1,
     "explicacion": "Baja a un nivel de menor energía: emite un fotón con hν = E₃ − E₂ ≈ 1.89 eV (Hα, rojo)."},
    {"enunciado": "¿Qué determina la serie espectral a la que pertenece una línea?",
     "opciones": ["el nivel inicial", "el nivel final", "la diferencia entre el nivel inicial y el final", "la temperatura del gas"],
     "correcta": 1, "explicacion": "Lyman ($n_f$ = 1), Balmer ($n_f$ = 2), Paschen ($n_f$ = 3)…"},
    {"enunciado": "¿Por qué la serie de Lyman está en el ultravioleta?",
     "opciones": ["porque el nivel 1 está muy separado de los demás: los fotones son muy energéticos",
                  "porque el electrón se mueve más despacio", "porque el núcleo absorbe la luz visible",
                  "por casualidad"], "correcta": 0,
     "explicacion": "E₂ − E₁ = 10.2 eV ya corresponde a 121.6 nm; todas las líneas de Lyman tienen energías entre 10.2 y 13.6 eV."},
    {"enunciado": "La energía mínima para ionizar un átomo de hidrógeno en su estado fundamental es…",
     "opciones": ["3.4 eV", "10.2 eV", "13.6 eV", "infinita"], "correcta": 2,
     "explicacion": "Hay que llevar el electrón de E₁ = −13.6 eV a E = 0."},
    {"enunciado": "Para el ion He⁺ (Z = 2), comparado con el hidrógeno, las energías de los niveles son…",
     "opciones": ["iguales", "el doble", "cuatro veces mayores (en valor absoluto)", "la mitad"], "correcta": 2,
     "explicacion": "Eₙ = −Z²·13.6 eV/n²: con Z = 2 se multiplican por 4."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("bohr_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


def _leer_parametros():
    with st.container(border=True):
        qc.seccion("Átomo y transición")
        c1, c2, c3, c4 = st.columns(4, vertical_alignment="bottom")
        nucleo = c1.selectbox("Átomo", list(NUCLEOS), key="bohr_nucleo", format_func=lambda k: NUCLEOS[k][2])
        ni = c2.number_input(r"Nivel inicial $n_i$", min_value=1, max_value=N_MAX, step=1, key="bohr_ni")
        nf = c3.number_input(r"Nivel final $n_f$", min_value=1, max_value=N_MAX, step=1, key="bohr_nf")
        mu = c4.toggle("Corrección de masa reducida", key="bohr_mu",
                       help="Tiene en cuenta que el núcleo no está quieto (μ = mₑM/(mₑ+M)). Sin ella se usa el modelo "
                            "de Bohr original con el núcleo infinitamente pesado.")
        qc.seccion("Representación")
        d1, d2, _, _ = st.columns(4)
        d1.radio("Escala del diagrama de niveles", ["real", "esquema"], key="bohr_escala", horizontal=True,
                 format_func=lambda k: "Energía real" if k == "real" else "Esquemática")
        d2.slider("Niveles mostrados", 3, 20, key="bohr_nmax")
        qc.pie_de_parametros(DEMOS, "bohr_demo", _aplicar_demo, VALORES_INICIALES, "bohr_reset")
    try:
        ni, nf, nucleo = validar_transicion(ni, nf, nucleo)
        return Transicion(ni, nf, nucleo, bool(mu))
    except ValueError as error:
        qc.error(error)
        return None


def _pestana_transicion(t: Transicion):
    d = calcular_transicion(t)
    texto = (f"**{d['tipo']}** {t.n_inicial} → {t.n_final}: el electrón "
             + ("baja a un nivel de menor energía y el átomo **emite** un fotón." if d["tipo"] == "Emisión"
                else "sube a un nivel de mayor energía; el átomo debe **absorber** un fotón."))
    qc.nota(texto)
    qc.seccion("Resultados")
    qc.metricas([
        (r"$E_i$ [eV]", f"{d['ei']:.5f}"), (r"$E_f$ [eV]", f"{d['ef']:.5f}"),
        (r"$\Delta E$ del átomo [eV]", f"{d['delta_e']:+.5f}", "E_f − E_i: negativo en emisión, positivo en absorción"),
        ("Energía del fotón [eV]", f"{d['e_foton_ev']:.5f}", f"{d['e_foton_j']:.4e} J"),
        ("Frecuencia ν [Hz]", qc.cientifico(d["frecuencia"], 5)),
        ("Longitud de onda λ [nm]", f"{d['longitud_nm']:.3f}", d["region"]),
        ("Serie espectral", d["serie"], f"Región típica: {d['region_serie']}"),
        ("Diferencia Bohr–Rydberg", f"{d['diferencia_rel']:.2e}",
         "Relativa. Sin masa reducida ≈ mₑ/M; con masa reducida ≈ 0."),
    ])
    color = qc.color_longitud_onda(d["longitud_nm"], fuera=None)
    if color:
        st.markdown(f'<p class="ql-subtitulo"><span style="display:inline-block;width:2.4rem;height:.8rem;border-radius:2px;'
                    f'background:{color};vertical-align:-1px;margin-right:.5rem"></span>Color aproximado de la línea '
                    f'({d["region"].lower()})</p>', unsafe_allow_html=True)
    qc.seccion("Visualización")
    n_max = max(int(st.session_state["bohr_nmax"]), t.n_inicial, t.n_final)
    qc.mostrar_pyplot(figura_transicion(t, d, n_max, st.session_state["bohr_escala"] == "real"),
                      archivo=f"bohr_{t.nucleo}_{t.n_inicial}a{t.n_final}.png")
    with st.expander("Valores numéricos detallados", expanded=False):
        qc.tabla([
            ("Átomo", NUCLEOS[t.nucleo][2], "", f"Z = {NUCLEOS[t.nucleo][0]}"),
            ("Energía del nivel inicial Eᵢ", f"{d['ei']:.8f}", "eV"),
            ("Energía del nivel final E_f", f"{d['ef']:.8f}", "eV"),
            ("ΔE del átomo (E_f − Eᵢ)", f"{d['delta_e']:+.8f}", "eV"),
            ("Energía del fotón |ΔE|", f"{d['e_foton_ev']:.8f}", "eV"),
            ("Energía del fotón", f"{d['e_foton_j']:.6e}", "J"),
            ("Frecuencia ν", f"{d['frecuencia']:.6e}", "Hz"),
            ("Longitud de onda (niveles de Bohr)", f"{d['longitud_nm']:.6f}", "nm", d["region"]),
            ("Longitud de onda (fórmula de Rydberg)", f"{d['longitud_rydberg_nm']:.6f}", "nm", "R_M = R∞·μ/mₑ"),
            ("Diferencia relativa", f"{d['diferencia_rel']:.3e}", ""),
            ("Radio de la órbita inicial rᵢ", f"{d['ri'] * 1e9:.6f}", "nm", f"{d['ri'] / A0:.3f} a₀"),
            ("Radio de la órbita final r_f", f"{d['rf'] * 1e9:.6f}", "nm", f"{d['rf'] / A0:.3f} a₀"),
            ("Velocidad orbital inicial vᵢ", f"{d['vi']:.6e}", "m/s", f"{d['vi'] / C:.4f} c"),
            ("Velocidad orbital final v_f", f"{d['vf']:.6e}", "m/s", f"{d['vf'] / C:.4f} c"),
            ("Momento angular Lᵢ / L_f", f"{t.n_inicial} ħ / {t.n_final} ħ", ""),
            ("Energía de ionización desde el nivel más bajo", f"{d['energia_ionizacion']:.6f}", "eV"),
        ], archivo=f"bohr_{t.nucleo}_{t.n_inicial}a{t.n_final}.csv")
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- Bohr postuló órbitas estables con momento angular cuantizado L = nħ. De ahí salen los radios "
            "rₙ = n²a₀/Z y las energías Eₙ = −Z²·13.6 eV/n².\n"
            "- El electrón solo emite o absorbe luz al **saltar** entre órbitas, con un fotón de energía exactamente "
            "|E_f − Eᵢ|. Por eso el espectro está formado por **líneas** y no es continuo.\n"
            "- El modelo reproduce el espectro del hidrógeno, pero **no** es la descripción moderna: los electrones no "
            "siguen órbitas definidas (ver el simulador de la partícula en una esfera y sus orbitales) y el modelo falla "
            "para átomos de más de un electrón.")


def _pestana_serie(t: Transicion):
    c1, c2, _, _ = st.columns(4)
    nf = c1.number_input(r"Nivel final fijo $n_f$", 1, 10, step=1, key="bohr_serie_nf")
    nmax = c2.number_input("Nivel inicial máximo", 2, N_MAX, step=1, key="bohr_serie_nmax")
    try:
        s = calcular_serie(nf, nmax, t.nucleo, t.masa_reducida)
    except ValueError as error:
        qc.error(error)
        return
    qc.seccion("Resultados")
    qc.metricas([
        ("Serie", s["serie"], s["region"]), ("Número de líneas", f"{len(s['n_inicial'])}"),
        ("Línea de mayor λ [nm]", f"{s['lambda_nm'][0]:.3f}", f"{s['n_inicial'][0]} → {s['n_final']}"),
        ("Límite de la serie [nm]", f"{s['limite_nm']:.3f}", "nᵢ → ∞: la energía del fotón tiende a |E_f|"),
    ])
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_serie(s), archivo=f"bohr_serie_nf{s['n_final']}.png")
    qc.seccion("Tabla de líneas")
    letras = "αβγδεζηθ"
    qc.tabla_libre([{"Línea": (f"{s['serie'][:1]}{letras[i]}" if i < len(letras) and t.nucleo == "H" else "—"),
                     "Transición": f"{n} → {s['n_final']}", "λ [nm]": f"{l:.4f}", "Región": qc.region_espectral(l)}
                    for i, (n, l) in enumerate(zip(s["n_inicial"], s["lambda_nm"]))],
                   numericas=("λ [nm]",), archivo=f"bohr_serie_nf{s['n_final']}.csv")


def _pestana_espectro(t: Transicion):
    qc.mostrar_pyplot(figura_espectro(t.nucleo, t.masa_reducida), archivo=f"bohr_espectro_{t.nucleo}.png")
    st.caption("Cada fila es una serie (todas las líneas que terminan en el mismo nivel). Solo la serie de Balmer cae, "
               "en parte, dentro de la franja visible. Las series de niveles más altos se solapan en el infrarrojo.")


def _pestana_ecuaciones():
    qc.seccion("Postulados y resultados de Bohr")
    st.latex(r"L=m_e v r=n\hbar\qquad r_n=\frac{n^2a_0}{Z}\qquad v_n=\frac{Z\alpha c}{n}\qquad E_n=-\frac{Z^2\,R_y}{n^2},\ \ R_y=13.6057\ \mathrm{eV}")
    qc.seccion("Transiciones")
    st.latex(r"E_{\rm fotón}=|E_f-E_i|=h\nu=\frac{hc}{\lambda}\qquad \frac{1}{\lambda}=R_M\,Z^2\left|\frac{1}{n_f^2}-\frac{1}{n_i^2}\right|")
    qc.seccion("Masa reducida")
    st.latex(r"\mu=\frac{m_eM}{m_e+M},\qquad R_M=R_\infty\frac{\mu}{m_e}=\frac{R_\infty}{1+m_e/M},\qquad R_\infty=1.0973731\times10^{7}\ \mathrm{m^{-1}}")


def interfaz() -> None:
    """Página completa del simulador 5 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 05", "Átomo de hidrógeno · modelo de Bohr",
                         "Niveles de energía, transiciones electrónicas, series espectrales y comparación con la "
                         "fórmula de Rydberg, incluida la corrección de masa reducida.")
    t = _leer_parametros()
    if t is None:
        return
    tabs = st.tabs(["Transición", "Serie espectral", "Espectro completo", "Ecuaciones",
                    "Guía de práctica", "Autoevaluación", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_transicion(t)
    with tabs[1]:
        _pestana_serie(t)
    with tabs[2]:
        _pestana_espectro(t)
    with tabs[3]:
        _pestana_ecuaciones()
    with tabs[4]:
        qc.guia_practica(GUIA, "bohr")
    with tabs[5]:
        qc.autoevaluacion(PREGUNTAS, "bohr")
    with tabs[6]:
        qc.boton_pruebas(ejecutar_pruebas, "bohr_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Modelo de Bohr", ":material/science:", "modelo_bohr.py")
