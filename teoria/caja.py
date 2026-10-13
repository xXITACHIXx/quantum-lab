"""
teoria/caja.py — Teoría: Partícula en una caja (semana 6).
"""

import itertools
import math

import numpy as np
import streamlit as st
from scipy.integrate import quad

import quantum_lab_comun as qc
from teoria._util import COL, EV, H, ME, dibujar, figura

U_MASA = 1.66053906660e-27
PARTICULAS = {"Electrón": ME, "Protón": 1.67262192369e-27, "Molécula de N₂": 28.0134 * U_MASA}


def energia_caja(n: int, masa: float, a: float) -> float:
    """E_n = h² n² / (8 m a²)   [J]."""
    return H ** 2 * n ** 2 / (8 * masa * a ** 2)


def psi_caja(n: int, x, a: float = 1.0):
    return np.sqrt(2 / a) * np.sin(n * np.pi * x / a)


def probabilidad_en_intervalo(n: int, f1: float, f2: float) -> float:
    """
    P(x₁ < x < x₂) con x₁ = f₁a, x₂ = f₂a para el estado n:
    (f₂ − f₁) − [sin(2nπf₂) − sin(2nπf₁)] / (2nπ).
    """
    return (f2 - f1) - (math.sin(2 * n * math.pi * f2) - math.sin(2 * n * math.pi * f1)) / (2 * n * math.pi)


def probabilidad_numerica(n: int, f1: float, f2: float) -> float:
    return quad(lambda u: 2 * math.sin(n * math.pi * u) ** 2, f1, f2)[0]


def separacion_relativa(n: int) -> float:
    """(E_{n+1} − E_n) / E_n = (2n + 1) / n²."""
    return (2 * n + 1) / n ** 2


def niveles_caja_3d(b_sobre_a: float = 1.0, c_sobre_a: float = 1.0, nmax: int = 8, cuantos: int = 12):
    """
    Niveles más bajos de una caja de lados a, b = (b/a)a, c = (c/a)c, en unidades de h²/(8 m a²):
    E = nx² + ny²/(b/a)² + nz²/(c/a)². Devuelve [(E, degeneración, [(nx, ny, nz), ...]), ...].
    """
    grupos = {}
    for nx, ny, nz in itertools.product(range(1, nmax + 1), repeat=3):
        e = nx ** 2 + ny ** 2 / b_sobre_a ** 2 + nz ** 2 / c_sobre_a ** 2
        grupos.setdefault(round(e, 9), []).append((nx, ny, nz))
    return [(e, len(v), v) for e, v in sorted(grupos.items())][:cuantos]


