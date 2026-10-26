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

import informes
import instrumentos
import inverso
import predice
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
    # La serie la fija el nivel INFERIOR de la transición (en emisión es el final; en absorción, el inicial).
    serie, region_serie = identificar_serie(min(t.n_inicial, t.n_final), t.nucleo)
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


# ---------------------------------------------------------------------
# 1.2 Átomo de hidrógeno CUÁNTICO (ecuación de Schrödinger) — para comparar con Bohr
# ---------------------------------------------------------------------
# ψ_nlm(r, θ, φ) = R_nl(r) · Y_lm(θ, φ)
# R_nl(r) = √[(2Z/na)³ (n−l−1)! / (2n (n+l)!)] · e^{−ρ/2} ρ^l L_{n−l−1}^{2l+1}(ρ),   ρ = 2Zr/(na)
# Las energías coinciden con las de Bohr (−Z²Ry/n², degeneradas en l y m), pero el electrón NO sigue una
# órbita: |ψ|² da la probabilidad de encontrarlo en cada punto (nube de probabilidad).
N_ORBITAL_MAX = 6
LETRAS_L = "spdfgh"


def radio_bohr_efectivo(nucleo: str = "H", masa_reducida: bool = False) -> float:
    """a = a₀·mₑ/μ (o a₀ con núcleo infinito)  [m]."""
    return A0 / (factor_masa_reducida(nucleo) if masa_reducida else 1.0)


def validar_orbital(n, l, m) -> tuple[int, int, int]:
    n = qc.entero_en_rango(n, "El número cuántico principal n", 1, N_ORBITAL_MAX)
    l = qc.entero_en_rango(l, "El número cuántico l", 0, N_ORBITAL_MAX)
    m = qc.entero_en_rango(m, "El número cuántico m", -N_ORBITAL_MAX, N_ORBITAL_MAX)
    if l > n - 1:
        raise ValueError(f"Para n = {n}, l debe cumplir 0 ≤ l ≤ n − 1 = {n - 1} (recibido: l = {l}).")
    if abs(m) > l:
        raise ValueError(f"Para l = {l}, m debe cumplir −{l} ≤ m ≤ {l} (recibido: m = {m}).")
    return n, l, m


def radial_hidrogeno(r, n: int, l: int, z: int = 1, a: float = A0):
    """R_nl(r) normalizada: ∫ R² r² dr = 1  [m^(−3/2)]."""
    from scipy.special import eval_genlaguerre, gammaln
    rho = 2.0 * z * np.asarray(r, dtype=float) / (n * a)
    log_norma = 1.5 * np.log(2.0 * z / (n * a)) + 0.5 * (gammaln(n - l) - np.log(2.0 * n) - gammaln(n + l + 1))
    return np.exp(log_norma) * np.exp(-rho / 2.0) * rho ** l * eval_genlaguerre(n - l - 1, 2 * l + 1, rho)


def r_medio(n: int, l: int, z: int = 1, a: float = A0) -> float:
    """⟨r⟩ = (a/2Z)[3n² − l(l+1)]."""
    return a / (2.0 * z) * (3 * n ** 2 - l * (l + 1))


def r2_medio(n: int, l: int, z: int = 1, a: float = A0) -> float:
    """⟨r²⟩ = (a²n²/2Z²)[5n² + 1 − 3l(l+1)]."""
    return a ** 2 * n ** 2 / (2.0 * z ** 2) * (5 * n ** 2 + 1 - 3 * l * (l + 1))


def p2_medio(n: int, z: int = 1, a: float = A0) -> float:
    """⟨p²⟩ = (Zħ/(na))²  (teorema del virial: ⟨T⟩ = −Eₙ)."""
    return (z * HBAR / (n * a)) ** 2


def _legendre_sin_fase(l: int, m: int, x):
    """P_l^{|m|}(x) SIN la fase de Condon–Shortley (así p_x es positivo hacia +x)."""
    from scipy.special import lpmv
    ma = abs(m)
    return (-1) ** ma * lpmv(ma, l, x)


def nombre_orbital_real(n: int, l: int, m: int) -> str:
    """Nombre químico del orbital real: 2p_x, 3d_z², 3d_xy…"""
    nombres = {(1, 0): "p_z", (1, 1): "p_x", (1, -1): "p_y",
               (2, 0): "d_z²", (2, 1): "d_xz", (2, -1): "d_yz", (2, 2): "d_x²−y²", (2, -2): "d_xy",
               (3, 0): "f_z³", (3, 1): "f_xz²", (3, -1): "f_yz²", (3, 2): "f_z(x²−y²)", (3, -2): "f_xyz",
               (3, 3): "f_x(x²−3y²)", (3, -3): "f_y(3x²−y²)"}
    if l == 0:
        return f"{n}s"
    if (l, m) in nombres:
        return f"{n}{nombres[(l, m)]}"
    return f"{n}{LETRAS_L[l]} (m = {str(m).replace('-', '−')})"


def _cdf_inversa(x, densidad, u):
    """Muestreo por transformada inversa de la CDF tabulada de una densidad (no necesariamente normalizada)."""
    from scipy.integrate import cumulative_trapezoid
    cdf = cumulative_trapezoid(np.maximum(densidad, 0.0), x, initial=0.0)
    cdf /= cdf[-1]
    unicos, idx = np.unique(cdf, return_index=True)        # la interpolación necesita una CDF creciente estricta
    return np.interp(u, unicos, x[idx])


def radio_maximo(n: int, z: int = 1, a: float = A0) -> float:
    """Radio hasta el que se tabula R_nl (la probabilidad más allá es despreciable, < 10⁻¹⁰)."""
    return a / z * (3 * n ** 2 + 14 * n + 12)


def muestrear_posiciones(n: int, l: int, m: int, real: bool, puntos: int, semilla: int = 1,
                         nucleo: str = "H", masa_reducida: bool = False) -> dict:
    """
    Simula `puntos` MEDIDAS independientes de la posición del electrón en el estado ψ_nlm: cada punto se
    extrae de la densidad |ψ|². Como ψ = R(r)·Θ(θ)·Φ(φ), se muestrean r, θ y φ por separado con sus densidades
    marginales: r²R², |P_l^m(cos θ)|² sin θ, y |Φ(φ)|² (uniforme para el orbital complejo; cos² o sin² para el real).
    Devuelve las posiciones en unidades de a (radio de Bohr) y el signo (real) o la fase (complejo) de ψ.
    """
    z = NUCLEOS[nucleo][0]
    a = radio_bohr_efectivo(nucleo, masa_reducida)
    rng = np.random.default_rng(int(semilla))
    rr = np.linspace(0.0, radio_maximo(n, z, a), 12001)
    Rr = radial_hidrogeno(rr, n, l, z, a)
    r = _cdf_inversa(rr, rr ** 2 * Rr ** 2, rng.random(puntos))
    th_grid = np.linspace(0.0, np.pi, 4001)
    th = _cdf_inversa(th_grid, _legendre_sin_fase(l, m, np.cos(th_grid)) ** 2 * np.sin(th_grid), rng.random(puntos))
    ma = abs(m)
    if real and ma > 0:
        ph_grid = np.linspace(0.0, 2 * np.pi, 4001)
        trig = np.cos(ma * ph_grid) if m > 0 else np.sin(ma * ph_grid)
        ph = _cdf_inversa(ph_grid, trig ** 2, rng.random(puntos))
    else:
        ph = rng.random(puntos) * 2 * np.pi
    x, y, zz = r * np.sin(th) * np.cos(ph), r * np.sin(th) * np.sin(ph), r * np.cos(th)
    amplitud = radial_hidrogeno(r, n, l, z, a) * _legendre_sin_fase(l, m, np.cos(th))
    if real:
        trig = 1.0 if ma == 0 else (np.cos(ma * ph) if m > 0 else np.sin(ma * ph))
        color = np.sign(amplitud * trig)
    else:
        color = np.angle(amplitud * np.exp(1j * m * ph))
    return {"x": x / a, "y": y / a, "z": zz / a, "r": r / a, "color": color, "a": a, "z_nuclear": z}


def densidad_corte(n: int, l: int, m: int, real: bool, nucleo: str = "H", masa_reducida: bool = False,
                   pixeles: int = 241) -> dict:
    """
    |ψ|² en el plano de corte (xy, xz o yz) donde el orbital es más visible. Coordenadas en unidades de a.
    """
    z = NUCLEOS[nucleo][0]
    a = radio_bohr_efectivo(nucleo, masa_reducida)
    L = 1.05 * (r_medio(n, l, z, a) + 3.2 * np.sqrt(max(r2_medio(n, l, z, a) - r_medio(n, l, z, a) ** 2, 0))) / a
    ejes = np.linspace(-L, L, pixeles)
    U, V = np.meshgrid(ejes, ejes, indexing="xy")
    planos = {"xz": (U, 0 * U, V), "xy": (U, V, 0 * U), "yz": (0 * U, U, V)}

    def dens(X, Y, Z_):
        r = np.sqrt(X ** 2 + Y ** 2 + Z_ ** 2) * a
        th = np.arccos(np.divide(Z_ * a, r, out=np.ones_like(r), where=r > 0))
        ph = np.arctan2(Y, X)
        ang = _legendre_sin_fase(l, m, np.cos(th))
        ma = abs(m)
        if real and ma > 0:
            ang = ang * (np.cos(ma * ph) if m > 0 else np.sin(ma * ph))
        return (radial_hidrogeno(r, n, l, z, a) * ang) ** 2

    valores = {k: dens(*v) for k, v in planos.items()}
    plano = max(valores, key=lambda k: float(np.sum(valores[k])))
    d = valores[plano]
    return {"plano": plano, "ejes": ejes, "densidad": d / d.max() if d.max() > 0 else d}


def _maximo_refinado(x, y) -> float:
    """Posición del máximo de y(x), refinada con una parábola por los tres puntos que lo rodean."""
    k = int(np.clip(np.argmax(y), 1, len(y) - 2))
    y0, y1, y2 = y[k - 1], y[k], y[k + 1]
    den = y0 - 2 * y1 + y2
    desplazamiento = 0.5 * (y0 - y2) / den if den != 0 else 0.0
    return float(x[k] + desplazamiento * (x[1] - x[0]))


