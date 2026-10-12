"""
oscilador_armonico.py — QUANTUM LAB · Simulador 2: oscilador armónico cuántico 1D
==================================================================================

Modelo:   V(x) = ½ m ω² x²           E_n = ħω (n + ½),  n = 0, 1, 2, …

Longitud característica:   x₀ = √(ħ/(mω))

Estados estacionarios (polinomios de Hermite de los físicos):

    ψ_n(x) = 1/√(2ⁿ n!) · 1/(π^{1/4} √x₀) · H_n(x/x₀) · exp[−x²/(2x₀²)]

Densidades de energía (para un estado estacionario real):

    u_V(x) = V(x)·|ψ_n(x)|²                   [energía / longitud]
    u_T(x) = (ħ²/2m)·|dψ_n/dx|²              [energía / longitud]
    E_n    = ∫ (u_T + u_V) dx

IMPORTANTE (distinción pedida en el enunciado):
  * V(x) es la energía potencial *por unidad de probabilidad* (se mide en
    energía): es el valor que tomaría la energía potencial si la partícula
    estuviese en x.
  * u_V(x) = V(x)|ψ|² es una *densidad de energía* (energía por unidad de
    longitud): pondera V(x) con la probabilidad de estar en x. Su integral
    es ⟨V⟩.
  u_T y u_V son las densidades espaciales de las contribuciones de los términos
  cinético y potencial del hamiltoniano; NO son la única definición posible de
  una densidad local de energía cuántica (p. ej. −(ħ²/2m)ψψ'' integra a lo
  mismo pero puede ser negativa localmente).

Estructura del archivo
    1. Física pura (no dibuja ni usa Streamlit para calcular)
    2. Figuras (Matplotlib y Plotly)
    3. Pruebas numéricas
    4. Interfaz Streamlit
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import streamlit as st
from scipy.special import eval_hermite, gammaln, erfc

import quantum_lab_comun as qc
from quantum_lab_comun import HBAR, M_E, E_CARGA, E_HARTREE, A0, COLORES

# =====================================================================
# 1. FÍSICA
# =====================================================================
N_MAX = 100                     # para n mayores H_n pierde precisión en el dominio usual
RANGO_MIN, RANGO_MAX = 3.0, 60.0  # semiancho del dominio, en múltiplos de x₀
RES_MIN, RES_MAX = 201, 20001
PUNTOS_POR_LONGITUD_ONDA = 8    # mínimo de puntos por longitud de onda local
METODOS_DERIVADA = {"numerica": "Numérica (diferencias centrales, orden 2)",
                    "analitica": "Analítica (recurrencia de Hermite)"}


@dataclass(frozen=True)
class ParametrosOscilador:
    """Parámetros ya validados y convertidos a SI."""
    n: int
    masa: float          # kg
    omega: float         # rad/s
    sistema: str
    rango: float         # semiancho del dominio en múltiplos de x₀
    resolucion: int
    metodo: str          # "numerica" | "analitica"


def validar_parametros_oscilador(n, masa_usuario, omega_usuario, sistema, rango, resolucion,
                                 metodo="numerica") -> ParametrosOscilador:
    """
    Valida los datos de la interfaz y los convierte a SI.

    masa en unidades de mₑ; ω en rad/s (modo SI) o en Eₕ/ħ (modo atómico);
    rango en múltiplos de x₀. Lanza ValueError con un mensaje comprensible.
    """
    n = qc.entero_en_rango(n, "El número cuántico n", 0, N_MAX)
    unidades = qc.obtener_unidades(sistema)
    masa = qc.positivo_finito(masa_usuario, "La masa m") * M_E
    omega = qc.positivo_finito(omega_usuario, "La frecuencia angular ω") * unidades["factor_omega"]
    rango = qc.positivo_finito(rango, "El intervalo espacial")
    if not (RANGO_MIN <= rango <= RANGO_MAX):
        raise ValueError(f"El intervalo espacial debe estar entre {RANGO_MIN:g} x₀ y {RANGO_MAX:g} x₀.")
    resolucion = qc.entero_en_rango(resolucion, "La resolución", RES_MIN, RES_MAX)
    if metodo not in METODOS_DERIVADA:
        raise ValueError("El método de derivación debe ser 'numerica' o 'analitica'.")
    # Puntos por longitud de onda local mínima λ ≈ 2π x₀/√(2n+1)
    puntos_por_lambda = (2 * np.pi / np.sqrt(2 * n + 1)) * (resolucion - 1) / (2 * rango)
    if puntos_por_lambda < PUNTOS_POR_LONGITUD_ONDA:
        raise ValueError(
            f"Resolución insuficiente para n = {n}: solo {puntos_por_lambda:.1f} puntos por longitud de onda "
            f"(mínimo {PUNTOS_POR_LONGITUD_ONDA}). Aumenta la resolución o reduce el intervalo.")
    return ParametrosOscilador(n, masa, omega, sistema, rango, resolucion, metodo)


def longitud_caracteristica(masa: float, omega: float) -> float:
    """x₀ = √(ħ/(mω))   [m]."""
    return float(np.sqrt(HBAR / (masa * omega)))


def malla_xi(rango: float, resolucion: int) -> np.ndarray:
    """
    Malla simétrica de ξ = x/x₀ en [−rango, +rango] con un número IMPAR de
    puntos (así x = 0 pertenece a la malla y los nodos de los estados impares
    caen sobre un punto exacto).
    """
    resolucion = int(resolucion)
    if resolucion % 2 == 0:
        resolucion += 1
    return np.linspace(-rango, rango, resolucion)


def potencial_armonico(x, masa: float, omega: float):
    """V(x) = ½ m ω² x²   [J]  (energía potencial por unidad de probabilidad)."""
    return 0.5 * masa * omega ** 2 * np.asarray(x) ** 2


def energia_teorica(n: int, omega: float) -> float:
    """E_n = ħω(n + ½)   [J]."""
    return HBAR * omega * (n + 0.5)


def psi_oscilador(x, n: int, masa: float, omega: float):
    """
    ψ_n(x) normalizada   [m^(-1/2)].

    Estabilidad numérica: el prefactor 1/√(2ⁿ n!) se calcula con logaritmos
    (gammaln) y los polinomios de Hermite con scipy.special.eval_hermite
    (recurrencia estable). 2ⁿ·n! desbordaría con factoriales enteros.
    """
    n = int(n)
    if n < 0:
        raise ValueError("El número cuántico n debe ser no negativo.")
    x0 = longitud_caracteristica(masa, omega)
    xi = np.asarray(x, dtype=float) / x0
    prefactor = np.exp(-0.5 * (n * np.log(2.0) + gammaln(n + 1.0)))
    return prefactor * np.pi ** -0.25 * x0 ** -0.5 * eval_hermite(n, xi) * np.exp(-xi ** 2 / 2.0)


def derivada_numerica(x, psi):
    """
    dψ/dx por diferencias centrales de orden 2 (también en los bordes, con
    np.gradient(edge_order=2)). Error de truncamiento ≈ (Δx²/6)·ψ‴ = O(Δx²).
    """
    return np.gradient(psi, x, edge_order=2)


def derivada_analitica(x, n: int, masa: float, omega: float):
    """
    dψ_n/dx = (1/x₀)·[√(n/2) ψ_{n−1} − √((n+1)/2) ψ_{n+1}]   (recurrencia exacta).
    No tiene error de discretización (solo el redondeo y el truncamiento del dominio).
    """
    x0 = longitud_caracteristica(masa, omega)
    psi_mas = psi_oscilador(x, n + 1, masa, omega)
    psi_menos = psi_oscilador(x, n - 1, masa, omega) if n > 0 else 0.0 * psi_mas
    return (np.sqrt(n / 2.0) * psi_menos - np.sqrt((n + 1) / 2.0) * psi_mas) / x0


def integrar(x, y) -> float:
    """Regla del trapecio (compatible con NumPy antiguo y moderno)."""
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def densidad_energia_potencial(x, psi, masa: float, omega: float):
    """u_V(x) = V(x)|ψ|²   [J/m]."""
    return potencial_armonico(x, masa, omega) * np.abs(psi) ** 2


def densidad_energia_cinetica(dpsi, masa: float):
    """u_T(x) = (ħ²/2m)|dψ/dx|²   [J/m]."""
    return (HBAR ** 2 / (2.0 * masa)) * np.abs(dpsi) ** 2


def normalizacion(x, psi) -> float:
    """∫|ψ|² dx."""
    return integrar(x, np.abs(psi) ** 2)


def valores_esperados(x, psi) -> tuple[float, float]:
    """⟨x⟩ y ⟨x²⟩ para ψ real normalizada."""
    rho = np.abs(psi) ** 2
    return integrar(x, x * rho), integrar(x, x ** 2 * rho)


def nodos_oscilador(x, psi) -> np.ndarray:
    """
    Nodos = cruces por cero de ψ (cambios de SIGNO), localizados por
    interpolación lineal. Si una muestra vale exactamente 0 (x = 0 en estados
    impares) se toma esa posición. (Mirar |ψ|² no sirve: nunca es negativa.)
    """
    signo = np.sign(psi)
    indices = np.flatnonzero(signo != 0)
    s = signo[indices]
    nodos = []
    for c in np.flatnonzero(s[:-1] * s[1:] < 0):
        i, j = indices[c], indices[c + 1]
        if j - i == 1:
            nodos.append(x[i] - psi[i] * (x[j] - x[i]) / (psi[j] - psi[i]))
        else:
            nodos.append(np.mean(x[i + 1:j]))
    return np.array(nodos)


def punto_retorno(n: int, masa: float, omega: float) -> float:
    """Punto de retorno clásico x_n = √(2n+1)·x₀ (donde V = E_n)   [m]."""
    return float(np.sqrt(2 * n + 1) * longitud_caracteristica(masa, omega))


def probabilidad_fuera_retorno(x, rho, x_retorno: float) -> float:
    """
    P(|x| > x_n): probabilidad en la región clásicamente prohibida (efecto túnel).
    El punto de retorno rara vez cae sobre un nodo de la malla: se inserta
    exactamente mediante interpolación lineal para no cometer un error O(Δx)
    por un enmascarado discontinuo.
    """
    x = np.asarray(x, dtype=float)
    rho = np.asarray(rho, dtype=float)
    total = 0.0
    for signo in (+1.0, -1.0):
        xt = signo * x_retorno
        if signo > 0:
            sel = x > xt
            if not sel.any():
                continue
            xs = np.concatenate(([xt], x[sel]))
            rs = np.concatenate(([np.interp(xt, x, rho)], rho[sel]))
        else:
            sel = x < xt
            if not sel.any():
                continue
            xs = np.concatenate((x[sel], [xt]))
            rs = np.concatenate((rho[sel], [np.interp(xt, x, rho)]))
        total += float(integrar(xs, rs))
    return total


def solapamiento(x, psi_a, psi_b) -> float:
    """⟨ψ_a|ψ_b⟩ para funciones reales."""
    return integrar(x, psi_a * psi_b)


def _energia_con_derivada(x, psi, masa, omega, derivada):
    u_T = densidad_energia_cinetica(derivada, masa)
    u_V = densidad_energia_potencial(x, psi, masa, omega)
    return integrar(x, u_T), integrar(x, u_V)


def estudio_convergencia(x, psi, masa: float, omega: float, n: int) -> dict:
    """
    Documenta el error de discretización de la derivada numérica: calcula la
    energía total con la malla completa y con mallas 2× y 4× más gruesas
    (tomando 1 de cada 2 / 4 puntos). Para un método de orden 2 el error debe
    caer ≈ 4 veces al duplicar la resolución (orden observado ≈ 2).
    """
    e_teo = energia_teorica(n, omega)
    filas = []
    for paso in (4, 2, 1):
        xs, ps = x[::paso], psi[::paso]
        if len(xs) < 20:
            continue
        t, v = _energia_con_derivada(xs, ps, masa, omega, derivada_numerica(xs, ps))
        filas.append({"paso": paso, "puntos": len(xs), "error_relativo": abs((t + v) / e_teo - 1.0)})
    ordenes = [float(np.log2(a["error_relativo"] / b["error_relativo"]))
               for a, b in zip(filas[:-1], filas[1:])
               if b["error_relativo"] > 1e-13 and a["error_relativo"] > 1e-13]
    return {"filas": filas, "orden_observado": float(np.mean(ordenes)) if ordenes else float("nan")}


def calcular_estado(p: ParametrosOscilador) -> dict:
    """Todos los datos físicos del estado n (sin dibujar nada)."""
    x0 = longitud_caracteristica(p.masa, p.omega)
    xi = malla_xi(p.rango, p.resolucion)
    x = xi * x0
    psi = psi_oscilador(x, p.n, p.masa, p.omega)
    rho = psi ** 2
    V = potencial_armonico(x, p.masa, p.omega)
    d_num = derivada_numerica(x, psi)
    d_ana = derivada_analitica(x, p.n, p.masa, p.omega)
    dpsi = d_num if p.metodo == "numerica" else d_ana

    u_V = densidad_energia_potencial(x, psi, p.masa, p.omega)
    u_T = densidad_energia_cinetica(dpsi, p.masa)
    e_teo = energia_teorica(p.n, p.omega)
    t_media, v_media = integrar(x, u_T), integrar(x, u_V)
    e_num = t_media + v_media
    t_num, _ = _energia_con_derivada(x, psi, p.masa, p.omega, d_num)
    t_ana, _ = _energia_con_derivada(x, psi, p.masa, p.omega, d_ana)
    x_media, x2_media = valores_esperados(x, psi)
    nodos = nodos_oscilador(x, psi)
    xt = punto_retorno(p.n, p.masa, p.omega)
    norma = normalizacion(x, psi)

    advertencias = []
    if abs(norma - 1.0) > 1e-6:
        advertencias.append(
            f"La normalización difiere de 1 en {abs(norma - 1):.2e}: el intervalo "
            f"(±{p.rango:g} x₀) recorta la función de onda de n = {p.n}, que se extiende hasta "
            f"≈ {np.sqrt(2 * p.n + 1) + 4:.1f} x₀. Aumenta el intervalo.")
    return {
        "x0": x0, "xi": xi, "x": x, "psi": psi, "rho": rho, "V": V, "u_V": u_V, "u_T": u_T,
        "dpsi": dpsi, "e_teo": e_teo, "e_num": e_num, "t_media": t_media, "v_media": v_media,
        "error_relativo": abs(e_num - e_teo) / e_teo,
        "e_num_numerica": t_num + v_media, "e_num_analitica": t_ana + v_media,
        "x_media": x_media, "x2_media": x2_media, "nodos": nodos, "xt": xt, "norma": norma,
        "prob_fuera": probabilidad_fuera_retorno(x, rho, xt),
        "convergencia": estudio_convergencia(x, psi, p.masa, p.omega, p.n),
        "advertencias": advertencias,
    }


# ---------------------------------------------------------------------
# Dinámica: superposición de estados estacionarios
# ---------------------------------------------------------------------
def onda_dependiente_del_tiempo(x, numeros, coeficientes, masa: float, omega: float, tau: float):
    """
    Ψ(x,t) = Σ c_n ψ_n(x) e^{-iE_n t/ħ}  con  τ = ωt  →  fase e^{-i(n+½)τ}.

    Para un solo estado, Ψ = ψ_n e^{-i(n+½)τ}: Re Ψ e Im Ψ oscilan, pero |Ψ|² es
    constante (una fase global no mueve la densidad).
    """
    numeros = np.asarray(numeros, dtype=int)
    coeficientes = np.asarray(coeficientes, dtype=complex)
    psi = np.zeros(np.shape(x), dtype=complex)
    for k, c in zip(numeros, coeficientes):
        psi += c * psi_oscilador(x, int(k), masa, omega) * np.exp(-1j * (int(k) + 0.5) * tau)
    return psi


def coeficientes_dos_estados(peso_segundo: float, fase: float) -> np.ndarray:
    """c₁ = √(1−w), c₂ = √w·e^{iφ}: superposición normalizada de dos estados."""
    if not (0.0 <= peso_segundo <= 1.0):
        raise ValueError("El peso del segundo estado debe estar entre 0 y 1.")
    return np.array([np.sqrt(1.0 - peso_segundo), np.sqrt(peso_segundo) * np.exp(1j * fase)])


def serie_dinamica(p: ParametrosOscilador, numeros, coeficientes, n_cuadros: int, puntos: int = 500):
    """
    Re Ψ, Im Ψ, |Ψ|² y ⟨x⟩ para n_cuadros instantes τ = ωt ∈ [0, 2π) (un periodo
    de la función de onda completa). Devuelve (x, taus, re, im, rho, x_medio).
    """
    x0 = longitud_caracteristica(p.masa, p.omega)
    nmax = int(max(numeros))
    semiancho = min(p.rango, np.sqrt(2 * nmax + 1) + 4.0) * x0
    x = np.linspace(-semiancho, semiancho, puntos)
    taus = np.linspace(0.0, 2 * np.pi, n_cuadros, endpoint=False)
    psi = np.array([onda_dependiente_del_tiempo(x, numeros, coeficientes, p.masa, p.omega, t) for t in taus])
    rho = np.abs(psi) ** 2
    x_medio = np.array([integrar(x, x * r) / integrar(x, r) for r in rho])
    return x, taus, psi.real, psi.imag, rho, x_medio


# =====================================================================
# 2. FIGURAS
# =====================================================================
# ---------------------------------------------------------------------
# Límite clásico (principio de correspondencia)
# ---------------------------------------------------------------------
def amplitud_clasica(n: int, masa: float, omega: float) -> float:
    """Amplitud A del oscilador CLÁSICO con la misma energía: ½mω²A² = ħω(n+½) ⇒ A = √(2n+1)·x₀."""
    return np.sqrt(2 * n + 1) * longitud_caracteristica(masa, omega)


def densidad_clasica(x, amplitud: float):
    """
    Densidad de probabilidad clásica (fracción del periodo que la partícula pasa cerca de x):
        P(x) = 1 / (π √(A² − x²))   para |x| < A,     0 fuera.
    Es integrable aunque diverge en los puntos de retorno ±A.
    """
    x = np.asarray(x, dtype=float)
    dentro = np.abs(x) < amplitud
    p = np.zeros_like(x)
    p[dentro] = 1.0 / (np.pi * np.sqrt(amplitud ** 2 - x[dentro] ** 2))
    return p


def acumulada_clasica(x, amplitud: float):
    """F(x) = ∫_{-∞}^{x} P dx = ½ + arcsin(x/A)/π   (exacta; 0 y 1 fuera de [−A, A])."""
    return 0.5 + np.arcsin(np.clip(np.asarray(x, dtype=float) / amplitud, -1.0, 1.0)) / np.pi


def calcular_limite_clasico(n: int, masa: float, omega: float, puntos: int = 6001) -> dict:
    """
    Compara |ψₙ|² con la densidad clásica de la misma energía. Como P_clásica diverge en los bordes,
    la comparación cuantitativa se hace con las distribuciones ACUMULADAS (distancia de
    Kolmogorov–Smirnov D = max|F_cuántica − F_clásica|), que tiende a 0 cuando n → ∞.
    """
    from scipy.integrate import cumulative_trapezoid
    x0 = longitud_caracteristica(masa, omega)
    A = amplitud_clasica(n, masa, omega)
    semiancho = A + 5.0 * x0
    puntos = max(puntos, int(40 * (2 * n + 1)))          # malla suficiente para las oscilaciones de ψₙ
    x = np.linspace(-semiancho, semiancho, puntos)
    rho = psi_oscilador(x, n, masa, omega) ** 2
    F_q = cumulative_trapezoid(rho, x, initial=0.0)
    F_q = F_q / F_q[-1]
    F_c = acumulada_clasica(x, A)
    return {
        "x": x, "x0": x0, "A": A, "rho": rho, "P_cl": densidad_clasica(x, A), "F_q": F_q, "F_cl": F_c,
        "distancia_ks": float(np.max(np.abs(F_q - F_c))),
        "x2_cuantico": integrar(x, x ** 2 * rho),
        "x2_clasico": A ** 2 / 2.0,                     # ⟨x²⟩ clásico = A²/2 = (n+½)x₀²
        "prob_fuera": probabilidad_fuera_retorno(x, rho, A),
    }


def distancias_ks(n_max: int, masa: float, omega: float) -> tuple[np.ndarray, np.ndarray]:
    """Distancia de Kolmogorov–Smirnov entre la distribución cuántica y la clásica para n = 0…n_max."""
    ns = np.arange(0, n_max + 1)
    return ns, np.array([calcular_limite_clasico(int(n), masa, omega, puntos=3001)["distancia_ks"] for n in ns])


def _et(sistema: str) -> dict:
    u = qc.obtener_unidades(sistema)
    return {"u": u, "fx": u["factor_longitud"], "fe": u["factor_energia"], "L": u["nombre_longitud"],
            "Ltex": u["nombre_longitud_tex"], "E": u["nombre_energia"]}


def _semiancho_visual(p: ParametrosOscilador, n_max: int, x0: float, zoom: bool) -> float:
    """Semiancho del eje x (en m): zoom a la zona física o dominio completo de cálculo."""
    return (min(p.rango, np.sqrt(2 * n_max + 1) + 3.0) if zoom else p.rango) * x0


def figura_estado_individual(d: dict, p: ParametrosOscilador, zoom: bool = True):
    """Seis paneles sincronizados (mismo eje x): ψ, ρ, V+E, u_V, u_T y energía acumulada."""
    import matplotlib.pyplot as plt
    from scipy.integrate import cumulative_trapezoid
    et = _et(p.sistema)
    fx, fe, L, Ltex, U = et["fx"], et["fe"], et["L"], et["Ltex"], et["E"]
    n = p.n
    x_vis = d["x"] / fx
    lim = _semiancho_visual(p, n, d["x0"], zoom) / fx
    e_vis = d["e_teo"] / fe
    hw_vis = HBAR * p.omega / fe

    fig, ejes = qc.rejilla(2, 3, (17.5, 9.2), constrained_layout=True, sharex=True)
    fig.suptitle(f"Oscilador armónico cuántico 1D — estado n = {n}", fontsize=17, fontweight="bold")
    for ax in ejes.flat:
        ax.set_xlim(-lim, lim)
        ax.grid(alpha=0.3)
    for ax in ejes[1]:
        ax.set_xlabel(f"x [{L}]")

    # 1. función de onda
    ax = ejes[0, 0]
    ax.fill_between(x_vis, d["psi"] * np.sqrt(fx), 0, where=d["psi"] >= 0, color=COLORES["onda"], alpha=0.16)
    ax.fill_between(x_vis, d["psi"] * np.sqrt(fx), 0, where=d["psi"] < 0, color=COLORES["energia"], alpha=0.16)
    ax.plot(x_vis, d["psi"] * np.sqrt(fx), color=COLORES["onda"], lw=2.4, label=rf"$\psi_{{{n}}}(x)$")
    ax.axhline(0, color="white", lw=0.8, alpha=0.5)
    ax.set_title("1 · Función de onda")
    ax.set_ylabel(rf"$\psi_n\ [{Ltex}^{{-1/2}}]$")
    ax.legend(loc="upper right")

    # 2. densidad de probabilidad
    ax = ejes[0, 1]
    ax.plot(x_vis, d["rho"] * fx, color=COLORES["densidad"], lw=2.4, label=rf"$|\psi_{{{n}}}|^2$")
    ax.fill_between(x_vis, d["rho"] * fx, color=COLORES["densidad"], alpha=0.12)
    if len(d["nodos"]):
        ax.scatter(d["nodos"] / fx, np.zeros(len(d["nodos"])), color=COLORES["energia"], s=45, zorder=5,
                   label=f"Nodos ({len(d['nodos'])})")
    ax.axvline(-d["xt"] / fx, color=COLORES["gris"], ls=":", lw=1.2)
    ax.axvline(d["xt"] / fx, color=COLORES["gris"], ls=":", lw=1.2, label="Puntos de retorno")
    ax.set_title("2 · Densidad de probabilidad")
    ax.set_ylabel(rf"$|\psi_n|^2\ [{Ltex}^{{-1}}]$")
    ax.legend(loc="upper right")

    # 3. potencial + nivel (V es energía por unidad de probabilidad)
    ax = ejes[0, 2]
    ax.plot(x_vis, d["V"] / fe, color=COLORES["potencial"], lw=2.4, label=r"$V(x)=\frac{1}{2} m\omega^2x^2$")
    ax.axhline(e_vis, color=COLORES["energia"], ls="--", lw=2.2, label=rf"$E_{{{n}}}$")
    ax.fill_between(x_vis, d["V"] / fe, e_vis, where=d["V"] / fe < e_vis, color=COLORES["potencial"], alpha=0.12)
    ax.plot(x_vis, e_vis + 0.9 * hw_vis * d["rho"] / d["rho"].max(), color=COLORES["densidad"], lw=1.3,
            label=r"$|\psi_n|^2$ (escala arbitraria)")
    ax.scatter([-d["xt"] / fx, d["xt"] / fx], [e_vis, e_vis], color=COLORES["energia"], s=40, zorder=5)
    ax.set_ylim(0, e_vis + 1.35 * hw_vis)
    ax.set_title("3 · Potencial V(x) y nivel E_n")
    ax.set_ylabel(f"Energía [{U}]")
    ax.legend(loc="upper center", fontsize=7.5)

    # 4. densidad de energía potencial
    ax = ejes[1, 0]
    ax.plot(x_vis, d["u_V"] * fx / fe, color=COLORES["potencial"], lw=2.4, label=r"$u_V=V\,|\psi|^2$")
    ax.fill_between(x_vis, d["u_V"] * fx / fe, color=COLORES["potencial"], alpha=0.12)
    ax.set_title("4 · Densidad de energía potencial")
    ax.set_ylabel(f"$u_V$ [{U}/{L}]")
    ax.legend(loc="upper right")

    # 5. densidad de energía cinética
    ax = ejes[1, 1]
    ax.plot(x_vis, d["u_T"] * fx / fe, color=COLORES["cinetica"], lw=2.4,
            label=r"$u_T=\frac{\hbar^2}{2m}|\psi'|^2$")
    ax.fill_between(x_vis, d["u_T"] * fx / fe, color=COLORES["cinetica"], alpha=0.12)
    ax.set_title("5 · Densidad de energía cinética")
    ax.set_ylabel(f"$u_T$ [{U}/{L}]")
    ax.legend(loc="upper right")

    # 6. energía total: la integral acumulada converge a ⟨T⟩, ⟨V⟩ y E
    ax = ejes[1, 2]
    acum_t = cumulative_trapezoid(d["u_T"], d["x"], initial=0.0) / fe
    acum_v = cumulative_trapezoid(d["u_V"], d["x"], initial=0.0) / fe
    ax.plot(x_vis, acum_t, color=COLORES["cinetica"], lw=2, label=r"$\int u_T\,dx\ \to\ \langle T\rangle$")
    ax.plot(x_vis, acum_v, color=COLORES["potencial"], lw=2, label=r"$\int u_V\,dx\ \to\ \langle V\rangle$")
    ax.plot(x_vis, acum_t + acum_v, color=COLORES["energia"], lw=2.6, label=r"$\int (u_T+u_V)\,dx\ \to\ E$")
    ax.axhline(e_vis, color=COLORES["onda"], ls="--", lw=1.6, label=rf"$E_{{{n}}}=\hbar\omega(n+\frac{{1}}{{2}})$")
    ax.axhline(e_vis / 2, color=COLORES["gris"], ls=":", lw=1.4, label=r"$E_n/2$ (virial)")
    ax.set_title("6 · Energía total (integral acumulada)")
    ax.set_ylabel(f"Energía [{U}]")
    ax.legend(loc="center left", fontsize=7.5)
    return fig


def figura_niveles_y_escalas(d: dict, p: ParametrosOscilador, zoom: bool = True):
    """
    Izquierda: parábola, niveles energéticos (el seleccionado resaltado) y ψ_n sobre su nivel.
    Derecha: ψ_n y |ψ_n|² en el mismo gráfico pero con EJES DISTINTOS y etiquetados.
    """
    import matplotlib.pyplot as plt
    et = _et(p.sistema)
    fx, fe, L, Ltex, U = et["fx"], et["fe"], et["L"], et["Ltex"], et["E"]
    n, x0 = p.n, d["x0"]
    k_max = max(n + 2, 6)
    hw = HBAR * p.omega / fe
    semi = (np.sqrt(2 * k_max + 1) + 0.8) * x0
    xs = np.linspace(-semi, semi, 800)

    fig, (ax1, ax2) = qc.rejilla(1, 2, (16, 6), constrained_layout=True)
    ax1.plot(xs / fx, potencial_armonico(xs, p.masa, p.omega) / fe, color=COLORES["potencial"], lw=2.6,
             label=r"$V(x)$")
    for k in range(0, k_max + 1):
        ek = energia_teorica(k, p.omega) / fe
        xk = punto_retorno(k, p.masa, p.omega) / fx
        actual = k == n
        ax1.hlines(ek, -xk, xk, color=COLORES["energia"] if actual else COLORES["gris"],
                   lw=3.4 if actual else 1.2, alpha=1.0 if actual else 0.7)
        ax1.text(xk * 1.02, ek, f"n={k}", va="center", fontsize=8.5,
                 color=COLORES["energia"] if actual else COLORES["gris"])
    psi_escala = 0.8 * hw * d["psi"] / np.max(np.abs(d["psi"]))
    ax1.plot(d["x"] / fx, energia_teorica(n, p.omega) / fe + psi_escala, color=COLORES["onda"], lw=1.8,
             label=rf"$\psi_{{{n}}}$ sobre su nivel (escala arbitraria)")
    ax1.set_xlim(-semi / fx, semi / fx)
    ax1.set_ylim(0, (k_max + 0.5) * hw * 1.12)
    ax1.set_title("Potencial parabólico y diagrama de niveles  ($E_n=\\hbar\\omega(n+\\frac{1}{2})$, equiespaciados)")
    ax1.set_xlabel(f"x [{L}]")
    ax1.set_ylabel(f"Energía [{U}]")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="upper center", fontsize=8)

    lim = _semiancho_visual(p, n, x0, zoom) / fx
    ax2.plot(d["x"] / fx, d["psi"] * np.sqrt(fx), color=COLORES["onda"], lw=2.4)
    ax2.axhline(0, color="white", lw=0.7, alpha=0.5)
    ax2.set_ylabel(rf"$\psi_n(x)\ [{Ltex}^{{-1/2}}]$   (eje izquierdo)", color=COLORES["onda"])
    ax2.tick_params(axis="y", colors=COLORES["onda"])
    ax3 = ax2.twinx()
    ax3.plot(d["x"] / fx, d["rho"] * fx, color=COLORES["densidad"], lw=2.4, ls="--")
    ax3.fill_between(d["x"] / fx, d["rho"] * fx, color=COLORES["densidad"], alpha=0.10)
    ax3.set_ylabel(rf"$|\psi_n(x)|^2\ [{Ltex}^{{-1}}]$   (eje derecho)", color=COLORES["densidad"])
    ax3.tick_params(axis="y", colors=COLORES["densidad"])
    ax2.set_xlim(-lim, lim)
    ax2.set_xlabel(f"x [{L}]")
    ax2.set_title("ψ y |ψ|² juntas, con escalas DIFERENTES (cada curva usa su propio eje)")
    ax2.grid(alpha=0.3)
    return fig


def figura_comparacion(datos: list[dict], p: ParametrosOscilador, modo_fundamental: bool = False):
    """
    Comparación de varios estados. `datos` = lista de dicts con n, x, psi, rho, xt.
    En `modo_fundamental` se muestran los puntos de retorno del fundamental y del excitado.
    """
    import matplotlib.pyplot as plt
    et = _et(p.sistema)
    fx, L, Ltex = et["fx"], et["L"], et["Ltex"]
    colores = [COLORES["onda"], COLORES["densidad"], COLORES["cinetica"], COLORES["energia"],
               COLORES["potencial"], COLORES["interferencia"], COLORES["gris"], "#FFFFFF"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.5, 8.6), constrained_layout=True, sharex=True)
    nmax = max(dd["n"] for dd in datos)
    for i, dd in enumerate(datos):
        c = colores[i % len(colores)]
        etiqueta = f"n = {dd['n']}" + (" (fundamental)" if dd["n"] == 0 else "")
        ax1.plot(dd["x"] / fx, dd["psi"] * np.sqrt(fx), color=c, lw=2.2, label=etiqueta)
        ax2.plot(dd["x"] / fx, dd["rho"] * fx, color=c, lw=2.2, label=etiqueta)
        if modo_fundamental:
            for ax in (ax1, ax2):
                ax.axvline(dd["xt"] / fx, color=c, ls=":", lw=1.1, alpha=0.8)
                ax.axvline(-dd["xt"] / fx, color=c, ls=":", lw=1.1, alpha=0.8)
    ax1.axhline(0, color="white", lw=0.7, alpha=0.4)
    ax1.set_title("Función de onda" + (" — líneas punteadas: puntos de retorno clásicos" if modo_fundamental else ""))
    ax1.set_ylabel(rf"$\psi_n\ [{Ltex}^{{-1/2}}]$")
    ax2.set_title("Densidad de probabilidad")
    ax2.set_ylabel(rf"$|\psi_n|^2\ [{Ltex}^{{-1}}]$")
    ax2.set_xlabel(f"x [{L}]")
    lim = min(p.rango, np.sqrt(2 * nmax + 1) + 3.0) * datos[0]["x0"] / fx
    for ax in (ax1, ax2):
        ax.set_xlim(-lim, lim)
        ax.grid(alpha=0.3)
        ax.legend(loc="upper right", ncol=2)
    return fig


def figura_limite_clasico(d: dict, n: int, sistema: str, ns=None, ks=None):
    """|ψₙ|² frente a la densidad clásica, sus distribuciones acumuladas y la distancia KS en función de n."""
    et = _et(sistema)
    fx, L = et["fx"], et["L"]
    paneles = 3 if ns is not None else 2
    fig, ejes = qc.rejilla(1, paneles, (17.5 if paneles == 3 else 13, 5.2), constrained_layout=True)
    x = d["x"] / fx
    A = d["A"] / fx
    ax = ejes[0]
    ax.fill_between(x, d["rho"] * fx, color=COLORES["densidad"], alpha=0.25)
    ax.plot(x, d["rho"] * fx, color=COLORES["densidad"], lw=1.8, label=rf"cuántica $|\psi_{{{n}}}|^2$")
    tope = 1.35 * np.max(d["rho"] * fx)
    ax.plot(x, np.minimum(d["P_cl"] * fx, tope * 0.98), color="white", ls="--", lw=1.8,
            label=r"clásica $1/(\pi\sqrt{A^2-x^2})$")
    for s_ in (-A, A):
        ax.axvline(s_, color=COLORES["energia"], ls=":", lw=1.2)
    ax.set_ylim(0, tope)
    ax.set_title(f"Densidad de probabilidad · n = {n}")
    ax.set_xlabel(f"x [{L}]")
    ax.set_ylabel(f"densidad [1/{L}]")
    ax.legend(loc="upper center")
    ax.grid(alpha=0.3)
    ax = ejes[1]
    ax.plot(x, d["F_q"], color=COLORES["densidad"], lw=2, label="cuántica")
    ax.plot(x, d["F_cl"], color="white", ls="--", lw=1.8, label="clásica  ½ + arcsin(x/A)/π")
    i = int(np.argmax(np.abs(d["F_q"] - d["F_cl"])))
    ax.annotate("", xy=(x[i], d["F_q"][i]), xytext=(x[i], d["F_cl"][i]),
                arrowprops=dict(arrowstyle="<->", color=COLORES["energia"], lw=1.5))
    ax.text(x[i], (d["F_q"][i] + d["F_cl"][i]) / 2, f"  D = {d['distancia_ks']:.3f}", color=COLORES["energia"],
            va="center", fontsize=10)
    ax.set_title("Probabilidad acumulada F(x)")
    ax.set_xlabel(f"x [{L}]")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    if ns is not None:
        ax = ejes[2]
        ax.plot(ns, ks, "o-", color=COLORES["onda"], ms=3.5, lw=1.4)
        ax.plot([n], [d["distancia_ks"]], "o", color=COLORES["energia"], ms=9)
        ax.set_yscale("log")
        ax.set_title("Distancia cuántica–clásica D frente a n")
        ax.set_xlabel("número cuántico n")
        ax.set_ylabel("D = max|F_q − F_cl|")
        ax.grid(alpha=0.3, which="both")
    return fig


def figura_dinamica(x_vis, taus, re, im, rho, x_medio, nombre_longitud: str, etiquetas: list[str],
                    titulo_estado: str):
    """
    Animación de Plotly. Arriba: la función de onda COMPLEJA (Re y Im). Abajo: la densidad |Ψ|²
    (con la densidad inicial como referencia) y el valor medio ⟨x⟩ como marcador.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=(f"Función de onda compleja Ψ(x,t) — {titulo_estado}",
                                        "Densidad de probabilidad |Ψ(x,t)|²  y  posición media ⟨x⟩"))
    fig.add_trace(go.Scatter(x=x_vis, y=re[0], name="Re Ψ", line=dict(color=COLORES["onda"], width=3)), 1, 1)
    fig.add_trace(go.Scatter(x=x_vis, y=im[0], name="Im Ψ", line=dict(color=COLORES["interferencia"], width=3)), 1, 1)
    fig.add_trace(go.Scatter(x=x_vis, y=rho[0], name="|Ψ|²", fill="tozeroy",
                             line=dict(color=COLORES["densidad"], width=3), fillcolor="rgba(255,176,0,0.15)"), 2, 1)
    fig.add_trace(go.Scatter(x=[x_medio[0]], y=[0], mode="markers", name="⟨x⟩",
                             marker=dict(color=COLORES["energia"], size=14, symbol="diamond")), 2, 1)
    fig.add_trace(go.Scatter(x=x_vis, y=rho[0], name="|Ψ(x,0)|² (referencia)",
                             line=dict(color="white", width=1.3, dash="dot")), 2, 1)
    nombres = [str(i) for i in range(len(taus))]
    fig.frames = [go.Frame(name=nombres[i], traces=[0, 1, 2, 3],
                           data=[go.Scatter(y=re[i]), go.Scatter(y=im[i]), go.Scatter(y=rho[i]),
                                 go.Scatter(x=[x_medio[i]], y=[0])]) for i in range(len(taus))]
    amp = 1.12 * max(np.max(np.abs(re)), np.max(np.abs(im)))
    fig.update_yaxes(range=[-amp, amp], title_text="Ψ (unid. de visualización)", row=1, col=1)
    fig.update_yaxes(range=[-0.03 * np.max(rho), 1.12 * np.max(rho)], title_text="|Ψ|²", row=2, col=1)
    fig.update_xaxes(title_text=f"x [{nombre_longitud}]", row=2, col=1)
    qc.aplicar_tema_plotly(fig, altura=640)
    qc.agregar_animacion(fig, nombres, etiquetas, duracion_ms=70)
    return fig


