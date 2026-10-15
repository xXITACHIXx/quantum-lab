"""
teoria/de_broglie.py — Teoría: Partículas con comportamiento ondulatorio
"""

import math

import numpy as np
import streamlit as st

import quantum_lab_comun as qc
from teoria._util import COL, EV, H, HBAR, ME, figura, dibujar

U_MASA = 1.66053906660e-27          # kg
PARTICULAS = {
    "Electrón": ME,
    "Protón": 1.67262192369e-27,
    "Neutrón": 1.67492749804e-27,
    "Átomo de helio": 4.002602 * U_MASA,
    "Molécula de N₂": 28.0134 * U_MASA,
    "Pelota de béisbol (0.145 kg)": 0.145,
}


def longitud_de_onda(masa: float, velocidad: float) -> float:
    """λ = h / (m v)   [m]."""
    return H / (masa * velocidad)


def lambda_desde_energia(masa: float, energia_J: float) -> float:
    """λ = h / √(2 m E) para una partícula libre no relativista   [m]."""
    return H / math.sqrt(2 * masa * energia_J)


def energia_para_lambda(masa: float, lam: float) -> float:
    """E = h² / (2 m λ²)   [J]."""
    return H ** 2 / (2 * masa * lam ** 2)


def _formato_longitud(lam: float) -> str:
    if lam >= 1e-9:
        return f"{lam * 1e9:.4g} nm"
    if lam >= 1e-12:
        return f"{lam * 1e12:.4g} pm"
    return f"{lam:.3e} m"


def mostrar() -> None:
    sub = st.tabs(["La hipótesis", "Confirmación experimental", "Ondas estacionarias y Bohr", "Calculadora"])
    with sub[0]:
        qc.seccion("Si la luz es onda y partícula, ¿y la materia?")
        st.markdown(
            "El efecto fotoeléctrico mostró que la luz, una onda, se comporta también como partículas de energía hν y "
            "momento p = h/λ. En 1924 Louis de Broglie propuso la simetría opuesta: **toda partícula con momento p tiene "
            "asociada una onda de longitud**")
        st.latex(r"\lambda=\frac{h}{p}=\frac{h}{mv}")
        st.markdown(
            "La constante de Planck es tan pequeña que esta longitud de onda es inimaginablemente pequeña para objetos "
            "cotidianos y apreciable solo para partículas ligeras: electrones, neutrones, átomos, moléculas pequeñas.")
        st.markdown("Para una partícula libre con energía cinética E = p²/2m, la longitud de onda también se escribe")
        st.latex(r"\lambda=\frac{h}{\sqrt{2mE}}")
        st.markdown("Para un electrón acelerado por una diferencia de potencial V (en voltios) es muy útil recordar que "
                    "λ ≈ 1.226 nm / √V.")
    with sub[1]:
        qc.seccion("Davisson y Germer (1927)")
        st.markdown(
            "Si los electrones son ondas, deben **difractarse** en una red cuyo espaciado sea comparable con su λ. En "
            "1927 Clinton Davisson y Lester Germer dispararon electrones de 54 eV contra un cristal de níquel y "
            "encontraron un máximo muy marcado de electrones dispersados a unos 50° respecto del haz incidente.")
        lam = lambda_desde_energia(ME, 54 * EV)
        d_ni = 0.215e-9
        lam_exp = d_ni * math.sin(math.radians(50))
        st.markdown("La comparación es notable:")
        qc.tabla_libre([
            {"Cantidad": "λ de De Broglie para 54 eV", "Valor": f"{lam * 1e9:.4f} nm"},
            {"Cantidad": "λ deducida del máximo de difracción (d = 0.215 nm, 50°)", "Valor": f"{lam_exp * 1e9:.4f} nm"},
        ], numericas=("Valor",))
        st.markdown(
            "Coinciden dentro de un pequeño error. Ese experimento confirmó que la materia presenta difracción, un "
            "fenómeno ondulatorio. Desde entonces se ha observado también con neutrones, átomos y moléculas, y se usa "
            "en técnicas de análisis de superficies y estructuras.")
        st.info("Difracción: cambio en la dirección y la intensidad de una onda al pasar por una abertura o una red de "
                "tamaño parecido a su longitud de onda.", icon=":material/info:")
    with sub[2]:
        qc.seccion("De Broglie y el modelo de Bohr")
        st.markdown(
            "De Broglie dio una interpretación a la condición que Bohr había postulado: un electrón en órbita es como una "
            "onda en un anillo. Solo hay interferencia constructiva (una onda estacionaria) si la circunferencia contiene "
            "un **número entero** de longitudes de onda; si no, la onda se cancela a sí misma tras cada vuelta.")
        st.latex(r"2\pi r=n\lambda=n\frac{h}{m_ev}\ \Rightarrow\ m_evr=n\hbar,\qquad n=1,2,3,\dots")
        n = st.slider("Longitudes de onda en la circunferencia", 1.0, 8.0, 3.0, 0.5, key="db_n")
        theta = np.linspace(0, 2 * np.pi, 1500)
        entero = abs(n - round(n)) < 1e-9
        r = 1 + 0.12 * np.cos(n * theta)
        fig, ax = figura(5.2, 5.2)
        ax.plot(np.cos(theta), np.sin(theta), color=COL["gris"], lw=0.8, ls=":")
        ax.plot(r * np.cos(theta), r * np.sin(theta), color=COL["cinetica"] if entero else COL["energia"], lw=2.4)
        ax.plot(0, 0, "o", color=COL["densidad"], ms=7)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title("Órbita permitida: la onda se cierra" if entero else "Órbita no permitida: la onda no se cierra")
        dibujar(fig, "debroglie_orbita.png")
        st.caption("En el caso no entero se ve el salto donde la onda debería empalmar consigo misma.")
    with sub[3]:
        qc.seccion("Calcular la longitud de onda de una partícula")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.selectbox("Partícula", list(PARTICULAS), key="db_part")
            modo = st.radio("Dato conocido", ["Velocidad", "Energía cinética"], horizontal=True, key="db_modo")
        masa = PARTICULAS[nombre]
        with c2:
            if modo == "Velocidad":
                v = st.number_input("Velocidad [m/s]", min_value=1e-6, max_value=2.9e7, value=1.0e6 if masa < 1e-20 else 40.0,
                                    format="%.6g", key=f"db_v_{nombre}")
                lam = longitud_de_onda(masa, v)
                energia = 0.5 * masa * v ** 2
            else:
                e_ev = st.number_input("Energía cinética [eV]", min_value=1e-9, max_value=1e6, value=54.0, format="%.6g", key="db_e")
                energia = e_ev * EV
                lam = lambda_desde_energia(masa, energia)
                v = math.sqrt(2 * energia / masa)
        qc.metricas([("Longitud de onda λ", _formato_longitud(lam)), ("Velocidad", f"{v:.4g} m/s"),
                     ("Energía cinética", f"{energia / EV:.4g} eV"), ("Momento p", f"{masa * v:.4g} kg·m/s")],
                    columnas=4)
        referencia = [("un átomo (≈ 0.1 nm)", 1e-10), ("el espaciado de una red cristalina (≈ 0.3 nm)", 3e-10)]
        for texto, tam in referencia:
            st.markdown(f"- λ / tamaño de {texto} = **{lam / tam:.3g}**")
        if lam < 1e-12:
            st.warning("La longitud de onda es mucho menor que cualquier estructura de la escala atómica: no hay "
                       "efectos ondulatorios observables. Se comporta como una partícula clásica.", icon=":material/info:")
        elif lam < 1e-9:
            st.success("Longitud de onda comparable con las distancias atómicas: se puede observar difracción en cristales.",
                       icon=":material/check_circle:")
        qc.seccion("Problema inverso: energía necesaria para una λ dada")
        lam_nm = st.number_input("Longitud de onda deseada [nm]", min_value=1e-4, max_value=100.0, value=0.25, format="%.4g",
                                 key="db_lam")
        e = energia_para_lambda(ME, lam_nm * 1e-9)
        st.markdown(f"Un electrón con λ = {lam_nm:.4g} nm necesita una energía cinética de "
                    f"**{e:.4g} J = {e / EV:.4g} eV**, es decir, un potencial acelerador de unos {e / EV:.4g} V.")


