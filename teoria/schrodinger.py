"""
teoria/schrodinger.py — Teoría: La ecuación de Schrödinger (semana 2).
"""

import numpy as np
import streamlit as st
from scipy.linalg import eigh_tridiagonal

import quantum_lab_comun as qc
from teoria._util import COL, figura, dibujar


def energias_numericas(sistema: str, n_puntos: int, n_estados: int = 4):
    """
    Resuelve −½ψ'' + Vψ = Eψ (unidades atómicas, ħ = m = 1) con diferencias finitas.

    sistema "caja"       : pozo infinito en [0, 1];          exacto E_n = n²π²/2
    sistema "oscilador"  : V = ½x², malla en [−8, 8];         exacto E_n = n + ½
    Devuelve (x, energías, funciones normalizadas, energías exactas).
    """
    if sistema == "caja":
        x = np.linspace(0.0, 1.0, n_puntos + 2)[1:-1]
        V = np.zeros_like(x)
        exactas = np.array([(n * np.pi) ** 2 / 2 for n in range(1, n_estados + 1)])
    else:
        x = np.linspace(-8.0, 8.0, n_puntos)
        V = 0.5 * x ** 2
        exactas = np.array([n + 0.5 for n in range(n_estados)])
    dx = x[1] - x[0]
    diag = 1.0 / dx ** 2 + V
    fuera = -0.5 / dx ** 2 * np.ones(len(x) - 1)
    E, psi = eigh_tridiagonal(diag, fuera, select="i", select_range=(0, n_estados - 1))
    psi = psi / np.sqrt(dx)              # ∫|ψ|² dx = 1
    return x, E, psi, exactas


def mostrar() -> None:
    sub = st.tabs(["De la onda clásica a Schrödinger", "Dependiente del tiempo", "Estados estacionarios",
                   "Resolverla numéricamente", "Resumen"])
    with sub[0]:
        qc.seccion("Una justificación, no una demostración")
        st.markdown(
            "La ecuación de Schrödinger es un **postulado**: no se deduce de principios más básicos, se justifica porque "
            "sus predicciones coinciden con el experimento. Aun así, hay un camino que la hace natural y que combina dos "
            "ingredientes de las semanas anteriores: la ecuación de onda clásica y la relación de De Broglie.")
        st.markdown("**Paso 1.** Una onda estacionaria clásica se puede escribir Ψ(x, t) = ψ(x)θ(t). Al sustituirla en la "
                    "ecuación de onda y quedarnos con la parte espacial queda:")
        st.latex(r"\frac{d^2\psi}{dx^2}+\frac{4\pi^2}{\lambda^2}\,\psi=0")
        st.markdown("**Paso 2.** Para una partícula con energía total E en un potencial V(x), la energía cinética es "
                    "E − V(x) = p²/2m, o sea p² = 2m(E − V).")
        st.markdown("**Paso 3.** Introducimos la idea cuántica: la longitud de onda es la de De Broglie, λ = h/p. Entonces "
                    "4π²/λ² = 4π²p²/h² = p²/ħ² = 2m(E − V)/ħ². Sustituyendo:")
        st.latex(r"-\frac{\hbar^2}{2m}\frac{d^2\psi(x)}{dx^2}+V(x)\,\psi(x)=E\,\psi(x)")
        st.markdown("Esta es la **ecuación de Schrödinger independiente del tiempo** en una dimensión. Es la ecuación "
                    "fundamental para estudiar los **estados estacionarios** de un sistema cuántico.")
    with sub[1]:
        qc.seccion("Cuando el sistema evoluciona")
        st.markdown("El análogo cuántico de la ecuación de onda dependiente del tiempo es la ecuación de Schrödinger "
                    "dependiente del tiempo:")
        st.latex(r"-\frac{\hbar^2}{2m}\frac{\partial^2\Psi(x,t)}{\partial x^2}+V(x,t)\,\Psi(x,t)=i\hbar\,\frac{\partial\Psi(x,t)}{\partial t}")
        st.markdown("Relaciona las derivadas espacial y temporal de Ψ con la energía potencial. Se aplica sobre todo a "
                    "sistemas cuya energía cambia con el tiempo. A diferencia de la ecuación de onda clásica, es de "
                    "primer orden en el tiempo y contiene el factor i: por eso Ψ es una función **compleja**.")
        st.latex(r"\hat H\,\Psi(x,t)=i\hbar\,\frac{\partial\Psi(x,t)}{\partial t},\qquad \hat H=-\frac{\hbar^2}{2m}\frac{\partial^2}{\partial x^2}+V(x,t)")
    with sub[2]:
        qc.seccion("Separar el tiempo")
        st.markdown("Si V no depende del tiempo, buscamos soluciones de la forma Ψ(x, t) = ψ(x)θ(t). Los estados que cumplen "
                    "ambas ecuaciones de Schrödinger satisfacen iħ ∂Ψ/∂t = EΨ. Entonces:")
        st.latex(r"i\hbar\frac{d\theta}{dt}=E\theta\ \Rightarrow\ \theta(t)=e^{-iEt/\hbar}\qquad\Rightarrow\qquad \Psi(x,t)=\psi(x)\,e^{-iEt/\hbar}")
        st.markdown(
            "La parte espacial ψ(x) cumple la ecuación independiente del tiempo. El factor temporal es solo una **fase** "
            "que gira a frecuencia E/ħ, así que")
        st.latex(r"|\Psi(x,t)|^2=\Psi^*\Psi=|\psi(x)|^2\qquad\text{(no depende de }t)")
        st.markdown(
            "Por eso se llaman **estados estacionarios**: la energía está definida y la densidad de probabilidad no cambia "
            "con el tiempo. Solo una **combinación** de estados con energías distintas (una superposición) produce una "
            "densidad que se mueve; eso se explora en los simuladores de la caja y del oscilador.")
    with sub[3]:
        qc.seccion("Resolver la ecuación con el ordenador")
        st.markdown(
            "En la mayoría de los sistemas reales la ecuación no tiene solución exacta. Una forma de resolverla es "
            "discretizar x en una malla: la segunda derivada se aproxima con diferencias finitas y el problema se "
            "convierte en hallar los autovalores de una matriz (el hamiltoniano discretizado). Aquí se usa para dos "
            "sistemas con solución exacta, de modo que se pueda comparar. Unidades atómicas (ħ = m = 1).")
        c1, c2 = st.columns(2)
        with c1:
            sistema = st.radio("Sistema", ["Partícula en una caja (L = 1)", "Oscilador armónico (ω = 1)"], key="sc_sis")
        with c2:
            n_pts = st.slider("Puntos de la malla", 50, 1500, 400, 50, key="sc_n")
        clave = "caja" if sistema.startswith("Part") else "oscilador"
        x, E, psi, exactas = energias_numericas(clave, n_pts)
        fig, ax = figura(9.5, 5.0)
        esc = 0.25 * (exactas[1] - exactas[0])
        for i in range(len(E)):
            signo = 1.0 if psi[np.argmax(np.abs(psi[:, i])), i] > 0 else -1.0
            ax.plot(x, E[i] + esc * signo * psi[:, i] / np.max(np.abs(psi[:, i])), color=COL["onda"], lw=2)
            ax.axhline(E[i], color=COL["energia"], lw=0.8, ls=":")
        if clave == "oscilador":
            ax.plot(x, 0.5 * x ** 2, color=COL["potencial"], lw=1.6, label="V(x) = ½x²")
            ax.set_ylim(0, exactas[-1] + 1.5)
            ax.set_xlim(-6, 6)
            ax.legend(loc="upper center")
        ax.set_xlabel("x")
        ax.set_ylabel("energía  (cada ψ se dibuja sobre su nivel)")
        ax.set_title("Autofunciones del hamiltoniano discretizado")
        dibujar(fig, "schrodinger_numerica.png")
        filas = [{"n": str(i + (1 if clave == "caja" else 0)), "E numérica": f"{E[i]:.6f}", "E exacta": f"{exactas[i]:.6f}",
                  "Error relativo": f"{abs(E[i] - exactas[i]) / exactas[i]:.2e}"} for i in range(len(E))]
        qc.tabla_libre(filas, numericas=("E numérica", "E exacta", "Error relativo"))
        st.caption("Con más puntos de malla el error disminuye. Los niveles son discretos: la cuantización aparece sola al "
                   "exigir que ψ se anule en las paredes (caja) o en el infinito (oscilador).")
    with sub[4]:
        qc.seccion("Resumen de ecuaciones")
        qc.tabla_libre([
            {"Concepto": "Ecuación independiente del tiempo", "Ecuación": "−(ħ²/2m) ψ'' + V ψ = E ψ"},
            {"Concepto": "Ecuación dependiente del tiempo", "Ecuación": "Ĥ Ψ = iħ ∂Ψ/∂t"},
            {"Concepto": "Estado estacionario", "Ecuación": "Ψ(x,t) = ψ(x) e^(−iEt/ħ)"},
            {"Concepto": "Densidad de probabilidad", "Ecuación": "|Ψ|² = |ψ|² (independiente de t)"},
            {"Concepto": "Hamiltoniano", "Ecuación": "Ĥ = −(ħ²/2m) d²/dx² + V(x)"},
        ])