# =====================================================================
# 3. PRUEBAS NUMÉRICAS
# =====================================================================
def ejecutar_pruebas() -> qc.RegistroPruebas:
    """Pruebas de física, de la derivada numérica, de las unidades y de la validación."""
    r = qc.RegistroPruebas("Oscilador armónico 1D")
    m, omega = M_E, 1.0e15
    x0 = longitud_caracteristica(m, omega)
    xi = malla_xi(12.0, 10001)
    x = xi * x0
    zona = np.abs(xi) < 6.0

    peor = {k: 0.0 for k in ("norma", "energia", "virial", "T", "nodos_pos", "x", "x2", "paridad",
                             "schro", "deriv")}
    nodos_ok = energia_ok = True
    for n in range(0, 13):
        psi = psi_oscilador(x, n, m, omega)
        e_teo = energia_teorica(n, omega)
        d_num = derivada_numerica(x, psi)
        t_media, v_media = _energia_con_derivada(x, psi, m, omega, d_num)
        peor["norma"] = max(peor["norma"], abs(normalizacion(x, psi) - 1.0))
        peor["energia"] = max(peor["energia"], abs((t_media + v_media) / e_teo - 1.0))
        peor["virial"] = max(peor["virial"], abs(t_media - v_media) / e_teo)
        peor["T"] = max(peor["T"], abs(t_media / e_teo - 0.5))
        energia_ok &= bool(np.isclose(e_teo, HBAR * omega * (n + 0.5), rtol=1e-12))
        nodos = nodos_oscilador(x, psi)
        raices = np.sort(np.polynomial.hermite.hermroots([0] * n + [1])) if n else np.array([])
        nodos_ok &= len(nodos) == n
        if n:
            peor["nodos_pos"] = max(peor["nodos_pos"], float(np.max(np.abs(nodos / x0 - raices))))
        xm, x2m = valores_esperados(x, psi)
        peor["x"] = max(peor["x"], abs(xm / x0))
        peor["x2"] = max(peor["x2"], abs(x2m / x0 ** 2 / (n + 0.5) - 1.0))
        peor["paridad"] = max(peor["paridad"], float(np.max(np.abs(psi[::-1] - (-1) ** n * psi)) / np.max(np.abs(psi))))
        dx = x[1] - x[0]
        d2 = np.gradient(np.gradient(psi, dx), dx)
        res = -(HBAR ** 2) / (2 * m) * d2 + potencial_armonico(x, m, omega) * psi - e_teo * psi
        peor["schro"] = max(peor["schro"], float(np.max(np.abs(res[zona])) / (e_teo * np.max(np.abs(psi)))))
        d_ana = derivada_analitica(x, n, m, omega)
        peor["deriv"] = max(peor["deriv"], float(np.max(np.abs(d_num - d_ana)[zona]) / np.max(np.abs(d_ana))))

    r.comprobar("Normalización ∫|ψ_n|² = 1 (n = 0…12)", peor["norma"] < 1e-9, f"máx |∫−1| = {peor['norma']:.2e}")
    r.comprobar("E_n = ħω(n+½) (n = 0…12)", energia_ok)
    r.comprobar("Energía integrada ∫(u_T+u_V)dx = ħω(n+½)", peor["energia"] < 1e-4,
                f"máx error relativo = {peor['energia']:.2e}")
    r.comprobar("Virial: ⟨T⟩ = ⟨V⟩", peor["virial"] < 1e-4, f"máx |⟨T⟩−⟨V⟩|/E = {peor['virial']:.2e}")
    r.comprobar("Virial: ⟨T⟩ = E_n/2", peor["T"] < 1e-4, f"máx |⟨T⟩/E − ½| = {peor['T']:.2e}")
    r.comprobar("Número de nodos = n (n = 0…12)", nodos_ok)
    r.comprobar("Posición de los nodos = raíces de H_n", peor["nodos_pos"] < 1e-4,
                f"máx desviación = {peor['nodos_pos']:.2e} x₀")
    r.comprobar("⟨x⟩ = 0", peor["x"] < 1e-10, f"máx |⟨x⟩|/x₀ = {peor['x']:.2e}")
    r.comprobar("⟨x²⟩ = (n+½)x₀²", peor["x2"] < 1e-6, f"máx error relativo = {peor['x2']:.2e}")
    r.comprobar("Paridad ψ(−x) = (−1)ⁿψ(x)", peor["paridad"] < 1e-12, f"{peor['paridad']:.2e}")
    r.comprobar("Ecuación de Schrödinger (residuo relativo)", peor["schro"] < 2e-3, f"{peor['schro']:.2e}")
    r.comprobar("Derivada numérica ≈ derivada analítica", peor["deriv"] < 1e-3, f"{peor['deriv']:.2e}")

    estados = [psi_oscilador(x, k, m, omega) for k in range(7)]
    peor_orto = max(abs(solapamiento(x, estados[i], estados[j])) for i in range(7) for j in range(i + 1, 7))
    r.comprobar("Ortogonalidad ⟨ψ_i|ψ_j⟩ = 0", peor_orto < 1e-8, f"máx = {peor_orto:.2e}")

    # Estabilidad numérica con n grande (2ⁿ n! desbordaría con enteros)
    x_g = malla_xi(25.0, 20001) * x0
    psi_g = psi_oscilador(x_g, 60, m, omega)
    r.comprobar("n = 60 sin desbordamiento (norma = 1)", np.all(np.isfinite(psi_g)) and abs(normalizacion(x_g, psi_g) - 1) < 1e-8)

    # Convergencia de la derivada numérica: error de orden 2
    p_conv = ParametrosOscilador(3, m, omega, "SI", 9.0, 2001, "numerica")
    conv = calcular_estado(p_conv)["convergencia"]
    r.comprobar("Derivada numérica de orden 2 (error ÷4 al duplicar la resolución)",
                1.8 < conv["orden_observado"] < 2.2, f"orden observado = {conv['orden_observado']:.2f}")

    # Región clásicamente prohibida: para n = 0, P(|x| > x₀) = erfc(1)
    d0 = calcular_estado(ParametrosOscilador(0, m, omega, "SI", 9.0, 3001, "analitica"))
    r.comprobar("n = 0: P(|x|>x₀) = erfc(1) ≈ 0.1573 (efecto túnel)", abs(d0["prob_fuera"] - erfc(1.0)) < 2e-5,
                f"{d0['prob_fuera']:.6f}")

    # Unidades atómicas
    m_au = M_E
    w_au = 1.0 * qc.obtener_unidades("Atómicas")["factor_omega"]
    r.comprobar("Unidades atómicas: m = mₑ, ω = 1 Eₕ/ħ → x₀ = a₀",
                abs(longitud_caracteristica(m_au, w_au) / A0 - 1.0) < 1e-8)
    r.comprobar("Unidades atómicas: E₀ = ½ Eₕ", abs(energia_teorica(0, w_au) / E_HARTREE - 0.5) < 1e-12)

    # Dinámica
    xd = np.linspace(-8 * x0, 8 * x0, 4001)
    c01 = coeficientes_dos_estados(0.5, 0.0)
    normas = [integrar(xd, np.abs(onda_dependiente_del_tiempo(xd, [0, 1], c01, m, omega, t)) ** 2)
              for t in np.linspace(0, 2 * np.pi, 7)]
    r.comprobar("Dinámica: la norma se conserva", np.max(np.abs(np.array(normas) - 1)) < 1e-8)
    for tau in (0.0, np.pi / 3, 2.0):
        rho_t = np.abs(onda_dependiente_del_tiempo(xd, [0, 1], c01, m, omega, tau)) ** 2
        xm = integrar(xd, xd * rho_t)
        if abs(xm / x0 - np.cos(tau) / np.sqrt(2)) > 1e-6:
            r.comprobar("Dinámica: ⟨x⟩(τ) = x₀ cos τ /√2 para (|0⟩+|1⟩)/√2", False, f"τ = {tau}")
            break
    else:
        r.comprobar("Dinámica: ⟨x⟩(τ) = x₀ cos τ /√2 para (|0⟩+|1⟩)/√2", True)
    uno = np.array([1.0 + 0j])
    rho_a = np.abs(onda_dependiente_del_tiempo(xd, [2], uno, m, omega, 0.0)) ** 2
    rho_b = np.abs(onda_dependiente_del_tiempo(xd, [2], uno, m, omega, 1.7)) ** 2
    psi_b = onda_dependiente_del_tiempo(xd, [2], uno, m, omega, 1.7)
    r.comprobar("Estado estacionario: ρ constante aunque Re Ψ e Im Ψ cambien",
                np.allclose(rho_a, rho_b, atol=1e-12 * rho_a.max())
                and np.max(np.abs(psi_b.imag)) > 0.1 * np.max(np.abs(psi_b.real)))

    # Validación de entradas
    v = validar_parametros_oscilador
    r.comprobar_error("Rechaza n < 0", v, -1, 1.0, 1e15, "SI", 9.0, 2001)
    r.comprobar_error("Rechaza n no entero (1.5)", v, 1.5, 1.0, 1e15, "SI", 9.0, 2001)
    r.comprobar_error("Rechaza masa ≤ 0", v, 0, 0.0, 1e15, "SI", 9.0, 2001)
    r.comprobar_error("Rechaza ω ≤ 0", v, 0, 1.0, -5.0, "SI", 9.0, 2001)
    r.comprobar_error("Rechaza ω no numérica", v, 0, 1.0, "abc", "SI", 9.0, 2001)
    r.comprobar_error("Rechaza intervalo fuera de rango", v, 0, 1.0, 1e15, "SI", 1.0, 2001)
    r.comprobar_error("Rechaza resolución insuficiente", v, 60, 1.0, 1e15, "SI", 30.0, 501)
    r.comprobar_error("Rechaza sistema desconocido", v, 0, 1.0, 1e15, "CGS", 9.0, 2001)

    # Límite clásico (principio de correspondencia)
    Ac = 2.0
    xs = np.array([-Ac, 0.0, Ac])
    r.comprobar("Acumulada clásica: F(−A) = 0, F(0) = ½, F(A) = 1",
                np.allclose(acumulada_clasica(xs, Ac), [0.0, 0.5, 1.0]))
    xi = np.linspace(-1.9, 1.9, 2001)
    dF = np.gradient(acumulada_clasica(xi, Ac), xi)
    r.comprobar("dF/dx = P_clásica = 1/(π√(A²−x²))", np.max(np.abs(dF[5:-5] - densidad_clasica(xi, Ac)[5:-5])) < 1e-4)
    lim = [calcular_limite_clasico(k, M_E, 1e15) for k in (0, 5, 20, 60)]
    r.comprobar("⟨x²⟩ cuántico = ⟨x²⟩ clásico = A²/2 = (n+½)x₀²",
                max(abs(d["x2_cuantico"] / d["x2_clasico"] - 1) for d in lim) < 1e-6)
    ks = [d["distancia_ks"] for d in lim]
    r.comprobar("Correspondencia: la distancia cuántica–clásica D disminuye con n (n = 0, 5, 20, 60)",
                all(a > b for a, b in zip(ks, ks[1:])), "D = " + ", ".join(f"{k:.3f}" for k in ks))
    pf = [d["prob_fuera"] for d in lim]
    r.comprobar("La probabilidad en la zona prohibida disminuye con n (n = 0 → erfc(1))",
                all(a > b for a, b in zip(pf, pf[1:])) and abs(pf[0] - erfc(1.0)) < 1e-4)
    return r


