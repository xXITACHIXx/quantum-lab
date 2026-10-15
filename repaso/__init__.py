"""
repaso — «Mi repaso» de QUANTUM LAB
===================================

Panel personal construido con el registro de intentos de los Ejercicios de práctica y del Modo examen: ejercicios por repasar,
temas con menor precisión y errores más frecuentes detectados por el calificador. Todo se calcula en la sesión del estudiante.
"""

from __future__ import annotations

import streamlit as st

import ejercicios
import examen
import quantum_lab_comun as qc
import teoria
from ejercicios import _bitacora, _estado
from ejercicios._modelo import TEMAS

MIN_INTENTOS_TEMA = 2            # un tema solo se señala como débil con al menos esta cantidad de comprobaciones


def motivo(ej_id: str) -> str:
    reg = _estado.bitacora().get(ej_id, {"intentos": 0, "solucion": 0})
    partes = []
    if reg["intentos"]:
        partes.append("comprobado sin acertar del todo" if ej_id not in _estado.hechos() else "comprobado")
    if reg["solucion"]:
        partes.append("solución consultada")
    return " y ".join(partes).capitalize() or "Marcado para repasar"


def temas_debiles(filas: list[dict], minimo: int = MIN_INTENTOS_TEMA) -> list[dict]:
    """Temas con al menos `minimo` comprobaciones, de menor a mayor precisión."""
    return sorted((f for f in filas if f["intentos"] >= minimo and f["precision"] is not None), key=lambda f: (f["precision"], -f["intentos"]))


def _abrir_ejercicio(ej_id: str) -> None:
    ejercicios._limpiar_filtros()
    st.session_state.update(ql_pagina="ejercicios", ej_sel=ej_id)


def _examen_con_pendientes() -> None:
    examen._preparar_repaso()
    st.session_state["ql_pagina"] = "examen"


def _ir(pagina: str) -> None:
    st.session_state["ql_pagina"] = pagina


def _por_repasar() -> None:
    qc.seccion("Ejercicios por repasar")
    pend = [ejercicios.buscar(i) for i in ejercicios.IDS if i in _estado.repasar()]
    if not pend:
        st.success("No hay ejercicios por repasar.", icon=":material/check_circle:")
        return
    st.markdown("Quedan aquí los ejercicios que se comprobaron sin acertar del todo y aquellos cuya solución se consultó sin haberlos "
                "resuelto. Salen de la lista al responderlos correctamente o al marcarlos como resueltos.")
    st.dataframe([{"Ejercicio": e.titulo, "Fuente": e.fuente, "Tema": TEMAS.get(e.tema, e.tema), "Nivel": e.dificultad,
                   "Motivo": motivo(e.id)} for e in pend], hide_index=True, width="stretch")
    c1, c2, c3 = st.columns([3, 1.4, 1.8], vertical_alignment="bottom")
    ids = [e.id for e in pend]
    c1.selectbox("Abrir un ejercicio por repasar", ids, key="rp_sel", format_func=lambda i: ejercicios.buscar(i).titulo)
    c2.button("Abrir ejercicio", key="rp_abrir", icon=":material/arrow_forward:", width="stretch",
              on_click=_abrir_ejercicio, args=(st.session_state.get("rp_sel", ids[0]),))
    c3.button("Examen con estos ejercicios", key="rp_examen", icon=":material/history_edu:", width="stretch",
              on_click=_examen_con_pendientes)


def _por_tema() -> None:
    filas = _bitacora.por_tema(_estado.bitacora(), ejercicios.EJERCICIOS, _estado.hechos(), _estado.repasar())
    qc.seccion("Rendimiento por tema")
    st.dataframe([{"Tema": TEMAS.get(f["tema"], f["tema"]), "Ejercicios": f["ejercicios"], "Resueltos": f["resueltos"],
                   "Por repasar": f["por_repasar"], "Comprobaciones": f["intentos"],
                   "Precisión": f["precision"]} for f in sorted(filas, key=lambda f: TEMAS.get(f["tema"], f["tema"]))],
                 hide_index=True, width="stretch",
                 column_config={"Precisión": st.column_config.ProgressColumn("Precisión", format="percent", min_value=0.0, max_value=1.0,
                                                                              help="Comprobaciones completamente correctas entre las realizadas.")})
    debiles = temas_debiles(filas)[:3]
    if debiles:
        st.markdown("**Temas con menor precisión** (con al menos "
                    f"{MIN_INTENTOS_TEMA} comprobaciones): " + ", ".join(f"{TEMAS[f['tema']]} ({100 * f['precision']:.0f} %)" for f in debiles) + ".")
        for f in debiles:
            hallado = teoria.buscar(f["tema"])
            if hallado and hallado[1].estado == teoria.DISPONIBLE:
                st.button(f"Repasar la teoría: {hallado[1].titulo}", key=f"rp_teoria_{f['tema']}", icon=":material/menu_book:",
                          on_click=qc.ir_a_tema, args=(f["tema"],))


