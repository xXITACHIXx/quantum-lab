"""
quantum_lab.py — QUANTUM LAB · menú principal
=============================================

Laboratorio interactivo de mecánica cuántica con seis simuladores independientes:

    particula_caja.py       Partícula en una caja 1D (estados, superposición e interferencia)
    oscilador_armonico.py   Oscilador armónico cuántico 1D (energías, virial, límite clásico, dinámica)
    particula_esfera.py     Armónicos esféricos y partícula en una esfera
    efecto_fotoelectrico.py Efecto fotoeléctrico (ecuación de Einstein, determinación de h)
    modelo_bohr.py          Átomo de hidrógeno: modelo de Bohr y átomo cuántico en 3D
    principio_incertidumbre.py  Principio de incertidumbre de Heisenberg (paquetes de ondas, dispersión, rendija)

Ejecución:      streamlit run quantum_lab.py
Cada simulador también funciona por separado:  streamlit run particula_caja.py   (etc.)
Pruebas:        python quantum_lab.py     (ejecuta las pruebas de todos los módulos)
"""

from __future__ import annotations

import sys

import streamlit as st

import quantum_lab_comun as qc
import efecto_fotoelectrico
import modelo_bohr
import oscilador_armonico
import particula_caja
import particula_esfera
import principio_incertidumbre
import teoria
import verificacion

# Páginas: clave → (título en la barra lateral, icono monocromo, módulo o None)
PAGINAS = {
    "inicio": ("Inicio", ":material/home:", None),
    "caja": ("Partícula en una caja", ":material/check_box_outline_blank:", particula_caja),
    "oscilador": ("Oscilador armónico", ":material/airwave:", oscilador_armonico),
    "esfera": ("Partícula en una esfera", ":material/language:", particula_esfera),
    "fotoelectrico": ("Efecto fotoeléctrico", ":material/wb_incandescent:", efecto_fotoelectrico),
    "bohr": ("Átomo de hidrógeno", ":material/radio_button_checked:", modelo_bohr),
    "incertidumbre": ("Principio de incertidumbre", ":material/blur_on:", principio_incertidumbre),
    "teoria": ("Centro de teoría", ":material/menu_book:", teoria),
    "verificacion": ("Verificación", ":material/verified:", verificacion),
    "pruebas": ("Pruebas numéricas", ":material/fact_check:", None),
}
GRUPOS = [
    ("Mecánica cuántica", ["caja", "oscilador", "esfera"], True),
    ("Fundamentos", ["fotoelectrico", "bohr", "incertidumbre"], True),
    ("Teoría y verificación", ["teoria", "verificacion", "pruebas"], True),
]


def _ir_a(pagina: str) -> None:
    """Callback de navegación."""
    st.session_state["ql_pagina"] = pagina


def ejecutar_todas_las_pruebas() -> list[qc.RegistroPruebas]:
    return [m.ejecutar_pruebas() for m in (particula_caja, oscilador_armonico, particula_esfera,
                                            efecto_fotoelectrico, modelo_bohr, principio_incertidumbre, teoria, verificacion)]


# ---------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------
def _boton_nav(clave: str) -> None:
    titulo, icono, _ = PAGINAS[clave]
    activa = st.session_state["ql_pagina"] == clave
    st.button(titulo, key=f"nav_{clave}", icon=icono, type="primary" if activa else "secondary",
              on_click=_ir_a, args=(clave,), width="stretch")