def calcular_orbital(n: int, l: int, m: int, nucleo: str = "H", masa_reducida: bool = False) -> dict:
    """Valores característicos del estado cuántico y comparación con la órbita de Bohr del mismo n."""
    z = NUCLEOS[nucleo][0]
    a = radio_bohr_efectivo(nucleo, masa_reducida)
    rr = np.linspace(0.0, radio_maximo(n, z, a), 20001)
    P = rr ** 2 * radial_hidrogeno(rr, n, l, z, a) ** 2
    rm, r2 = r_medio(n, l, z, a), r2_medio(n, l, z, a)
    R = radial_hidrogeno(rr[1:], n, l, z, a)                 # se excluye r = 0 (allí R puede ser 0 para l > 0)
    cambio = np.sign(R[:-1]) * np.sign(R[1:]) < 0
    nodos = 0.5 * (rr[1:][:-1][cambio] + rr[1:][1:][cambio])
    return {
        "r": rr / a, "P": P * a, "norma": float((getattr(np, "trapezoid", None) or np.trapz)(P, rr)),
        "r_medio": rm / a, "r_probable": _maximo_refinado(rr, P) / a, "delta_r": float(np.sqrt(r2 - rm ** 2) / a),
        "r_bohr": float(radio_orbita(n, nucleo, masa_reducida) / a), "energia": float(energia_nivel(n, nucleo, masa_reducida)),
        "nodos_radiales": n - l - 1, "nodos_angulares": l, "nodos_r": nodos / a,
        # Para estados s (simetría esférica): Δx = √(⟨r²⟩/3), Δpₓ = √(⟨p²⟩/3)
        "dx_dp_s": float(np.sqrt(r2 / 3.0) * np.sqrt(p2_medio(n, z, a) / 3.0) / HBAR) if l == 0 else None,
        "L": np.sqrt(l * (l + 1)), "a": a,
    }


# =====================================================================
# 2. FIGURAS
# =====================================================================
def _banda_visible(ax, y0, y1, log=False):
    """Pinta el arcoíris del visible (380–750 nm) como fondo entre y0 e y1."""
    lams = np.linspace(380, 750, 300)
    from matplotlib.colors import to_rgb
    colores = np.array([[to_rgb(qc.color_longitud_onda(l))] for l in lams]).transpose(1, 0, 2)
    ax.imshow(colores, extent=[380, 750, y0, y1], aspect="auto", alpha=0.28, zorder=0)


def _onda_foton(ax, x0, x1, y, color, ciclos, amplitud, lw=2.0):
    """Dibuja un fotón como un tren de ondas horizontal entre x0 y x1 con flecha final."""
    xs = np.linspace(x0, x1, 400)
    env = np.sin(np.pi * (xs - x0) / (x1 - x0)) ** 0.6
    ax.plot(xs, y + amplitud * env * np.sin(2 * np.pi * ciclos * (xs - x0) / (x1 - x0)), color=color, lw=lw, zorder=6)
    paso = 0.25 if x1 > x0 else -0.25          # la punta de flecha indica el sentido de propagación
    ax.annotate("", xy=(x1 + paso, y), xytext=(x1, y), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw), zorder=6)


def figura_transicion(t: Transicion, d: dict, n_max: int, escala_real: bool):
    """
    Arriba: diagrama de niveles con TODAS las transiciones de la serie (tenues) y la elegida destacada; el fotón
    se dibuja como un tren de ondas de su color. Abajo: posición de la línea en el espectro electromagnético.
    """
    from matplotlib.patches import Rectangle
    fig, (ax, ax2) = qc.rejilla(2, 1, (14, 9.4), constrained_layout=True, gridspec_kw={"height_ratios": [3.2, 1]})
    niveles = np.arange(1, n_max + 1)
    energias = energia_nivel(niveles, t.nucleo, t.masa_reducida)
    y = energias if escala_real else niveles.astype(float)
    y_ion = 0.0 if escala_real else n_max + 1.2
    emision = d["tipo"] == "Emisión"
    c_tipo = COLORES["energia"] if emision else COLORES["cinetica"]
    c_foton = qc.color_longitud_onda(d["longitud_nm"], fuera="#E6EAF5")
    alto = float(y_ion - y.min())

    # Continuo de energías por encima de la ionización
    X0, X1 = 2.6, 7.4                      # extremo izquierdo y derecho de las líneas de nivel
    ax.add_patch(Rectangle((X0, y_ion), X1 - X0, 0.07 * alto, color=COLORES["potencial"], alpha=0.18, lw=0))
    ax.text((X0 + X1) / 2, y_ion + 0.035 * alto, "continuo (electrón libre, E > 0)", ha="center", va="center",
            fontsize=9, color=COLORES["potencial"])
    ax.plot([X0, X1], [y_ion, y_ion], color=COLORES["potencial"], ls="--", lw=1.1)

    # Rótulos sin solaparse
    hueco = 0.045 * alto
    rotulados, ultimo = {t.n_inicial, t.n_final}, None
    for n, yy in zip(niveles, y):
        if n in rotulados:
            continue
        lejos = all(abs(yy - y[k - 1]) >= hueco for k in (t.n_inicial, t.n_final))
        if lejos and (ultimo is None or abs(yy - ultimo) >= hueco):
            rotulados.add(n)
            ultimo = yy
    for n, yy, en in zip(niveles, y, energias):
        sel = n in (t.n_inicial, t.n_final)
        ax.hlines(yy, X0, X1, color="white" if sel else COLORES["gris"], lw=2.4 if sel else 1.2, alpha=1 if sel else 0.75)
        if n in rotulados:
            ax.text(X0 - 1.15, yy, f"n = {n}", ha="right", va="center", fontsize=10.5 if sel else 9.5,
                    color="white" if sel else COLORES["gris"], fontweight="bold" if sel else None)
            ax.text(X0 - 0.12, yy, f"{en:.3f} eV", ha="right", va="center", fontsize=9, color=COLORES["gris"])

    # Todas las líneas de la serie de n_f (emisión desde niveles superiores), tenues
    n_bajo, n_alto = min(t.n_inicial, t.n_final), max(t.n_inicial, t.n_final)
    superiores = [n for n in niveles if n > n_bajo and n != n_alto]
    xs = np.linspace(X0 + 0.35, X1 - 1.3, max(len(superiores), 1))
    x_sel = X1 - 0.55                       # la transición elegida va siempre a la derecha, junto a la salida del fotón
    for xk, n in zip(xs, superiores):
        lam = H * C / (abs(float(energia_nivel(n, t.nucleo, t.masa_reducida) - energia_nivel(n_bajo, t.nucleo, t.masa_reducida))) * E) * 1e9
        ax.annotate("", xy=(xk, y[n_bajo - 1]), xytext=(xk, y[n - 1]),
                    arrowprops=dict(arrowstyle="-|>", color=qc.color_longitud_onda(lam, fuera=COLORES["gris"]),
                                    lw=1.1, alpha=0.45))
    yi, yf = y[t.n_inicial - 1], y[t.n_final - 1]
    ax.annotate("", xy=(x_sel, yf), xytext=(x_sel, yi),
                arrowprops=dict(arrowstyle="-|>", color=c_tipo, lw=3.4, mutation_scale=24), zorder=5)
    ax.plot([x_sel], [yi], "o", color=COLORES["onda"], ms=9, zorder=7)
    ax.plot([x_sel], [yf], "o", color=COLORES["onda"], ms=9, mfc="none", mew=2, zorder=7)
    y_foton = (yi + yf) / 2
    ciclos = float(np.clip(9 * 656.0 / d["longitud_nm"], 4, 26))
    if emision:
        _onda_foton(ax, x_sel + 0.2, 9.9, y_foton, c_foton, ciclos, 0.025 * alto, lw=2.2)
    else:
        _onda_foton(ax, 10.1, x_sel + 0.45, y_foton, c_foton, ciclos, 0.025 * alto, lw=2.2)
    ax.text(10.4, y_foton, f"fotón {'emitido' if emision else 'absorbido'}\nλ = {d['longitud_nm']:.2f} nm\n"
                            f"hν = {d['e_foton_ev']:.4f} eV\n{d['region']}", va="center", fontsize=10, color="white",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=COLORES["panel"], edgecolor=c_foton, lw=1.8))
    ax.set_xlim(0.2, 12.8)
    margen = 0.05 * alto
    ax.set_ylim(float(y.min()) - margen, y_ion + 0.09 * alto)
    ax.set_xticks([])
    if escala_real:
        ax.set_ylabel("Energía [eV]")
    else:
        ax.set_yticks([])
    for lado in ("top", "right", "bottom") + (() if escala_real else ("left",)):
        ax.spines[lado].set_visible(False)
    ax.set_title(f"{d['tipo']} {t.n_inicial} → {t.n_final} · {NUCLEOS[t.nucleo][2]}", fontsize=12)

    # Espectro electromagnético
    lam_min, lam_max = 60.0, 6000.0
    for x0, x1, col, etq in ((lam_min, 380, "#5B4B8A", "ultravioleta"), (750, lam_max, "#6B2E2E", "infrarrojo")):
        ax2.axvspan(x0, x1, color=col, alpha=0.35, lw=0)
        ax2.text(np.sqrt(x0 * x1), 0.82, etq, ha="center", va="center", fontsize=9, color=COLORES["texto"])
    _banda_visible(ax2, 0, 1)
    ax2.text(np.sqrt(380 * 750), 0.82, "visible", ha="center", va="center", fontsize=9, color="black")
    serie = calcular_serie(min(t.n_inicial, t.n_final), max(n_max, min(t.n_inicial, t.n_final) + 2), t.nucleo, t.masa_reducida)
    for l in serie["lambda_nm"]:
        if lam_min < l < lam_max:
            ax2.axvline(l, ymax=0.62, color="white", lw=0.8, alpha=0.45)
    if lam_min < d["longitud_nm"] < lam_max:
        ax2.axvline(d["longitud_nm"], ymax=0.62, color=c_foton if c_foton != "#E6EAF5" else "white", lw=3)
        ax2.annotate(f"{d['longitud_nm']:.1f} nm", (d["longitud_nm"], 0.62), xytext=(0, 4), textcoords="offset points",
                     ha="center", fontsize=9.5, color="white")
    ax2.set_xscale("log")
    ax2.set_xlim(lam_min, lam_max)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.set_xlabel("longitud de onda λ [nm] (escala logarítmica) · líneas tenues: resto de la serie")
    ax2.set_title("Espectro electromagnético", fontsize=11)
    return fig


