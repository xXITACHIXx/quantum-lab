"""
teoria/postulados.py — Teoría: Los postulados de la mecánica cuántica
"""

import numpy as np
import streamlit as st
from scipy.integrate import trapezoid

import quantum_lab_comun as qc
from teoria._util import COL, figura, dibujar


# ---------------------------------------------------------------------
# Física del simulador de medidas: superposición de estados de la caja (E_n = n² E₁)
# ---------------------------------------------------------------------
def probabilidades(coef) -> np.ndarray:
    """p_n = |b_n|² / Σ|b|²  (normaliza los coeficientes que dé el usuario)."""
    c = np.asarray(coef, dtype=complex)
    pesos = np.abs(c) ** 2
    total = pesos.sum()
    if total == 0:
        raise ValueError("Todos los coeficientes son cero: no hay estado.")
    return pesos / total


def energia_esperada(coef) -> float:
    """⟨E⟩ = Σ |b_n|² E_n en unidades de E₁ (E_n = n²)."""
    p = probabilidades(coef)
    n = np.arange(1, len(p) + 1)
    return float(np.sum(p * n ** 2))


def energia_esperada_por_integral(coef, L: float = 1.0, puntos: int = 40001) -> float:
    """
    Comprobación independiente del postulado 4: ⟨E⟩/E₁ = ∫Ψ* Ĥ Ψ dx / ∫Ψ*Ψ dx, con Ĥ = −(ħ²/2m)d²/dx²
    aplicada numéricamente (diferencias finitas) a la superposición, en unidades de E₁ = π²ħ²/2mL².
    """
    c = np.asarray(coef, dtype=complex)
    x = np.linspace(0, L, puntos)
    psi = sum(c[n - 1] * np.sqrt(2 / L) * np.sin(n * np.pi * x / L) for n in range(1, len(c) + 1))
    dx = x[1] - x[0]
    d2 = np.zeros_like(psi)
    d2[1:-1] = (psi[2:] - 2 * psi[1:-1] + psi[:-2]) / dx ** 2
    E1_en_unidades = np.pi ** 2 / (2 * L ** 2)                # ħ = m = 1
    num = trapezoid(np.conj(psi) * (-0.5 * d2), x).real
    den = trapezoid(np.abs(psi) ** 2, x).real
    return float(num / den / E1_en_unidades)


def simular_medidas(coef, n_medidas: int, semilla: int) -> np.ndarray:
    """Cada medida de la energía da UNO de los autovalores n² con probabilidad p_n."""
    p = probabilidades(coef)
    rng = np.random.default_rng(semilla)
    n = rng.choice(np.arange(1, len(p) + 1), size=n_medidas, p=p)
    return n ** 2