def _barra_lateral() -> None:
    with st.sidebar:
        st.markdown('<div class="ql-marca"><div class="ql-marca-nombre">Quantum Lab</div>'
                    '<div class="ql-marca-sub">Mecánica cuántica</div></div>', unsafe_allow_html=True)
        _boton_nav("inicio")
        actual = st.session_state["ql_pagina"]
        for titulo, claves, abierto in GRUPOS:
            with st.expander(titulo, expanded=abierto or actual in claves):
                for clave in claves:
                    _boton_nav(clave)
        st.markdown("")
        qc.interruptor_movil()
        st.markdown('<div class="ql-pie">Cálculo con NumPy y SciPy.<br>La dirección de la página guarda la '
                    f'configuración: cópiala para compartirla.<br><br>Versión {qc.VERSION} · 6 simuladores</div>',
                    unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------
TARJETAS = [
    ("caja", "Simulador 01", "Partícula en una caja",
     "Estados estacionarios, energías, longitud de onda de De Broglie y nodos. Superposición e "
     "interferencia dependientes del tiempo.", "Eₙ = n²π²ħ² / 2ma²"),
    ("oscilador", "Simulador 02", "Oscilador armónico",
     "Polinomios de Hermite, densidades de energía cinética y potencial, teorema del virial, "
     "efecto túnel y dinámica de superposiciones.", "Eₙ = ħω (n + ½)"),
    ("esfera", "Simulador 03", "Partícula en una esfera",
     "Armónicos esféricos en 3D, nodos y simetrías, orbitales complejos frente a reales y un modelo "
     "confinado con funciones de Bessel.", "L² Yₗᵐ = ħ² l(l+1) Yₗᵐ"),
    ("fotoelectrico", "Simulador 04", "Efecto fotoeléctrico",
     "Frecuencia umbral, energía de los electrones emitidos, corriente fotoeléctrica y determinación "
     "de la constante de Planck al estilo de Millikan.", "Kₘₐₓ = hν − Φ"),
    ("bohr", "Simulador 05", "Átomo de hidrógeno",
     "Modelo de Bohr: niveles, transiciones y series espectrales. Átomo cuántico en 3D: nubes de "
     "probabilidad que se construyen medida a medida.", "Eₙ = −13.6 eV / n²"),
    ("incertidumbre", "Simulador 06", "Principio de incertidumbre",
     "Paquetes de ondas en posición y momento, el límite de Heisenberg, el ensanchamiento de una "
     "partícula libre y la difracción por una rendija.", "Δx · Δp ≥ ħ / 2"),
]


def _pagina_inicio() -> None:
    st.markdown(
        '<div class="ql-portada"><p class="ql-etiqueta">Laboratorio interactivo de mecánica cuántica</p>'
        '<div class="ql-titulo">Quantum Lab</div>'
        '<p class="ql-subtitulo">Funciones de onda, energías, densidades de probabilidad, interferencia y armónicos '
        'esféricos a partir de parámetros físicos reales. Cada resultado se acompaña de su comprobación numérica.</p></div>',
        unsafe_allow_html=True)
    for titulo_grupo, desde, hasta in (("Mecánica cuántica", 0, 3), ("Orígenes y fundamentos", 3, 6)):
        qc.seccion(titulo_grupo)
        columnas = st.columns(3)
        for col, (clave, etiqueta, titulo, texto, ecuacion) in zip(columnas, TARJETAS[desde:hasta]):
            with col:
                st.markdown(f'<div class="ql-card"><p class="ql-etiqueta">{etiqueta}</p><h3>{titulo}</h3>'
                            f'<p>{texto}</p><div class="ql-ecuacion">{ecuacion}</div></div>', unsafe_allow_html=True)
                st.button("Abrir simulador", key=f"ql_abrir_{clave}", on_click=_ir_a, args=(clave,),
                          icon=":material/arrow_forward:", width="stretch")
    qc.seccion("Teoría del curso")
    st.markdown("El **Centro de teoría** reúne en un solo lugar la teoría de cada tema, con enlaces a su simulador, "
                "experimentos guiados y autoevaluación. Los temas que el curso aún no cubre ya tienen su lugar.")
    st.button("Abrir el Centro de teoría", key="ql_abrir_teoria", on_click=_ir_a, args=("teoria",),
              icon=":material/menu_book:")
    st.markdown("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        qc.seccion("Uso")
        st.markdown("1. Elige un simulador o el **Centro de teoría** en la barra lateral o en las tarjetas.\n"
                    "2. Ajusta los **parámetros del sistema** en el panel superior; los resultados se recalculan al instante.\n"
                    "3. Recorre las **pestañas**: resultados, visualización, valores detallados e interpretación.\n"
                    "4. «Configuración de ejemplo» carga casos típicos; «Restaurar valores iniciales» vuelve al comienzo.\n"
                    "5. **Ver la teoría de este tema** abre su explicación; **Guía de práctica** propone experimentos con predicción y resultado; **Autoevaluación** "
                    "corrige preguntas de opción múltiple; **Pruebas numéricas** verifica los cálculos.\n"
                    "6. Las gráficas y tablas se pueden **descargar** (PNG, HTML o CSV) y «Compartir configuración» "
                    "da un enlace con los parámetros exactos.")
    with c2:
        qc.seccion("Alcance del modelo")
        st.markdown("- Las **fórmulas** (ψₙ, Eₙ, Hermite, Yₗᵐ…) son exactas; las **integrales y derivadas** se calculan "
                    "en mallas numéricas con el error documentado en cada simulador.\n"
                    "- Las deformaciones y «lóbulos» de la esfera son recursos geométricos, no objetos físicos.\n"
                    "- Herramienta **educativa**: una partícula, sin espín ni interacciones; no describe átomos reales.")


def _pagina_pruebas() -> None:
    qc.encabezado_pagina("Verificación", "Pruebas numéricas globales",
                         "Comprobaciones de los seis simuladores y de la página de verificación. También se ejecutan con «python quantum_lab.py» o con pytest.")
    if st.button("Ejecutar todas las pruebas", type="primary", icon=":material/play_arrow:"):
        with st.spinner("Calculando…"):
            registros = ejecutar_todas_las_pruebas()
        qc.metricas([(reg.nombre, f"{sum(x['ok'] for x in reg.resultados)} / {len(reg.resultados)}") for reg in registros],
                    columnas=3)
        for reg in registros:
            with st.expander(f"Detalle · {reg.nombre}", expanded=not reg.todo_ok()):
                st.dataframe(reg.tabla(), hide_index=True, width="stretch")


def main() -> None:
    st.set_page_config(page_title="Quantum Lab", page_icon=":material/science:", layout="wide",
                       initial_sidebar_state="auto")
    qc.inyectar_css()
    qc.preparar_sesion()
    if "ql_pagina" not in st.session_state:          # primera carga: la página puede venir en el enlace (?sim=…)
        sim = st.query_params.get("sim")
        if sim == "intro":                            # enlaces antiguos a la «Introducción teórica» (ahora, el tema de Schrödinger)
            sim = "teoria"
            st.session_state["ql_tema"] = "schrodinger"
        st.session_state["ql_pagina"] = sim if sim in PAGINAS else "inicio"
    _barra_lateral()
    pagina = st.session_state["ql_pagina"]
    if pagina in ("inicio", "pruebas", "verificacion"):
        qc.escribir_en_url(None)
    if pagina == "inicio":
        _pagina_inicio()
    elif pagina == "pruebas":
        _pagina_pruebas()
    elif pagina == "verificacion":
        verificacion.interfaz()
    else:
        PAGINAS[pagina][2].interfaz()


def _bajo_streamlit() -> bool:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    return get_script_run_ctx() is not None


if _bajo_streamlit():
    main()
elif __name__ == "__main__":
    registros = ejecutar_todas_las_pruebas()
    for reg in registros:
        reg.imprimir()
    print("\nPara abrir el laboratorio:  python -m streamlit run quantum_lab.py")
    sys.exit(0 if all(r.todo_ok() for r in registros) else 1)