def figura_nube_3d(n: int, l: int, m: int, real: bool, puntos: int, semilla: int, nucleo: str, masa_reducida: bool,
                   mostrar_bohr: bool = True, animar: bool = True, altura: int = 680):
    """
    Nube de probabilidad: cada punto es una posible medida de la posición del electrón (extraída de |ψ|²).
    Con `animar`, las medidas se acumulan cuadro a cuadro. Se superpone la órbita de Bohr del mismo n.
    """
    import plotly.graph_objects as go
    mst = muestrear_posiciones(n, l, m, real, puntos, semilla, nucleo, masa_reducida)
    z = NUCLEOS[nucleo][0]
    con_fase = (not real) and m != 0
    if con_fase:
        colorscale, cmin, cmax = "Twilight", -np.pi, np.pi
        barra = dict(title=dict(text="fase de ψ [rad]", side="right"), thickness=12, len=0.6)
    else:
        colorscale, cmin, cmax = [[0, COLORES["densidad"]], [0.5, COLORES["densidad"]], [0.5, COLORES["onda"]],
                                  [1, COLORES["onda"]]], -1, 1
        barra = dict(title=dict(text="signo de ψ", side="right"), tickvals=[-0.5, 0.5], ticktext=["−", "+"],
                     thickness=12, len=0.4)

    def nube(k):
        # Con pocas medidas cada punto se dibuja más grande y opaco para facilitar su visualización; con miles, pequeño y translúcido.
        tam = float(np.clip(6.5 - 1.25 * np.log10(max(k, 1)), 2.1, 6.0))
        opa = float(np.clip(1.15 - 0.15 * np.log10(max(k, 1)), 0.55, 1.0))
        return go.Scatter3d(x=mst["x"][:k], y=mst["y"][:k], z=mst["z"][:k], mode="markers", name="medidas",
                            marker=dict(size=tam, color=mst["color"][:k], colorscale=colorscale, cmin=cmin, cmax=cmax,
                                        opacity=opa, colorbar=barra, showscale=True),
                            hovertemplate="x=%{x:.2f} a₀<br>y=%{y:.2f} a₀<br>z=%{z:.2f} a₀<extra></extra>")
    datos = [nube(puntos)]
    datos.append(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers", name="núcleo",
                              marker=dict(size=6, color=COLORES["energia"]), hoverinfo="name"))
    if mostrar_bohr:
        rb = n ** 2 / z
        th = np.linspace(0, 2 * np.pi, 200)
        datos.append(go.Scatter3d(x=rb * np.cos(th), y=rb * np.sin(th), z=0 * th, mode="lines",
                                  name=f"órbita de Bohr n = {n} (r = {rb:g} a₀)",
                                  line=dict(color="white", width=5), hoverinfo="name"))
    fig = go.Figure(data=datos)
    L = float(np.percentile(np.abs(np.concatenate([mst["x"], mst["y"], mst["z"]])), 99.3)) * 1.05
    L = max(L, 1.15 * n ** 2 / z if mostrar_bohr else L)
    eje = dict(range=[-L, L], backgroundcolor=COLORES["panel"], gridcolor=COLORES["rejilla"], zerolinecolor=COLORES["gris"],
               showbackground=True, color=COLORES["texto"])
    nombre = nombre_orbital_real(n, l, m) if real else f"{n}{LETRAS_L[l]}, m = {m} (complejo)"
    qc.aplicar_tema_plotly(fig, f"Nube de probabilidad · {nombre}", altura=altura)
    fig.update_layout(scene=dict(xaxis=dict(title="x [a₀]", **eje), yaxis=dict(title="y [a₀]", **eje),
                                 zaxis=dict(title="z [a₀]", **eje), aspectmode="cube",
                                 camera=dict(eye=dict(x=1.35, y=1.35, z=0.85))),
                      legend=dict(orientation="h", y=1.02, x=0.0), margin=dict(l=0, r=0, t=60, b=0))
    if animar:
        # Las medidas se acumulan de forma geométrica: 1, 3, 8, 20… hasta el total. Con pocas medidas los puntos
        # parecen aleatorios; al acumular miles aparece la forma del orbital (la distribución |ψ|²).
        cuentas = sorted({int(round(k)) for k in np.geomspace(1, puntos, 16)} | {puntos})
        fig.frames = [go.Frame(data=[nube(k)], traces=[0], name=f"c{i}") for i, k in enumerate(cuentas)]
        qc.agregar_animacion(fig, [f"c{i}" for i in range(len(cuentas))],
                             [f"{k} medida" if k == 1 else f"{k} medidas" for k in cuentas], duracion_ms=550)
        # La figura se abre con TODAS las medidas: el deslizador marca el último cuadro y «Reproducir»
        # vuelve a empezar desde la primera medida.
        fig.layout.sliders[0].active = len(cuentas) - 1
        boton = fig.layout.updatemenus[0].buttons[0]
        opciones = dict(boton.args[1])
        opciones["fromcurrent"] = False
        boton.args = [[f"c{i}" for i in range(len(cuentas))], opciones]
    return fig


def figura_orbital_2d(n: int, l: int, m: int, real: bool, nucleo: str, masa_reducida: bool):
    """Distribución radial P(r) comparada con el radio de Bohr, y corte de la densidad |ψ|²."""
    o = calcular_orbital(n, l, m, nucleo, masa_reducida)
    c = densidad_corte(n, l, m, real, nucleo, masa_reducida)
    fig, (ax, ax2) = qc.rejilla(1, 2, (15, 5.8), constrained_layout=True, gridspec_kw={"width_ratios": [1.25, 1]})
    r, P = o["r"], o["P"]
    lim = o["r_medio"] + 4.5 * o["delta_r"]
    ax.fill_between(r, P, color=COLORES["densidad"], alpha=0.25)
    ax.plot(r, P, color=COLORES["densidad"], lw=2.2, label="P(r) = r²|R(r)|² (cuántico)")
    ax.axvspan(o["r_medio"] - o["delta_r"], o["r_medio"] + o["delta_r"], color=COLORES["onda"], alpha=0.10,
               label=f"⟨r⟩ ± Δr = {o['r_medio']:.2f} ± {o['delta_r']:.2f} a₀")
    ax.axvline(o["r_medio"], color=COLORES["onda"], lw=1.6)
    ax.axvline(o["r_probable"], color=COLORES["cinetica"], ls=":", lw=1.8, label=f"más probable: {o['r_probable']:.2f} a₀")
    ax.axvline(o["r_bohr"], color="white", ls="--", lw=1.8, label=f"radio de Bohr n²a₀/Z = {o['r_bohr']:.2f} a₀")
    for rn in o["nodos_r"]:
        ax.plot([rn], [0], "o", color=COLORES["energia"], ms=6)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, P.max() * 1.18)
    ax.set_xlabel("distancia al núcleo r [a₀]")
    ax.set_ylabel("Densidad de probabilidad radial [1/a₀]")
    ax.set_title("Densidad de probabilidad radial")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    e = c["ejes"]
    im = ax2.imshow(c["densidad"] ** 0.6, extent=[e[0], e[-1], e[0], e[-1]], origin="lower", cmap="magma", aspect="equal")
    if m == 0 or c["plano"] != "xy":
        pass
    rb = o["r_bohr"]
    th = np.linspace(0, 2 * np.pi, 200)
    ax2.plot(rb * np.cos(th), rb * np.sin(th), color="white", ls="--", lw=1.2, alpha=0.8)
    ejes = {"xz": ("x", "z"), "xy": ("x", "y"), "yz": ("y", "z")}[c["plano"]]
    ax2.set_xlabel(f"{ejes[0]} [a₀]")
    ax2.set_ylabel(f"{ejes[1]} [a₀]")
    ax2.set_title(f"Densidad de probabilidad · plano {c['plano']}")
    fig.colorbar(im, ax=ax2, label="Densidad de probabilidad [relativa]", shrink=0.85)
    return fig


