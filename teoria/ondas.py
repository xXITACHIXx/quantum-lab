"""
teoria/ondas.py — Teoría: Ondas clásicas y funciones complejas
"""

import cmath
import math

import numpy as np
import streamlit as st

import quantum_lab_comun as qc
from teoria._util import COL, figura, dibujar


def onda_viajera(x, t, A, k, omega, fase=0.0):
    """Ψ(x, t) = A sin(kx − ωt + φ)."""
    return A * np.sin(k * x - omega * t + fase)


def onda_estacionaria(x, t, A, k, omega):
    """Suma de dos ondas iguales que viajan en sentidos opuestos: A[sin(kx − ωt) + sin(kx + ωt)] = 2A sin(kx) cos(ωt)."""
    return A * (np.sin(k * x - omega * t) + np.sin(k * x + omega * t))


def onda_compleja(x, t, A, k, omega, fase=0.0):
    """Ψ(x, t) = A e^{i(kx − ωt + φ)}."""
    return A * np.exp(1j * (k * x - omega * t + fase))


def residuo_ecuacion_de_onda(A=1.0, k=2.0, omega=6.0, fase=0.3, x0=0.7, t0=0.4, h=1e-4):
    """
    Comprueba numéricamente (diferencias finitas) que Ψ = A sin(kx − ωt + φ) cumple
    ∂²Ψ/∂x² = (1/v²) ∂²Ψ/∂t² con v = ω/k. Devuelve la diferencia relativa entre ambos miembros.
    """
    f = lambda x, t: onda_viajera(x, t, A, k, omega, fase)
    d2x = (f(x0 + h, t0) - 2 * f(x0, t0) + f(x0 - h, t0)) / h ** 2
    d2t = (f(x0, t0 + h) - 2 * f(x0, t0) + f(x0, t0 - h)) / h ** 2
    v = omega / k
    return abs(d2x - d2t / v ** 2) / max(abs(d2x), 1e-30)


