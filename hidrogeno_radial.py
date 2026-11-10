"""
hidrogeno_radial.py — QUANTUM LAB · Simulador 07: átomo de hidrógeno, función radial
====================================================================================

Átomo hidrogenoide (Z = 1) resuelto con la ecuación de Schrödinger radial. Para cualquier estado (n, l):

    R_nl(r) = N · e^(−ρ/2) · ρ^l · L^(2l+1)_(n−l−1)(ρ),      ρ = 2r/(n a₀)
    P(r)    = r² |R_nl(r)|²                                    ∫₀^∞ P dr = 1
    ⟨r⟩     = (a₀/2) [3n² − l(l+1)]
    Eₙ      = −R∞ / n²                                         (no depende de l)

Además: nodos radiales (n − l − 1, ceros del polinomio de Laguerre), radio más probable y comprobación numérica de la
normalización. La distribución radial se dibuja en unidades de a₀ con ⟨r⟩ marcado.

Los resultados coinciden con los del cuaderno de Colab «Hidrogeno_radial» y se contrastan con `modelo_bohr.radial_hidrogeno`.

Estructura: 1. Física · 2. Figuras · 3. Pruebas · 4. Interfaz Streamlit
"""

from __future__ import annotations

import numbers
import re

import numpy as np
import streamlit as st
from scipy.optimize import minimize_scalar
from scipy.special import eval_genlaguerre, gammaln, roots_genlaguerre

import quantum_lab_comun as qc
from quantum_lab_comun import COLORES

# =====================================================================
# 1. FÍSICA
# =====================================================================
A0 = 5.29177210903e-11          # radio de Bohr, m
EV_A_J = 1.602176634e-19        # eV → J
RY = 13.605693009               # R∞, eV (núcleo de masa infinita)
MP_ME = 1836.15267343           # masa del protón / masa del electrón
LETRAS = "spdfghiklmnoqrtuvwxyz"
N_MAX = 60                      # límite de la interfaz (la función admite más)
_integrar = getattr(np, "trapezoid", None) or np.trapz


def validar_estado(n, l) -> tuple[int, int]:
    """n y l enteros con n ≥ 1 y 0 ≤ l ≤ n − 1. Devuelve (n, l) como int; lanza TypeError o ValueError."""
    for nombre, valor in (("n", n), ("l", l)):
        if isinstance(valor, bool) or not isinstance(valor, numbers.Integral):
            raise TypeError(f"{nombre} debe ser un número entero (se recibió {valor!r}): los números cuánticos solo "
                            "toman valores enteros porque la solución debe ser finita y univaluada.")
    n, l = int(n), int(l)
    if n < 1:
        raise ValueError(f"n = {n} no es válido: el número cuántico principal cumple n = 1, 2, 3, …")
    if l < 0 or l >= n:
        raise ValueError(f"l = {l} no es válido para n = {n}: debe cumplirse 0 ≤ l ≤ n − 1 (es decir, 0 ≤ l ≤ {n - 1}).")
    return n, l


def nombre_estado(n: int, l: int) -> str:
    """Notación espectroscópica: (3, 2) → «3d»."""
    return f"{n}{LETRAS[l]}" if l < len(LETRAS) else f"n={n}, l={l}"


def leer_notacion(texto: str) -> tuple[int, int]:
    """Interpreta «3d», «3 d», «3,2» o «n=3, l=2». No valida que el estado exista."""
    t = texto.strip().lower().replace(" ", "")
    m = re.fullmatch(r"(\d+)([a-z])", t)
    if m and m.group(2) in LETRAS:
        return int(m.group(1)), LETRAS.index(m.group(2))
    m = re.fullmatch(r"(?:n=)?(\d+),(?:l=)?(\d+)", t)
    if m:
        return int(m.group(1)), int(m.group(2))
    raise ValueError(f"No se entiende «{texto}». Escribe, por ejemplo, 3d, 2p, «3,2» o «n=3, l=2».")