def figura_orbitas_3d(t: Transicion, d: dict, n_mostrar: int, altura: int = 640):
    """
    Animación del modelo de Bohr: el electrón gira en la órbita inicial, salta a la final y se emite (o absorbe)
    un fotón dibujado con su color. Radios a escala (rₙ = n²a₀/Z); las velocidades angulares NO están a escala.
    """
    import plotly.graph_objects as go
    z = NUCLEOS[t.nucleo][0]
    ns = range(1, n_mostrar + 1)
    radio = lambda n: n ** 2 / z
    R_ext = radio(n_mostrar)
    th = np.linspace(0, 2 * np.pi, 160)
    datos = []
    for n in ns:
        sel = n in (t.n_inicial, t.n_final)
        datos.append(go.Scatter3d(x=radio(n) * np.cos(th), y=radio(n) * np.sin(th), z=0 * th, mode="lines",
                                  line=dict(color=COLORES["onda"] if sel else COLORES["gris"], width=5 if sel else 2),
                                  name=f"n = {n}", hoverinfo="name", showlegend=False, opacity=1 if sel else 0.5))
    datos.append(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers", marker=dict(size=7, color=COLORES["energia"]),
                              name="núcleo", hoverinfo="name", showlegend=False))
    # Etiquetas «n = k» delante de cada órbita (se omiten las que quedarían amontonadas cerca del núcleo)
    visibles = [n for n in ns if n in (t.n_inicial, t.n_final) or radio(n) - radio(n - 1) > 0.07 * R_ext]
    datos.append(go.Scatter3d(x=[0.0] * len(visibles), y=[-radio(n) for n in visibles], z=[0.0] * len(visibles),
                              mode="text", text=[f"n = {n}" for n in visibles], textposition="bottom center",
                              textfont=dict(color=[("white" if n in (t.n_inicial, t.n_final) else COLORES["gris"])
                                                   for n in visibles], size=12), hoverinfo="skip", showlegend=False))
    i_e, i_f = len(datos), len(datos) + 1
    emision = d["tipo"] == "Emisión"
    c_foton = qc.color_longitud_onda(d["longitud_nm"], fuera="#E6EAF5")
    ri, rf = radio(t.n_inicial), radio(t.n_final)
    # Trayectoria del electrón: 26 cuadros en la órbita inicial, 8 de salto y 40 en la final
    ang, rad, fases = [], [], []
    a0_ = 0.6
    for k in range(26):
        ang.append(a0_ + 0.22 * k * (min(ri, rf) / ri) ** 0.75); rad.append(ri); fases.append("inicial")
    for k in range(1, 9):
        ang.append(ang[-1] + 0.05); rad.append(ri + (rf - ri) * k / 8); fases.append("salto")
    for k in range(40):
        ang.append(ang[-1] + 0.22 * (min(ri, rf) / rf) ** 0.75); rad.append(rf); fases.append("final")
    k_salto = 26 + 4
    p_salto = np.array([rad[k_salto] * np.cos(ang[k_salto]), rad[k_salto] * np.sin(ang[k_salto]), 0.0])
    direccion = np.array([np.cos(ang[k_salto]), np.sin(ang[k_salto]), 0.8])
    direccion /= np.linalg.norm(direccion)
    perp = np.cross(direccion, [0, 0, 1.0])
    perp = perp / np.linalg.norm(perp) if np.linalg.norm(perp) > 0 else np.array([1.0, 0, 0])
    largo = 0.4 * R_ext
    paso = 0.035 * R_ext                       # avance del fotón por cuadro
    limite = 1.3 * R_ext                       # el fotón deja de dibujarse al salir de esta esfera
    ciclos = float(np.clip(7 * 656.0 / d["longitud_nm"], 3, 22))

    vacio = go.Scatter3d(x=[None], y=[None], z=[None], mode="lines", showlegend=False, hoverinfo="skip")

    def foton(desplazamiento):
        s_ = np.linspace(0, 1, 120)
        base = p_salto[None, :] + (desplazamiento + s_[:, None] * largo) * direccion[None, :]
        env = np.sin(np.pi * s_) ** 0.6
        pts = base + (0.06 * R_ext * env * np.sin(2 * np.pi * ciclos * s_))[:, None] * perp[None, :]
        if np.max(np.linalg.norm(pts, axis=1)) > limite:
            return vacio
        return go.Scatter3d(x=pts[:, 0], y=pts[:, 1], z=pts[:, 2], mode="lines", line=dict(color=c_foton, width=6),
                            name="fotón", hoverinfo="name", showlegend=False)

    marcos, etiquetas = [], []
    for k, (a_, r_, f_) in enumerate(zip(ang, rad, fases)):
        e = go.Scatter3d(x=[r_ * np.cos(a_)], y=[r_ * np.sin(a_)], z=[0], mode="markers",
                         marker=dict(size=8, color=COLORES["onda"], line=dict(color="white", width=1)),
                         name="electrón", hoverinfo="name", showlegend=False)
        if emision:
            fo = foton((k - k_salto) * paso) if k >= k_salto else vacio
        else:
            fo = foton(-(k_salto - k) * paso - largo) if k < k_salto else vacio
        texto = {"inicial": f"electrón en la órbita n = {t.n_inicial}",
                 "salto": f"salto cuántico {t.n_inicial} → {t.n_final} (instantáneo en el modelo)",
                 "final": f"electrón en n = {t.n_final}" + (f" · fotón emitido, λ = {d['longitud_nm']:.1f} nm" if emision else "")}[f_]
        if not emision and f_ == "inicial":
            texto += f" · llega un fotón de λ = {d['longitud_nm']:.1f} nm"
        marcos.append(go.Frame(data=[e, fo], traces=[i_e, i_f], name=f"k{k}",
                               layout=dict(annotations=[dict(text=texto, x=0.5, y=1.0, xref="paper", yref="paper",
                                                             showarrow=False, font=dict(size=14, color="white"))])))
        etiquetas.append(f"{k}")
    datos.append(marcos[0].data[0])
    datos.append(marcos[0].data[1])
    fig = go.Figure(data=datos, frames=marcos)
    qc.aplicar_tema_plotly(fig, None, altura=altura)
    L = limite
    oculto = dict(visible=False, range=[-L, L])
    fig.update_layout(scene=dict(xaxis=oculto, yaxis=oculto, zaxis=dict(visible=False, range=[-0.6 * L, 0.9 * L]),
                                 aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.75),
                                 camera=dict(eye=dict(x=0.0, y=-1.0, z=0.62))),
                      annotations=[dict(text=f"electrón en la órbita n = {t.n_inicial}", x=0.5, y=1.0, xref="paper",
                                        yref="paper", showarrow=False, font=dict(size=14, color="white"))],
                      margin=dict(l=0, r=0, t=40, b=0))
    qc.agregar_animacion(fig, [f"k{k}" for k in range(len(marcos))], etiquetas, duracion_ms=90)
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
    ax2.set_title("Líneas de emisión")
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
    ax.set_title(f"Espectro de emisión · {NUCLEOS[nucleo][2]}")
    ax.grid(alpha=0.25, which="both", axis="x")
    return fig


# =====================================================================
# 3. PRUEBAS NUMÉRICAS
# =====================================================================
# ---------------------------------------------------------------------
# Predice y experimenta · Laboratorio inverso · Informe
# ---------------------------------------------------------------------
def _calc_bohr(magnitud, modificar, unidad):
    def f(t: Transicion):
        return float(magnitud(t)), float(magnitud(modificar(t))), unidad
    return f


def _abs_energia(t):
    return abs(float(energia_nivel(t.n_final, t.nucleo, t.masa_reducida)))


def _radio_nm(t):
    return float(radio_orbita(t.n_final, t.nucleo, t.masa_reducida)) * 1e9


def _doble_n(t: Transicion):
    return Transicion(t.n_inicial, 2 * t.n_final, t.nucleo, t.masa_reducida)


def _sin_correccion_h(t: Transicion):
    return Transicion(t.n_inicial, t.n_final, "H", False)


def _sin_correccion_he(t: Transicion):
    return Transicion(t.n_inicial, t.n_final, "He+", False)


PREGUNTAS_PREDICE = [
    predice.Pregunta(
        "energia_2n", "¿Qué le pasa a la magnitud de la energía |Eₙ| si se duplica el nivel n (nivel final de la transición)?",
        "Se cambia n → 2n (mismo átomo)",
        (predice.Opcion("Se duplica", 2.0), predice.Opcion("Se reduce a la mitad", 0.5),
         predice.Opcion("Se reduce a la cuarta parte", 0.25), predice.Opcion("Se cuadruplica", 4.0)),
        ("Mira la dependencia de Eₙ con n.", "Eₙ = −Z²·Ry/n²: n aparece al cuadrado en el denominador."),
        "|Eₙ| ∝ 1/n²: al duplicar n el electrón está menos ligado y |Eₙ| se divide entre 4.", "bohr", "Energía |Eₙ|",
        _calc_bohr(_abs_energia, _doble_n, "eV")),
    predice.Pregunta(
        "radio_2n", "¿Qué le pasa al radio de la órbita de Bohr si se duplica n?", "Se cambia n → 2n (mismo átomo)",
        (predice.Opcion("Se duplica", 2.0), predice.Opcion("Se cuadruplica", 4.0), predice.Opcion("Se multiplica por 8", 8.0),
         predice.Opcion("Se reduce a la mitad", 0.5)),
        ("En el modelo de Bohr, el radio crece con una potencia de n.", "rₙ = n²·a₀/Z."),
        "rₙ ∝ n²: al duplicar n el radio se cuadruplica.", "bohr", "Radio rₙ", _calc_bohr(_radio_nm, _doble_n, "nm")),
    predice.Pregunta(
        "carga_nuclear", "¿Qué le pasa a |Eₙ| (mismo n) si el átomo pasa de H a He⁺ (Z = 1 → 2)?",
        "Se cambia H → He⁺ (sin corrección de masa reducida)",
        (predice.Opcion("Se duplica", 2.0), predice.Opcion("Se cuadruplica", 4.0), predice.Opcion("Se reduce a la mitad", 0.5),
         predice.Opcion("No cambia", 1.0)),
        ("Eₙ contiene Z elevada a una potencia.", "Eₙ = −Z²·Ry/n²."),
        "|Eₙ| ∝ Z²: con el doble de carga nuclear, el electrón está cuatro veces más ligado.", "bohr", "Energía |Eₙ|",
        lambda t: (_abs_energia(_sin_correccion_h(t)), _abs_energia(_sin_correccion_he(t)), "eV")),
]


def _lambda_nm_reto(v: dict) -> float:
    if int(v["ni"]) == int(v["nf"]):
        raise ValueError("Los niveles inicial y final deben ser distintos: una transición requiere un cambio de nivel.")
    return longitud_rydberg(int(v["ni"]), int(v["nf"]), "H") * 1e9


RETOS_INVERSOS = [
    inverso.Reto(
        "bohr_lambda", "¿Qué transición del hidrógeno emite o absorbe 486.27 nm?",
        "Encuentra los niveles inicial y final del hidrógeno (con la masa del protón) cuya transición corresponde a "
        "una longitud de onda de 486.27 nm (línea azul-verdosa de la serie de Balmer).",
        "Longitud de onda λ", "nm", 486.27,
        (inverso.Variable("ni", "Nivel inicial nᵢ", "", 1, N_MAX, 1, 3, True),
         inverso.Variable("nf", "Nivel final n_f", "", 1, N_MAX, 1, 2, True)),
        _lambda_nm_reto,
        ("Esta línea pertenece a la serie de Balmer: el nivel inferior es el mismo para todas sus líneas.",
         "La serie de Balmer termina en n = 2 (en emisión). Prueba valores de nᵢ por encima de 2.",
         "1/λ = R·(1/n_f² − 1/nᵢ²). Con n_f = 2, la línea de 486 nm es la segunda de la serie."),
        "La longitud de onda depende de la diferencia 1/n_f² − 1/nᵢ² (ley de Rydberg); solo una pareja la reproduce.",
        lambda v: "Con **n_f = 2**: 1/λ = R(1/4 − 1/nᵢ²) ⇒ **nᵢ = 4** (emisión 4 → 2) reproduce λ = 486.27 nm.",
        "λ depende de 1/n_f² − 1/nᵢ²: una diferencia mayor da una longitud de onda menor.",
        tol_exacta=5e-5, tol_aprox=0.02,
        soluciones="Hay dos respuestas equivalentes: la emisión 4 → 2 y la absorción 2 → 4 (misma energía de fotón).",
        metodo="Ley de Rydberg evaluada directamente; se prueban las parejas de niveles sin búsqueda numérica."),
]


