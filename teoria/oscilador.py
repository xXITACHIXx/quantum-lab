"""
teoria/oscilador.py — Teoría: El oscilador armónico cuántico
"""

import math

import numpy as np
import streamlit as st
from numpy.polynomial import hermite as Hm
from scipy import constants as const
from scipy.integrate import trapezoid
from scipy.special import eval_hermite, factorial

import quantum_lab_comun as qc
from teoria._util import C, COL, EV, H, HBAR, dibujar, figura

U_MASA = const.atomic_mass

# Molécula: (masas atómicas en u, número de onda vibracional experimental ω̃ₑ [cm⁻¹], descripción)
MOLECULAS = {
    "H₂": (1.00782503 / 2, 4401.21),
    "HCl (H³⁵Cl)": (1.00782503 * 34.96885268 / (1.00782503 + 34.96885268), 2990.95),
    "CO": (12.0 * 15.99491462 / (12.0 + 15.99491462), 2169.81),
    "N₂": (14.0030740 / 2, 2358.57),
    "O₂": (15.99491462 / 2, 1580.19),
}


def alfa(mu: float, k: float) -> float:
    """α = (μk/ħ²)^{1/4}   [1/m]."""
    return (mu * k / HBAR ** 2) ** 0.25


def frecuencia(mu: float, k: float) -> float:
    """ν = (1/2π)√(k/μ)   [Hz]."""
    return math.sqrt(k / mu) / (2 * math.pi)


def energia(n: int, mu: float, k: float) -> float:
    """Eₙ = (n + ½) h ν   [J]."""
    return (n + 0.5) * H * frecuencia(mu, k)


def constante_de_fuerza(mu: float, numero_de_onda_cm: float) -> float:
    """k = μ (2π c ω̃)²  con ω̃ en cm⁻¹   [N/m]."""
    return mu * (2 * math.pi * C * numero_de_onda_cm * 100) ** 2


def psi(n: int, z):
    """ψₙ en la variable adimensional z = αx, normalizada respecto de z: Nₙ Hₙ(z) e^{−z²/2}, Nₙ = (1/(2ⁿ n! √π))^{1/2}."""
    Nn = (1 / (2.0 ** n * factorial(n) * math.sqrt(math.pi))) ** 0.5
    return Nn * eval_hermite(n, z) * np.exp(-z ** 2 / 2)


def nodos(n: int):
    """Raíces de Hₙ(z): los nodos de ψₙ están en x = z/α."""
    if n == 0:
        return np.array([])
    return np.sort(Hm.hermroots([0] * n + [1]))


def energias_medias_adimensionales(n: int, puntos: int = 40001):
    """
    ⟨T⟩ y ⟨V⟩ en unidades de ħω para el estado n, por integración numérica en z = αx:
    T = ∫ψ (−½ψ'') dz,  V = ∫ ψ (½z²) ψ dz  (unidades de ħω).
    """
    z = np.linspace(-14, 14, puntos)
    p = psi(n, z)
    dz = z[1] - z[0]
    d1 = np.gradient(p, dz)
    T = 0.5 * trapezoid(d1 ** 2, z)
    V = 0.5 * trapezoid(z ** 2 * p ** 2, z)
    return float(T), float(V)


