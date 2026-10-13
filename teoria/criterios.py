"""
teoria/criterios.py — Teoría: ¿Por qué y cuándo usar la mecánica cuántica?
"""

import math

import numpy as np
import streamlit as st

import quantum_lab_comun as qc
from teoria._util import COL, EV, H, KB, ME, cifras, figura, dibujar

U_MASA = 1.66053906660e-27
CM1_A_EV = 1.239841984e-4              # 1 cm⁻¹ en eV
KJMOL_A_EV = 1000 / 6.02214076e23 / EV


def kT_ev(T: float) -> float:
    return KB * T / EV


def razon_de_poblaciones(delta_e_ev: float, T: float, g_i: int = 1, g_j: int = 1) -> float:
    """n_i / n_j = (g_i / g_j) · exp(−ΔE / kT), con ε_i > ε_j y ΔE = ε_i − ε_j."""
    x = delta_e_ev / kT_ev(T)
    return (g_i / g_j) * math.exp(-x) if x < 700 else 0.0


def espaciado_traslacional_ev(masa: float, L: float) -> float:
    """Diferencia entre los dos primeros niveles de una partícula en una caja de longitud L: 3h²/(8mL²)   [eV]."""
    return 3 * H ** 2 / (8 * masa * L ** 2) / EV


def mostrar() -> None:
    sub = st.tabs(["Por qué estudiarla", "Criterio 1: longitud de onda", "Criterio 2: espaciado de energía",
                   "Resumen"])
    with sub[0]:
        qc.seccion("Un conocimiento básico del químico")
        st.markdown(
            "La química describe cómo se ordenan y reaccionan los átomos, y esa descripción depende de cómo se comportan "
            "los electrones. La mecánica cuántica predice que átomos y moléculas solo pueden tener **energías discretas**, y "
            "con ello explica de forma unificada las espectroscopías: infrarroja, de resonancia magnética nuclear y de "
            "rayos X permiten identificar compuestos e incluso obtener imágenes de órganos y huesos.")
        st.markdown("Gran parte de la tecnología actual se apoya en ella:")
        st.markdown("- fabricación de circuitos integrados;\n- cálculo de propiedades químicas de moléculas de interés "
                    "farmacéutico;\n- computación cuántica, un área de investigación muy activa.")
        st.markdown(
            "La teoría no nació en el vacío: surgió de la tensión entre experimentos que la física clásica no podía explicar "
            "(radiación del cuerpo negro, efecto fotoeléctrico, espectros atómicos, difracción de electrones) y las "
            "ideas nuevas que los explicaban. Los primeros temas del curso recorren esos experimentos.")
    with sub[1]:
        qc.seccion("¿Es comparable la longitud de onda con el tamaño del problema?")
        st.markdown(
            "La luz de longitud de onda λ que atraviesa una rendija de ancho a se describe bien con rayos mientras λ ≪ a. "
            "La difracción solo se nota cuando λ es comparable con a. Con partículas ocurre lo mismo, con "
            "λ = h/p. **No hay una frontera nítida** entre «partícula» y «onda»: lo que importa es la razón λ/a.")
        qc.seccion("Calculadora")
        opciones = {"Electrón": ME, "Átomo de helio": 4.002602 * U_MASA, "Molécula de N₂": 28.0134 * U_MASA,
                    "Mota de polvo (1 µg)": 1e-9}
        c1, c2, c3 = st.columns(3)
        with c1:
            nombre = st.selectbox("Partícula", list(opciones), key="cr_part")
        with c2:
            v0 = {"Electrón": 1e6, "Átomo de helio": 1e3, "Molécula de N₂": 500.0, "Mota de polvo (1 µg)": 1e-3}[nombre]
            v = st.number_input("Velocidad [m/s]", 1e-6, 1e7, v0, format="%.4g", key=f"cr_v_{nombre}")
        with c3:
            a_nm = st.number_input("Tamaño del sistema a [nm]", 1e-3, 1e9, 0.3, format="%.4g", key="cr_a")
        lam = H / (opciones[nombre] * v)
        razon = lam / (a_nm * 1e-9)
        qc.metricas([("λ de De Broglie", f"{lam * 1e9:.4g} nm"), ("λ / a", f"{razon:.3g}")], columnas=2)
        if razon < 0.01:
            st.info("λ ≪ a: la mecánica clásica describe bien el movimiento.", icon=":material/info:")
        elif razon < 100:
            st.success("λ comparable con a: hay que usar la mecánica cuántica (difracción, niveles discretos).",
                       icon=":material/check_circle:")
        else:
            st.success("λ ≫ a: régimen fuertemente cuántico (confinamiento).", icon=":material/check_circle:")
        st.caption("Los umbrales 0.01 y 100 son orientativos: no existe un límite exacto.")
    with sub[2]:
        qc.seccion("¿Qué tan seguidos están los niveles de energía?")
        st.markdown(
            "El segundo criterio compara el espaciado ΔE entre niveles con la energía térmica disponible, kT. La "
            "distribución de Boltzmann da la proporción de átomos o moléculas en dos niveles:")
        st.latex(r"\frac{n_i}{n_j}=\frac{g_i}{g_j}\,e^{-(\varepsilon_i-\varepsilon_j)/k_BT},\qquad \Delta E=\varepsilon_i-\varepsilon_j")
        st.markdown("donde g es la degeneración de cada nivel. kT tiene unidades de energía y es, aproximadamente, la "
                    "energía media por partícula a la temperatura T.")
        st.markdown(
            "- Si **ΔE ≫ kT**, el nivel superior está casi vacío: la distribución es muy distinta de la clásica "
            "(continua) y hay que usar mecánica cuántica.\n"
            "- Si **ΔE ≲ kT**, muchos niveles están poblados y los resultados cuántico y clásico se parecen.")
        qc.seccion("Calculadora de poblaciones")
        c1, c2, c3 = st.columns(3)
        with c1:
            T = st.slider("Temperatura T [K]", 10, 5000, 298, 1, key="cr_T")
        with c2:
            unidad = st.selectbox("Unidad de ΔE", ["eV", "cm⁻¹", "kJ/mol"], key="cr_u")
        with c3:
            valor = st.number_input(f"ΔE [{unidad}]", 1e-12, 1e7, 0.5 if unidad == "eV" else (4000.0 if unidad == "cm⁻¹" else 50.0),
                                    format="%.6g", key="cr_dE")
        c4, c5 = st.columns(2)
        with c4:
            g_i = st.number_input("Degeneración del nivel superior g_i", 1, 100, 1, key="cr_gi")
        with c5:
            g_j = st.number_input("Degeneración del nivel inferior g_j", 1, 100, 1, key="cr_gj")
        dE = valor * {"eV": 1.0, "cm⁻¹": CM1_A_EV, "kJ/mol": KJMOL_A_EV}[unidad]
        x = dE / kT_ev(T)
        qc.metricas([("kT", f"{kT_ev(T):.4g} eV"), ("ΔE", f"{dE:.4g} eV"), ("ΔE / kT", f"{x:.4g}"),
                     ("n_i / n_j", f"{razon_de_poblaciones(dE, T, int(g_i), int(g_j)):.4g}")], columnas=4)
        if x > 3:
            st.success("ΔE ≫ kT: el comportamiento es claramente cuántico (el nivel superior casi no se puebla).",
                       icon=":material/check_circle:")
        elif x < 0.3:
            st.info("ΔE ≪ kT: muchos niveles poblados, el sistema se comporta de forma casi clásica.", icon=":material/info:")
        else:
            st.warning("ΔE ≈ kT: zona intermedia; ambos niveles tienen población apreciable.", icon=":material/info:")
        fig, ax = figura(8.5, 3.8)
        xs = np.linspace(0, 12, 400)
        ax.plot(xs, np.exp(-xs), color=COL["densidad"], lw=2.4)
        ax.axvline(x if x <= 12 else 12, color=COL["energia"], ls="--", lw=1.6, label=f"ΔE/kT = {x:.3g}")
        ax.set_xlabel("ΔE / kT")
        ax.set_ylabel("n_i / n_j  (g_i = g_j)")
        ax.set_yscale("log")
        ax.set_title("Población relativa del nivel superior")
        ax.legend()
        dibujar(fig, "boltzmann.png")
        qc.seccion("Órdenes de magnitud a 298 K")
        trasl = espaciado_traslacional_ev(28.0134 * U_MASA, 1e-2)
        qc.tabla_libre([
            {"Tipo de movimiento": "Electrónico", "ΔE típico [eV]": "1 – 10", "ΔE / kT (298 K)": "≈ 40 – 400",
             "Conclusión": "estrictamente cuántico"},
            {"Tipo de movimiento": "Vibracional", "ΔE típico [eV]": "0.05 – 0.5", "ΔE / kT (298 K)": "≈ 2 – 20",
             "Conclusión": "cuántico"},
            {"Tipo de movimiento": "Rotacional", "ΔE típico [eV]": "≈ 10⁻³", "ΔE / kT (298 K)": "≈ 0.04",
             "Conclusión": "casi clásico"},
            {"Tipo de movimiento": "Traslacional (N₂, caja de 1 cm)", "ΔE típico [eV]": cifras(trasl, 2),
             "ΔE / kT (298 K)": cifras(trasl / kT_ev(298), 2), "Conclusión": "clásico"},
        ])
        st.caption("Valores aproximados; el espaciado traslacional se calcula con 3h²/8mL² para el N₂.")
    with sub[3]:
        qc.seccion("Resumen")
        qc.tabla_libre([
            {"Criterio": "1. Longitud de onda", "Se compara": "λ = h/p con el tamaño a del sistema",
             "Clásico si": "λ ≪ a", "Cuántico si": "λ ≳ a"},
            {"Criterio": "2. Espaciado de energía", "Se compara": "ΔE con kT",
             "Clásico si": "ΔE ≲ kT", "Cuántico si": "ΔE ≫ kT"},
        ])
        st.latex(r"\frac{n_i}{n_j}=\frac{g_i}{g_j}\,e^{-\Delta E/k_BT}")


