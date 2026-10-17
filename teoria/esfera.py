"""
teoria/esfera.py — Teoría: Rotación y momento angular
"""

import math

import numpy as np
import streamlit as st
from scipy import constants as const

import quantum_lab_comun as qc
from teoria._util import C, COL, HBAR, dibujar, figura

U_MASA = const.atomic_mass

# Molécula: (masa reducida [u], longitud de enlace r_e [pm])
MOLECULAS = {
    "H₂": (1.00782503 / 2, 74.14),
    "HCl (H³⁵Cl)": (1.00782503 * 34.96885268 / (1.00782503 + 34.96885268), 127.46),
    "CO": (12.0 * 15.99491462 / (12.0 + 15.99491462), 112.83),
    "N₂": (14.0030740 / 2, 109.77),
    "O₂": (15.99491462 / 2, 120.75),
}


def momento_de_inercia(mu: float, r: float) -> float:
    """I = μ r²   [kg m²]."""
    return mu * r ** 2


def energia_anillo(m: int, I: float) -> float:
    """E_m = m² ħ² / 2I   [J]."""
    return m ** 2 * HBAR ** 2 / (2 * I)


def energia_esfera(l: int, I: float) -> float:
    """E_l = l(l + 1) ħ² / 2I   [J]."""
    return l * (l + 1) * HBAR ** 2 / (2 * I)


def phi_anillo(m: int, phi):
    """Φ_m(φ) = e^{imφ} / √(2π)."""
    return np.exp(1j * m * phi) / math.sqrt(2 * math.pi)


def angulo_minimo(l: int) -> float:
    """Menor ángulo (grados) entre el vector L y el eje z: cosθ = l/√(l(l+1))."""
    return math.degrees(math.acos(l / math.sqrt(l * (l + 1))))


def angulos_permitidos(l: int):
    """Ángulos θ (grados) con cosθ = m/√(l(l+1)) para m = l, …, −l."""
    return [(m, math.degrees(math.acos(m / math.sqrt(l * (l + 1))))) for m in range(l, -l - 1, -1)]


def _armonico(l: int, m: int, theta, phi):
    try:
        from scipy.special import sph_harm_y
        return sph_harm_y(l, m, theta, phi)
    except ImportError:                                     # SciPy < 1.15
        from scipy.special import sph_harm
        return sph_harm(m, l, phi, theta)


def autovalor_legendriano(l: int, m: int, theta0: float = 0.9, phi0: float = 0.4, h: float = 1e-4):
    """
    Evalúa numéricamente −Λ²Y / Y en un punto, con Λ² = (1/sin²θ)∂²_φ + (1/sinθ)∂_θ(sinθ ∂_θ), usando diferencias
    finitas. Debe valer l(l + 1).
    """
    f = lambda t, p: _armonico(l, m, t, p)
    d2phi = (f(theta0, phi0 + h) - 2 * f(theta0, phi0) + f(theta0, phi0 - h)) / h ** 2
    g = lambda t: math.sin(t) * (f(t + h, phi0) - f(t - h, phi0)) / (2 * h)
    dtheta = (g(theta0 + h) - g(theta0 - h)) / (2 * h)
    lam = d2phi / math.sin(theta0) ** 2 + dtheta / math.sin(theta0)
    return float((-lam / f(theta0, phi0)).real)


