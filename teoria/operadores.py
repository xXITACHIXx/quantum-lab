"""
teoria/operadores.py — Teoría: Operadores, autofunciones, ortogonalidad y completitud
"""

import numpy as np
import streamlit as st
from scipy.integrate import quad, trapezoid

import quantum_lab_comun as qc
from teoria._util import COL, figura, dibujar


# ---------------------------------------------------------------------
# Probador de autofunciones (ħ = 1)
# ---------------------------------------------------------------------
FUNCIONES = {
    "e^(i·2x)": (lambda x: np.exp(2j * x), lambda x: 2j * np.exp(2j * x), lambda x: -4 * np.exp(2j * x)),
    "sin(2x)": (lambda x: np.sin(2 * x), lambda x: 2 * np.cos(2 * x), lambda x: -4 * np.sin(2 * x)),
    "cos(3x)": (lambda x: np.cos(3 * x), lambda x: -3 * np.sin(3 * x), lambda x: -9 * np.cos(3 * x)),
    "e^(−x²)": (lambda x: np.exp(-x ** 2), lambda x: -2 * x * np.exp(-x ** 2), lambda x: (4 * x ** 2 - 2) * np.exp(-x ** 2)),
    "e^(3x)": (lambda x: np.exp(3 * x), lambda x: 3 * np.exp(3 * x), lambda x: 9 * np.exp(3 * x)),
}
OPERADORES = ["d/dx", "d²/dx²", "x (multiplicar por x)", "p̂ = −i d/dx  (ħ = 1)"]


def aplicar_operador(nombre: str, f_tuple, x):
    f, f1, f2 = f_tuple
    f0 = f(x)
    if nombre == "d/dx":
        return f0, f1(x)
    if nombre == "d²/dx²":
        return f0, f2(x)
    if nombre.startswith("x"):
        return f0, x * f0
    return f0, -1j * f1(x)


def probar_autofuncion(nombre_funcion: str, nombre_operador: str, tol: float = 1e-9):
    """
    Evalúa (Ôf)/f en varios puntos. Si el cociente es el mismo número en todos, f es autofunción y ese número
    es el autovalor. Devuelve (es_autofuncion, autovalor o None).
    """
    x = np.linspace(-1.3, 1.1, 37) + 0.0123          # puntos que evitan ceros exactos de f
    f0, Of = aplicar_operador(nombre_operador, FUNCIONES[nombre_funcion], x)
    ok = np.abs(f0) > 1e-9
    cociente = Of[ok] / f0[ok]
    if np.max(np.abs(cociente - cociente[0])) < tol * max(1.0, np.abs(cociente[0])):
        return True, complex(cociente[0])
    return False, None


# ---------------------------------------------------------------------
# Base de la caja: sin(nπx/L)
# ---------------------------------------------------------------------
def fi_caja(n: int, x, L: float = 1.0):
    return np.sqrt(2 / L) * np.sin(n * np.pi * x / L)


def matriz_de_solapamiento(N: int, L: float = 1.0, puntos: int = 20001):
    """S_nm = ∫₀ᴸ φ_n φ_m dx para las N primeras autofunciones de la caja."""
    x = np.linspace(0, L, puntos)
    F = np.array([fi_caja(n, x, L) for n in range(1, N + 1)])
    return np.array([[trapezoid(F[i] * F[j], x) for j in range(N)] for i in range(N)])


# Funciones objetivo para el desarrollo en la base de la caja
OBJETIVOS = {
    "Parábola x(L − x)": lambda x, L: x * (L - x),
    "Triángulo": lambda x, L: np.minimum(x, L - x),
    "Pulso cuadrado (L/4 a 3L/4)": lambda x, L: ((x > L / 4) & (x < 3 * L / 4)).astype(float),
    "Función con pico a la izquierda": lambda x, L: np.exp(-((x - 0.25 * L) / (0.08 * L)) ** 2),
}