def funcion_radial(n, l, r):
    """R̃(r) = a₀^(3/2) R_nl(r), con r en unidades de a₀. La normalización se calcula con logaritmos (n grande no desborda)."""
    n, l = validar_estado(n, l)
    r = np.asarray(r, dtype=float)
    rho = 2.0 * r / n
    log_norm = 1.5 * np.log(2.0 / n) + 0.5 * (gammaln(n - l) - np.log(2.0 * n) - gammaln(n + l + 1))
    return np.exp(log_norm) * np.exp(-rho / 2.0) * rho ** l * eval_genlaguerre(n - l - 1, 2 * l + 1, rho)


def distribucion_radial(n, l, r):
    """P(r) = r²|R|² (en unidades de 1/a₀): P(r) dr es la probabilidad de hallar al electrón entre r y r + dr."""
    r = np.asarray(r, dtype=float)
    return r ** 2 * np.abs(funcion_radial(n, l, r)) ** 2


def distancia_esperada(n, l) -> float:
    """⟨r⟩ = (a₀/2)[3n² − l(l+1)] en unidades de a₀."""
    n, l = validar_estado(n, l)
    return 0.5 * (3 * n ** 2 - l * (l + 1))


def energia_estado(n, masa_reducida: bool = False) -> tuple[float, float]:
    """(Eₙ en eV, Eₙ en J). Con masa_reducida se multiplica por μ/mₑ = M/(M + mₑ) (protón de masa finita)."""
    if isinstance(n, bool) or not isinstance(n, numbers.Integral) or n < 1:
        raise ValueError("n debe ser un entero positivo.")
    factor = 1.0 / (1.0 + 1.0 / MP_ME) if masa_reducida else 1.0
    e_ev = -RY * factor / int(n) ** 2
    return e_ev, e_ev * EV_A_J


def nodos_radiales(n, l) -> np.ndarray:
    """Posiciones (en a₀) de los n − l − 1 nodos radiales: r = nρ/2 con ρ los ceros de L^(2l+1)_(n−l−1)."""
    n, l = validar_estado(n, l)
    k = n - l - 1
    if k == 0:
        return np.array([])
    return n * np.sort(roots_genlaguerre(k, 2 * l + 1)[0]) / 2.0


def limite_r(n, l) -> float:
    """Radio máximo del dibujo (en a₀): deja ver toda la cola, que llega a ≈ 2n² + 15n."""
    n, l = validar_estado(n, l)
    return max(40.0, 2.0 * n ** 2 + 15.0 * n + 10.0)


def malla_radial(n, l, puntos: int | None = None) -> np.ndarray:
    r_max = limite_r(n, l)
    if puntos is None:
        puntos = int(min(max(4000, 40 * r_max), 400000))
    return np.linspace(0.0, r_max, puntos)


def radio_mas_probable(n, l) -> float:
    """Radio (en a₀) del máximo global de P(r): búsqueda en malla y refinamiento acotado."""
    n, l = validar_estado(n, l)
    r = np.linspace(0.0, limite_r(n, l), 40001)
    i = int(np.argmax(distribucion_radial(n, l, r)))
    res = minimize_scalar(lambda x: -float(distribucion_radial(n, l, x)), bounds=(r[max(i - 1, 0)], r[min(i + 1, len(r) - 1)]),
                          method="bounded", options={"xatol": 1e-10})
    return float(res.x)


def comprobar_normalizacion(n, l) -> tuple[float, float]:
    """(∫P dr, ∫r P dr) por integración numérica: deben valer 1 y ⟨r⟩."""
    r = malla_radial(n, l)
    P = distribucion_radial(n, l, r)
    return float(_integrar(P, r)), float(_integrar(r * P, r))


ESTADOS_COMPARACION = [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]