# =====================================================================
# 4. INTERFAZ (Streamlit)
# =====================================================================
VALORES_INICIALES = {
    "osc_n": 0, "osc_masa": 1.0, "osc_omega": "1e15", "osc_sistema": "SI", "osc__sistema_previo": "SI",
    "osc_rango": 9.0, "osc_resolucion": 3001, "osc_metodo": "numerica", "osc_zoom": True,
    "osc_niveles_n": 3, "osc_comp_n": [0, 1, 3], "osc_comp_exc": 3,
    "osc_clas_n": 20, "osc_dyn_n1": 0, "osc_dyn_n2": 1, "osc_dyn_peso": 0.5, "osc_dyn_fase": 0.0, "osc_dyn_modo": "Superposición n₁ + n₂",
}
DEMOS = {
    "Estado fundamental (n = 0, gaussiana)": {"osc_n": 0, "osc_comp_exc": 1},
    "Primer excitado (n = 1)": {"osc_n": 1},
    "Estado muy excitado (n = 10)": {"osc_n": 10, "osc_rango": 10.0, "osc_resolucion": 4001},
    "Unidades atómicas: m = mₑ, ω = 1 Eₕ/ħ (x₀ = a₀)": {"osc_sistema": "Atómicas", "osc__sistema_previo": "Atómicas",
                                                         "osc_omega": "1", "osc_masa": 1.0, "osc_n": 2},
    "Molécula diatómica ligera (m = 1000 mₑ, ω = 5×10¹⁴ rad/s)": {"osc_sistema": "SI", "osc__sistema_previo": "SI",
                                                                 "osc_masa": 1000.0, "osc_omega": "5e14", "osc_n": 1},
}