def informe_transicion(t: Transicion, d: dict, conclusiones: str = "") -> informes.Informe:
    _, _, nombre = NUCLEOS[t.nucleo]
    niveles = np.arange(1, 9)
    with informes.estilo_claro():
        fig, ax = informes.figura_clara(6.0, 3.6)
        for k in niveles:
            e = float(energia_nivel(k, t.nucleo, t.masa_reducida))
            ax.hlines(e, 0.3, 0.7, color="#1F3A93")
            ax.text(0.72, e, f"n = {k}", va="center", fontsize=8)
        if max(t.n_inicial, t.n_final) <= 8:
            ax.annotate("", xy=(0.5, d["ef"]), xytext=(0.5, d["ei"]), arrowprops={"arrowstyle": "->", "color": "#B03A2E", "lw": 2})
        ax.set(ylabel="Energía [eV]", title=f"Niveles de {nombre}", xticks=[], xlim=(0, 1))
        fig.tight_layout()
    return informes.Informe(
        titulo=f"Transición {t.n_inicial} → {t.n_final} en {nombre}", simulador="Átomo de hidrógeno · modelo de Bohr",
        objetivo="Calcular la energía, la frecuencia y la longitud de onda del fotón asociado a una transición entre niveles.",
        modelo="Modelo de Bohr (semiclásico) para átomos de un electrón. Sirve para niveles y series; no describe la "
               "estructura fina ni las reglas de selección.",
        ecuaciones=[r"E_n=-\frac{Z^2\,Ry}{n^2}", r"\Delta E=h\nu=\frac{hc}{\lambda}",
                    r"\frac{1}{\lambda}=R\,Z^2\left|\frac{1}{n_f^2}-\frac{1}{n_i^2}\right|"],
        parametros=[("Átomo", nombre, ""), ("Nivel inicial nᵢ", f"{t.n_inicial}", ""), ("Nivel final n_f", f"{t.n_final}", ""),
                    ("Masa reducida", "Sí" if t.masa_reducida else "No", "")],
        procedimiento=["Se calculan Eᵢ y E_f con Eₙ = −Z²·Ry/n².", "ΔE = E_f − Eᵢ y la energía del fotón es |ΔE|.",
                       "ν = |ΔE|/h y λ = c/ν.", "Se comprueba λ con la ley de Rydberg."],
        resultados=[("Tipo de transición", d["tipo"], ""), ("Energía inicial", f"{d['ei']:.8g}", "eV"),
                    ("Energía final", f"{d['ef']:.8g}", "eV"), ("Energía del fotón", f"{d['e_foton_ev']:.8g}", "eV"),
                    ("Frecuencia ν", f"{d['frecuencia']:.8g}", "Hz"), ("Longitud de onda λ", f"{d['longitud_nm']:.8g}", "nm"),
                    ("λ con la ley de Rydberg", f"{d['longitud_rydberg_nm']:.8g}", "nm"),
                    ("Diferencia relativa", f"{d['diferencia_rel']:.2e}", ""), ("Serie", d["serie"], "")],
        figuras=[fig],
        preguntas=["¿Por qué las líneas de una serie se acercan a un límite?", "¿Qué cambia si el átomo es He⁺ en vez de H?"],
        conclusiones=conclusiones)


def _pestana_predice(t: Transicion):
    st.markdown("Predice, ejecuta y compara. Las preguntas usan el **nivel final** de la transición que elegiste arriba.")
    _, _, nombre = NUCLEOS[t.nucleo]
    datos = {"simulador": "Átomo de hidrógeno · modelo de Bohr", "modelo": "Modelo de Bohr para átomos de un electrón.",
             "ecuaciones": [r"E_n=-\frac{Z^2\,Ry}{n^2}"],
             "parametros": [("Átomo", nombre, ""), ("Nivel inicial", f"{t.n_inicial}", ""), ("Nivel final", f"{t.n_final}", ""),
                            ("Masa reducida", "Sí" if t.masa_reducida else "No", "")]}
    predice.panel(PREGUNTAS_PREDICE, t, "bohr", datos_informe=datos)


def _pestana_instrumentos(t: Transicion):
    d = calcular_transicion(t)
    st.markdown("**Fotón entre niveles de este átomo.** Con las energías del modelo de Bohr (con la corrección de masa "
                "reducida si está activada).")
    instrumentos.panel_fotones(lambda k: float(energia_nivel(int(k), t.nucleo, t.masa_reducida)) * E, "bohr", N_MAX,
                               n_ini=t.n_inicial, n_fin=t.n_final)
    informes.boton_informe(lambda texto: informe_transicion(t, d, texto), "bohr_inf",
                           f"bohr_informe_{t.n_inicial}_{t.n_final}")


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
    r.comprobar("La serie la fija el nivel inferior: absorción 1 → 4 es Lyman; emisión 4 → 1 también",
                calcular_transicion(Transicion(1, 4, "H", True))["serie"] == "Lyman"
                and calcular_transicion(Transicion(4, 1, "H", True))["serie"] == "Lyman")
    r.comprobar("E_fotón = hν = hc/λ", abs(ha["e_foton_j"] - H * ha["frecuencia"]) / ha["e_foton_j"] < 1e-14
                and abs(ha["frecuencia"] * ha["longitud_m"] - C) / C < 1e-14)
    r.comprobar("r₁ = a₀, rₙ = n²a₀ (H, núcleo infinito)", abs(float(radio_orbita(1)) - A0) < 1e-22
                and abs(float(radio_orbita(3)) / A0 - 9) < 1e-12)
    r.comprobar("v₁ = αc ≈ 2.19×10⁶ m/s", abs(float(velocidad_orbita(1)) - 2.1877e6) / 2.1877e6 < 1e-4)
    r.comprobar("Paschen α (4 → 3) en el infrarrojo", calcular_transicion(Transicion(4, 3, "H", True))["region"] == "Infrarrojo")
    r.comprobar("He⁺ 4 → 2 ≈ Hβ/4 (Z² = 4)… salvo la masa reducida",
                abs(calcular_transicion(Transicion(4, 2, "He+", False))["longitud_nm"] * 4
                    - calcular_transicion(Transicion(4, 2, "H", False))["longitud_nm"]) < 1e-9)
    # --- Átomo de hidrógeno cuántico ---
    estados = [(n, l) for n in range(1, 6) for l in range(n)]
    normas = [calcular_orbital(n, l, 0)["norma"] for n, l in estados]
    r.comprobar("Funciones radiales normalizadas: ∫R²r²dr = 1 (n ≤ 5, todos los l)", max(abs(x - 1) for x in normas) < 1e-6,
                f"máx |∫−1| = {max(abs(x - 1) for x in normas):.1e}")
    rr = np.linspace(0, radio_maximo(4), 40001) * 1.0
    num = (getattr(np, "trapezoid", None) or np.trapz)(rr ** 3 * radial_hidrogeno(rr, 4, 2) ** 2, rr)
    r.comprobar("⟨r⟩ numérico = (a₀/2)[3n² − l(l+1)] (4d)", abs(num / r_medio(4, 2) - 1) < 1e-6)
    r.comprobar("Para l = n − 1 el radio más probable es el de Bohr, n²a₀",
                all(abs(calcular_orbital(n, n - 1, 0)["r_probable"] - n ** 2) < 0.01 for n in range(1, 6)))
    r.comprobar("Nodos radiales = n − l − 1 (2s: un nodo en r = 2a₀)",
                all(len(calcular_orbital(n, l, 0)["nodos_r"]) == n - l - 1 for n, l in estados)
                and abs(calcular_orbital(2, 0, 0)["nodos_r"][0] - 2.0) < 0.01)
    r1 = np.linspace(0.05, 20, 4000) * A0
    psi = r1 * radial_hidrogeno(r1, 3, 1)                           # u(r) = r R(r)
    d2 = np.gradient(np.gradient(psi, r1), r1)
    lado = -HBAR ** 2 / (2 * M_E) * d2 + (HBAR ** 2 * 2 / (2 * M_E * r1 ** 2) - E ** 2 / (4 * np.pi * const.epsilon_0 * r1)) * psi
    en = float(energia_nivel(3)) * E
    resid = np.max(np.abs(lado[50:-50] - en * psi[50:-50])) / np.max(np.abs(en * psi))
    r.comprobar("R₃₁ resuelve la ecuación de Schrödinger radial con E₃ de Bohr (degeneración en l)", resid < 1e-3,
                f"residuo relativo = {resid:.1e}")
    mst = muestrear_posiciones(3, 2, 0, True, 40000, 7)
    err = abs(mst["r"].mean() - r_medio(3, 2) / A0) / (calcular_orbital(3, 2, 0)["delta_r"] / np.sqrt(40000))
    r.comprobar("Muestreo Monte Carlo: el promedio de las medidas coincide con ⟨r⟩ (dentro de 4σ)", err < 4,
                f"desviación = {err:.2f} σ")
    px = muestrear_posiciones(2, 1, 1, True, 40000, 3)
    r.comprobar("Orbital 2p_x: ⟨x²⟩ = 3⟨y²⟩ y ψ > 0 hacia +x", abs(np.mean(px["x"] ** 2) / np.mean(px["y"] ** 2) - 3) < 0.15
                and np.all(px["color"][px["x"] > 0.2] > 0))
    o1 = calcular_orbital(1, 0, 0)
    r.comprobar("Incertidumbre en 1s: Δx·Δpₓ = ħ/√3 ≈ 0.577ħ ≥ ħ/2", abs(o1["dx_dp_s"] - 1 / np.sqrt(3)) < 1e-12)
    r.comprobar("Δx·Δpₓ ≥ ħ/2 en todos los estados s (n ≤ 6)",
                all(calcular_orbital(n, 0, 0)["dx_dp_s"] >= 0.5 for n in range(1, 7)))
    r.comprobar_error("Orbital: rechaza l ≥ n", validar_orbital, 2, 2, 0)
    r.comprobar_error("Orbital: rechaza |m| > l", validar_orbital, 3, 1, 2)
    r.comprobar_error("Rechaza nᵢ = n_f", validar_transicion, 2, 2)
    r.comprobar_error("Rechaza n < 1", validar_transicion, 0, 2)
    r.comprobar_error("Rechaza n no entero", validar_transicion, 2.5, 1)
    r.comprobar_error(f"Rechaza n > {N_MAX}", validar_transicion, N_MAX + 1, 1)
    r.comprobar_error("Rechaza átomo desconocido", validar_transicion, 3, 2, "U92+")
    r.comprobar_error("Serie: rechaza nᵢ máximo ≤ n_f", calcular_serie, 3, 3)
    # --- Modo «Predice y experimenta» y laboratorio inverso: la respuesta correcta sale del cálculo
    p_pd = Transicion(3, 2, "H", False)
    for q in PREGUNTAS_PREDICE:
        r.comprobar(f"Pregunta de predicción «{q.id}»: la respuesta correcta sale del cálculo",
                    predice.validar_pregunta(q, p_pd) == [], "; ".join(predice.validar_pregunta(q, p_pd)))
    for reto in RETOS_INVERSOS:
        r.comprobar(f"Reto inverso «{reto.id}» bien construido", inverso.validar_reto(reto) == [],
                    "; ".join(inverso.validar_reto(reto)))
    return r


