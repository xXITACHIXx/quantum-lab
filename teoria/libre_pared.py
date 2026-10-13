"""
teoria/libre_pared.py — Teoría: Partícula libre y pared de potencial
"""

import math

import numpy as np
import streamlit as st

import quantum_lab_comun as qc
from teoria._util import COL, EV, H, HBAR, ME, dibujar, figura

PARTICULAS = {"Electrón": ME, "Protón": 1.67262192369e-27}


def numero_de_onda(masa: float, energia_J: float) -> float:
    """k = √(2mE)/ħ   [1/m]."""
    return math.sqrt(2 * masa * energia_J) / HBAR


def kappa(masa: float, V_J: float, E_J: float) -> float:
    """κ = √(2m(V − E))/ħ para E < V   [1/m]."""
    if E_J >= V_J:
        raise ValueError("Se necesita E < V para que la onda decaiga dentro de la pared.")
    return math.sqrt(2 * masa * (V_J - E_J)) / HBAR


def profundidad_de_penetracion(masa: float, V_J: float, E_J: float) -> float:
    """1/κ: distancia en la que la amplitud cae a 1/e de su valor en el borde   [m]."""
    return 1.0 / kappa(masa, V_J, E_J)


def funcion_de_onda_pared(x, k: float, kap: float):
    """
    Solución estacionaria con onda incidente e^{ikx} desde x < 0 contra la pared x ≥ 0 (E < V):
        x < 0:  e^{ikx} + R e^{−ikx},   R = (k − iκ)/(k + iκ),   |R| = 1
        x ≥ 0:  T e^{−κx},              T = 2k/(k + iκ)
    (la continuidad de ψ y ψ' en x = 0 fija R y T; es un complemento a las diapositivas).
    """
    R = (k - 1j * kap) / (k + 1j * kap)
    T = 2 * k / (k + 1j * kap)
    x = np.asarray(x, dtype=float)
    return np.where(x < 0, np.exp(1j * k * x) + R * np.exp(-1j * k * x), T * np.exp(-kap * np.clip(x, 0, None))), R, T


