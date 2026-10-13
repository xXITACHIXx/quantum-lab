"""
teoria/conmutadores.py — Teoría: Operadores que conmutan y que no conmutan; principio de incertidumbre (semana 7).
"""

import numpy as np
import streamlit as st
from scipy.integrate import trapezoid

import quantum_lab_comun as qc
from teoria._util import COL, figura, dibujar

H_PASO = 1e-3


# ---------------------------------------------------------------------
# Operadores sobre funciones (ħ = 1), con derivadas por diferencias centrales
# ---------------------------------------------------------------------
def op_x(g):
    return lambda x: x * g(x)


def op_x2(g):
    return lambda x: x ** 2 * g(x)


def op_p(g):
    return lambda x: -1j * (g(x + H_PASO) - g(x - H_PASO)) / (2 * H_PASO)


def op_p2(g):
    return op_p(op_p(g))


def op_T(g):
    return lambda x: -0.5 * (g(x + H_PASO) - 2 * g(x) + g(x - H_PASO)) / H_PASO ** 2


OPS = {"x̂": op_x, "x̂²": op_x2, "p̂": op_p, "p̂²": op_p2, "T̂ = p̂²/2": op_T}


def f_prueba(x):
    """Función de prueba arbitraria y derivable."""
    return np.exp(-x ** 2 / 2) * (1 + 0.3 * x)


def f_prueba_d1(x):
    return np.exp(-x ** 2 / 2) * (0.3 - x * (1 + 0.3 * x))


def conmutador_numerico(A: str, B: str, x):
    """[A, B] f(x) = A(B f) − B(A f)."""
    AB = OPS[A](OPS[B](f_prueba))
    BA = OPS[B](OPS[A](f_prueba))
    return AB(x) - BA(x)


def conmutador_esperado(A: str, B: str, x):
    """Resultado exacto conocido de [A, B] f(x) (ħ = 1), o None si no está tabulado."""
    f, f1 = f_prueba(x), f_prueba_d1(x)
    tabla = {("x̂", "p̂"): 1j * f, ("p̂", "x̂"): -1j * f, ("x̂", "p̂²"): 2j * (-1j * f1),
             ("p̂²", "x̂"): -2j * (-1j * f1), ("x̂²", "p̂"): 2j * x * f, ("p̂", "x̂²"): -2j * x * f,
             ("x̂", "x̂²"): 0 * f, ("x̂²", "x̂"): 0 * f, ("p̂", "p̂²"): 0 * f, ("p̂²", "p̂"): 0 * f,
             ("p̂", "T̂ = p̂²/2"): 0 * f, ("T̂ = p̂²/2", "p̂"): 0 * f}
    if A == B:
        return 0 * f
    return tabla.get((A, B))


# ---------------------------------------------------------------------
# Partícula en una caja: Δx Δp del estado n
# ---------------------------------------------------------------------
def incertidumbres_caja(n: int):
    """
    Devuelve (Δx/L, Δp/(ħ/L), producto/ħ) analíticos para el estado n de una caja de longitud L:
    Δx² = L²(1/12 − 1/(2n²π²)),  Δp = nπħ/L.
    """
    dx = np.sqrt(1 / 12 - 1 / (2 * n ** 2 * np.pi ** 2))
    dp = n * np.pi
    return float(dx), float(dp), float(dx * dp)


def incertidumbres_caja_numericas(n: int, puntos: int = 200001):
    """Misma magnitud calculada integrando ⟨x⟩, ⟨x²⟩, ⟨p²⟩ (L = 1, ħ = 1); ⟨p⟩ = 0 por simetría de la onda real."""
    x = np.linspace(0, 1, puntos)
    psi = np.sqrt(2) * np.sin(n * np.pi * x)
    d = x[1] - x[0]
    dpsi = np.gradient(psi, d)
    xm = trapezoid(psi ** 2 * x, x)
    x2 = trapezoid(psi ** 2 * x ** 2, x)
    p2 = trapezoid(dpsi ** 2, x)                       # ⟨p²⟩ = ∫|ψ'|² dx (ħ = 1)
    p_med = trapezoid(psi * (-1j) * dpsi, x).real
    dx = np.sqrt(x2 - xm ** 2)
    dp = np.sqrt(p2 - p_med ** 2)
    return float(dx), float(dp), float(dx * dp)