# =====================================================================
# 4. INTERFAZ (Streamlit)
# =====================================================================
VALORES_INICIALES = {
    "bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2, "bohr_mu": True, "bohr_escala": "real", "bohr_nmax": 6,
    "bohr_serie_nf": 2, "bohr_serie_nmax": 12,
    "bohr_vista3d": "nube", "bohr_orb_n": 2, "bohr_orb_l": 1, "bohr_orb_m": 0, "bohr_orb_tipo": "real",
    "bohr_orb_puntos": 6000, "bohr_orb_semilla": 1, "bohr_orb_bohr": True,
}
DEMOS = {
    "Hα: 3 → 2 (rojo, Balmer)": {"bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2},
    "Lyman α: 2 → 1 (ultravioleta)": {"bohr_nucleo": "H", "bohr_ni": 2, "bohr_nf": 1},
    "Absorción desde el fundamental: 1 → 4": {"bohr_nucleo": "H", "bohr_ni": 1, "bohr_nf": 4},
    "Paschen α: 4 → 3 (infrarrojo)": {"bohr_nucleo": "H", "bohr_ni": 4, "bohr_nf": 3},
    "He⁺: 4 → 3 (Z = 2)": {"bohr_nucleo": "He+", "bohr_ni": 4, "bohr_nf": 3},
}
EJEMPLOS_ORBITALES = {
    "1s · estado fundamental": (1, 0, 0),
    "2s · un nodo radial": (2, 0, 0),
    "2p_z · dos lóbulos": (2, 1, 0),
    "2p_x": (2, 1, 1),
    "3s · dos nodos radiales": (3, 0, 0),
    "3p_y": (3, 1, -1),
    "3d_z² · lóbulos y anillo": (3, 2, 0),
    "3d_xy · cuatro lóbulos": (3, 2, -2),
    "4f_xyz · ocho lóbulos": (4, 3, -2),
    "6h (l = 5) · radio de Bohr 36 a₀": (6, 5, 0),
}
N_ORBITAS_3D = 12

GUIA = [
    {"titulo": "Las líneas visibles del hidrógeno",
     "objetivo": "Identificar las cuatro líneas de Balmer observables con un espectroscopio.",
     "pasos": ["Cargar la configuración ($n_f$ = 2, nᵢ hasta 6).", "Registrar λ para nᵢ = 3, 4, 5 y 6 y su color.",
               "Aumentar nᵢ máximo a 30 y observar el límite de la serie."],
     "pregunta": "¿Por qué las líneas se juntan hacia longitudes de onda cortas?",
     "resultado": "Hα 656.5 nm (rojo), Hβ 486.3 nm (azul verdoso), Hγ 434.2 nm y Hδ 410.3 nm (violeta). Al subir nᵢ "
                  "los niveles se acercan entre sí (Eₙ ∝ −1/n²), así que las energías de los fotones tienden a "
                  "Ry/4 y las λ se acumulan en el límite de la serie, 364.7 nm (ya en el ultravioleta).",
     "pestana": "Series y espectro", "config": {"bohr_nucleo": "H", "bohr_serie_nf": 2, "bohr_serie_nmax": 6, "bohr_mu": True}},
    {"titulo": "Emisión y absorción",
     "objetivo": "Comparar una transición con su inversa.",
     "pasos": ["Cargar la configuración (3 → 2).", "Registrar ΔE y λ.", "Intercambia los niveles (2 → 3)."],
     "pregunta": "¿Qué cambia y qué se conserva al invertir la transición?",
     "resultado": "Cambiar el signo de ΔE del átomo (pierde energía al emitir, la gana al absorber) y el sentido de la "
                  "flecha; la energía y la longitud de onda del fotón son idénticas (656.47 nm). Por eso un gas frío "
                  "absorbe exactamente las mismas líneas que emite caliente.",
     "pestana": "Transición", "config": {"bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2}},
    {"titulo": "Corrección de masa reducida",
     "objetivo": "Explicar la pequeña diferencia entre Bohr y la fórmula de Rydberg medida.",
     "pasos": ["Cargar la configuración (3 → 2, sin masa reducida).", "Registrar la diferencia Bohr–Rydberg.",
               "Activar «Corrección de masa reducida» y vuelve a mirarla."],
     "pregunta": "¿Cuál es el origen de una diferencia de ≈ 0.05 %?",
     "resultado": "Sin corrección la diferencia es ≈ 5.4×10⁻⁴ = mₑ/m_p: el modelo supone el núcleo inmóvil. Con la "
                  "masa reducida μ = mₑm_p/(mₑ + m_p) ambos cálculos coinciden (diferencia < 10⁻¹⁰). Este efecto "
                  "permitió descubrir el deuterio en 1931.",
     "pestana": "Transición", "config": {"bohr_nucleo": "H", "bohr_ni": 3, "bohr_nf": 2, "bohr_mu": False}},
    {"titulo": "Iones hidrogenoides",
     "objetivo": "Ver el efecto de la carga nuclear Z.",
     "pasos": ["Cargar la configuración (He⁺, 4 → 2).", "Comparar λ con la de Hβ (4 → 2 en el hidrógeno).",
               "Observar el radio de las órbitas."],
     "pregunta": "¿Cómo escalan las energías, las longitudes de onda y los radios con Z?",
     "resultado": "Eₙ ∝ Z², así que λ ∝ 1/Z²: la línea 4 → 2 del He⁺ (≈ 121.5 nm) es casi exactamente Hβ/4, y "
                  "coincide casi con Lyman α del hidrógeno (la diferencia viene de la masa reducida, base de la "
                  "«serie de Pickering»). Los radios rₙ = n²a₀/Z son la mitad.",
     "pestana": "Transición", "config": {"bohr_nucleo": "He+", "bohr_ni": 4, "bohr_nf": 2, "bohr_mu": True}},
    {"titulo": "La nube de probabilidad se construye medida a medida",
     "objetivo": "Ver cómo la forma del orbital aparece solo al repetir muchas veces la medida de la posición.",
     "pasos": ["Cargar la configuración (orbital 1s) y abre «Átomo en 3D».",
               "Pulsar «Reproducir» y observar las primeras 10 o 20 medidas.",
               "Deja que se acumulen todas y compara la nube con la órbita de Bohr (círculo blanco).",
               "Cambiar la semilla: el experimento se repite con otras medidas."],
     "pregunta": "¿Es posible predecir dónde aparecerá la próxima medida? ¿Qué magnitudes sí son predecibles?",
     "resultado": "No: cada medida cae en un lugar distinto y al azar. Lo que es predecible es la DISTRIBUCIÓN de "
                  "muchas medidas, |ψ|². Con pocas medidas no se distingue ninguna forma; con miles aparece la esfera "
                  "difusa del 1s. El electrón no recorre el círculo de Bohr: se encuentra a cualquier distancia, "
                  "aunque la más probable es justamente a₀ (r más probable = 1.00 a₀).",
     "pestana": "Átomo en 3D",
     "config": {"bohr_vista3d": "nube", "bohr_orb_n": 1, "bohr_orb_l": 0, "bohr_orb_m": 0, "bohr_orb_tipo": "real",
                "bohr_nucleo": "H"}},
    {"titulo": "¿Cuándo coincide Bohr con la mecánica cuántica?",
     "objetivo": "Comparar el radio más probable de cada orbital con el radio de Bohr del mismo n.",
     "pasos": ["Cargar la configuración (n = 3, orbital 3s).", "Registrar el radio más probable y el de Bohr (9 a₀).",
               "Cambiar a l = 1 (3p) y a l = 2 (3d) y vuelve a comparar.", "Observar el número de nodos radiales."],
     "pregunta": "¿Con qué valor de l coinciden los dos radios?",
     "resultado": "Solo con l = n − 1 (el 3d): su radio más probable es exactamente n²a₀ = 9 a₀, el de Bohr, y no "
                  "tiene nodos radiales (es la «órbita circular» cuántica). El 3s tiene 2 nodos radiales y su máximo "
                  "principal está más lejos (≈ 13.1 a₀), aunque tiene probabilidad apreciable cerca del núcleo. Las "
                  "energías, en cambio, son iguales para todos los l: Eₙ = −13.6 eV/n² en ambos modelos.",
     "pestana": "Átomo en 3D",
     "config": {"bohr_vista3d": "nube", "bohr_orb_n": 3, "bohr_orb_l": 0, "bohr_orb_m": 0, "bohr_orb_tipo": "real",
                "bohr_nucleo": "H"}},
    {"titulo": "El principio de incertidumbre dentro del átomo",
     "objetivo": "Comprobar que el estado fundamental cumple Δx·Δpₓ ≥ ħ/2 y entender por qué el átomo no colapsa.",
     "pasos": ["Cargar la configuración (1s).", "Registrar Δx·Δpₓ.", "Repite con 2s y 3s."],
     "pregunta": "Si el electrón se acercara más al núcleo, ¿qué le pasaría a su energía cinética?",
     "resultado": "Para el 1s, Δx·Δpₓ = ħ/√3 ≈ 0.577 ħ, por encima del mínimo 0.5 ħ; para 2s y 3s el producto crece. "
                  "Confinar el electrón en una región más pequeña (Δx menor) obliga a un Δp mayor y por tanto a más "
                  "energía cinética (≈ ħ²/2mr²). El equilibrio entre esa energía y la atracción del núcleo fija el "
                  "tamaño del átomo, a₀, y la energía −13.6 eV: el átomo es estable gracias a la incertidumbre.",
     "pestana": "Átomo en 3D",
     "config": {"bohr_vista3d": "nube", "bohr_orb_n": 1, "bohr_orb_l": 0, "bohr_orb_m": 0, "bohr_orb_tipo": "real",
                "bohr_nucleo": "H"}},
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
     "opciones": ["el nivel más alto de la transición", "el nivel más bajo de la transición",
                  "la diferencia entre los dos niveles", "la temperatura del gas"],
     "correcta": 1, "explicacion": "Lyman (nivel bajo 1), Balmer (2), Paschen (3)… En emisión es el nivel final; en "
                                   "absorción, el inicial. Por eso 1 → 4 (absorción) es una línea de Lyman."},
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
    {"enunciado": "En la nube de probabilidad, cada punto representa…",
     "opciones": ["un tramo de la trayectoria del electrón", "una medida de la posición en un átomo preparado en el mismo estado",
                  "un electrón distinto del mismo átomo", "un fotón emitido por el átomo"], "correcta": 1,
     "explicacion": "El átomo de hidrógeno tiene un solo electrón. Cada punto es el resultado de UNA medida; la nube "
                    "completa es la distribución |ψ|² de muchas medidas repetidas. No hay trayectoria."},
    {"enunciado": "Para el orbital 1s del hidrógeno, la distancia al núcleo más probable es…",
     "opciones": ["0 (el núcleo)", "a₀ = 0.0529 nm, el radio de Bohr", "1.5 a₀", "4 a₀"], "correcta": 1,
     "explicacion": "P(r) = r²|R|² es máxima en r = a₀. Nótese que |ψ|² (por unidad de volumen) es máxima en el núcleo, "
                    "pero el volumen de una capa esférica crece como r², y el producto es máximo en a₀. "
                    "El valor medio es ⟨r⟩ = 1.5 a₀."},
    {"enunciado": "Según la mecánica cuántica, ¿por qué el electrón no cae al núcleo?",
     "opciones": ["porque gira muy rápido", "porque confinarlo en una región menor aumenta su Δp y su energía cinética",
                  "porque el núcleo lo repele a distancias cortas", "porque emite fotones que lo empujan hacia afuera"],
     "correcta": 1,
     "explicacion": "Por el principio de incertidumbre, Δp ≳ ħ/Δx: concentrarlo cerca del núcleo cuesta energía "
                    "cinética ≈ ħ²/2mr². El mínimo de la energía total está en r ≈ a₀ con E = −13.6 eV."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("bohr_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


def _aplicar_ejemplo_orbital():
    eleccion = st.session_state.get("bohr_orb_ejemplo")
    if eleccion in EJEMPLOS_ORBITALES:
        n, l, m = EJEMPLOS_ORBITALES[eleccion]
        qc.fijar_estado({"bohr_orb_n": n, "bohr_orb_l": l, "bohr_orb_m": m, "bohr_orb_tipo": "real"})


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
        ("Serie espectral", d["serie"], f"La fija el nivel más bajo de la transición. Región típica: {d['region_serie']}"),
        ("Diferencia Bohr–Rydberg", f"{d['diferencia_rel']:.2e}",
         "Relativa. Sin masa reducida ≈ mₑ/M; con masa reducida ≈ 0."),
    ])
    color = qc.color_longitud_onda(d["longitud_nm"], fuera=None)
    if color:
        st.markdown(f'<p class="ql-subtitulo"><span style="display:inline-block;width:2.4rem;height:.8rem;border-radius:2px;'
                    f'background:{color};vertical-align:-1px;margin-right:.5rem"></span>Color aproximado de la línea '
                    f'({d["region"].lower()})</p>', unsafe_allow_html=True)
    qc.seccion("Diagrama de niveles y espectro")
    n_max = max(int(st.session_state["bohr_nmax"]), t.n_inicial, t.n_final)
    qc.mostrar_pyplot(figura_transicion(t, d, n_max, st.session_state["bohr_escala"] == "real"),
                      archivo=f"bohr_{t.nucleo}_{t.n_inicial}a{t.n_final}.png")
    st.caption("Arriba: niveles de energía con la transición elegida (flecha gruesa), las demás líneas de la misma "
               "serie (flechas tenues) y el fotón dibujado como una onda de su color. Abajo: posición de la línea en "
               "el espectro electromagnético (escala logarítmica) junto a las demás líneas de la serie.")
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
            "- Bohr postuló órbitas estables con momento angular cuantizado L = nħ. De ahí se obtienen los radios "
            "rₙ = n²a₀/Z y las energías Eₙ = −Z²·13.6 eV/n².\n"
            "- El electrón solo emite o absorbe luz al **saltar** entre órbitas, con un fotón de energía exactamente "
            "|E_f − Eᵢ|. Por eso el espectro está formado por **líneas** y no es continuo.\n"
            "- Los niveles se juntan al subir n: por encima de E = 0 el electrón queda libre (continuo de ionización).\n"
            "- El modelo reproduce el espectro del hidrógeno, pero **no** es la descripción moderna: los electrones no "
            "siguen órbitas definidas (pestaña «Átomo en 3D») y el modelo falla para átomos de más de un electrón.")


# ---------------------------------------------------------------------
# Átomo en 3D
# ---------------------------------------------------------------------
@st.cache_data(show_spinner="Simulando las medidas de la posición…", max_entries=16)
def _cache_nube(n, l, m, real, puntos, semilla, nucleo, mu, mostrar_bohr, altura):
    return figura_nube_3d(n, l, m, real, puntos, semilla, nucleo, mu, mostrar_bohr=mostrar_bohr, animar=True,
                          altura=altura)


@st.cache_data(show_spinner="Preparando la animación…", max_entries=16)
def _cache_orbitas(ni, nf, nucleo, mu, n_mostrar, altura):
    t = Transicion(ni, nf, nucleo, mu)
    return figura_orbitas_3d(t, calcular_transicion(t), n_mostrar, altura=altura)


def _ajustar_numeros_cuanticos():
    """Mantiene 0 ≤ l ≤ n − 1 y |m| ≤ l antes de dibujar los controles (también con valores del enlace)."""
    ss = st.session_state
    try:
        n = int(min(max(int(ss.get("bohr_orb_n", 2)), 1), N_ORBITAL_MAX))
        l = int(min(max(int(ss.get("bohr_orb_l", 0)), 0), n - 1))
        m = int(min(max(int(ss.get("bohr_orb_m", 0)), -l), l))
    except (TypeError, ValueError):
        n, l, m = 2, 1, 0
    ss["bohr_orb_n"], ss["bohr_orb_l"], ss["bohr_orb_m"] = n, l, m


def _texto_m(m: int) -> str:
    return str(m).replace("-", "−")


def _subvista_nube(t: Transicion):
    _ajustar_numeros_cuanticos()
    ss = st.session_state
    with st.container(border=True):
        qc.seccion("Estado cuántico (n, l, m)")
        c1, c2, c3, c4 = st.columns(4, vertical_alignment="bottom")
        n = c1.selectbox("Número principal n", list(range(1, N_ORBITAL_MAX + 1)), key="bohr_orb_n",
                         help="Fija la energía: Eₙ = −Z²·13.6 eV/n², igual que en el modelo de Bohr.")
        l = c2.selectbox("Momento angular l", list(range(0, int(n))), key="bohr_orb_l",
                         format_func=lambda k: f"l = {k} ({LETRAS_L[k]})",
                         help="0 ≤ l ≤ n − 1. Fija la forma del orbital y |L| = √(l(l+1)) ħ.")
        real = ss.get("bohr_orb_tipo", "real") == "real"
        m = c3.selectbox("Número magnético m", list(range(-int(l), int(l) + 1)), key="bohr_orb_m",
                         format_func=(lambda k: f"m = {_texto_m(k)} · {nombre_orbital_real(int(n), int(l), k)}") if real
                         else (lambda k: f"m = {_texto_m(k)}"),
                         help="−l ≤ m ≤ l. Fija la orientación (proyección Lz = mħ en los orbitales complejos).")
        c4.radio("Tipo de orbital", ["real", "complejo"], key="bohr_orb_tipo", horizontal=True,
                 format_func=lambda k: "Real (química)" if k == "real" else "Complejo (Lz definido)",
                 help="Los reales (pₓ, d_xy…) son combinaciones de m y −m; se colorean por el SIGNO de ψ. "
                      "Los complejos tienen Lz = mħ definido y se colorean por la FASE de ψ.")
        qc.seccion("Simulación de las medidas")
        e1, e2, e3, e4 = st.columns(4, vertical_alignment="bottom")
        e1.select_slider("Número de medidas", [1000, 2000, 4000, 6000, 10000, 15000, 20000], key="bohr_orb_puntos",
                         help="Cada punto es una medida de la posición del electrón en un átomo preparado en este estado.")
        e2.number_input("Semilla aleatoria", 1, 9999, step=1, key="bohr_orb_semilla",
                        help="Cambiarla repite el experimento con otras medidas: los puntos cambian, la forma no.")
        e3.selectbox("Orbital de ejemplo", ["Seleccionar…"] + list(EJEMPLOS_ORBITALES), key="bohr_orb_ejemplo",
                     on_change=_aplicar_ejemplo_orbital)
        e4.toggle("Órbita de Bohr del mismo n", key="bohr_orb_bohr")
    try:
        n, l, m = validar_orbital(n, l, m)
    except ValueError as error:
        qc.error(error)
        return
    real = ss["bohr_orb_tipo"] == "real"
    o = calcular_orbital(n, l, m, t.nucleo, t.masa_reducida)
    escala = o["a"] / A0                                  # paso de unidades de a a unidades de a₀
    nombre = nombre_orbital_real(n, l, m) if real else f"{n}{LETRAS_L[l]} (m = {_texto_m(m)})"
    qc.seccion("Resultados")
    items = [
        ("Orbital", nombre, f"n = {n}, l = {l}, m = {_texto_m(m)} · {NUCLEOS[t.nucleo][2]}"),
        (r"Energía $E_n$ [eV]", f"{o['energia']:.5f}", "Depende solo de n: coincide con el modelo de Bohr."),
        (r"Distancia media $\langle r\rangle$ [a₀]", f"{o['r_medio'] * escala:.3f}", "⟨r⟩ = (a₀/2Z)[3n² − l(l+1)]"),
        ("Incertidumbre Δr [a₀]", f"{o['delta_r'] * escala:.3f}", "Dispersión de la distancia al núcleo: √(⟨r²⟩ − ⟨r⟩²)"),
        ("r más probable [a₀]", f"{o['r_probable'] * escala:.3f}", "Máximo de P(r) = r²|R(r)|²"),
        ("Radio de Bohr rₙ [a₀]", f"{o['r_bohr'] * escala:.3f}",
         "rₙ = n²a₀/Z. Coincide con la distancia más probable solo si l = n − 1."),
    ]
    if o["dx_dp_s"] is not None:
        items.append((r"$\Delta x\,\Delta p_x$ [ħ]", f"{o['dx_dp_s']:.4f}",
                      "Producto de incertidumbres en la dirección x. Siempre ≥ 0.5 ħ (Heisenberg)."))
    else:
        items.append(("Momento angular |L| [ħ]", f"{o['L']:.4f}",
                      f"√(l(l+1)) = √{l * (l + 1)}. En Bohr sería L = nħ = {n} ħ."))
    items.append(("Nodos radiales / angulares", f"{o['nodos_radiales']} / {o['nodos_angulares']}",
                  "Radiales: n − l − 1 (esferas). Angulares: l (planos o conos). Total: n − 1."))
    qc.metricas(items)

    qc.seccion("Nube de probabilidad en 3D")
    altura = 520 if qc.modo_compacto() else 680
    figura = _cache_nube(n, l, m, real, int(ss["bohr_orb_puntos"]), int(ss["bohr_orb_semilla"]), t.nucleo,
                         t.masa_reducida, bool(ss["bohr_orb_bohr"]), altura)
    qc.mostrar_plotly(figura, "bohr_nube", archivo=f"bohr_nube_{n}{LETRAS_L[l]}_m{m}.html")
    st.caption("Pulsar «Reproducir» para ver cómo se acumulan las medidas (de 1 al total). Cada punto es una medida "
               "independiente de la posición del electrón; arrastra para girar el átomo. "
               + ("Colores: signo de ψ (cian +, naranja −)." if real or m == 0 else "Colores: fase de ψ, que gira "
                  f"{abs(m)} {'vez' if abs(m) == 1 else 'veces'} alrededor del eje z (Lz = {_texto_m(m)} ħ).")
               + " Distancias en radios de Bohr a₀"
               + (" (con masa reducida la unidad de la figura es a = a₀·mₑ/μ, 0.05 % mayor)." if t.masa_reducida else "."))
    with st.container(border=True):
        qc.seccion("Cómo leer la nube: el principio de incertidumbre")
        st.markdown(
            "- **Una medida da un punto; muchas medidas dan una forma.** No se puede predecir dónde caerá la próxima "
            "medida; solo la distribución de muchas, que es |ψ|². Al reproducir la animación, las primeras medidas "
            "parecen dispersas al azar y la forma del orbital aparece al acumularse.\n"
            "- **No hay trayectoria.** El modelo de Bohr asigna al electrón una posición (el círculo blanco) y "
            "una velocidad exactas en cada instante, algo que prohíbe el principio de incertidumbre Δx·Δp ≥ ħ/2. En "
            "la mecánica cuántica el electrón no «está» en ningún punto concreto antes de medirlo.\n"
            f"- **Lo que se conserva de Bohr.** La energía (−13.6 eV/n²) es la misma, y la distancia más probable "
            f"coincide con el radio de Bohr n²a₀ cuando l = n − 1 (orbitales sin nodos radiales: 1s, 2p, 3d…). "
            f"Aquí: {o['r_probable'] * escala:.2f} a₀ frente a {o['r_bohr'] * escala:.2f} a₀.\n"
            "- **Por qué el átomo no colapsa.** Encerrar al electrón cerca del núcleo (Δx pequeño) exige un Δp grande "
            "y por tanto más energía cinética. El equilibrio entre esa energía y la atracción eléctrica fija el "
            "tamaño del átomo (a₀ ≈ 0.053 nm) y la energía del estado fundamental.")
    qc.seccion("Distribución radial y corte del orbital")
    qc.mostrar_pyplot(figura_orbital_2d(n, l, m, real, t.nucleo, t.masa_reducida),
                      archivo=f"bohr_orbital_{n}{LETRAS_L[l]}_m{m}.png")
    st.caption("Izquierda: probabilidad de encontrar el electrón a cada distancia del núcleo; los puntos marcan los "
               "nodos radiales (distancias donde nunca se encuentra). Derecha: densidad |ψ|² en el plano donde el "
               "orbital se ve mejor, con el círculo de Bohr.")


def _subvista_orbitas(t: Transicion):
    n_mostrar = max(t.n_inicial, t.n_final, 3)
    if n_mostrar > N_ORBITAS_3D:
        qc.aviso(f"La animación 3D dibuja órbitas hasta n = {N_ORBITAS_3D} (los radios crecen como n² y las "
                 f"órbitas interiores dejarían de verse). Seleccionar niveles menores o iguales que {N_ORBITAS_3D}.")
        return
    d = calcular_transicion(t)
    qc.metricas([
        ("Radio inicial rᵢ [a₀]", f"{d['ri'] / A0:.3f}", f"{d['ri'] * 1e9:.4f} nm"),
        ("Radio final r_f [a₀]", f"{d['rf'] / A0:.3f}", f"{d['rf'] * 1e9:.4f} nm"),
        ("Velocidad inicial vᵢ / c", f"{d['vi'] / C:.5f}", f"{d['vi']:.4e} m/s"),
        ("Fotón λ [nm]", f"{d['longitud_nm']:.2f}", f"{d['tipo']} · {d['region']}"),
    ])
    altura = 500 if qc.modo_compacto() else 640
    figura = _cache_orbitas(t.n_inicial, t.n_final, t.nucleo, t.masa_reducida, n_mostrar, altura)
    qc.mostrar_plotly(figura, "bohr_orbitas", archivo=f"bohr_orbitas_{t.nucleo}_{t.n_inicial}a{t.n_final}.html")
    st.caption("Radios a escala (rₙ = n²a₀/Z). Las velocidades de giro NO están a escala: en realidad el periodo crece "
               "como n³. El salto se dibuja en varios cuadros para facilitar la visualización, pero en el modelo de Bohr es instantáneo. "
               "El fotón se dibuja con el color de su longitud de onda (gris claro si es invisible: ultravioleta o "
               "infrarrojo). Los niveles se eligen arriba, en «Átomo y transición».")


def _pestana_atomo_3d(t: Transicion):
    st.radio("Modelo", ["nube", "orbitas"], key="bohr_vista3d", horizontal=True,
             format_func=lambda k: "Nube de probabilidad (mecánica cuántica)" if k == "nube"
             else "Órbitas de Bohr (animación del salto)")
    if st.session_state["bohr_vista3d"] == "nube":
        _subvista_nube(t)
    else:
        _subvista_orbitas(t)


# ---------------------------------------------------------------------
# Series y espectro
# ---------------------------------------------------------------------
def _pestana_series(t: Transicion):
    with st.container(border=True):
        qc.seccion("Serie espectral")
        c1, c2, _, _ = st.columns(4)
        nf = c1.number_input(r"Nivel inferior $n_f$", 1, 10, step=1, key="bohr_serie_nf",
                             help="Todas las líneas de una serie comparten el nivel más bajo.")
        nmax = c2.number_input("Nivel superior máximo", 2, N_MAX, step=1, key="bohr_serie_nmax")
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
    qc.seccion("Líneas de la serie")
    qc.mostrar_pyplot(figura_serie(s), archivo=f"bohr_serie_nf{s['n_final']}.png")
    with st.expander("Tabla de líneas", expanded=False):
        letras = "αβγδεζηθ"
        qc.tabla_libre([{"Línea": (f"{s['serie'][:1]}{letras[i]}" if i < len(letras) and t.nucleo == "H" else "—"),
                         "Transición": f"{n} → {s['n_final']}", "λ [nm]": f"{l:.4f}", "Región": qc.region_espectral(l)}
                        for i, (n, l) in enumerate(zip(s["n_inicial"], s["lambda_nm"]))],
                       numericas=("λ [nm]",), archivo=f"bohr_serie_nf{s['n_final']}.csv")
    qc.seccion("Espectro completo del átomo")
    qc.mostrar_pyplot(figura_espectro(t.nucleo, t.masa_reducida), archivo=f"bohr_espectro_{t.nucleo}.png")
    st.caption("Cada fila es una serie (todas las líneas que comparten el nivel más bajo). Solo la serie de Balmer cae, "
               "en parte, dentro de la franja visible. Las series de niveles más altos se solapan en el infrarrojo.")


# ---------------------------------------------------------------------
# Teoría
# ---------------------------------------------------------------------
def interfaz() -> None:
    """Página completa del simulador 5 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 05", "Átomo de hidrógeno · de Bohr a la mecánica cuántica",
                         "Niveles de energía, transiciones y series espectrales del modelo de Bohr, y el átomo "
                         "cuántico en 3D: nubes de probabilidad, orbitales y principio de incertidumbre.")
    qc.enlace_teoria("bohr")
    qc.ficha_simulador(
        "Calcular niveles, transiciones y series espectrales del modelo de Bohr y compararlos con el átomo cuántico 3D.",
        r"\begin{gathered}E_n=-\dfrac{\mu e^4}{8\varepsilon_0^2h^2}\dfrac{Z^2}{n^2}\\[4pt]"
        r"\dfrac{1}{\lambda}=R\,Z^2\left(\dfrac{1}{n_1^2}-\dfrac{1}{n_2^2}\right)\end{gathered}",
        [("n", "número cuántico principal"), ("Z", "carga nuclear"), ("μ", "masa reducida"),
         ("n₁, n₂", "niveles inferior y superior")],
        "El modelo de Bohr es semiclásico y solo describe sistemas hidrogenoides de un electrón; "
        "los orbitales 3D provienen de la ecuación de Schrödinger.")
    t = _leer_parametros()
    if t is None:
        return
    tabs = st.tabs(["Transición", "Átomo en 3D", "Series y espectro", "Guía de práctica", "Autoevaluación",
                    "Predice y experimenta", "Laboratorio inverso", "Instrumentos e informe", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_transicion(t)
    with tabs[1]:
        _pestana_atomo_3d(t)
    with tabs[2]:
        _pestana_series(t)
    with tabs[3]:
        qc.guia_practica(GUIA, "bohr")
    with tabs[4]:
        qc.autoevaluacion(PREGUNTAS, "bohr")
    with tabs[5]:
        _pestana_predice(t)
    with tabs[6]:
        inverso.panel(RETOS_INVERSOS, "bohr")
    with tabs[7]:
        _pestana_instrumentos(t)
    with tabs[8]:
        qc.boton_pruebas(ejecutar_pruebas, "bohr_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Modelo de Bohr", ":material/science:", "modelo_bohr.py")
