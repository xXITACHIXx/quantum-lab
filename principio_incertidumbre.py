"""
principio_incertidumbre.py — QUANTUM LAB · Simulador 06: principio de incertidumbre de Heisenberg
=================================================================================================

Un paquete de ondas ψ(x) y su distribución de momentos φ(p) son transformadas de Fourier una de la otra:

    φ(k) = (1/√2π) ∫ ψ(x) e^{−ikx} dx,      p = ħk

Por eso no pueden ser estrechas a la vez:  Δx·Δp ≥ ħ/2  (Kennard, 1927). Este simulador calcula Δx y Δp
NUMÉRICAMENTE (momentos de |ψ|² y de |φ|², con la transformada rápida de Fourier) para varios paquetes:

    gaussiano           ψ ∝ e^{−x²/4σ²} e^{ik₀x}                Δx·Δp = ħ/2        (el mínimo)
    gaussiano con chirp ψ ∝ e^{−(1−iβ)x²/4σ²} e^{ik₀x}          Δx·Δp = ħ/2·√(1+β²)
    triangular          ψ ∝ 1 − |x|/a  (|x| < a)                Δx·Δp = ħ·√(3/10)
    secante hiperbólica ψ ∝ sech(x/a)                           Δx·Δp = ħ·π/6
    dos gaussianas      ψ ∝ g(x − d/2) + g(x + d/2)             Δx grande, Δp casi como una sola

Además:
  * evolución libre: el paquete se ensancha, σ(t) = σ₀√(1 + 2βs + (1+β²)s²) con s = t/τ, τ = 2mσ₀²/ħ
    (Δp no cambia: la partícula libre conserva el momento); la forma en unidades de τ no depende de la masa;
  * difracción por una rendija: confinar la partícula en Δy ≈ a da Δp_y ≈ h/a (primer mínimo sin θ = λ/a).

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
M_E = const.m_e
U_ATOMICA = const.physical_constants["atomic mass constant"][0]
E_CARGA = const.e

TIPOS = {
    "gaussiano": "Gaussiano",
    "chirp": "Gaussiano con chirp",
    "triangular": "Triangular",
    "sech": "Secante hiperbólica",
    "dos": "Dos gaussianas",
}
MASAS = {
    "electron": ("Electrón", M_E),
    "proton": ("Protón", const.m_p),
    "rb87": ("Átomo de rubidio-87", 86.909180527 * U_ATOMICA),
    "c60": ("Molécula de C₆₀ (fulereno)", 720.0 * U_ATOMICA),
    "polvo": ("Grano de polvo (10⁻¹⁵ kg)", 1e-15),
}
ANCHO_MIN, ANCHO_MAX = 0.05, 10.0          # nm
K0_MAX = 30.0                               # nm⁻¹
BETA_MAX = 6.0
_N_MALLA = 2 ** 15


@dataclass(frozen=True)
class Paquete:
    tipo: str
    ancho: float          # σ (gaussianos) o a (triangular, sech)  [nm]
    k0: float             # número de onda central  [nm⁻¹]  (p₀ = ħk₀)
    beta: float = 0.0     # chirp (solo «chirp»)
    separacion: float = 0.0   # d (solo «dos»)  [nm]


def validar_paquete(tipo, ancho, k0, beta=0.0, separacion=0.0) -> Paquete:
    if tipo not in TIPOS:
        raise ValueError(f"Tipo de paquete desconocido: {tipo!r}.")
    ancho = qc.positivo_finito(ancho, "El ancho del paquete")
    if not ANCHO_MIN <= ancho <= ANCHO_MAX:
        raise ValueError(f"El ancho debe estar entre {ANCHO_MIN} y {ANCHO_MAX} nm (recibido: {ancho:g} nm).")
    try:
        k0, beta, separacion = float(k0), float(beta), float(separacion)
    except (TypeError, ValueError):
        raise ValueError("k₀, β y la separación deben ser números.")
    beta = beta if tipo == "chirp" else 0.0              # cada parámetro solo cuenta para su tipo de paquete
    separacion = separacion if tipo == "dos" else 0.0
    if not (np.isfinite(k0) and abs(k0) <= K0_MAX):
        raise ValueError(f"El número de onda central k₀ debe cumplir |k₀| ≤ {K0_MAX:g} nm⁻¹ (recibido: {k0:g}).")
    if not (np.isfinite(beta) and abs(beta) <= BETA_MAX):
        raise ValueError(f"El chirp β debe cumplir |β| ≤ {BETA_MAX:g} (recibido: {beta:g}).")
    if not (np.isfinite(separacion) and 0 <= separacion <= 40 * ancho):
        raise ValueError(f"La separación d debe estar entre 0 y 40 veces el ancho ({40 * ancho:g} nm); "
                         f"recibido: {separacion:g} nm.")
    return Paquete(tipo, ancho, k0, beta, separacion)


def funcion_onda(p: Paquete, x):
    """ψ(x) sin normalizar (x en nm)."""
    x = np.asarray(x, dtype=float)
    a = p.ancho
    if p.tipo == "gaussiano":
        env = np.exp(-x ** 2 / (4 * a ** 2)).astype(complex)
    elif p.tipo == "chirp":
        env = np.exp(-(1 - 1j * p.beta) * x ** 2 / (4 * a ** 2))
    elif p.tipo == "triangular":
        env = np.clip(1 - np.abs(x) / a, 0, None).astype(complex)
    elif p.tipo == "sech":
        env = (1.0 / np.cosh(np.clip(x / a, -700, 700))).astype(complex)
    else:  # dos gaussianas
        d = p.separacion
        env = (np.exp(-(x - d / 2) ** 2 / (4 * a ** 2)) + np.exp(-(x + d / 2) ** 2 / (4 * a ** 2))).astype(complex)
    return env * np.exp(1j * p.k0 * x)


def _malla(p: Paquete, extension: float = 0.0, paso: float | None = None, n_max: int = 2 ** 17):
    """Malla simétrica en x [nm]: cubre el paquete con holgura y resuelve sus oscilaciones."""
    dx = paso if paso is not None else p.ancho / 400.0
    semi = max(41 * p.ancho, 0.5 * p.separacion + 12 * p.ancho) + extension
    n = int(2 ** np.ceil(np.log2(max(2 * semi / dx, 1024))))
    n = min(n, n_max)
    dx = 2 * semi / n
    return -semi + dx * np.arange(n)


def _a_momentos(x, psi):
    """φ(k) con la convención unitaria φ(k) = (1/√2π) ∫ψ e^{−ikx} dx, ordenada de k negativo a positivo."""
    dx = x[1] - x[0]
    k = 2 * np.pi * np.fft.fftfreq(len(x), dx)
    phi = dx / np.sqrt(2 * np.pi) * np.fft.fft(psi) * np.exp(-1j * k * x[0])
    orden = np.argsort(k)
    return k[orden], phi[orden]


def _momentos(x, densidad):
    dx = x[1] - x[0]
    norma = float(np.sum(densidad) * dx)
    medio = float(np.sum(x * densidad) * dx / norma)
    var = float(np.sum((x - medio) ** 2 * densidad) * dx / norma)
    return norma, medio, np.sqrt(max(var, 0.0))


def calcular_paquete(p: Paquete) -> dict:
    """ψ y φ normalizadas, Δx y Δk (Δp = ħΔk) calculados numéricamente, y el producto Δx·Δp en unidades de ħ."""
    x = _malla(p)
    psi = funcion_onda(p, x)
    dx = x[1] - x[0]
    psi = psi / np.sqrt(np.sum(np.abs(psi) ** 2) * dx)
    k, phi = _a_momentos(x, psi)
    _, x_medio, dx_ = _momentos(x, np.abs(psi) ** 2)
    norma_k, k_medio, dk_ = _momentos(k, np.abs(phi) ** 2)
    # Δk también a partir de la derivada: ⟨k²⟩ = ∫|ψ'|² dx (control independiente de la FFT). Se deriva la
    # envolvente ψ·e^{−ik₀x}, que no oscila (Δk no cambia al desplazar k), para que la diferencia finita sea precisa.
    envolvente = psi * np.exp(-1j * p.k0 * x)
    k2_deriv = float(np.sum(np.abs(np.gradient(envolvente, dx)) ** 2) * dx)
    return {"x": x, "psi": psi, "k": k, "phi": phi, "x_medio": x_medio, "delta_x": dx_, "k_medio": k_medio,
            "delta_k": dk_, "producto": dx_ * dk_, "norma_k": norma_k,
            "delta_k_derivada": np.sqrt(max(k2_deriv - (k_medio - p.k0) ** 2, 0.0))}


def producto_teorico(p: Paquete) -> float | None:
    """Δx·Δp/ħ exacto (fórmula cerrada) para cada tipo de paquete."""
    if p.tipo == "gaussiano":
        return 0.5
    if p.tipo == "chirp":
        return 0.5 * np.sqrt(1 + p.beta ** 2)
    if p.tipo == "triangular":
        return float(np.sqrt(3 / 10))
    if p.tipo == "sech":
        return float(np.pi / 6)
    return float(np.prod(incertidumbres_dos_gaussianas(p.ancho, p.separacion)))


def incertidumbres_dos_gaussianas(sigma: float, d: float) -> tuple[float, float]:
    """Δx y Δk exactos para ψ ∝ g(x − d/2) + g(x + d/2) (incluye el solapamiento q = e^{−d²/8σ²})."""
    q = np.exp(-d ** 2 / (8 * sigma ** 2))
    x2 = (sigma ** 2 + d ** 2 / 4 + q * sigma ** 2) / (1 + q)
    sk2 = 1 / (4 * sigma ** 2)
    k2 = (sk2 + (sk2 - sk2 ** 2 * d ** 2) * q) / (1 + q)
    return float(np.sqrt(x2)), float(np.sqrt(k2))


def tiempo_caracteristico(ancho_nm: float, masa_kg: float) -> float:
    """τ = 2mσ₀²/ħ  [s]: en t = τ un paquete gaussiano sin chirp se ensancha en un factor √2."""
    return 2 * masa_kg * (ancho_nm * 1e-9) ** 2 / HBAR


def sigma_libre_gaussiana(sigma0: float, beta: float, s):
    """σ(t) de un gaussiano libre con chirp β, con s = t/τ:  σ₀√(1 + 2βs + (1+β²)s²)."""
    s = np.asarray(s, dtype=float)
    return sigma0 * np.sqrt(1 + 2 * beta * s + (1 + beta ** 2) * s ** 2)


def evolucionar(p: Paquete, s_valores) -> dict:
    """
    Evolución libre exacta en el espacio de momentos: φ(k, t) = φ(k, 0)·e^{−iħk²t/2m}.
    Con t = s·τ y τ = 2m·ancho²/ħ, la fase vale k²·ancho²·s: en unidades de τ el resultado NO depende de la masa.
    """
    s_valores = np.atleast_1d(np.asarray(s_valores, dtype=float))
    s_max = float(np.max(np.abs(s_valores)))
    d0 = calcular_paquete(p)
    desplazamiento = 2 * abs(p.k0) * p.ancho ** 2 * s_max
    ensanche = d0["delta_x"] + 2 * p.ancho ** 2 * d0["delta_k"] * s_max
    x = _malla(p, extension=desplazamiento + 7 * ensanche, paso=p.ancho / 60.0)
    dx = x[1] - x[0]
    psi0 = funcion_onda(p, x)
    psi0 = psi0 / np.sqrt(np.sum(np.abs(psi0) ** 2) * dx)
    k = 2 * np.pi * np.fft.fftfreq(len(x), dx)
    phi0 = np.fft.fft(psi0)
    densidades, x_medios, deltas_x, deltas_k, normas = [], [], [], [], []
    for s in s_valores:
        psi = np.fft.ifft(phi0 * np.exp(-1j * k ** 2 * p.ancho ** 2 * s))
        dens = np.abs(psi) ** 2
        norma, xm, dxs = _momentos(x, dens)
        kk, ph = _a_momentos(x, psi)
        _, _, dks = _momentos(kk, np.abs(ph) ** 2)
        densidades.append(dens)
        x_medios.append(xm); deltas_x.append(dxs); deltas_k.append(dks); normas.append(norma)
    return {"x": x, "s": s_valores, "densidades": np.array(densidades), "x_medio": np.array(x_medios),
            "delta_x": np.array(deltas_x), "delta_k": np.array(deltas_k), "normas": np.array(normas),
            "velocidad_nm_por_tau": 2 * p.k0 * p.ancho ** 2}


# ---------------------------------------------------------------------
# Difracción por una rendija
# ---------------------------------------------------------------------
PARTICULAS_RENDIJA = {"foton": "Fotón (luz)", "electron": "Electrón"}


@dataclass(frozen=True)
class Rendija:
    particula: str
    longitud_onda_nm: float
    ancho_nm: float
    distancia_m: float


def longitud_onda_electron_nm(energia_ev: float) -> float:
    """λ = h/√(2mₑE) (no relativista)  [nm]."""
    return H / np.sqrt(2 * M_E * energia_ev * E_CARGA) * 1e9


def validar_rendija(particula, valor, ancho_nm, distancia_m) -> Rendija:
    if particula not in PARTICULAS_RENDIJA:
        raise ValueError(f"Partícula desconocida: {particula!r}.")
    if particula == "foton":
        lam = qc.positivo_finito(valor, "La longitud de onda")
    else:
        energia = qc.positivo_finito(valor, "La energía del electrón")
        if energia > 1e5:
            raise ValueError("La energía del electrón debe ser ≤ 100 keV (el cálculo es no relativista).")
        lam = longitud_onda_electron_nm(energia)
    a = qc.positivo_finito(ancho_nm, "El ancho de la rendija")
    L = qc.positivo_finito(distancia_m, "La distancia a la pantalla")
    return Rendija(particula, lam, a, L)


def intensidad_rendija(sen_theta, ancho_nm: float, lam_nm: float):
    """Fraunhofer: I/I₀ = sinc²(πa·sinθ/λ)."""
    return np.sinc(ancho_nm * np.asarray(sen_theta, dtype=float) / lam_nm) ** 2


def intensidad_rendija_numerica(sen_theta, ancho_nm: float, lam_nm: float, fuentes: int = 4001):
    """Misma intensidad sumando ondas de Huygens desde `fuentes` puntos de la rendija (control independiente)."""
    y = np.linspace(-ancho_nm / 2, ancho_nm / 2, fuentes)
    fase = -2j * np.pi / lam_nm * np.outer(np.atleast_1d(sen_theta), y)
    campo = (getattr(np, "trapezoid", None) or np.trapz)(np.exp(fase), y, axis=1) / ancho_nm
    return np.abs(campo) ** 2


def calcular_rendija(r: Rendija) -> dict:
    p = H / (r.longitud_onda_nm * 1e-9)
    hay_minimo = r.longitud_onda_nm < r.ancho_nm
    sen1 = r.longitud_onda_nm / r.ancho_nm if hay_minimo else None
    theta1 = float(np.arcsin(sen1)) if hay_minimo else None
    y1 = r.distancia_m * np.tan(theta1) if hay_minimo else None
    return {"p": p, "hay_minimo": hay_minimo, "sen1": sen1, "theta1": theta1, "y1_m": y1,
            "dpy": p * sen1 if hay_minimo else None, "h_sobre_a": H / (r.ancho_nm * 1e-9),
            "producto_h": (r.ancho_nm * 1e-9) * p * sen1 / H if hay_minimo else None}


def ejemplos_escala() -> list[dict]:
    """Mínima incertidumbre en la velocidad, Δv = ħ/(2mΔx), para objetos de distintas escalas."""
    casos = [("Electrón en un átomo", M_E, 0.05e-9, "Δx ≈ radio de Bohr"),
             ("Protón en un núcleo", const.m_p, 1e-15, "Δx ≈ 1 fm"),
             ("Átomo de rubidio en una trampa óptica", 86.909 * U_ATOMICA, 1e-6, "Δx ≈ 1 µm"),
             ("Grano de polvo (10⁻¹⁵ kg)", 1e-15, 1e-6, "Δx ≈ 1 µm"),
             ("Pelota de béisbol (0.145 kg)", 0.145, 1e-3, "Δx ≈ 1 mm")]
    filas = []
    for nombre, m, dx, nota in casos:
        dp = HBAR / (2 * dx)
        dv = dp / m
        filas.append({"nombre": nombre, "masa": m, "dx": dx, "dp": dp, "dv": dv, "energia_ev": dp ** 2 / (2 * m) / E_CARGA,
                      "nota": nota})
    return filas


def texto_tiempo(t: float) -> str:
    """Tiempo en la unidad más legible (as … años)."""
    unidades = [(3.156e7, "años"), (86400, "días"), (3600, "h"), (1, "s"), (1e-3, "ms"), (1e-6, "µs"),
                (1e-9, "ns"), (1e-12, "ps"), (1e-15, "fs"), (1e-18, "as")]
    for factor, nombre in unidades:
        if abs(t) >= factor:
            return f"{t / factor:.3g} {nombre}"
    return f"{t:.3g} s"


# =====================================================================
# 2. FIGURAS
# =====================================================================
def _remuestrear(x, y, x0, x1, puntos=450):
    xs = np.linspace(x0, x1, puntos)
    return xs.astype(np.float32), np.interp(xs, x, y).astype(np.float32)


def figura_compresion(p: Paquete, compacto: bool = False):
    """
    Figura interactiva (Plotly): el deslizador cambia el ancho del paquete; a la izquierda |ψ(x)|² y a la derecha
    |φ(p)|². Los ejes están FIJOS para que se vea que, al estrechar uno, el otro se ensancha.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    lo, hi = max(ANCHO_MIN, 0.25 * p.ancho), min(ANCHO_MAX, 4.0 * p.ancho)
    anchos = np.unique(np.round(np.concatenate([np.geomspace(lo, hi, 21), [p.ancho]]), 6))
    activo = int(np.argmin(np.abs(anchos - p.ancho)))
    calculos = []
    for w in anchos:
        try:
            q = validar_paquete(p.tipo, w, p.k0, p.beta, min(p.separacion, 40 * w))
        except ValueError:
            continue
        calculos.append((w, calcular_paquete(q)))
    dx_max = max(c["delta_x"] for _, c in calculos)
    dk_max = max(c["delta_k"] for _, c in calculos)
    x_lim = 3.0 * dx_max
    k0_ = calculos[0][1]["k_medio"]
    k_lim = (k0_ - 3.0 * dk_max, k0_ + 3.0 * dk_max)
    filas, cols = (2, 1) if compacto else (1, 2)
    fig = make_subplots(rows=filas, cols=cols, horizontal_spacing=0.08, vertical_spacing=0.16,
                        subplot_titles=("Posición: |ψ(x)|²", "Momento: |φ(p)|²"))
    pos2 = (2, 1) if compacto else (1, 2)

    def trazas(c):
        xs, dens = _remuestrear(c["x"], np.abs(c["psi"]) ** 2, -x_lim, x_lim)
        _, re = _remuestrear(c["x"], c["psi"].real, -x_lim, x_lim)
        escala = dens.max() / max(np.abs(c["psi"]).max(), 1e-300)
        ks, dk = _remuestrear(c["k"], np.abs(c["phi"]) ** 2, *k_lim)
        xm, sx, km, sk = c["x_medio"], c["delta_x"], c["k_medio"], c["delta_k"]
        return [
            go.Scatter(x=xs, y=dens, mode="lines", fill="tozeroy", line=dict(color=COLORES["densidad"], width=2.4),
                       fillcolor="rgba(255,176,0,0.25)", name="|ψ(x)|²", hovertemplate="x=%{x:.3f} nm<extra></extra>"),
            go.Scatter(x=xs, y=re * escala, mode="lines", line=dict(color=COLORES["onda"], width=1), opacity=0.55,
                       name="Re ψ (escala arbitraria)", hoverinfo="skip"),
            go.Scatter(x=[xm - sx, xm - sx, None, xm + sx, xm + sx], y=[0, dens.max(), None, 0, dens.max()], mode="lines",
                       line=dict(color="white", width=1.4, dash="dot"), name="⟨x⟩ ± Δx", hoverinfo="skip"),
            go.Scatter(x=ks, y=dk, mode="lines", fill="tozeroy", line=dict(color=COLORES["potencial"], width=2.4),
                       fillcolor="rgba(139,92,246,0.28)", name="|φ(p)|²", hovertemplate="p=%{x:.3f} ħ/nm<extra></extra>"),
            go.Scatter(x=[km - sk, km - sk, None, km + sk, km + sk], y=[0, dk.max(), None, 0, dk.max()], mode="lines",
                       line=dict(color="white", width=1.4, dash="dot"), name="⟨p⟩ ± Δp", hoverinfo="skip", showlegend=False),
        ], dens.max(), dk.max(), min(0.0, float(np.min(re * escala)))

    def texto(w, c):
        if compacto:
            return (f"Δx = {c['delta_x']:.3f} nm  ·  Δp = {c['delta_k']:.3f} ħ/nm<br>"
                    f"Δx·Δp = {c['producto']:.4f} ħ  (mínimo 0.5 ħ)")
        return (f"ancho = {w:.3g} nm   ·   Δx = {c['delta_x']:.3f} nm   ·   Δp = {c['delta_k']:.3f} ħ/nm   ·   "
                f"Δx·Δp = {c['producto']:.4f} ħ  (mínimo 0.5 ħ)")

    def anotacion(w, c):
        return [dict(text=texto(w, c), x=0.5, y=1.13 if not compacto else 1.17, xref="paper", yref="paper",
                     showarrow=False, font=dict(size=13, color="white", family=qc.FUENTE_CIFRAS))]

    marcos = []
    idx_activo = 0
    for i, (w, c) in enumerate(calculos):
        tr, ymx, ymk, ymn = trazas(c)
        lay = {"yaxis.range": [1.08 * ymn, 1.08 * ymx], "yaxis2.range": [0, 1.08 * ymk]}
        marcos.append(go.Frame(data=tr, name=f"w{i}", layout=dict(
            annotations=list(fig.layout.annotations[:2]) + anotacion(w, c),
            yaxis=dict(range=lay["yaxis.range"]), yaxis2=dict(range=lay["yaxis2.range"]))))
        if abs(w - p.ancho) < 1e-9:
            idx_activo = i
    tr, ymx, ymk, ymn = trazas(calculos[idx_activo][1])
    for j, t in enumerate(tr):
        fila, col = (1, 1) if j < 3 else pos2
        fig.add_trace(t, row=fila, col=col)
    fig.frames = marcos
    altura = 760 if compacto else 560
    qc.aplicar_tema_plotly(fig, None, altura=altura)
    fig.update_layout(annotations=list(fig.layout.annotations[:2]) + anotacion(*calculos[idx_activo]),
                      legend=dict(orientation="h", y=-0.13, x=0), showlegend=not compacto,
                      margin=dict(t=140 if compacto else 90))
    fig.update_xaxes(range=[-x_lim, x_lim], title_text="x [nm]", row=1, col=1)
    fig.update_xaxes(range=list(k_lim), title_text="p [ħ/nm]", row=pos2[0], col=pos2[1])
    fig.update_yaxes(range=[1.08 * ymn, 1.08 * ymx], title_text="densidad [1/nm]", row=1, col=1)
    fig.update_yaxes(range=[0, 1.08 * ymk], title_text="densidad [nm/ħ]", row=pos2[0], col=pos2[1])
    fig.update_layout(sliders=[dict(
        active=idx_activo, x=0.025, len=0.95, y=-0.2 if not compacto else -0.12, yanchor="top",
        currentvalue=dict(prefix="ancho del paquete: ", suffix=" nm", font=dict(size=12, family=qc.FUENTE_CIFRAS)),
        pad=dict(t=10), bgcolor="#1A2342", bordercolor=COLORES["rejilla"], activebgcolor=COLORES["onda"],
        tickcolor=COLORES["gris"], font=dict(size=10, color=COLORES["gris"]),
        steps=[dict(label=f"{w:.3g}", method="animate",
                    args=[[f"w{i}"], dict(frame=dict(duration=0, redraw=True), transition=dict(duration=0),
                                          mode="immediate")]) for i, (w, _) in enumerate(calculos)])])
    fig.update_layout(margin=dict(b=150 if not compacto else 130))
    return fig