def mostrar() -> None:
    sub = st.tabs(["Onda viajera", "Interferencia y ondas estacionarias", "La ecuación de onda",
                   "Representación compleja", "Visualizador"])
    with sub[0]:
        qc.seccion("Describir una onda")
        st.markdown(
            "Una onda se puede representar con una sucesión de **frentes de onda**: superficies donde la amplitud es "
            "máxima o mínima. Pueden ser planos, esféricos o cilíndricos, y la dirección de propagación es perpendicular "
            "a ellos. Llamamos x a la coordenada a lo largo de esa dirección. La **función de onda** Ψ(x, t) dice cuánto "
            "vale la amplitud en cada punto y en cada instante.")
        st.markdown("Para una onda sinusoidal de longitud de onda λ y frecuencia ν = 1/T (T es el periodo) que avanza hacia +x:")
        st.latex(r"\Psi(x,t)=A\sin\!\left[2\pi\left(\frac{x}{\lambda}-\frac{t}{T}\right)\right]=A\sin(kx-\omega t+\varphi)")
        st.markdown(
            "- A es la amplitud (la oscilación pico a pico vale 2A).\n"
            "- **k = 2π/λ** es el número de onda (o vector de onda).\n"
            "- **ω = 2πν** es la frecuencia angular.\n"
            "- El argumento kx − ωt + φ es la **fase**; φ es la fase inicial y desplaza la onda.\n"
            "- La velocidad de propagación es v = λν = ω/k.")
        st.markdown("Como el seno se repite cada 2π, dos puntos separados una longitud de onda tienen la misma fase y se mueven al unísono.")
    with sub[1]:
        qc.seccion("Superposición")
        st.markdown(
            "Cuando dos o más ondas coinciden en una región, sus amplitudes **se suman**. Si ambas son positivas (o "
            "negativas) hay **interferencia constructiva**; si tienen signos opuestos e igual magnitud hay "
            "**interferencia destructiva**.")
        qc.seccion("Ondas estacionarias")
        st.markdown("Superponer dos ondas de igual frecuencia y amplitud que viajan en sentidos contrarios:")
        st.latex(r"\Psi(x,t)=A[\sin(kx-\omega t)+\sin(kx+\omega t)]=\big(2A\sin kx\big)\big(\cos\omega t\big)=\psi(x)\,\theta(t)")
        st.markdown(
            "La identidad sin(α ± β) = sin α cos β ± cos α sin β separa la dependencia espacial y la temporal. "
            "Los **nodos** (donde sin kx = 0) están siempre en el mismo sitio. Esa es la diferencia con una onda viajera, "
            "donde los nodos avanzan con la onda. Esta separación Ψ = ψ(x)θ(t) es la que aparecerá otra vez en la "
            "ecuación de Schrödinger para los estados estacionarios.")
    with sub[2]:
        qc.seccion("La ecuación de onda no dispersiva")
        st.markdown("En un medio donde todas las frecuencias viajan con la misma velocidad v, la amplitud cumple")
        st.latex(r"\frac{\partial^2\Psi}{\partial x^2}=\frac{1}{v^2}\frac{\partial^2\Psi}{\partial t^2}")
        st.markdown("Comprobación con Ψ = A sin(kx − ωt + φ):")
        st.latex(r"\frac{\partial^2\Psi}{\partial x^2}=-k^2\Psi,\qquad \frac{1}{v^2}\frac{\partial^2\Psi}{\partial t^2}=-\frac{\omega^2}{v^2}\Psi")
        st.markdown("Ambos miembros coinciden porque v = ω/k. Esta ecuación es el punto de partida para justificar la "
                    "de Schrödinger.")
        res = residuo_ecuacion_de_onda()
        st.caption(f"Comprobación numérica por diferencias finitas con A = 1, k = 2, ω = 6: diferencia relativa entre los "
                   f"dos miembros = {res:.1e}.")
    with sub[3]:
        qc.seccion("Por qué usar números complejos")
        st.markdown(
            "Operar con senos y cosenos es incómodo. Con la fórmula de Euler, e^{iα} = cos α + i sin α, una onda se "
            "escribe en una sola exponencial:")
        st.latex(r"\Psi(x,t)=A\,e^{i(kx-\omega t+\varphi')}")
        st.markdown("Ahí caben la amplitud, la longitud de onda, el periodo y la fase inicial. La onda real es su parte real "
                    "(o imaginaria). Propiedades que se usan constantemente:")
        st.markdown(
            "- Un número complejo se escribe a + ib o en forma polar r e^{iθ}, con r = √(a² + b²).\n"
            "- El **conjugado** f* se obtiene cambiando i por −i. Para r e^{iθ} es r e^{−iθ}.\n"
            "- El **módulo** es |f| = √(f* f). Para r e^{iθ}, |f| = r.\n"
            "- En mecánica cuántica Ψ es compleja, pero la **densidad de probabilidad |Ψ|² = Ψ*Ψ siempre es real y "
            "no negativa**.")
        qc.seccion("Calculadora de módulo y fase")
        c1, c2 = st.columns(2)
        with c1:
            a = st.number_input("Parte real a", value=1.0, format="%.4g", key="on_a")
        with c2:
            b = st.number_input("Parte imaginaria b", value=2.0, format="%.4g", key="on_b")
        z = complex(a, b)
        r, th = cmath.polar(z)
        qc.metricas([("Módulo |z|", f"{r:.5g}"), ("Fase θ [rad]", f"{th:.5g}"), ("Fase θ [grados]", f"{math.degrees(th):.5g}"),
                     ("Conjugado z*", f"{z.conjugate():.4g}")], columnas=4)
        st.caption("Comprobación: z* z = |z|² = " + f"{(z.conjugate() * z).real:.5g}" + " (siempre real).")
    with sub[4]:
        qc.seccion("Explorar las ondas")
        c1, c2, c3 = st.columns(3)
        with c1:
            lam = st.slider("Longitud de onda λ", 0.5, 3.0, 1.0, 0.1, key="on_lam")
        with c2:
            t_rel = st.slider("Tiempo t / T", 0.0, 2.0, 0.0, 0.05, key="on_t")
        with c3:
            fase = st.slider("Fase inicial φ [rad]", 0.0, 6.28, 0.0, 0.1, key="on_fase")
        A, T = 1.0, 1.0
        k, omega = 2 * math.pi / lam, 2 * math.pi / T
        x = np.linspace(0, 4, 1200)
        fig, ejes = figura(10, 8.2, filas=3)
        a1, a2, a3 = ejes
        a1.plot(x, onda_viajera(x, 0, A, k, omega, fase), color=COL["gris"], lw=1.2, ls="--", label="t = 0")
        a1.plot(x, onda_viajera(x, t_rel * T, A, k, omega, fase), color=COL["onda"], lw=2.4, label=f"t = {t_rel:.2f} T")
        a1.set_title("Onda viajera A sin(kx − ωt + φ): todo el patrón se desplaza")
        a1.legend(loc="upper right", fontsize=8.5)
        a2.plot(x, onda_estacionaria(x, t_rel * T, A, k, omega), color=COL["densidad"], lw=2.4)
        nodos = np.arange(0, 4 + 1e-9, lam / 2)
        a2.plot(nodos, np.zeros_like(nodos), "o", color=COL["energia"], ms=6, label="nodos (fijos)")
        a2.plot(x, 2 * A * np.sin(k * x), color=COL["gris"], lw=0.9, ls=":")
        a2.plot(x, -2 * A * np.sin(k * x), color=COL["gris"], lw=0.9, ls=":")
        a2.set_title("Onda estacionaria 2A sin(kx) cos(ωt): los nodos no se mueven")
        a2.legend(loc="upper right", fontsize=8.5)
        z = onda_compleja(x, t_rel * T, A, k, omega, fase)
        a3.plot(x, z.real, color=COL["onda"], lw=2.2, label="Re Ψ")
        a3.plot(x, z.imag, color=COL["interferencia"], lw=2.0, ls="--", label="Im Ψ")
        a3.plot(x, np.abs(z), color=COL["densidad"], lw=1.6, label="|Ψ| = A")
        a3.set_title("Onda compleja A e^{i(kx − ωt + φ)}")
        a3.legend(loc="upper right", fontsize=8.5)
        for ax in ejes:
            ax.set_xlim(0, 4)
            ax.set_ylim(-2.3, 2.3)
            ax.set_xlabel("x")
            ax.set_ylabel("amplitud")
        dibujar(fig, "ondas.png")
        st.caption("Mover t / T: en la onda viajera cada máximo avanza; en la estacionaria solo cambia la altura entre "
                   "los nodos. En la onda compleja Re y Im giran en cuadratura mientras el módulo permanece constante.")