PREGUNTAS = [
    {"enunciado": "Según De Broglie, la longitud de onda de una partícula es...",
     "opciones": ["λ = h·p", "λ = h/p", "λ = p/h", "λ = hν"],
     "correcta": 1, "explicacion": "λ = h/p = h/(mv): cuanto mayor el momento, menor la longitud de onda."},
    {"enunciado": "Si se duplica la velocidad de un electrón (no relativista), su longitud de onda...",
     "opciones": ["se duplica", "se reduce a la mitad", "queda igual", "se cuadruplica"],
     "correcta": 1, "explicacion": "λ = h/(mv) es inversamente proporcional a v."},
    {"enunciado": "¿Por qué no se observa la difracción de una pelota de béisbol?",
     "opciones": ["Porque no tiene carga", "Porque su longitud de onda es inmensamente menor que cualquier abertura real",
                  "Porque la constante de Planck no se aplica a objetos grandes", "Porque se mueve muy despacio"],
     "correcta": 1, "explicacion": "Con m ≈ 0.145 kg, λ ~ 10⁻³⁴ m: no hay estructura comparable en la que difractarse."},
    {"enunciado": "El experimento de Davisson y Germer mostró que...",
     "opciones": ["los electrones se difractan en un cristal", "la luz tiene masa", "el átomo tiene núcleo",
                  "la energía del electrón es continua"],
     "correcta": 0, "explicacion": "El máximo de electrones dispersados confirmó la naturaleza ondulatoria del electrón."},
    {"enunciado": "La condición 2πr = nλ aplicada a la órbita del electrón en el hidrógeno conduce a...",
     "opciones": ["mvr = nħ", "E = hν", "p = h/λ solamente", "ΔxΔp ≥ ħ/2"],
     "correcta": 0, "explicacion": "Sustituyendo λ = h/(mv) se obtiene mvr = nh/2π = nħ, la cuantización del momento angular de Bohr."},
]