def mostrar() -> None:
    sub = st.tabs(["1. Función de onda", "2. Operadores", "3. La medida", "4. Valor esperado", "5. Evolución temporal",
                   "Simulador de medidas"])
    with sub[0]:
        qc.seccion("Postulado 1 · El estado y la probabilidad")
        st.markdown(
            "El estado de un sistema cuántico queda completamente especificado por una **función de onda** Ψ(x, t). "
            "La probabilidad de encontrar la partícula, en el instante t₀, en un intervalo dx alrededor de x₀ es")
        st.latex(r"P(x_0,t_0)=\Psi^*(x_0,t_0)\,\Psi(x_0,t_0)\,dx=|\Psi(x_0,t_0)|^2dx")
        st.markdown(
            "La amplitud Ψ en sí misma no tiene un significado físico directo (puede ser compleja o negativa); lo que "
            "tiene sentido es |Ψ|², una **densidad de probabilidad**. Como la partícula tiene que estar en algún lugar, "
            "la función debe estar **normalizada**:")
        st.latex(r"\int_{-\infty}^{\infty}\Psi^*(x,t)\,\Psi(x,t)\,dx=1")
        qc.seccion("Condiciones para que Ψ sea aceptable")
        st.markdown(
            "1. **Univaluada**: un solo valor en cada punto (si no, habría dos probabilidades distintas para el mismo lugar).\n"
            "2. **Continua, y con primera derivada continua** (salvo donde el potencial sea infinito): así la segunda derivada "
            "existe y la ecuación de Schrödinger tiene sentido.\n"
            "3. **De cuadrado integrable**: ∫|ψ|² dx < ∞, lo que exige ψ → 0 cuando x → ±∞.")
        qc.tabla_libre([
            {"Función": "e^(−x²)", "¿Aceptable?": "Sí", "Motivo": "continua, derivable y se anula en ±∞"},
            {"Función": "e^(x²)", "¿Aceptable?": "No", "Motivo": "crece sin límite: ∫|ψ|² diverge"},
            {"Función": "1/x", "¿Aceptable?": "No", "Motivo": "no está definida en x = 0 y ∫|ψ|² diverge allí"},
            {"Función": "sin x (en toda la recta)", "¿Aceptable?": "No", "Motivo": "no se anula en el infinito: no es de cuadrado integrable"},
            {"Función": "|x| e^(−|x|)", "¿Aceptable?": "No (si V es finita)", "Motivo": "su derivada salta en x = 0: no hay segunda derivada"},
            {"Función": "sin(πx/L) en [0, L]", "¿Aceptable?": "Sí (caja)", "Motivo": "se anula en las paredes, donde V → ∞"},
        ])
    with sub[1]:
        qc.seccion("Postulado 2 · Cada observable tiene un operador")
        st.markdown(
            "Para cada propiedad medible (posición, momento, energía…) existe un **operador** en mecánica cuántica. Un "
            "experimento de laboratorio que mide esa propiedad se representa, en la teoría, actuando con el operador sobre "
            "la función de onda. Todos estos operadores son **hermíticos**, lo que garantiza autovalores reales.")
        st.latex(r"\int\psi^*(x)\,[\hat A\psi(x)]\,dx=\int\psi(x)\,[\hat A\psi(x)]^*dx")
        qc.tabla_libre([
            {"Observable": "Posición", "Operador": "x̂ = x (multiplicar por x)"},
            {"Observable": "Momento lineal", "Operador": "p̂ₓ = −iħ d/dx"},
            {"Observable": "Energía cinética", "Operador": "T̂ = −(ħ²/2m) d²/dx²"},
            {"Observable": "Energía potencial", "Operador": "V̂ = V(x) (multiplicar por V)"},
            {"Observable": "Energía total", "Operador": "Ĥ = T̂ + V̂"},
            {"Observable": "Componente z del momento angular", "Operador": "L̂_z = −iħ ∂/∂φ"},
        ])
    with sub[2]:
        qc.seccion("Postulado 3 · Una medida individual")
        st.markdown(
            "En una sola medida de la magnitud asociada al operador Â, **los únicos valores que se pueden obtener son los "
            "autovalores de Â**. Por ejemplo, al medir la energía del átomo de hidrógeno solo salen los valores Eₙ de "
            "la ecuación de Schrödinger; nunca uno intermedio.")
        st.latex(r"\hat H\,\Psi_n=E_n\,\Psi_n")
        st.markdown(
            "Importante: la función de onda del sistema **no** tiene que ser una autofunción de Ĥ. Las autofunciones "
            "son solo un subconjunto de todas las funciones aceptables. Si el estado es una superposición, el resultado de "
            "cada medida es uno de los autovalores, pero no se puede predecir cuál: solo su probabilidad.")
    with sub[3]:
        qc.seccion("Postulado 4 · El valor esperado")
        st.markdown(
            "Si se mide a en muchos sistemas idénticamente preparados en el estado Ψ, el **promedio** de los resultados es "
            "el valor esperado:")
        st.latex(r"\langle a\rangle=\frac{\int\Psi^*\hat A\Psi\,dx}{\int\Psi^*\Psi\,dx}")
        st.markdown("(Con Ψ normalizada, el denominador vale 1.) Hay dos casos:")
        st.markdown("**Caso 1: Ψ es autofunción de Â**, con Âφⱼ = aⱼφⱼ. Entonces ⟨a⟩ = aⱼ y cada medida da exactamente aⱼ.")
        st.markdown("**Caso 2: Ψ no es autofunción.** Como las autofunciones de Â forman un conjunto completo, se desarrolla "
                    "Ψ = Σ bₙφₙ. Con la ortonormalidad:")
        st.latex(r"\langle a\rangle=\sum_n a_n\,|b_n|^2,\qquad \sum_n|b_n|^2=1")
        st.markdown(
            "El coeficiente |bₙ|² es la **probabilidad** de medir el autovalor aₙ. Cuanto mayor es |bₙ|², más probable es "
            "obtener aₙ y más pesa en el promedio. Ejemplo: un átomo de hidrógeno preparado como "
            "Ψ = b₁Ψ₁ₛ + b₂Ψ₂ₛ + b₃Ψ₂ₚ + b₄Ψ₃ₛ solo puede dar E₁ₛ, E₂ₛ, E₂ₚ o E₃ₛ en una medida, cada una con probabilidad |bₙ|².")
    with sub[4]:
        qc.seccion("Postulado 5 · Evolución en el tiempo")
        st.markdown("La evolución temporal de un sistema cuántico la gobierna la ecuación de Schrödinger dependiente del tiempo:")
        st.latex(r"\hat H\,\Psi(x,t)=i\hbar\,\frac{\partial\Psi(x,t)}{\partial t},\qquad \hat H=-\frac{\hbar^2}{2m}\frac{\partial^2}{\partial x^2}+V(x,t)")
        st.markdown("Para los estados estacionarios, Ψ(x, t) = ψ(x) e^(−iEt/ħ). Como el factor temporal sale fuera de cualquier "
                    "operador Â(x) que no dependa del tiempo:")
        st.latex(r"\hat A(x)\,\Psi_n(x,t)=a_n\Psi_n(x,t)\ \Longleftrightarrow\ \hat A(x)\,\psi_n(x)=a_n\,\psi_n(x)")
        st.markdown("Las ecuaciones de autovalores se pueden escribir usando solo la parte espacial ψ(x).")
    with sub[5]:
        qc.seccion("Mide la energía de una superposición en la caja")
        st.markdown(
            "Preparar el estado Ψ = b₁φ₁ + b₂φ₂ + b₃φ₃ + b₄φ₄ de una partícula en una caja (Eₙ = n² E₁). Los coeficientes se "
            "normalizan solos. Cada medida da E₁, 4E₁, 9E₁ o 16E₁; el promedio de muchas medidas se acerca al valor esperado.")
        cols = st.columns(4)
        defecto = [1.0, 0.8, 0.0, 0.4]
        coef = [col.slider(f"|b{i + 1}|", 0.0, 1.0, defecto[i], 0.05, key=f"po_b{i + 1}") for i, col in enumerate(cols)]
        c1, c2 = st.columns(2)
        with c1:
            n_med = st.slider("Número de medidas", 10, 20000, 500, 10, key="po_nm")
        with c2:
            semilla = st.number_input("Semilla aleatoria", 0, 10 ** 6, 1, key="po_seed",
                                      help="Cambiar la semilla para repetir el experimento con otros resultados.")
        if sum(c ** 2 for c in coef) == 0:
            st.error("Establecer al menos un coeficiente distinto de cero.", icon=":material/error:")
            return
        p = probabilidades(coef)
        e_esp = energia_esperada(coef)
        medidas = simular_medidas(coef, n_med, int(semilla))
        fig, (a1, a2) = figura(10, 4.2, columnas=2)
        niveles = np.array([1, 4, 9, 16])
        frec = np.array([(medidas == n).mean() for n in niveles])
        ancho = 0.38
        a1.bar(np.arange(4) - ancho / 2, p, ancho, color=COL["onda"], label="|bₙ|² (teoría)")
        a1.bar(np.arange(4) + ancho / 2, frec, ancho, color=COL["densidad"], label="frecuencia medida")
        a1.set_xticks(range(4), [f"E = {n} E₁" for n in niveles])
        a1.set_ylabel("probabilidad")
        a1.set_title("Resultados posibles de una medida")
        a1.legend(fontsize=8.5)
        promedio = np.cumsum(medidas) / np.arange(1, n_med + 1)
        a2.plot(np.arange(1, n_med + 1), promedio, color=COL["densidad"], lw=1.8, label="promedio de las medidas")
        a2.axhline(e_esp, color=COL["energia"], ls="--", lw=1.8, label=f"⟨E⟩ = {e_esp:.3f} E₁")
        a2.set_xscale("log")
        a2.set_xlabel("número de medidas")
        a2.set_ylabel("energía media [E₁]")
        a2.set_title("El promedio converge al valor esperado")
        a2.legend(fontsize=8.5)
        dibujar(fig, "postulados_medidas.png")
        qc.metricas([("⟨E⟩ = Σ |bₙ|² Eₙ", f"{e_esp:.4f} E₁"), ("Promedio medido", f"{promedio[-1]:.4f} E₁"),
                     ("⟨E⟩ por integral ∫Ψ*ĤΨ", f"{energia_esperada_por_integral(coef):.4f} E₁")], columnas=3)
        st.caption("La tercera cifra se obtiene aplicando el hamiltoniano a la función Ψ y integrando (postulado 4 en su forma "
                   "integral); coincide con la suma Σ |bₙ|² Eₙ.")