def _ir_simulador():
    st.session_state["ql_pagina"] = "incertidumbre"


def mostrar() -> None:
    sub = st.tabs(["Medidas simultáneas", "El conmutador", "Posición y momento", "Principio de incertidumbre",
                   "Ejemplo: partícula en una caja"])
    with sub[0]:
        qc.seccion("¿Se pueden conocer dos propiedades a la vez?")
        st.markdown(
            "Medir una propiedad puede **cambiar el estado** del sistema. Dos observables α y β, con operadores Â y B̂, "
            "solo se pueden determinar simultáneamente si la primera medida no perturba el resultado de la segunda.")
        st.markdown(
            "Supón que el sistema está en ψₙ. Si ψₙ es autofunción de Â, medir α deja el sistema en ψₙ y da αₙ. Después "
            "se mide β: el estado se mantiene solo si ψₙ **también** es autofunción de B̂. En ese caso:")
        st.latex(r"\hat B[\hat A\psi_n]=\alpha_n\beta_n\psi_n=\hat A[\hat B\psi_n]")
        st.markdown(
            "El orden de las medidas no importa. Si, al contrario, el estado no es autofunción de ambos, la medida de uno "
            "cambia el estado respecto del otro y el orden sí importa.")
    with sub[1]:
        qc.seccion("Definición")
        st.markdown(
            "Dos operadores tienen un **conjunto común de autofunciones** si y solo si el resultado de aplicarlos en uno u "
            "otro orden es igual para cualquier función f. La diferencia se llama **conmutador**:")
        st.latex(r"[\hat A,\hat B]\,f(x)=\hat A\big[\hat B f(x)\big]-\hat B\big[\hat A f(x)\big]")
        st.markdown(
            "- Si [Â, B̂] = 0, los operadores **conmutan**: los observables pueden conocerse a la vez, con exactitud.\n"
            "- Si [Â, B̂] ≠ 0, **no conmutan**: no pueden determinarse simultáneamente con exactitud.")
        st.markdown("Casos conocidos: las tres componentes de la posición (x, y, z) conmutan entre sí, y también las tres "
                    "componentes del momento lineal (pₓ, $p_y$, $p_z$). Pero x y pₓ **no** conmutan.")
        qc.seccion("Calcúlalo numéricamente")
        st.markdown("Se aplica el conmutador a una función de prueba arbitraria y se compara con el resultado exacto "
                    "(con ħ = 1; las derivadas se calculan por diferencias finitas).")
        c1, c2 = st.columns(2)
        with c1:
            A = st.selectbox("Operador Â", list(OPS), index=0, key="co_A")
        with c2:
            B = st.selectbox("Operador B̂", list(OPS), index=2, key="co_B")
        x = np.linspace(-2, 2, 9)
        num = conmutador_numerico(A, B, x)
        esp = conmutador_esperado(A, B, x)
        f = f_prueba(x)
        if esp is None:
            st.info("Para esta pareja no se tiene tabulado el resultado exacto; se muestra solo el valor numérico.",
                    icon=":material/info:")
        else:
            err = np.max(np.abs(num - esp))
            if err < 1e-4:
                if np.max(np.abs(esp)) < 1e-12:
                    st.success("[Â, B̂] f = 0 para esta f: **los operadores conmutan**.", icon=":material/check_circle:")
                else:
                    st.error("[Â, B̂] f ≠ 0: **no conmutan**.", icon=":material/close:")
            qc.metricas([("Máx |[Â,B̂]f|", f"{np.max(np.abs(num)):.4g}"), ("Error vs exacto", f"{err:.2e}")], columnas=2)
        qc.tabla_libre([{"x": f"{xi:.2f}", "f(x)": f"{fi:.5f}", "[Â,B̂]f (numérico)": f"{ni.real:.5f} {ni.imag:+.5f}i"}
                        for xi, fi, ni in zip(x, f, num)], numericas=("x", "f(x)", "[Â,B̂]f (numérico)"))
        st.caption("Para x̂ y p̂ el resultado es i·f(x): es decir, [x̂, p̂] = iħ (con ħ = 1).")
    with sub[2]:
        qc.seccion("El conmutador de x y pₓ")
        st.latex(r"[\hat x,\hat p_x]f=x\left(-i\hbar\frac{\partial f}{\partial x}\right)-\left(-i\hbar\right)\frac{\partial(xf)}{\partial x}"
                 r"=-i\hbar x f'+i\hbar\,(f+xf')=i\hbar f")
        st.latex(r"\boxed{[\hat x,\hat p_x]=i\hbar}")
        st.markdown("No es cero: posición y momento son observables **complementarios** y no se pueden especificar a la "
                    "vez con exactitud. En cambio, el momento y la energía cinética sí conmutan: da igual derivar primero dos "
                    "veces y luego una, o al revés.")
    with sub[3]:
        qc.seccion("De la complementariedad a una desigualdad")
        st.markdown(
            "Aunque no se pueden fijar a la vez x y pₓ, sí se puede decir cuánto se puede saber de cada uno. Si se conoce la "
            "posición con una incertidumbre Δx, el momento tiene al menos una incertidumbre Δpₓ dada por")
        st.latex(r"\Delta x\,\Delta p_x\ \ge\ \frac{\hbar}{2}")
        st.markdown("Esto es un caso particular de la forma general del principio de incertidumbre de Heisenberg (1927) para "
                    "dos observables cualesquiera a y b:")
        st.latex(r"\Delta a\,\Delta b\ \ge\ \frac12\,\big|\langle[\hat A,\hat B]\rangle\big|,\qquad \Delta a=\sqrt{\langle\hat A^2\rangle-\langle\hat A\rangle^2}")
        st.markdown(
            "Δa es la desviación cuadrática media. Es coherente con la conmutación: si [Â, B̂] = 0 el lado derecho vale "
            "cero y se puede tener Δa = 0 y Δb = 0. Si no conmutan, ambas incertidumbres están **inversamente** "
            "relacionadas. Para x y pₓ, ½|⟨iħ⟩| = ħ/2.")
        st.markdown("La incertidumbre es una propiedad del **estado**, no un defecto del aparato de medida. "
                    "El simulador de incertidumbre permite explorarla con paquetes de ondas.")
        st.button("Abrir el simulador de incertidumbre", key="co_sim", on_click=_ir_simulador, icon=":material/arrow_forward:")
    with sub[4]:
        qc.seccion("Estados estacionarios de la caja")
        st.markdown(
            "Para una partícula en una caja de longitud L en el estado ψₙ = √(2/L) sin(nπx/L) se tiene ⟨x⟩ = L/2, ⟨pₓ⟩ = 0 y")
        st.latex(r"\langle x^2\rangle=L^2\left(\frac13-\frac{1}{2n^2\pi^2}\right),\qquad \langle p_x^2\rangle=\frac{n^2\pi^2\hbar^2}{L^2}")
        st.latex(r"\Delta x\,\Delta p_x=\hbar\,n\pi\sqrt{\frac1{12}-\frac1{2n^2\pi^2}}")
        st.markdown("Para el estado fundamental (n = 1) queda ΔxΔp = ħ√((π² − 6)/12) ≈ 0.568 ħ, mayor que ħ/2 como exige el principio.")
        n = st.slider("Estado n", 1, 20, 1, 1, key="co_n")
        dx, dp, prod = incertidumbres_caja(n)
        dxn, dpn, prodn = incertidumbres_caja_numericas(n)
        qc.metricas([("Δx", f"{dx:.5f} L"), ("Δp", f"{dp:.5f} ħ/L"), ("Δx·Δp", f"{prod:.5f} ħ"),
                     ("Δx·Δp por integración", f"{prodn:.5f} ħ"), ("(Δx·Δp) / (ħ/2)", f"{prod / 0.5:.4f}")], columnas=5)
        ns = np.arange(1, 21)
        productos = np.array([incertidumbres_caja(int(m))[2] for m in ns])
        xx = np.linspace(0, 1, 800)
        fig, (a1, a2) = figura(10, 4.2, columnas=2)
        a1.plot(xx, np.sqrt(2) * np.sin(n * np.pi * xx), color=COL["onda"], lw=2.2, label="ψₙ")
        a1.plot(xx, 2 * np.sin(n * np.pi * xx) ** 2, color=COL["densidad"], lw=2.0, label="|ψₙ|²")
        a1.axvspan(0.5 - dx, 0.5 + dx, color=COL["cinetica"], alpha=0.15, label="⟨x⟩ ± Δx")
        a1.set_xlabel("x / L")
        a1.legend(loc="upper right", fontsize=8.5)
        a1.set_title(f"Estado n = {n}")
        a2.plot(ns, productos, "o-", color=COL["onda"], lw=1.8, label="Δx·Δp")
        a2.axhline(0.5, color=COL["energia"], ls="--", lw=1.8, label="límite ħ/2")
        a2.plot([n], [prod], "s", color=COL["densidad"], ms=9)
        a2.set_xlabel("n")
        a2.set_ylabel("Δx·Δp [ħ]")
        a2.set_title("Siempre por encima de ħ/2")
        a2.legend(fontsize=8.5)
        dibujar(fig, "incertidumbre_caja.png")
        st.caption("El producto crece con n: aunque ψₙ sea un estado estacionario, Δp aumenta como n y Δx tiende a L/√12.")


