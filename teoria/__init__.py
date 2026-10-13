"""
teoria — Centro de teoría de QUANTUM LAB
========================================

Un único lugar para consultar la teoría del curso y pasar de ella a las simulaciones, la práctica y la
autoevaluación. Cada tema tiene tres partes:

    Teoría                  texto y ecuaciones (un módulo teoria/<tema>.py con la función mostrar())
    Simulación y práctica   botón al simulador y experimentos guiados
    Autoevaluación          preguntas de opción múltiple con explicación

Cómo añadir un tema nuevo (cuando el curso llegue a él):
    1. Crear teoria/<id>.py con una función mostrar() que escriba la teoría con Streamlit.
    2. En la lista UNIDADES de abajo, cambiar su estado a DISPONIBLE y rellenar `modulo`
       (y `simulador`, `modulo_sim`, `prefijo` si ya existe un simulador con su guía y preguntas).

El orden y los nombres de las unidades son PROVISIONALES: se ajustarán al temario real del curso.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field

import streamlit as st

import quantum_lab_comun as qc

DISPONIBLE = "disponible"
PROXIMAMENTE = "proximamente"


@dataclass(frozen=True)
class Tema:
    id: str
    titulo: str
    resumen: str
    ecuacion: str = ""
    estado: str = PROXIMAMENTE
    modulo: str = ""                  # teoria.<modulo> con mostrar(); vacío si aún no hay contenido
    simulador: str = ""               # clave de página del simulador en quantum_lab.PAGINAS
    modulo_sim: str = ""              # módulo Python del simulador (GUIA y PREGUNTAS)
    prefijo: str = ""                 # prefijo de claves de la guía y la autoevaluación
    previsto: tuple = field(default_factory=tuple)   # contenidos planeados (solo para «próximamente»)


@dataclass(frozen=True)
class Unidad:
    id: str
    titulo: str
    descripcion: str
    temas: tuple


UNIDADES: tuple[Unidad, ...] = (
    Unidad("origenes", "Orígenes de la teoría cuántica",
           "De los fallos de la física clásica a los primeros modelos con energía cuantizada.", (
        Tema("cuerpo_negro", "Radiación del cuerpo negro",
             "La catástrofe ultravioleta y la hipótesis de Planck.", "E = hν",
             previsto=("Ley de Planck frente a Rayleigh–Jeans", "Leyes de Wien y de Stefan–Boltzmann",
                       "Simulador de espectros a distintas temperaturas")),
        Tema("fotoelectrico", "Efecto fotoeléctrico",
             "Frecuencia umbral, ecuación de Einstein y la constante de Planck al estilo de Millikan.",
             "Kmáx = hν − Φ", DISPONIBLE, "fotoelectrico", "fotoelectrico", "efecto_fotoelectrico", "foto"),
        Tema("bohr", "Modelo de Bohr y átomo de hidrógeno",
             "Niveles de energía, transiciones, series espectrales y el átomo cuántico en 3D.",
             "Eₙ = −13.6 eV / n²", DISPONIBLE, "bohr", "bohr", "modelo_bohr", "bohr"),
        Tema("de_broglie", "Dualidad onda–partícula",
             "Ondas de materia de De Broglie y difracción de electrones.", "λ = h / p",
             previsto=("Longitud de onda de De Broglie de partículas y objetos", "Experimento de la doble rendija",
                       "Condición de Bohr como onda estacionaria")),
    )),
    Unidad("fundamentos", "Fundamentos de la mecánica cuántica",
           "Las ideas y herramientas con las que se interpreta cualquier resultado posterior.", (
        Tema("introduccion", "Introducción a la mecánica cuántica",
             "Función de onda, ecuación de Schrödinger, superposición, momento angular y unidades.",
             "iħ ∂ₜΨ = ĤΨ", DISPONIBLE, "introduccion"),
        Tema("incertidumbre", "Principio de incertidumbre",
             "Paquetes de ondas, el límite de Heisenberg, ensanchamiento libre y difracción por una rendija.",
             "Δx · Δp ≥ ħ / 2", DISPONIBLE, "incertidumbre", "incertidumbre", "principio_incertidumbre", "inc"),
        Tema("postulados", "Postulados y operadores",
             "Observables, operadores hermíticos, valores esperados y conmutadores.", "[x̂, p̂] = iħ",
             previsto=("Valores esperados y desviaciones", "Conmutadores e incertidumbre generalizada",
                       "Medida y colapso")),
    )),
    Unidad("modelos", "Sistemas modelo",
           "Problemas resolubles de forma exacta que sirven de laboratorio para entender la cuantización.", (
        Tema("caja", "Partícula en una caja",
             "Estados estacionarios, energías, nodos, superposición e interferencia.",
             "Eₙ = n²π²ħ² / 2ma²", DISPONIBLE, "caja", "caja", "particula_caja", "caja"),
        Tema("oscilador", "Oscilador armónico",
             "Polinomios de Hermite, teorema del virial, límite clásico y dinámica.",
             "Eₙ = ħω (n + ½)", DISPONIBLE, "oscilador", "oscilador", "oscilador_armonico", "osc"),
        Tema("esfera", "Momento angular y partícula en una esfera",
             "Armónicos esféricos, orbitales complejos y reales y partícula confinada.",
             "L² Yₗᵐ = ħ² l(l+1) Yₗᵐ", DISPONIBLE, "esfera", "esfera", "particula_esfera", "esf"),
        Tema("tunel", "Efecto túnel y barreras",
             "Penetración en regiones prohibidas y transmisión a través de una barrera.", "T ≈ e^(−2κa)",
             previsto=("Barrera rectangular: transmisión y reflexión", "Pozo finito", "Aplicaciones: STM, desintegración α")),
        Tema("rotor", "Rotor rígido",
             "Rotación molecular y espectros rotacionales.", "E_J = ħ² J(J+1) / 2I",
             previsto=("Niveles rotacionales y reglas de selección", "Espectro de rotación de moléculas diatómicas")),
    )),
    Unidad("atomos", "Átomos hidrogenoides y polielectrónicos",
           "Del átomo de hidrógeno exacto a los métodos aproximados para varios electrones.", (
        Tema("hidrogeno", "Átomo de hidrógeno (ecuación radial)",
             "Funciones radiales, números cuánticos y orbitales.", "ψₙₗₘ = Rₙₗ(r) Yₗᵐ(θ, φ)",
             previsto=("Funciones de onda radiales y distribuciones radiales", "Orbitales s, p, d en 3D",
                       "Degeneración y niveles de energía")),
        Tema("espin", "Espín y principio de exclusión",
             "Momento angular de espín, estados de dos electrones y configuraciones electrónicas.", "s = ½",
             previsto=("Espín del electrón", "Principio de Pauli y configuraciones", "Acoplamiento de momentos angulares")),
        Tema("aproximados", "Métodos aproximados",
             "Teoría de perturbaciones y método variacional.", "E_var ≥ E₀",
             previsto=("Método variacional con funciones de prueba", "Perturbaciones independientes del tiempo",
                       "Átomo de helio")),
    )),
    Unidad("moleculas", "Estructura molecular",
           "Cómo se enlazan los átomos: de Born–Oppenheimer a los orbitales moleculares.", (
        Tema("born_oppenheimer", "Aproximación de Born–Oppenheimer",
             "Separación del movimiento nuclear y electrónico; superficies de energía potencial.", "V(R)",
             previsto=("Curvas de energía potencial", "Vibración de moléculas diatómicas")),
        Tema("orbitales_moleculares", "Orbitales moleculares",
             "Combinación lineal de orbitales atómicos, enlace y antienlace.", "ψ_MO = Σ cᵢ φᵢ",
             previsto=("Ión molecular H₂⁺", "Molécula H₂", "Diagramas de orbitales moleculares")),
        Tema("espectroscopia", "Espectroscopía molecular",
             "Transiciones rotacionales, vibracionales y electrónicas.", "ΔE = hν",
             previsto=("Espectros rotovibracionales", "Regla de selección y principio de Franck–Condon")),
    )),
)

def todos_los_temas() -> list[tuple[Unidad, Tema]]:
    return [(u, t) for u in UNIDADES for t in u.temas]


def buscar(tema_id: str) -> tuple[Unidad, Tema] | None:
    for u, t in todos_los_temas():
        if t.id == tema_id:
            return u, t
    return None


def contenido(tema: Tema):
    """Importa teoria.<modulo> y devuelve su función mostrar (None si el tema aún no tiene contenido)."""
    if tema.estado != DISPONIBLE or not tema.modulo:
        return None
    return importlib.import_module(f"teoria.{tema.modulo}").mostrar


# ---------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------
def _abrir_tema(tema_id: str) -> None:
    st.session_state["ql_tema"] = tema_id


def _volver_al_indice() -> None:
    st.session_state["ql_tema"] = ""


def _ir_a_simulador(clave: str) -> None:
    st.session_state["ql_pagina"] = clave


def _vista_indice() -> None:
    qc.encabezado_pagina("Teoría", "Centro de teoría",
                         "Toda la teoría del curso en un solo lugar, conectada con las simulaciones, los experimentos "
                         "guiados y la autoevaluación de cada tema.")
    todos = todos_los_temas()
    listos = sum(t.estado == DISPONIBLE for _, t in todos)
    qc.metricas([("Temas disponibles", f"{listos}"), ("Temas en preparación", f"{len(todos) - listos}"),
                 ("Unidades", f"{len(UNIDADES)}")], columnas=3)
    st.info("El orden de las unidades es **provisional**: se ajustará al temario real del curso. Los temas «en preparación» "
            "ya tienen su lugar y se activan cuando el curso llegue a ellos.", icon=":material/info:")
    for unidad in UNIDADES:
        qc.seccion(unidad.titulo)
        st.caption(unidad.descripcion)
        for inicio in range(0, len(unidad.temas), 3):
            columnas = st.columns(3)
            for col, tema in zip(columnas, unidad.temas[inicio:inicio + 3]):
                listo = tema.estado == DISPONIBLE
                with col:
                    etiqueta = "Disponible" if listo else "En preparación"
                    st.markdown(f'<div class="ql-card" style="min-height:250px"><p class="ql-etiqueta">{etiqueta}</p><h3>{tema.titulo}</h3>'
                                f'<p>{tema.resumen}</p><div class="ql-ecuacion">{tema.ecuacion}</div></div>',
                                unsafe_allow_html=True)
                    st.button("Leer" if listo else "Ver contenidos previstos", key=f"tc_abrir_{tema.id}",
                              on_click=_abrir_tema, args=(tema.id,), width="stretch",
                              icon=":material/menu_book:" if listo else ":material/schedule:",
                              type="primary" if listo else "secondary")


def _practica(tema: Tema) -> None:
    sim = importlib.import_module(tema.modulo_sim)
    st.markdown("Pon a prueba la teoría con el simulador de este tema: cambia los parámetros y compara con lo que predice "
                "la teoría.")
    st.button("Abrir el simulador", key=f"tc_sim_{tema.id}", icon=":material/arrow_forward:", type="primary",
              on_click=_ir_a_simulador, args=(tema.simulador,))
    qc.seccion("Experimentos propuestos")
    for i, e in enumerate(sim.GUIA, 1):
        with st.container(border=True):
            st.markdown(f"**{i}. {e['titulo']}**")
            st.markdown(e["objetivo"])
    st.caption("Los pasos detallados, con sus configuraciones listas para cargar, están en la pestaña «Guía de práctica» "
               "del simulador.")


def _vista_tema(tema_id: str) -> None:
    hallado = buscar(tema_id)
    if hallado is None:
        _volver_al_indice()
        st.rerun()
    unidad, tema = hallado
    c1, c2 = st.columns([1, 5], vertical_alignment="center")
    with c1:
        st.button("Índice", key="tc_volver", icon=":material/arrow_back:", on_click=_volver_al_indice, width="stretch")
    with c2:
        st.caption(f"{unidad.titulo}")
    qc.encabezado_pagina("Teoría · " + unidad.titulo, tema.titulo, tema.resumen)

    mostrar = contenido(tema)
    if mostrar is None:
        st.warning("Este tema está **en preparación**: se activará cuando el curso llegue a él.", icon=":material/schedule:")
        if tema.previsto:
            qc.seccion("Contenidos previstos")
            st.markdown("\n".join(f"- {p}" for p in tema.previsto))
        return

    nombres = ["Teoría"]
    if tema.simulador:
        nombres += ["Simulación y práctica", "Autoevaluación"]
    tabs = st.tabs(nombres)
    with tabs[0]:
        mostrar()
    if tema.simulador:
        with tabs[1]:
            _practica(tema)
        with tabs[2]:
            qc.autoevaluacion(importlib.import_module(tema.modulo_sim).PREGUNTAS, tema.prefijo)


def interfaz() -> None:
    """Página «Centro de teoría» (índice por unidades o un tema)."""
    if "ql_tema" not in st.session_state:             # primera carga: el tema puede venir en la dirección (?tema=…)
        pedido = st.query_params.get("tema")
        st.session_state["ql_tema"] = pedido if pedido and buscar(pedido) else ""
    tema_id = st.session_state.get("ql_tema") or ""
    qc.escribir_en_url(None, extra={"tema": tema_id})
    if tema_id:
        _vista_tema(tema_id)
    else:
        _vista_indice()


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def ejecutar_pruebas() -> "qc.RegistroPruebas":
    """Consistencia del índice: identificadores únicos, módulos importables y estados coherentes."""
    r = qc.RegistroPruebas("Centro de teoría")
    todos = todos_los_temas()
    ids = [t.id for _, t in todos]
    r.comprobar("Identificadores de tema únicos", len(ids) == len(set(ids)))
    r.comprobar("Identificadores de unidad únicos", len({u.id for u in UNIDADES}) == len(UNIDADES))
    disponibles = [t for _, t in todos if t.estado == DISPONIBLE]
    r.comprobar("Todo tema disponible tiene contenido importable",
                all(callable(contenido(t)) for t in disponibles))
    r.comprobar("Todo tema en preparación declara sus contenidos previstos",
                all(t.previsto for _, t in todos if t.estado == PROXIMAMENTE))
    r.comprobar("Cada simulador enlazado tiene guía y preguntas",
                all(importlib.import_module(t.modulo_sim).GUIA and importlib.import_module(t.modulo_sim).PREGUNTAS
                    for t in disponibles if t.simulador))
    r.comprobar("Los 6 simuladores y la introducción están en el índice",
                {"caja", "oscilador", "esfera", "fotoelectrico", "bohr", "incertidumbre", "introduccion"} <= set(ids))
    return r
