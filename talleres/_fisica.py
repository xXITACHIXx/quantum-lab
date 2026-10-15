"""
talleres/_fisica.py — Cálculos de los talleres (puros, con NumPy/SciPy) y sus referencias independientes.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import constants as const
from scipy.optimize import minimize_scalar
from scipy.special import eval_genlaguerre

H = const.h
HBAR = const.hbar
C = const.c
EV = const.e
U = const.atomic_mass
A0 = const.physical_constants["Bohr radius"][0]
RYDBERG_EV = 13.605693122994           # e²/(8πε₀a₀) en eV (CODATA 2018)

# Masas atómicas [u]
MASA = {"H": 1.00782503, "D": 2.01410178, "F": 18.99840316, "Cl": 34.96885268, "Br": 78.9183376,
        "C": 12.0, "O": 15.99491462, "N": 14.0030740}

# molécula: (átomo 1, átomo 2, constante de fuerza k [N/m], longitud de enlace [pm])
DIATOMICAS = {
    "HF": ("H", "F", 966.0, 91.68),
    "HCl": ("H", "Cl", 516.0, 127.46),
    "HBr": ("H", "Br", 412.0, 141.44),
    "CO": ("C", "O", 1857.0, 112.83),
}


def masa_reducida_u(a: str, b: str) -> float:
    """μ = m₁m₂/(m₁ + m₂) en u."""
    return MASA[a] * MASA[b] / (MASA[a] + MASA[b])


def momento_de_inercia(mu_u: float, r_pm: float) -> float:
    """I = μ r²  [kg m²]."""
    return mu_u * U * (r_pm * 1e-12) ** 2


def frecuencia_vibracion(k: float, mu_u: float) -> float:
    """ν = (1/2π)√(k/μ)  [Hz]; todas las transiciones puras n → n+1 del oscilador armónico tienen esta frecuencia."""
    return math.sqrt(k / (mu_u * U)) / (2 * math.pi)


def constante_rotacional_hz(I: float) -> float:
    """B = h/(8π²I)  [Hz]  (E_l = h B l(l+1))."""
    return H / (8 * math.pi ** 2 * I)


def frecuencia_rotacion(l_inicial: int, I: float) -> float:
    """Frecuencia de la transición l → l+1: ν = 2B(l+1)  [Hz]."""
    return 2 * constante_rotacional_hz(I) * (l_inicial + 1)


def longitud_de_enlace_desde_nu(nu_hz: float, mu_u: float, l_inicial: int = 0) -> float:
    """Longitud de enlace [pm] a partir de la frecuencia de la transición l → l+1."""
    I = H * (l_inicial + 1) / (4 * math.pi ** 2 * nu_hz)
    return math.sqrt(I / (mu_u * U)) * 1e12


def energia_hidrogenoide_ev(Z: int, n: int = 1) -> float:
    """Eₙ = −Z² · 13.6057 eV / n²."""
    return -Z ** 2 * RYDBERG_EV / n ** 2


def energia_anillo(m: int, I: float) -> float:
    """Rotor plano (2D): E = m²ħ²/2I  [J]."""
    return m ** 2 * HBAR ** 2 / (2 * I)


# ---------------------------------------------------------------------
# Átomo hidrogenoide (Z = 1, unidades de a₀)
# ---------------------------------------------------------------------
def radial_hidrogeno(n: int, l: int, r):
    """R_nl(r) con r en unidades de a₀ (normalizada: ∫R² r² dr = 1)."""
    r = np.asarray(r, dtype=float)
    rho = 2 * r / n
    norma = math.sqrt((2 / n) ** 3 * math.factorial(n - l - 1) / (2 * n * math.factorial(n + l)))
    return norma * np.exp(-rho / 2) * rho ** l * eval_genlaguerre(n - l - 1, 2 * l + 1, rho)


def distribucion_radial(n: int, l: int, r):
    """P(r) = r² R_nl(r)² (probabilidad por unidad de a₀)."""
    r = np.asarray(r, dtype=float)
    return r ** 2 * radial_hidrogeno(n, l, r) ** 2


def maximos_radiales(n: int, l: int, r_max: float = 80.0, puntos: int = 400001) -> list[float]:
    """Posiciones (a₀) de los máximos locales de P(r), refinadas numéricamente."""
    r = np.linspace(1e-6, r_max, puntos)
    p = distribucion_radial(n, l, r)
    idx = [i for i in range(1, len(r) - 1) if p[i] > p[i - 1] and p[i] >= p[i + 1]]
    salida = []
    for i in idx:
        res = minimize_scalar(lambda x: -float(distribucion_radial(n, l, x)), bracket=(r[i - 1], r[i], r[i + 1]))
        salida.append(float(res.x))
    return salida


def nodos_radiales_numericos(n: int, l: int, r_max: float = 80.0, puntos: int = 400001) -> list[float]:
    """Ceros de R_nl(r) para r > 0 (a₀), por cambio de signo."""
    r = np.linspace(1e-6, r_max, puntos)
    R = radial_hidrogeno(n, l, r)
    cambios = np.where(np.sign(R[:-1]) * np.sign(R[1:]) < 0)[0]
    return [float(0.5 * (r[i] + r[i + 1])) for i in cambios]


# ---------------------------------------------------------------------
# Parte angular (m = 0)
# ---------------------------------------------------------------------
def densidad_angular_m0(l: int, theta):
    """|Y_l^0(θ)|² (por estereorradián)."""
    from scipy.special import eval_legendre
    theta = np.asarray(theta, dtype=float)
    return (2 * l + 1) / (4 * math.pi) * eval_legendre(l, np.cos(theta)) ** 2


def angulos_nodales_m0(l: int) -> list[float]:
    """Ángulos θ (grados) donde Y_l^0 se anula: raíces de P_l(cosθ)."""
    raices = np.polynomial.legendre.Legendre.basis(l).roots()
    return sorted(math.degrees(math.acos(float(np.real(x)))) for x in raices)


# ---------------------------------------------------------------------
# Dos orbitales atómicos (método LCAO con solapamiento)
# ---------------------------------------------------------------------
def energias_lcao_homonuclear(H11: float, S: float, K: float = 1.75) -> dict:
    """
    H11 = H22 (eV, negativo), solapamiento S y H12 = −K·S·√(H11·H22) = K·S·H11 (eV).
    Ecuación secular |H11 − E, H12 − ES; H12 − ES, H22 − E| = 0  →  E± = (H11 ± H12)/(1 ± S).
    Coeficientes: enlazante c₁ = c₂ = 1/√(2(1+S)); antienlazante c₁ = −c₂ = 1/√(2(1−S)).
    """
    H12 = -K * S * math.sqrt(H11 * H11)
    return {"H12": H12,
            "E_enlazante": (H11 + H12) / (1 + S),
            "E_antienlazante": (H11 - H12) / (1 - S),
            "c_enlazante": 1 / math.sqrt(2 * (1 + S)),
            "c_antienlazante": 1 / math.sqrt(2 * (1 - S))}


def energias_lcao_numericas(H11: float, S: float, K: float = 1.75) -> np.ndarray:
    """Referencia independiente: problema de autovalores generalizado H c = E S c (SciPy)."""
    from scipy.linalg import eigh
    H12 = -K * S * abs(H11)
    return eigh(np.array([[H11, H12], [H12, H11]]), np.array([[1.0, S], [S, 1.0]]), eigvals_only=True)


# ---------------------------------------------------------------------
# Hückel del sistema alílico (3 carbonos)
# ---------------------------------------------------------------------
def huckel_alilo():
    """
    Energías (E = α + xβ) y coeficientes del alilo. Devuelve (x, C) con x ordenado de enlazante a antienlazante y C[:, k]
    el orbital k. La matriz de Hückel es la de adyacencia de la cadena de 3 átomos (con β < 0, E = α + xβ).
    """
    A = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
    x, C = np.linalg.eigh(A)               # x ascendente: −√2, 0, +√2
    orden = np.argsort(-x)                 # el mayor x es el más enlazante (β < 0)
    x, C = x[orden], C[:, orden]
    C = C * np.sign(C[0, :] + 1e-12)       # signo: coeficiente del primer átomo positivo
    return x, C
