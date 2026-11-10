"""
teoria/hidrogeno.py — Teoría: El átomo de hidrógeno (ecuación radial, funciones radiales y orbitales)
"""

import numpy as np
import streamlit as st

import hidrogeno_radial as hr
import quantum_lab_comun as qc
from teoria._util import COL, dibujar, figura


def mostrar() -> None:
    sub = st.tabs(["El problema", "Ecuación radial", "Funciones radiales", "Números cuánticos y energía",
                   "Distribución radial", "Orbitales", "Calculadora", "Resumen"])
    with sub[0]:
        qc.seccion("Un electrón en el campo de Coulomb")
        st.markdown("Un átomo **hidrogenoide** tiene un solo electrón y un núcleo de carga +Ze (H, He⁺, Li²⁺…). Como la energía potencial "
                    "solo depende de la distancia r al núcleo, el problema tiene simetría esférica y la solución se separa en una parte "
                    "radial y una parte angular.")
        st.latex(r"\hat H=-\frac{\hbar^2}{2\mu}\nabla^2-\frac{Ze^2}{4\pi\varepsilon_0\,r},\qquad \mu=\frac{m_em_N}{m_e+m_N}")
        st.markdown("μ es la **masa reducida**: como el núcleo no es infinitamente pesado, el electrón y el núcleo giran alrededor de su centro de "
                    "masa. Para el hidrógeno μ ≈ 0.99946 mₑ. Se busca ψ(r, θ, φ) con Ĥψ = Eψ.")
        st.latex(r"\psi_{nlm_l}(r,\theta,\varphi)=R_{nl}(r)\,Y_l^{m_l}(\theta,\varphi)")
        st.markdown("La parte angular Yₗᵐ son los **armónicos esféricos** del tema de rotación (autofunciones de L̂² y L̂_z). Todo lo nuevo "
                    "está en la función radial R_nl(r).")
    with sub[1]:
        qc.seccion("De ψ a la ecuación radial")
        st.markdown("Al sustituir ψ = R(r)Y y usar L̂²Y = ħ²l(l+1)Y, la ecuación para u(r) = r R(r) es unidimensional:")
        st.latex(r"-\frac{\hbar^2}{2\mu}\frac{d^2u}{dr^2}+\left[\frac{l(l+1)\hbar^2}{2\mu r^2}-\frac{Ze^2}{4\pi\varepsilon_0 r}\right]u=E\,u")
        st.markdown("El corchete es un **potencial efectivo**: la atracción de Coulomb más el término centrífugo l(l+1)ħ²/2μr², repulsivo, que "
                    "crece con l y mantiene al electrón lejos del núcleo.")
        st.markdown("**Comportamiento límite** (determina la forma de la solución):\n"
                    "- Cerca del núcleo domina el término centrífugo: R(r) ≈ A rˡ. Solo los estados s (l = 0) son distintos de cero en r = 0.\n"
                    "- Lejos del núcleo, R(r) decae como una exponencial e^(−Zr/na₀): la solución debe ser normalizable.")
        st.markdown("Exigir una solución finita y normalizable cuantiza la energía: solo existen soluciones para n = 1, 2, 3, … con l ≤ n − 1.")
    with sub[2]:
        qc.seccion("Las soluciones: polinomios de Laguerre asociados")
        st.latex(r"\rho=\frac{2Zr}{na_0},\qquad R_{nl}(r)=N_{nl}\;e^{-\rho/2}\,\rho^{\,l}\,L_{n-l-1}^{\,2l+1}(\rho)")
        st.latex(r"N_{nl}^2=\left(\frac{2Z}{na_0}\right)^3\frac{(n-l-1)!}{2n\,(n+l)!},\qquad \int_0^\infty R_{nl}^2\,r^2\,dr=1")
        st.markdown("Los textos usan distintas definiciones de los polinomios de Laguerre (y por tanto de N y del signo global); **R² y todas las "
                    "magnitudes físicas son las mismas**. El polinomio tiene n − l − 1 ceros: son los **nodos radiales**.")
        st.markdown("**Ejemplo de la clase:** nodos de R₃₀. El polinomio 6 − 6ρ + ρ² se anula en ρ = 3 ± √3, es decir")
        st.latex(r"r=\left(3\pm\sqrt3\right)\frac{3a_0}{2Z}\;\approx\;1.90\,a_0\ \text{y}\ 7.10\,a_0\quad(Z=1)")
        c1, c2 = st.columns(2)
        r = np.linspace(0, 30, 1500)
        with c1:
            fig, ax = figura(5.4, 3.6)
            for (n, l), col in zip(((1, 0), (2, 0), (2, 1), (3, 0)), (COL["onda"], COL["densidad"], COL["energia"], COL["cinetica"])):
                ax.plot(r, hr.funcion_radial(n, l, r), color=col, lw=2, label=hr.nombre_estado(n, l))
            ax.axhline(0, color=COL["gris"], lw=0.8)
            ax.set_xlabel("r / a₀"); ax.set_ylabel("a₀^(3/2) R(r)"); ax.set_title("Funciones radiales"); ax.legend(); ax.grid(alpha=0.25)
            dibujar(fig)
        with c2:
            st.markdown("**Primeras funciones radiales (Z = 1, r en a₀):**")
            st.latex(r"R_{10}=2e^{-r},\quad R_{20}=\frac{2-r}{2\sqrt2}e^{-r/2},\quad R_{21}=\frac{r}{2\sqrt6}e^{-r/2}")
            st.caption("Estas tres fórmulas se usan como prueba independiente en el simulador. R₁₀ no tiene nodos; R₂₀ tiene uno en r = 2a₀.")
    with sub[3]:
        qc.seccion("Energía y papel de cada número cuántico")
        st.latex(r"E_n=-\frac{Z^2\mu e^4}{32\pi^2\varepsilon_0^2\hbar^2}\,\frac{1}{n^2}\;\xrightarrow{\ Z=1,\ \mu\to m_e\ }\;-\frac{13.6057\ \text{eV}}{n^2}")
        st.markdown("La energía **solo depende de n**: es independiente de l y de mₗ, así que cada nivel es **n²-veces degenerado** (esta degeneración "
                    "en l es propia del potencial de Coulomb).")
        qc.tabla_libre([
            {"Número": "n = 1, 2, 3…", "Fija": "la energía", "Además": "l = 0, …, n−1; n² orbitales; n − 1 nodos en total"},
            {"Número": "l = 0, …, n−1", "Fija": "el módulo del momento angular orbital √(l(l+1))ħ", "Además": "2l+1 orbitales; l nodos angulares; n−l−1 radiales"},
            {"Número": "mₗ = −l, …, l", "Fija": "la componente z: mₗħ", "Además": "para n y l dados, identifica cada orbital"},
        ])
        st.caption("Letras: l = 0 → s, 1 → p, 2 → d, 3 → f.")
    with sub[4]:
        qc.seccion("¿Dónde está el electrón? P(r) = r²R²")
        st.markdown("La probabilidad de hallar al electrón entre dos esferas de radios r y r + dr, sin importar la dirección, resulta de integrar |ψ|² "
                    "sobre los ángulos; como los armónicos esféricos están normalizados, solo queda la parte radial:")
        st.latex(r"P(r)\,dr=R_{nl}^2(r)\,r^2\,dr,\qquad \int_0^\infty P(r)\,dr=1")
        st.markdown("- P(r) es cero en r = 0 y tiende a cero en el infinito.\n"
                    "- Para 1s: P(r) = 4(Z/a₀)³ r² e^(−2Zr/a₀), con máximo en r = a₀/Z: el radio de Bohr es el radio **más probable** del estado fundamental.\n"
                    "- La **distancia esperada** es:")
        st.latex(r"\langle r\rangle=\frac{a_0}{2Z}\left[3n^2-l(l+1)\right]")
        st.markdown("Para 1s, ⟨r⟩ = 3a₀/2 > a₀: la cola exterior de P desplaza el promedio. Para l = n − 1 (sin nodos radiales) el máximo está en n²a₀.")
    with sub[5]:
        qc.seccion("Orbitales atómicos")
        st.markdown("Las funciones ψ_nlm de las funciones de onda de un electrón se llaman **orbitales**. Son reales si mₗ = 0 y complejas en otro caso. "
                    "Para dibujarlas se forman combinaciones reales de ψ(+mₗ) y ψ(−mₗ): los orbitales pₓ, p_y, p_z; d_z², d_xz, d_yz, d_x²−y², d_xy.")
        st.latex(r"\psi_{100}=\frac{1}{\sqrt\pi}\left(\frac{1}{a_0}\right)^{3/2}e^{-r/a_0},\qquad \psi_{2p_z}=\frac{1}{4\sqrt{2\pi}}\left(\frac{1}{a_0}\right)^{3/2}\frac{r}{a_0}\,e^{-r/2a_0}\cos\theta")
        st.markdown("Los orbitales s son esféricos (sin momento angular). La representación con sombreado o con superficies límite es geométrica: "
                    "la nube de probabilidad del simulador del átomo cuántico 3D muestra estas formas.")
    with sub[6]:
        qc.seccion("Calculadora de un estado")
        c1, c2 = st.columns(2)
        n = c1.number_input("n", 1, 30, 3, key="th_hid_n")
        st.session_state["th_hid_l"] = min(st.session_state.get("th_hid_l", 1), int(n) - 1)       # l ≤ n − 1
        l = c2.number_input("l", 0, int(n) - 1, key="th_hid_l")
        n, l = int(n), int(l)
        nodos = hr.nodos_radiales(n, l)
        qc.metricas([("Estado", hr.nombre_estado(n, l)), ("Energía", f"{hr.energia_estado(n)[0]:.5f} eV"),
                     ("⟨r⟩", f"{hr.distancia_esperada(n, l):.4f} a₀"), ("Radio más probable", f"{hr.radio_mas_probable(n, l):.4f} a₀"),
                     ("Nodos radiales n−l−1", f"{len(nodos)}"), ("Orbitales del nivel n²", f"{n ** 2}")], columnas=3)
        if len(nodos):
            st.caption("Nodos (a₀): " + ", ".join(f"{x:.4f}" for x in nodos))
        st.button("Abrir el simulador", key="th_hid_sim", icon=":material/arrow_forward:",
                  on_click=lambda: st.session_state.update(ql_pagina="radial", rad_n=n, rad_l=l))
    with sub[7]:
        qc.seccion("Resumen de ecuaciones")
        qc.tabla_libre([
            {"Concepto": "Función de onda", "Ecuación": "ψ(r,θ,φ) = R_nl(r) Yₗᵐ(θ,φ)"},
            {"Concepto": "Ecuación radial", "Ecuación": "−(ħ²/2μ)u″ + [l(l+1)ħ²/2μr² − Ze²/4πε₀r]u = Eu,  u = rR"},
            {"Concepto": "Energía", "Ecuación": "Eₙ = −Z²μe⁴/(32π²ε₀²ħ²) · 1/n² = −13.6057 eV · Z²/n²"},
            {"Concepto": "Números cuánticos", "Ecuación": "n ≥ 1;  0 ≤ l ≤ n−1;  −l ≤ mₗ ≤ l"},
            {"Concepto": "Nodos", "Ecuación": "radiales n−l−1;  angulares l;  totales n−1"},
            {"Concepto": "Distribución radial", "Ecuación": "P(r) = r²R²;  ∫P dr = 1"},
            {"Concepto": "Distancia esperada", "Ecuación": "⟨r⟩ = (a₀/2Z)[3n² − l(l+1)]"},
            {"Concepto": "Degeneración", "Ecuación": "n² por nivel (2l+1 por subcapa)"},
        ])


