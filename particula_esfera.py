"""
particula_esfera.py — QUANTUM LAB · Simulador 3: armónicos esféricos y partícula en una esfera
================================================================================================

PARTE ANGULAR (válida para cualquier potencial central V(r)):

    Y_l^m(θ, φ) = (−1)^m √[ (2l+1)/(4π) · (l−m)!/(l+m)! ] · P_l^m(cos θ) · e^{i m φ}     (m ≥ 0, con la
                                                                                      fase de Condon–Shortley)
    Y_l^{−m}    = (−1)^m · conj(Y_l^m)

    L² Y_l^m = ħ² l(l+1) Y_l^m        L_z Y_l^m = ħ m Y_l^m        l = 0, 1, 2, …      m = −l, …, +l

CONVENCIÓN DE ÁNGULOS (la usada en física y en SciPy ≥ 1.15):

    θ ∈ [0, π]  ángulo POLAR (medido desde el eje +z)
    φ ∈ [0, 2π) ángulo AZIMUTAL (medido en el plano xy desde el eje +x)
    x = r sin θ cos φ ,  y = r sin θ sin φ ,  z = r cos θ

    ⚠ La antigua `scipy.special.sph_harm(m, n, theta, phi)` usaba theta = AZIMUTAL y phi = POLAR (¡al revés!).
      Este archivo no se fía de la versión instalada: al importarse CALIBRA la función de SciPy contra las
      fórmulas cerradas de Y_0^0 … Y_2^m (incluida la fase de Condon–Shortley) y, si ninguna variante de SciPy
      pasa la calibración, usa una implementación propia basada en `scipy.special.lpmv`.

MODELO OPCIONAL: PARTÍCULA CONFINADA EN UNA ESFERA IMPENETRABLE (pozo esférico infinito de radio R)

    ψ_{nlm}(r, θ, φ) = R_{nl}(r) · Y_l^m(θ, φ)
    R_{nl}(r) = √(2/R³) · j_l(α_{nl} r / R) / |j_{l+1}(α_{nl})|        α_{nl} = n-ésimo cero de j_l
    E_{nl}    = ħ² α_{nl}² / (2 m R²)                                   (degeneración 2l+1)

IMPORTANTE: |Y_l^m|² es una densidad ANGULAR (por estereorradián) sobre una esfera de radio fijo. La densidad
de probabilidad VOLUMÉTRICA del modelo confinado es |R_{nl}|²|Y_l^m|² (por unidad de volumen). No son lo mismo.

Estructura: 1. Física pura · 2. Figuras · 3. Pruebas numéricas · 4. Interfaz Streamlit
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, replace

import numpy as np
import streamlit as st
from scipy import special
from scipy.optimize import brentq

import informes
import instrumentos
import predice
import quantum_lab_comun as qc
from quantum_lab_comun import COLORES, HBAR, M_E

# =====================================================================
# 1. FÍSICA
# =====================================================================
L_MAX = 20                  # l máximo del visor angular
L_CONF_MAX = 8              # l máximo del modelo confinado
N_CONF_MAX = 6              # n radial máximo del modelo confinado
NTHETA_MIN, NTHETA_MAX = 20, 400
ALFA_MAX = 0.9              # deformación suave máxima (para que r > 0)
LETRAS = "spdfghiklmnoqrtuvw"   # notación espectroscópica: l = 0 → s, 1 → p, 2 → d, 3 → f, 4 → g, …


def letra(l: int) -> str:
    """Letra espectroscópica de l (para l mayor que las letras disponibles, se muestra «l=…»)."""
    return LETRAS[l] if 0 <= l < len(LETRAS) else f"[l={l}]"

MODOS = {
    "densidad": "Densidad angular",
    "prob": "Densidad de probabilidad",
    "re": "Parte real Re Y",
    "im": "Parte imaginaria Im Y",
    "fase": "Fase arg Y",
    "real_cos": "Combinación real ∝ cos(|m|φ)",
    "real_sin": "Combinación real ∝ sin(|m|φ)",
}
UNIDAD_MODO = {"densidad": "sr⁻¹", "prob": "R⁻²", "re": "sr^(−1/2)", "im": "sr^(−1/2)", "fase": "rad",
               "real_cos": "sr^(−1/2)", "real_sin": "sr^(−1/2)"}
FORMAS = {
    "esfera": "Esfera intacta (color)",
    "suave": "Deformación suave",
    "lobulos": "Lóbulos (r ∝ |valor|)",
}
MAPAS_COLOR = ["Viridis", "Plasma", "Turbo", "Inferno", "Cividis", "RdBu", "Twilight", "IceFire"]


# ---------------------------------------------------------------------
# 1.1 Armónicos esféricos: backends y calibración
# ---------------------------------------------------------------------
def _armonico_lpmv(l, m, theta, phi):
    """
    Implementación propia e INDEPENDIENTE de SciPy.sph_harm: usa `lpmv`, que ya
    incluye la fase de Condon–Shortley (−1)^m. θ = polar, φ = azimutal.
    """
    ma = abs(int(m))
    norma = np.sqrt((2 * l + 1) / (4 * np.pi) * np.exp(special.gammaln(l - ma + 1) - special.gammaln(l + ma + 1)))
    y = norma * special.lpmv(ma, l, np.cos(theta)) * np.exp(1j * ma * np.asarray(phi))
    return y if m >= 0 else (-1) ** ma * np.conj(y)


def formas_cerradas(l, m, theta, phi):
    """Y_l^m exactas para l ≤ 2 (con Condon–Shortley). Se usan para calibrar y para las pruebas."""
    s, c = np.sin(theta), np.cos(theta)
    e = np.exp(1j * m * phi)
    tabla = {
        (0, 0): np.sqrt(1 / (4 * np.pi)) + 0 * theta,
        (1, 0): np.sqrt(3 / (4 * np.pi)) * c,
        (1, 1): -np.sqrt(3 / (8 * np.pi)) * s,
        (1, -1): np.sqrt(3 / (8 * np.pi)) * s,
        (2, 0): np.sqrt(5 / (16 * np.pi)) * (3 * c ** 2 - 1),
        (2, 1): -np.sqrt(15 / (8 * np.pi)) * s * c,
        (2, -1): np.sqrt(15 / (8 * np.pi)) * s * c,
        (2, 2): 0.25 * np.sqrt(15 / (2 * np.pi)) * s ** 2,
        (2, -2): 0.25 * np.sqrt(15 / (2 * np.pi)) * s ** 2,
    }
    return tabla[(l, m)] * (e if m != 0 else 1.0)


def _pasa_calibracion(funcion) -> bool:
    """¿Reproduce `funcion(l, m, θ, φ)` las formas cerradas, con θ polar y φ azimutal?"""
    th = np.array([0.31, 0.9, 1.7, 2.6])
    ph = np.array([0.4, 1.9, 3.3, 5.6])               # asimétricos: detectan intercambio θ↔φ y signos
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for (l, m) in [(0, 0), (1, 0), (1, 1), (1, -1), (2, 0), (2, 1), (2, -1), (2, 2), (2, -2)]:
                y = np.asarray(funcion(l, m, th, ph), dtype=complex)
                if y.shape != th.shape or not np.allclose(y, formas_cerradas(l, m, th, ph), atol=1e-10):
                    return False
    except Exception:
        return False
    return True


def construir_backend(modulo=special):
    """
    Elige y calibra la función de armónicos esféricos. Devuelve (nombre, función(l, m, θ, φ)).
    Orden de preferencia: sph_harm_y (SciPy ≥ 1.15) → sph_harm (legada, ángulos invertidos) → lpmv propia.
    """
    candidatos = []
    if hasattr(modulo, "sph_harm_y"):
        candidatos.append(("scipy.special.sph_harm_y", lambda l, m, th, ph: modulo.sph_harm_y(l, m, th, ph)))
    if hasattr(modulo, "sph_harm"):
        # firma legada: sph_harm(m, n, theta=AZIMUTAL, phi=POLAR)
        candidatos.append(("scipy.special.sph_harm (legada)", lambda l, m, th, ph: modulo.sph_harm(m, l, ph, th)))
    candidatos.append(("implementación propia (lpmv)", _armonico_lpmv))
    for nombre, funcion in candidatos:
        if _pasa_calibracion(funcion):
            return nombre, funcion
    return "implementación propia (lpmv)", _armonico_lpmv      # (inalcanzable: lpmv pasa la calibración)


NOMBRE_BACKEND, _Y = construir_backend()


def _trapecio(y, x=None, axis=-1):
    """Regla del trapecio compatible con NumPy 1.x (`trapz`) y 2.x (`trapezoid`)."""
    funcion = getattr(np, "trapezoid", None) or np.trapz
    return funcion(y, x, axis=axis) if x is not None else funcion(y, axis=axis)


def armonico_esferico(l: int, m: int, theta, phi):
    """Y_l^m(θ, φ) con θ polar y φ azimutal (siempre, sea cual sea la versión de SciPy)."""
    return np.asarray(_Y(l, m, np.asarray(theta, dtype=float), np.asarray(phi, dtype=float)), dtype=complex)


def evaluar_campo(l: int, m: int, modo: str, theta, phi, radio: float = 1.0):
    """
    Campo escalar real a dibujar para el modo elegido.

    real_cos / real_sin: combinaciones reales de Y_l^{±|m|} (las «orbitales reales» de la química):
        R_c = (Y^{−|m|} + (−1)^m Y^{|m|})/√2 = √2 (−1)^m Re Y^{|m|}
        R_s = i (Y^{−|m|} − (−1)^m Y^{|m|})/√2 = √2 (−1)^m Im Y^{|m|}
    Para m = 0 solo existe R_c = Y_l^0 (ya es real).
    """
    if modo not in MODOS:
        raise ValueError(f"Modo desconocido: {modo!r}.")
    if modo in ("real_cos", "real_sin"):
        ma = abs(m)
        if ma == 0:
            if modo == "real_sin":
                raise ValueError("Para m = 0 no existe la combinación ∝ sin(|m|φ) (sería idénticamente nula): "
                                 "Y_l^0 ya es real y coincide con la combinación ∝ cos.")
            return armonico_esferico(l, 0, theta, phi).real
        y = armonico_esferico(l, ma, theta, phi)
        c = np.sqrt(2.0) * (-1) ** ma
        return c * (y.real if modo == "real_cos" else y.imag)
    y = armonico_esferico(l, m, theta, phi)
    if modo == "densidad":
        return np.abs(y) ** 2
    if modo == "prob":                                  # probabilidad por unidad de área sobre la esfera de radio R
        return np.abs(y) ** 2 / radio ** 2
    if modo == "re":
        return y.real
    if modo == "im":
        return y.imag
    return np.angle(y)                                  # fase


# ---------------------------------------------------------------------
# 1.2 Validación
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class ParametrosEsfera:
    l: int
    m: int
    radio: float            # m (SI); solo es una ESCALA GEOMÉTRICA para la parte angular
    sistema: str
    n_theta: int            # puntos en θ (en φ se usan 2×)
    modo: str
    forma: str
    alfa: float
    mapa: str

    @property
    def n_phi(self) -> int:
        return 2 * self.n_theta


def l_permitidos(l_max: int = L_MAX):
    return list(range(0, l_max + 1))


def m_permitidos(l: int):
    return list(range(-l, l + 1))


def ajustar_m(l: int, m: int) -> int:
    """Restringe m al intervalo permitido [−l, l] (usado por la interfaz al cambiar l)."""
    return int(max(-l, min(l, m)))


def validar_numeros_cuanticos(l, m) -> tuple[int, int]:
    l = qc.entero_en_rango(l, "El número cuántico l", 0, L_MAX)
    m = qc.entero_en_rango(m, "El número cuántico magnético m", -L_MAX, L_MAX)
    if abs(m) > l:
        raise ValueError(f"Para l = {l} el número m debe cumplir −{l} ≤ m ≤ {l} (recibido: m = {m}).")
    return l, m


def validar_parametros_esfera(l, m, radio, sistema, n_theta, modo, forma="esfera", alfa=0.3,
                              mapa="Viridis") -> ParametrosEsfera:
    l, m = validar_numeros_cuanticos(l, m)
    u = qc.obtener_unidades(sistema)
    radio_m = qc.positivo_finito(radio, f"El radio [{u['nombre_longitud']}]") * u["factor_longitud"]
    n_theta = qc.entero_en_rango(n_theta, "La resolución angular (puntos en θ)", NTHETA_MIN, NTHETA_MAX)
    minimo = 4 * l + 8
    if n_theta < minimo:
        raise ValueError(f"Resolución insuficiente: para l = {l} hacen falta al menos {minimo} puntos en θ "
                         f"(recibido: {n_theta}); si no, los lóbulos se dibujarían mal.")
    if modo not in MODOS:
        raise ValueError(f"Modo de visualización desconocido: {modo!r}.")
    if forma not in FORMAS:
        raise ValueError(f"Forma de la superficie desconocida: {forma!r}.")
    if modo == "real_sin" and m == 0:
        raise ValueError("Para m = 0 no existe la combinación real ∝ sin(|m|φ): elige otro modo.")
    try:
        alfa = float(alfa)
    except (TypeError, ValueError):
        raise ValueError(f"La amplitud de deformación α debe ser un número (recibido: {alfa!r}).")
    if not (0.0 <= alfa <= ALFA_MAX):
        raise ValueError(f"La amplitud de deformación α debe estar entre 0 y {ALFA_MAX} (recibido: {alfa}).")
    if mapa not in MAPAS_COLOR:
        raise ValueError(f"Mapa de color desconocido: {mapa!r}.")
    return ParametrosEsfera(l, m, radio_m, sistema, n_theta, modo, forma, alfa, mapa)


# ---------------------------------------------------------------------
# 1.3 Geometría y nodos
# ---------------------------------------------------------------------
def esfericas_a_cartesianas(r, theta, phi):
    """(r, θ, φ) → (x, y, z) con θ polar y φ azimutal."""
    return (r * np.sin(theta) * np.cos(phi), r * np.sin(theta) * np.sin(phi), r * np.cos(theta))


def cartesianas_a_esfericas(x, y, z):
    """(x, y, z) → (r, θ, φ) con θ ∈ [0, π] y φ ∈ [0, 2π)."""
    x, y, z = (np.asarray(v, dtype=float) for v in (x, y, z))
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    theta = np.arccos(np.divide(z, r, out=np.ones_like(r), where=r > 0))
    phi = np.mod(np.arctan2(y, x), 2 * np.pi)
    return r, theta, phi


def malla_angular(n_theta: int, n_phi: int | None = None):
    """Malla (θ, φ) que incluye ambos extremos (la costura φ = 0 ≡ 2π queda cerrada)."""
    n_phi = 2 * n_theta if n_phi is None else n_phi
    theta = np.linspace(0.0, np.pi, n_theta)
    phi = np.linspace(0.0, 2 * np.pi, n_phi)
    return np.meshgrid(theta, phi, indexing="ij")       # forma (n_theta, n_phi)


# ---------------------------------------------------------------------
# 1.3b Densidad de probabilidad |Y_l^m|² en función de la posición (x, y, z)
# ---------------------------------------------------------------------
PLANOS = {"xz": "Plano xz (y = 0)", "yz": "Plano yz (x = 0)", "xy": "Plano xy (z = 0)"}


def densidad_probabilidad(l: int, m: int, theta, phi, real: bool = False):
    """
    Densidad de probabilidad angular [sr⁻¹]: |Y_l^m(θ, φ)|² (armónico complejo, L_z = mħ definido) o, con
    `real=True`, el cuadrado de la combinación real (m > 0 → ∝ cos|m|φ, m < 0 → ∝ sin|m|φ; orbitales pₓ, d_xy…).
    La probabilidad de hallar la partícula en el ángulo sólido dΩ = sinθ dθ dφ es |Y|² dΩ.
    """
    if real and m != 0:
        return evaluar_campo(l, m, "real_cos" if m > 0 else "real_sin", theta, phi) ** 2
    return np.abs(armonico_esferico(l, m, theta, phi)) ** 2


def densidad_en_punto(l: int, m: int, x: float, y: float, z: float, radio: float, real: bool = False) -> dict:
    """
    Evalúa la densidad en la dirección del punto (x, y, z). La partícula está sobre la esfera de radio R, así que
    el punto se proyecta radialmente sobre ella. Devuelve θ, φ, |Y|² [sr⁻¹], |Y|²/R² [1/longitud²] (probabilidad
    por unidad de ÁREA de la esfera) y el punto proyectado.
    """
    valores = [float(v) for v in (x, y, z)]
    if not all(np.isfinite(valores)):
        raise ValueError("Las coordenadas x, y, z deben ser números finitos.")
    r, theta, phi = (float(v) for v in cartesianas_a_esfericas(*valores))
    if r == 0:
        raise ValueError("El origen (0, 0, 0) no define ninguna dirección: escriba un punto distinto del origen.")
    if not (np.isfinite(radio) and radio > 0):
        raise ValueError("El radio R debe ser positivo.")
    d = float(densidad_probabilidad(l, m, theta, phi, real))
    escala = float(np.max(densidad_probabilidad(l, m, *malla_angular(61), real)))
    if abs(d) < 1e-12 * escala:                    # ruido de redondeo (≈1e−33) sobre una superficie nodal
        d = 0.0
    return {"r": r, "theta": theta, "phi": phi, "densidad_sr": d, "densidad_area": d / radio ** 2,
            "punto_esfera": tuple(radio * v / r for v in valores)}


def curva_densidad_plano(l: int, m: int, plano: str, real: bool = False, n: int = 1441):
    """
    Corte polar de la densidad en un plano coordenado: puntos (h, v) a distancia |Y|² del origen en cada dirección
    del plano. «xz»: (x, z) con φ = 0 y π; «yz»: (y, z) con φ = π/2 y 3π/2; «xy»: (x, y) con θ = π/2.
    Devuelve (h, v, densidad, ángulo en el plano).
    """
    if plano not in PLANOS:
        raise ValueError(f"Plano desconocido: {plano!r}.")
    t = np.linspace(0.0, 2 * np.pi, n)
    if plano == "xy":
        theta, phi = np.full_like(t, np.pi / 2), t
        dens = densidad_probabilidad(l, m, theta, phi, real)
        return dens * np.cos(t), dens * np.sin(t), dens, t
    phi0 = 0.0 if plano == "xz" else np.pi / 2
    theta = np.where(t <= np.pi, t, 2 * np.pi - t)
    phi = np.where(t <= np.pi, phi0, phi0 + np.pi)
    dens = densidad_probabilidad(l, m, theta, phi, real)
    x, y, z = esfericas_a_cartesianas(dens, theta, phi)
    return (x if plano == "xz" else y), z, dens, t


def meridiano_maximo(m: int, real: bool) -> float:
    """Azimut φ donde la combinación real alcanza su máximo (|cos|m|φ| o |sin|m|φ| = 1); 0 para el armónico complejo."""
    if real and m < 0:
        return float(np.pi / (2 * abs(m)))
    return 0.0


def densidad_frente_a_z(l: int, m: int, real: bool = False, phi: float = 0.0, n: int = 801):
    """|Y|² sobre la esfera en función de la altura z/R = cosθ, a lo largo del meridiano φ."""
    z = np.linspace(-1.0, 1.0, n)
    return z, densidad_probabilidad(l, m, np.arccos(z), np.full_like(z, phi), real)


def nodos_latitud(l: int, m: int) -> np.ndarray:
    """
    Ángulos polares θ (rad, crecientes) de los nodos latitudinales de Y_l^m: ceros de P_l^{|m|}(cos θ) en
    (−1, 1). Son exactamente l − |m|. (Además, si m ≠ 0, |Y| se anula en los polos θ = 0, π.)
    """
    ma = abs(m)
    if ma > l:
        raise ValueError("|m| no puede superar a l.")
    if l == ma:
        return np.array([])
    poli = np.polynomial.legendre.Legendre.basis(l).deriv(ma)                # P_l^m ∝ (1−x²)^{m/2} P_l^{(m)}(x)
    raices = poli.roots()
    x = np.sort(np.real(raices[np.abs(np.imag(raices)) < 1e-9]))
    dpoli = poli.deriv()
    for _ in range(4):                                                       # refinado de Newton (las raíces de la matriz
        x = x - poli(x) / dpoli(x)                                           # compañera pierden algo de precisión)
    return np.sort(np.arccos(x))


def nodos_meridianos(m: int, tipo: str) -> np.ndarray:
    """
    Ángulos azimutales φ ∈ [0, 2π) de los semiplanos nodales de una combinación REAL:
    cos(|m|φ) = 0 → φ = (2k+1)π/(2|m|);  sin(|m|φ) = 0 → φ = kπ/|m|.  (2|m| semiplanos = |m| planos.)
    Para el armónico COMPLEJO |Y|² no depende de φ: no tiene meridianos nodales.
    """
    ma = abs(m)
    if ma == 0:
        return np.array([])
    k = np.arange(2 * ma)
    return (2 * k + 1) * np.pi / (2 * ma) if tipo == "real_cos" else k * np.pi / ma


def numero_total_superficies_nodales(l: int, m: int) -> int:
    """Combinación real: (l − |m|) conos + |m| planos = l superficies nodales."""
    return len(nodos_latitud(l, m)) + abs(m)


# ---------------------------------------------------------------------
# 1.4 Normalización angular
# ---------------------------------------------------------------------
def integral_solapamiento(l1: int, m1: int, l2: int, m2: int, n_gl: int = 64) -> complex:
    """
    ⟨Y_{l1}^{m1}|Y_{l2}^{m2}⟩ = ∬ conj(Y1) Y2 sin θ dθ dφ, con cuadratura de Gauss–Legendre en cos θ
    (exacta para polinomios) y regla uniforme (exacta para funciones periódicas) en φ.
    """
    x, w = np.polynomial.legendre.leggauss(n_gl)
    theta = np.arccos(x)
    n_phi = 2 * n_gl
    phi = np.arange(n_phi) * 2 * np.pi / n_phi
    T, P = np.meshgrid(theta, phi, indexing="ij")
    integrando = np.conj(armonico_esferico(l1, m1, T, P)) * armonico_esferico(l2, m2, T, P)
    return complex(np.sum(w[:, None] * integrando) * (2 * np.pi / n_phi))


def integral_angular_malla(valores, theta, phi) -> float:
    """∬ f sin θ dθ dφ sobre la MALLA DE VISUALIZACIÓN (trapecio). `theta`, `phi` son los ejes 1D."""
    return float(_trapecio(_trapecio(valores * np.sin(theta)[:, None], phi, axis=1), theta))


def normalizacion_malla(l: int, m: int, n_theta: int):
    """∫|Y_l^m|² dΩ en la malla del gráfico y su desviación respecto de 1."""
    T, P = malla_angular(n_theta)
    valor = integral_angular_malla(np.abs(armonico_esferico(l, m, T, P)) ** 2, T[:, 0], P[0, :])
    return valor, abs(valor - 1.0)


# ---------------------------------------------------------------------
# 1.5 Superficie 3D
# ---------------------------------------------------------------------
def geometria_superficie(campo, forma: str, radio: float, alfa: float, modo: str):
    """
    Radio de cada punto de la superficie:
      esfera  → r = R (la esfera queda intacta; el valor solo se ve en el color)
      suave   → r = R (1 + α f/max|f|)         (deformación ARTIFICIAL para ver el patrón; no es física)
      lobulos → r = R |f|/max|f|               (la distancia al origen codifica |f|; no es una superficie física)
    En el modo «fase» no se permite deformar: el ángulo de fase no es una magnitud con tamaño.
    """
    if modo == "fase" and forma != "esfera":
        forma = "esfera"
    mx = np.max(np.abs(campo))
    f = campo / mx if mx > 0 else np.zeros_like(campo)
    if forma == "esfera":
        return np.full_like(campo, radio, dtype=float), "esfera"
    if forma == "suave":
        return radio * (1.0 + alfa * f), "suave"
    return radio * np.abs(f), "lobulos"


# ---------------------------------------------------------------------
# 1.6 Partícula confinada en una esfera
# ---------------------------------------------------------------------
def ceros_bessel_esferica(l: int, k_max: int) -> np.ndarray:
    """Primeros `k_max` ceros positivos de la función de Bessel esférica j_l (barrido + brentq)."""
    if l < 0 or k_max < 1:
        raise ValueError("Se necesita l ≥ 0 y k_max ≥ 1.")
    if l == 0:
        return np.pi * np.arange(1, k_max + 1)          # j_0 = sin x / x → ceros nπ (exactos)
    x_max = (k_max + l / 2.0 + 3.0) * np.pi
    xs = np.arange(1e-3, x_max, 0.02)
    ys = special.spherical_jn(l, xs)
    cambios = np.where(np.sign(ys[:-1]) * np.sign(ys[1:]) < 0)[0]
    ceros = [brentq(lambda x: special.spherical_jn(l, x), xs[i], xs[i + 1], xtol=1e-14) for i in cambios]
    if len(ceros) < k_max:
        raise RuntimeError("No se encontraron suficientes ceros de j_l.")
    return np.array(ceros[:k_max])


def energia_confinada(n: int, l: int, radio: float, masa: float) -> float:
    """E_{nl} = ħ² α_{nl}² / (2 m R²)  [J]."""
    alfa = ceros_bessel_esferica(l, n)[n - 1]
    return HBAR ** 2 * alfa ** 2 / (2.0 * masa * radio ** 2)


def radial_confinada(r, n: int, l: int, radio: float):
    """R_{nl}(r) = √(2/R³) j_l(α r/R)/|j_{l+1}(α)|   [m^(−3/2)]."""
    alfa = ceros_bessel_esferica(l, n)[n - 1]
    return np.sqrt(2.0 / radio ** 3) * special.spherical_jn(l, alfa * np.asarray(r) / radio) \
        / abs(special.spherical_jn(l + 1, alfa))


@dataclass(frozen=True)
class ParametrosConfinada:
    n: int
    l: int
    m: int
    radio: float            # m
    masa: float             # kg
    sistema: str


def validar_parametros_confinada(n, l, m, radio, masa, sistema) -> ParametrosConfinada:
    u = qc.obtener_unidades(sistema)
    n = qc.entero_en_rango(n, "El número cuántico radial n", 1, N_CONF_MAX)
    l = qc.entero_en_rango(l, "El número cuántico l (modelo confinado)", 0, L_CONF_MAX)
    m = qc.entero_en_rango(m, "El número cuántico magnético m", -L_CONF_MAX, L_CONF_MAX)
    if abs(m) > l:
        raise ValueError(f"Para l = {l} el número m debe cumplir −{l} ≤ m ≤ {l} (recibido: m = {m}).")
    radio_m = qc.positivo_finito(radio, f"El radio de la esfera [{u['nombre_longitud']}]") * u["factor_longitud"]
    masa_kg = qc.positivo_finito(masa, "La masa [mₑ]") * M_E
    return ParametrosConfinada(n, l, m, radio_m, masa_kg, sistema)


def calcular_confinada(p: ParametrosConfinada, n_r: int = 4001) -> dict:
    """Todo lo necesario del estado |n l m⟩ en la esfera: energía, R_nl, P(r), nodos radiales, normalización."""
    ceros = ceros_bessel_esferica(p.l, p.n)
    alfa = ceros[p.n - 1]
    r = np.linspace(0.0, p.radio, n_r)
    R = radial_confinada(r, p.n, p.l, p.radio)
    P = r ** 2 * R ** 2                                   # densidad de probabilidad radial [1/m]
    return {
        "alfa": alfa, "ceros": ceros, "r": r, "R": R, "P": P,
        "energia": HBAR ** 2 * alfa ** 2 / (2.0 * p.masa * p.radio ** 2),
        "norma_radial": float(_trapecio(P, r)),
        "r_medio": float(_trapecio(r * P, r)),
        "nodos_radiales": p.radio * ceros[:p.n - 1] / alfa,        # ceros interiores de R_nl
        "degeneracion": 2 * p.l + 1,
    }


def niveles_confinados(n_max: int = 3, l_max: int = 4):
    """Lista ordenada [(α, n, l)] de los primeros niveles (E ∝ α²)."""
    filas = [(ceros_bessel_esferica(l, n_max)[n - 1], n, l) for l in range(l_max + 1) for n in range(1, n_max + 1)]
    return sorted(filas)


def nombre_orbital(n: int, l: int) -> str:
    return f"{n}{letra(l)}"


def rebanada_densidad(p: ParametrosConfinada, n_pix: int = 241):
    """
    Corte y = 0 (plano xz) de la densidad VOLUMÉTRICA |ψ|² = R_nl² |Y_l^m|², en unidades de 1/R³.
    Fuera de la esfera (r > R) devuelve NaN. Devuelve (x/R, z/R, ρR³).
    """
    ejes = np.linspace(-1.0, 1.0, n_pix)
    X, Z = np.meshgrid(ejes, ejes, indexing="xy")
    r, theta, phi = cartesianas_a_esfericas(X * p.radio, 0.0 * X, Z * p.radio)
    dens = radial_confinada(r, p.n, p.l, p.radio) ** 2 * np.abs(armonico_esferico(p.l, p.m, theta, phi)) ** 2
    dens = np.where(r <= p.radio, dens * p.radio ** 3, np.nan)
    return ejes, ejes, dens


# =====================================================================
# 2. FIGURAS
# =====================================================================
def _plotly():
    import plotly.graph_objects as go
    return go


def _unidad_modo(modo, unidad_long=None):
    """Unidad del campo; la densidad por área depende de la unidad de longitud elegida."""
    if modo == "prob" and unidad_long:
        return f"{unidad_long}⁻²"
    return UNIDAD_MODO[modo]


def _rango_color(campo, modo):
    if modo in ("densidad", "prob"):
        return 0.0, float(np.max(campo)) or 1.0
    if modo == "fase":
        return -np.pi, np.pi
    mx = float(np.max(np.abs(campo))) or 1.0
    return -mx, mx


def _superficie(go, p_l, p_m, modo, forma, radio, alfa, mapa, n_theta, escala_long, colorbar=True,
                cmin=None, cmax=None, scene=None, unidad_long=None):
    """Una traza `go.Surface` y el radio máximo (para fijar los ejes)."""
    T, P = malla_angular(n_theta)
    campo = evaluar_campo(p_l, p_m, modo, T, P, radio / escala_long)
    if modo == "fase":                                     # la fase no está definida donde |Y| = 0
        campo = np.where(np.abs(armonico_esferico(p_l, p_m, T, P)) < 1e-6, np.nan, campo)
        campo_geo = np.zeros_like(campo)
    else:
        campo_geo = campo
    r, forma_efectiva = geometria_superficie(np.nan_to_num(campo_geo), forma, radio, alfa, modo)
    X, Y, Z = (v / escala_long for v in esfericas_a_cartesianas(r, T, P))
    lo, hi = _rango_color(np.nan_to_num(campo), modo)
    cmin = lo if cmin is None else cmin
    cmax = hi if cmax is None else cmax
    traza = go.Surface(
        x=X, y=Y, z=Z, surfacecolor=campo, colorscale=mapa, cmin=cmin, cmax=cmax, showscale=colorbar,
        colorbar=dict(title=dict(text=f"{MODOS[modo]}<br>[{_unidad_modo(modo, unidad_long)}]", side="right"), thickness=14, len=0.8),
        lighting=dict(ambient=0.6, diffuse=0.7, specular=0.25, roughness=0.6),
        hovertemplate="x=%{x:.3f}<br>y=%{y:.3f}<br>z=%{z:.3f}<br>valor=%{surfacecolor:.4g}<extra></extra>",
        **({"scene": scene} if scene else {}))
    return traza, float(np.max(r)) / escala_long, forma_efectiva


def _estilo_escena(limite, unidad, titulo_ejes=True):
    eje = dict(range=[-limite, limite], backgroundcolor=COLORES["panel"], gridcolor=COLORES["rejilla"],
               zerolinecolor=COLORES["gris"], showbackground=True, color=COLORES["texto"])
    return dict(xaxis=dict(title=f"x [{unidad}]" if titulo_ejes else "", **eje),
                yaxis=dict(title=f"y [{unidad}]" if titulo_ejes else "", **eje),
                zaxis=dict(title=f"z [{unidad}]" if titulo_ejes else "", **eje),
                aspectmode="cube", camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)))


def figura_superficie_3d(p: ParametrosEsfera):
    """Superficie 3D rotable y ampliable de la magnitud angular elegida sobre la esfera de radio R."""
    go = _plotly()
    u = qc.obtener_unidades(p.sistema)
    traza, rmax, forma_ef = _superficie(go, p.l, p.m, p.modo, p.forma, p.radio, p.alfa, p.mapa, p.n_theta,
                                        u["factor_longitud"], unidad_long=u["nombre_longitud"])
    fig = go.Figure(traza)
    qc.aplicar_tema_plotly(fig, f"{MODOS[p.modo]} · l = {p.l}, m = {p.m} · radio R = "
                                f"{p.radio / u['factor_longitud']:.4g} {u['nombre_longitud']}", altura=640)
    fig.update_layout(scene=_estilo_escena(1.15 * rmax, u["nombre_longitud"]), margin=dict(l=0, r=0, t=50, b=0))
    return fig, forma_ef


def figura_comparacion_orbitales(estados, modo: str, forma: str, mapa: str, n_theta: int = 70):
    """Rejilla de superficies 3D con escala de color COMÚN y forma normalizada por orbital."""
    from plotly.subplots import make_subplots
    go = _plotly()
    n = len(estados)
    cols = min(3, n)
    filas = int(np.ceil(n / cols))
    fig = make_subplots(rows=filas, cols=cols, specs=[[{"type": "scene"}] * cols for _ in range(filas)],
                        subplot_titles=[f"l = {l}, m = {m}  ({nombre_orbital(l + 1, l)[1:]})" for l, m in estados],
                        vertical_spacing=0.06, horizontal_spacing=0.02)
    campos = [evaluar_campo(l, m, modo, *malla_angular(n_theta)) for l, m in estados]
    lo, hi = (min(float(np.min(c)) for c in campos), max(float(np.max(c)) for c in campos))
    if modo not in ("densidad", "prob"):
        lo, hi = -max(abs(lo), abs(hi)), max(abs(lo), abs(hi))
    for i, (l, m) in enumerate(estados):
        nom = "scene" if i == 0 else f"scene{i + 1}"
        traza, _, _ = _superficie(go, l, m, modo, forma, 1.0, 0.4, mapa, n_theta, 1.0, colorbar=(i == 0),
                                  cmin=lo, cmax=hi)
        fig.add_trace(traza, row=i // cols + 1, col=i % cols + 1)
        fig.update_layout({nom: _estilo_escena(1.1, "R", titulo_ejes=False)})
    qc.aplicar_tema_plotly(fig, None, altura=430 * filas)
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig


def figura_complejo_vs_real(l: int, m: int, n_theta: int = 80):
    """|Y_l^m|², |Y_l^{−m}|² (complejos) frente a las dos combinaciones reales cos y sin."""
    from plotly.subplots import make_subplots
    go = _plotly()
    m = abs(m)
    paneles = [(m, "densidad", f"|Y<sub>{l}</sub><sup>{m}</sup>|² (complejo)"),
               (-m, "densidad", f"|Y<sub>{l}</sub><sup>{-m}</sup>|² (complejo)"),
               (m, "real_cos", f"combinación real ∝ cos({m}φ)"),
               (m, "real_sin", f"combinación real ∝ sin({m}φ)")]
    fig = make_subplots(rows=2, cols=2, specs=[[{"type": "scene"}] * 2] * 2, subplot_titles=[t for *_, t in paneles],
                        vertical_spacing=0.07, horizontal_spacing=0.02)
    for i, (mm, modo, _) in enumerate(paneles):
        nom = "scene" if i == 0 else f"scene{i + 1}"
        mapa = "Viridis" if modo == "densidad" else "RdBu"
        traza, _, _ = _superficie(go, l, mm, modo, "lobulos", 1.0, 0.4, mapa, n_theta, 1.0, colorbar=False)
        fig.add_trace(traza, row=i // 2 + 1, col=i % 2 + 1)
        fig.update_layout({nom: _estilo_escena(1.1, "R", titulo_ejes=False)})
    qc.aplicar_tema_plotly(fig, None, altura=820)
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig


def figura_proyeccion_2d(p: ParametrosEsfera, phi_corte: float, theta_corte: float):
    """Mapa (φ, θ) del campo + cortes a φ fijo y a θ fijo, con los nodos marcados."""
    import matplotlib.pyplot as plt
    T, P = malla_angular(max(p.n_theta, 60))
    u = qc.obtener_unidades(p.sistema)
    rr = p.radio / u["factor_longitud"]
    unid = _unidad_modo(p.modo, u["nombre_longitud"])
    campo = evaluar_campo(p.l, p.m, p.modo, T, P, rr)
    if p.modo == "fase":
        campo = np.where(np.abs(armonico_esferico(p.l, p.m, T, P)) < 1e-6, np.nan, campo)
    lo, hi = _rango_color(np.nan_to_num(campo), p.modo)
    cmap = {"Twilight": "twilight", "IceFire": "coolwarm"}.get(p.mapa, p.mapa.lower())
    try:
        plt.get_cmap(cmap)
    except ValueError:
        cmap = "viridis"
    if qc.modo_compacto():
        fig, (ax, ax2, ax3) = plt.subplots(3, 1, figsize=(7.4, 11.5), constrained_layout=True)
    else:
        fig = plt.figure(figsize=(14, 4.6), constrained_layout=True)
        gs = fig.add_gridspec(1, 3, width_ratios=[1.5, 1, 1])
        ax, ax2, ax3 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    im = ax.pcolormesh(np.degrees(P), np.degrees(T), campo, cmap=cmap, vmin=lo, vmax=hi, shading="auto")
    for th in nodos_latitud(p.l, p.m):
        ax.axhline(np.degrees(th), color="white", ls="--", lw=0.9, alpha=0.8)
    if p.modo in ("real_cos", "real_sin"):
        for ph in nodos_meridianos(p.m, p.modo):
            ax.axvline(np.degrees(ph), color="white", ls=":", lw=0.9, alpha=0.8)
    ax.axvline(np.degrees(phi_corte), color=COLORES["energia"], lw=1.2)
    ax.axhline(np.degrees(theta_corte), color=COLORES["densidad"], lw=1.2)
    ax.set_xlabel("φ azimutal [°]")
    ax.set_ylabel("θ polar [°]  (0° = polo norte)")
    ax.set_ylim(180, 0)
    ax.set_xlim(0, 360)
    ax.set_title(f"Proyección equirrectangular · {MODOS[p.modo]}")
    fig.colorbar(im, ax=ax, label=f"[{unid}]")
    th = np.linspace(0, np.pi, 600)
    f_th = evaluar_campo(p.l, p.m, p.modo, th, np.full_like(th, phi_corte), rr)
    ax2.plot(np.degrees(th), f_th, color=COLORES["energia"], lw=2)
    for nodo in nodos_latitud(p.l, p.m):
        ax2.axvline(np.degrees(nodo), color=COLORES["gris"], ls="--", lw=0.8)
    ax2.set_xlabel("θ [°]")
    ax2.set_ylabel(f"[{unid}]")
    ax2.set_title(f"Corte a φ = {np.degrees(phi_corte):.0f}°")
    ax2.grid(True)
    ph = np.linspace(0, 2 * np.pi, 600)
    f_ph = evaluar_campo(p.l, p.m, p.modo, np.full_like(ph, theta_corte), ph, rr)
    ax3.plot(np.degrees(ph), f_ph, color=COLORES["densidad"], lw=2)
    ax3.set_xlabel("φ [°]")
    ax3.set_title(f"Corte a θ = {np.degrees(theta_corte):.0f}°")
    ax3.grid(True)
    return fig


def figura_densidad_3d(l: int, m: int, real: bool, radio: float, sistema: str, n_theta: int = 90):
    """
    Dos vistas 3D en coordenadas cartesianas: (1) la esfera real de radio R con cada punto (x, y, z) coloreado por la
    densidad por unidad de área |Y|²/R²; (2) la superficie polar r = |Y|²(θ, φ), donde la distancia al origen en cada
    dirección es la densidad angular.
    """
    from plotly.subplots import make_subplots
    go = _plotly()
    u = qc.obtener_unidades(sistema)
    R = radio / u["factor_longitud"]
    T, P = malla_angular(n_theta)
    dens = densidad_probabilidad(l, m, T, P, real)
    xs, ys, zs = esfericas_a_cartesianas(R, T, P)
    xp, yp, zp = esfericas_a_cartesianas(dens, T, P)
    unidad_area = f"{u['nombre_longitud']}⁻²"
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "scene"}, {"type": "scene"}]], horizontal_spacing=0.02,
                        subplot_titles=["Densidad de probabilidad  P = |Y|²/R²", "Densidad angular  |Y|²"])
    fig.add_trace(go.Surface(x=xs, y=ys, z=zs, surfacecolor=dens / R ** 2, colorscale="Viridis", cmin=0,
                             colorbar=dict(title=dict(text=f"Densidad de probabilidad<br>[{unidad_area}]", side="right"), x=0.40, len=0.75, thickness=12),
                             hovertemplate=f"x=%{{x:.3f}} {u['nombre_longitud']}<br>y=%{{y:.3f}}<br>z=%{{z:.3f}}<br>"
                                           f"Densidad de probabilidad=%{{surfacecolor:.4g}} {unidad_area}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Surface(x=xp, y=yp, z=zp, surfacecolor=dens, colorscale="Viridis", cmin=0,
                             colorbar=dict(title=dict(text="Densidad angular<br>[sr⁻¹]", side="right"), x=1.0, len=0.75, thickness=12),
                             hovertemplate="x=%{x:.4f}<br>y=%{y:.4f}<br>z=%{z:.4f}<br>Densidad angular=%{surfacecolor:.4g} sr⁻¹<extra></extra>"),
                  row=1, col=2)
    lim = 1.15 * float(np.max(dens)) or 1.0
    tipo = " · orbital real" if (real and m != 0) else ""
    qc.aplicar_tema_plotly(fig, f"l = {l}, mₗ = {m} · radio R = {R:.4g} {u['nombre_longitud']}{tipo}", altura=600)
    fig.update_layout(scene=_estilo_escena(1.15 * R, u["nombre_longitud"]),
                      scene2=_estilo_escena(lim, "sr⁻¹"), margin=dict(l=0, r=0, t=90, b=0))
    return fig


def figura_densidad_cartesiana(l: int, m: int, real: bool):
    """
    Densidad de probabilidad |Y_l^m|² frente a la posición en coordenadas cartesianas: cortes polares en los planos
    xz, yz y xy (distancia al origen = |Y|² en esa dirección) y |Y|² sobre la esfera en función de z/R = cosθ.
    """
    import matplotlib.pyplot as plt
    if qc.modo_compacto():
        fig, ejes = plt.subplots(4, 1, figsize=(7.2, 22), constrained_layout=True)
    else:
        fig, ejes = plt.subplots(2, 2, figsize=(13.5, 12), constrained_layout=True)
    ejes = np.ravel(ejes)
    ejes_letras = {"xz": ("x", "z"), "yz": ("y", "z"), "xy": ("x", "y")}
    escala = float(np.max(densidad_probabilidad(l, m, *malla_angular(61), real)))
    lim = 0.0
    for ax, plano in zip(ejes[:3], PLANOS):
        h, v, dens, _ = curva_densidad_plano(l, m, plano, real)
        lim = max(lim, float(np.max(np.abs(np.concatenate([h, v])))))
        ax.fill(h, v, color=COLORES["densidad"], alpha=0.30, lw=0)
        ax.plot(h, v, color=COLORES["densidad"], lw=2.2, label=None)
        ax.axhline(0, color=COLORES["gris"], lw=0.8)
        ax.axvline(0, color=COLORES["gris"], lw=0.8)
        a, b = ejes_letras[plano]
        ax.set_xlabel(f"{a}")
        ax.set_ylabel(f"{b}")
        ax.set_title(f"Plano {plano}")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        if float(np.max(dens)) < 1e-12 * escala:
            ax.text(0.5, 0.62, "Densidad nula", transform=ax.transAxes,
                    ha="center", va="center", fontsize=11, color=COLORES["gris"])
    lim = 1.12 * (lim or 1.0)
    for ax in ejes[:3]:
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
    ax = ejes[3]
    phi_max = meridiano_maximo(m, real)
    z, d0 = densidad_frente_a_z(l, m, real, phi_max)
    ax.plot(z, d0, color=COLORES["densidad"], lw=2.4)
    for t in nodos_latitud(l, m):
        ax.axvline(np.cos(t), color=COLORES["gris"], ls=":", lw=1.2)
    ax.set_xlabel("z / R")
    ax.set_ylabel("Densidad angular [sr⁻¹]")
    ax.set_title("Densidad angular frente a z")
    ax.set_xlim(-1, 1)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    tipo = " · orbital real" if (real and m != 0) else ""
    fig.suptitle(f"Densidad angular |Y|² [sr⁻¹] · l = {l}, mₗ = {m}{tipo}", fontsize=13, fontweight="bold")
    return fig


def figura_confinada(p: ParametrosConfinada, d: dict, n_niveles: int = 3):
    """Radial R_nl, P(r), corte de la densidad volumétrica y diagrama de niveles."""
    import matplotlib.pyplot as plt
    u = qc.obtener_unidades(p.sistema)
    fx, fe = u["factor_longitud"], u["factor_energia"]
    r = d["r"]
    fig, ejes = qc.rejilla(2, 2, (13, 8.6), constrained_layout=True)
    a = ejes[0, 0]
    a.plot(r / fx, d["R"] * fx ** 1.5, color=COLORES["onda"], lw=2)
    a.axhline(0, color=COLORES["gris"], lw=0.8)
    for nodo in d["nodos_radiales"]:
        a.axvline(nodo / fx, color=COLORES["gris"], ls="--", lw=0.8)
    a.set_xlabel(f"r [{u['nombre_longitud']}]")
    a.set_ylabel(f"R_nl(r) [{u['nombre_longitud']}^(−3/2)]")
    a.set_title(f"Función radial del estado {nombre_orbital(p.n, p.l)}  ·  {p.n - 1} nodo(s) radial(es)")
    a.grid(True)
    a = ejes[0, 1]
    a.plot(r / fx, d["P"] * fx, color=COLORES["densidad"], lw=2)
    a.fill_between(r / fx, d["P"] * fx, color=COLORES["densidad"], alpha=0.2)
    a.axvline(d["r_medio"] / fx, color=COLORES["energia"], ls="--", lw=1.2, label=f"⟨r⟩ = {d['r_medio'] / fx:.4g}")
    a.set_xlabel(f"r [{u['nombre_longitud']}]")
    a.set_ylabel(f"P(r) = r²R² [1/{u['nombre_longitud']}]")
    a.set_title("Densidad de probabilidad RADIAL (∫P dr = 1)")
    a.legend()
    a.grid(True)
    a = ejes[1, 0]
    x, z, dens = rebanada_densidad(p)
    im = a.imshow(dens, extent=[-1, 1, -1, 1], origin="lower", cmap="magma", aspect="equal")
    a.add_patch(plt.Circle((0, 0), 1.0, fill=False, color=COLORES["onda"], lw=1.5))
    a.set_xlabel("x / R")
    a.set_ylabel("z / R")
    a.set_title(f"Corte y = 0 de la densidad VOLUMÉTRICA |ψ|² (m = {p.m})")
    plt.colorbar(im, ax=a, label="|ψ|² · R³")
    a = ejes[1, 1]
    niveles = niveles_confinados(max(n_niveles, p.n), max(4, p.l))
    e0 = HBAR ** 2 / (2.0 * p.masa * p.radio ** 2)
    for alfa, n, l in niveles:
        sel = (n == p.n and l == p.l)
        y = e0 * alfa ** 2 / fe
        a.hlines(y, l - 0.38, l + 0.38, color=COLORES["energia"] if sel else COLORES["onda"], lw=3 if sel else 1.6)
        a.text(l, y, f" {nombre_orbital(n, l)}", va="bottom", ha="center", fontsize=8,
               color=COLORES["energia"] if sel else COLORES["texto"])
    a.set_xticks(range(0, max(4, p.l) + 1))
    a.set_xticklabels([f"l = {l}\n({letra(l)})" for l in range(0, max(4, p.l) + 1)])
    a.set_ylabel(f"E [{u['nombre_energia']}]")
    a.set_title("Niveles de energía (degeneración 2l+1; no depende de m)")
    a.grid(True, axis="y")
    return fig


# =====================================================================
# 3. PRUEBAS NUMÉRICAS
# =====================================================================
# ---------------------------------------------------------------------
# Predice y experimenta · Instrumentos · Informe
# ---------------------------------------------------------------------
_THETA_PD, _PHI_PD = 1.1, 0.5          # dirección genérica (rad) para comparar densidades


def _calc_esf(magnitud, modificar, unidad):
    def f(p: ParametrosEsfera):
        return float(magnitud(p)), float(magnitud(modificar(p))), unidad
    return f


def _superficies_nodales(p):
    return numero_total_superficies_nodales(p.l, 0)


def _densidad_generica(p):
    return float(densidad_probabilidad(p.l, p.m, _THETA_PD, _PHI_PD))


PREGUNTAS_PREDICE = [
    predice.Pregunta(
        "nodales_2l", "¿Qué le pasa al número de superficies nodales del armónico Yₗ⁰ si se duplica l?",
        "Se cambia l → 2l (m = 0)",
        (predice.Opcion("Se duplica", 2.0), predice.Opcion("Se cuadruplica", 4.0), predice.Opcion("No cambia", 1.0),
         predice.Opcion("Se reduce a la mitad", 0.5)),
        ("Cuenta las superficies nodales de s, p y d: 0, 1 y 2.", "El número de superficies nodales es l."),
        "Un armónico esférico real tiene l superficies nodales (l − |m| conos más |m| planos): al duplicar l se duplican.",
        "esfera", "Superficies nodales", _calc_esf(_superficies_nodales, lambda p: replace(p, l=2 * p.l, m=0), "")),
    predice.Pregunta(
        "simetria_m", "¿Cómo se compara la densidad |Yₗᵐ|² con |Yₗ⁻ᵐ|² en una misma dirección (armónicos complejos)?",
        "Se cambia m → −m (misma dirección θ = 1.1 rad, φ = 0.5 rad)",
        (predice.Opcion("Son iguales", 1.0), predice.Opcion("La de −m es el doble", 2.0),
         predice.Opcion("La de −m es la mitad", 0.5), predice.Opcion("La de −m es cuatro veces mayor", 4.0)),
        ("Yₗ⁻ᵐ y Yₗᵐ solo se diferencian en la fase e^{imφ}.", "El módulo de una fase compleja es 1."),
        "|Yₗ⁻ᵐ| = |Yₗᵐ|: la densidad de los complejos conjugados es la misma; solo cambia el sentido de giro de la fase.",
        "esfera", "Densidad |Y|²", _calc_esf(_densidad_generica, lambda p: replace(p, m=-p.m), "sr⁻¹")),
]


def informe_estado_angular(p: ParametrosEsfera, conclusiones: str = "") -> informes.Informe:
    h, v, _dens, _ = curva_densidad_plano(p.l, p.m, "xz", False)
    d_polo = float(densidad_probabilidad(p.l, p.m, 0.0, 0.0))
    d_ecuador = float(densidad_probabilidad(p.l, p.m, np.pi / 2, 0.0))
    norma = float(np.real(integral_solapamiento(p.l, p.m, p.l, p.m)))
    with informes.estilo_claro():
        fig, ax = informes.figura_clara(4.6, 4.6)
        ax.plot(h, v, color="#1F3A93")
        ax.set_aspect("equal")
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        ax.set(xlabel="x [sr⁻¹]", ylabel="z [sr⁻¹]", title=f"Corte polar de |Y|² (l = {p.l}, m = {p.m}, plano xz)")
        fig.tight_layout()
    return informes.Informe(
        titulo=f"Armónico esférico Y(l = {p.l}, m = {p.m})", simulador="Partícula en una esfera · armónicos esféricos",
        objetivo="Interpretar la densidad angular |Yₗᵐ|² y reconocer qué información da (y cuál no) sobre la partícula.",
        modelo="Armónicos esféricos exactos. Solo describen la parte angular: no dan información sobre la distancia al "
               "centro, que depende de la parte radial.",
        ecuaciones=[r"\hat L^2Y_l^m=\hbar^2\,l(l+1)\,Y_l^m", r"P\approx|Y_l^m|^2\,\Delta\Omega,\quad \Delta\Omega=\sin\theta\,\Delta\theta\,\Delta\varphi",
                    r"\int|Y_l^m|^2\,d\Omega=1"],
        parametros=[("Número cuántico l", f"{p.l}", ""), ("Número cuántico m", f"{p.m}", ""), ("Tipo", "Complejo", "")],
        procedimiento=["Se evalúa Yₗᵐ(θ, φ) con la función de Legendre asociada.", "Se calcula la densidad |Y|².",
                       "Se comprueba la normalización con una cuadratura angular."],
        resultados=[("|Y|² en el eje z (θ = 0)", f"{d_polo:.8g}", "sr⁻¹"), ("|Y|² en el ecuador (θ = 90°, φ = 0)", f"{d_ecuador:.8g}", "sr⁻¹"),
                    ("Superficies nodales", f"{numero_total_superficies_nodales(p.l, p.m)}", ""),
                    ("Degeneración 2l + 1", f"{2 * p.l + 1}", ""), ("Normalización ∫|Y|²dΩ", f"{norma:.10f}", "")],
        figuras=[fig],
        preguntas=["¿Cómo se obtiene la probabilidad de hallar la partícula en una dirección?",
                   "¿Dan estas gráficas información sobre la distancia al núcleo? Justifica."],
        conclusiones=conclusiones)


def _pestana_predice(p: ParametrosEsfera):
    st.markdown("Predice, ejecuta y compara con el estado angular (l, m) elegido arriba. La primera pregunta necesita l ≥ 1.")
    datos = {"simulador": "Partícula en una esfera · armónicos esféricos", "modelo": "Armónicos esféricos exactos.",
             "ecuaciones": [r"\hat L^2Y_l^m=\hbar^2\,l(l+1)\,Y_l^m"],
             "parametros": [("l", f"{p.l}", ""), ("m", f"{p.m}", "")]}
    predice.panel(PREGUNTAS_PREDICE, p, "esf", datos_informe=datos)


def _pestana_instrumentos(p: ParametrosEsfera):
    st.markdown("**Probabilidad en una dirección.** *Mide:* la densidad angular |Y|² en una dirección y la probabilidad "
                "P ≈ |Y|²·ΔΩ de hallar la partícula en un pequeño ángulo sólido. *No mide:* la distancia al núcleo, "
                "ni una posición real: |Y|² solo depende de la dirección.")
    c1, c2, c3, c4 = st.columns(4)
    th = c1.number_input("θ [°]", 0.0, 180.0, 45.0, 1.0, key="esf_inst_th", format="%.4g")
    ph = c2.number_input("φ [°]", 0.0, 360.0, 0.0, 1.0, key="esf_inst_ph", format="%.4g")
    dth = c3.number_input("Δθ [°]", 0.1, 90.0, 5.0, 0.5, key="esf_inst_dth", format="%.4g")
    dph = c4.number_input("Δφ [°]", 0.1, 180.0, 5.0, 0.5, key="esf_inst_dph", format="%.4g")
    t, f, dt, df = np.radians([th, ph, dth, dph])
    t1, t2 = max(0.0, t - dt / 2), min(np.pi, t + dt / 2)
    try:
        dens = float(densidad_probabilidad(p.l, p.m, t, f))
        p_num = instrumentos.probabilidad_angular(lambda a, b: densidad_probabilidad(p.l, p.m, a, b), t1, t2, f - df / 2, f + df / 2)
    except ValueError as error:
        qc.error(error)
        return
    d_omega = np.sin(t) * dt * df
    p_aprox = dens * d_omega
    qc.metricas([("|Y|² en la dirección [sr⁻¹]", f"{dens:.8g}", "Densidad angular, no probabilidad"),
                 ("ΔΩ = senθ·Δθ·Δφ [sr]", f"{d_omega:.6g}", "Ángulo sólido de la región"),
                 ("P ≈ |Y|²·ΔΩ", f"{p_aprox:.6g}", "Aproximación para región pequeña"),
                 ("P por cuadratura", f"{p_num:.6g}", "Integral numérica sobre la región")], columnas=4)
    if p_num > 0:
        st.caption(f"Diferencia relativa entre la aproximación y la cuadratura: {abs(p_aprox - p_num) / p_num * 100:.3g} %. "
                   "Es **error de aproximación** (región finita), no incertidumbre experimental.")
    st.latex(r"P\approx|Y_l^m(\theta,\varphi)|^2\,\Delta\Omega,\qquad \Delta\Omega=\sin\theta\,\Delta\theta\,\Delta\varphi")
    informes.boton_informe(lambda texto: informe_estado_angular(p, texto), "esf_inf", f"esfera_informe_l{p.l}_m{p.m}")


def ejecutar_pruebas() -> qc.RegistroPruebas:
    r = qc.RegistroPruebas("Armónicos esféricos y partícula en una esfera")
    r.comprobar(f"Calibración del backend: «{NOMBRE_BACKEND}» reproduce las fórmulas cerradas (l ≤ 2, con Condon–Shortley)",
                _pasa_calibracion(armonico_esferico))

    th = np.array([0.2, 0.8, 1.4, 2.1, 2.9])
    ph = np.array([0.1, 1.3, 2.2, 4.0, 5.9])
    err = max(np.max(np.abs(armonico_esferico(l, m, th, ph) - formas_cerradas(l, m, th, ph)))
              for l in range(3) for m in range(-l, l + 1))
    r.comprobar("Armónicos = formas cerradas Y_0^0 … Y_2^m", err < 1e-12, f"máx error = {err:.2e}")
    err = max(np.max(np.abs(armonico_esferico(l, m, th, ph) - _armonico_lpmv(l, m, th, ph)))
              for l in range(9) for m in range(-l, l + 1))
    r.comprobar("Backend de SciPy = implementación independiente (lpmv), l ≤ 8", err < 1e-10, f"máx diferencia = {err:.2e}")

    # Convención de ángulos y fase de Condon–Shortley
    y11 = armonico_esferico(1, 1, np.pi / 2, 0.0)
    r.comprobar("Condon–Shortley: Y_1^1(θ=π/2, φ=0) = −√(3/8π) < 0", abs(y11 - (-np.sqrt(3 / (8 * np.pi)))) < 1e-12)
    r.comprobar("Convención: Y_1^0 es máximo en el polo norte θ = 0 (θ es el ángulo POLAR)",
                abs(armonico_esferico(1, 0, 0.0, 0.7) - np.sqrt(3 / (4 * np.pi))) < 1e-12)
    r.comprobar("Convención: Y_1^1 se anula en el polo (θ = 0) y no en el ecuador",
                abs(armonico_esferico(1, 1, 0.0, 0.7)) < 1e-12 and abs(armonico_esferico(1, 1, np.pi / 2, 0.7)) > 0.3)
    r.comprobar("Sin invertir ángulos: |Y_1^1|² no depende de φ pero sí de θ",
                abs(abs(armonico_esferico(1, 1, 1.0, 0.2)) - abs(armonico_esferico(1, 1, 1.0, 4.4))) < 1e-12
                and abs(abs(armonico_esferico(1, 1, 0.5, 0.2)) - abs(armonico_esferico(1, 1, 1.5, 0.2))) > 0.1)

    # Simetrías
    e1 = max(np.max(np.abs(armonico_esferico(l, -m, th, ph) - (-1) ** m * np.conj(armonico_esferico(l, m, th, ph))))
             for l in range(7) for m in range(l + 1))
    r.comprobar("Simetría Y_l^{−m} = (−1)^m conj(Y_l^m)", e1 < 1e-10, f"máx = {e1:.2e}")
    e2 = max(np.max(np.abs(armonico_esferico(l, m, np.pi - th, ph + np.pi) - (-1) ** l * armonico_esferico(l, m, th, ph)))
             for l in range(8) for m in range(-l, l + 1))
    r.comprobar("Paridad: Y(π−θ, φ+π) = (−1)^l Y(θ, φ)", e2 < 1e-10, f"máx = {e2:.2e}")
    d = 0.77
    e3 = max(np.max(np.abs(armonico_esferico(l, m, th, ph + d) - np.exp(1j * m * d) * armonico_esferico(l, m, th, ph)))
             for l in range(6) for m in range(-l, l + 1))
    r.comprobar("L_z: Y(θ, φ+δ) = e^{imδ} Y(θ, φ)", e3 < 1e-10, f"máx = {e3:.2e}")

    # Normalización y ortogonalidad (Gauss–Legendre)
    e4 = max(abs(integral_solapamiento(l, m, l, m) - 1.0) for l in range(0, 13) for m in range(-l, l + 1))
    r.comprobar("Normalización ∫|Y_l^m|² dΩ = 1 (Gauss–Legendre, l ≤ 12)", e4 < 1e-12, f"máx |∫−1| = {e4:.2e}")
    estados = [(l, m) for l in range(5) for m in range(-l, l + 1)]
    G = np.array([[integral_solapamiento(*a, *b) for b in estados] for a in estados])
    e5 = np.max(np.abs(G - np.eye(len(estados))))
    r.comprobar("Ortonormalidad ⟨Y_l^m|Y_l'^m'⟩ = δδ (l ≤ 4)", e5 < 1e-12, f"máx desviación = {e5:.2e}")
    val, dev = normalizacion_malla(3, 2, 90)
    r.comprobar("Normalización sobre la MALLA del gráfico (l=3, m=2, 90×180)", dev < 1e-3,
                f"∫ = {val:.6f}, desviación = {dev:.2e}")

    # Combinaciones reales
    T, P = np.meshgrid(np.linspace(0.05, 3.09, 40), np.linspace(0, 6.2, 60), indexing="ij")
    px = evaluar_campo(1, 1, "real_cos", T, P)
    py = evaluar_campo(1, 1, "real_sin", T, P)
    r.comprobar("Real ∝ cos(φ), l=1: = √(3/4π) sinθ cosφ  (orbital pₓ)",
                np.max(np.abs(px - np.sqrt(3 / (4 * np.pi)) * np.sin(T) * np.cos(P))) < 1e-12)
    r.comprobar("Real ∝ sin(φ), l=1: = √(3/4π) sinθ sinφ  (orbital p_y)",
                np.max(np.abs(py - np.sqrt(3 / (4 * np.pi)) * np.sin(T) * np.sin(P))) < 1e-12)
    xg, wg = np.polynomial.legendre.leggauss(40)
    TG, PG = np.meshgrid(np.arccos(xg), np.arange(80) * 2 * np.pi / 80, indexing="ij")

    def integrar_g(f):
        return float(np.sum(wg[:, None] * f) * 2 * np.pi / 80)
    fc, fs = evaluar_campo(3, 2, "real_cos", TG, PG), evaluar_campo(3, 2, "real_sin", TG, PG)
    r.comprobar("Combinaciones reales normalizadas y ortogonales (l=3, |m|=2)",
                abs(integrar_g(fc ** 2) - 1) < 1e-12 and abs(integrar_g(fs ** 2) - 1) < 1e-12
                and abs(integrar_g(fc * fs)) < 1e-12)
    r.comprobar_error("Rechaza la combinación sin para m = 0", evaluar_campo, 2, 0, "real_sin", T, P)
    r.comprobar("|Y_l^m|² es independiente de φ para m ≠ 0 pero la combinación real NO lo es",
                np.ptp(evaluar_campo(2, 1, "densidad", np.full(9, 1.0), np.linspace(0, 6, 9))) < 1e-12
                and np.ptp(evaluar_campo(2, 1, "real_cos", np.full(9, 1.0), np.linspace(0, 6, 9))) > 0.1)
    fase = evaluar_campo(3, 2, "fase", T, P)
    r.comprobar("La fase arg Y está en [−π, π]", np.all(np.abs(fase) <= np.pi + 1e-12))

    # Nodos
    ok_nodos = all(len(nodos_latitud(l, m)) == l - abs(m) for l in range(0, 13) for m in range(-l, l + 1))
    r.comprobar("Número de nodos latitudinales = l − |m| (l ≤ 12)", ok_nodos)
    r.comprobar("Nodos de Y_1^0: θ = π/2", np.allclose(nodos_latitud(1, 0), [np.pi / 2]))
    r.comprobar("Nodos de Y_2^0: cos θ = ±1/√3", np.allclose(nodos_latitud(2, 0), np.arccos([1 / np.sqrt(3), -1 / np.sqrt(3)])))
    err = max(np.max(np.abs(special.lpmv(abs(m), l, np.cos(nodos_latitud(l, m))))) / np.max(np.abs(special.lpmv(abs(m), l, np.linspace(-1, 1, 2001)))) if l > abs(m) else 0.0
              for l in range(1, 13) for m in range(-l, l + 1))
    r.comprobar("Los nodos son ceros de P_l^{|m|}(cos θ)", err < 1e-8, f"máx |P|/máx|P| en los nodos = {err:.2e}")
    r.comprobar("Combinación real: l superficies nodales (l−|m| conos + |m| planos)",
                all(numero_total_superficies_nodales(l, m) == l for l in range(9) for m in range(-l, l + 1)))
    ang = nodos_meridianos(2, "real_cos")
    r.comprobar("Meridianos nodales de cos(2φ): 4 semiplanos y valor nulo en ellos",
                len(ang) == 4 and np.max(np.abs(evaluar_campo(2, 2, "real_cos", np.full(4, 1.0), ang))) < 1e-12)

    # Geometría
    x, y, z = esfericas_a_cartesianas(2.0, np.array([np.pi / 2, 0.0, np.pi / 2]), np.array([0.0, 1.0, np.pi / 2]))
    r.comprobar("Cartesianas: (θ=π/2, φ=0) → +x;  θ=0 → +z;  (θ=π/2, φ=π/2) → +y",
                np.allclose([x[0], y[0], z[0]], [2, 0, 0], atol=1e-12) and np.allclose([x[1], y[1], z[1]], [0, 0, 2])
                and np.allclose([x[2], y[2], z[2]], [0, 2, 0], atol=1e-12))
    Tm, Pm = malla_angular(40)
    X, Y, Z = esfericas_a_cartesianas(1.7, Tm, Pm)
    r.comprobar("x² + y² + z² = R² en toda la malla", np.max(np.abs(X ** 2 + Y ** 2 + Z ** 2 - 1.7 ** 2)) < 1e-12)
    rr, tt, pp = cartesianas_a_esfericas(X, Y, Z)
    i = slice(1, -1)                         # en los polos φ no está definido: se excluyen
    r.comprobar("Transformación cartesianas ↔ esféricas (ida y vuelta, fuera de los polos)",
                np.max(np.abs(rr - 1.7)) < 1e-12 and np.max(np.abs(tt[i] - Tm[i])) < 1e-9
                and np.max(np.abs(np.exp(1j * pp[i]) - np.exp(1j * Pm[i]))) < 1e-12)
    r.comprobar("La costura φ = 0 ≡ 2π queda cerrada (superficie sin hueco)",
                np.max(np.abs(evaluar_campo(3, 2, "densidad", Tm, Pm)[:, 0] - evaluar_campo(3, 2, "densidad", Tm, Pm)[:, -1])) < 1e-12)
    campo = evaluar_campo(2, 1, "real_cos", Tm, Pm)
    rl, _ = geometria_superficie(campo, "lobulos", 1.0, 0.3, "real_cos")
    rs, _ = geometria_superficie(campo, "suave", 1.0, 0.3, "real_cos")
    r.comprobar("Lóbulos: r ≤ R;  deformación suave: R(1−α) ≤ r ≤ R(1+α);  esfera: r = R exacto",
                abs(np.max(rl) - 1.0) < 1e-12 and np.min(rs) >= 0.7 - 1e-12 and np.max(rs) <= 1.3 + 1e-12
                and np.all(geometria_superficie(campo, "esfera", 1.0, 0.3, "real_cos")[0] == 1.0))

    # Validación
    v = validar_parametros_esfera
    base = dict(radio=1.0, sistema="SI", n_theta=90, modo="densidad")
    r.comprobar_error("Rechaza l < 0", v, -1, 0, **base)
    r.comprobar_error("Rechaza l no entero", v, 1.5, 0, **base)
    r.comprobar_error(f"Rechaza l > {L_MAX}", v, L_MAX + 1, 0, **base)
    r.comprobar_error("Rechaza |m| > l", v, 2, 3, **base)
    r.comprobar_error("Rechaza m no entero", v, 2, 0.5, **base)
    r.comprobar_error("Rechaza radio ≤ 0", v, 1, 0, **{**base, "radio": 0.0})
    r.comprobar_error("Rechaza resolución angular insuficiente", v, 10, 0, **{**base, "n_theta": 30})
    r.comprobar_error("Rechaza modo desconocido", v, 1, 0, **{**base, "modo": "xyz"})
    r.comprobar_error("Rechaza combinación sin con m = 0", v, 1, 0, **{**base, "modo": "real_sin"})
    r.comprobar_error("Rechaza α fuera de rango", v, 1, 0, alfa=2.0, **base)
    r.comprobar("m se restringe a [−l, l] al cambiar l", ajustar_m(1, 3) == 1 and ajustar_m(2, -5) == -2 and ajustar_m(0, 2) == 0)
    r.comprobar("Para cada l hay exactamente 2l+1 valores de m", all(len(m_permitidos(l)) == 2 * l + 1 for l in l_permitidos()))

    # Robustez del backend: simulación de versiones de SciPy
    class FalsoLegado:                       # solo existe la firma antigua sph_harm(m, n, azimut, polar)
        @staticmethod
        def sph_harm(m, n, azimut, polar):
            return _armonico_lpmv(n, m, polar, azimut)

    class FalsoMalo:                         # sph_harm_y con ángulos intercambiados (convención incorrecta)
        @staticmethod
        def sph_harm_y(n, m, theta, phi):
            return _armonico_lpmv(n, m, phi, theta)

    class FalsoNuevo:
        @staticmethod
        def sph_harm_y(n, m, theta, phi):
            return _armonico_lpmv(n, m, theta, phi)
    r.comprobar("Backend: firma legada sph_harm (ángulos invertidos) se adapta correctamente",
                construir_backend(FalsoLegado)[0].endswith("(legada)"))
    r.comprobar("Backend: una función con θ↔φ intercambiados se RECHAZA y se usa la implementación propia",
                construir_backend(FalsoMalo)[0].startswith("implementación propia"))
    r.comprobar("Backend: sph_harm_y correcta se acepta", construir_backend(FalsoNuevo)[0] == "scipy.special.sph_harm_y")

    # Modelo confinado
    r.comprobar("Ceros de j_0: α_n0 = nπ", np.allclose(ceros_bessel_esferica(0, 5), np.pi * np.arange(1, 6)))
    r.comprobar("Ceros conocidos: j_1 → 4.493409, 7.725252;  j_2 → 5.763459",
                np.allclose(ceros_bessel_esferica(1, 2), [4.493409457909, 7.725251836938], atol=1e-9)
                and abs(ceros_bessel_esferica(2, 1)[0] - 5.763459196895) < 1e-9)
    z = [ceros_bessel_esferica(l, 4) for l in range(0, 9)]
    r.comprobar("Los α_nl son ceros de j_l y crecen con n",
                all(np.max(np.abs(special.spherical_jn(l, z[l]))) < 1e-9 and np.all(np.diff(z[l]) > 0) for l in range(9)))
    R0 = 1e-9
    m0 = M_E
    r.comprobar("Radial: ∫R_nl² r² dr = 1 (n ≤ 4, l ≤ 4)",
                max(abs(calcular_confinada(ParametrosConfinada(n, l, 0, R0, m0, "SI"))["norma_radial"] - 1.0)
                    for n in range(1, 5) for l in range(5)) < 1e-6)
    pc = ParametrosConfinada(3, 2, 0, R0, m0, "SI")
    dc = calcular_confinada(pc)
    cuenta = int(np.sum(np.sign(dc["R"][1:-2]) * np.sign(dc["R"][2:-1]) < 0))
    r.comprobar("R_nl(R) = 0 en la pared y n − 1 nodos radiales interiores",
                abs(dc["R"][-1]) < 1e-6 * np.max(np.abs(dc["R"])) and cuenta == 2 == len(dc["nodos_radiales"]))
    r.comprobar("Normalización 3D = (radial) × (angular) = 1", abs(dc["norma_radial"] * abs(integral_solapamiento(2, 1, 2, 1)) - 1) < 1e-6)
    e1s, e2s = energia_confinada(1, 0, R0, m0), energia_confinada(2, 0, R0, m0)
    r.comprobar("E_n0 ∝ n² (E_20/E_10 = 4)", abs(e2s / e1s - 4.0) < 1e-12)
    r.comprobar("E ∝ 1/R² (R → 2R divide E por 4)", abs(energia_confinada(1, 1, 2 * R0, m0) / energia_confinada(1, 1, R0, m0) - 0.25) < 1e-12)
    r.comprobar("E_10 = ħ²π²/(2mR²)", abs(e1s - HBAR ** 2 * np.pi ** 2 / (2 * m0 * R0 ** 2)) / e1s < 1e-12)
    r.comprobar("E_11/E_10 = (4.4934/π)²", abs(energia_confinada(1, 1, R0, m0) / e1s - (4.493409457909 / np.pi) ** 2) < 1e-9)
    r.comprobar("Orden de niveles: 1s < 1p < 1d < 2s < 1f < 2p",
                [nombre_orbital(n, l) for _, n, l in niveles_confinados(2, 3)][:6] == ["1s", "1p", "1d", "2s", "1f", "2p"])
    r.comprobar("La energía no depende de m (degeneración 2l+1)",
                calcular_confinada(ParametrosConfinada(1, 2, 2, R0, m0, "SI"))["energia"]
                == calcular_confinada(ParametrosConfinada(1, 2, -1, R0, m0, "SI"))["energia"]
                and calcular_confinada(ParametrosConfinada(1, 2, 0, R0, m0, "SI"))["degeneracion"] == 5)
    _, _, dens = rebanada_densidad(ParametrosConfinada(1, 0, 0, R0, m0, "SI"), 401)
    h = 2.0 / 400
    suma = np.nansum(np.where(np.isnan(dens), 0.0, dens)) * h * h      # ∫ρ dx dz en el plano y = 0 (solo comprobación de forma)
    r.comprobar("Corte volumétrico: NaN fuera de la esfera y densidad finita dentro", np.isnan(dens[0, 0]) and np.isfinite(dens[200, 200]) and suma > 0)
    r.comprobar_error("Confinada: rechaza masa ≤ 0", validar_parametros_confinada, 1, 0, 0, 1.0, 0.0, "SI")
    r.comprobar_error("Confinada: rechaza radio ≤ 0", validar_parametros_confinada, 1, 0, 0, -1.0, 1.0, "SI")
    r.comprobar_error("Confinada: rechaza n = 0", validar_parametros_confinada, 0, 0, 0, 1.0, 1.0, "SI")
    r.comprobar_error("Confinada: rechaza |m| > l", validar_parametros_confinada, 1, 0, 1, 1.0, 1.0, "SI")
    pa = validar_parametros_confinada(1, 0, 0, 2.0, 1.0, "Atómicas")
    r.comprobar("Unidades atómicas: R = 2 a₀ en metros", abs(pa.radio - 2 * qc.A0) < 1e-20)
    pu = validar_parametros_confinada(1, 0, 0, 1.0, 1.0, "Atómicas")
    r.comprobar("Atómicas: R = 1 a₀, m = mₑ → E₁s = π²/2 Eₕ", abs(energia_confinada(1, 0, pu.radio, pu.masa) / qc.E_HARTREE - np.pi ** 2 / 2) < 1e-9)

    # Humo de figuras
    p = validar_parametros_esfera(2, 1, 1.0, "SI", 50, "densidad", "lobulos")
    r.comprobar("Figuras: superficie 3D y comparación se construyen sin error",
                len(figura_superficie_3d(p)[0].data) == 1 and len(figura_comparacion_orbitales([(0, 0), (1, 0), (1, 1)], "densidad", "lobulos", "Viridis", 30).data) == 3)
    # Densidad de probabilidad en coordenadas cartesianas (criterio del curso)
    r.comprobar("Densidad |Y_1^0|² en (0, 0, 1) = 3/(4π)", abs(densidad_en_punto(1, 0, 0, 0, 1, 1.0)["densidad_sr"] - 3 / (4 * np.pi)) < 1e-12)
    r.comprobar("Densidad |Y_1^0|² en el plano nodal z = 0 es cero", densidad_en_punto(1, 0, 1, 1, 0, 1.0)["densidad_sr"] < 1e-25)
    r.comprobar("Orbital pₓ (real, m = 1): |p|² = 3/(4π) en (1, 0, 0)",
                abs(densidad_en_punto(1, 1, 1, 0, 0, 1.0, real=True)["densidad_sr"] - 3 / (4 * np.pi)) < 1e-12)
    hh, vv, dd, _ = curva_densidad_plano(2, 1, "xz")
    r.comprobar("Corte polar xz: distancia al origen = |Y|²", bool(np.allclose(np.hypot(hh, vv), dd, atol=1e-14)))
    r.comprobar_error("Densidad: el origen no define una dirección", densidad_en_punto, 1, 0, 0, 0, 0, 1.0)
    # --- Modo «Predice y experimenta»: la respuesta correcta sale del cálculo
    p_pd = validar_parametros_esfera(2, 1, 1.0, "SI", 90, "densidad", "lobulos", 0.4, "Viridis")
    for q in PREGUNTAS_PREDICE:
        r.comprobar(f"Pregunta de predicción «{q.id}»: la respuesta correcta sale del cálculo",
                    predice.validar_pregunta(q, p_pd) == [], "; ".join(predice.validar_pregunta(q, p_pd)))
    return r


# =====================================================================
# 4. INTERFAZ (Streamlit)
# =====================================================================
VALORES_INICIALES = {
    "esf_l": 2, "esf_m": 1, "esf_radio": 1.0, "esf_sistema": "SI", "esf_ntheta": 90, "esf_modo": "densidad",
    "esf_forma": "lobulos", "esf_alfa": 0.4, "esf_mapa": "Viridis", "esf_phi0": 0.0, "esf_theta0": 90.0,
    "esf_comp_sel": [(0, 0), (1, 0), (1, 1), (2, 0)], "esf_comp_l": 3, "esf_comp_m": 2, "esf_comp_extra": False,
    "esf_comp_modo": "densidad", "esf_comp_forma": "lobulos",
    "esf_cv_l": 1, "esf_cv_m": 1,
    "esf_c_n": 1, "esf_c_l": 1, "esf_c_m": 0, "esf_c_masa": 1.0, "esf_c_radio": 1.0,
}
DEMOS = {
    "Orbital s · l = 0, m = 0 (simetría esférica)": {"esf_l": 0, "esf_m": 0, "esf_modo": "densidad", "esf_forma": "esfera"},
    "Orbital p_z · l = 1, m = 0 (dos lóbulos)": {"esf_l": 1, "esf_m": 0, "esf_modo": "densidad", "esf_forma": "lobulos"},
    "p complejo · l = 1, m = 1 (anillo, |Y|² sin φ)": {"esf_l": 1, "esf_m": 1, "esf_modo": "densidad", "esf_forma": "lobulos"},
    "Orbital pₓ real · l = 1, |m| = 1 (∝ cos φ)": {"esf_l": 1, "esf_m": 1, "esf_modo": "real_cos", "esf_forma": "lobulos", "esf_mapa": "RdBu"},
    "Orbital d_z² · l = 2, m = 0": {"esf_l": 2, "esf_m": 0, "esf_modo": "densidad", "esf_forma": "lobulos"},
    "Fase de Y₃² sobre la esfera": {"esf_l": 3, "esf_m": 2, "esf_modo": "fase", "esf_forma": "esfera", "esf_mapa": "Twilight"},
}


# ---------------------------------------------------------------------
# Guía de práctica y autoevaluación
# ---------------------------------------------------------------------
GUIA = [
    {"titulo": "Nodos latitudinales: l − |m|",
     "objetivo": "Relacionar los números cuánticos con la forma de |Yₗᵐ|².",
     "pasos": ["Cargar la configuración (l = 3, m = 0).", "Contar los conos nodales en la vista 3D o en la proyección 2D.",
               "Cambiar m a 1, 2 y 3 y cuenta otra vez."],
     "pregunta": "¿Cuántos nodos latitudinales esperas para l = 3 y cada valor de m?",
     "resultado": "Hay l − |m| nodos latitudinales: 3, 2, 1 y 0. Además, para m ≠ 0 la densidad se anula en los polos "
                  "(factor sin^|m| θ). Con m = ±3 la densidad es un anillo en el ecuador.",
     "pestana": "Armónico 3D", "config": {"esf_l": 3, "esf_m": 0, "esf_modo": "densidad", "esf_forma": "lobulos"}},
    {"titulo": "Orbital complejo frente a orbital real",
     "objetivo": "Ver que ±m dan la misma |Y|² y que los orbitales reales son combinaciones de ambos.",
     "pasos": ["Cargar la configuración (l = 1, m = 1, densidad).", "Observar la forma (anillo).",
               "Cambiar la magnitud a «Combinación real ∝ cos(|m|φ)» y después a «∝ sin(|m|φ)»."],
     "pregunta": "¿Por qué el armónico complejo no tiene orientación en el plano xy y el real sí?",
     "resultado": "|Y₁^{±1}|² ∝ sin²θ no depende de φ (simetría axial). Las combinaciones reales ∝ sinθ cosφ y "
                  "∝ sinθ sinφ son los orbitales pₓ y p_y: tienen un plano nodal y una orientación definida. Ambas "
                  "bases describen el mismo espacio de estados.",
     "pestana": "Armónico 3D", "config": {"esf_l": 1, "esf_m": 1, "esf_modo": "densidad", "esf_forma": "lobulos"}},
    {"titulo": "Paridad (−1)ˡ",
     "objetivo": "Comprobar cómo cambia el signo del armónico al invertir la dirección r → −r.",
     "pasos": ["Cargar la configuración (l = 2, m = 0, parte real).", "En la proyección 2D compara θ y 180° − θ.",
               "Repite con l = 3."],
     "pregunta": "¿Para qué valores de l el armónico es simétrico respecto al ecuador?",
     "resultado": "Para l par (paridad +1) el valor en θ y en 180° − θ (con φ → φ + 180°) es el mismo; para l impar "
                  "cambia de signo (paridad −1). En la vista 3D se ve como colores iguales u opuestos en lóbulos "
                  "opuestos.",
     "pestana": "Proyección 2D y cortes", "config": {"esf_l": 2, "esf_m": 0, "esf_modo": "re", "esf_forma": "lobulos",
                                                     "esf_mapa": "RdBu"}},
    {"titulo": "Niveles de una partícula confinada en una esfera",
     "objetivo": "Medir la dependencia E ∝ 1/R² y el orden de los niveles.",
     "pasos": ["Cargar la configuración (n = 1, l = 0, R = 1 nm).", "Registrar la energía.",
               "Cambiar R a 2 nm. Después vuelve a 1 nm y prueba l = 1 y l = 2, y n = 2 con l = 0."],
     "pregunta": "¿Qué nivel es más bajo: 2s (n = 2, l = 0) o 1d (n = 1, l = 2)?",
     "resultado": "Con R = 1 nm, E₁ₛ ≈ 0.376 eV (igual que la caja 1D de 1 nm, porque α = π) y con R = 2 nm se "
                  "divide por 4. El orden es 1s < 1p < 1d < 2s < 1f < 2p: el 1d (α ≈ 5.76) está por debajo del 2s "
                  "(α = 2π ≈ 6.28).",
     "pestana": "Partícula confinada", "config": {"esf_c_n": 1, "esf_c_l": 0, "esf_c_m": 0, "esf_c_masa": 1.0,
                                                  "esf_c_radio": 1.0, "esf_sistema": "SI"}},
]

PREGUNTAS = [
    {"enunciado": "Para l = 2, ¿qué valores puede tomar m?",
     "opciones": ["0, 1, 2", "−2, −1, 0, 1, 2", "1, 2", "Cualquier entero"], "correcta": 1,
     "explicacion": "m va de −l a +l en pasos de 1: hay 2l + 1 = 5 valores."},
    {"enunciado": "¿Cuántos nodos latitudinales (conos θ = cte) tiene Yₗᵐ?",
     "opciones": ["l", "|m|", "l − |m|", "l + |m|"], "correcta": 2,
     "explicacion": "Son las raíces de Pₗ^|m|(cos θ) en (−1, 1): hay exactamente l − |m|."},
    {"enunciado": "|Y₁¹|² y |Y₁⁻¹|² son…",
     "opciones": ["iguales y sin dependencia en φ", "iguales pero giradas 90°", "distintas: una es pₓ y la otra p_y",
                  "nulas en el ecuador"], "correcta": 0,
     "explicacion": "Y₁^{±1} ∝ sinθ e^{±iφ}: el módulo al cuadrado ∝ sin²θ es idéntico. Se diferencian en la fase (L_z = ±ħ)."},
    {"enunciado": "En las convenciones de física, θ es…",
     "opciones": ["el ángulo azimutal, medido en el plano xy", "el ángulo polar, medido desde el eje z",
                  "la longitud geográfica", "el ángulo entre r y el eje x"], "correcta": 1,
     "explicacion": "θ ∈ [0, π] es polar (desde +z) y φ ∈ [0, 2π) es azimutal. La antigua función de SciPy los usaba al revés."},
    {"enunciado": "La densidad |Yₗᵐ(θ, φ)|² representa…",
     "opciones": ["la probabilidad por unidad de volumen", "la probabilidad por unidad de ángulo sólido (dirección)",
                  "la distancia del electrón al núcleo", "la energía del estado"], "correcta": 1,
     "explicacion": "Es una densidad angular (sr⁻¹). La densidad volumétrica necesita además la parte radial: |R(r)|²|Y|²."},
    {"enunciado": "Para la partícula en una esfera impenetrable de radio R, la energía de un nivel es proporcional a…",
     "opciones": ["R", "1/R", "1/R²", "R²"], "correcta": 2,
     "explicacion": "E_nl = ħ²α_nl²/(2mR²), donde α_nl es un cero de la función de Bessel esférica jₗ."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("esf_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])
        st.session_state["esf_m"] = ajustar_m(st.session_state["esf_l"], st.session_state["esf_m"])


def _al_cambiar_l():
    """Callback: al cambiar l, m se restringe automáticamente a [−l, l]."""
    st.session_state["esf_m"] = ajustar_m(st.session_state["esf_l"], st.session_state["esf_m"])


def _campo_m(col, prefijo: str, l: int, etiqueta: str = "Número cuántico m") -> int:
    """Deslizador de m restringido a [−l, l]. Para l = 0 no hay rango: se muestra un campo fijo."""
    st.session_state[f"{prefijo}_m"] = ajustar_m(l, st.session_state[f"{prefijo}_m"])
    if l == 0:
        col.text_input(etiqueta, value="0  (único valor para l = 0)", disabled=True, key=f"{prefijo}_m_fijo")
        return 0
    return int(col.slider(etiqueta, -l, l, key=f"{prefijo}_m", help="Proyección L_z = mħ. Solo −l ≤ m ≤ l."))


def _selector_lm(prefijo: str, l_max: int, etiqueta: str = "", columnas=None):
    """Pareja (l, m) con m auto-restringido."""
    c1, c2 = columnas if columnas else st.columns(2)

    def _clamp():
        st.session_state[f"{prefijo}_m"] = ajustar_m(st.session_state[f"{prefijo}_l"], st.session_state[f"{prefijo}_m"])
    l = c1.slider(f"{etiqueta}l", 0, l_max, key=f"{prefijo}_l", on_change=_clamp,
                  help="Número cuántico de momento angular orbital: l = 0 (s), 1 (p), 2 (d), 3 (f)…")
    m = _campo_m(c2, prefijo, int(l), f"{etiqueta}m")
    return int(l), int(m)


def _leer_parametros():
    with st.container(border=True):
        qc.seccion("Estado angular y geometría")
        c1, c2, c3, c4 = st.columns(4)
        l = c1.slider("Número cuántico l", 0, L_MAX, key="esf_l", on_change=_al_cambiar_l,
                      help="Momento angular orbital: 0 (s), 1 (p), 2 (d), 3 (f)…")
        m = _campo_m(c2, "esf", int(l))
        sistema = c3.radio("Unidades de longitud", ["SI", "Atómicas"], key="esf_sistema", horizontal=True,
                           help="Solo cambia las unidades del radio R (nm o a₀).")
        u = qc.obtener_unidades(sistema)
        radio = c4.number_input(f"Radio R [{u['nombre_longitud']}]", min_value=0.0, step=0.5, format="%.4g",
                                key="esf_radio", help="Escala geométrica de la esfera. La parte angular no depende de R.")
        qc.seccion("Representación")
        d1, d2, d3, d4 = st.columns(4)
        d1.selectbox("Magnitud", list(MODOS), key="esf_modo", format_func=MODOS.get,
                     help="El armónico complejo tiene parte real, imaginaria, módulo y fase. Las combinaciones reales "
                          "son los orbitales de la química (pₓ, p_y, d…).")
        d2.selectbox("Forma de la superficie", list(FORMAS), key="esf_forma", format_func=FORMAS.get)
        d3.slider("Amplitud de deformación α", 0.0, ALFA_MAX, step=0.05, key="esf_alfa",
                  disabled=(st.session_state["esf_forma"] != "suave"),
                  help="Solo para «deformación suave»: r = R(1 + α f/max|f|). Es una deformación artificial.")
        d4.selectbox("Mapa de color", MAPAS_COLOR, key="esf_mapa")
        qc.pie_de_parametros(DEMOS, "esf_demo", _aplicar_demo, VALORES_INICIALES, "esf_reset",
                             medio=lambda col: col.slider(
                                 "Resolución angular (puntos en θ)", NTHETA_MIN, 200, step=10, key="esf_ntheta",
                                 help="En φ se usa el doble. Más puntos: superficie más suave y más lenta. "
                                      "Mínimo exigido: 4l + 8."))
    try:
        return validar_parametros_esfera(l, m, radio, sistema, st.session_state["esf_ntheta"], st.session_state["esf_modo"],
                                         st.session_state["esf_forma"], st.session_state["esf_alfa"], st.session_state["esf_mapa"])
    except ValueError as error:
        qc.error(error)
        return None


@st.cache_data(show_spinner=False, max_entries=24)
def _cache_superficie(l, m, radio, sistema, n_theta, modo, forma, alfa, mapa):
    p = validar_parametros_esfera(l, m, radio / qc.obtener_unidades(sistema)["factor_longitud"], sistema, n_theta,
                                  modo, forma, alfa, mapa)
    return figura_superficie_3d(p)


@st.cache_data(show_spinner=False, max_entries=12)
def _cache_comparacion(estados, modo, forma, mapa):
    return figura_comparacion_orbitales(list(estados), modo, forma, mapa)


@st.cache_data(show_spinner=False, max_entries=12)
def _cache_complejo_real(l, m):
    return figura_complejo_vs_real(l, m)


def _pestana_3d(p: ParametrosEsfera):
    val, dev = normalizacion_malla(p.l, p.m, p.n_theta)
    lat = nodos_latitud(p.l, p.m)
    qc.seccion("Resultados")
    qc.metricas([
        ("Orbital", f"{letra(p.l)}   (l = {p.l}, m = {p.m})"),
        ("L² = l(l+1)ħ²", f"{p.l * (p.l + 1)} ħ²", f"|L| = {np.sqrt(p.l * (p.l + 1)):.4f} ħ"),
        (r"$L_z = m\hbar$", f"{p.m} ħ"),
        ("Paridad (−1)ˡ", "par (+1)" if p.l % 2 == 0 else "impar (−1)"),
        ("Nodos latitudinales", f"{len(lat)}", "Conos θ = cte; hay l − |m|."),
        ("Superficies nodales (real)", f"{p.l}", "Combinación real: (l − |m|) conos + |m| planos."),
        ("Degeneración 2l + 1", f"{2 * p.l + 1}"),
        ("∫|Y|² dΩ (malla)", f"{val:.6f}", f"Desviación respecto de 1: {dev:.2e}"),
    ])
    try:
        figura, forma_ef = _cache_superficie(p.l, p.m, p.radio, p.sistema, p.n_theta, p.modo, p.forma, p.alfa, p.mapa)
    except ValueError as error:
        qc.error(error)
        return
    qc.seccion("Visualización 3D")
    if forma_ef == "esfera" and p.forma != "esfera":
        qc.nota("La fase no se puede «deformar»: la esfera se mantiene intacta.")
    if p.forma == "lobulos" and p.modo != "fase":
        qc.aviso("Lóbulos: la distancia al origen representa el valor; no es una superficie física.")
    if p.forma == "suave":
        qc.aviso("Deformación artificial, solo para apreciar el patrón.")
    qc.mostrar_plotly(figura, "esf_fig3d", archivo=f"esfera_Y_l{p.l}_m{p.m}.html")
    T, P = malla_angular(p.n_theta)
    Y = armonico_esferico(p.l, p.m, T, P)
    qc.exportar_datos({"theta [rad]": T, "phi [rad]": P,
                       "x [m]": p.radio * np.sin(T) * np.cos(P), "y [m]": p.radio * np.sin(T) * np.sin(P),
                       "z [m]": p.radio * np.cos(T), "|Y|^2 [1/sr]": np.abs(Y) ** 2, "Y": Y},
                      f"esfera_datos_l{p.l}_m{p.m}.csv", "Descargar |Y|² sobre la esfera, con x, y, z (CSV)")
    st.caption("Arrastrar para rotar · rueda para ampliar · doble clic para restablecer la vista.")
    with st.expander("Valores numéricos detallados", expanded=False):
        nodos_txt = "ninguno" if len(lat) == 0 else ", ".join(f"{np.degrees(t):.3f}" for t in lat)
        filas = [
            ("Nodos latitudinales θ", nodos_txt, "°", f"{len(lat)} = l − |m|"),
            ("Nodos en los polos θ = 0°, 180°", "sí" if p.m != 0 else "no", "", "|Y| ∝ sin^|m| θ"),
            ("Meridianos nodales del armónico complejo", "ninguno", "", "|Y|² no depende de φ"),
            ("Planos nodales de la combinación real", f"{abs(p.m)}", "", f"{2 * abs(p.m)} semiplanos"),
            ("Normalización ∫|Y|² sinθ dθ dφ (malla)", f"{val:.10f}", "", f"error de la regla del trapecio: {dev:.2e}"),
            ("Normalización (Gauss–Legendre)", f"{abs(integral_solapamiento(p.l, p.m, p.l, p.m)):.14f}", ""),
            ("Radio de la esfera", f"{p.radio / qc.obtener_unidades(p.sistema)['factor_longitud']:.6g}",
             qc.obtener_unidades(p.sistema)["nombre_longitud"]),
            ("Malla angular (θ × φ)", f"{p.n_theta} × {p.n_phi}", "puntos"),
            ("Función de SciPy calibrada", NOMBRE_BACKEND, ""),
        ]
        qc.tabla(filas, archivo=f"esfera_valores_l{p.l}_m{p.m}.csv")
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- **θ** es el ángulo **polar** (desde el eje z, 0 ≤ θ ≤ π); **φ** el **azimutal** (en el plano xy desde el eje x, "
            "0 ≤ φ < 2π). La antigua `scipy.special.sph_harm` los tenía intercambiados; este programa lo calibra y comprueba.\n"
            "- |Yₗᵐ|² es una **densidad de probabilidad angular** (por estereorradián): la probabilidad de encontrar la "
            "dirección (θ, φ) es |Y|² sinθ dθ dφ. **No** es una densidad volumétrica: no dice nada sobre la distancia r.\n"
            "- El color es el valor sobre una esfera de radio fijo R; la parte angular **no depende de R**.\n"
            "- Para m ≠ 0 complejo, |Y|² es simétrico respecto de z (anillo); la **fase** gira m veces al recorrer φ.\n"
            "- Los armónicos complejos con ±m dan la misma |Y|². Los orbitales reales (pₓ, p_y, d_xy…) son combinaciones "
            "lineales de Y^{+|m|} e Y^{−|m|}: misma energía (degeneración), distinta orientación.")


def _pestana_2d(p: ParametrosEsfera):
    c1, c2 = st.columns(2)
    phi0 = c1.slider("Corte a φ fijo [°]", 0.0, 360.0, step=5.0, key="esf_phi0")
    th0 = c2.slider("Corte a θ fijo [°]", 0.0, 180.0, step=5.0, key="esf_theta0")
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_proyeccion_2d(p, np.radians(phi0), np.radians(th0)), archivo=f"esfera_proyeccion_l{p.l}_m{p.m}.png")
    st.caption("Líneas discontinuas: nodos latitudinales (θ = cte). Líneas punteadas verticales: semiplanos nodales "
               "de las combinaciones reales. En esta proyección el área no es proporcional al ángulo sólido "
               "(las bandas cercanas a los polos están exageradas); por eso la normalización incluye el factor sinθ.")


@st.cache_data(show_spinner=False, max_entries=16)
def _cache_densidad_3d(l, m, real, radio, sistema):
    return figura_densidad_3d(l, m, real, radio, sistema)


def _pestana_densidad(p: ParametrosEsfera):
    """Criterio del curso: densidad de probabilidad (armónicos esféricos) frente a la posición en coordenadas cartesianas."""
    u = qc.obtener_unidades(p.sistema)
    L = u["nombre_longitud"]
    R = p.radio / u["factor_longitud"]
    st.latex(r"P=\frac{|Y_l^{m_l}(\theta,\varphi)|^{2}}{R^{2}}\qquad dA=R^{2}\sin\theta\,d\theta\,d\varphi")
    st.caption(f"Densidad de probabilidad P [{L}⁻²]: P·dA es la probabilidad de hallar la partícula en el área dA "
               "(interpretación de Born). Densidad angular |Yₗᵐ|² [sr⁻¹].")
    real = False
    if p.m != 0:
        real = st.toggle("Orbital real (±mₗ)", key="esf_dens_real", value=False,
                         help="Complejo: L_z definido y simetría axial. Real: mezcla +m y −m (pₓ, p_y, d_xy…).")
    try:
        qc.mostrar_plotly(_cache_densidad_3d(p.l, p.m, real, p.radio, p.sistema), "esf_fig_densidad3d",
                          archivo=f"esfera_densidad_l{p.l}_m{p.m}.html")
    except ValueError as error:
        qc.error(error)
        return
    qc.mostrar_pyplot(figura_densidad_cartesiana(p.l, p.m, real), archivo=f"esfera_densidad_cortes_l{p.l}_m{p.m}.png")
    qc.seccion("Punto (x, y, z)")
    c1, c2, c3 = st.columns(3)
    x = c1.number_input(f"x [{L}]", value=float(R * np.sqrt(0.5)), format="%.4g", key="esf_px")
    y = c2.number_input(f"y [{L}]", value=0.0, format="%.4g", key="esf_py")
    z = c3.number_input(f"z [{L}]", value=float(R * np.sqrt(0.5)), format="%.4g", key="esf_pz")
    try:
        d = densidad_en_punto(p.l, p.m, x, y, z, R, real)
    except ValueError as error:
        qc.error(error)
        return
    px, py, pz = d["punto_esfera"]
    qc.metricas([
        ("θ (polar)", f"{np.degrees(d['theta']):.4f}°"), ("φ (azimutal)", f"{np.degrees(d['phi']):.4f}°"),
        ("Densidad angular", f"{d['densidad_sr']:.6g} sr⁻¹"),
        ("Densidad de probabilidad P", f"{d['densidad_area']:.6g} {L}⁻²"),
    ])
    if abs(d["r"] - R) > 1e-9 * max(R, 1.0):
        st.caption(f"Fuera de la esfera: se usa su dirección, punto ({px:.4g}, {py:.4g}, {pz:.4g}) {L}.")
    if d["densidad_sr"] == 0:
        st.caption("Densidad nula: superficie nodal.")
    h, v, dens, t = curva_densidad_plano(p.l, p.m, "xz", real, n=361)
    theta = np.where(t <= np.pi, t, 2 * np.pi - t)
    phi = np.where(t <= np.pi, 0.0, np.pi)
    xs, ys, zs = esfericas_a_cartesianas(R, theta, phi)
    qc.exportar_datos({f"x [{L}]": xs, f"y [{L}]": ys, f"z [{L}]": zs, "theta [rad]": theta, "phi [rad]": phi,
                       "|Y|^2 [1/sr]": dens, f"|Y|^2/R^2 [1/{L}^2]": dens / R ** 2},
                      f"esfera_densidad_xz_l{p.l}_m{p.m}.csv", "Descargar la densidad a lo largo del plano xz (CSV)")


def _pestana_comparacion(p: ParametrosEsfera):
    opciones = [(l, m) for l in range(0, 4) for m in range(-l, l + 1)]
    with st.container(border=True):
        qc.seccion("Orbitales a comparar")
        c1, c2, c3 = st.columns([2, 1, 1])
        sel = c1.multiselect("Orbitales preseleccionados (máx. 6)", opciones, key="esf_comp_sel",
                             format_func=lambda t: f"l = {t[0]}, m = {t[1]}", max_selections=6)
        modo = c2.selectbox("Magnitud", ["densidad", "prob", "re", "real_cos"], key="esf_comp_modo", format_func=MODOS.get)
        forma = c3.selectbox("Forma", ["lobulos", "esfera"], key="esf_comp_forma", format_func=FORMAS.get)
        d1, d2, d3, _ = st.columns(4)
        usar = d1.toggle("Añadir un orbital propio", key="esf_comp_extra")
        estados = list(sel)
        if usar:
            l, m = _selector_lm("esf_comp", L_MAX, "Orbital propio · ", columnas=(d2, d3))
            if (l, m) not in estados:
                estados.append((l, m))
    estados = estados[:6]
    if not estados:
        qc.nota("Seleccionar al menos un orbital.")
        return
    qc.seccion("Visualización")
    try:
        qc.mostrar_plotly(_cache_comparacion(tuple(estados), modo, forma, p.mapa), "esf_comp_fig", archivo="esfera_comparacion.html")
    except ValueError as error:
        qc.error(error)
        return
    st.caption("Escala de color común para todos los paneles (un orbital con colores tenues tiene valores pequeños); "
               "la forma de los lóbulos está normalizada por orbital para comparar la orientación.")
    qc.seccion("Tabla comparativa")
    qc.tabla_libre([{"l": l, "m": m, "Tipo": letra(l), "Nodos latitudinales": len(nodos_latitud(l, m)),
                     "Superficies nodales (real)": l, "Paridad": "+" if l % 2 == 0 else "−", "L_z / ħ": m,
                     "L² / ħ²": l * (l + 1)} for l, m in estados],
                   numericas=("l", "m", "Nodos latitudinales", "Superficies nodales (real)", "L_z / ħ", "L² / ħ²"),
                   archivo="esfera_comparacion.csv")
    st.caption("Simetrías: los orbitales s son esféricos (sin nodos); los p tienen un plano nodal; los d, dos superficies "
               "nodales; en general l. El número de conos θ = cte es l − |m|. La paridad bajo r → −r es (−1)ˡ.")


def _pestana_complejo_real():
    c1, c2, _, _ = st.columns(4)
    l, m = _selector_lm("esf_cv", 6, "", columnas=(c1, c2))
    if l == 0:
        qc.nota("Para l = 0 no hay diferencia entre complejo y real.")
        return
    m = abs(m) or 1
    qc.seccion("Visualización")
    qc.mostrar_plotly(_cache_complejo_real(l, m), "esf_cv_fig", archivo=f"esfera_complejo_real_l{l}_m{m}.html")
    st.markdown(
        rf"- **Complejos** $Y_{{{l}}}^{{\pm {m}}}$: $|Y|^2$ es **idéntico** para $+m$ y $-m$ y no depende de $\varphi$ (simetría axial); "
        rf"lo que distingue a $+m$ de $-m$ es la **fase** $e^{{\pm i{m}\varphi}}$, es decir, el sentido de giro ($L_z=\pm {m}\hbar$)."
        "\n"
        rf"- **Reales**: $R_c=\sqrt2(-1)^m\,\mathrm{{Re}}\,Y^{{{m}}}\propto\cos({m}\varphi)$ y "
        rf"$R_s=\sqrt2(-1)^m\,\mathrm{{Im}}\,Y^{{{m}}}\propto\sin({m}\varphi)$. **Sí** dependen de $\varphi$, "
        f"tienen {m} planos nodales y signo (rojo/azul). No son autoestados de L_z (mezclan +{m} y −{m}) pero sí de L² y del mismo "
        "nivel de energía en cualquier potencial central.\n"
        "- Ambas bases describen **el mismo espacio** de estados; cambiar de una a otra es un cambio de base unitario.")


def _leer_confinada():
    sistema = st.session_state["esf_sistema"]
    u = qc.obtener_unidades(sistema)
    with st.container(border=True):
        qc.seccion("Parámetros del modelo confinado")
        c1, c2, c3, c4, c5 = st.columns(5)
        n = c1.number_input("n (radial)", 1, N_CONF_MAX, step=1, key="esf_c_n")
        l = c2.number_input("l", 0, L_CONF_MAX, step=1, key="esf_c_l")
        m = _campo_m(c3, "esf_c", int(l), "m")
        masa = c4.number_input("Masa [mₑ]", min_value=0.0, step=0.5, format="%.4g", key="esf_c_masa")
        radio = c5.number_input(f"Radio R [{u['nombre_longitud']}]", min_value=0.0, step=0.5, format="%.4g",
                                key="esf_c_radio")
    try:
        return validar_parametros_confinada(n, l, m, radio, masa, sistema)
    except ValueError as error:
        qc.error(error)
        return None


def _pestana_confinada():
    qc.nota("**Modelo opcional.** Partícula de masa m dentro de una esfera impenetrable (V = 0 para r < R, V = ∞ para "
            "r ≥ R). Aquí sí aparece la dependencia radial; la parte angular son los mismos armónicos Yₗᵐ.")
    pc = _leer_confinada()
    if pc is None:
        return
    d = calcular_confinada(pc)
    u = qc.obtener_unidades(pc.sistema)
    qc.seccion("Resultados")
    qc.metricas([
        (f"Energía del nivel {nombre_orbital(pc.n, pc.l)} [{u['nombre_energia']}]",
         qc.cientifico(d["energia"] / u["factor_energia"], 5), qc.texto_energia(d["energia"], pc.sistema)),
        (rf"$\alpha_{{{pc.n}{pc.l}}}$ (cero {pc.n} de $j_{{{pc.l}}}$)", f"{d['alfa']:.6f}"),
        ("Degeneración 2l + 1", f"{d['degeneracion']}"),
        ("Nodos radiales n − 1", f"{pc.n - 1}"),
        ("∫P(r) dr", f"{d['norma_radial']:.8f}"),
        (rf"$\langle r\rangle$ [{u['nombre_longitud']}]", qc.cientifico(d["r_medio"] / u["factor_longitud"], 5)),
        (r"$\langle r\rangle / R$", f"{d['r_medio'] / pc.radio:.5f}"),
        ("Energía [J]", qc.cientifico(d["energia"], 5)),
    ])
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_confinada(pc, d), archivo=f"esfera_confinada_{nombre_orbital(pc.n, pc.l)}.png")
    with st.expander("Interpretación física", expanded=True):
        st.markdown(
            "- **Cuantización:** ψ debe anularse en r = R ⇒ j_l(α) = 0 ⇒ α son los ceros de la función de Bessel "
            "esférica j_l. Para l = 0, α_n = nπ (como la caja 1D); para l ≥ 1 se calculan numéricamente.\n"
            "- **Densidades distintas:** |Y|² es angular (sr⁻¹) y vive sobre la esfera; |ψ|² = R²|Y|² es volumétrica "
            "(m⁻³); P(r) = r²R² es radial (m⁻¹). El corte muestra la volumétrica; por el factor r², P(r) se anula en "
            "el centro aunque |ψ|² de un estado s no lo haga.\n"
            "- Se grafica el armónico **complejo**: |ψ|² tiene simetría axial alrededor de z (corte idéntico para ±m).")


def interfaz() -> None:
    """Página completa del simulador 3 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 03", "Partícula en una esfera · armónicos esféricos",
                         "Armónicos Yₗᵐ sobre una esfera de radio fijo, sus nodos y simetrías, y el modelo opcional "
                         "de una partícula confinada en una esfera impenetrable.")
    qc.enlace_teoria("esfera")
    qc.ficha_simulador(
        "Visualizar los armónicos esféricos Yₗᵐ, sus nodos y simetrías, y la relación entre l, m y el momento angular.",
        r"\begin{gathered}\hat L^2 Y_l^m=\hbar^2\,l(l+1)\,Y_l^m\\[4pt]"
        r"\hat L_z Y_l^m=m\hbar\,Y_l^m,\quad |m|\le l\end{gathered}",
        [("l", "número cuántico de momento angular, entero ≥ 0"), ("m", "proyección, de −l a +l"),
         ("θ, φ", "ángulos polar y azimutal"), ("R", "radio, solo en el modelo opcional")],
        "Los Yₗᵐ son soluciones exactas. La partícula en una esfera impenetrable es un modelo opcional "
        "y se identifica como tal.")
    p = _leer_parametros()
    if p is None:
        return
    tabs = st.tabs(["Densidad de probabilidad", "Armónico 3D", "Proyección 2D y cortes", "Comparación de orbitales", "Complejos y reales",
                    "Partícula confinada", "Guía de práctica", "Autoevaluación", "Predice y experimenta", "Instrumentos e informe", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_densidad(p)
    with tabs[1]:
        _pestana_3d(p)
    with tabs[2]:
        _pestana_2d(p)
    with tabs[3]:
        _pestana_comparacion(p)
    with tabs[4]:
        _pestana_complejo_real()
    with tabs[5]:
        _pestana_confinada()
    with tabs[6]:
        qc.guia_practica(GUIA, "esf")
    with tabs[7]:
        qc.autoevaluacion(PREGUNTAS, "esf")
    with tabs[8]:
        _pestana_predice(p)
    with tabs[9]:
        _pestana_instrumentos(p)
    with tabs[10]:
        qc.boton_pruebas(ejecutar_pruebas, "esf_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Partícula en una esfera", ":material/science:", "particula_esfera.py")