PREGUNTAS = [
    {"enunciado": "Para un par de niveles con ΔE/kT = 10 y degeneraciones iguales, la razón de poblaciones n_i/n_j es aproximadamente...",
     "opciones": ["4.5 × 10⁻⁵", "0.9", "1", "10"],
     "correcta": 0, "explicacion": "n_i/n_j = e^(−10) ≈ 4.5 × 10⁻⁵: el nivel superior está prácticamente vacío."},
    {"enunciado": "Los resultados clásico y cuántico se parecen cuando...",
     "opciones": ["ΔE ≫ kT", "ΔE ≲ kT", "T = 0", "λ ≫ a"],
     "correcta": 1, "explicacion": "Si el espaciado es pequeño frente a kT hay muchos niveles poblados y el espectro se ve «continuo»."},
    {"enunciado": "La difracción de una onda en una rendija de ancho a se observa claramente cuando...",
     "opciones": ["λ ≪ a", "λ es comparable con a", "λ = 0", "a es muy grande"],
     "correcta": 1, "explicacion": "Si λ ≪ a se cumple la óptica de rayos; la difracción aparece cuando λ ~ a."},
    {"enunciado": "¿Qué representa kT?",
     "opciones": ["Una energía del orden de la energía térmica media por partícula",
                  "La constante de Planck por la temperatura",
                  "La temperatura en julios por segundo", "La energía del estado fundamental"],
     "correcta": 0, "explicacion": "kT tiene unidades de energía y es aproximadamente la energía térmica media por partícula."},
    {"enunciado": "¿Por qué la traslación de un gas en un recipiente macroscópico se trata clásicamente?",
     "opciones": ["Porque los niveles están extremadamente juntos frente a kT",
                  "Porque no tiene energía", "Porque no hay partículas", "Porque el gas no tiene masa"],
     "correcta": 0, "explicacion": "Los espaciados son ~10⁻¹⁹ eV, mucho menores que kT ≈ 0.026 eV a 298 K."},
]
