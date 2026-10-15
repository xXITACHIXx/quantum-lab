"""
ejercicios/_figuras.py — Gráficas interactivas que acompañan algunas soluciones.

Cada figura es una función pura `crear(parametro) -> plotly.graph_objects.Figure` (sin Streamlit, para poder probarla).
`FIGURAS` asocia el id de un ejercicio con sus figuras; la página las muestra bajo la solución.
Un parámetro opcional (por ejemplo, el número cuántico n) se maneja con un deslizador.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
import plotly.graph_objects as go
from numpy.polynomial import hermite as _herm
from plotly.subplots import make_subplots

from quantum_lab_comun import COLORES, aplicar_tema_plotly


@dataclass(frozen=True)
class Figura:
    titulo: str
    descripcion: str                                   # Markdown: qué mirar en la gráfica
    crear: Callable                                    # crear(parametro) -> Figure
    parametro: tuple | None = None                     # (etiqueta, mínimo, máximo, valor inicial) → deslizador entero

    def dibujar(self, valor=None) -> go.Figure:
        """Crea la figura; sin parámetro se ignora `valor`, con parámetro se usa el inicial si no se da otro."""
        if self.parametro is None:
            return self.crear()
        return self.crear(self.parametro[3] if valor is None else valor)


_ROJO, _AZUL = "#FF4D6D", "#00D4FF"


def _sub(n: int) -> str:
    """Subíndice Unicode (ψ₄), que se ve bien en los títulos de Plotly."""
    return str(n).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))


# ---------------------------------------------------------------------
# Oscilador armónico: nodos de ψ_n
# ---------------------------------------------------------------------
def nodos_hermite(n: int) -> np.ndarray:
    """Ceros de H_n (los nodos de ψ_n en la variable u = αx), ordenados."""
    if n == 0:
        return np.array([])
    return np.sort(_herm.hermroots([0] * n + [1]))


def psi_oscilador(n: int, u: np.ndarray) -> np.ndarray:
    """ψ_n(u) / α^{1/2} con u = αx, normalizada: ∫ψ² du = 1."""
    norma = 1.0 / math.sqrt(2.0 ** n * math.factorial(n) * math.sqrt(math.pi))
    return norma * _herm.hermval(u, [0] * n + [1]) * np.exp(-u * u / 2)


def _acabado(fig: go.Figure, titulo: str, altura: int = 480, leyenda: bool = True) -> go.Figure:
    """Tema común: título corto (no choca con la barra de herramientas), leyenda debajo y ejes con aire."""
    aplicar_tema_plotly(fig, titulo, altura=altura)
    fig.update_layout(
        margin=dict(l=80, r=30, t=75, b=125 if leyenda else 80),
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=13)),
        title=dict(font=dict(size=15)),
    )
    fig.update_xaxes(title_standoff=14, tickfont=dict(size=12), title_font=dict(size=13))
    fig.update_yaxes(title_standoff=14, tickfont=dict(size=12), title_font=dict(size=13))
    fig.update_annotations(font_size=13)
    return fig


def fig_oscilador_nodos(n: int = 4) -> go.Figure:
    u = np.linspace(-6, 6, 1201)
    psi = psi_oscilador(n, u)
    nodos = nodos_hermite(n)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=u, y=psi, name=f"ψ{_sub(n)}", line=dict(color=COLORES["onda"], width=3),
                             hovertemplate="αx = %{x:.3f}<br>ψ = %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=u, y=psi ** 2, name=f"|ψ{_sub(n)}|²", line=dict(color=COLORES["densidad"], width=2, dash="dot"),
                             hovertemplate="αx = %{x:.3f}<br>|ψ|² = %{y:.4f}<extra></extra>"))
    if len(nodos):
        fig.add_trace(go.Scatter(x=nodos, y=np.zeros_like(nodos), mode="markers", name=f"nodos ({len(nodos)})",
                                 marker=dict(color=_ROJO, size=12, symbol="x", line=dict(width=2, color=_ROJO)),
                                 hovertemplate="nodo en αx = %{x:.4f}<extra></extra>"))
    fig.update_xaxes(title_text="αx  (posición adimensional)", range=[-6, 6])
    fig.update_yaxes(title_text="ψ  (en unidades de α^½)")
    return _acabado(fig, f"Oscilador armónico, n = {n}: {n} nodos", altura=470)


# ---------------------------------------------------------------------
# Momento angular: modelo vectorial
# ---------------------------------------------------------------------
def angulos_cono(l: int) -> list[tuple[int, float]]:
    """(m, θ en grados) para m = −l … +l, con cos θ = m / √(l(l+1))."""
    longitud = math.sqrt(l * (l + 1))
    return [(m, math.degrees(math.acos(m / longitud))) for m in range(l, -l - 1, -1)]


def fig_conos(l: int = 5) -> go.Figure:
    longitud = math.sqrt(l * (l + 1))
    fig = go.Figure()
    t = np.linspace(0, 2 * math.pi, 361)
    fig.add_trace(go.Scatter(x=longitud * np.sin(t), y=longitud * np.cos(t), mode="lines", showlegend=False,
                             line=dict(color=COLORES["rejilla"], width=1.5), hoverinfo="skip"))
    for m, theta in angulos_cono(l):
        rho = math.sqrt(longitud ** 2 - m ** 2)
        for signo in (1, -1):
            extremo = m == l
            fig.add_trace(go.Scatter(
                x=[0, signo * rho], y=[0, m], mode="lines+markers+text", showlegend=False,
                text=["", f"m = {m}" if signo == 1 else ""], textposition="middle right", textfont=dict(size=12, color=COLORES["texto"]),
                line=dict(color=(COLORES["densidad"] if extremo else COLORES["onda"]) if signo == 1 else "rgba(0,212,255,0.35)",
                          width=3 if signo == 1 else 1.5),
                marker=dict(size=[0, 9], color=COLORES["densidad"]),
                hovertemplate=f"m = {m}<br>θ = {theta:.2f}°<br>L_z = {m} ħ<extra></extra>"))
        fig.add_hline(y=m, line=dict(color=COLORES["rejilla"], width=1, dash="dot"))
    theta_min = angulos_cono(l)[0][1]
    fig.add_annotation(x=-longitud * 1.02, y=l, text=f"θ mínimo = {theta_min:.2f}° (m = ±{l})", showarrow=False, xanchor="left",
                       yanchor="bottom", font=dict(color=COLORES["densidad"]))
    fig.update_xaxes(title_text="componente perpendicular al eje z  (ħ)", scaleanchor="y", scaleratio=1, zeroline=False,
                     range=[-longitud * 1.25, longitud * 1.8], constrain="domain")
    fig.update_yaxes(title_text="L_z  (ħ)", tickmode="linear", dtick=1 if l <= 8 else 2, range=[-longitud * 1.12, longitud * 1.2],
                     constrain="domain")
    return _acabado(fig, f"l = {l}: |L| = {longitud:.3f} ħ, {2 * l + 1} orientaciones", altura=600, leyenda=False)


def fig_cono_minimo(l_marca: int = 1000) -> go.Figure:
    ls = np.unique(np.round(np.logspace(0, 4, 300)).astype(int))
    theta = np.degrees(np.arccos(np.sqrt(ls / (ls + 1.0))))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ls, y=theta, name="ángulo mínimo", line=dict(color=COLORES["onda"], width=3), showlegend=False,
                             hovertemplate="l = %{x}<br>θ mínimo = %{y:.3f}°<extra></extra>"))
    for l, ax, ay in ((5, 60, -45), (l_marca, -75, -55)):
        t = math.degrees(math.acos(math.sqrt(l / (l + 1))))
        fig.add_trace(go.Scatter(x=[l], y=[t], mode="markers", showlegend=False,
                                 marker=dict(size=12, color=COLORES["densidad"], line=dict(color="white", width=1.5)),
                                 hovertemplate=f"l = {l}<br>θ mínimo = {t:.3f}°<extra></extra>"))
        fig.add_annotation(x=math.log10(l), y=math.log10(t), xref="x", yref="y", text=f"<b>l = {l}</b><br>θ = {t:.2f}°",
                           showarrow=True, arrowhead=0, arrowcolor=COLORES["densidad"], ax=ax, ay=ay,
                           bgcolor="rgba(11,16,32,0.9)", bordercolor=COLORES["densidad"], borderwidth=1, borderpad=5,
                           font=dict(size=13, color=COLORES["texto"]))
    fig.update_xaxes(title_text="número cuántico l  (escala logarítmica)", type="log", range=[0, 4.05],
                     tickmode="array", tickvals=[1, 10, 100, 1000, 10000], ticktext=["1", "10", "100", "1000", "10 000"])
    fig.update_yaxes(title_text="ángulo del cono más cercano a z  (°)", type="log", range=[math.log10(0.4), math.log10(70)],
                     tickmode="array", tickvals=[0.5, 1, 2, 5, 10, 20, 45], ticktext=["0.5°", "1°", "2°", "5°", "10°", "20°", "45°"])
    return _acabado(fig, "Ángulo mínimo del cono según l", altura=470, leyenda=False)


# ---------------------------------------------------------------------
# Hidrógeno: funciones radiales (a₀ = 1)
# ---------------------------------------------------------------------
def radial_30(r: np.ndarray) -> np.ndarray:
    return 2 / (81 * math.sqrt(3)) * (27 - 18 * r + 2 * r * r) * np.exp(-r / 3)


def radial_42(r: np.ndarray) -> np.ndarray:
    return 1 / (64 * math.sqrt(5)) * r ** 2 * (1 - r / 12) * np.exp(-r / 4)


def radial_21(r: np.ndarray) -> np.ndarray:
    return 1 / (2 * math.sqrt(6)) * r * np.exp(-r / 2)


def _radial(funcion, nodos, rmax: float, nombre: str, titulo: str) -> go.Figure:
    r = np.linspace(0, rmax, 1200)
    R = funcion(r)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.14,
                        subplot_titles=(f"Función radial {nombre}(r): cambia de signo en cada nodo", f"Distribución radial r²·{nombre}²"))
    fig.add_trace(go.Scatter(x=r, y=R, name=nombre, line=dict(color=COLORES["onda"], width=3),
                             hovertemplate="r = %{x:.2f} a₀<br>R = %{y:.4f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=r, y=r * r * R * R, name="r²R²", line=dict(color=COLORES["densidad"], width=3),
                             fill="tozeroy", fillcolor="rgba(255,176,0,0.15)",
                             hovertemplate="r = %{x:.2f} a₀<br>r²R² = %{y:.4f}<extra></extra>"), row=2, col=1)
    for k, rn in enumerate(nodos):
        fig.add_trace(go.Scatter(x=[rn], y=[0], mode="markers", name="nodo radial" if k == 0 else None, showlegend=k == 0,
                                 marker=dict(color=_ROJO, size=12, symbol="x", line=dict(width=2, color=_ROJO)),
                                 hovertemplate=f"nodo en r = {rn:.3f} a₀<extra></extra>"), row=1, col=1)
        fig.add_vline(x=rn, line=dict(color=_ROJO, width=1, dash="dash"))
    fig.update_xaxes(title_text="r  (a₀)", row=2, col=1)
    fig.update_yaxes(title_text=f"{nombre}  (a₀^-3/2)", row=1, col=1)
    fig.update_yaxes(title_text="r²R²  (a₀^-1)", row=2, col=1)
    return _acabado(fig, titulo, altura=620)


def nodos_3s() -> tuple[float, float]:
    return 1.5 * (3 - math.sqrt(3)), 1.5 * (3 + math.sqrt(3))


def fig_radial_3s(_=None) -> go.Figure:
    return _radial(radial_30, nodos_3s(), 22, "R₃₀", "Orbital 3s: dos nodos radiales")


def fig_radial_4d(_=None) -> go.Figure:
    return _radial(radial_42, (12.0,), 45, "R₄₂", "Orbital 4d: un nodo radial")


# ---------------------------------------------------------------------
# Formas angulares
# ---------------------------------------------------------------------
def fig_2pz(_=None) -> go.Figure:
    """Corte de ψ_2pz en el plano xz (a₀ = 1): ψ ∝ z e^{−r/2}. Los puntos de máxima |ψ|² están en z = ±2 a₀."""
    eje = np.linspace(-12, 12, 241)
    X, Z = np.meshgrid(eje, eje)
    R = np.hypot(X, Z)
    psi = Z * np.exp(-R / 2)
    psi = psi / np.abs(psi).max()
    fig = go.Figure(go.Heatmap(x=eje, y=eje, z=psi, zmin=-1, zmax=1, colorscale="RdBu", reversescale=True, showscale=False,
                               hovertemplate="x = %{x:.1f} a₀<br>z = %{y:.1f} a₀<br>ψ = %{z:.3f} (relativo)<extra></extra>"))
    # Entradas de leyenda en lugar de barra de color: el signo se lee sin tapar nada
    for nombre, color in (("ψ > 0", "#B2182B"), ("ψ < 0", "#2166AC")):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=nombre, marker=dict(size=13, color=color, symbol="square")))
    fig.add_trace(go.Scatter(x=[0, 0], y=[2, -2], mode="markers", name="máximo de |ψ|² (z = ±2 a₀)",
                             marker=dict(color="white", size=13, symbol="star", line=dict(color="black", width=1.5)),
                             hovertemplate="máximo de |ψ|²: z = %{y:.0f} a₀<extra></extra>"))
    fig.add_hline(y=0, line=dict(color="#0B1020", width=1.5, dash="dash"))
    fig.add_annotation(x=-11.6, y=-0.9, text="plano nodal z = 0", showarrow=False, xanchor="left", yanchor="top",
                       font=dict(color="#0B1020", size=13))
    fig.update_xaxes(title_text="x  (a₀)", range=[-12, 12], scaleanchor="y", scaleratio=1, constrain="domain")
    fig.update_yaxes(title_text="z  (a₀)", range=[-12, 12], constrain="domain")
    return _acabado(fig, "Orbital 2pz: corte en el plano xz", altura=580)


def fig_y20(_=None) -> go.Figure:
    """Lóbulos de Y₂⁰ ∝ 3cos²θ − 1 en el plano xz y sus dos conos nodales."""
    theta = np.linspace(0, math.pi, 600)
    y = (3 * np.cos(theta) ** 2 - 1)
    radio = np.abs(y)
    crit = math.acos(1 / math.sqrt(3))
    fig = go.Figure()
    for nombre, mascara, color in (("Y₂⁰ > 0 (lóbulos a lo largo de z)", y >= 0, _AZUL), ("Y₂⁰ < 0 (anillo en el plano xy)", y <= 0, _ROJO)):
        for lado in (1, -1):
            fig.add_trace(go.Scatter(x=lado * radio[mascara] * np.sin(theta[mascara]), y=radio[mascara] * np.cos(theta[mascara]),
                                     mode="lines", fill="toself", name=nombre, legendgroup=nombre, showlegend=lado == 1,
                                     line=dict(color=color, width=2), hoverinfo="name"))
    for k, ang in enumerate((crit, math.pi - crit)):
        for lado in (1, -1):
            fig.add_trace(go.Scatter(x=[0, lado * 2.2 * math.sin(ang)], y=[0, 2.2 * math.cos(ang)], mode="lines",
                                     name="conos nodales", legendgroup="nodal", showlegend=(k == 0 and lado == 1),
                                     line=dict(color="white", width=1.5, dash="dash"),
                                     hovertemplate=f"nodo: θ = {math.degrees(ang):.2f}°<extra></extra>"))
    fig.update_xaxes(title_text="x  (unidades arbitrarias)", range=[-2.6, 2.6], scaleanchor="y", scaleratio=1, zeroline=False, constrain="domain")
    fig.update_yaxes(title_text="z  (unidades arbitrarias)", range=[-2.6, 2.6], constrain="domain")
    return _acabado(fig, f"|Y₂⁰|: nodos en {math.degrees(crit):.2f}° y {180 - math.degrees(crit):.2f}°", altura=580)


# ---------------------------------------------------------------------
# Partícula en una caja
# ---------------------------------------------------------------------
def fig_caja_tercio(_=None) -> go.Figure:
    x = np.linspace(0, 1, 600)
    dens = 2 * np.sin(math.pi * x) ** 2
    medio = (x >= 1 / 3) & (x <= 2 / 3)
    p = 1 / 3 + math.sqrt(3) / (2 * math.pi)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=dens, name="densidad cuántica |ψ₁|²", line=dict(color=COLORES["densidad"], width=3),
                             hovertemplate="x/a = %{x:.3f}<br>a·|ψ|² = %{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=x[medio], y=dens[medio], fill="tozeroy", name=f"tercio central: P = {p:.3f}", mode="lines",
                             line=dict(color=COLORES["onda"], width=0), fillcolor="rgba(0,212,255,0.35)"))
    fig.add_trace(go.Scatter(x=x, y=np.ones_like(x), name="clásica (uniforme): P = 0.333", line=dict(color=COLORES["gris"], width=2, dash="dash"),
                             hoverinfo="skip"))
    fig.update_xaxes(title_text="x / a  (posición dentro de la caja)")
    fig.update_yaxes(title_text="a·|ψ|²  (densidad de probabilidad)", range=[0, 2.2])
    return _acabado(fig, f"Estado fundamental: {100 * p:.1f} % en el tercio central", altura=470)


# ---------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------
FIGURAS: dict[str, tuple[Figura, ...]] = {
    "s9_nodos": (Figura(
        "Los nodos de ψ_n",
        "Mueve el deslizador: ψ_n tiene exactamente **n nodos**, los ceros del polinomio de Hermite. "
        "Con n = 4 son los cuatro puntos que calculaste (±0.5246 y ±1.6507 en αx). Pasa el cursor sobre las cruces rojas.",
        fig_oscilador_nodos, ("Número cuántico n", 0, 8, 4)),),
    "s10_conos": (Figura(
        "El cono más cercano al eje z",
        "Para l grande el ángulo mínimo tiende a 0: el vector L puede apuntar casi a lo largo de z, como en la física clásica.",
        fig_cono_minimo),),
    "l04_conos_l5": (
        Figura("Los 2l + 1 conos", "Cada línea es una orientación permitida de L (cada m). Cambia l con el deslizador y observa cómo se reparten los ángulos.",
               fig_conos, ("Número cuántico l", 1, 10, 5)),
        Figura("Ángulo mínimo según l", "El punto de l = 5 es el que se pide; compara con l = 1000.", fig_cono_minimo)),
    "s11_nodos3s": (Figura(
        "R₃₀ y su distribución radial",
        "Arriba, la función radial cruza el cero en 1.902 a₀ y 7.098 a₀ (cruces rojas). Abajo, la probabilidad radial tiene tres picos separados por esos nodos.",
        fig_radial_3s),),
    "s11_2pz": (Figura(
        "Dónde está el electrón 2pz",
        "Mapa de ψ en el plano xz: los dos lóbulos tienen signos opuestos y el máximo de |ψ|² está sobre el eje z a 2 a₀ (estrellas).",
        fig_2pz),),
    "l07_y20_nodos": (Figura(
        "Lóbulos y conos nodales de Y₂⁰",
        "Dos lóbulos azules (positivos) a lo largo de z, un anillo rojo (negativo) en el plano xy y dos conos nodales (líneas discontinuas).",
        fig_y20),),
    "h10_4dz2": (Figura(
        "Nodo radial del 4d",
        "El único nodo radial está en r = 12 a₀. Los nodos angulares (dos conos de 54.74°) no aparecen en esta gráfica porque dependen de θ, no de r.",
        fig_radial_4d),),
    "s6_prob_tercio": (Figura(
        "Probabilidad en el tercio central",
        "El área sombreada es la probabilidad pedida. La línea punteada sería la densidad si la partícula fuese clásica.",
        fig_caja_tercio),),
}


def figuras_de(ej_id: str) -> tuple[Figura, ...]:
    return FIGURAS.get(ej_id, ())
