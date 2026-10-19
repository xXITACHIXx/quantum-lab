"""
quantum_lab.py — QUANTUM LAB · menú principal
=============================================

Laboratorio interactivo de mecánica cuántica con seis simuladores independientes y herramientas de estudio (biblioteca, solucionador, tutor, guía de usuario):

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
import biblioteca
import ejercicios
import examen
import formulario
import guia
import modelo_bohr
import oscilador_armonico
import particula_caja
import particula_esfera
import principio_incertidumbre
import quantum_lab_escena as escena
import quantum_lab_portada as portada
import repaso
import ruta
import solucionador
import talleres
import teoria
import tutor
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
    "talleres": ("Talleres de repaso", ":material/edit_note:", talleres),
    "ejercicios": ("Ejercicios de práctica", ":material/calculate:", ejercicios),
    "ruta": ("Ruta de estudio", ":material/route:", ruta),
    "examen": ("Modo examen", ":material/timer:", examen),
    "repaso": ("Repaso personalizado", ":material/history_edu:", repaso),
    "formulario": ("Formulario", ":material/functions:", formulario),
    "biblioteca": ("Biblioteca científica", ":material/local_library:", biblioteca),
    "solucionador": ("Solucionador paso a paso", ":material/function:", solucionador),
    "tutor": ("Tutor de errores conceptuales", ":material/psychology_alt:", tutor),
    "guia": ("Guía de usuario", ":material/account_tree:", guia),
    "verificacion": ("Verificación", ":material/verified:", verificacion),
    "pruebas": ("Pruebas numéricas", ":material/fact_check:", None),
}
GRUPOS = [
    ("Mecánica cuántica", ["caja", "oscilador", "esfera"], True),
    ("Fundamentos", ["fotoelectrico", "bohr", "incertidumbre"], True),
    ("Teoría y repaso", ["ruta", "teoria", "formulario", "talleres", "ejercicios", "examen", "repaso"], True),
    ("Herramientas de estudio", ["biblioteca", "solucionador", "tutor", "guia"], True),
    ("Verificación", ["verificacion", "pruebas"], True),
]


def _ir_a(pagina: str) -> None:
    """Callback de navegación."""
    st.session_state["ql_pagina"] = pagina


def ejecutar_todas_las_pruebas() -> list[qc.RegistroPruebas]:
    return [m.ejecutar_pruebas() for m in (particula_caja, oscilador_armonico, particula_esfera,
                                            efecto_fotoelectrico, modelo_bohr, principio_incertidumbre, teoria, talleres, ejercicios, formulario, examen, repaso, ruta, biblioteca, solucionador, tutor, guia, verificacion)]


# ---------------------------------------------------------------------
# Pie de página (sin barra lateral: se navega desde la portada y las sub-portadas)
# ---------------------------------------------------------------------
def _pie() -> None:
    with st.container(key="ql_pie"):
        qc.interruptor_movil()
        escena.instalar_efectos(st, len(portada.CATEGORIAS), len(portada.MODULOS))
        st.markdown(portada.css_navegacion() + '<div class="ql-pie">Cálculo con NumPy y SciPy. La dirección de la página guarda la '
                    f'configuración: cópiala para compartirla. Versión {qc.VERSION} · 6 simuladores</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------
def _ubicacion(pagina: str) -> None:
    """Barra de ubicación (categoría / página / número) con regreso al capítulo y a la portada."""
    m = portada.modulo(pagina)
    c1, c2, c3 = st.columns([4, 1.5, 1.25], vertical_alignment="center")
    c1.markdown(escena.ubicacion_html(m[2], m[4], m[1], len(portada.MODULOS)), unsafe_allow_html=True)
    c2.button(f"\u2190 {m[2]}", key="ql_categoria", type="tertiary", on_click=_ir_a, args=(portada.CAT_CLAVE[m[2]],), width="stretch")
    c3.button("\u2190 Inicio", key="ql_volver", type="tertiary", on_click=_ir_a, args=("inicio",), width="stretch")


def _pagina_inicio() -> None:
    portada.pagina_inicio(_ir_a, lambda: ruta.tarjeta_sugerencia(ruta.estados(), "ru_inicio"))


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
                       initial_sidebar_state="collapsed")
    qc.inyectar_css()
    qc.preparar_sesion()
    if "ql_pagina" not in st.session_state:          # primera carga: la página puede venir en el enlace (?sim=…)
        sim = st.query_params.get("sim")
        if sim == "intro":                            # enlaces antiguos a la «Introducción teórica» (ahora, el tema de Schrödinger)
            sim = "teoria"
            st.session_state["ql_tema"] = "schrodinger"
        st.session_state["ql_pagina"] = sim if sim in PAGINAS else "inicio"
    pagina = st.session_state["ql_pagina"]
    if pagina in ("inicio", "pruebas", "verificacion") or pagina in portada.CLAVE_CAT:
        qc.escribir_en_url(None)
    # La clave del contenedor cambia solo al cambiar de página: la animación de entrada se reproduce al navegar y no al mover un control.
    with st.container(key=f"ql_escena_{pagina}"):
        if pagina != "inicio" and pagina not in portada.CLAVE_CAT:
            _ubicacion(pagina)
        if pagina == "inicio":
            _pagina_inicio()
        elif pagina in portada.CLAVE_CAT:
            portada.pagina_subinicio(_ir_a, portada.CLAVE_CAT[pagina])
        elif pagina == "pruebas":
            _pagina_pruebas()
        elif pagina == "verificacion":
            verificacion.interfaz()
        else:
            PAGINAS[pagina][2].interfaz()
    _pie()


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
