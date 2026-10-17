"""
teoria/cuerpo_negro.py — Teoría: Radiación del cuerpo negro

Nota: el tema figura en la agenda del curso, pero las diapositivas recibidas no lo desarrollan; esta página
está escrita a partir de los textos de referencia del curso (Atkins; McQuarrie; Engel y Hehre).
"""

import numpy as np
import streamlit as st
from scipy.integrate import trapezoid

import quantum_lab_comun as qc
from teoria._util import C, COL, H, KB, SIGMA, figura, dibujar

B_WIEN = H * C / (4.965114231744276 * KB)          # constante de desplazamiento de Wien [m·K] (≈ 2.8978e-3)


def planck(lam, T):
    """Densidad espectral de energía u(λ, T) = 8πhc/λ⁵ · 1/(e^{hc/λkT} − 1)   [J m⁻⁴]."""
    x = H * C / (lam * KB * T)
    return 8 * np.pi * H * C / lam ** 5 / np.expm1(x)


def rayleigh_jeans(lam, T):
    """Predicción clásica u(λ, T) = 8πkT/λ⁴   [J m⁻⁴]."""
    return 8 * np.pi * KB * T / lam ** 4


def lambda_max(T):
    """Ley de desplazamiento de Wien: λ_max = b / T   [m]."""
    return B_WIEN / T


def energia_media_planck(nu, T):
    """Energía media de un oscilador de frecuencia ν: hν / (e^{hν/kT} − 1)   [J]."""
    return H * nu / np.expm1(H * nu / (KB * T))


MATERIAL = "Atkins, Friedman · McQuarrie · Engel y Hehre (textos del curso)"