# ---------------------------------------------------------------------
# Guía de práctica y autoevaluación
# ---------------------------------------------------------------------
GUIA = [
    {"titulo": "Teorema del virial",
     "objetivo": "Comprobar que en todo estado estacionario la energía se reparte por igual entre cinética y potencial.",
     "pasos": ["Carga la configuración (n = 3).", "Anota ⟨T⟩/E y ⟨V⟩/E en «Resultados».",
               "Cambia n a 0, 7 y 15, y después la masa o ω. Anota de nuevo ambos cocientes."],
     "pregunta": "¿Depende el reparto de n, de la masa o de ω?",
     "resultado": "Siempre ⟨T⟩/E = ⟨V⟩/E = 0.5 (salvo el error numérico, ~10⁻⁵). Es el teorema del virial para "
                  "un potencial cuadrático: 2⟨T⟩ = 2⟨V⟩. No depende de n, m ni ω. El panel 6 muestra cómo se "
                  "acumulan ambas contribuciones a lo largo de x.",
     "pestana": "Estado individual", "config": {"osc_n": 3, "osc_masa": 1.0, "osc_omega": "1e15", "osc_sistema": "SI",
                                                "osc__sistema_previo": "SI"}},
    {"titulo": "Efecto túnel",
     "objetivo": "Medir la probabilidad de encontrar la partícula donde la física clásica lo prohíbe.",
     "pasos": ["Carga la configuración (n = 0).", "Anota «P en zona prohibida».",
               "Repite con n = 1, 5 y 20."],
     "pregunta": "¿Es cero la probabilidad fuera de los puntos de retorno? ¿Cómo cambia con n?",
     "resultado": "Para n = 0 vale erfc(1) ≈ 15.7 %: la onda penetra en la región donde E < V(x). Disminuye al "
                  "aumentar n (≈ 11 % para n = 1, ≈ 7 % para n = 5, ≈ 5 % para n = 20): el sistema se acerca al "
                  "comportamiento clásico.",
     "pestana": "Estado individual", "config": {"osc_n": 0}},
    {"titulo": "Principio de correspondencia",
     "objetivo": "Ver cómo la distribución cuántica se aproxima a la clásica al crecer n.",
     "pasos": ["Carga la configuración (n = 0).", "Compara la curva cuántica con la clásica (línea discontinua).",
               "Sube n a 5, 20 y 60 y anota la distancia D entre las distribuciones acumuladas."],
     "pregunta": "¿Dónde es más probable encontrar la partícula clásica? ¿Y la cuántica para n grande?",
     "resultado": "La partícula clásica pasa más tiempo cerca de los puntos de retorno (donde se frena), por eso P(x) "
                  "crece hacia ±A. Para n = 0 la cuántica es máxima en el centro (lo opuesto). Al crecer n, la "
                  "envolvente de |ψₙ|² sigue a la clásica y D baja (0.097 → 0.041 → 0.026 → 0.018).",
     "pestana": "Límite clásico", "config": {"osc_clas_n": 0}},
    {"titulo": "Error de discretización",
     "objetivo": "Comprobar que el error de la derivada numérica es de orden 2.",
     "pasos": ["Carga la configuración (n = 2, resolución 801).", "Anota el error relativo de E.",
               "Sube la resolución a 1601 y a 3201. Abre «Error de discretización de la derivada».",
               "Cambia el método a «Analítica (Hermite)»."],
     "pregunta": "Al duplicar el número de puntos, ¿por cuánto se divide el error?",
     "resultado": "Aproximadamente por 4 (orden observado ≈ 2), como corresponde a diferencias centrales de orden 2. "
                  "Con la derivada analítica el error baja varios órdenes: lo que queda es el error de la integral.",
     "pestana": "Estado individual", "config": {"osc_n": 2, "osc_resolucion": 801, "osc_metodo": "numerica"}},
    {"titulo": "Estado estacionario frente a superposición",
     "objetivo": "Distinguir una fase global (sin movimiento) de una interferencia real.",
     "pasos": ["Carga la configuración (superposición de n = 0 y n = 1).", "Reproduce la animación y observa ⟨x⟩.",
               "Cambia a «Estado estacionario único» y reprodúcela de nuevo."],
     "pregunta": "¿En cuál de los dos casos se mueve la densidad |Ψ|²? ¿Con qué periodo?",
     "resultado": "En la superposición ⟨x⟩ oscila como x₀cos(ωt)/√2 con periodo T = 2π/ω (el del oscilador clásico). "
                  "En el estado estacionario Re Ψ e Im Ψ cambian, pero |Ψ|² y ⟨x⟩ = 0 permanecen fijos.",
     "pestana": "Dinámica", "config": {"osc_dyn_modo": "Superposición n₁ + n₂", "osc_dyn_n1": 0, "osc_dyn_n2": 1,
                                       "osc_dyn_peso": 0.5, "osc_dyn_fase": 0.0}},
]