def desarrollar(nombre: str, N: int, L: float = 1.0, puntos: int = 8001):
    """Coeficientes b_n = ∫φ_n ψ dx del objetivo normalizado y su aproximación con N términos."""
    x = np.linspace(0, L, puntos)
    psi = OBJETIVOS[nombre](x, L).astype(float)
    psi = psi / np.sqrt(trapezoid(psi ** 2, x))
    nmax = max(N, 60)
    b = np.array([trapezoid(fi_caja(n, x, L) * psi, x) for n in range(1, nmax + 1)])
    aprox = sum(b[n - 1] * fi_caja(n, x, L) for n in range(1, N + 1))
    return x, psi, b, aprox


def constante_de_normalizacion(nombre: str, a: float):
    """Devuelve (N numérica, N analítica, integral de |f|²) para f en el intervalo indicado."""
    if nombre == "x(a − x) en [0, a]":
        f2 = lambda x: (x * (a - x)) ** 2
        integral = quad(f2, 0, a)[0]
        analitica = np.sqrt(30 / a ** 5)
    elif nombre == "sin(πx/a) en [0, a]":
        integral = quad(lambda x: np.sin(np.pi * x / a) ** 2, 0, a)[0]
        analitica = np.sqrt(2 / a)
    else:                                               # e^(−x/a) en [0, ∞)
        integral = quad(lambda x: np.exp(-2 * x / a), 0, np.inf)[0]
        analitica = np.sqrt(2 / a)
    return 1 / np.sqrt(integral), float(analitica), integral