def mostrar() -> None:
    sub = st.tabs(["El problema clásico", "La hipótesis de Planck", "Gráfica interactiva", "Resumen de ecuaciones"])
    with sub[0]:
        qc.seccion("Un cuerpo caliente brilla")
        st.markdown(
            "Todo cuerpo caliente emite radiación electromagnética. Un **cuerpo negro** es el caso ideal: absorbe toda la "
            "radiación que le llega y, por eso, lo que emite depende **solo de su temperatura**, no del material. Un "
            "horno con un pequeño orificio es una buena aproximación: la luz que sale por el hueco es radiación "
            "térmica en equilibrio con las paredes.")
        st.markdown("Los experimentos de finales del siglo XIX mostraron tres hechos:")
        st.markdown(
            "- A cada temperatura el espectro tiene un **máximo** y cae hacia longitudes de onda cortas y largas.\n"
            "- Al subir la temperatura, el máximo se desplaza hacia **longitudes de onda más cortas** (el hierro pasa del "
            "rojo al blanco azulado): ley de Wien.\n"
            "- La energía total emitida crece como **T⁴**: ley de Stefan–Boltzmann.")
        qc.seccion("Lo que predice la física clásica")
        st.markdown(
            "La radiación dentro de la cavidad se comporta como un conjunto de ondas estacionarias (modos). El número de "
            "modos por unidad de volumen y de longitud de onda crece como 8π/λ⁴. La física clásica asigna a cada modo la "
            "misma energía media, kT (equipartición). El resultado es la fórmula de Rayleigh–Jeans:")
        st.latex(r"u_{\rm RJ}(\lambda,T)=\frac{8\pi k_BT}{\lambda^4}")
        st.markdown(
            "Esta fórmula funciona a longitudes de onda largas, pero **crece sin límite** cuando λ → 0. Integrarla sobre "
            "todas las longitudes de onda da una energía total infinita: la **catástrofe ultravioleta**. Un horno "
            "caliente irradiaría una energía infinita en el ultravioleta, lo cual es absurdo y contradice el experimento. "
            "Ninguna corrección razonable dentro de la física clásica arregla el problema.")
    with sub[1]:
        qc.seccion("Energía cuantizada de los osciladores")
        st.markdown(
            "En 1900 Max Planck resolvió la discrepancia con una hipótesis: las paredes de la cavidad intercambian energía "
            "con la radiación en **paquetes**. Un oscilador de frecuencia ν solo puede tener las energías")
        st.latex(r"\varepsilon_n = n\,h\nu,\qquad n=0,1,2,\dots")
        st.markdown(
            "Al promediar con los pesos de Boltzmann e^(−nhν/kT) se obtiene la energía media de un modo (una suma "
            "geométrica):")
        st.latex(r"\langle\varepsilon\rangle=\frac{\sum_n n h\nu\,e^{-nh\nu/k_BT}}{\sum_n e^{-nh\nu/k_BT}}"
                 r"=\frac{h\nu}{e^{h\nu/k_BT}-1}")
        st.markdown(
            "Hay dos límites que aclaran todo:\n"
            "- Si hν ≪ kT (frecuencias bajas) los escalones son pequeños frente a la energía térmica y ⟨ε⟩ → kT: "
            "se recupera el resultado clásico.\n"
            "- Si hν ≫ kT (frecuencias altas) ⟨ε⟩ es exponencialmente pequeña: a esa temperatura casi nunca hay "
            "energía térmica suficiente para excitar ni un solo cuanto. Esto elimina la catástrofe ultravioleta.")
        st.markdown(
            "Es el primer ejemplo del primer criterio del curso: la física cuántica es imprescindible cuando el "
            "espaciado entre energías permitidas (aquí hν) no es pequeño frente a kT.")
        qc.seccion("La ley de Planck y sus consecuencias")
        st.latex(r"u(\lambda,T)=\frac{8\pi hc}{\lambda^5}\,\frac{1}{e^{hc/\lambda k_BT}-1}")
        st.markdown("De ella se derivan las dos leyes experimentales:")
        st.latex(r"\lambda_{\max}\,T=b\approx2.898\times10^{-3}\ \mathrm{m\,K}\qquad\text{(Wien)}")
        st.latex(r"M=\sigma T^4,\qquad \sigma=\frac{2\pi^5k_B^4}{15h^3c^2}=5.670\times10^{-8}\ \mathrm{W\,m^{-2}K^{-4}}\qquad\text{(Stefan–Boltzmann)}")
        st.markdown(
            "El ajuste de la curva experimental dio el valor de la nueva constante, h ≈ 6.6 × 10⁻³⁴ J·s, "
            "que reaparece después en el efecto fotoeléctrico y en la relación de De Broglie.")
    with sub[2]:
        qc.seccion("Comparar a Planck con la física clásica")
        c1, c2 = st.columns(2)
        with c1:
            T = st.slider("Temperatura T [K]", 1000, 10000, 5772, 100, key="cn_T",
                          help="5772 K es aproximadamente la temperatura de la superficie del Sol.")
        with c2:
            lmax_plot = st.slider("Longitud de onda máxima del gráfico [nm]", 1000, 6000, 3000, 250, key="cn_lmax")
        lam = np.linspace(50e-9, lmax_plot * 1e-9, 1500)
        up = planck(lam, T)
        urj = rayleigh_jeans(lam, T)
        lm = lambda_max(T)
        fig, ax = figura(9.5, 4.6)
        escala = 1e4
        ax.plot(lam * 1e9, up / escala, color=COL["densidad"], lw=2.4, label="Planck (cuántica)")
        ax.plot(lam * 1e9, np.minimum(urj, 3 * up.max()) / escala, color=COL["energia"], lw=1.8, ls="--",
                label="Rayleigh–Jeans (clásica)")
        ax.axvspan(380, 750, color=COL["onda"], alpha=0.10, label="luz visible")
        ax.axvline(lm * 1e9, color=COL["cinetica"], ls=":", lw=1.8, label=f"λ_máx de Wien = {lm * 1e9:.0f} nm")
        ax.set_ylim(0, 1.5 * up.max() / escala)
        ax.set_xlim(0, lmax_plot)
        ax.set_xlabel("longitud de onda λ [nm]")
        ax.set_ylabel(r"$u(\lambda,T)$  [$10^4$ J m$^{-4}$]")
        ax.set_title(f"Radiación de cuerpo negro a T = {T} K")
        ax.legend(loc="upper right", fontsize=9)
        dibujar(fig, f"cuerpo_negro_{T}K.png")
        lam_fino = np.linspace(20e-9, 60e-6, 400000)
        e_total = float(trapezoid(planck(lam_fino, T), lam_fino))
        a_rad = 4 * SIGMA / C
        qc.metricas([
            ("λ_máx (Wien)", f"{lm * 1e9:.1f} nm"),
            ("Exitancia M = σT⁴", f"{SIGMA * T ** 4:.4g} W/m²"),
            ("Energía total por volumen", f"{e_total:.4g} J/m³"),
            ("Comprobación: 4σT⁴/c", f"{a_rad * T ** 4:.4g} J/m³"),
        ], columnas=4)
        st.caption("La integral numérica de Planck coincide con 4σT⁴/c: es la ley de Stefan–Boltzmann. "
                   "Con la fórmula clásica esa integral diverge.")
        qc.seccion("Qué observar")
        st.markdown(
            "1. Aumentar T: el máximo crece muy rápido (∝ T⁵) y se corre hacia el azul.\n"
            "2. Aumentar el rango del eje horizontal: a longitudes de onda largas las dos curvas coinciden.\n"
            "3. Hacia λ pequeñas la curva clásica se dispara y la de Planck cae a cero.")
    with sub[3]:
        qc.seccion("Resumen")
        qc.tabla_libre([
            {"Concepto": "Energía de un cuanto", "Ecuación": "E = hν = hc/λ"},
            {"Concepto": "Energía media de un modo (Planck)", "Ecuación": "⟨ε⟩ = hν / (e^{hν/kT} − 1)"},
            {"Concepto": "Densidad espectral (Planck)", "Ecuación": "u(λ,T) = (8πhc/λ⁵) / (e^{hc/λkT} − 1)"},
            {"Concepto": "Rayleigh–Jeans (clásica)", "Ecuación": "u(λ,T) = 8πkT/λ⁴"},
            {"Concepto": "Desplazamiento de Wien", "Ecuación": "λ_máx · T = 2.898 × 10⁻³ m·K"},
            {"Concepto": "Stefan–Boltzmann", "Ecuación": "M = σT⁴, σ = 5.670 × 10⁻⁸ W m⁻² K⁻⁴"},
        ])
        st.caption(f"Referencias: {MATERIAL}.")