def figura_relacion(p: Paquete):
    """Plano Δx–Δp con la región prohibida, los cinco tipos de paquete y el producto de cada uno."""
    fig, (ax, ax2) = qc.rejilla(1, 2, (14.5, 5.6), constrained_layout=True, gridspec_kw={"width_ratios": [1.15, 1]})
    dxs = np.geomspace(p.ancho / 40, p.ancho * 60, 300)
    ax.fill_between(dxs, 1e-9, 0.5 / dxs, color=COLORES["energia"], alpha=0.16, label="prohibido: Δx·Δp < ħ/2")
    ax.plot(dxs, 0.5 / dxs, color=COLORES["energia"], lw=2.2, label="Δx·Δp = ħ/2 (gaussiano)")
    for f, ls in ((1, "--"), (3, ":")):
        ax.plot(dxs, f / dxs, color=COLORES["gris"], lw=1, ls=ls, alpha=0.7, label=f"Δx·Δp = {f} ħ")
    resultados = []
    colores = [COLORES["densidad"], COLORES["onda"], COLORES["cinetica"], COLORES["potencial"], COLORES["interferencia"]]
    for (tipo, nombre), col in zip(TIPOS.items(), colores):
        q = validar_paquete(tipo, p.ancho, p.k0, p.beta if tipo == "chirp" else 0.0,
                            p.separacion if tipo == "dos" else 0.0)
        if tipo == "chirp" and q.beta == 0:
            q = validar_paquete(tipo, p.ancho, p.k0, 2.0)
        if tipo == "dos" and q.separacion == 0:
            q = validar_paquete(tipo, p.ancho, p.k0, 0.0, 6 * p.ancho)
        c = calcular_paquete(q)
        resultados.append((tipo, nombre, c, col, q))
        actual = tipo == p.tipo
        ax.plot(c["delta_x"], c["delta_k"], "o", ms=13 if actual else 8, color=col,
                mec="white" if actual else col, mew=2 if actual else 0, zorder=5)
        desplaz = {"gaussiano": (-14, -16), "chirp": (10, 6), "triangular": (-12, 10), "sech": (-12, 8),
                   "dos": (10, 4)}[tipo]
        ax.annotate(nombre, (c["delta_x"], c["delta_k"]), xytext=desplaz, textcoords="offset points",
                    fontsize=9.5, color=col, ha="right" if desplaz[0] < 0 else "left")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(dxs[0], dxs[-1]); ax.set_ylim(0.5 / dxs[-1], 0.5 / dxs[0] * 3)
    ax.set_xlabel("Δx [nm]"); ax.set_ylabel("Δp [ħ/nm]")
    ax.set_title(f"Plano de incertidumbres (ancho = {p.ancho:g} nm)")
    ax.legend(loc="upper right", fontsize=8.5)
    ax.grid(alpha=0.25, which="both")
    nombres = [n + ("\n(β = %g)" % q.beta if t == "chirp" else "\n(d = %g nm)" % q.separacion if t == "dos" else "")
               for t, n, _, _, q in resultados]
    valores = [c["producto"] for _, _, c, _, _ in resultados]
    barras = ax2.barh(range(len(valores)), valores, color=[c for *_, c, _ in resultados], alpha=0.85)
    for b, v, (t, *_rest) in zip(barras, valores, resultados):
        ax2.text(v + 0.03, b.get_y() + b.get_height() / 2, f"{v:.4f} ħ", va="center", fontsize=10,
                 fontweight="bold" if t == p.tipo else "normal")
    ax2.axvline(0.5, color=COLORES["energia"], lw=2, label="límite ħ/2")
    ax2.set_yticks(range(len(valores)), nombres, fontsize=9)
    ax2.invert_yaxis()
    ax2.set_xlim(0, max(valores) * 1.3)
    ax2.set_xlabel("Δx·Δp [ħ]")
    ax2.set_title("Producto de incertidumbres de cada paquete")
    ax2.legend(loc="lower right", fontsize=9)
    ax2.grid(alpha=0.25, axis="x")
    ax2.set_axisbelow(True)
    return fig