PREGUNTAS = [
    {"enunciado": "La ecuación de Schrödinger independiente del tiempo es una ecuación de...",
     "opciones": ["autovalores del hamiltoniano", "Newton para la posición", "Maxwell", "difusión"],
     "correcta": 0, "explicacion": "Ĥψ = Eψ: ψ es autofunción de Ĥ y E es el autovalor (la energía)."},
    {"enunciado": "En un estado estacionario, la densidad de probabilidad |Ψ(x, t)|²...",
     "opciones": ["oscila con frecuencia E/ħ", "no depende del tiempo", "es siempre cero", "crece con t"],
     "correcta": 1, "explicacion": "Ψ = ψ(x)e^(−iEt/ħ): el factor temporal tiene módulo 1 y se cancela en Ψ*Ψ."},
    {"enunciado": "¿De qué ingredientes se parte para justificar la ecuación independiente del tiempo?",
     "opciones": ["Ecuación de onda clásica y relación de De Broglie", "Ley de Wien y Stefan–Boltzmann",
                  "Condición de Bohr y serie de Balmer", "Teoría de la relatividad"],
     "correcta": 0, "explicacion": "Se combina la parte espacial de la onda estacionaria con λ = h/p y p² = 2m(E − V)."},
    {"enunciado": "¿Por qué la función de onda Ψ debe ser compleja?",
     "opciones": ["Porque la ecuación contiene i y es de primer orden en el tiempo",
                  "Porque la energía es negativa", "Porque la masa es compleja", "No tiene que serlo"],
     "correcta": 0, "explicacion": "En iħ∂Ψ/∂t = ĤΨ el factor i obliga a que las soluciones sean complejas."},
    {"enunciado": "En el cálculo numérico, al aumentar los puntos de la malla el error en la energía...",
     "opciones": ["disminuye", "aumenta", "no cambia", "se vuelve negativo"],
     "correcta": 0, "explicacion": "La aproximación por diferencias finitas mejora al reducir el paso dx."},
]