PREGUNTAS = [
    {"enunciado": "En la ecuación radial, el término l(l+1)ħ²/2μr² representa…",
     "opciones": ["la atracción de Coulomb", "una barrera centrífuga repulsiva", "la energía cinética total", "el espín"],
     "correcta": 1, "explicacion": "Viene del momento angular: es repulsivo y mantiene al electrón lejos del núcleo cuando l crece."},
    {"enunciado": "Cerca del núcleo, R_nl(r) se comporta como…",
     "opciones": ["r^l", "e^(−r)", "1/r", "constante"], "correcta": 0,
     "explicacion": "Domina el término centrífugo: R ≈ A rˡ. Solo l = 0 es distinto de cero en r = 0."},
    {"enunciado": "La energía del átomo de hidrógeno depende de…",
     "opciones": ["n y l", "solo n", "n, l y mₗ", "solo l"], "correcta": 1,
     "explicacion": "Eₙ = −13.6 eV/n²: es independiente de l y mₗ (degeneración n²)."},
    {"enunciado": "El número de nodos radiales de un orbital (n, l) es…",
     "opciones": ["n", "n − l", "n − l − 1", "l"], "correcta": 2, "explicacion": "Es el número de ceros del polinomio de Laguerre: n − l − 1."},
    {"enunciado": "Los orbitales con n = 3 son en total…",
     "opciones": ["3", "6", "9", "18"], "correcta": 2, "explicacion": "n² = 9 = 1 (3s) + 3 (3p) + 5 (3d)."},
    {"enunciado": "La distribución radial de probabilidad es…",
     "opciones": ["R(r)", "|R(r)|²", "r²|R(r)|²", "4π|R(r)|²"], "correcta": 2,
     "explicacion": "P(r) = r²R²: P(r) dr es la probabilidad de hallar al electrón entre las esferas r y r + dr."},
    {"enunciado": "El radio más probable de 1s y su ⟨r⟩ son…",
     "opciones": ["a₀ y a₀", "a₀ y 3a₀/2", "3a₀/2 y a₀", "2a₀ y 3a₀/2"], "correcta": 1,
     "explicacion": "El máximo de P está en a₀; ⟨r⟩ = (a₀/2)(3 − 0) = 3a₀/2 por la cola exterior."},
]