def mostrar() -> None:
    sub = st.tabs(["Operadores y autovalores", "El hamiltoniano", "Ortogonalidad", "Completitud", "Normalización"])
    with sub[0]:
        qc.seccion("Una cantidad medible, un operador")
        st.markdown(
            "A cada magnitud medible (posición, momento, energía…) le corresponde un **operador**: una instrucción que "
            "actúa sobre una función y devuelve otra. Casi siempre es derivar respecto de una variable o multiplicar por "
            "ella. Se escribe con un acento circunflejo: Ô.")
        st.markdown("Para un operador Ô puede haber funciones ψₙ tales que")
        st.latex(r"\hat O\,\psi_n=a_n\,\psi_n")
        st.markdown(
            "Son sus **autofunciones**, y los números aₙ son sus **autovalores**. Los operadores de la mecánica cuántica "
            "tienen **autovalores reales**, porque son los valores que se miden en un experimento.")
        qc.seccion("Prueba si una función es autofunción")
        c1, c2 = st.columns(2)
        with c1:
            nf = st.selectbox("Función f(x)", list(FUNCIONES), key="op_f")
        with c2:
            no = st.selectbox("Operador", OPERADORES, key="op_o")
        ok, lam = probar_autofuncion(nf, no)
        if ok:
            valor = f"{lam.real:.4g}" if abs(lam.imag) < 1e-12 else f"{lam.real:.4g} {lam.imag:+.4g}i"
            st.success(f"**Sí**: Ô f = a · f con a = {valor}. El resultado es la misma función multiplicada por una constante.",
                       icon=":material/check_circle:")
        else:
            st.error("**No**: Ô f no es proporcional a f (el cociente (Ôf)/f cambia con x).", icon=":material/close:")
        st.caption("La prueba compara (Ôf)/f en 37 puntos: es autofunción si el cociente es el mismo en todos.")
        st.markdown("Observa un caso instructivo: sin(2x) **no** es autofunción de d/dx, pero sí de d²/dx² con autovalor −4.")
    with sub[1]:
        qc.seccion("El operador de la energía")
        st.markdown("El operador de la energía total se llama **hamiltoniano** (por razones históricas):")
        st.latex(r"\hat H=-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}+V(x)")
        st.markdown(
            "La ecuación de Schrödinger independiente del tiempo es entonces la ecuación de autovalores de la energía:")
        st.latex(r"\hat H\,\psi_n(x)=E_n\,\psi_n(x)")
        st.markdown(
            "Al actuar sobre una de sus autofunciones, Ĥ devuelve la misma función multiplicada por su energía. Resolver "
            "un sistema cuántico significa encontrar las autofunciones ψₙ y las energías permitidas Eₙ.")
    with sub[2]:
        qc.seccion("Funciones ortogonales")
        st.markdown(
            "Dos vectores son perpendiculares si su producto escalar es cero. Para funciones, el análogo es la integral del "
            "producto. Dos autofunciones ψᵢ y ψⱼ (con autovalores distintos) son **ortogonales**:")
        st.latex(r"\int_{-\infty}^{\infty}\psi_i^*(x)\,\psi_j(x)\,dx=0\qquad (i\neq j)")
        st.markdown("Se usa el conjugado ψᵢ* porque las funciones pueden ser complejas. Si además la integral vale 1 cuando "
                    "i = j, las funciones están **normalizadas** y forman un conjunto **ortonormal**: ∫ψᵢ*ψⱼ dx = δᵢⱼ.")
        qc.seccion("Compruébalo para la partícula en una caja")
        N = st.slider("Número de funciones sin(nπx/L)", 2, 8, 5, 1, key="op_N")
        S = matriz_de_solapamiento(N)
        fig, ax = figura(5.6, 4.8)
        im = ax.imshow(S, cmap="magma", vmin=0, vmax=1)
        ax.set_xticks(range(N), [str(i + 1) for i in range(N)])
        ax.set_yticks(range(N), [str(i + 1) for i in range(N)])
        for i in range(N):
            for j in range(N):
                ax.text(j, i, f"{S[i, j]:.2f}", ha="center", va="center", color="white" if S[i, j] < 0.6 else "black", fontsize=9)
        ax.set_xlabel("m")
        ax.set_ylabel("n")
        ax.set_title(r"$\int_0^L\varphi_n\,\varphi_m\,dx$")
        ax.grid(False)
        dibujar(fig, "ortogonalidad_caja.png")
        st.caption("La diagonal vale 1 (normalizadas) y el resto 0 (ortogonales); los valores pequeños distintos de cero "
                   "son error numérico de la integral.")
    with sub[3]:
        qc.seccion("Cualquier función se puede escribir con ellas")
        st.markdown(
            "Igual que cualquier vector se escribe como combinación de los tres vectores unitarios, cualquier función "
            "razonable ψ(x) se puede **desarrollar** en las autofunciones φₙ de un operador (conjunto **completo**):")
        st.latex(r"\psi(x)=\sum_{n=1}^{\infty}b_n\,\varphi_n(x),\qquad b_n=\int\varphi_n^*(x)\,\psi(x)\,dx")
        st.markdown("El coeficiente bₙ mide cuánto «se parece» ψ a la autofunción n-ésima. Más adelante se "
                    "verá que |bₙ|² es una probabilidad.")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.selectbox("Función a representar (en [0, L])", list(OBJETIVOS), key="op_obj")
        with c2:
            N = st.slider("Términos de la suma", 1, 40, 5, 1, key="op_Nt")
        x, psi, b, aprox = desarrollar(nombre, N)
        error = trapezoid((psi - aprox) ** 2, x)
        fig, (a1, a2) = figura(10, 4.2, columnas=2)
        a1.plot(x, psi, color=COL["gris"], lw=2.2, label="función exacta")
        a1.plot(x, aprox, color=COL["densidad"], lw=2.0, label=f"suma de {N} términos")
        a1.set_xlabel("x / L")
        a1.legend(loc="upper right", fontsize=8.5)
        a1.set_title("Reconstrucción")
        a2.bar(range(1, 16), b[:15] ** 2, color=COL["onda"])
        a2.set_xlabel("n")
        a2.set_ylabel(r"$b_n^2$")
        a2.set_title("Peso de cada autofunción")
        dibujar(fig, "completitud_caja.png")
        qc.metricas([("Σ bₙ² (N términos)", f"{np.sum(b[:N] ** 2):.6f}"), ("Error ∫(ψ − ψ_N)² dx", f"{error:.3e}")], columnas=2)
        st.caption("La función se normaliza antes de desarrollarla. Cuando N crece, Σ bₙ² tiende a 1 y el error a 0: esa es "
                   "la completitud. Las funciones con esquinas o saltos necesitan más términos.")
    with sub[4]:
        qc.seccion("Normalizar una función")
        st.markdown(
            "Para interpretar |ψ|² como probabilidad, la integral de |ψ|² sobre todo el dominio debe valer 1. Si una función "
            "f no cumple eso, se multiplica por una constante N: ψ = N f, con")
        st.latex(r"N^2\int f^*(x)\,f(x)\,dx=1\ \Rightarrow\ N=\left[\int|f|^2dx\right]^{-1/2}")
        qc.seccion("Ejemplo resuelto: f(x) = x(a − x) en [0, a]")
        st.latex(r"\int_0^a x^2(a-x)^2dx=\frac{a^5}{3}-\frac{a^5}{2}+\frac{a^5}{5}=\frac{a^5}{30}\ \Rightarrow\ N=\sqrt{\frac{30}{a^5}}")
        qc.seccion("Calculadora")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.selectbox("Función", ["x(a − x) en [0, a]", "sin(πx/a) en [0, a]", "e^(−x/a) en [0, ∞)"], key="op_nf")
        with c2:
            a = st.number_input("Parámetro a", 0.1, 100.0, 2.0, format="%.4g", key="op_a")
        num, ana, integral = constante_de_normalizacion(nombre, a)
        qc.metricas([("∫|f|² dx", f"{integral:.6g}"), ("N (integral numérica)", f"{num:.6g}"), ("N (fórmula)", f"{ana:.6g}")],
                    columnas=3)
        st.caption("Las dos formas de obtener N coinciden: la integral numérica y el resultado analítico.")