# =====================================================================
# 2. FIGURAS
# =====================================================================
def figura_estado(n: int, l: int, compacto: bool = False):
    """R(r) y P(r) en unidades de a₀, con ⟨r⟩ (línea discontinua), el radio más probable y los nodos radiales."""
    r = malla_radial(n, l)
    R, P = funcion_radial(n, l, r), distribucion_radial(n, l, r)
    r_med, r_mp, nodos = distancia_esperada(n, l), radio_mas_probable(n, l), nodos_radiales(n, l)
    nombre = nombre_estado(n, l)
    fig, ejes = qc.rejilla(1, 2, (14.5, 5.2), (7, 8.4), constrained_layout=True) if not compacto else qc.rejilla(
        2, 1, (7, 8.4), (7, 8.4), constrained_layout=True)
    for ax, y, color, titulo, etiqueta in ((ejes[0], R, COLORES["onda"], f"Función radial R({nombre})", "a₀^(3/2) R(r)"),
                                           (ejes[1], P, COLORES["densidad"], f"Distribución radial P({nombre}) = r²R²", "a₀ P(r)")):
        ax.plot(r, y, color=color, lw=2.2)
        ax.axhline(0, color=COLORES["gris"], lw=0.8)
        ax.axvline(r_med, color=COLORES["energia"], ls="--", lw=1.8, label=f"⟨r⟩ = {r_med:.3f} a₀")
        if ax is ejes[1]:
            ax.axvline(r_mp, color=COLORES["interferencia"], ls=":", lw=1.8, label=f"máximo de P: {r_mp:.3f} a₀")
        if len(nodos):
            ax.plot(nodos, np.zeros_like(nodos), "o", color=COLORES["texto"], ms=6, zorder=5, label=f"nodos radiales ({len(nodos)})")
        ax.set_title(titulo)
        ax.set_xlabel("r / a₀")
        ax.set_ylabel(etiqueta)
        ax.grid(alpha=0.25)
        ax.legend(loc="upper right")
    return fig


def figura_comparacion():
    """r²R² frente a r/a₀ para 1s, 2s, 2p, 3s, 3p y 3d (la figura de las diapositivas), con el máximo de cada una."""
    fig, ax = qc.rejilla(1, 1, (11, 5.2), (7, 5), constrained_layout=True)
    r = np.linspace(0, 25, 5001)
    serie = [COLORES["onda"], COLORES["densidad"], COLORES["energia"], COLORES["cinetica"], COLORES["potencial"], COLORES["interferencia"]]
    for (n, l), color in zip(ESTADOS_COMPARACION, serie):
        ax.plot(r, distribucion_radial(n, l, r), lw=2, color=color, label=nombre_estado(n, l))
        rm = radio_mas_probable(n, l)
        ax.plot(rm, float(distribucion_radial(n, l, rm)), "o", color=color)
    ax.set_xlabel("r / a₀")
    ax.set_ylabel("a₀ P(r) = a₀ r² R²")
    ax.set_title("Distribución radial de los primeros orbitales del hidrógeno")
    ax.grid(alpha=0.25)
    ax.legend()
    return fig


def figura_niveles(n: int, masa_reducida: bool):
    """Niveles de energía del hidrógeno con el nivel elegido resaltado (solo se rotulan n = 1–4 y el elegido)."""
    fig, ax = qc.rejilla(1, 1, (5.2, 5.2), (5.2, 5), constrained_layout=True)
    for k in range(1, max(9, n + 1)):
        e = energia_estado(k, masa_reducida)[0]
        actual = k == n
        ax.hlines(e, 0, 1, color=COLORES["energia"] if actual else COLORES["gris"], lw=3.2 if actual else 1.4)
        if actual or k <= 4:
            ax.text(1.04, e, f"n = {k}  ({e:.4f} eV)", va="center", fontsize=9,
                    color=COLORES["energia"] if actual else COLORES["gris"], fontweight="bold" if actual else "normal")
    ax.axhline(0, color=COLORES["texto"], lw=1, ls="--")
    ax.text(1.04, 0.0, "E = 0 (ionización)", va="bottom", fontsize=9, color=COLORES["texto"])
    ax.set_xlim(0, 2.4)
    ax.set_ylim(energia_estado(1, masa_reducida)[0] * 1.08, 1.2)
    ax.set_xticks([])
    ax.set_xlabel("los niveles n ≥ 5 se juntan hacia E = 0", fontsize=8)
    ax.set_ylabel("E [eV]")
    ax.set_title("Niveles de energía")
    return fig


