"""
examen — Modo examen de QUANTUM LAB
===================================

Simulacro cronometrado con ejercicios de la colección de práctica: el estudiante elige fuente, temas, nivel, número de ejercicios y
duración; durante el examen no hay pistas ni soluciones ni retroalimentación; al entregar (o al terminar el tiempo) se califica sobre
5.0 y se muestra la corrección completa con la solución paso a paso. Los resultados alimentan «Mi repaso».

Archivos:
    _logica.py      selección reproducible, nota, tiempo (sin Streamlit)
    __init__.py     página y pruebas internas
"""

from __future__ import annotations

import time

import streamlit as st

import ejercicios
import quantum_lab_comun as qc
from ejercicios import _estado
from ejercicios._modelo import FUENTES, TEMAS, calificar
from examen import _logica
from talleres._calificar import OK, VACIA
from talleres._modelo import OPC

RELOJ = time.time                       # sustituible en las pruebas
POOL_TODOS, POOL_NUEVOS, POOL_REPASO = "Todos los ejercicios", "Solo los que no he resuelto", "Solo los que tengo por repasar"
NIVELES = ("Básico", "Intermedio", "Avanzado")


def _clave(ej_id: str, parte: str) -> str:
    return f"exm_{ej_id}_{parte}"


def _texto(valor) -> str:
    return "" if valor is None else str(valor).strip()


# ---------------------------------------------------------------------
# Selección
# ---------------------------------------------------------------------
def candidatos(pool: str, fuentes, temas, niveles) -> list[str]:
    """Ids de los ejercicios que cumplen los filtros. `temas` son claves de TEMAS."""
    salida = []
    for e in ejercicios.EJERCICIOS:
        if e.fuente not in fuentes or e.tema not in temas or e.dificultad not in niveles or not e.comprobable:
            continue
        if pool == POOL_NUEVOS and e.id in _estado.hechos():
            continue
        if pool == POOL_REPASO and e.id not in _estado.repasar():
            continue
        salida.append(e.id)
    return salida


def _borrar_respuestas() -> None:
    for k in [k for k in st.session_state if str(k).startswith("exm_")]:
        del st.session_state[k]


def _comenzar(ids: list[str], minutos: int) -> None:
    _borrar_respuestas()
    st.session_state.update(ex_fase="curso", ex_ids=list(ids), ex_inicio=RELOJ(), ex_dur=60.0 * minutos,
                            ex_confirmar=False, ex_entrega=None)


def _iniciar() -> None:
    """Callback del botón «Comenzar»: lee la configuración y arranca el examen."""
    fuentes = st.session_state.get("ex_fuentes", list(FUENTES))
    claves = [k for k, t in TEMAS.items() if t in st.session_state.get("ex_temas", [])]
    niveles = st.session_state.get("ex_niveles", list(NIVELES))
    pool = candidatos(st.session_state.get("ex_pool", POOL_TODOS), fuentes, claves, niveles)
    semilla = _texto(st.session_state.get("ex_semilla")) or f"{RELOJ():.3f}"
    n = int(st.session_state.get("ex_n", 5))
    ids = _logica.seleccionar(pool, n, semilla)
    if ids:
        _comenzar(ids, int(st.session_state.get("ex_min", _logica.duracion_sugerida(len(ids)))))