def mostrar() -> None:
    sub = st.tabs(["El potencial armónico", "Funciones de onda", "Energías", "Teorema del virial",
                   "Calculadora molecular", "Resumen del simulador"])
    with sub[0]:
        qc.seccion("¿Por qué un oscilador?")
        st.markdown(
            "Cerca de la distancia de equilibrio, la forma de la energía potencial de un enlace se aproxima bien por una "
            "parábola. Hay oscilaciones armónicas cuando una parte del sistema siente una **fuerza restauradora proporcional "
            "al desplazamiento** desde el equilibrio. En una dimensión es la ley de Hooke, F = −kx, y k es la constante de fuerza.")
        st.latex(r"V(x)=\tfrac12\,k\,x^2")
        st.markdown(
            "Para un enlace débil o a temperaturas altas el potencial real (tipo Morse) se aparta de la parábola y el modelo "
            "armónico deja de ser suficiente. Para una molécula diatómica, la masa que vibra es la masa reducida μ.")
        st.markdown("Hay que resolver la ecuación de Schrödinger con ese potencial:")
        st.latex(r"-\frac{\hbar^2}{2\mu}\frac{d^2\psi_n}{dx^2}+\frac12kx^2\psi_n=E_n\psi_n")
    with sub[1]:
        qc.seccion("Gaussiana por polinomio")
        st.markdown("Las soluciones tienen la forma de una gaussiana, e^(−z²), multiplicada por un polinomio en el desplazamiento:")
        st.latex(r"\psi_n(x)=N_n\,H_n(\alpha x)\,e^{-\alpha^2x^2/2},\qquad \alpha=\left(\frac{\mu k}{\hbar^2}\right)^{1/4},\qquad N_n=\left(\frac{\alpha}{2^n n!\sqrt\pi}\right)^{1/2}")
        st.markdown("α tiene unidades de 1/longitud (por eso αx no tiene dimensiones) y Hₙ son los **polinomios de Hermite**.")
        st.markdown(
            "Propiedades de los polinomios de Hermite:\n"
            "- Ecuación diferencial: Hₙ″ − 2zHₙ′ + 2nHₙ = 0.\n"
            "- Recurrencia: Hₙ₊₁ = 2zHₙ − 2nHₙ₋₁.\n"
            "- Ortogonalidad: ∫Hₙ Hₙ′ e^(−z²) dz = 0 si n ≠ n′.\n"
            "- Normalización: ∫Hₙ² e^(−z²) dz = √π 2ⁿ n!.")
        st.markdown("Los primeros: H₀ = 1, H₁ = 2z, H₂ = 4z² − 2, H₃ = 8z³ − 12z, H₄ = 16z⁴ − 48z² + 12.")
        st.markdown(
            "El estado fundamental es una gaussiana pura, ψ₀ = (α/√π)^(1/2) e^(−α²x²/2). El estado n = 1 es esa gaussiana por 2αx "
            "con otra constante de normalización. El número de nodos aumenta con n, y las funciones pares son simétricas y "
            "las impares antisimétricas respecto de x = 0.")
        n = st.slider("Estado n", 0, 10, 4, key="oc_n")
        z = np.linspace(-6, 6, 1200)
        p = psi(n, z)
        zn = nodos(n)
        fig, (a1, a2) = figura(10, 4.3, columnas=2)
        a1.plot(z, p, color=COL["onda"], lw=2.2)
        a1.plot(zn, np.zeros_like(zn), "o", color=COL["energia"], ms=7, label="nodos")
        a1.axhline(0, color="black", lw=0.7)
        a1.set_xlabel("z = αx")
        a1.set_title(f"ψ{n}: {n} nodos")
        a1.legend(fontsize=8.5)
        a2.plot(z, p ** 2, color=COL["densidad"], lw=2.2)
        a2.fill_between(z, p ** 2, color=COL["densidad"], alpha=0.15)
        a2.set_xlabel("z = αx")
        a2.set_title(f"|ψ{n}|²")
        dibujar(fig, "oscilador_psi.png")
        if n:
            st.caption("Nodos en z = " + ", ".join(f"{v:+.4f}" for v in zn) + ". Para n = 4: ±0.5246 y ±1.6507.")
    with sub[2]:
        qc.seccion("Una escalera de niveles igualmente espaciados")
        st.latex(r"E_n=\left(n+\tfrac12\right)h\nu,\qquad \nu=\frac1{2\pi}\sqrt{\frac k\mu},\qquad n=0,1,2,\dots")
        st.markdown(
            "- La energía está cuantizada, como cabía esperar de la forma del potencial.\n"
            "- El estado más bajo tiene **energía del punto cero**, E₀ = ½hν > 0: clásicamente, el oscilador nunca deja de "
            "fluctuar alrededor del equilibrio.\n"
            "- Los niveles forman una escalera de separación constante, Eₙ₊₁ − Eₙ = hν, sea cual sea ν.")
        st.markdown(
            "El espaciado depende de la molécula:\n"
            "- A mayor masa, ν es menor y los niveles se acercan.\n"
            "- A mayor constante de fuerza (potencial más confinante), ν ∝ k^(1/2) y los niveles se separan más.\n"
            "- En el límite k → 0 la parábola no confina, no hay cuantización y se vuelve a la partícula libre.")
        qc.seccion("Ejemplo: ¿satisface e^(−βx²) la ecuación?")
        st.markdown(
            "Al aplicar Ĥ a e^(−βx²) aparecen dos términos con x² que solo se cancelan si β = √(kμ)/(2ħ). Con ese valor, "
            "Ĥe^(−βx²) = (ħ/2)√(k/μ) e^(−βx²): la función es autofunción, con energía E = ½ħ√(k/μ) = ½hν, es decir, **es el "
            "estado fundamental**. Además β = α²/2, de acuerdo con ψ₀.")
        st.latex(r"\beta=\frac{\sqrt{k\mu}}{2\hbar}=\frac{\alpha^2}{2},\qquad E=\frac\hbar2\sqrt{\frac k\mu}=\frac12h\nu")
    with sub[3]:
        qc.seccion("Reparto entre energía cinética y potencial")
        st.markdown(
            "Si la energía potencial es de la forma V = a xˢ, el **teorema del virial** relaciona las energías medias:")
        st.latex(r"2\langle E_k\rangle=s\,\langle E_p\rangle\ \Rightarrow\ E=\langle E_k\rangle+\langle E_p\rangle=\left(1+\frac2s\right)\langle E_k\rangle")
        st.markdown("Para el oscilador armónico, s = 2: $\\langle E_k\\rangle$ = $\\langle E_p\\rangle$ y E = 2$\\langle E_k\\rangle$. Al aumentar la energía total crecen ambas.")
        n = st.slider("Estado n", 0, 12, 1, key="oc_nv")
        T, V = energias_medias_adimensionales(n)
        qc.metricas([("⟨E_k⟩", f"{T:.5f} ħω"), ("⟨E_p⟩", f"{V:.5f} ħω"), ("⟨E_k⟩ + ⟨E_p⟩", f"{T + V:.5f} ħω"),
                     ("(n + ½)", f"{n + 0.5:.5f}")], columnas=4)
        st.caption("Calculado integrando numéricamente ψₙ: $\\langle E_k\\rangle$ = $\\langle E_p\\rangle$ = E/2, tal como pide el virial. Para n = 1 resulta 3/4 ħω cada uno.")
    with sub[4]:
        qc.seccion("Vibración de moléculas diatómicas")
        st.markdown("Con la masa reducida μ y el número de onda vibracional experimental se obtiene la constante de fuerza del "
                    "enlace y los niveles del oscilador armónico equivalente.")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.selectbox("Molécula", list(MOLECULAS) + ["Personalizada"], key="oc_mol")
        if nombre == "Personalizada":
            with c2:
                mu_u = st.number_input("Masa reducida μ [u]", 0.1, 500.0, 6.86, format="%.5g", key="oc_mu")
                k_nm = st.number_input("Constante de fuerza k [N/m]", 1.0, 5000.0, 1857.0, format="%.6g", key="oc_k")
            mu = mu_u * U_MASA
            k = k_nm
        else:
            mu = MOLECULAS[nombre][0] * U_MASA
            k = constante_de_fuerza(mu, MOLECULAS[nombre][1])
            with c2:
                st.markdown(f"μ = **{MOLECULAS[nombre][0]:.5f} u**  \nk = **{k:.4g} N/m** (deducida de ω̃ₑ = {MOLECULAS[nombre][1]} cm⁻¹)")
        nu = frecuencia(mu, k)
        qc.metricas([("ν", f"{nu:.4g} Hz"), ("ν̃ = ν/c", f"{nu / (C * 100):.5g} cm⁻¹"), ("E₀ = ½hν", f"{0.5 * H * nu / EV:.5g} eV"),
                     ("Espaciado hν", f"{H * nu / EV:.5g} eV")], columnas=4)
        qc.tabla_libre([{"n": str(n), "Eₙ [eV]": f"{energia(n, mu, k) / EV:.6g}", "Eₙ [kJ/mol]": f"{energia(n, mu, k) * const.N_A / 1000:.6g}"}
                        for n in range(0, 6)], numericas=("Eₙ [eV]", "Eₙ [kJ/mol]"))
        st.caption("Las constantes de fuerza son efectivas, deducidas de la frecuencia de vibración medida; la aproximación "
                   "armónica es buena cerca del equilibrio.")
    with sub[5]:
        qc.seccion("Resumen de ecuaciones (simulador)")
        st.latex(r"V(x)=\tfrac12 m\omega^2x^2\qquad x_0=\sqrt{\frac{\hbar}{m\omega}}\qquad E_n=\hbar\omega\left(n+\tfrac12\right)")
        st.latex(r"\psi_n(x)=\frac{1}{\sqrt{2^n n!}}\frac{1}{\pi^{1/4}\sqrt{x_0}}H_n\!\left(\frac{x}{x_0}\right)e^{-x^2/2x_0^2}")
        st.latex(r"\langle T\rangle=\langle V\rangle=\frac{E_n}{2}\qquad \langle x\rangle=0\qquad \langle x^2\rangle=\left(n+\tfrac12\right)x_0^2")
        st.latex(r"x_n^{\rm retorno}=\pm\sqrt{2n+1}\,x_0\qquad \Psi(x,t)=\sum_n c_n\psi_n(x)e^{-i(n+1/2)\omega t}")
        st.latex(r"A=\sqrt{2n+1}\,x_0,\qquad P_{\rm cl}(x)=\frac{1}{\pi\sqrt{A^2-x^2}}")
        st.markdown("Aquí x₀ = 1/α y ω = √(k/m). **V(x)** (energía por unidad de probabilidad) no debe confundirse con "
                    "**u_V(x)** (densidad de energía potencial, en energía/longitud).")