PREGUNTAS = [
    {"enunciado": "¿Qué es la «catástrofe ultravioleta»?",
     "opciones": ["La fórmula clásica predice una energía que crece sin límite hacia longitudes de onda cortas",
                  "El ultravioleta del Sol daña la atmósfera",
                  "Los cuerpos calientes dejan de emitir luz visible",
                  "La constante de Planck se vuelve infinita"],
     "correcta": 0,
     "explicacion": "Rayleigh–Jeans da u ∝ 1/λ⁴, que diverge cuando λ → 0 y lleva a una energía total infinita."},
    {"enunciado": "¿Qué supuso Planck para eliminar la divergencia?",
     "opciones": ["Que la luz es una partícula sin masa",
                  "Que la energía de un oscilador solo puede tomar valores nhν",
                  "Que la temperatura es negativa",
                  "Que las paredes no emiten radiación"],
     "correcta": 1,
     "explicacion": "Con energías cuantizadas, los modos de alta frecuencia casi nunca se excitan porque hν ≫ kT."},
    {"enunciado": "Si la temperatura de un cuerpo negro se duplica, la longitud de onda del máximo de emisión...",
     "opciones": ["se duplica", "se reduce a la mitad", "no cambia", "se hace cuatro veces menor"],
     "correcta": 1,
     "explicacion": "Ley de Wien: λ_máx · T = constante, así que λ_máx es inversamente proporcional a T."},
    {"enunciado": "Si la temperatura se duplica, la energía total emitida por unidad de área se multiplica por...",
     "opciones": ["2", "4", "8", "16"],
     "correcta": 3,
     "explicacion": "Stefan–Boltzmann: M = σT⁴, y 2⁴ = 16."},
    {"enunciado": "¿Cuándo coinciden la fórmula de Planck y la clásica?",
     "opciones": ["Cuando hν ≫ kT", "Cuando hν ≪ kT, es decir, a frecuencias bajas",
                  "Nunca", "Solo a T = 0"],
     "correcta": 1,
     "explicacion": "Si el escalón hν es pequeño frente a kT, ⟨ε⟩ → kT, el valor clásico."},
]