# =====================================================================
# 3. PRUEBAS
# =====================================================================
def ejecutar_pruebas() -> qc.RegistroPruebas:
    r = qc.RegistroPruebas("Hidrógeno · función radial")
    r1 = np.linspace(0, 30, 3001)
    r.comprobar("R₁₀ = 2e^(−r)", np.allclose(funcion_radial(1, 0, r1), 2 * np.exp(-r1), rtol=1e-12))
    r.comprobar("R₂₀ = (2−r)e^(−r/2)/(2√2)",
                np.allclose(funcion_radial(2, 0, r1), (2 - r1) * np.exp(-r1 / 2) / (2 * np.sqrt(2)), rtol=1e-10, atol=1e-14))
    r.comprobar("R₂₁ = r e^(−r/2)/(2√6)",
                np.allclose(funcion_radial(2, 1, r1), r1 * np.exp(-r1 / 2) / (2 * np.sqrt(6)), rtol=1e-10, atol=1e-14))
    for n, l in ((1, 0), (2, 1), (3, 2), (5, 3), (10, 4), (20, 0), (30, 29)):
        norma, _ = comprobar_normalizacion(n, l)
        r.comprobar(f"Normalización ∫P dr = 1 ({nombre_estado(n, l)})", abs(norma - 1) < 1e-5, f"{norma:.8f}")
    rr = np.linspace(0, 120, 240001)
    cruz = _integrar(funcion_radial(1, 0, rr) * funcion_radial(2, 0, rr) * rr ** 2, rr)
    r.comprobar("Ortogonalidad ∫R₁₀R₂₀ r²dr = 0", abs(cruz) < 1e-7, f"{cruz:.1e}")
    for n, l in ((1, 0), (2, 1), (3, 0), (4, 3), (6, 2)):
        _, r_num = comprobar_normalizacion(n, l)
        r.comprobar(f"⟨r⟩ numérico = fórmula ({nombre_estado(n, l)})", abs(r_num - distancia_esperada(n, l)) < 1e-4,
                    f"{r_num:.5f} frente a {distancia_esperada(n, l):.5f}")
    r.comprobar("⟨r⟩: 1s = 3/2, 2s = 6, 2p = 5, 3d = 10.5 (a₀)",
                [distancia_esperada(1, 0), distancia_esperada(2, 0), distancia_esperada(2, 1), distancia_esperada(3, 2)] == [1.5, 6, 5, 10.5])
    r.comprobar("Radio más probable: 1s → a₀, 2p → 4a₀, 3d → 9a₀ (n² para l = n−1)",
                abs(radio_mas_probable(1, 0) - 1) < 1e-6 and abs(radio_mas_probable(2, 1) - 4) < 1e-6 and abs(radio_mas_probable(3, 2) - 9) < 1e-6)
    r.comprobar("Radio más probable de 2s = (3+√5) a₀ ≈ 5.2361", abs(radio_mas_probable(2, 0) - (3 + np.sqrt(5))) < 1e-5)
    r.comprobar("Número de nodos radiales n−l−1", all(len(nodos_radiales(n, l)) == n - l - 1 for n in range(1, 9) for l in range(n)))
    r.comprobar("Nodo de 2s en r = 2a₀", np.allclose(nodos_radiales(2, 0), [2.0]))
    r.comprobar("Nodos de 3s: (3 ± √3)·3/2 a₀ (ejemplo de la clase)",
                np.allclose(nodos_radiales(3, 0), [(3 - np.sqrt(3)) * 1.5, (3 + np.sqrt(3)) * 1.5]))
    r.comprobar("R se anula en los nodos (4s, 5p, 6d)",
                all(np.max(np.abs(funcion_radial(n, l, nodos_radiales(n, l)))) < 1e-9 for n, l in ((4, 0), (5, 1), (6, 2))))
    e1 = energia_estado(1)[0]
    r.comprobar("E₁ = −13.605693 eV", abs(e1 + 13.605693009) < 1e-9, f"{e1:.9f} eV")
    r.comprobar("Eₙ = E₁/n² (n = 2, 3, 7)", all(abs(energia_estado(n)[0] - e1 / n ** 2) < 1e-12 for n in (2, 3, 7)))
    r.comprobar("E₁ = −2.179872×10⁻¹⁸ J", abs(energia_estado(1)[1] / 1e-18 + 2.179872) < 1e-6)
    r.comprobar("Masa reducida: E₁ = −13.5983 eV", abs(energia_estado(1, True)[0] + 13.5983) < 1e-3)
    try:                                                      # contraste con la implementación del simulador 05
        import modelo_bohr
        r_ = np.linspace(0.01, 40, 800)
        ok = all(np.allclose(funcion_radial(n, l, r_), modelo_bohr.radial_hidrogeno(r_ * modelo_bohr.A0, n, l) * modelo_bohr.A0 ** 1.5,
                             rtol=1e-9, atol=1e-14) for n, l in ((1, 0), (3, 1), (5, 2)))
        r.comprobar("Contraste con modelo_bohr.radial_hidrogeno (1s, 3p, 5d)", ok)
    except Exception as error:                                # pragma: no cover
        r.comprobar("Contraste con modelo_bohr", False, repr(error))
    r.comprobar_error("Rechaza l ≥ n", validar_estado, 2, 2)
    r.comprobar_error("Rechaza n = 0", validar_estado, 0, 0)
    r.comprobar_error("Rechaza l negativo", validar_estado, 3, -1)
    r.comprobar_error("Rechaza n no entero", validar_estado, 2.5, 1, tipo=TypeError)
    r.comprobar_error("Rechaza l booleano", validar_estado, 2, True, tipo=TypeError)
    r.comprobar("Acepta enteros de NumPy", validar_estado(np.int64(3), np.int32(2)) == (3, 2))
    r.comprobar("Lee «3d», «4 f» y «n=3, l=2»", leer_notacion("3d") == (3, 2) and leer_notacion("4 f") == (4, 3) and leer_notacion("n=3, l=2") == (3, 2))
    return r