def figura_evolucion(p: Paquete, ev: dict, tau_s: float, masa_nombre: str, compacto: bool = False):
    """Animación (Plotly) de |ψ(x, t)|² en la evolución libre."""
    import plotly.graph_objects as go
    x = ev["x"]
    lo = float(np.min(ev["x_medio"] - 3.8 * ev["delta_x"]))
    hi = float(np.max(ev["x_medio"] + 3.8 * ev["delta_x"]))
    ymax = float(ev["densidades"].max()) * 1.08
    analitica = p.tipo in ("gaussiano", "chirp")

    def traza(i):
        xs, ds = _remuestrear(x, ev["densidades"][i], lo, hi, 800)
        return go.Scatter(x=xs, y=ds, mode="lines", fill="tozeroy", line=dict(color=COLORES["densidad"], width=2.4),
                          fillcolor="rgba(255,176,0,0.25)", name="|ψ(x, t)|²", hovertemplate="x=%{x:.2f} nm<extra></extra>")

    def banda(i):
        xm, sx = ev["x_medio"][i], ev["delta_x"][i]
        return go.Scatter(x=[xm - sx, xm - sx, None, xm + sx, xm + sx], y=[0, ymax * 0.9, None, 0, ymax * 0.9],
                          mode="lines", line=dict(color="white", width=1.4, dash="dot"), name="⟨x⟩ ± Δx", hoverinfo="skip")

    def texto(i):
        s = ev["s"][i]
        sep = "<br>" if compacto else "   ·   "
        return (f"t = {s:.2f} τ = {texto_tiempo(s * tau_s)}   ·   Δx = {ev['delta_x'][i]:.3f} nm{sep}"
                f"Δp = {ev['delta_k'][i]:.3f} ħ/nm (constante)   ·   Δx·Δp = {ev['delta_x'][i] * ev['delta_k'][i]:.3f} ħ")

    inicial = go.Scatter(x=_remuestrear(x, ev["densidades"][0], lo, hi, 800)[0],
                         y=_remuestrear(x, ev["densidades"][0], lo, hi, 800)[1], mode="lines",
                         line=dict(color=COLORES["gris"], width=1.2, dash="dash"), name="t = 0", hoverinfo="skip")
    fig = go.Figure(data=[inicial, traza(0), banda(0)])
    fig.frames = [go.Frame(data=[traza(i), banda(i)], traces=[1, 2], name=f"t{i}",
                           layout=dict(annotations=[dict(text=texto(i), x=0.5, y=1.07, xref="paper", yref="paper",
                                                         showarrow=False, font=dict(size=12, color="white",
                                                                                    family=qc.FUENTE_CIFRAS))]))
                  for i in range(len(ev["s"]))]
    qc.aplicar_tema_plotly(fig, None, altura=520 if compacto else 560)
    fig.update_layout(xaxis=dict(range=[lo, hi], title="x [nm]"), yaxis=dict(range=[0, ymax], title="densidad [1/nm]"),
                      annotations=[dict(text=texto(0), x=0.5, y=1.07, xref="paper", yref="paper", showarrow=False,
                                        font=dict(size=12, color="white", family=qc.FUENTE_CIFRAS))],
                      legend=dict(orientation="h", y=1.18, x=0), margin=dict(t=95))
    qc.agregar_animacion(fig, [f"t{i}" for i in range(len(ev["s"]))], [f"{s:.2f} τ" for s in ev["s"]], duracion_ms=80)
    return fig