def mostrar() -> None:
    sub = st.tabs(["El modelo y su solución", "Energías y nodos", "Probabilidades y valores esperados",
                   "Principio de correspondencia", "Cajas en 2D y 3D", "Superposición (complemento)"])
    with sub[0]:
        qc.seccion("Paredes impenetrables")
        st.markdown(
            "Para mantener la matemática sencilla se estudia una partícula que se mueve en una dimensión, el análogo de una "
            "partícula libre dentro de un cubo con paredes impenetrables. Las paredes se modelan haciendo infinita la "
            "energía potencial fuera de una región de ancho a:")
        st.latex(r"V(x)=0\ \ (0\le x\le a),\qquad V(x)=\infty\ \ (x<0\ \text{o}\ x>a)")
        st.latex(r"\frac{d^2\psi}{dx^2}=\frac{2m}{\hbar^2}\,[V(x)-E]\,\psi(x)")
        st.markdown(
            "Como la segunda derivada debe existir y ser razonable, ψ tiene que valer cero fuera de la caja y también en las "
            "paredes. Esas son las **condiciones de contorno**:")
        st.latex(r"\psi(0)=\psi(a)=0,\qquad \psi(x)=0\ \text{si}\ x<0\ \text{o}\ x>a")
        qc.seccion("Resolver dentro de la caja")
        st.markdown("Dentro, donde V = 0, la ecuación es la de la partícula libre; se escribe la solución con funciones "
                    "trigonométricas:")
        st.latex(r"\psi(x)=A\sin kx+B\cos kx,\qquad k=\sqrt{2mE}/\hbar")
        st.markdown(
            "- ψ(0) = 0 obliga a B = 0.\n"
            "- ψ(a) = A sin ka = 0 se cumple con A = 0 (no hay partícula, se descarta) o con **ka = nπ**, con n entero. "
            "Además n = 0 daría ψ = 0, y los n negativos reproducen el mismo estado (con signo cambiado), así que n = 1, 2, 3…")
        st.latex(r"\psi_n(x)=A\sin\frac{n\pi x}{a}")
        qc.seccion("Normalizar")
        st.latex(r"\int_0^a|\psi_n|^2dx=A^2\int_0^a\sin^2\frac{n\pi x}{a}dx=A^2\frac a2=1\ \Rightarrow\ A=\sqrt{\frac2a}")
        st.latex(r"\boxed{\psi_n(x)=\sqrt{\frac2a}\,\sin\frac{n\pi x}{a},\qquad n=1,2,3,\dots}")
        st.markdown("Cada valor de n es una autofunción distinta y, como se ve a continuación, tiene su propia energía.")
    with sub[1]:
        qc.seccion("Energías cuantizadas")
        st.markdown("Aplicando el operador de energía a ψₙ se recupera la misma función multiplicada por una constante:")
        st.latex(r"-\frac{\hbar^2}{2m}\frac{d^2\psi_n}{dx^2}=\frac{\hbar^2}{2m}\left(\frac{n\pi}{a}\right)^2\psi_n=E_n\psi_n"
                 r"\ \Rightarrow\ \boxed{E_n=\frac{h^2n^2}{8ma^2},\quad n=1,2,3,\dots}")
        st.markdown(
            "- La energía solo toma valores discretos: está **cuantizada**, y n es un número cuántico.\n"
            "- La energía más baja (n = 1) es mayor que cero: es la **energía del punto cero**. La partícula nunca está "
            "quieta.\n"
            "- La cuantización viene del **confinamiento**. Al hacer a → ∞ se elimina el confinamiento y se vuelve a la "
            "partícula libre, con energía continua.\n"
            "- El estado estacionario es una **onda estacionaria**: sus nodos (puntos donde ψ = 0) están en posiciones "
            "fijas. Hay n − 1 nodos; los extremos de la caja **no** se cuentan como nodos.")
        qc.seccion("Calculadora de niveles")
        c1, c2, c3 = st.columns(3)
        with c1:
            nombre = st.selectbox("Partícula", list(PARTICULAS), key="cj_part")
        with c2:
            a_nm = st.number_input("Ancho de la caja a [nm]", 0.01, 1e6, 1.0, format="%.4g", key="cj_a")
        with c3:
            nmax = st.slider("Niveles a mostrar", 2, 8, 5, key="cj_nm")
        m = PARTICULAS[nombre]
        a = a_nm * 1e-9
        filas = [{"n": str(n), "Eₙ [eV]": f"{energia_caja(n, m, a) / EV:.6g}", "Eₙ [J]": f"{energia_caja(n, m, a):.5g}",
                  "Nodos": str(n - 1)} for n in range(1, nmax + 1)]
        qc.tabla_libre(filas, numericas=("Eₙ [eV]", "Eₙ [J]"))
        e21 = energia_caja(2, m, a) - energia_caja(1, m, a)
        st.caption(f"Transición 1 → 2: ΔE = {e21 / EV:.5g} eV, es decir, un fotón de λ = {H * 2.99792458e8 / e21 * 1e9:.5g} nm.")
        xx = np.linspace(0, 1, 600)
        fig, (a1, a2) = figura(10, 4.4, columnas=2)
        for n in range(1, nmax + 1):
            e = n ** 2
            a1.plot(xx, e + 0.35 * n * psi_caja(n, xx) / math.sqrt(2) * 1.0, color=COL["onda"], lw=1.7)
            a1.axhline(e, color=COL["energia"], lw=0.8, ls=":")
        a1.set_xlabel("x / a")
        a1.set_ylabel("Eₙ / E₁  (ψₙ dibujada sobre su nivel)")
        a1.set_title("Niveles y funciones de onda")
        for n in (1, 2, 3):
            a2.plot(xx, psi_caja(n, xx) ** 2, lw=2, label=f"|ψ{n}|²")
        a2.set_xlabel("x / a")
        a2.set_title("Densidades de probabilidad")
        a2.legend(fontsize=8.5)
        dibujar(fig, "caja_niveles.png")
    with sub[2]:
        qc.seccion("Probabilidad de encontrar la partícula en un intervalo")
        st.markdown(
            "Por el postulado 1, la probabilidad de hallar la partícula en [x₁, x₂] es la integral de |ψ|² en ese tramo. "
            "Aunque |ψ|² vale cero en un nodo, la integral sobre cualquier intervalo finito dentro de la caja "
            "**nunca** es cero.")
        st.latex(r"P(x_1,x_2)=\frac2a\int_{x_1}^{x_2}\sin^2\frac{n\pi x}{a}dx=\frac{x_2-x_1}{a}-\frac{1}{2n\pi}\left[\sin\frac{2n\pi x_2}{a}-\sin\frac{2n\pi x_1}{a}\right]")
        st.markdown("Ejemplo: en el estado fundamental, la probabilidad en el tercio central de la caja es "
                    f"**{probabilidad_en_intervalo(1, 1 / 3, 2 / 3):.4f}** (= 1/3 + √3/2π). No se puede predecir el resultado de una "
                    "medida individual, pero en el 60.9 % de muchas medidas la partícula aparece en ese tramo.")
        c1, c2 = st.columns(2)
        with c1:
            n = st.slider("Estado n", 1, 12, 1, key="cj_n")
        with c2:
            f1, f2 = st.slider("Intervalo [x₁, x₂] / a", 0.0, 1.0, (1 / 3, 2 / 3), 0.01, key="cj_f")
        p_a = probabilidad_en_intervalo(n, f1, f2)
        p_n = probabilidad_numerica(n, f1, f2)
        xx = np.linspace(0, 1, 800)
        fig, ax = figura(9, 3.8)
        ax.plot(xx, psi_caja(n, xx) ** 2, color=COL["densidad"], lw=2.2)
        sel = (xx >= f1) & (xx <= f2)
        ax.fill_between(xx[sel], psi_caja(n, xx[sel]) ** 2, color=COL["cinetica"], alpha=0.35)
        ax.set_xlabel("x / a")
        ax.set_ylabel(r"$|\psi_n|^2$  [1/a]")
        ax.set_title(f"P = {p_a:.4f}")
        dibujar(fig, "caja_probabilidad.png")
        qc.metricas([("P (fórmula)", f"{p_a:.6f}"), ("P (integral numérica)", f"{p_n:.6f}"), ("⟨x⟩", "a/2")], columnas=3)
        st.markdown(
            "El estado ψₙ **no** es autofunción del operador posición (xψₙ no es una constante por ψₙ), así que la posición "
            "no tiene un valor definido; su valor esperado, ⟨x⟩ = a/2, indica que la partícula está igual de probable en "
            "ambas mitades de la caja.")
    with sub[3]:
        qc.seccion("De lo cuántico a lo clásico")
        st.markdown(
            "El espaciado entre niveles contiguos, E₍ₙ₊₁₎ − Eₙ, crece con n, lo que parece indicar que el espectro nunca se "
            "vuelve continuo. Es mejor mirar el espaciado **relativo**:")
        st.latex(r"\frac{E_{n+1}-E_n}{E_n}=\frac{(n+1)^2-n^2}{n^2}=\frac{2n+1}{n^2}\ \xrightarrow[n\to\infty]{}\ 0")
        st.markdown(
            "La energía crece como n², más rápido que el espaciado, así que para n grande los niveles quedan "
            "muy juntos respecto de la energía y el espectro parece continuo: el resultado cuántico coincide con el clásico. "
            "Es un ejemplo del **principio de correspondencia**.")
        ns = np.array([1, 2, 5, 10, 100, 1000])
        qc.tabla_libre([{"n": str(int(n)), "(Eₙ₊₁ − Eₙ)/Eₙ": f"{separacion_relativa(int(n)):.5g}"} for n in ns],
                       numericas=("(Eₙ₊₁ − Eₙ)/Eₙ",))
        c1, c2 = st.columns(2)
        with c1:
            n_alto = st.slider("Estado alto n", 2, 60, 20, key="cj_nalto")
        xx = np.linspace(0, 1, 4000)
        fig, (a1, a2) = figura(10, 4.0, columnas=2)
        nn = np.arange(1, 200)
        a1.loglog(nn, [separacion_relativa(int(k)) for k in nn], color=COL["onda"], lw=2.2)
        a1.set_xlabel("n")
        a1.set_ylabel("(Eₙ₊₁ − Eₙ) / Eₙ")
        a1.set_title("El espectro se vuelve «continuo»")
        a2.plot(xx, psi_caja(n_alto, xx) ** 2, color=COL["densidad"], lw=1.2, label=f"|ψ{n_alto}|²")
        a2.axhline(1.0, color=COL["energia"], ls="--", lw=2, label="densidad clásica 1/a")
        a2.set_xlabel("x / a")
        a2.set_title("La densidad se aproxima a la clásica")
        a2.legend(fontsize=8.5)
        dibujar(fig, "caja_correspondencia.png")
    with sub[4]:
        qc.seccion("Separación de variables")
        st.markdown(
            "Pasar de una a dos dimensiones es directo, así que se trabaja directamente en 3D: una caja de lados a, b y c "
            "con V = 0 dentro e infinita fuera. Dentro:")
        st.latex(r"-\frac{\hbar^2}{2m}\left(\frac{\partial^2}{\partial x^2}+\frac{\partial^2}{\partial y^2}+\frac{\partial^2}{\partial z^2}\right)\psi=E\psi")
        st.markdown("Se prueba una solución producto ψ = X(x)Y(y)Z(z). Al dividir por ella, cada término depende de una sola "
                    "variable, de modo que la energía se reparte en tres contribuciones independientes, E = Eₓ + $E_y$ + $E_z$, y la "
                    "ecuación se separa en **tres ecuaciones de la caja unidimensional**:")
        st.latex(r"\psi_{n_xn_yn_z}=N\sin\frac{n_x\pi x}{a}\sin\frac{n_y\pi y}{b}\sin\frac{n_z\pi z}{c},\qquad "
                 r"E=\frac{h^2}{8m}\left(\frac{n_x^2}{a^2}+\frac{n_y^2}{b^2}+\frac{n_z^2}{c^2}\right)")
        st.markdown(
            "Como distintos conjuntos de números cuánticos (nₓ, $n_y$, $n_z$) pueden dar la misma energía, el nivel es "
            "**degenerado**; la **degeneración** es el número de estados (autofunciones distintas) con esa energía.")
        qc.seccion("Niveles de una caja 3D")
        c1, c2 = st.columns(2)
        with c1:
            rb = st.slider("b / a", 0.5, 2.0, 1.0, 0.05, key="cj_rb")
        with c2:
            rc = st.slider("c / a", 0.5, 2.0, 1.0, 0.05, key="cj_rc")
        niveles = niveles_caja_3d(rb, rc)
        qc.tabla_libre([{"E [h²/8ma²]": f"{e:.4f}", "Degeneración": str(g),
                         "Estados (nx, ny, nz)": ", ".join(str(t) for t in estados[:6]) + (" …" if len(estados) > 6 else "")}
                        for e, g, estados in niveles], numericas=("E [h²/8ma²]", "Degeneración"))
        st.caption("Con b = c = a (cubo) aparecen degeneraciones por simetría: por ejemplo (1,1,2), (1,2,1) y (2,1,1) tienen la "
                   "misma energía. Al cambiar b/a o c/a, la simetría se rompe y la degeneración desaparece (se levanta).")
        qc.seccion("Densidad en una caja 2D")
        c1, c2 = st.columns(2)
        with c1:
            nx = st.slider("nₓ", 1, 6, 2, key="cj_nx")
        with c2:
            ny = st.slider("n_y", 1, 6, 1, key="cj_ny")
        gx, gy = np.meshgrid(np.linspace(0, 1, 220), np.linspace(0, 1, 220))
        dens = (psi_caja(nx, gx) * psi_caja(ny, gy)) ** 2
        fig, ax = figura(4.8, 4.4)
        im = ax.imshow(dens, origin="lower", extent=[0, 1, 0, 1], cmap="magma")
        ax.set_xlabel("x / a")
        ax.set_ylabel("y / b")
        ax.set_title(f"|ψ|²  (nₓ = {nx}, n_y = {ny})")
        ax.grid(False)
        dibujar(fig, "caja_2d.png")
    with sub[5]:
        qc.seccion("Superposición de estados")
        st.markdown("Una superposición como ψ = c sin(πx/a) + d sin(2πx/a) es una función **aceptable** (cumple las condiciones de "
                    "contorno y es derivable), pero **no** es autofunción de Ĥ: al aplicarlo se obtiene c·E₁·sin(πx/a) + d·4E₁·sin(2πx/a), "
                    "que no es ψ multiplicado por una constante. La energía no tiene un valor definido: en una medida sale E₁ o "
                    "4E₁ (postulado 3).")
        st.latex(r"\Psi(x,t)=\sum_n c_n\,\psi_n(x)\,e^{-iE_nt/\hbar},\qquad |\Psi|^2=\sum_n|c_n|^2|\psi_n|^2+2\sum_{n<m}\mathrm{Re}\!\left[c_n^*c_m\,\psi_n\psi_m\,e^{-i(E_m-E_n)t/\hbar}\right]")
        st.markdown("Los términos cruzados dependen del tiempo y de las fases relativas: son la interferencia cuántica, y "
                    "explican por qué **no** se pueden sumar las densidades. Se explora en el simulador de la partícula en una caja.")