PREGUNTAS = [
    {"enunciado": "¿Cuánto vale la separación entre dos niveles consecutivos del oscilador armónico?",
     "opciones": ["ħω, igual para todos los niveles", "Crece como n²", "Disminuye como 1/n²", "Es cero"],
     "correcta": 0, "explicacion": "Eₙ = ħω(n + ½), así que Eₙ₊₁ − Eₙ = ħω: los niveles están equiespaciados."},
    {"enunciado": "¿Cuál es la energía del estado fundamental?",
     "opciones": ["0", "ħω/2", "ħω", "−ħω/2"],
     "correcta": 1, "explicacion": "E₀ = ħω/2 > 0 es la energía de punto cero, consecuencia del principio de incertidumbre."},
    {"enunciado": "En un estado estacionario del oscilador, ¿qué relación hay entre ⟨T⟩ y ⟨V⟩?",
     "opciones": ["⟨T⟩ = 2⟨V⟩", "⟨T⟩ = ⟨V⟩ = Eₙ/2", "⟨V⟩ = 0", "Depende de la masa"],
     "correcta": 1, "explicacion": "Teorema del virial para V ∝ x²: 2⟨T⟩ = 2⟨V⟩, y como ⟨T⟩ + ⟨V⟩ = Eₙ, cada uno vale Eₙ/2."},
    {"enunciado": "¿Cuántos nodos tiene ψₙ?",
     "opciones": ["n − 1", "n", "n + 1", "2n"],
     "correcta": 1, "explicacion": "ψₙ es proporcional al polinomio de Hermite Hₙ, que tiene exactamente n raíces reales."},
    {"enunciado": "Para n = 0, la probabilidad de encontrar la partícula fuera de los puntos de retorno clásicos es…",
     "opciones": ["exactamente 0", "≈ 15.7 %", "50 %", "100 %"],
     "correcta": 1, "explicacion": "Vale erfc(1) ≈ 0.157: la función de onda penetra en la región clásicamente prohibida."},
    {"enunciado": "Al aumentar mucho n, la densidad cuántica promediada localmente se parece cada vez más a…",
     "opciones": ["una gaussiana centrada en 0", "una distribución uniforme",
                  "la densidad clásica, máxima cerca de los puntos de retorno", "una función nula"],
     "correcta": 2, "explicacion": "Es el principio de correspondencia: P_clásica = 1/(π√(A² − x²)) es máxima donde la "
                                   "partícula clásica va más lenta, en ±A."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("osc_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


def _al_cambiar_sistema():
    """Convierte ω al nuevo sistema para conservar la física (el mismo número significaría otra cosa)."""
    nuevo, previo = st.session_state["osc_sistema"], st.session_state["osc__sistema_previo"]
    if nuevo == previo:
        return
    try:
        omega_si = float(st.session_state["osc_omega"]) * qc.obtener_unidades(previo)["factor_omega"]
        st.session_state["osc_omega"] = f"{omega_si / qc.obtener_unidades(nuevo)['factor_omega']:.12g}"
    except ValueError:
        pass                                  # texto inválido: se avisará en la validación
    st.session_state["osc__sistema_previo"] = nuevo


def _leer_parametros_fisicos():
    with st.container(border=True):
        qc.seccion("Parámetros del sistema")
        c1, c2, c3, c4 = st.columns(4)
        sistema = c1.radio("Sistema de unidades", ["SI", "Atómicas"], key="osc_sistema", horizontal=True,
                           on_change=_al_cambiar_sistema,
                           help="SI: ω en rad/s, longitudes en nm, energías en eV. Atómicas: ω en Eₕ/ħ, longitudes "
                                "en a₀, energías en Eₕ. Al cambiar de sistema, ω se convierte automáticamente.")
        u = qc.obtener_unidades(sistema)
        masa = c2.number_input("Masa m [mₑ]", min_value=0.0, step=0.1, format="%.6g", key="osc_masa")
        omega = c3.text_input(f"Frecuencia angular ω [{u['nombre_omega']}]", key="osc_omega",
                              help="Admite notación científica, p. ej. 1e15")
        c4.selectbox("Derivada para u_T", list(METODOS_DERIVADA), key="osc_metodo",
                     format_func=lambda k: "Numérica (orden 2)" if k == "numerica" else "Analítica (Hermite)",
                     help="Se usa para la densidad de energía cinética. La otra se muestra como contraste.")
        qc.seccion("Malla numérica y vista")
        d1, d2, d3, _ = st.columns(4, vertical_alignment="bottom")
        d1.slider("Intervalo espacial ± [x₀]", RANGO_MIN, 20.0, step=0.5, key="osc_rango", format="%.1f",
                  help="Semiancho del dominio de cálculo en múltiplos de x₀ = √(ħ/mω).")
        d2.slider("Resolución (puntos)", RES_MIN + 300, 8001, step=100, key="osc_resolucion")
        d3.toggle("Ampliar a la zona física", key="osc_zoom",
                  help="Si se desactiva, las gráficas muestran todo el intervalo de cálculo.")
        qc.pie_de_parametros(DEMOS, "osc_demo", _aplicar_demo, VALORES_INICIALES, "osc_reset")
    try:
        return validar_parametros_oscilador(0, masa, omega, sistema, st.session_state["osc_rango"],
                                            st.session_state["osc_resolucion"], st.session_state["osc_metodo"])
    except ValueError as error:
        qc.error(error)
        return None


def _con_n(p: ParametrosOscilador, n) -> ParametrosOscilador:
    """Copia de p con otro n, revalidando la resolución para ese n."""
    u = qc.obtener_unidades(p.sistema)
    return validar_parametros_oscilador(n, p.masa / M_E, p.omega / u["factor_omega"], p.sistema, p.rango,
                                        p.resolucion, p.metodo)


def _pestana_individual(p_base: ParametrosOscilador):
    c1, _, _, _ = st.columns(4)
    n = c1.number_input("Número cuántico n", min_value=0, max_value=N_MAX, step=1, key="osc_n")
    try:
        p = _con_n(p_base, n)
    except ValueError as error:
        qc.error(error)
        return
    d = calcular_estado(p)
    u = qc.obtener_unidades(p.sistema)
    fe, fx, U, L = u["factor_energia"], u["factor_longitud"], u["nombre_energia"], u["nombre_longitud"]
    for texto in d["advertencias"]:
        qc.aviso(texto)

    qc.seccion("Resultados")
    qc.metricas([
        (f"E teórica ħω(n+½) [{U}]", qc.cientifico(d["e_teo"] / fe, 6), qc.texto_energia(d["e_teo"], p.sistema)),
        (f"E numérica ∫(u_T+u_V)dx [{U}]", qc.cientifico(d["e_num"] / fe, 6), qc.texto_energia(d["e_num"], p.sistema)),
        ("Error relativo", f"{100 * d['error_relativo']:.3e} %"),
        ("Nodos", f"{len(d['nodos'])}", f"Esperados: n = {p.n}"),
        (r"$\langle T\rangle / E$", f"{d['t_media'] / d['e_num']:.6f}", "Teorema del virial: 0.5"),
        (r"$\langle V\rangle / E$", f"{d['v_media'] / d['e_num']:.6f}", "Teorema del virial: 0.5"),
        ("Normalización ∫|ψ|²dx", f"{d['norma']:.10f}"),
        ("P en zona prohibida", f"{100 * d['prob_fuera']:.4f} %", "Probabilidad de |x| mayor que el punto de retorno"),
    ])
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_estado_individual(d, p, st.session_state["osc_zoom"]), archivo=f"oscilador_estado_n{p.n}.png")
    qc.exportar_datos({"x [m]": d["x"], "psi [m^-1/2]": d["psi"], "rho = |psi|^2 [1/m]": d["rho"],
                       "V [J]": d["V"], "u_T cinetica [J/m]": d["u_T"], "u_V potencial [J/m]": d["u_V"],
                       "E_n [J]": np.full_like(d["x"], d["e_teo"])}, f"oscilador_datos_n{p.n}.csv")

    with st.expander("Valores numéricos detallados", expanded=False):
        nodos_txt = "ninguno" if not len(d["nodos"]) else ", ".join(f"{v / fx:.4g}" for v in d["nodos"])
        qc.tabla([
            ("Longitud característica x₀ = √(ħ/mω)", f"{d['x0'] / fx:.8g}", L),
            ("Cuanto de energía ħω", qc.cientifico(HBAR * p.omega / fe, 8), U),
            ("Energía teórica ħω(n+½)", qc.cientifico(d["e_teo"] / fe, 10), U),
            ("Energía calculada ∫(u_T+u_V)dx", qc.cientifico(d["e_num"] / fe, 10), U),
            ("Error relativo", f"{100 * d['error_relativo']:.4e}", "%"),
            ("Nodos", nodos_txt, L, f"{len(d['nodos'])} nodos"),
            ("⟨x⟩", f"{d['x_media'] / fx:.4e}", L, "esperado 0"),
            ("⟨x²⟩", f"{d['x2_media'] / fx ** 2:.6e}", f"{L}²",
             f"esperado (n+½)x₀² = {(p.n + 0.5) * d['x0'] ** 2 / fx ** 2:.6e}"),
            ("⟨T⟩", qc.cientifico(d["t_media"] / fe, 8), U, f"{d['t_media'] / d['e_num']:.6f} E"),
            ("⟨V⟩", qc.cientifico(d["v_media"] / fe, 8), U, f"{d['v_media'] / d['e_num']:.6f} E"),
            ("Virial |⟨T⟩ − ⟨V⟩| / E", f"{abs(d['t_media'] - d['v_media']) / d['e_num']:.3e}", ""),
            ("Punto de retorno ±√(2n+1)x₀", f"±{d['xt'] / fx:.6g}", L),
            ("Probabilidad en la zona prohibida", f"{100 * d['prob_fuera']:.5f}", "%"),
        ], archivo=f"oscilador_valores_n{p.n}.csv")
    with st.expander("Error de discretización de la derivada", expanded=False):
        c = d["convergencia"]
        st.markdown("La derivada numérica usa diferencias centrales de **orden 2**: el error de truncamiento es "
                    "≈ (Δx²/6)·ψ‴, de modo que el error de la energía cae ≈ 4 veces al duplicar la resolución.")
        qc.tabla([(f"{f['puntos']} puntos", f"{f['error_relativo']:.3e}", "") for f in c["filas"]],
                 encabezados=("Malla", "Error relativo de E", ""))
        qc.tabla([
            ("Orden de convergencia observado", f"{c['orden_observado']:.2f}", "", "teórico: 2"),
            ("E con derivada numérica", qc.cientifico(d["e_num_numerica"] / fe, 8), U),
            ("E con derivada analítica", qc.cientifico(d["e_num_analitica"] / fe, 8), U),
            ("E teórica", qc.cientifico(d["e_teo"] / fe, 8), U),
        ])
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- **V(x)** (panel 3) es la energía potencial *por unidad de probabilidad*: la energía que tendría la "
            "partícula si estuviese en x. **u_V(x) = V(x)|ψ|²** (panel 4) es una *densidad de energía*: pondera V con "
            "la probabilidad de estar en x; sus unidades son energía/longitud y su integral es ⟨V⟩.\n"
            "- **u_T** y **u_V** son las densidades espaciales de las contribuciones de los términos cinético y "
            "potencial del hamiltoniano. No son la única definición posible de una densidad local de energía cuántica.\n"
            "- La integral acumulada (panel 6) muestra cómo cada región aporta a ⟨T⟩, ⟨V⟩ y E; para todo estado "
            "estacionario ⟨T⟩ = ⟨V⟩ = Eₙ/2 (teorema del virial para potenciales cuadráticos).\n"
            "- La función de onda **penetra** más allá de los puntos de retorno clásicos (efecto túnel): "
            "para n = 0 la probabilidad de estar en la región prohibida es erfc(1) ≈ 15.7 %.\n"
            "- Los niveles son **equiespaciados** (ΔE = ħω), a diferencia de la caja (∝ n²).")


def _pestana_niveles(p_base: ParametrosOscilador):
    c1, _, _, _ = st.columns(4)
    n = c1.number_input("Nivel resaltado n", min_value=0, max_value=N_MAX, step=1, key="osc_niveles_n")
    try:
        p = _con_n(p_base, n)
    except ValueError as error:
        qc.error(error)
        return
    d = calcular_estado(p)
    u = qc.obtener_unidades(p.sistema)
    qc.seccion("Resultados")
    qc.metricas([
        (f"Eₙ [{u['nombre_energia']}]", qc.cientifico(d["e_teo"] / u["factor_energia"], 6)),
        (f"ħω [{u['nombre_energia']}]", qc.cientifico(HBAR * p.omega / u["factor_energia"], 6), "Separación entre niveles"),
        (f"Punto de retorno [{u['nombre_longitud']}]", f"±{d['xt'] / u['factor_longitud']:.5g}"),
        (f"x₀ [{u['nombre_longitud']}]", f"{d['x0'] / u['factor_longitud']:.5g}"),
    ])
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_niveles_y_escalas(d, p, st.session_state["osc_zoom"]), archivo=f"oscilador_niveles_n{p.n}.png")
    st.caption("En el panel derecho ψₙ y |ψₙ|² comparten el eje x pero no el eje y: tienen unidades distintas "
               "(L^(−1/2) y L^(−1)), por eso cada una usa su propia escala, indicada por el color del eje.")