PREGUNTAS = [
    {"enunciado": "Si dos operadores conmutan, [Â, B̂] = 0, entonces...",
     "opciones": ["sus observables pueden conocerse simultáneamente con exactitud", "no se pueden medir nunca",
                  "tienen los mismos autovalores", "deben ser iguales"],
     "correcta": 0, "explicacion": "Tienen un conjunto común de autofunciones, así que el estado puede ser autofunción de ambos."},
    {"enunciado": "El conmutador [x̂, p̂ₓ] vale...",
     "opciones": ["0", "iħ", "ħ/2", "−ħ²"],
     "correcta": 1, "explicacion": "[x̂, p̂ₓ]f = iħ f para cualquier f."},
    {"enunciado": "El principio de incertidumbre para posición y momento dice que...",
     "opciones": ["Δx·Δp ≥ ħ/2", "Δx·Δp = 0", "Δx + Δp ≥ ħ", "Δx·Δp ≤ ħ/2"],
     "correcta": 0, "explicacion": "Es el caso particular de ΔaΔb ≥ ½|⟨[Â,B̂]⟩| con [x̂,p̂] = iħ."},
    {"enunciado": "Para el estado fundamental de una partícula en una caja, Δx·Δp es aproximadamente...",
     "opciones": ["0.568 ħ", "0.25 ħ", "ħ", "0"],
     "correcta": 0, "explicacion": "ΔxΔp = ħ√((π² − 6)/12) ≈ 0.568 ħ, algo mayor que ħ/2."},
    {"enunciado": "¿Cuál de estas parejas de observables SÍ puede conocerse a la vez con exactitud?",
     "opciones": ["x y $p_x$", "x e y", "x y la energía de una partícula en una caja", "$p_x$ y x²"],
     "correcta": 1, "explicacion": "Las tres componentes de la posición conmutan entre sí."},
    {"enunciado": "Si el momento de una partícula se conoce exactamente (Δp = 0), la posición...",
     "opciones": ["queda completamente indeterminada (Δx → ∞)", "es exacta", "es cero", "es la mitad"],
     "correcta": 0, "explicacion": "Δx·Δp ≥ ħ/2 exige Δx infinito si Δp = 0: un estado de momento definido es una onda plana."},
]