PREGUNTAS = [
    {"enunciado": "En Ψ = A sin(kx − ωt), el número de onda k vale...",
     "opciones": ["2π/λ", "2πν", "λ/2π", "ω/ν"],
     "correcta": 0, "explicacion": "k = 2π/λ; en cambio ω = 2πν es la frecuencia angular."},
    {"enunciado": "¿Qué distingue a una onda estacionaria de una viajera?",
     "opciones": ["Sus nodos permanecen fijos", "Tiene mayor frecuencia", "No tiene amplitud", "No cumple la ecuación de onda"],
     "correcta": 0, "explicacion": "Ψ = ψ(x)θ(t): los nodos (sin kx = 0) están siempre en la misma posición."},
    {"enunciado": "La velocidad de fase de la onda sin(kx − ωt) es...",
     "opciones": ["v = ωk", "v = ω/k", "v = k/ω", "v = 2πk"],
     "correcta": 1, "explicacion": "v = ω/k = λν; se obtiene de exigir que kx − ωt sea constante."},
    {"enunciado": "El módulo de z = 3 + 4i es...",
     "opciones": ["7", "5", "25", "1"],
     "correcta": 1, "explicacion": "|z| = √(3² + 4²) = 5."},
    {"enunciado": "Para una función compleja Ψ, la cantidad Ψ*Ψ es...",
     "opciones": ["compleja en general", "real y no negativa", "siempre cero", "imaginaria pura"],
     "correcta": 1, "explicacion": "Ψ*Ψ = |Ψ|² ≥ 0: por eso puede interpretarse como una densidad de probabilidad."},
]