def _pestana_comparacion(p_base: ParametrosOscilador):
    c1, c2 = st.columns([1, 2], vertical_alignment="bottom")
    modo = c1.radio("Modo", ["Varios estados", "Fundamental frente a un estado excitado"], key="osc_comp_modo")
    if modo == "Varios estados":
        lista = c2.multiselect("Estados n a comparar (máx. 8)", list(range(0, 13)), key="osc_comp_n", max_selections=8)
    else:
        exc = c2.number_input("Estado excitado n", min_value=1, max_value=N_MAX, step=1, key="osc_comp_exc")
        lista = [0, int(exc)]
    if not lista:
        qc.nota("Selecciona al menos un estado.")
        return
    try:
        datos = []
        for n in sorted(lista):
            p = _con_n(p_base, n)
            x = malla_xi(p.rango, p.resolucion) * longitud_caracteristica(p.masa, p.omega)
            psi = psi_oscilador(x, n, p.masa, p.omega)
            datos.append({"n": n, "x": x, "psi": psi, "rho": psi ** 2, "xt": punto_retorno(n, p.masa, p.omega),
                          "x0": longitud_caracteristica(p.masa, p.omega), "p": p})
    except ValueError as error:
        qc.error(error)
        return
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_comparacion(datos, datos[0]["p"], modo != "Varios estados"), archivo="oscilador_comparacion.png")
    u = qc.obtener_unidades(p_base.sistema)
    qc.seccion("Tabla comparativa")
    qc.tabla_libre([{"n": dd["n"],
                     f"Eₙ [{u['nombre_energia']}]": f"{energia_teorica(dd['n'], p_base.omega) / u['factor_energia']:.6g}",
                     "Nodos": len(nodos_oscilador(dd["x"], dd["psi"])),
                     f"Punto de retorno [{u['nombre_longitud']}]": f"{dd['xt'] / u['factor_longitud']:.5g}",
                     "⟨x²⟩/x₀²": f"{integrar(dd['x'], dd['x'] ** 2 * dd['rho']) / dd['x0'] ** 2:.4f}",
                     f"⟨ψ{datos[0]['n']}|ψₙ⟩": f"{solapamiento(dd['x'], datos[0]['psi'], dd['psi']):+.6f}"}
                    for dd in datos],
                   numericas=("n", f"Eₙ [{u['nombre_energia']}]", "Nodos", f"Punto de retorno [{u['nombre_longitud']}]",
                              "⟨x²⟩/x₀²", f"⟨ψ{datos[0]['n']}|ψₙ⟩"), archivo="oscilador_comparacion.csv")
    st.caption("Estados distintos son ortogonales: el solapamiento es 0 salvo consigo mismo (= 1). "
               "La extensión espacial crece como √(2n+1)·x₀.")