def mostrar() -> None:
    sub = st.tabs(["La partícula libre", "Momento y posición", "Pared de potencial", "Simulación: penetración",
                   "Resumen"])
    with sub[0]:
        qc.seccion("El sistema más simple")
        st.markdown(
            "Una **partícula libre** se mueve en una dimensión sin que actúe fuerza alguna. Eso significa que la energía "
            "potencial es constante, y como el cero de la energía potencial no tiene una referencia fija, se elige V = 0. "
            "La ecuación de Schrödinger independiente del tiempo se reduce a")
        st.latex(r"-\frac{\hbar^2}{2m}\frac{d^2\psi(x)}{dx^2}=E\,\psi(x)")
        st.markdown("Tiene dos soluciones independientes, **ondas planas**: una que avanza hacia +x y otra hacia −x.")
        st.latex(r"\psi^{+}(x)=A_+e^{+ikx},\qquad \psi^{-}(x)=A_-e^{-ikx},\qquad k=\sqrt{\frac{2mE}{\hbar^2}}=\frac{2\pi}{\lambda}")
        st.markdown(
            "Como el movimiento no está confinado, **la energía no está cuantizada**: cualquier E ≥ 0 es posible. "
            "La cuantización aparecerá cuando se confine la partícula (como en la partícula en una caja).")
        st.latex(r"E=\frac{p^2}{2m}=\frac{\hbar^2k^2}{2m}\ \Rightarrow\ p=\hbar k=\frac{h}{\lambda}")
        st.markdown("Se recupera la relación de De Broglie: una partícula con momento p = ħk tiene longitud de onda λ = 2π/k.")
    with sub[1]:
        qc.seccion("Las ondas planas son autofunciones del momento")
        st.markdown("Aplicando el operador de momento p̂ = −iħ d/dx a cada solución:")
        st.latex(r"\hat p\,\psi^{+}=\frac{\hbar}{i}\frac{d}{dx}\big(A_+e^{ikx}\big)=+\hbar k\,\psi^{+},\qquad \hat p\,\psi^{-}=-\hbar k\,\psi^{-}")
        st.markdown(
            "Son autofunciones con autovalores +ħk y −ħk: estados con el mismo módulo de momento y **sentidos opuestos**. "
            "Las dos funciones son complejas conjugadas una de la otra.")
        qc.seccion("¿Dónde está la partícula?")
        st.markdown(
            "La onda plana **no es de cuadrado integrable** en toda la recta: no se puede normalizar. Si se restringe a "
            "[−L, L] con L muy grande, la probabilidad en dx es")
        st.latex(r"P(x)\,dx=\frac{\psi^{+*}\psi^{+}\,dx}{\int_{-L}^{L}\psi^{+*}\psi^{+}dx}=\frac{dx}{2L}")
        st.markdown(
            "No depende de x: la partícula tiene la **misma probabilidad de estar en cualquier lugar**. Si se conoce "
            "exactamente el momento (ħk o −ħk), no se sabe nada de la posición. Es el principio de incertidumbre en su caso extremo (Δp = 0, Δx → ∞).")
        qc.seccion("Calculadora")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.selectbox("Partícula", list(PARTICULAS), key="lp_part")
        with c2:
            e_ev = st.number_input("Energía [eV]", 1e-6, 1e6, 10.0, format="%.6g", key="lp_E")
        m = PARTICULAS[nombre]
        k = numero_de_onda(m, e_ev * EV)
        qc.metricas([("k", f"{k * 1e-9:.5g} nm⁻¹"), ("λ = 2π/k", f"{2 * math.pi / k * 1e9:.5g} nm"),
                     ("p = ħk", f"{HBAR * k:.5g} kg·m/s"), ("v = p/m", f"{HBAR * k / m:.5g} m/s")], columnas=4)
        st.caption(f"Comprobación con De Broglie: h/p = {H / (HBAR * k) * 1e9:.5g} nm, igual a 2π/k.")
        x = np.linspace(0, 4 * 2 * math.pi / k, 1500)
        fig, ax = figura(9.5, 3.6)
        ax.plot(x * 1e9, np.cos(k * x), color=COL["onda"], lw=2.2, label="Re ψ⁺ = cos(kx)  (hacia +x)")
        ax.plot(x * 1e9, np.sin(k * x), color=COL["interferencia"], lw=1.8, ls="--", label="Im ψ⁺ = sin(kx)")
        ax.plot(x * 1e9, np.ones_like(x), color=COL["densidad"], lw=2.0, label="|ψ⁺|² = 1 (uniforme)")
        ax.set_xlabel("x [nm]")
        ax.set_ylabel("amplitud (A = 1)")
        ax.set_title("Onda plana: la densidad es uniforme")
        ax.legend(loc="upper right", fontsize=8.5, ncol=1)
        ax.set_ylim(-1.5, 2.2)
        dibujar(fig, "onda_plana.png")
    with sub[2]:
        qc.seccion("Una pared que se extiende hasta el infinito")
        st.markdown(
            "Imagina una partícula que viene desde la izquierda y encuentra, en x = 0, una región donde la energía potencial "
            "pasa de 0 a un valor V y se mantiene así para siempre (barrera de altura finita y espesor semi-infinito).")
        st.latex(r"x<0\ (\text{zona I}):\ V=0,\qquad x\ge0\ (\text{zona II}):\ V=V_0")
        st.markdown("Las ecuaciones de cada zona son las de una partícula libre, con energía cinética E en la zona I y E − V en la II:")
        st.latex(r"\text{Zona I: }\psi=Ae^{ikx},\ \hbar k=\sqrt{2mE}\qquad\text{Zona II: }\psi=A'e^{ik'x},\ \hbar k'=\sqrt{2m(E-V)}")
        qc.seccion("Cuando E < V: penetración")
        st.markdown(
            "Clásicamente la partícula no podría entrar en la pared. Pero si E < V, k′ es imaginario: k′ = iκ, con κ real, y "
            "en la zona II la función **ya no oscila**; queda una exponencial decreciente (la creciente se descarta porque "
            "divergiría):")
        st.latex(r"\psi=A'e^{-\kappa x},\qquad \hbar\kappa=\sqrt{2m(V-E)}")
        st.markdown(
            "Como la función de onda no vale cero dentro de la pared, la partícula puede encontrarse en una región "
            "clásicamente prohibida: es el efecto de **penetración**. La rapidez con que decae la fija κ: la amplitud cae a "
            "1/e de su valor en el borde a la distancia")
        st.latex(r"\frac{1}{\kappa}=\frac{\hbar}{\sqrt{2m(V-E)}}\qquad\text{(profundidad de penetración)}")
        d = profundidad_de_penetracion(ME, 3 * EV, 1 * EV)
        st.markdown(
            f"Ejemplo: un electrón de 1 eV frente a una pared de 3 eV penetra 1/κ = **{d * 1e9:.3f} nm**, aproximadamente el "
            "tamaño de un átomo. Por eso la penetración importa en superficies, electrodos y en todo proceso a escala atómica.")
    with sub[3]:
        qc.seccion("Mira la función de onda cerca de la pared")
        c1, c2, c3 = st.columns(3)
        with c1:
            nombre = st.selectbox("Partícula", list(PARTICULAS), key="lpp_part")
        with c2:
            E_ev = st.slider("Energía E [eV]", 0.1, 5.0, 1.0, 0.1, key="lpp_E")
        with c3:
            V_ev = st.slider("Altura de la pared V [eV]", 0.2, 10.0, 3.0, 0.1, key="lpp_V")
        if V_ev <= E_ev:
            st.warning("Aquí se estudia el caso E < V. Sube V o baja E.", icon=":material/info:")
            return
        m = PARTICULAS[nombre]
        k = numero_de_onda(m, E_ev * EV)
        kap = kappa(m, V_ev * EV, E_ev * EV)
        d = 1 / kap
        x = np.linspace(-4 * 2 * math.pi / k, 6 * d, 3000)
        psi, R, T = funcion_de_onda_pared(x, k, kap)
        fig, (a1, a2) = figura(10, 4.4, columnas=2)
        for ax in (a1, a2):
            ax.axvspan(0, x[-1] * 1e9, color=COL["potencial"], alpha=0.14)
            ax.axvline(0, color=COL["potencial"], lw=1.6)
            ax.set_xlabel("x [nm]")
        a1.plot(x * 1e9, psi.real, color=COL["onda"], lw=2.0, label="Re ψ")
        a1.plot(x * 1e9, psi.imag, color=COL["interferencia"], lw=1.5, ls="--", label="Im ψ")
        a1.set_title("Función de onda")
        a1.legend(fontsize=8.5, loc="upper right")
        a2.plot(x * 1e9, np.abs(psi) ** 2, color=COL["densidad"], lw=2.2)
        a2.axvline(d * 1e9, color=COL["energia"], ls=":", lw=1.6, label=f"1/κ = {d * 1e9:.3f} nm")
        a2.set_title("|ψ|²: se mete en la pared y decae")
        a2.legend(fontsize=8.5, loc="upper right")
        x2 = x[x >= 0]
        a1.set_xlim(x[0] * 1e9, x[-1] * 1e9)
        a2.set_xlim(x[0] * 1e9, x[-1] * 1e9)
        dibujar(fig, "penetracion.png")
        qc.metricas([("κ", f"{kap * 1e-9:.4g} nm⁻¹"), ("Profundidad 1/κ", f"{d * 1e9:.4g} nm"),
                     ("Longitud de onda (zona I)", f"{2 * math.pi / k * 1e9:.4g} nm"),
                     ("|ψ(0)|² / |ψ_inc|²", f"{abs(T) ** 2:.4g}  (= 4E/V = {4 * E_ev / V_ev:.4g})")], columnas=4)
        st.caption(
            "Complemento a las diapositivas: imponiendo que ψ y ψ' sean continuas en x = 0 se obtiene la onda reflejada "
            "R = (k − iκ)/(k + iκ), con |R| = 1: la pared refleja toda la onda, pero la función de onda penetra una "
            "distancia ~1/κ. A la izquierda se forma un patrón de interferencia entre la onda incidente y la reflejada.")
    with sub[4]:
        qc.seccion("Resumen de ecuaciones")
        qc.tabla_libre([
            {"Concepto": "Partícula libre", "Ecuación": "ψ± = A± e^(±ikx),  k = √(2mE)/ħ"},
            {"Concepto": "Energía y momento", "Ecuación": "E = ħ²k²/2m,  p = ħk = h/λ"},
            {"Concepto": "Autovalores del momento", "Ecuación": "p̂ ψ± = ±ħk ψ±"},
            {"Concepto": "Pared, E < V (zona II)", "Ecuación": "ψ = A′ e^(−κx),  κ = √(2m(V − E))/ħ"},
            {"Concepto": "Profundidad de penetración", "Ecuación": "1/κ = ħ / √(2m(V − E))"},
        ])