PREGUNTAS = [
    {"enunciado": "Si Ôψ = aψ, entonces...",
     "opciones": ["ψ es autofunción de Ô con autovalor a", "a es una función", "ψ es cero", "Ô es la identidad siempre"],
     "correcta": 0, "explicacion": "Esa es la definición de autofunción y autovalor."},
    {"enunciado": "¿Es e^(i k x) autofunción del operador d/dx?",
     "opciones": ["Sí, con autovalor ik", "No", "Sí, con autovalor k", "Solo si k = 0"],
     "correcta": 0, "explicacion": "d/dx e^(ikx) = ik e^(ikx): la misma función por la constante ik."},
    {"enunciado": "Dos autofunciones ψᵢ y ψⱼ de un operador hermítico con autovalores distintos cumplen...",
     "opciones": ["∫ψᵢ*ψⱼ dx = 0", "∫ψᵢ*ψⱼ dx = 1", "ψᵢ = ψⱼ", "∫ψᵢ ψⱼ dx = ∞"],
     "correcta": 0, "explicacion": "Son ortogonales; si además están normalizadas, ∫ψᵢ*ψⱼ dx = δᵢⱼ."},
    {"enunciado": "El coeficiente bₙ del desarrollo ψ = Σ bₙφₙ se calcula como...",
     "opciones": ["∫φₙ* ψ dx", "∫φₙ dx", "ψ(0)", "∫ψ² dx"],
     "correcta": 0, "explicacion": "Se proyecta ψ sobre φₙ usando la ortonormalidad."},
    {"enunciado": "La constante de normalización de f(x) = x(a − x) en [0, a] es...",
     "opciones": ["√(30/a⁵)", "√(3/a⁵)", "1/a", "a⁵/30"],
     "correcta": 0, "explicacion": "∫x²(a−x)²dx = a⁵/30, así que N = (a⁵/30)^(−1/2) = √(30/a⁵)."},
]