def mostrar() -> None:
    sub = st.tabs(["Rotación en un plano", "Rotación en 3D", "Cuantización del momento angular",
                   "Calculadora molecular", "Resumen del simulador"])
    with sub[0]:
        qc.seccion("Separar los movimientos")
        st.markdown(
            "Si se desprecia el acoplamiento entre traslación, vibración y rotación, el hamiltoniano de una molécula es una "
            "suma, Ĥ = $\\hat H_{trans}$ + $\\hat H_{vib}$ + $\\hat H_{rot}$. La función de onda es el producto de las tres y la energía, la suma de las "
            "tres contribuciones. Así se puede resolver cada movimiento por separado. La magnitud que caracteriza la "
            "rotación es el **momento de inercia**:")
        st.latex(r"I=\mu r^2,\qquad \psi_{\rm total}=\psi_{\rm trans}\,\psi_{\rm vib}\,\psi_{\rm rot},\qquad E_{\rm total}=E_{\rm trans}+E_{\rm vib}+E_{\rm rot}")
        qc.seccion("Partícula en un anillo")
        st.markdown(
            "Una partícula de masa μ se mueve sobre una circunferencia de radio r en el plano xy, con V = 0. En coordenadas "
            "polares, y con r constante (se descartan las derivadas respecto de r), el hamiltoniano solo depende del ángulo φ:")
        st.latex(r"\hat H=-\frac{\hbar^2}{2\mu r^2}\frac{d^2}{d\varphi^2}=-\frac{\hbar^2}{2I}\frac{d^2}{d\varphi^2}\ \Rightarrow\ -\frac{\hbar^2}{2I}\frac{d^2\Phi}{d\varphi^2}=E\,\Phi")
        st.latex(r"\Phi_\pm(\varphi)=A_\pm e^{\pm im_l\varphi},\qquad m_l=\sqrt{\frac{2IE}{\hbar^2}}")
        st.markdown(
            "Las dos soluciones corresponden a rotación en sentido antihorario y horario. La función de onda debe tener un "
            "solo valor, luego Φ(φ + 2π) = Φ(φ): es una **condición de contorno cíclica**. Se cumple solo si $m_l$ es un "
            "**entero**: $m_l$ = 0, ±1, ±2, …")
        st.latex(r"e^{im_l(\varphi+2\pi)}=e^{im_l\varphi}e^{2\pi im_l}=e^{im_l\varphi}\iff m_l\in\mathbb Z")
        st.markdown("Normalizando, ∫₀^(2π) |Φ|² dφ = 2π|A|² = 1:")
        st.latex(r"\Phi_{m_l}(\varphi)=\frac{1}{\sqrt{2\pi}}\,e^{im_l\varphi},\qquad |\Phi_{m_l}|^2=\frac1{2\pi}\ \text{(densidad uniforme)}")
        st.latex(r"\boxed{E_{m_l}=\frac{m_l^2\hbar^2}{2I},\qquad m_l=0,\pm1,\pm2,\dots}")
        st.markdown(
            "- La separación entre niveles vecinos crece con $m_l$.\n"
            "- Es pequeña si el momento de inercia es grande.\n"
            "- No hay energía del punto cero: el estado más bajo tiene E = 0.\n"
            "- Todos los niveles excepto el fundamental son **doblemente degenerados**: ±$m_l$ corresponden a sentidos opuestos.")
        m = st.slider("Número cuántico m_l", -6, 6, 3, key="es_m")
        phi = np.linspace(0, 2 * np.pi, 800)
        F = phi_anillo(m, phi) * math.sqrt(2 * math.pi)
        fig, (a1, a2) = figura(10, 4.4, columnas=2)
        a1.remove()
        a1 = fig.add_subplot(1, 2, 1)
        a1.plot(np.cos(phi), np.sin(phi), color=COL["gris"], lw=0.8, ls=":")
        r = 1 + 0.18 * F.real
        a1.plot(r * np.cos(phi), r * np.sin(phi), color=COL["onda"], lw=2.2, label="Re Φ sobre el anillo")
        a1.set_aspect("equal")
        a1.axis("off")
        a1.set_title(f"m_l = {m}: |m_l| longitudes de onda")
        a1.legend(fontsize=8, loc="lower center")
        a2.plot(phi, F.real, color=COL["onda"], lw=2, label="Re Φ")
        a2.plot(phi, F.imag, color=COL["interferencia"], lw=1.8, ls="--", label="Im Φ")
        a2.plot(phi, np.abs(F) ** 2, color=COL["densidad"], lw=2, label="|Φ|² (uniforme)")
        a2.set_xlabel("φ [rad]")
        a2.legend(fontsize=8.5, loc="upper right")
        a2.set_ylim(-1.5, 2.0)
        dibujar(fig, "anillo.png")
        st.caption(f"Estado $m_l$ = {m}: $L_z$ = {m}ħ, E = {m ** 2} ħ²/2I. Aunque la amplitud varía con φ, la densidad es uniforme.")
    with sub[1]:
        qc.seccion("Una partícula sobre la superficie de una esfera")
        st.markdown(
            "Con V = 0 y movimiento confinado a una esfera de radio fijo r, el hamiltoniano contiene solo la parte angular "
            "del laplaciano, el **legendriano** Λ²:")
        st.latex(r"\hat H=-\frac{\hbar^2}{2\mu r^2}\Lambda^2=-\frac{\hbar^2}{2I}\Lambda^2,\qquad \Lambda^2=\frac1{\sin^2\theta}\frac{\partial^2}{\partial\varphi^2}+\frac1{\sin\theta}\frac\partial{\partial\theta}\left(\sin\theta\frac\partial{\partial\theta}\right)")
        st.markdown("Las soluciones son los **armónicos esféricos** Yₗ^(mₗ)(θ, φ), que satisfacen:")
        st.latex(r"\Lambda^2Y_l^{m_l}=-l(l+1)\,Y_l^{m_l},\qquad l=0,1,2,\dots,\quad m_l=l,l-1,\dots,-l\ \ (2l+1\ \text{valores})")
        st.markdown("Se factorizan como Y = Θ(θ)Φ(φ): Φ es la misma función del anillo y Θ son las funciones asociadas de Legendre.")
        st.latex(r"\boxed{E_l=l(l+1)\frac{\hbar^2}{2I}}\qquad\text{degeneración }2l+1")
        st.markdown(
            "- La separación entre niveles, proporcional a l(l + 1), crece con l y es pequeña si I es grande.\n"
            "- No hay energía del punto cero (E₀ = 0, con Y₀,₀ constante).\n"
            "- Cada nivel con l > 0 es (2l + 1) veces degenerado: son las 2l + 1 orientaciones del momento angular en el espacio.\n"
            "- Cada Yₗ^m tiene l nodos angulares.")
        qc.seccion("Comprobación numérica del autovalor")
        c1, c2 = st.columns(2)
        with c1:
            l = st.slider("l", 0, 8, 1, key="es_l")
        with c2:
            ml = st.slider("m_l", -l, l, 0, key="es_ml") if l > 0 else 0
        v = autovalor_legendriano(l, ml)
        qc.metricas([("−Λ²Y / Y (numérico)", f"{round(v, 5) + 0.0:.5f}"), ("l(l + 1)", f"{l * (l + 1)}")], columnas=2)
        st.caption("Se aplica Λ² por diferencias finitas a Yₗ^m en un punto de la esfera. Para l = 1, m = 0, Y = N cos θ y "
                   "Λ²Y = −2Y, como se comprueba a mano derivando.")
    with sub[2]:
        qc.seccion("Momento angular y su componente z")
        st.markdown("Clásicamente **l** = **r** × **p**, y su componente z es $l_z$ = x $p_y$ − y $p_x$. Como operador, en coordenadas "
                    "polares:")
        st.latex(r"\hat l_z=\frac\hbar i\left(x\frac\partial{\partial y}-y\frac\partial{\partial x}\right)=\frac\hbar i\frac\partial{\partial\varphi}")
        st.latex(r"\hat l_z\,\Phi_{m_l}=m_l\hbar\,\Phi_{m_l},\qquad \hat l_z\,Y_l^{m_l}=m_l\hbar\,Y_l^{m_l}")
        st.markdown(
            "Φ y Y son autofunciones de $\\hat l_z$ con autovalor $m_l$ħ: el signo de $m_l$ indica el sentido de giro y, como $m_l$ solo toma "
            "2l + 1 valores, la componente z está **cuantizada**. Comparando la energía con la clásica E = l²/2I se obtiene "
            "la magnitud del momento angular:")
        st.latex(r"|\vec l|=\sqrt{l(l+1)}\,\hbar")
        qc.seccion("Orientaciones permitidas")
        st.markdown("Con l y $m_l$ conocidos, el vector forma con el eje z un ángulo tal que cos θ = $m_l$/√(l(l+1)). Las "
                    "componentes x e y **no** se pueden especificar (no conmutan con $\\hat l_z$, como se vio en conmutadores e incertidumbre): el vector "
                    "está en algún punto de un cono.")
        l = st.slider("l (modelo vectorial)", 1, 6, 2, key="es_lv")
        fig, (a1, a2) = figura(10, 4.6, columnas=2)
        L = math.sqrt(l * (l + 1))
        th = np.linspace(0, 2 * np.pi, 200)
        a1.plot(L * np.cos(th), L * np.sin(th), color=COL["gris"], lw=0.8, ls=":")
        for m_, ang in angulos_permitidos(l):
            lp = math.sqrt(max(L ** 2 - m_ ** 2, 0))
            a1.annotate("", xy=(lp, m_), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=COL["onda"], lw=1.6))
            a1.plot([-lp, lp], [m_, m_], color=COL["gris"], lw=0.6, ls="--")
            a1.text(lp + 0.15, m_, f"m = {m_}", va="center", fontsize=8.5)
        a1.set_aspect("equal")
        a1.set_xlim(-L - 1, L + 2.2)
        a1.set_ylim(-L - 1, L + 1)
        a1.set_ylabel("l_z / ħ")
        a1.set_xticks([])
        a1.set_title(f"{2 * l + 1} orientaciones, |l| = √{l * (l + 1)} ħ = {L:.3f} ħ")
        a2.axis("off")
        filas = [[str(m_), f"{ang:.2f}°"] for m_, ang in angulos_permitidos(l)]
        tabla = a2.table(cellText=filas, colLabels=["m_l", "θ (con el eje z)"], loc="center", cellLoc="center")
        tabla.scale(1, 1.25)
        for celda in tabla.get_celld().values():
            celda.set_text_props(color=COL["texto"])
            celda.set_edgecolor(COL["rejilla"])
            celda.set_facecolor(COL["panel"])
        dibujar(fig, "momento_angular.png")
        st.markdown(
            f"Para l grande, los ángulos permitidos se hacen casi continuos: con l = 1000 hay 2001 conos y el menor ángulo es "
            f"**{angulo_minimo(1000):.2f}°**.")
    with sub[3]:
        qc.seccion("Niveles de rotación de una molécula diatómica")
        st.markdown("Una molécula que rota se aproxima por una partícula de masa reducida μ sobre una esfera de radio $r_e$ "
                    "(rotor rígido). Su momento de inercia es I = μ$r_e$² y sus niveles, $E_l$ = l(l + 1)ħ²/2I.")
        nombre = st.selectbox("Molécula", list(MOLECULAS), key="es_mol")
        mu_u, r_pm = MOLECULAS[nombre]
        I = momento_de_inercia(mu_u * U_MASA, r_pm * 1e-12)
        B = HBAR / (4 * math.pi * C * 100 * I)           # cm⁻¹
        qc.metricas([("Masa reducida μ", f"{mu_u:.5f} u"), ("Longitud de enlace", f"{r_pm} pm"),
                     ("I = μr²", f"{I:.4g} kg·m²"), ("B = ħ/4πcI", f"{B:.4g} cm⁻¹")], columnas=4)
        qc.tabla_libre([{"l": str(l), "Degeneración": str(2 * l + 1), "Eₗ [meV]": f"{energia_esfera(l, I) / const.e * 1e3:.5g}",
                         "Eₗ [cm⁻¹]": f"{l * (l + 1) * B:.5g}", "|l|/ħ": f"{math.sqrt(l * (l + 1)):.4f}"} for l in range(0, 7)],
                       numericas=("Degeneración", "Eₗ [meV]", "Eₗ [cm⁻¹]", "|l|/ħ"))
        st.caption("Cuanto mayor es I, más juntos están los niveles: por eso el H₂ (ligero) tiene niveles rotacionales mucho más "
                   "separados que el N₂. Los valores de B coinciden con los espectroscópicos (H₂ ≈ 60.9, HCl ≈ 10.6, CO ≈ 1.93, "
                   "N₂ ≈ 2.0, O₂ ≈ 1.44 cm⁻¹).")
    with sub[4]:
        qc.seccion("Armónicos esféricos (simulador)")
        st.latex(r"Y_l^m(\theta,\varphi)=(-1)^m\sqrt{\frac{2l+1}{4\pi}\frac{(l-m)!}{(l+m)!}}\;P_l^m(\cos\theta)\,e^{im\varphi},\quad m\ge 0")
        st.latex(r"Y_l^{-m}=(-1)^m\,\overline{Y_l^m}\qquad \hat L^2Y_l^m=\hbar^2l(l+1)Y_l^m\qquad \hat L_zY_l^m=\hbar mY_l^m")
        st.latex(r"\int_0^{2\pi}\!\!\int_0^{\pi}\overline{Y_l^m}\,Y_{l'}^{m'}\sin\theta\,d\theta\,d\varphi=\delta_{ll'}\delta_{mm'}")
        st.markdown("**Combinaciones reales.** Los orbitales reales son mezclas de ±m (cos mφ y sin mφ): ya no tienen $L_z$ definido. "
                    "Nodos latitudinales: raíces de P_l^|m|(cos θ), hay l − |m|; con la combinación real, además |m| planos "
                    "verticales: en total l superficies nodales.")
        st.markdown("**Partícula en una esfera impenetrable** (simulador, con parte radial):")
        st.latex(r"\psi_{nlm}=R_{nl}(r)\,Y_l^m,\qquad R_{nl}(r)=\sqrt{\frac{2}{R^3}}\,\frac{j_l(\alpha_{nl}r/R)}{|j_{l+1}(\alpha_{nl})|},\qquad E_{nl}=\frac{\hbar^2\alpha_{nl}^2}{2mR^2}")
        st.markdown("Las superficies deformadas o de lóbulos del simulador son representaciones geométricas, no objetos físicos. "
                    "No se considera el espín.")