PREGUNTAS = [
    {"enunciado": "¿Está cuantizada la energía de una partícula libre?",
     "opciones": ["No: cualquier E ≥ 0 es posible", "Sí, E = n²h²/8ma²", "Sí, E = (n + ½)hν", "Solo si V ≠ 0"],
     "correcta": 0, "explicacion": "Sin confinamiento no hay condiciones de contorno que cuantifiquen la energía."},
    {"enunciado": "La función ψ⁺ = A e^(ikx) es autofunción del operador momento con autovalor...",
     "opciones": ["+ħk", "−ħk", "ħ/k", "0"],
     "correcta": 0, "explicacion": "p̂ e^(ikx) = −iħ (ik) e^(ikx) = ħk e^(ikx)."},
    {"enunciado": "Si el momento de una partícula libre es exactamente ħk, su posición es...",
     "opciones": ["completamente indeterminada (probabilidad uniforme)", "exactamente x = 0", "x = ħk",
                  "determinada con error ħ/2"],
     "correcta": 0, "explicacion": "|ψ|² es constante: la partícula está igual de probable en cualquier lugar."},
    {"enunciado": "Una partícula con E < V incide sobre una pared de espesor infinito. Dentro de la pared, ψ...",
     "opciones": ["decae exponencialmente como e^(−κx)", "oscila como e^(ik′x)", "vale exactamente 0", "crece como e^(κx)"],
     "correcta": 0, "explicacion": "Con E < V, k′ es imaginario y la solución aceptable es la exponencial decreciente."},
    {"enunciado": "Un electrón de 1 eV incide sobre una pared de 5 eV. La profundidad de penetración es aproximadamente...",
     "opciones": ["0.098 nm", "0.98 nm", "9.8 nm", "0.0098 nm"],
     "correcta": 0, "explicacion": "1/κ = ħ/√(2m·4 eV) = 0.1952 nm / √4 ≈ 0.098 nm (para 1 eV de diferencia vale 0.195 nm)."},
    {"enunciado": "Si la altura V de la pared aumenta (con E fijo), la profundidad de penetración...",
     "opciones": ["disminuye", "aumenta", "no cambia", "se hace infinita"],
     "correcta": 0, "explicacion": "κ crece con V − E, y 1/κ disminuye."},
]