@st.cache_data(show_spinner="Calculando la distancia cuántica–clásica…", max_entries=8)
def _distancias_cacheadas(n_max: int, masa: float, omega: float):
    return distancias_ks(n_max, masa, omega)


def _pestana_limite_clasico(p_base: ParametrosOscilador):
    c1, c2, _, _ = st.columns(4, vertical_alignment="bottom")
    n = int(c1.slider("Número cuántico n", 0, 60, key="osc_clas_n"))
    curva = c2.toggle("Mostrar D frente a n", key="osc_clas_curva", value=True,
                      help="Calcula la distancia cuántica–clásica para n = 0…60 (tarda unos segundos la primera vez).")
    d = calcular_limite_clasico(n, p_base.masa, p_base.omega)
    u = qc.obtener_unidades(p_base.sistema)
    fx, L = u["factor_longitud"], u["nombre_longitud"]
    qc.seccion("Resultados")
    qc.metricas([
        (f"Amplitud clásica A [{L}]", f"{d['A'] / fx:.5g}", "A = √(2n+1)·x₀: la partícula clásica de la misma energía oscila entre ±A."),
        ("Distancia D cuántica–clásica", f"{d['distancia_ks']:.4f}",
         "D = max|F_cuántica − F_clásica| entre las probabilidades acumuladas. Tiende a 0 cuando n → ∞."),
        (r"$\langle x^2\rangle$ cuántico / clásico", f"{d['x2_cuantico'] / d['x2_clasico']:.8f}",
         "Ambos valen (n+½)x₀² = A²/2: el segundo momento coincide exactamente para todo n."),
        ("P fuera de ±A (cuántica)", f"{100 * d['prob_fuera']:.3f} %", "En el caso clásico es exactamente 0."),
    ])
    qc.seccion("Visualización")
    ns, ks = _distancias_cacheadas(60, p_base.masa, p_base.omega) if curva else (None, None)
    qc.mostrar_pyplot(figura_limite_clasico(d, n, p_base.sistema, ns, ks), archivo=f"oscilador_limite_clasico_n{n}.png")
    with st.expander("Interpretación física", expanded=True):
        st.markdown(
            "- **Clásicamente** la partícula pasa más tiempo donde va más despacio: cerca de los puntos de retorno ±A. "
            "Por eso P(x) = 1/(π√(A² − x²)) es mínima en el centro y diverge en los bordes.\n"
            "- **Cuánticamente**, para n pequeño ocurre lo contrario (n = 0 es máximo en el centro) y hay probabilidad "
            "fuera de ±A (efecto túnel).\n"
            "- Al crecer n, |ψₙ|² oscila cada vez más rápido y su **promedio local** sigue a la curva clásica: es el "
            "**principio de correspondencia**. Como P_clásica diverge en ±A, la comparación cuantitativa se hace con "
            "las probabilidades acumuladas (panel central), cuya máxima diferencia D disminuye con n.")


