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

Las unidades siguen las diapositivas del curso (semanas 1, 2, 3 y 7 recibidas). Las semanas 4 a 6 agrupan los sistemas
modelo ya disponibles y se reordenarán cuando llegue el cronograma.
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
    Unidad("semana1", "Semana 1 · De la mecánica clásica a la cuántica",
           "Por qué hace falta una física nueva: los experimentos que la clásica no explica y los primeros modelos.", (
        Tema("cuerpo_negro", "Radiación del cuerpo negro",
             "La catástrofe ultravioleta, la hipótesis de Planck y las leyes de Wien y Stefan–Boltzmann.",
             "E = hν", DISPONIBLE, "cuerpo_negro"),
        Tema("fotoelectrico", "Efecto fotoeléctrico",
             "Frecuencia umbral, ecuación de Einstein y la constante de Planck al estilo de Millikan.",
             "Kmáx = hν − Φ", DISPONIBLE, "fotoelectrico", "fotoelectrico", "efecto_fotoelectrico", "foto"),
        Tema("de_broglie", "Partículas con comportamiento ondulatorio",
             "Ondas de materia de De Broglie, difracción de electrones y ondas estacionarias de Bohr.",
             "λ = h / p", DISPONIBLE, "de_broglie"),
        Tema("bohr", "Espectros atómicos y modelo de Bohr",
             "Niveles de energía, transiciones, series espectrales y el átomo cuántico en 3D.",
             "Eₙ = −13.6 eV / n²", DISPONIBLE, "bohr", "bohr", "modelo_bohr", "bohr"),
        Tema("criterios", "¿Cuándo usar la mecánica cuántica?",
             "Dos criterios: la longitud de onda frente al tamaño del sistema y el espaciado de energía frente a kT.",
             "nᵢ/nⱼ = (gᵢ/gⱼ) e^(−ΔE/kT)", DISPONIBLE, "criterios"),
    )),
    Unidad("semana2", "Semana 2 · La ecuación de Schrödinger",
           "De las ondas clásicas a la ecuación fundamental, y el lenguaje de operadores y autofunciones.", (
        Tema("ondas", "Ondas clásicas y funciones complejas",
             "Ondas viajeras y estacionarias, la ecuación de onda y la representación con exponenciales complejas.",
             "Ψ = A e^(i(kx − ωt))", DISPONIBLE, "ondas"),
        Tema("schrodinger", "La ecuación de Schrödinger",
             "Justificación, versión dependiente del tiempo, estados estacionarios y solución numérica.",
             "Ĥψ = Eψ", DISPONIBLE, "schrodinger"),
        Tema("operadores", "Operadores, ortogonalidad y completitud",
             "Autofunciones y autovalores, funciones ortogonales, desarrollo en una base y normalización.",
             "∫ψᵢ*ψⱼ dx = δᵢⱼ", DISPONIBLE, "operadores"),
    )),
    Unidad("semana3", "Semana 3 · Los postulados de la mecánica cuántica",
           "Las cinco reglas con las que se interpreta cualquier cálculo cuántico.", (
        Tema("postulados", "Los cinco postulados",
             "Función de onda y probabilidad, operadores, resultado de una medida, valor esperado y evolución temporal.",
             "⟨a⟩ = Σ aₙ |bₙ|²", DISPONIBLE, "postulados"),
    )),
    Unidad("sistemas", "Semanas 4 a 6 · Sistemas modelo",
           "Problemas con solución exacta (orden por confirmar con el cronograma del curso).", (
        Tema("caja", "Partícula en una caja",
             "Estados estacionarios, energías, nodos, superposición e interferencia.",
             "Eₙ = n²π²ħ² / 2ma²", DISPONIBLE, "caja", "caja", "particula_caja", "caja"),
        Tema("oscilador", "Oscilador armónico",
             "Polinomios de Hermite, teorema del virial, límite clásico y dinámica.",
             "Eₙ = ħω (n + ½)", DISPONIBLE, "oscilador", "oscilador", "oscilador_armonico", "osc"),
        Tema("esfera", "Momento angular y partícula en una esfera",
             "Armónicos esféricos, orbitales complejos y reales y partícula confinada.",
             "L² Yₗᵐ = ħ² l(l+1) Yₗᵐ", DISPONIBLE, "esfera", "esfera", "particula_esfera", "esf"),
    )),
    Unidad("semana7", "Semana 7 · Operadores que conmutan y que no conmutan",
           "Cuándo dos propiedades se pueden conocer a la vez y el principio de incertidumbre de Heisenberg.", (
        Tema("conmutadores", "Conmutadores e incertidumbre",
             "El conmutador, [x̂, p̂] = iħ, la forma general del principio y el ejemplo de la caja.",
             "[x̂, p̂] = iħ", DISPONIBLE, "conmutadores"),
        Tema("incertidumbre", "Paquetes de ondas y principio de incertidumbre",
             "Paquetes de ondas, el límite de Heisenberg, ensanchamiento libre y difracción por una rendija.",
             "Δx · Δp ≥ ħ / 2", DISPONIBLE, "incertidumbre", "incertidumbre", "principio_incertidumbre", "inc"),
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
    qc.metricas([("Temas disponibles", f"{listos}"), ("Unidades", f"{len(UNIDADES)}")], columnas=2)
    st.info("Organizado según las diapositivas del curso. Las semanas 4 a 6 reúnen los sistemas modelo ya disponibles y se "
            "reordenarán con el cronograma; cada semana nueva se añade a medida que avanza el curso.",
            icon=":material/info:")
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


def _preguntas(tema: Tema):
    """Preguntas de autoevaluación: las del simulador si lo hay y, si no, las del propio módulo de teoría."""
    if tema.simulador:
        return importlib.import_module(tema.modulo_sim).PREGUNTAS
    return getattr(importlib.import_module(f"teoria.{tema.modulo}"), "PREGUNTAS", None)


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

    preguntas = _preguntas(tema)
    nombres = ["Teoría"]
    if tema.simulador:
        nombres.append("Simulación y práctica")
    if preguntas:
        nombres.append("Autoevaluación")
    tabs = st.tabs(nombres)
    with tabs[0]:
        mostrar()
    k = 1
    if tema.simulador:
        with tabs[k]:
            _practica(tema)
        k += 1
    if preguntas:
        with tabs[k]:
            qc.autoevaluacion(preguntas, tema.prefijo or f"tq_{tema.id}")


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
    r.comprobar("Los 6 simuladores y los temas de las semanas 1, 2, 3 y 7 están en el índice",
                {"caja", "oscilador", "esfera", "fotoelectrico", "bohr", "incertidumbre", "cuerpo_negro", "de_broglie", "criterios",
                 "ondas", "schrodinger", "operadores", "postulados", "conmutadores"} <= set(ids))
    r.comprobar("Todo tema disponible sin simulador tiene autoevaluación propia (≥ 5 preguntas)",
                all(len(_preguntas(t) or []) >= 5 for t in disponibles if not t.simulador))
    r.comprobar("Las preguntas de autoevaluación tienen la respuesta correcta dentro de las opciones",
                all(0 <= p["correcta"] < len(p["opciones"]) for t in disponibles for p in (_preguntas(t) or [])))
    return r