# =====================================================================
# 4. INTERFAZ STREAMLIT
# =====================================================================
VALORES_INICIALES = {"rad_n": 3, "rad_l": 1, "rad_mred": False}
DEMOS = {
    "1s: estado fundamental": {"rad_n": 1, "rad_l": 0},
    "2s frente a 2p (mismo n)": {"rad_n": 2, "rad_l": 0},
    "3d: sin nodos radiales": {"rad_n": 3, "rad_l": 2},
    "Orbital «circular» 4f (l = n − 1)": {"rad_n": 4, "rad_l": 3},
    "Estado de Rydberg n = 20": {"rad_n": 20, "rad_l": 2},
}

GUIA = [
    {"titulo": "El radio de Bohr es el radio más probable de 1s",
     "objetivo": "Comprobar que el máximo de P(r) del estado fundamental está en a₀ aunque ⟨r⟩ = 1.5 a₀.",
     "pasos": ["Cargar la configuración (1s).", "Leer el radio más probable y ⟨r⟩ en los resultados.",
               "En la gráfica de P(r) ver la diferencia entre la línea roja (⟨r⟩) y el máximo."],
     "pregunta": "¿Por qué ⟨r⟩ es mayor que el radio más probable?",
     "resultado": "El máximo de P está en a₀ (el radio que calculó Bohr), pero P(r) tiene una cola larga hacia fuera: promediar sobre ella desplaza "
                  "⟨r⟩ a 3a₀/2.",
     "pestana": "Resultados y gráficas", "config": {"rad_n": 1, "rad_l": 0}},
    {"titulo": "Nodos radiales: n − l − 1",
     "objetivo": "Contar los nodos de R(r) y relacionarlos con los números cuánticos.",
     "pasos": ["Cargar 3s y contar los puntos negros de la gráfica.", "Repetir con 3p y con 3d.", "Comparar con la tabla de nodos."],
     "pregunta": "¿Cuántos nodos radiales tienen 3s, 3p y 3d? ¿Dónde están los de 3s?",
     "resultado": "3s tiene 2, 3p tiene 1 y 3d ninguno. Los nodos de 3s están en r = (3 ± √3)·3a₀/2 ≈ 1.90 a₀ y 7.10 a₀ (los ceros de 6 − 6ρ + ρ² con ρ = 2r/3a₀).",
     "pestana": "Resultados y gráficas", "config": {"rad_n": 3, "rad_l": 0}},
    {"titulo": "A igual n, la energía no cambia con l",
     "objetivo": "Ver que la energía depende solo de n mientras la forma de la distribución cambia mucho.",
     "pasos": ["Abrir «Comparación de orbitales».", "Mirar la tabla: 2s y 2p, y 3s, 3p, 3d.", "Cambiar l en los parámetros y observar la energía."],
     "pregunta": "¿Qué estados tienen la misma energía que 2s? ¿Cuántos orbitales hay en el nivel n = 3?",
     "resultado": "2p (y sus tres orientaciones). El nivel n tiene n² orbitales: 9 para n = 3 (1 + 3 + 5). La degeneración en l es propia del potencial de Coulomb.",
     "pestana": "Comparación de orbitales", "config": {"rad_n": 2, "rad_l": 1}},
    {"titulo": "Orbitales «circulares» (l = n − 1)",
     "objetivo": "Comprobar que para l = n − 1 el máximo está en n² a₀.",
     "pasos": ["Cargar 4f.", "Leer el radio más probable.", "Probar 2p y 3d."],
     "pregunta": "¿Dónde está el máximo de 2p, 3d y 4f?",
     "resultado": "En 4, 9 y 16 a₀ respectivamente: n² a₀, como las órbitas de Bohr. Estos estados no tienen nodos radiales.",
     "pestana": "Resultados y gráficas", "config": {"rad_n": 4, "rad_l": 3}},
]