PREGUNTAS = [
    {"enunciado": "El postulado 1 asocia con |Ψ(x, t)|² dx...",
     "opciones": ["la probabilidad de encontrar la partícula en dx", "la energía en dx", "el momento", "la fase"],
     "correcta": 0, "explicacion": "|Ψ|² es una densidad de probabilidad por unidad de longitud."},
    {"enunciado": "¿Cuál de estas funciones NO es aceptable como función de onda en toda la recta real?",
     "opciones": ["e^(−x²)", "e^(x²)", "x e^(−x²)", "e^(−|x|)"],
     "correcta": 1, "explicacion": "e^(x²) crece sin límite; su integral de cuadrado diverge."},
    {"enunciado": "En una medida individual de la energía, los valores que se pueden obtener son...",
     "opciones": ["cualquier valor real", "los autovalores del hamiltoniano", "solo el valor esperado", "solo el estado fundamental"],
     "correcta": 1, "explicacion": "Postulado 3: solo se miden autovalores del operador."},
    {"enunciado": "Si Ψ = b₁φ₁ + b₂φ₂ con |b₁|² = 0.25 y |b₂|² = 0.75, el valor esperado de a es...",
     "opciones": ["0.25 a₁ + 0.75 a₂", "a₁ + a₂", "0.75 a₁ + 0.25 a₂", "(a₁ + a₂)/2 siempre"],
     "correcta": 0, "explicacion": "⟨a⟩ = Σ aₙ|bₙ|²: cada autovalor pesa su probabilidad."},
    {"enunciado": "Si Ψ es autofunción de Â con autovalor aⱼ, cada medida de a da...",
     "opciones": ["aⱼ siempre", "un valor aleatorio", "cero", "el promedio de todos los autovalores"],
     "correcta": 0, "explicacion": "Con un solo coeficiente distinto de cero (|bⱼ|² = 1) no hay incertidumbre en a."},
    {"enunciado": "En un estado estacionario, el factor temporal e^(−iEt/ħ)...",
     "opciones": ["es solo una fase y no cambia |Ψ|²", "cambia la probabilidad", "elimina la energía", "es un operador"],
     "correcta": 0, "explicacion": "|e^(−iEt/ħ)| = 1, así que Ψ*Ψ = ψ*ψ."},
]
