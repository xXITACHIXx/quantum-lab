"""
ruta — Ruta de estudio de QUANTUM LAB
=====================================

El curso no avanza por fechas; la ruta se organiza por dominio de cada tema y por dependencias físicas (ver `ejercicios/_ruta.py`).
Cada tema muestra tres pasos (teoría leída, ejercicios resueltos, mini-examen aprobado), los prerrequisitos que conviene reforzar
y accesos directos. La página propone el «siguiente paso» según la bitácora de intentos.

Cómo cambiar el orden o los prerrequisitos: editar `ORDEN` y `PREREQ` en `ejercicios/_ruta.py`; las pruebas verifican que sean consistentes.
"""

from __future__ import annotations

import streamlit as st

import ejercicios
import examen
import quantum_lab_comun as qc
import teoria
from ejercicios import _bitacora, _estado, _ruta
from ejercicios._modelo import FUENTES, TEMAS
from examen import _logica as _lx

ETIQUETA_ESTADO = {_ruta.HECHO: ":material/check_circle:", _ruta.PENDIENTE: ":material/radio_button_unchecked:", _ruta.NA: ":material/remove:"}


def estados() -> dict:
    """Estado de cada tema de la ruta con los datos de la sesión actual."""
    filas = {f["tema"]: f for f in _bitacora.por_tema(_estado.bitacora(), ejercicios.EJERCICIOS, _estado.hechos(), _estado.repasar())}
    for f in filas.values():
        f["comprobables"] = sum(1 for e in ejercicios.EJERCICIOS if e.tema == f["tema"] and e.comprobable)
    disponible = {t: (teoria.buscar(t) is not None and teoria.buscar(t)[1].estado == teoria.DISPONIBLE) for t in _ruta.ORDEN}
    return _ruta.evaluar(_estado.marcas(), filas, disponible)


def _titulo(tema: str) -> str:
    return TEMAS.get(tema, tema)


# ---------------------------------------------------------------------
# Acciones
# ---------------------------------------------------------------------
def _abrir_ejercicios(tema: str) -> None:
    st.session_state.update(ql_pagina="ejercicios", ej_fuente=ejercicios.TODAS, ej_tema=TEMAS[tema], ej_buscar="")


def _mini_examen(tema: str) -> None:
    """Prepara y comienza un examen corto con ejercicios del tema (cambia en cada intento)."""
    pool = examen.candidatos(examen.POOL_TODOS, FUENTES, [tema], examen.NIVELES)
    previos = sum(1 for x in _estado.historial() if x["temas"] == [TEMAS[tema]])
    ids = _lx.seleccionar(pool, _ruta.MINI_N, f"mini-{tema}-{previos}")
    if not ids:
        return
    st.session_state["ql_pagina"] = "examen"
    examen._comenzar(ids, _lx.duracion_sugerida(len(ids)))
    st.session_state["ex_mini"] = tema


def _marcar_teoria(tema: str) -> None:
    _estado.marcar_ruta(_ruta.marca_teoria(tema), bool(st.session_state.get(f"ru_t_{tema}")))


def _ir(pagina: str) -> None:
    st.session_state["ql_pagina"] = pagina


def _accion(tema: str, paso: str, clave: str) -> None:
    """Botón que lleva a hacer el paso indicado."""
    if paso == _ruta.TEORIA:
        st.button("Abrir la teoría", key=f"{clave}_teo", icon=":material/menu_book:", on_click=qc.ir_a_tema, args=(tema,), width="stretch")
    elif paso == _ruta.EJERCICIOS:
        st.button("Ir a los ejercicios", key=f"{clave}_ej", icon=":material/calculate:", on_click=_abrir_ejercicios, args=(tema,), width="stretch")
    else:
        st.button(f"Mini-examen ({_ruta.MINI_N} ejercicios)", key=f"{clave}_mini", icon=":material/timer:", on_click=_mini_examen, args=(tema,), width="stretch")


# ---------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------
def tarjeta_sugerencia(est: dict, clave: str = "ru_sug") -> None:
    """Bloque «Siguiente paso sugerido» (también se usa en el inicio)."""
    s = _ruta.siguiente(est)
    with st.container(border=True):
        st.markdown("**Siguiente paso sugerido**")
        if s.tema is None:
            st.markdown("La ruta está completa. Se recomienda un examen general para consolidar.")
            st.button("Abrir el modo examen", key=f"{clave}_ex", icon=":material/timer:", on_click=_ir, args=("examen",))
            return
        st.markdown(f"**{_titulo(s.tema)}** · {_ruta.NOMBRE_PASO[s.paso].lower()}")
        st.caption(s.motivo[0].upper() + s.motivo[1:] + ".")
        _accion(s.tema, s.paso, clave)