@st.cache_data(show_spinner="Calculando la animación…", max_entries=10)
def _animacion_cacheada(modo, n1, n2, peso, fase, masa, omega, sistema, rango, n_cuadros):
    p = ParametrosOscilador(0, masa, omega, sistema, rango, 2001, "numerica")
    if modo == "estacionario":
        numeros, coef, titulo = [n1], np.array([1.0 + 0j]), f"estado estacionario n = {n1}"
    else:
        numeros, coef = [n1, n2], coeficientes_dos_estados(peso, fase)
        titulo = f"superposición de n = {n1} y n = {n2}"
    x, taus, re, im, rho, x_medio = serie_dinamica(p, numeros, coef, n_cuadros)
    et = _et(sistema)
    u = et["u"]
    etiquetas = [f"τ = ωt = {t:.2f} (t = {t / omega / u['factor_tiempo']:.3g} {u['nombre_tiempo']})" for t in taus]
    return figura_dinamica(x / et["fx"], taus, re * np.sqrt(et["fx"]), im * np.sqrt(et["fx"]), rho * et["fx"],
                           x_medio / et["fx"], et["L"], etiquetas, titulo)


def _pestana_dinamica(p_base: ParametrosOscilador):
    with st.container(border=True):
        qc.seccion("Estado inicial")
        modo = st.radio("Qué animar", ["Superposición n₁ + n₂", "Estado estacionario único (fase global)"],
                        horizontal=True, key="osc_dyn_modo")
        c1, c2, c3, c4 = st.columns(4)
        n1 = c1.number_input("n₁", min_value=0, max_value=30, step=1, key="osc_dyn_n1")
        n2 = c2.number_input("n₂", min_value=0, max_value=30, step=1, key="osc_dyn_n2")
        peso = c3.slider("Peso |c₂|² del segundo estado", 0.0, 1.0, step=0.05, key="osc_dyn_peso")
        fase = c4.slider("Fase relativa φ [rad]", -float(np.pi), float(np.pi), step=float(np.pi / 12), format="%.3f",
                         key="osc_dyn_fase")
    estacionario = modo.startswith("Estado")
    if not estacionario and n1 == n2:
        qc.error("Elige dos números cuánticos distintos (n₁ ≠ n₂).")
        return
    try:
        _con_n(p_base, max(n1, n2))
    except ValueError as error:
        qc.error(error)
        return
    u = qc.obtener_unidades(p_base.sistema)
    if estacionario:
        qc.nota("**Estado estacionario.** La función de onda compleja gira en el plano complejo: Re Ψ e Im Ψ "
                "oscilan en el tiempo. Pero es solo una **fase global** e^{−iEₙt/ħ}; la densidad |Ψ|² (curva "
                "inferior) **no cambia** y ⟨x⟩ permanece en 0. La oscilación de Re Ψ no significa que la partícula "
                "se mueva.")
    else:
        t_rho = 2 * np.pi / (p_base.omega * abs(int(n2) - int(n1)))
        qc.nota(f"**Superposición.** La densidad cambia por la interferencia entre estados de energías distintas "
                f"(frecuencia |n₂−n₁|ω) y se repite cada Δτ = 2π/|n₂−n₁| = {2 * np.pi / abs(int(n2) - int(n1)):.3f} "
                f"(T = {t_rho / u['factor_tiempo']:.4g} {u['nombre_tiempo']}). Para (|0⟩+|1⟩)/√2, ⟨x⟩ oscila como "
                f"x₀ cos(ωt)/√2: es el movimiento del paquete, no de una fase global.")
    qc.seccion("Animación")
    figura = _animacion_cacheada("estacionario" if estacionario else "superposicion", int(n1), int(n2), float(peso),
                                 float(fase), p_base.masa, p_base.omega, p_base.sistema, p_base.rango, 72)
    qc.mostrar_plotly(figura, clave="osc_anim", archivo="oscilador_dinamica.html")
    st.caption("Animación en el navegador: «Reproducir», «Pausa» y deslizador. Un periodo completo τ ∈ [0, 2π).")


def _pestana_ecuaciones():
    qc.seccion("Modelo")
    st.latex(r"V(x)=\tfrac12 m\omega^2x^2\qquad x_0=\sqrt{\frac{\hbar}{m\omega}}\qquad E_n=\hbar\omega\left(n+\tfrac12\right)")
    st.latex(r"\left[-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}+\tfrac12 m\omega^2x^2\right]\psi_n=E_n\psi_n")
    st.latex(r"\psi_n(x)=\frac{1}{\sqrt{2^n n!}}\frac{1}{\pi^{1/4}\sqrt{x_0}}H_n\!\left(\frac{x}{x_0}\right)e^{-x^2/2x_0^2}")
    qc.seccion("Densidades de energía")
    st.latex(r"u_V(x)=V(x)\,|\psi_n(x)|^2\qquad u_T(x)=\frac{\hbar^2}{2m}\left|\frac{d\psi_n}{dx}\right|^2\qquad E_n=\int(u_T+u_V)\,dx")
    st.latex(r"\langle T\rangle=\langle V\rangle=\frac{E_n}{2}\qquad \langle x\rangle=0\qquad \langle x^2\rangle=\left(n+\tfrac12\right)x_0^2")
    st.latex(r"\psi_n'(x)=\frac{1}{x_0}\left[\sqrt{\tfrac n2}\,\psi_{n-1}-\sqrt{\tfrac{n+1}{2}}\,\psi_{n+1}\right]")
    qc.seccion("Dinámica")
    st.latex(r"x_n^{\rm retorno}=\pm\sqrt{2n+1}\,x_0\qquad \Psi(x,t)=\sum_n c_n\psi_n(x)e^{-i(n+1/2)\omega t}")
    qc.seccion("Límite clásico")
    st.latex(r"A=\sqrt{2n+1}\,x_0,\qquad P_{\rm cl}(x)=\frac{1}{\pi\sqrt{A^2-x^2}},\qquad F_{\rm cl}(x)=\frac12+\frac{1}{\pi}\arcsin\frac{x}{A}")
    st.latex(r"D=\max_x\left|F_{\rm cuántica}(x)-F_{\rm cl}(x)\right|\ \xrightarrow[n\to\infty]{}\ 0,\qquad \langle x^2\rangle_{\rm cl}=\frac{A^2}{2}=\left(n+\tfrac12\right)x_0^2")
    st.markdown("**V(x)** (energía por unidad de probabilidad, en energía) no debe confundirse con **u_V(x)** "
                "(densidad de energía potencial, en energía/longitud).")


def interfaz() -> None:
    """Página completa del simulador 2 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 02", "Oscilador armónico cuántico",
                         "Estados de Hermite, densidades de energía cinética y potencial, teorema del virial "
                         "y dinámica de superposiciones.")
    p_base = _leer_parametros_fisicos()
    if p_base is None:
        return
    tabs = st.tabs(["Estado individual", "Niveles y potencial", "Comparación de estados", "Límite clásico",
                    "Dinámica", "Ecuaciones", "Guía de práctica", "Autoevaluación", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_individual(p_base)
    with tabs[1]:
        _pestana_niveles(p_base)
    with tabs[2]:
        _pestana_comparacion(p_base)
    with tabs[3]:
        _pestana_limite_clasico(p_base)
    with tabs[4]:
        _pestana_dinamica(p_base)
    with tabs[5]:
        _pestana_ecuaciones()
    with tabs[6]:
        qc.guia_practica(GUIA, "osc")
    with tabs[7]:
        qc.autoevaluacion(PREGUNTAS, "osc")
    with tabs[8]:
        qc.boton_pruebas(ejecutar_pruebas, "osc_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Oscilador armónico", ":material/science:", "oscilador_armonico.py")