PREGUNTAS = [
    {"enunciado": "Las energías permitidas del oscilador armónico cuántico son...",
     "opciones": ["(n + ½)hν", "n²h²/8ma²", "−13.6 eV/n²", "n h ν"],
     "correcta": 0, "explicacion": "Eₙ = (n + ½)hν, con n = 0, 1, 2…; el espaciado hν es constante."},
    {"enunciado": "La energía del punto cero del oscilador es...",
     "opciones": ["½hν", "0", "hν", "2hν"],
     "correcta": 0, "explicacion": "E₀ = ½hν > 0: el oscilador nunca está en reposo."},
    {"enunciado": "Si se duplica la constante de fuerza k, el espaciado entre niveles...",
     "opciones": ["se multiplica por √2", "se duplica", "se reduce a la mitad", "no cambia"],
     "correcta": 0, "explicacion": "ν = (1/2π)√(k/μ) ∝ √k, y el espaciado es hν."},
    {"enunciado": "¿Cuántos nodos tiene ψ₄ (sin contar el infinito)?",
     "opciones": ["4", "3", "5", "2"],
     "correcta": 0, "explicacion": "El número de nodos coincide con n: están en las raíces de H₄(z) = 16z⁴ − 48z² + 12."},
    {"enunciado": "Según el teorema del virial, en el oscilador armónico (V ∝ x²)...",
     "opciones": ["$\\langle E_k\\rangle$ = $\\langle E_p\\rangle$", "$\\langle E_k\\rangle$ = 2$\\langle E_p\\rangle$", "$\\langle E_p\\rangle$ = 0", "$\\langle E_k\\rangle$ = 0"],
     "correcta": 0, "explicacion": "2$\\langle E_k\\rangle$ = s$\\langle E_p\\rangle$ con s = 2."},
    {"enunciado": "Al aumentar la masa reducida μ de una molécula, manteniendo k, la frecuencia de vibración...",
     "opciones": ["disminuye", "aumenta", "no cambia", "se anula"],
     "correcta": 0, "explicacion": "ν ∝ 1/√μ."},
]