PREGUNTAS = [
    {"enunciado": "La función de distribución radial P(r) es…",
     "opciones": ["|R(r)|²", "r²|R(r)|²", "r|R(r)|", "R(r)/r²"], "correcta": 1,
     "explicacion": "P(r) = r²R², porque el volumen de la corona esférica entre r y r + dr es 4πr² dr; P(r) dr es la probabilidad de hallar el electrón entre ambas esferas."},
    {"enunciado": "El estado 3p del hidrógeno tiene…",
     "opciones": ["0 nodos radiales", "1 nodo radial", "2 nodos radiales", "3 nodos radiales"], "correcta": 1,
     "explicacion": "Nodos radiales = n − l − 1 = 3 − 1 − 1 = 1."},
    {"enunciado": "El radio más probable del estado 1s es…",
     "opciones": ["a₀/2", "a₀", "3a₀/2", "2a₀"], "correcta": 1,
     "explicacion": "El máximo de P(r) = 4r²e^(−2r/a₀)/a₀³ está en a₀; 3a₀/2 es la distancia esperada ⟨r⟩."},
    {"enunciado": "La energía del hidrógeno en el nivel n = 3 es…",
     "opciones": ["−13.6 eV", "−4.53 eV", "−1.51 eV", "−0.85 eV"], "correcta": 2,
     "explicacion": "E₃ = −13.6057 eV / 9 ≈ −1.512 eV. La energía depende solo de n."},
    {"enunciado": "¿Cuántos orbitales tiene el nivel n = 3?",
     "opciones": ["3", "6", "9", "18"], "correcta": 2,
     "explicacion": "n² = 9: un 3s, tres 3p y cinco 3d (sin contar el espín)."},
    {"enunciado": "Cerca del núcleo, R_nl(r) se comporta como…",
     "opciones": ["constante para todo l", "r^l", "e^(−r)", "1/r"], "correcta": 1,
     "explicacion": "La barrera centrífuga l(l+1)ħ²/2μr² impide acercarse al núcleo: solo los estados s (l = 0) son distintos de cero en r = 0."},
    {"enunciado": "Si l = n − 1, el máximo de P(r) está en…",
     "opciones": ["a₀", "n a₀", "n² a₀", "2n a₀"], "correcta": 2,
     "explicacion": "Para l = n − 1 no hay nodos radiales y P ∝ r^(2n) e^(−2r/n a₀), cuyo máximo está en n² a₀ (los radios de Bohr)."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("rad_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


def _leer_parametros():
    ss = st.session_state
    with st.container(border=True):
        qc.seccion("Estado del electrón")
        c1, c2, c3 = st.columns(3, vertical_alignment="bottom")
        n = c1.number_input("Número cuántico principal n", min_value=1, max_value=N_MAX, step=1, key="rad_n",
                            help="Fija la energía y el número de nodos totales (n − 1).")
        ss["rad_l"] = int(min(max(ss["rad_l"], 0), int(n) - 1))          # l ≤ n − 1: se ajusta si se baja n
        l = c2.number_input("Número cuántico orbital l", min_value=0, max_value=int(n) - 1, step=1, key="rad_l",
                            help="0 = s, 1 = p, 2 = d, 3 = f…")
        c3.toggle("Masa reducida del protón", key="rad_mred",
                  help="Corrige solo la energía por la masa finita del núcleo; las gráficas siguen en unidades de a₀.")
        qc.pie_de_parametros(DEMOS, "rad_demo", _aplicar_demo, VALORES_INICIALES, "rad_reset")
    try:
        return validar_estado(n, l)
    except (TypeError, ValueError) as error:
        qc.error(error)
        return None


@st.cache_data(show_spinner=False, max_entries=24)
def _cache_estado(n: int, l: int, compacto: bool):
    return figura_estado(n, l, compacto)


@st.cache_data(show_spinner=False)
def _cache_comparacion():
    return figura_comparacion()


def _pestana_estado(n: int, l: int, masa_reducida: bool):
    nombre = nombre_estado(n, l)
    e_ev, e_j = energia_estado(n, masa_reducida)
    r_med, r_mp, nodos = distancia_esperada(n, l), radio_mas_probable(n, l), nodos_radiales(n, l)
    norma, r_num = comprobar_normalizacion(n, l)
    qc.seccion(f"Resultados · estado {nombre}")
    qc.metricas([
        ("Energía Eₙ [eV]", f"{e_ev:.8f}", "Eₙ = −R/n². Depende solo de n"),
        ("Energía Eₙ [J]", f"{e_j:.6e}"),
        ("⟨r⟩ [a₀]", f"{r_med:.5f}", "⟨r⟩ = (a₀/2)[3n² − l(l+1)]"),
        ("⟨r⟩ [m]", f"{r_med * A0:.5e}"),
        ("Radio más probable [a₀]", f"{r_mp:.5f}", "Máximo de P(r)"),
        ("Nodos radiales", f"{len(nodos)}", "n − l − 1"),
        ("Nodos angulares", f"{l}", "l"),
        ("Degeneración del nivel", f"{n ** 2}", "n² orbitales (sin espín)"),
    ])
    if n > 40:
        qc.aviso("Con n grande el estado es de Rydberg: la distribución es casi clásica y el dibujo muy ancho; el cálculo sigue siendo exacto.")
    if masa_reducida:
        qc.nota("La energía incluye la corrección de masa reducida. Las gráficas siguen en unidades del radio de Bohr de núcleo infinitamente pesado.")
    qc.seccion("Función radial y distribución radial")
    qc.mostrar_pyplot(_cache_estado(n, l, qc.modo_compacto()), archivo=f"hidrogeno_radial_{nombre}.png")
    r = malla_radial(n, l)
    qc.exportar_datos({"r [a0]": r, "R [a0^-3/2]": funcion_radial(n, l, r), "P [1/a0]": distribucion_radial(n, l, r)},
                      f"hidrogeno_radial_{nombre}.csv")
    if len(nodos):
        qc.seccion("Nodos radiales")
        qc.tabla([(str(i + 1), f"{x:.6f}", f"{2 * x / n:.6f}") for i, x in enumerate(nodos)],
                 encabezados=("Nodo", "r [a₀]", "ρ = 2r/(n a₀)"))
    qc.seccion("Comprobaciones numéricas")
    qc.tabla([("∫₀^∞ P(r) dr", f"{norma:.8f}", "debe ser 1"), ("⟨r⟩ por integración ∫ r P dr", f"{r_num:.6f}", "a₀"),
              ("⟨r⟩ por la fórmula", f"{r_med:.6f}", "a₀")])
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- R(r) ∼ r^l cerca del núcleo: solo los estados s son distintos de cero en r = 0, pero P(r) = r²R² se anula en r = 0 para todos.\n"
            "- El máximo de P no coincide con ⟨r⟩: la cola exterior larga desplaza el promedio hacia fuera.\n"
            f"- El estado {nombre} tiene {len(nodos)} nodo(s) radial(es) y {l} angular(es): n − 1 = {n - 1} en total.\n"
            "- La energía solo depende de n: el nivel es n²-degenerado.")
    c1, _ = st.columns([1, 1])
    with c1:
        qc.mostrar_pyplot(figura_niveles(n, masa_reducida), archivo="hidrogeno_niveles.png")


def _pestana_comparacion():
    qc.seccion("Distribución radial de 1s, 2s, 2p, 3s, 3p y 3d")
    qc.mostrar_pyplot(_cache_comparacion(), archivo="hidrogeno_comparacion.png")
    qc.tabla_libre([{"Estado": nombre_estado(n, l), "Nodos radiales": n - l - 1, "r más probable [a₀]": f"{radio_mas_probable(n, l):.4f}",
                     "⟨r⟩ [a₀]": f"{distancia_esperada(n, l):.3f}", "E [eV]": f"{energia_estado(n)[0]:.4f}"}
                    for n, l in ESTADOS_COMPARACION], numericas=("Nodos radiales", "r más probable [a₀]", "⟨r⟩ [a₀]", "E [eV]"))
    st.caption("Al crecer n el electrón se aleja del núcleo y aparecen más nodos radiales; a igual n, el estado con menor l penetra más cerca "
               "del núcleo (3s tiene un máximo interno), aunque en el hidrógeno todos tienen la misma energía.")


def interfaz() -> None:
    """Página completa del simulador 7 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 07", "Átomo de hidrógeno: función radial",
                         "Función radial R(r), distribución radial P(r) = r²R², distancia esperada, nodos y energía de cualquier estado (n, l).")
    qc.enlace_teoria("hidrogeno")
    qc.ficha_simulador(
        "Dibujar R(r) y la distribución radial en unidades de a₀ para un estado (n, l), mostrar ⟨r⟩ y calcular la energía.",
        r"\begin{gathered}P(r)=r^2\,|R_{nl}(r)|^2\\[4pt]\langle r\rangle=\dfrac{a_0}{2}\left[3n^2-l(l+1)\right],\quad E_n=-\dfrac{R_\infty}{n^2}\end{gathered}",
        [("n, l", "números cuánticos principal y orbital"), ("R(r)", "función radial"), ("P(r)", "distribución radial"),
         ("a₀", "radio de Bohr")],
        "Átomo hidrogenoide de un electrón (Z = 1), sin espín; núcleo de masa infinita salvo en la opción de masa reducida (solo energía).")
    estado = _leer_parametros()
    if estado is None:
        return
    n, l = estado
    tabs = st.tabs(["Resultados y gráficas", "Comparación de orbitales", "Guía de práctica", "Autoevaluación", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_estado(n, l, bool(st.session_state["rad_mred"]))
    with tabs[1]:
        _pestana_comparacion()
    with tabs[2]:
        qc.guia_practica(GUIA, "rad")
    with tabs[3]:
        qc.autoevaluacion(PREGUNTAS, "rad")
    with tabs[4]:
        qc.boton_pruebas(ejecutar_pruebas, "rad_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Hidrógeno radial", ":material/science:", "hidrogeno_radial.py")