def figura_anchura(p: Paquete, ev: dict, tau_s: float):
    """Δx(t) numérico (y analítico en los gaussianos), Δp(t) y el producto."""
    fig, (ax, ax2) = qc.rejilla(1, 2, (14, 4.8), constrained_layout=True)
    s = ev["s"]
    ax.plot(s, ev["delta_x"], color=COLORES["densidad"], lw=2.6, label="Δx(t) numérico")
    if p.tipo in ("gaussiano", "chirp"):
        ax.plot(s, sigma_libre_gaussiana(p.ancho, p.beta, s), color="white", ls="--", lw=1.4,
                label="σ₀√(1 + 2βs + (1+β²)s²)")
    ax.set_xlabel("tiempo t/τ")
    ax.set_ylabel("Δx [nm]")
    ax.set_title(f"Ensanchamiento del paquete (τ = {texto_tiempo(tau_s)})")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax2.plot(s, ev["delta_x"] * ev["delta_k"], color=COLORES["onda"], lw=2.6, label="Δx·Δp(t)")
    ax2.plot(s, ev["delta_k"] * ev["delta_x"][0], color=COLORES["potencial"], lw=1.5, ls=":",
             label="Δp·Δx(0): Δp no cambia")
    ax2.axhline(0.5, color=COLORES["energia"], lw=1.6, label="ħ/2")
    ax2.set_xlabel("tiempo t/τ")
    ax2.set_ylabel("[ħ]")
    ax2.set_ylim(0, max(1.0, float(np.max(ev["delta_x"] * ev["delta_k"])) * 1.1))
    ax2.set_title("Producto de incertidumbres en el tiempo")
    ax2.legend(fontsize=9)
    ax2.grid(alpha=0.3)
    return fig