def _errores() -> None:
    qc.seccion("Errores más frecuentes")
    bit = _estado.bitacora()
    frecuentes = _bitacora.errores_frecuentes(bit)
    ninguno = _bitacora.sin_patron(bit)
    if not frecuentes and not ninguno:
        st.markdown("Aún no hay errores registrados.")
        return
    st.markdown("El calificador reconoce los errores típicos (factor 2π, unidades, factor 2, signo, confusiones propias de cada ejercicio). "
                "Estos son los que se han detectado en sus respuestas:")
    for mensaje, veces, ids in frecuentes[:8]:
        titulos = "; ".join(ejercicios.buscar(i).titulo for i in ids[:3]) + ("…" if len(ids) > 3 else "")
        st.markdown(f"- **{veces} {'vez' if veces == 1 else 'veces'}.** {mensaje}  \n  *Ejercicios: {titulos}.*")
    if ninguno:
        st.caption(f"Además, {ninguno} {'respuesta incorrecta' if ninguno == 1 else 'respuestas incorrectas'} no coincidieron con ningún error "
                   "típico conocido; en esos casos, la solución paso a paso muestra el procedimiento completo.")


def interfaz() -> None:
    """Página «Mi repaso»."""
    qc.encabezado_pagina("Evaluación", "Mi repaso",
                         "Resumen personal de la práctica: ejercicios por repasar, temas con menor precisión y errores más frecuentes, "
                         "a partir de las comprobaciones y los exámenes realizados.")
    qc.escribir_en_url(None)
    bit = _estado.bitacora()
    intentos, aciertos = _bitacora.totales(bit)
    precision = f"{100 * aciertos / intentos:.0f} %" if intentos else "—"
    qc.metricas([("Resueltos", f"{len(_estado.hechos())} de {len(ejercicios.EJERCICIOS)}"), ("Por repasar", f"{len(_estado.repasar())}"),
                 ("Comprobaciones", f"{intentos}"), ("Precisión", precision, "Comprobaciones completamente correctas entre las realizadas."),
                 ("Exámenes", f"{len(_estado.historial())}")], columnas=5)
    if not intentos and not _estado.repasar() and not _estado.historial() and not _estado.hechos():
        st.info("Aún no hay actividad registrada. El panel se completa al comprobar respuestas en los Ejercicios de práctica o al realizar un examen.",
                icon=":material/info:")
        c1, c2, _ = st.columns([1, 1, 2])
        c1.button("Ir a los ejercicios", key="rp_ir_ej", icon=":material/calculate:", width="stretch", on_click=_ir, args=("ejercicios",))
        c2.button("Hacer un examen", key="rp_ir_ex", icon=":material/timer:", width="stretch", on_click=_ir, args=("examen",))
    else:
        _por_repasar()
        _por_tema()
        _errores()
        examen._historial()
    ejercicios.copia_de_seguridad("rp")


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def ejecutar_pruebas() -> "qc.RegistroPruebas":
    from talleres._calificar import CASI, MAL, OK, Resultado
    from talleres._modelo import Calificacion

    reg = qc.RegistroPruebas("Mi repaso")
    bit: dict = {}
    mal = Calificacion({"a": Resultado(MAL, "x"), "b": Resultado(CASI, "falta 2π")}, 0.0, 1.0)
    bien = Calificacion({"a": Resultado(OK, "ok")}, 1.0, 1.0)
    _bitacora.registrar_intento(bit, "s1_lyman", mal)
    _bitacora.registrar_intento(bit, "s1_lyman", mal)
    _bitacora.registrar_intento(bit, "s1_lyman", bien)
    reg.comprobar("Intentos y aciertos", _bitacora.totales(bit) == (3, 1))
    reg.comprobar("Error típico contado", _bitacora.errores_frecuentes(bit) == [("falta 2π", 2, ["s1_lyman"])])
    reg.comprobar("Respuestas sin patrón contadas aparte", _bitacora.sin_patron(bit) == 2)
    reg.comprobar("Combinar bitácoras suma contadores", _bitacora.combinar(bit, bit)["s1_lyman"]["intentos"] == 6)
    reg.comprobar("Depurar descarta ids y contadores inválidos",
                  _bitacora.depurar({"s1_lyman": {"intentos": -3, "errores": {"x": "y"}}, "no_existe": {}}, ejercicios.IDS)
                  == {"s1_lyman": {"intentos": 0, "aciertos": 0, "solucion": 0, "errores": {}}})
    return reg