PREGUNTAS = [
    {"enunciado": "En la partícula en una caja, la energía del estado n es...",
     "opciones": ["h²n²/(8ma²)", "(n + ½)hν", "h²/(8ma²n²)", "n h ν"],
     "correcta": 0, "explicacion": "Eₙ = h²n²/8ma², con n = 1, 2, 3…"},
    {"enunciado": "El estado de menor energía de la caja tiene energía...",
     "opciones": ["mayor que cero (energía del punto cero)", "exactamente cero", "negativa", "infinita"],
     "correcta": 0, "explicacion": "n = 0 daría ψ = 0 (sin partícula); el mínimo es E₁ = h²/8ma² > 0."},
    {"enunciado": "¿Cuántos nodos tiene ψₙ dentro de la caja (sin contar los extremos)?",
     "opciones": ["n − 1", "n", "n + 1", "2n"],
     "correcta": 0, "explicacion": "ψₙ = √(2/a) sin(nπx/a) se anula en x = ka/n, con k = 1, …, n − 1 dentro de la caja."},
    {"enunciado": "La probabilidad de hallar la partícula en el tercio central de la caja, en el estado fundamental, es...",
     "opciones": ["≈ 0.609", "1/3", "≈ 0.25", "0.5"],
     "correcta": 0, "explicacion": "P = 1/3 + √3/(2π) ≈ 0.609: la densidad se concentra en el centro."},
    {"enunciado": "¿Qué dice el principio de correspondencia en la caja?",
     "opciones": ["Para n grande, (Eₙ₊₁ − Eₙ)/Eₙ → 0 y el espectro parece continuo",
                  "La energía se vuelve negativa", "Los nodos desaparecen para n = 1", "La caja se hace infinita"],
     "correcta": 0, "explicacion": "(2n + 1)/n² → 0 cuando n → ∞."},
    {"enunciado": "En un cubo (a = b = c), el nivel con (nₓ, $n_y$, $n_z$) = (1, 1, 2) tiene degeneración...",
     "opciones": ["3", "1", "2", "6"],
     "correcta": 0, "explicacion": "Las combinaciones (1,1,2), (1,2,1) y (2,1,1) tienen E = 6 h²/8ma²."},
    {"enunciado": "La superposición ψ = c sin(πx/a) + d sin(2πx/a) (c, d ≠ 0) es...",
     "opciones": ["aceptable pero no autofunción de Ĥ", "autofunción de Ĥ", "inaceptable", "igual a ψ₃"],
     "correcta": 0, "explicacion": "Cumple las condiciones de contorno, pero Ĥψ no es proporcional a ψ porque E₂ ≠ E₁."},
]