def _vista_tema(est: dict, tema: str) -> None:
    e = est[tema]
    with st.container(border=True):
        cab, barra = st.columns([3, 2], vertical_alignment="center")
        estado = "Completo" if e.completo else ("En curso" if e.iniciado else "Sin iniciar")
        cab.markdown(f"**{_titulo(tema)}**  ·  {estado}")
        barra.progress(e.hechos / len(e.aplicables) if e.aplicables else 1.0, text=f"{e.hechos} de {len(e.aplicables)} pasos")
        for p, nombre in _ruta.NOMBRE_PASO.items():
            icono = ETIQUETA_ESTADO[e.pasos[p]]
            if p == _ruta.TEORIA:
                if e.pasos[p] == _ruta.NA:
                    st.markdown(f"{icono} {nombre}: la teoría de este tema aún no está disponible.")
                else:
                    st.checkbox(f"{nombre}", value=e.pasos[p] == _ruta.HECHO, key=f"ru_t_{tema}", on_change=_marcar_teoria, args=(tema,))
            elif p == _ruta.EJERCICIOS:
                st.markdown(f"{icono} {nombre}: {e.resueltos} de {e.total} (se requieren {_ruta.requeridos(e.total)})" if e.total
                            else f"{icono} {nombre}: este tema no tiene ejercicios todavía.")
            else:
                st.markdown(f"{icono} {nombre}" + ("" if e.comprobables else ": sin ejercicios comprobables."))
        if e.por_repasar:
            st.caption(f"{e.por_repasar} ejercicio(s) de este tema por repasar.")
        if e.debil:
            st.warning(f"Precisión de {100 * e.precision:.0f} % en {e.intentos} comprobaciones: se recomienda repasar este tema.", icon=":material/trending_down:")
        for pre, motivo in _ruta.prerrequisitos_flojos(tema, est):
            st.warning(f"Prerrequisito por reforzar: {_titulo(pre)} ({motivo}).", icon=":material/account_tree:")
        c1, c2, c3 = st.columns(3)
        if e.pasos[_ruta.TEORIA] != _ruta.NA:
            with c1:
                _accion(tema, _ruta.TEORIA, f"ru_{tema}")
        if e.total:
            with c2:
                _accion(tema, _ruta.EJERCICIOS, f"ru_{tema}")
        if e.comprobables:
            with c3:
                _accion(tema, _ruta.MINI, f"ru_{tema}")


def interfaz() -> None:
    """Página «Ruta de estudio»."""
    qc.encabezado_pagina("Plan de estudio", "Ruta de estudio",
                         "Recorrido por dominio de cada tema, en orden de dependencias físicas y sin depender de fechas. Cada tema se completa con teoría, "
                         "ejercicios y un mini-examen.")
    qc.escribir_en_url(None)
    est = estados()
    completos = sum(e.completo for e in est.values())
    pasos_hechos = sum(e.hechos for e in est.values())
    pasos_total = sum(len(e.aplicables) for e in est.values())
    qc.metricas([("Temas completos", f"{completos} de {len(est)}"), ("Pasos cumplidos", f"{pasos_hechos} de {pasos_total}"),
                 ("Temas con bajo desempeño", str(sum(e.debil for e in est.values())),
                  f"Temas con precisión menor de {100 * _ruta.PRECISION_BAJA:.0f} % en al menos {_ruta.MIN_INTENTOS} comprobaciones.")], columnas=3)
    st.progress(pasos_hechos / pasos_total if pasos_total else 0.0)
    tarjeta_sugerencia(est)
    with st.expander("Cómo se completa un tema", icon=":material/help:"):
        st.markdown(f"- **Teoría leída:** se marca a mano al terminar de leer el tema.\n"
                    f"- **Ejercicios resueltos:** al menos el {100 * _ruta.FRACCION_EJERCICIOS:.0f} % de los ejercicios del tema resueltos.\n"
                    f"- **Mini-examen aprobado:** {_ruta.MINI_N} ejercicios del tema, con una nota de {_ruta.NOTA_MINI:.1f} o más sobre 5.0.\n"
                    "- Los pasos que no aplican (teoría aún no disponible) no cuentan.\n"
                    "- El orden respeta las dependencias: cada tema indica los prerrequisitos que conviene reforzar antes de avanzar.\n"
                    "- El progreso se guarda en la dirección de la página y en la copia de seguridad.")
    for i, tema in enumerate(_ruta.ORDEN, 1):
        pre = _ruta.PREREQ[tema]
        st.markdown(f"##### {i}. {_titulo(tema)}")
        if pre:
            st.caption("Requiere: " + ", ".join(_titulo(p) for p in pre))
        _vista_tema(est, tema)


def ejecutar_pruebas() -> "qc.RegistroPruebas":
    reg = qc.RegistroPruebas("Ruta de estudio")
    reg.comprobar("Estructura de la ruta consistente", not _ruta.validar_estructura(TEMAS), "; ".join(_ruta.validar_estructura(TEMAS)))
    reg.comprobar("Todos los temas de los ejercicios están en la ruta", {e.tema for e in ejercicios.EJERCICIOS} <= set(_ruta.ORDEN))
    vacio = _ruta.evaluar(set(), {}, {t: True for t in _ruta.ORDEN})
    reg.comprobar("Sin actividad, se sugiere el primer tema", _ruta.siguiente(vacio).tema in ("fotoelectrico", "ondas"))
    reg.comprobar("Marcas de la ruta con token único",
                  len({ejercicios._progreso.token(m) for m in _ruta.todas_las_marcas()}) == len(_ruta.todas_las_marcas()))
    return reg