def figura_rendija(r: Rendija, d: dict):
    """Patrón en la pantalla y anchura angular del máximo central frente al ancho de la rendija."""
    fig, (ax, ax2) = qc.rejilla(1, 2, (14, 5.2), constrained_layout=True)
    if d["hay_minimo"]:
        y_lim = 3.2 * d["y1_m"]
        th_lim = np.arctan(y_lim / r.distancia_m)
    else:
        th_lim = np.pi / 2 * 0.999
        y_lim = r.distancia_m * np.tan(th_lim)
    th = np.linspace(-th_lim, th_lim, 2001)
    y = r.distancia_m * np.tan(th)
    escala, unidad = (1e3, "mm") if y_lim < 2 else (1, "m")
    I = intensidad_rendija(np.sin(th), r.ancho_nm, r.longitud_onda_nm)
    color = qc.color_longitud_onda(r.longitud_onda_nm, fuera=COLORES["onda"]) if r.particula == "foton" else COLORES["onda"]
    ax.fill_between(y * escala, I, color=color, alpha=0.3)
    ax.plot(y * escala, I, color=color, lw=2.2, label="intensidad (Fraunhofer)")
    if d["hay_minimo"]:
        for sgn in (-1, 1):
            ax.axvline(sgn * d["y1_m"] * escala, color="white", ls="--", lw=1.2)
        ax.annotate("", xy=(d["y1_m"] * escala, 0.55), xytext=(-d["y1_m"] * escala, 0.55),
                    arrowprops=dict(arrowstyle="<->", color="white", lw=1.4))
        ax.text(0, 0.6, f"máximo central: {2 * d['y1_m'] * escala:.3g} {unidad}", ha="center", color="white", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", fc=COLORES["fondo"], ec=COLORES["rejilla"], alpha=0.9))
    ax.set_xlabel(f"posición en la pantalla y [{unidad}]")
    ax.set_ylabel("intensidad relativa I/I₀")
    ancho_txt = f"{r.ancho_nm / 1000:.3g} µm" if r.ancho_nm >= 1000 else f"{r.ancho_nm:.3g} nm"
    ax.set_title(f"Patrón a {r.distancia_m:g} m de una rendija de {ancho_txt} (λ = {r.longitud_onda_nm:.4g} nm)")
    ax.set_ylim(0, 1.08)
    ax.grid(alpha=0.3)
    anchos = np.geomspace(r.longitud_onda_nm * 1.02, r.longitud_onda_nm * 1e4, 300)
    ax2.plot(anchos, np.degrees(np.arcsin(r.longitud_onda_nm / anchos)), color=COLORES["densidad"], lw=2.4,
             label="θ₁ = arcsen(λ/a)")
    if d["hay_minimo"]:
        ax2.plot([r.ancho_nm], [np.degrees(d["theta1"])], "o", ms=11, color=COLORES["energia"], mec="white", mew=1.5,
                 label="rendija actual")
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel("ancho de la rendija a [nm]  (Δy ≈ a)")
    ax2.set_ylabel("ángulo del primer mínimo θ₁ [°]  (Δp_y ∝ sen θ₁)")
    ax2.set_title("Más estrecha la rendija → más se abre el haz")
    ax2.legend(fontsize=9)
    ax2.grid(alpha=0.25, which="both")
    return fig


# =====================================================================
# 3. PRUEBAS
# =====================================================================
def ejecutar_pruebas() -> qc.RegistroPruebas:
    r = qc.RegistroPruebas("Principio de incertidumbre")
    g = calcular_paquete(validar_paquete("gaussiano", 1.0, 0.0))
    r.comprobar("Gaussiano: Δx = σ", abs(g["delta_x"] - 1.0) < 1e-6, f"{g['delta_x']:.8f} nm")
    r.comprobar("Gaussiano: Δk = 1/(2σ)", abs(g["delta_k"] - 0.5) < 1e-6, f"{g['delta_k']:.8f} nm⁻¹")
    r.comprobar("Gaussiano: Δx·Δp = ħ/2 (el mínimo)", abs(g["producto"] - 0.5) < 1e-6, f"{g['producto']:.8f} ħ")
    r.comprobar("Parseval: ∫|φ|²dk = ∫|ψ|²dx = 1", abs(g["norma_k"] - 1) < 1e-10, f"{g['norma_k']:.12f}")
    gk = calcular_paquete(validar_paquete("gaussiano", 0.7, 8.0))
    r.comprobar("⟨p⟩ = ħk₀ (k₀ = 8 nm⁻¹)", abs(gk["k_medio"] - 8.0) < 1e-6, f"{gk['k_medio']:.8f} nm⁻¹")
    r.comprobar("k₀ no cambia el producto", abs(gk["producto"] - 0.5) < 1e-6)
    r.comprobar("Δk por FFT = Δk por derivada (control independiente)",
                abs(gk["delta_k"] - gk["delta_k_derivada"]) / gk["delta_k"] < 1e-4,
                f"{gk['delta_k']:.6f} / {gk['delta_k_derivada']:.6f}")
    for beta in (1.0, -2.5):
        c = calcular_paquete(validar_paquete("chirp", 0.8, 3.0, beta))
        r.comprobar(f"Chirp β = {beta:g}: Δx·Δp = ½√(1+β²)", abs(c["producto"] - 0.5 * np.sqrt(1 + beta ** 2)) < 1e-5,
                    f"{c['producto']:.6f} ħ")
    t = calcular_paquete(validar_paquete("triangular", 1.0, 0.0))
    r.comprobar("Triangular: Δx·Δp = √(3/10) ≈ 0.5477", abs(t["producto"] - np.sqrt(0.3)) < 2e-3, f"{t['producto']:.5f} ħ")
    s_ = calcular_paquete(validar_paquete("sech", 1.0, 0.0))
    r.comprobar("Secante hiperbólica: Δx·Δp = π/6 ≈ 0.5236", abs(s_["producto"] - np.pi / 6) < 1e-5, f"{s_['producto']:.6f} ħ")
    for dd in (2.0, 6.0):
        c = calcular_paquete(validar_paquete("dos", 1.0, 0.0, 0.0, dd))
        dx_t, dk_t = incertidumbres_dos_gaussianas(1.0, dd)
        r.comprobar(f"Dos gaussianas (d = {dd:g}σ): Δx y Δp numéricos = fórmula con solapamiento",
                    abs(c["delta_x"] - dx_t) < 1e-5 and abs(c["delta_k"] - dk_t) < 1e-5,
                    f"Δx·Δp = {c['producto']:.5f} ħ")
    rng = np.random.default_rng(3)
    minimo = min(calcular_paquete(validar_paquete(tp, rng.uniform(0.2, 3), rng.uniform(-10, 10), rng.uniform(-4, 4),
                                                  rng.uniform(0, 8)))["producto"] for tp in TIPOS for _ in range(3))
    r.comprobar("Ningún paquete viola Δx·Δp ≥ ħ/2 (15 paquetes al azar)", minimo >= 0.5 - 1e-6, f"mínimo {minimo:.6f} ħ")

    p = validar_paquete("gaussiano", 1.0, 5.0)
    ev = evolucionar(p, [0.0, 1.0, 2.0])
    r.comprobar("Evolución libre: σ(τ) = √2·σ₀", abs(ev["delta_x"][1] / np.sqrt(2) - 1.0) < 1e-4,
                f"{ev['delta_x'][1]:.6f} nm")
    r.comprobar("Evolución libre: σ(2τ) = √5·σ₀", abs(ev["delta_x"][2] - np.sqrt(5)) < 1e-4, f"{ev['delta_x'][2]:.6f} nm")
    r.comprobar("La norma se conserva", np.all(np.abs(ev["normas"] - 1) < 1e-9))
    r.comprobar("Δp se conserva (partícula libre)", np.ptp(ev["delta_k"]) < 1e-6)
    r.comprobar("⟨x⟩ avanza con la velocidad de grupo ħk₀/m", abs(ev["x_medio"][2] - 2 * ev["velocidad_nm_por_tau"]) < 1e-4,
                f"{ev['x_medio'][2]:.5f} nm en 2τ")
    pf = validar_paquete("chirp", 1.0, 0.0, -1.0)
    ev2 = evolucionar(pf, np.linspace(0, 1, 41))
    i = int(np.argmin(ev2["delta_x"]))
    r.comprobar("Chirp β = −1: el paquete se enfoca hasta σ₀/√2 en t = τ/2",
                abs(ev2["s"][i] - 0.5) < 1e-9 and abs(ev2["delta_x"][i] - 1 / np.sqrt(2)) < 1e-4,
                f"mínimo {ev2['delta_x'][i]:.5f} nm en t = {ev2['s'][i]:.3f} τ")
    tau = tiempo_caracteristico(1.0, M_E)
    r.comprobar("τ(electrón, σ₀ = 1 nm) = 2mσ₀²/ħ ≈ 17.3 fs", abs(tau / 1.7275e-14 - 1) < 1e-3, texto_tiempo(tau))

    rd = validar_rendija("foton", 500.0, 2000.0, 1.0)
    d = calcular_rendija(rd)
    r.comprobar("Rendija: primer mínimo en sen θ = λ/a", abs(d["sen1"] - 0.25) < 1e-12 and
                intensidad_rendija(d["sen1"], 2000.0, 500.0) < 1e-20)
    sen = np.linspace(-0.9, 0.9, 37)
    num = intensidad_rendija_numerica(sen, 2000.0, 500.0)
    r.comprobar("Suma de ondas de Huygens = sinc² (Fraunhofer)", np.max(np.abs(num - intensidad_rendija(sen, 2000.0, 500.0))) < 1e-6)
    r.comprobar("a·p·sen θ₁ = h (Δy·Δp_y ≈ h ≥ ħ/2)", abs(d["producto_h"] - 1) < 1e-12)
    r.comprobar("Electrón de 150.4 eV: λ = h/√(2mE) ≈ 0.1000 nm", abs(longitud_onda_electron_nm(150.412) - 0.1) < 1e-4,
                f"{longitud_onda_electron_nm(150.412):.5f} nm")
    ej = ejemplos_escala()
    r.comprobar("Protón confinado en 1 fm: energía cinética mínima del orden de MeV", 1e6 < ej[1]["energia_ev"] < 1e7,
                f"{ej[1]['energia_ev'] / 1e6:.2f} MeV")
    r.comprobar_error("Error: ancho negativo", validar_paquete, "gaussiano", -1, 0)
    r.comprobar_error("Error: tipo desconocido", validar_paquete, "cuadrado", 1, 0)
    r.comprobar_error("Error: separación excesiva", validar_paquete, "dos", 0.1, 0, 0, 50)
    r.comprobar_error("Error: chirp fuera de rango", validar_paquete, "chirp", 1, 0, 99)
    r.comprobar_error("Error: energía del electrón no válida", validar_rendija, "electron", "abc", 100, 1)
    r.comprobar("Rendija más estrecha que λ: no hay mínimos (se avisa, no falla)",
                not calcular_rendija(validar_rendija("foton", 600, 400, 1))["hay_minimo"])
    return r


# =====================================================================
# 4. INTERFAZ (Streamlit)
# =====================================================================
VALORES_INICIALES = {
    "inc_tipo": "gaussiano", "inc_ancho": 1.0, "inc_k0": 5.0, "inc_beta": 2.0, "inc_sep": 6.0,
    "inc_masa": "electron", "inc_smax": 3.0,
    "inc_ren_particula": "foton", "inc_ren_lambda": 532.0, "inc_ren_energia": 50.0, "inc_ren_ancho": 20000.0,
    "inc_ren_distancia": 1.0,
}
DEMOS = {
    "Gaussiano: el mínimo exacto ħ/2": {"inc_tipo": "gaussiano", "inc_ancho": 1.0, "inc_k0": 5.0},
    "Paquete muy estrecho (0.2 nm)": {"inc_tipo": "gaussiano", "inc_ancho": 0.2, "inc_k0": 5.0},
    "Chirp β = 3: mismo Δx, más Δp": {"inc_tipo": "chirp", "inc_ancho": 1.0, "inc_beta": 3.0},
    "Chirp β = −2: el paquete se enfoca": {"inc_tipo": "chirp", "inc_ancho": 1.0, "inc_beta": -2.0, "inc_k0": 0.0},
    "Dos gaussianas: «gato» cuántico": {"inc_tipo": "dos", "inc_ancho": 0.6, "inc_sep": 6.0, "inc_k0": 0.0},
    "Triangular": {"inc_tipo": "triangular", "inc_ancho": 1.5, "inc_k0": 0.0},
}

GUIA = [
    {"titulo": "Comprimir un paquete",
     "objetivo": "Comprobar que estrechar el paquete en x lo ensancha en p.",
     "pasos": ["Carga la configuración (gaussiano de 1 nm).", "En la figura interactiva mueve el deslizador del ancho "
               "hacia la izquierda y hacia la derecha.", "Anota Δx, Δp y su producto para tres anchos distintos."],
     "pregunta": "Si reduces Δx a la mitad, ¿qué le pasa a Δp? ¿Y al producto?",
     "resultado": "Δp se duplica y el producto se mantiene exactamente en 0.5 ħ: el gaussiano es el paquete de "
                  "mínima incertidumbre para cualquier ancho. Las curvas de x y p son transformadas de Fourier una de "
                  "la otra: no se pueden estrechar las dos a la vez.",
     "pestana": "Paquete de ondas", "config": {"inc_tipo": "gaussiano", "inc_ancho": 1.0, "inc_k0": 5.0}},
    {"titulo": "No todos los paquetes son mínimos",
     "objetivo": "Comparar el producto Δx·Δp de distintas formas de paquete.",
     "pasos": ["Carga la configuración.", "Abre «Relación Δx–Δp» y mira el gráfico de barras.",
               "Sube el chirp β a 4 y vuelve a mirar."],
     "pregunta": "¿Cuál de los paquetes tiene el menor producto? ¿Puede alguno bajar de 0.5 ħ?",
     "resultado": "El gaussiano (0.5 ħ). Le siguen la secante hiperbólica (π/6 ≈ 0.524 ħ) y el triangular "
                  "(√0.3 ≈ 0.548 ħ). El chirp añade una fase que no cambia |ψ|² pero sí el reparto de momentos: "
                  "½√(1+β²) ≈ 2.06 ħ con β = 4. Ninguno baja de ħ/2: es un teorema, no una limitación técnica.",
     "pestana": "Relación Δx–Δp", "config": {"inc_tipo": "chirp", "inc_ancho": 1.0, "inc_beta": 2.0, "inc_k0": 5.0}},
    {"titulo": "Δx no es «el tamaño de cada trozo»",
     "objetivo": "Ver la incertidumbre en un estado superposición de dos posiciones.",
     "pasos": ["Carga la configuración (dos gaussianas de 0.6 nm separadas 6 nm).",
               "Mira |φ(p)|²: ¿qué aparece en la distribución de momentos?", "Reduce la separación a 1 nm."],
     "pregunta": "¿Por qué el producto es tan grande si cada pico es estrecho?",
     "resultado": "Δx mide la dispersión de TODAS las posiciones posibles (≈ d/2 = 3 nm), no la anchura de cada pico. "
                  "En momento aparecen franjas de interferencia (cos²(pd/2ħ)), señal de que los dos picos son una "
                  "sola onda coherente. Al juntarlos, el producto vuelve hacia 0.5 ħ.",
     "pestana": "Paquete de ondas", "config": {"inc_tipo": "dos", "inc_ancho": 0.6, "inc_sep": 6.0, "inc_k0": 0.0}},
    {"titulo": "El paquete se dispersa",
     "objetivo": "Observar la evolución libre y la escala de tiempo τ = 2mσ₀²/ħ.",
     "pasos": ["Carga la configuración (electrón, 1 nm).", "Abre «Evolución libre» y reproduce la animación.",
               "Cambia la partícula a protón y luego a un grano de polvo; mira τ."],
     "pregunta": "¿Por qué no vemos ensancharse una pelota o un grano de polvo?",
     "resultado": "Δp no cambia, pero las componentes de distinto momento se separan: Δx(t) crece y en t = τ ya es "
                  "√2 veces mayor. Para un electrón de 1 nm τ ≈ 17 fs; para un protón ≈ 32 ps; para un grano de polvo "
                  "de 10⁻¹⁵ kg confinado en 1 nm, ≈ 19 s, y confinado en 1 µm, unos 7 meses. Para una pelota, más que la edad "
                  "del universo: la masa grande hace la dispersión imperceptible.",
     "pestana": "Evolución libre", "config": {"inc_tipo": "gaussiano", "inc_ancho": 1.0, "inc_k0": 5.0, "inc_masa": "electron"}},
    {"titulo": "Una rendija como medida de la posición",
     "objetivo": "Relacionar el ancho de una rendija con la dispersión angular del haz.",
     "pasos": ["Carga la configuración (luz verde, rendija de 20 µm).", "Anota el ancho del máximo central.",
               "Reduce la rendija a 5 µm y después a 1 µm."],
     "pregunta": "¿Por qué el haz se abre MÁS cuando la rendija es MÁS estrecha?",
     "resultado": "La rendija localiza la partícula en Δy ≈ a; eso obliga a una dispersión del momento transversal "
                  "Δp_y ≈ h/a, y el ángulo del primer mínimo cumple sen θ₁ = λ/a. Con 20 µm el máximo central mide "
                  "≈ 53 mm a 1 m; con 5 µm ≈ 21 cm; con 1 µm la luz se abre en un abanico de ±32°.",
     "pestana": "Difracción por una rendija",
     "config": {"inc_ren_particula": "foton", "inc_ren_lambda": 532.0, "inc_ren_ancho": 20000.0, "inc_ren_distancia": 1.0}},
]

PREGUNTAS = [
    {"enunciado": "El principio de incertidumbre Δx·Δp ≥ ħ/2 se debe fundamentalmente a…",
     "opciones": ["la imprecisión de los aparatos de medida", "que ψ(x) y φ(p) son transformadas de Fourier una de la otra",
                  "que el electrón es muy pequeño", "el efecto de la temperatura"], "correcta": 1,
     "explicacion": "Es una propiedad de las ondas: una onda localizada necesita muchas longitudes de onda (momentos) "
                    "distintas. No depende de la calidad del instrumento."},
    {"enunciado": "Si se reduce a la mitad el ancho de un paquete gaussiano, su Δp…",
     "opciones": ["se reduce a la mitad", "no cambia", "se duplica", "se cuadruplica"], "correcta": 2,
     "explicacion": "Para el gaussiano Δx·Δp = ħ/2 siempre, así que Δp = ħ/(2Δx)."},
    {"enunciado": "¿Qué paquete tiene el producto Δx·Δp más pequeño posible?",
     "opciones": ["el triangular", "el gaussiano sin chirp", "el rectangular", "cualquiera, si es suficientemente estrecho"],
     "correcta": 1, "explicacion": "Solo el gaussiano (sin chirp) alcanza la igualdad Δx·Δp = ħ/2."},
    {"enunciado": "Un paquete libre se ensancha con el tiempo. Durante esa evolución, Δp…",
     "opciones": ["aumenta", "disminuye", "se mantiene constante", "oscila"], "correcta": 2,
     "explicacion": "Sin fuerzas el momento se conserva, y con él su distribución. Lo que crece es Δx, porque las "
                    "componentes rápidas y lentas se separan."},
    {"enunciado": "Al estrechar la rendija por la que pasa un haz de luz o de electrones…",
     "opciones": ["el haz sale más concentrado", "el máximo central se ensancha", "desaparece el patrón",
                  "solo cambia la intensidad"], "correcta": 1,
     "explicacion": "Δy ≈ a disminuye, así que Δp_y ≈ h/a aumenta: sen θ₁ = λ/a crece."},
    {"enunciado": "¿Por qué no notamos el principio de incertidumbre con una pelota de béisbol?",
     "opciones": ["porque no se aplica a objetos grandes", "porque ħ es muy pequeña comparada con m·Δx de la pelota",
                  "porque la pelota no es una onda", "porque se mueve muy deprisa"], "correcta": 1,
     "explicacion": "Δv ≥ ħ/(2mΔx): con m = 0.145 kg y Δx = 1 mm, Δv ≈ 4×10⁻³¹ m/s, imposible de medir. La ley se "
                    "aplica, pero su efecto es despreciable."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("inc_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


def _leer_parametros():
    ss = st.session_state
    with st.container(border=True):
        qc.seccion("Paquete de ondas")
        c1, c2, c3, c4 = st.columns(4, vertical_alignment="bottom")
        tipo = c1.selectbox("Forma del paquete", list(TIPOS), key="inc_tipo", format_func=TIPOS.get)
        etiqueta = "Ancho σ [nm]" if tipo in ("gaussiano", "chirp", "dos") else "Semiancho a [nm]"
        ancho = c2.number_input(etiqueta, min_value=ANCHO_MIN, max_value=ANCHO_MAX, step=0.1, format="%.3f",
                                key="inc_ancho", help="Controla lo localizado que está el paquete en x.")
        k0 = c3.number_input("Momento central p₀ [ħ/nm]", min_value=-K0_MAX, max_value=K0_MAX, step=1.0, format="%.2f",
                             key="inc_k0", help="p₀ = ħk₀. Desplaza la distribución de momentos sin cambiar su anchura.")
        if tipo == "chirp":
            c4.slider("Chirp β", -BETA_MAX, BETA_MAX, step=0.1, key="inc_beta",
                      help="Fase cuadrática e^{iβx²/4σ²}: no cambia |ψ|², pero sí la distribución de momentos.")
        elif tipo == "dos":
            c4.number_input("Separación d [nm]", min_value=0.0, max_value=200.0, step=0.5, format="%.2f", key="inc_sep",
                            help="Distancia entre los centros de las dos gaussianas.")
        qc.pie_de_parametros(DEMOS, "inc_demo", _aplicar_demo, VALORES_INICIALES, "inc_reset")
    try:
        return validar_paquete(tipo, ancho, k0, ss["inc_beta"], ss["inc_sep"])
    except ValueError as error:
        qc.error(error)
        return None


@st.cache_data(show_spinner=False, max_entries=24)
def _cache_compresion(p: Paquete, compacto: bool):
    return figura_compresion(p, compacto)


@st.cache_data(show_spinner="Calculando la evolución…", max_entries=16)
def _cache_evolucion(p: Paquete, s_max: float):
    return evolucionar(p, np.linspace(0, s_max, 61))


def _pestana_paquete(p: Paquete):
    c = calcular_paquete(p)
    teo = producto_teorico(p)
    qc.seccion("Resultados")
    qc.metricas([
        ("Δx [nm]", f"{c['delta_x']:.5f}", "Desviación típica de la posición, calculada de |ψ(x)|²"),
        ("Δp [ħ/nm]", f"{c['delta_k']:.5f}", f"= {c['delta_k'] * 1e9 * HBAR:.4e} kg·m/s. Calculada de |φ(p)|² con la FFT"),
        ("Δx·Δp [ħ]", f"{c['producto']:.5f}", "Siempre ≥ 0.5 ħ"),
        ("Valor exacto [ħ]", f"{teo:.5f}" if teo is not None else "—", "Fórmula cerrada para esta forma de paquete"),
        ("⟨p⟩ [ħ/nm]", f"{c['k_medio']:.4f}", "Momento medio: ħk₀"),
        ("Exceso sobre el mínimo", f"{c['producto'] / 0.5:.4f} × ħ/2", "1 = paquete de mínima incertidumbre"),
        ("Δv de un electrón", f"{c['delta_k'] * 1e9 * HBAR / M_E:.4e} m/s", "Δv = Δp/mₑ"),
        ("Normalización ∫|φ|²dp", f"{c['norma_k']:.10f}", "Teorema de Parseval: igual a ∫|ψ|²dx = 1"),
    ])
    qc.seccion("Posición y momento: el mismo paquete visto de dos maneras")
    qc.mostrar_plotly(_cache_compresion(p, qc.modo_compacto()), "inc_compresion",
                      archivo=f"incertidumbre_{p.tipo}.html")
    st.caption("Mueve el deslizador para cambiar el ancho del paquete: los ejes están fijos, así que se ve cómo al "
               "estrecharse |ψ(x)|² se ensancha |φ(p)|², y al revés. El deslizador solo cambia la figura; los "
               "resultados de arriba corresponden al ancho elegido en los parámetros. Líneas punteadas: ±Δx y ±Δp. "
               "La curva azul tenue es Re ψ: sus oscilaciones tienen longitud de onda 2π/k₀.")
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- ψ(x) y φ(p) contienen **la misma información**: una es la transformada de Fourier de la otra. Para "
            "construir un pico estrecho en x hay que sumar ondas de muchos momentos distintos.\n"
            "- La desigualdad Δx·Δp ≥ ħ/2 no habla de errores de medida: dice que **no existe** ningún estado con "
            "posición y momento bien definidos a la vez.\n"
            "- Las curvas son distribuciones de probabilidad: si se mide la posición de muchas partículas preparadas "
            "igual, los resultados se reparten según |ψ(x)|²; si se mide el momento, según |φ(p)|².\n"
            "- Δp = 1 ħ/nm equivale a 1.05×10⁻²⁵ kg·m/s: para un electrón, una velocidad de 116 km/s.")


def _pestana_relacion(p: Paquete):
    qc.mostrar_pyplot(figura_relacion(p), archivo=f"incertidumbre_relacion_{p.tipo}.png")
    st.caption("Izquierda: cada punto es un paquete del mismo ancho; la curva roja es el límite ħ/2 y la región "
               "sombreada está prohibida. El punto con borde blanco es el paquete elegido. Derecha: producto Δx·Δp de "
               "cada forma (para el chirp y las dos gaussianas se usan β y d elegidos, o β = 2 y d = 6σ si están en cero).")
    qc.seccion("Consecuencias a distintas escalas")
    st.caption("Velocidad mínima compatible con el confinamiento: Δv = ħ/(2mΔx).")
    qc.tabla_libre([{"Objeto": e["nombre"], "Masa [kg]": f"{e['masa']:.3e}", "Confinamiento": e["nota"],
                     "Δp mínimo [kg·m/s]": f"{e['dp']:.2e}", "Δv mínimo [m/s]": f"{e['dv']:.2e}",
                     "Energía cinética mínima [eV]": f"{e['energia_ev']:.2e}"} for e in ejemplos_escala()],
                   numericas=("Masa [kg]", "Δp mínimo [kg·m/s]", "Δv mínimo [m/s]", "Energía cinética mínima [eV]"),
                   archivo="incertidumbre_escalas.csv")
    st.caption("El electrón confinado en un átomo tiene velocidades de ~10⁶ m/s y energías de eV (las energías "
               "químicas); el protón en un núcleo, de MeV (las energías nucleares). Para objetos cotidianos el efecto "
               "es inmensurable.")


def _pestana_evolucion(p: Paquete):
    with st.container(border=True):
        qc.seccion("Partícula y duración")
        c1, c2, _, _ = st.columns(4)
        masa = c1.selectbox("Partícula", list(MASAS), key="inc_masa", format_func=lambda k: MASAS[k][0],
                            help="La masa solo fija la escala de tiempo τ: en unidades de τ la evolución es la misma.")
        s_max = c2.slider("Duración [τ]", 0.5, 6.0, step=0.5, key="inc_smax")
    m = MASAS[masa][1]
    tau = tiempo_caracteristico(p.ancho, m)
    ev = _cache_evolucion(p, float(s_max))
    v_grupo = HBAR * p.k0 * 1e9 / m
    qc.metricas([
        ("Tiempo característico τ", texto_tiempo(tau), "τ = 2m·ancho²/ħ: en t = τ un gaussiano sin chirp es √2 veces más ancho"),
        ("Δx inicial → final [nm]", f"{ev['delta_x'][0]:.3f} → {ev['delta_x'][-1]:.3f}", f"tras {s_max:g} τ = {texto_tiempo(s_max * tau)}"),
        ("Velocidad de grupo [m/s]", f"{v_grupo:.4e}", "ħk₀/m: el centro del paquete se mueve como una partícula clásica"),
        ("Δv = Δp/m [m/s]", f"{ev['delta_k'][0] * 1e9 * HBAR / m:.4e}", "Dispersión de velocidades: responsable del ensanchamiento"),
    ])
    qc.mostrar_plotly(figura_evolucion(p, ev, tau, MASAS[masa][0], qc.modo_compacto()), "inc_evolucion",
                      archivo=f"incertidumbre_evolucion_{p.tipo}.html")
    st.caption("Línea gris discontinua: el paquete en t = 0. El centro avanza con la velocidad de grupo y el paquete se "
               "ensancha porque contiene momentos distintos (Δp). Con un chirp negativo el paquete primero se ESTRECHA "
               "(las componentes lentas van delante) y después se ensancha.")
    qc.mostrar_pyplot(figura_anchura(p, ev, tau), archivo=f"incertidumbre_anchura_{p.tipo}.png")


def _pestana_rendija():
    ss = st.session_state
    with st.container(border=True):
        qc.seccion("Montaje")
        c1, c2, c3, c4 = st.columns(4, vertical_alignment="bottom")
        particula = c1.radio("Partícula", list(PARTICULAS_RENDIJA), key="inc_ren_particula",
                             format_func=PARTICULAS_RENDIJA.get, horizontal=True)
        if particula == "foton":
            valor = c2.number_input("Longitud de onda λ [nm]", min_value=1.0, max_value=100000.0, step=10.0,
                                    format="%.1f", key="inc_ren_lambda")
        else:
            valor = c2.number_input("Energía del electrón [eV]", min_value=0.01, max_value=100000.0, step=10.0,
                                    format="%.2f", key="inc_ren_energia", help="λ = h/√(2mₑE)")
        a = c3.number_input("Ancho de la rendija a [nm]", min_value=0.01, max_value=1e7, step=1000.0, format="%.4g",
                            key="inc_ren_ancho")
        L = c4.number_input("Distancia a la pantalla [m]", min_value=0.01, max_value=100.0, step=0.1, format="%.2f",
                            key="inc_ren_distancia")
    try:
        r = validar_rendija(particula, valor, a, L)
    except ValueError as error:
        qc.error(error)
        return
    d = calcular_rendija(r)
    if not d["hay_minimo"]:
        qc.aviso(f"La rendija ({r.ancho_nm:.4g} nm) es más estrecha que la longitud de onda ({r.longitud_onda_nm:.4g} nm): "
                 "no hay mínimos y la onda sale en todas direcciones.")
    qc.metricas([
        ("Longitud de onda λ [nm]", f"{r.longitud_onda_nm:.5g}", "De Broglie: λ = h/p" if particula == "electron" else "Luz"),
        ("Momento p [kg·m/s]", f"{d['p']:.4e}", "p = h/λ"),
        ("Ángulo del primer mínimo θ₁", f"{np.degrees(d['theta1']):.4g}°" if d["hay_minimo"] else "—", "sen θ₁ = λ/a"),
        ("Ancho del máximo central", (f"{2 * d['y1_m'] * 1e3:.4g} mm" if d["hay_minimo"] else "—"), "2L·tan θ₁ en la pantalla"),
        ("Δy ≈ a [m]", f"{r.ancho_nm * 1e-9:.3e}", "La rendija localiza la partícula"),
        ("Δp_y ≈ p·sen θ₁ [kg·m/s]", f"{d['dpy']:.4e}" if d["hay_minimo"] else "—", "= h/a"),
        ("Δy·Δp_y [h]", f"{d['producto_h']:.4f}" if d["hay_minimo"] else "—", "= 1 h ≈ 6.3 ħ, mayor que ħ/2"),
        ("Sombra geométrica", f"{r.ancho_nm * 1e-6:.4g} mm", "Lo que se vería si la luz fuera un chorro de partículas clásicas"),
    ])
    qc.mostrar_pyplot(figura_rendija(r, d), archivo="incertidumbre_rendija.png")
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- Antes de la rendija la partícula viaja en la dirección x con p_y = 0 bien definido. Al pasar, su posición "
            "transversal queda acotada a Δy ≈ a; el principio de incertidumbre exige entonces una dispersión del "
            "momento transversal, y el haz se abre.\n"
            "- El primer mínimo está en sen θ₁ = λ/a; el momento transversal correspondiente es p·sen θ₁ = h/a. Así "
            "Δy·Δp_y ≈ h, que es del orden de ħ (la estimación es aproximada: para una rendija de bordes netos la "
            "desviación típica de p_y no es finita, por eso se usa el ancho del máximo central).\n"
            "- Con electrones ocurre exactamente lo mismo, con λ = h/p (difracción de electrones, Davisson–Germer 1927).")


def _pestana_teoria():
    sub = st.tabs(["El principio", "Por qué ocurre", "Consecuencias", "Malentendidos", "Resumen de ecuaciones"])
    with sub[0]:
        qc.seccion("Heisenberg, 1927")
        st.markdown(
            "En 1927 Werner Heisenberg publicó que en la mecánica cuántica la posición y el momento de una partícula "
            "no pueden tener a la vez valores precisos. Lo ilustró con un «microscopio de rayos gamma»: para ver dónde "
            "está un electrón con precisión Δx hay que iluminarlo con luz de longitud de onda corta, λ ≲ Δx; pero un "
            "fotón así tiene un momento grande, h/λ, y al rebotar en el electrón le da un empujón imprevisible del "
            "orden de h/Δx.")
        st.markdown("Ese mismo año Earle Kennard demostró la forma precisa, con Δ las desviaciones típicas de las "
                    "distribuciones de probabilidad:")
        st.latex(r"\Delta x\,\Delta p\ \ge\ \frac{\hbar}{2},\qquad \Delta x=\sqrt{\langle x^2\rangle-\langle x\rangle^2},\quad \Delta p=\sqrt{\langle p^2\rangle-\langle p\rangle^2}")
        st.markdown("En 1929 Howard Robertson la generalizó a cualquier par de magnitudes A y B cuyos operadores no "
                    "conmutan:")
        st.latex(r"\Delta A\,\Delta B\ \ge\ \frac{1}{2}\left|\langle[\hat A,\hat B]\rangle\right|,\qquad [\hat x,\hat p]=i\hbar\ \Rightarrow\ \Delta x\,\Delta p\ge\frac{\hbar}{2}")
        st.markdown("Las componentes de distintas direcciones sí conmutan: se pueden conocer a la vez x y p_y, por "
                    "ejemplo. La restricción es para cada par conjugado (x con pₓ, y con p_y, z con p_z).")
    with sub[1]:
        qc.seccion("Es una propiedad de las ondas")
        st.markdown(
            "Una partícula cuántica se describe por una onda. Con longitud de onda bien definida (un único momento, "
            "p = h/λ) la onda se extiende por todo el espacio: no está localizada. Para fabricar un pulso localizado hay "
            "que superponer muchas ondas de longitudes distintas que interfieran constructivamente en una región y se "
            "anulen fuera. Cuanto más corto el pulso, más variedad de longitudes de onda (de momentos) hace falta.")
        st.latex(r"\psi(x)=\frac{1}{\sqrt{2\pi\hbar}}\int\varphi(p)\,e^{ipx/\hbar}\,dp\qquad\Longleftrightarrow\qquad\varphi(p)=\frac{1}{\sqrt{2\pi\hbar}}\int\psi(x)\,e^{-ipx/\hbar}\,dx")
        st.markdown(
            "Lo mismo ocurre con el sonido: una nota muy corta no tiene un tono definido (Δt·Δf ≳ 1/4π). La "
            "aportación de la física cuántica es identificar el momento con la frecuencia espacial, p = ħk; la "
            "desigualdad matemática Δx·Δk ≥ ½ se convierte así en una ley física.")
        qc.seccion("El paquete de mínima incertidumbre")
        st.markdown("La igualdad Δx·Δp = ħ/2 solo se alcanza con un gaussiano sin chirp. Cualquier otra forma, o un "
                    "gaussiano con fase cuadrática, tiene un producto mayor:")
        qc.tabla_libre([
            {"Paquete": "Gaussiano", "ψ(x)": "e^{−x²/4σ²}", "Δx·Δp": "ħ/2 = 0.5 ħ"},
            {"Paquete": "Secante hiperbólica", "ψ(x)": "sech(x/a)", "Δx·Δp": "πħ/6 ≈ 0.524 ħ"},
            {"Paquete": "Triangular", "ψ(x)": "1 − |x|/a", "Δx·Δp": "√(3/10) ħ ≈ 0.548 ħ"},
            {"Paquete": "Gaussiano con chirp", "ψ(x)": "e^{−(1−iβ)x²/4σ²}", "Δx·Δp": "½√(1+β²) ħ"},
            {"Paquete": "Rectangular", "ψ(x)": "1 si |x| < a", "Δx·Δp": "infinito (los bordes abruptos necesitan momentos arbitrariamente grandes)"},
        ])
    with sub[2]:
        qc.seccion("El tamaño y la estabilidad de los átomos")
        st.markdown("Confinar un electrón en una región de tamaño r le da un momento de al menos ~ħ/r, y una energía "
                    "cinética ~ħ²/2mr². Minimizando la energía total frente a la atracción del núcleo resulta el radio "
                    "de Bohr y la energía del hidrógeno (ver el simulador 05):")
        st.latex(r"E(r)\approx\frac{\hbar^2}{2m_er^2}-\frac{e^2}{4\pi\varepsilon_0r}\ \Rightarrow\ r_{\min}=a_0=0.053\ \mathrm{nm},\quad E_{\min}=-13.6\ \mathrm{eV}")
        qc.seccion("Energía de punto cero")
        st.markdown("Una partícula ligada nunca puede estar en reposo en el fondo del pozo: eso supondría Δx y Δp nulos. "
                    "Por eso el estado fundamental del oscilador armónico tiene energía ħω/2 (simulador 02) y la partícula "
                    "en una caja, π²ħ²/2ma² (simulador 01). El helio sigue líquido a presión atmosférica incluso cerca del "
                    "cero absoluto por esta energía.")
        qc.seccion("Escalas nucleares")
        st.markdown("Un protón confinado en un núcleo (Δx ≈ 1 fm) tiene energías cinéticas de varios MeV, un millón de "
                    "veces las energías químicas: de ahí la enorme energía de las reacciones nucleares.")
        qc.seccion("Energía y tiempo")
        st.latex(r"\Delta E\,\Delta t\ \gtrsim\ \frac{\hbar}{2}")
        st.markdown("No es exactamente igual que la de posición y momento (el tiempo no es un operador), pero tiene un "
                    "sentido preciso: un estado que dura un tiempo τ tiene una energía indefinida en ~ħ/τ. Por eso las "
                    "líneas espectrales de los átomos tienen una anchura natural, y las partículas muy inestables, una "
                    "masa «borrosa».")
        qc.seccion("Ensanchamiento de los paquetes")
        st.markdown("Una partícula libre con Δp tiene una dispersión de velocidades Δv = Δp/m; con el tiempo su posición "
                    "se vuelve cada vez más incierta. Para objetos macroscópicos el tiempo necesario es astronómico.")
    with sub[3]:
        qc.seccion("Lo que el principio NO dice")
        st.markdown(
            "- **No es un problema de los instrumentos.** Ningún aparato, por perfecto que sea, puede preparar un estado "
            "con Δx·Δp < ħ/2: esos estados no existen.\n"
            "- **No dice que la partícula tenga una posición y un momento exactos que desconocemos.** Antes de medir, "
            "esas magnitudes no tienen valores definidos simultáneos (los experimentos sobre desigualdades de Bell "
            "descartan las teorías «locales» de valores ocultos).\n"
            "- **No impide medir con precisión una sola magnitud.** Se puede medir x con toda la precisión que se "
            "quiera; lo que ocurre es que entonces p queda muy indeterminado.\n"
            "- **No se limita al «empujón» de la medida.** El microscopio de Heisenberg es una buena ilustración, pero "
            "la desigualdad de Kennard trata del estado en sí, haya o no medida.\n"
            "- **No es algo exclusivo del mundo microscópico.** Se aplica a todo; simplemente, para masas grandes, ħ "
            "es tan pequeña que el efecto no se puede detectar.")
    with sub[4]:
        qc.seccion("Relaciones de incertidumbre")
        st.latex(r"\Delta x\,\Delta p_x\ge\frac{\hbar}{2}\qquad\Delta A\,\Delta B\ge\frac12\left|\langle[\hat A,\hat B]\rangle\right|\qquad\Delta E\,\Delta t\gtrsim\frac{\hbar}{2}")
        qc.seccion("Paquetes de ondas")
        st.latex(r"\psi(x)\propto e^{-(1-i\beta)x^2/4\sigma^2}\,e^{ik_0x}\quad\Rightarrow\quad\Delta x=\sigma,\quad\Delta p=\frac{\hbar\sqrt{1+\beta^2}}{2\sigma},\quad\langle p\rangle=\hbar k_0")
        qc.seccion("Evolución libre")
        st.latex(r"\varphi(p,t)=\varphi(p,0)\,e^{-ip^2t/2m\hbar}\qquad\sigma(t)=\sigma_0\sqrt{1+2\beta s+(1+\beta^2)s^2},\quad s=\frac{t}{\tau},\quad\tau=\frac{2m\sigma_0^2}{\hbar}")
        qc.seccion("Rendija")
        st.latex(r"\frac{I(\theta)}{I_0}=\left[\frac{\sin(\pi a\sin\theta/\lambda)}{\pi a\sin\theta/\lambda}\right]^2,\qquad \sin\theta_1=\frac{\lambda}{a},\qquad \Delta y\,\Delta p_y\approx a\cdot\frac{h}{a}=h")
        qc.seccion("Ondas de materia")
        st.latex(r"\lambda=\frac{h}{p}=\frac{h}{\sqrt{2mE}}\qquad(\text{electrón: }\lambda\,[\mathrm{nm}]\approx\frac{1.226}{\sqrt{E\,[\mathrm{eV}]}})")


def interfaz() -> None:
    """Página completa del simulador 6 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 06", "Principio de incertidumbre de Heisenberg",
                         "Paquetes de ondas en posición y en momento, el límite Δx·Δp ≥ ħ/2, el ensanchamiento de "
                         "una partícula libre y la difracción por una rendija.")
    p = _leer_parametros()
    if p is None:
        return
    tabs = st.tabs(["Paquete de ondas", "Relación Δx–Δp", "Evolución libre", "Difracción por una rendija", "Teoría",
                    "Guía de práctica", "Autoevaluación", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_paquete(p)
    with tabs[1]:
        _pestana_relacion(p)
    with tabs[2]:
        _pestana_evolucion(p)
    with tabs[3]:
        _pestana_rendija()
    with tabs[4]:
        _pestana_teoria()
    with tabs[5]:
        qc.guia_practica(GUIA, "inc")
    with tabs[6]:
        qc.autoevaluacion(PREGUNTAS, "inc")
    with tabs[7]:
        qc.boton_pruebas(ejecutar_pruebas, "inc_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Principio de incertidumbre", ":material/science:",
              "principio_incertidumbre.py")