def _repetir() -> None:
    _comenzar(st.session_state["ex_ids"], int(st.session_state["ex_dur"] // 60))


def _nuevo() -> None:
    _borrar_respuestas()
    st.session_state.update(ex_fase="config", ex_entrega=None, ex_confirmar=False)


def _preparar_repaso() -> None:
    _nuevo()
    st.session_state["ex_pool"] = POOL_REPASO


def _pedir_confirmacion() -> None:
    st.session_state["ex_confirmar"] = True


def _seguir() -> None:
    st.session_state["ex_confirmar"] = False


def _entregar(motivo: str = "entrega") -> None:
    """Califica las respuestas escritas, las registra en la bitácora y pasa a la corrección."""
    ids = st.session_state["ex_ids"]
    respuestas, cals = {}, {}
    for ej_id in ids:
        ej = ejercicios.buscar(ej_id)
        respuestas[ej_id] = {p.clave: st.session_state.get(_clave(ej_id, p.clave)) for p in ej.partes}
        cals[ej_id] = calificar(ej, respuestas[ej_id])
        _estado.registrar_calificacion(ej_id, cals[ej_id])
    nota, pct = _logica.nota(c.fraccion for c in cals.values())
    usados = min(st.session_state["ex_dur"], RELOJ() - st.session_state["ex_inicio"])
    _estado.registrar_examen(ids, nota, pct, usados, st.session_state["ex_dur"], [TEMAS[ejercicios.buscar(i).tema] for i in ids])
    st.session_state.update(ex_fase="fin", ex_confirmar=False,
                            ex_entrega={"respuestas": respuestas, "cals": cals, "nota": nota, "pct": pct, "usados": usados,
                                        "motivo": motivo})


def _restante() -> float:
    return _logica.restante(st.session_state["ex_inicio"], st.session_state["ex_dur"], RELOJ())


# ---------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------
def _vista_configuracion() -> None:
    qc.seccion("Configuración del examen")
    st.markdown(f"Cada examen se compone de ejercicios elegidos al azar entre los que cumplen los filtros. Durante el examen no se "
                f"muestran pistas ni soluciones, y no hay retroalimentación hasta entregarlo. La calificación es sobre "
                f"**{_logica.ESCALA:.1f}**, con el mismo peso para cada ejercicio y crédito parcial por cada parte correcta.")
    temas_presentes = [t for k, t in TEMAS.items() if any(e.tema == k for e in ejercicios.EJERCICIOS)]
    c1, c2 = st.columns(2)
    with c1:
        st.radio("Ejercicios disponibles", (POOL_TODOS, POOL_NUEVOS, POOL_REPASO), key="ex_pool",
                 help="«Por repasar»: ejercicios comprobados sin acertar del todo o cuya solución se consultó sin haberlos resuelto.")
        st.multiselect("Fuente", FUENTES, default=list(FUENTES), key="ex_fuentes")
    with c2:
        st.multiselect("Temas", temas_presentes, default=temas_presentes, key="ex_temas")
        st.multiselect("Nivel", NIVELES, default=list(NIVELES), key="ex_niveles")
    claves = [k for k, t in TEMAS.items() if t in st.session_state.get("ex_temas", temas_presentes)]
    pool = candidatos(st.session_state.get("ex_pool", POOL_TODOS), st.session_state.get("ex_fuentes", FUENTES), claves,
                      st.session_state.get("ex_niveles", NIVELES))
    if not pool:
        st.warning("Ningún ejercicio cumple los filtros seleccionados. Amplíe la selección.", icon=":material/search_off:")
        return
    c3, c4, c5 = st.columns(3)
    with c3:
        maximo = min(_logica.MAX_EJERCICIOS, len(pool))
        minimo = min(_logica.MIN_EJERCICIOS, maximo)
        if minimo < maximo:
            st.slider("Número de ejercicios", minimo, maximo, min(5, maximo), key="ex_n")
        else:
            st.session_state["ex_n"] = maximo
            st.markdown(f"**Número de ejercicios:** {maximo} (todos los disponibles)")
    with c4:
        n = int(st.session_state.get("ex_n", min(5, maximo)))
        st.slider("Duración (minutos)", _logica.MIN_MINUTOS, _logica.MAX_MINUTOS, _logica.duracion_sugerida(n), step=5, key="ex_min",
                  help=f"Sugerencia: {_logica.MINUTOS_POR_EJERCICIO} minutos por ejercicio.")
    with c5:
        st.text_input("Semilla (opcional)", key="ex_semilla", placeholder="Por ejemplo: parcial2",
                      help="La misma semilla y los mismos filtros generan siempre el mismo examen, útil para repetirlo o compartirlo.")
    st.caption(f"{len(pool)} ejercicios cumplen los filtros.")
    st.button("Comenzar examen", key="ex_comenzar", type="primary", icon=":material/play_arrow:", on_click=_iniciar)
    _historial()


@st.fragment(run_every=1)
def _reloj() -> None:
    """Cuenta regresiva. Se actualiza cada segundo sin recalcular el resto de la página."""
    resto = _restante()
    total = st.session_state["ex_dur"]
    st.progress(resto / total if total else 0.0, text=f"Tiempo restante: {_logica.formato_tiempo(resto)}")
    if resto <= 0:
        st.rerun()


def _respondidas(ej) -> int:
    return sum(1 for p in ej.partes if _texto(st.session_state.get(_clave(ej.id, p.clave))))


def _vista_examen() -> None:
    ids = st.session_state["ex_ids"]
    ejs = [ejercicios.buscar(i) for i in ids]
    partes_total = sum(len(e.partes) for e in ejs)
    partes_resp = sum(_respondidas(e) for e in ejs)
    qc.metricas([("Ejercicios", f"{len(ids)}"), ("Partes respondidas", f"{partes_resp} de {partes_total}"),
                 ("Duración", f"{int(st.session_state['ex_dur'] // 60)} min")], columnas=3)
    _reloj()
    st.caption("No hay pistas ni soluciones hasta entregar. Las respuestas se escriben como número (por ejemplo 3.00e-19 o 3,00 x 10^-19) "
               "o se elige una opción.")
    pestanas = st.tabs([f"Ejercicio {i}" + ("  ✓" if _respondidas(e) == len(e.partes) else "") for i, e in enumerate(ejs, 1)])
    for i, (tab, ej) in enumerate(zip(pestanas, ejs), 1):
        with tab:
            qc.seccion(f"Ejercicio {i} de {len(ejs)}  ·  {ej.titulo}")
            st.caption(f"{TEMAS.get(ej.tema, ej.tema)}  ·  Nivel: {ej.dificultad}")
            st.markdown(ej.enunciado)
            if ej.nota:
                st.info(ej.nota, icon=":material/info:")
            for p in ej.partes:
                clave = _clave(ej.id, p.clave)
                if p.tipo == OPC:
                    st.radio(p.etiqueta, p.opciones, index=None, key=clave)
                else:
                    etiqueta = p.etiqueta + (f"  [{p.unidad}]" if p.unidad and "(" not in p.etiqueta else "")
                    st.text_input(etiqueta, key=clave, placeholder="Escriba un número, por ejemplo 3.00e-19 o 3,00 x 10^-19")
    st.markdown("")
    if st.session_state.get("ex_confirmar"):
        sin = partes_total - partes_resp
        st.warning(f"Quedan {sin} partes sin responder. Una vez entregado el examen no se puede modificar." if sin
                   else "Se entregará el examen para su calificación. Una vez entregado no se puede modificar.", icon=":material/warning:")
        c1, c2, _ = st.columns([1, 1, 2])
        c1.button("Confirmar entrega", key="ex_confirmar_si", type="primary", icon=":material/check:", on_click=_entregar, args=("entrega",))
        c2.button("Seguir resolviendo", key="ex_confirmar_no", on_click=_seguir)
    else:
        c1, c2, _ = st.columns([1, 1, 2])
        c1.button("Entregar examen", key="ex_entregar", type="primary", icon=":material/send:", on_click=_pedir_confirmacion)
        c2.button("Cancelar examen", key="ex_cancelar", icon=":material/close:", on_click=_nuevo,
                  help="Descarta el examen sin calificarlo ni registrarlo.")


def _estado_parte(res) -> str:
    return {OK: "Correcta", VACIA: "Sin responder"}.get(res.estado, "Incorrecta")


def _vista_correccion() -> None:
    ent = st.session_state["ex_entrega"]
    ids = st.session_state["ex_ids"]
    cals = ent["cals"]
    correctos = sum(1 for c in cals.values() if c.fraccion >= 0.999)
    if ent["motivo"] == "tiempo":
        st.warning("Se agotó el tiempo: el examen se entregó automáticamente con las respuestas escritas hasta ese momento.",
                   icon=":material/timer_off:")
    qc.metricas([("Nota", f"{ent['nota']:.2f} / {_logica.ESCALA:.1f}"), ("Porcentaje", f"{ent['pct']:.0f} %"),
                 ("Ejercicios correctos", f"{correctos} de {len(ids)}"),
                 ("Tiempo empleado", f"{_logica.formato_tiempo(ent['usados'])} de {_logica.formato_tiempo(st.session_state['ex_dur'])}")],
                columnas=4)
    filas = []
    for i, ej_id in enumerate(ids, 1):
        ej, cal = ejercicios.buscar(ej_id), cals[ej_id]
        resp = sum(1 for r in cal.resultados.values() if r.estado != VACIA)
        filas.append({"N.º": i, "Ejercicio": ej.titulo, "Tema": TEMAS.get(ej.tema, ej.tema),
                      "Resultado": f"{100 * cal.fraccion:.0f} %", "Veredicto": _logica.veredicto(cal.fraccion, resp)})
    st.dataframe(filas, hide_index=True, width="stretch")
    st.caption("Los ejercicios no acertados del todo quedaron en «Mi repaso».")
    qc.seccion("Corrección detallada")
    for i, ej_id in enumerate(ids, 1):
        ej, cal = ejercicios.buscar(ej_id), cals[ej_id]
        with st.expander(f"Ejercicio {i} · {ej.titulo}  —  {100 * cal.fraccion:.0f} %", expanded=cal.fraccion < 0.999 and i == 1):
            st.markdown(ej.enunciado)
            tabla = []
            for p in ej.partes:
                res = cal.resultados[p.clave]
                dado = _texto(ent["respuestas"][ej_id].get(p.clave)) or "—"
                tabla.append({"Parte": p.etiqueta.replace("$", ""), "Su respuesta": dado, "Valor esperado": p.respuesta_correcta().replace("$", ""),
                              "Resultado": _estado_parte(res), "Observación": res.mensaje if res.estado != OK else ""})
            st.dataframe(tabla, hide_index=True, width="stretch")
            st.markdown("**Solución paso a paso**")
            st.markdown(ej.solucion)
    c1, c2, c3 = st.columns(3)
    c1.button("Repetir este examen", key="ex_repetir", icon=":material/replay:", width="stretch", on_click=_repetir)
    c2.button("Nuevo examen", key="ex_nuevo", icon=":material/add:", width="stretch", on_click=_nuevo)
    c3.button("Examen con mis ejercicios por repasar", key="ex_repasar_pend", icon=":material/history_edu:", width="stretch",
              on_click=_preparar_repaso, disabled=not _estado.repasar())


def _historial() -> None:
    hist = _estado.historial()
    if not hist:
        return
    qc.seccion("Historial de exámenes")
    st.dataframe([{"Fecha": h["fecha"], "Ejercicios": len(h["ejercicios"]), "Nota": f"{h['nota']:.2f}", "Porcentaje": f"{h['porcentaje']:.0f} %",
                   "Tiempo": f"{h['minutos_usados']:.0f} de {h['minutos_totales']:.0f} min", "Temas": ", ".join(h["temas"])}
                  for h in reversed(hist)], hide_index=True, width="stretch")
    if len(hist) >= 2:
        st.line_chart({"Nota": [h["nota"] for h in hist]}, y_label="Nota (0 a 5)", x_label="Examen n.º")


def interfaz() -> None:
    """Página «Modo examen»."""
    st.session_state.setdefault("ex_fase", "config")
    qc.encabezado_pagina("Evaluación", "Modo examen",
                         "Simulacro cronometrado con ejercicios de la colección de práctica, sin pistas ni soluciones durante la prueba, "
                         "con calificación sobre 5.0 y corrección completa al entregarlo.")
    qc.escribir_en_url(None)
    fase = st.session_state["ex_fase"]
    if fase == "curso" and _restante() <= 0:
        _entregar("tiempo")
        fase = "fin"
    if fase == "curso":
        _vista_examen()
    elif fase == "fin":
        _vista_correccion()
    else:
        _vista_configuracion()


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def ejecutar_pruebas() -> "qc.RegistroPruebas":
    reg = qc.RegistroPruebas("Modo examen")
    ids = [e.id for e in ejercicios.EJERCICIOS if e.comprobable]
    a, b = _logica.seleccionar(ids, 6, "s"), _logica.seleccionar(ids, 6, "s")
    reg.comprobar("Misma semilla → mismo examen", a == b and len(set(a)) == 6)
    reg.comprobar("Otra semilla → otro examen", a != _logica.seleccionar(ids, 6, "t"))
    reg.comprobar("Nunca se piden más ejercicios que los disponibles", len(_logica.seleccionar(ids[:2], 9, "x")) == 2)
    reg.comprobar("Todo correcto → 5.0", _logica.nota([1, 1, 1]) == (5.0, 100.0))
    reg.comprobar("Mitad de crédito → 2.5", _logica.nota([1, 0, 0.5, 0.5]) == (2.5, 50.0))
    reg.comprobar("Formato del tiempo", _logica.formato_tiempo(65) == "01:05" and _logica.formato_tiempo(3725) == "1:02:05")
    reg.comprobar("El tiempo nunca es negativo", _logica.restante(0, 60, 100) == 0.0)
    reg.comprobar("Un examen con todas las respuestas correctas obtiene 5.0",
                  _logica.nota(calificar(e, ejercicios.respuestas_correctas(e)).fraccion for e in ejercicios.EJERCICIOS[:5])[0] == 5.0)
    return reg