PREGUNTAS = [
    {"enunciado": "En la partícula en un anillo, ¿por qué $m_l$ debe ser entero?",
     "opciones": ["Porque Φ(φ + 2π) = Φ(φ) (función univaluada)", "Porque la energía es entera",
                  "Porque la masa es entera", "Porque V = ∞ en φ = 0"],
     "correcta": 0, "explicacion": "La condición cíclica e^{2πi $m_l$} = 1 solo se cumple si $m_l$ ∈ ℤ."},
    {"enunciado": "La energía de la partícula en un anillo es...",
     "opciones": ["$m_l^2$ ħ²/2I", "m_l ħ²/2I", "(m_l + ½)ħω", "l(l + 1)ħ²/2I"],
     "correcta": 0, "explicacion": "E = $m_l^2$ħ²/2I, con m_l = 0, ±1, ±2…; todos los niveles salvo m_l = 0 están doblemente degenerados."},
    {"enunciado": "El nivel con número cuántico l de una partícula en una esfera tiene degeneración...",
     "opciones": ["2l + 1", "l", "2l", "l + 1"],
     "correcta": 0, "explicacion": "$m_l$ toma los valores l, l − 1, …, −l: son 2l + 1."},
    {"enunciado": "La magnitud del momento angular en el estado l es...",
     "opciones": ["√(l(l + 1)) ħ", "l ħ", "l² ħ", "(l + ½) ħ"],
     "correcta": 0, "explicacion": "Se obtiene al igualar E = l(l + 1)ħ²/2I con la expresión clásica E = |l|²/2I."},
    {"enunciado": "Si el momento de inercia I aumenta, la separación entre niveles de rotación...",
     "opciones": ["disminuye", "aumenta", "no cambia", "se anula siempre"],
     "correcta": 0, "explicacion": "Los niveles son proporcionales a 1/I: las moléculas pesadas tienen niveles más juntos."},
    {"enunciado": "Para l = 1000, ¿cuántos valores de $m_l$ (conos) hay?",
     "opciones": ["2001", "1000", "1001", "2000"],
     "correcta": 0, "explicacion": "2l + 1 = 2001."},
    {"enunciado": "¿Qué componentes del momento angular se pueden conocer a la vez que su módulo y $l_z$?",
     "opciones": ["Ninguna otra: $l_x$ y $l_y$ no conmutan con $l_z$", "$l_x$", "$l_y$", "Todas"],
     "correcta": 0, "explicacion": "Solo |l| y $l_z$ tienen valores definidos; $l_x$ y $l_y$ quedan indeterminadas (el vector está sobre un cono)."},
]
