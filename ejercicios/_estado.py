"""
ejercicios/_estado.py — Estado de sesión del estudiante, compartido por Ejercicios, Modo examen y Mi repaso.

Guarda qué ejercicios están resueltos, cuáles quedan por repasar, la bitácora de intentos y el historial de exámenes.
Los dos conjuntos de ejercicios viajan en la dirección de la página (`prog` y `rev`, ver `_progreso`); la bitácora y los exámenes
solo viven en la sesión y en la copia de seguridad.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from ejercicios import _bitacora, _progreso


def _ids() -> tuple:
    import ejercicios
    return ejercicios.IDS


def _conjunto(clave_estado: str, clave_url: str) -> set:
    if clave_estado not in st.session_state:
        codigo = st.session_state.get(f"ql_fijo_{clave_url}") or st.query_params.get(clave_url)
        st.session_state[clave_estado] = _progreso.decodificar(codigo, _ids())
    return st.session_state[clave_estado]


def hechos() -> set:
    """Ejercicios resueltos (acertados al comprobar o marcados a mano)."""
    return _conjunto("ej_hechos", "prog")


def repasar() -> set:
    """Ejercicios por repasar: comprobados sin acertar del todo, o cuya solución se abrió sin haberlos resuelto."""
    return _conjunto("ej_repasar", "rev")


def marcas() -> set:
    """Marcas de la Ruta de estudio: «teoría leída» y «mini-examen aprobado» (ver `_ruta`)."""
    from ejercicios import _ruta
    if "ej_ruta" not in st.session_state:
        codigo = st.session_state.get("ql_fijo_rut") or st.query_params.get("rut")
        st.session_state["ej_ruta"] = _progreso.decodificar(codigo, _ruta.todas_las_marcas())
    return st.session_state["ej_ruta"]


def marcar_ruta(marca: str, valor: bool = True) -> None:
    (marcas().add if valor else marcas().discard)(marca)
    guardar_url()


def bitacora() -> dict:
    return st.session_state.setdefault("ej_bitacora", {})


def historial() -> list:
    return st.session_state.setdefault("ex_historial", [])


def guardar_url() -> None:
    ids = _ids()
    st.session_state["ql_fijo_prog"] = _progreso.codificar(hechos(), ids)
    st.session_state["ql_fijo_rev"] = _progreso.codificar(repasar(), ids)
    from ejercicios import _ruta
    st.session_state["ql_fijo_rut"] = _progreso.codificar(marcas(), _ruta.todas_las_marcas())


def marcar(ej_id: str, resuelto: bool) -> None:
    if resuelto:
        hechos().add(ej_id)
        repasar().discard(ej_id)
    else:
        hechos().discard(ej_id)
    guardar_url()


def registrar_calificacion(ej_id: str, calificacion) -> bool:
    """Anota una comprobación (o la corrección de un examen). Devuelve True si fue completamente correcta."""
    completo = _bitacora.registrar_intento(bitacora(), ej_id, calificacion)
    if completo:
        hechos().add(ej_id)
        repasar().discard(ej_id)
    else:
        repasar().add(ej_id)
    guardar_url()
    return completo


def registrar_solucion(ej_id: str) -> None:
    _bitacora.registrar_solucion(bitacora(), ej_id)
    if ej_id not in hechos():
        repasar().add(ej_id)
    guardar_url()


def registrar_examen(ejercicios_ids, nota: float, porcentaje: float, usados_s: float, total_s: float, temas) -> None:
    historial().append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "ejercicios": list(ejercicios_ids),
                        "nota": round(nota, 2), "porcentaje": round(porcentaje, 1),
                        "minutos_usados": round(usados_s / 60, 1), "minutos_totales": round(total_s / 60, 1),
                        "temas": sorted(set(temas))})


def estado_de(ej_id: str) -> str:
    if ej_id in hechos():
        return "Resuelto"
    if ej_id in repasar():
        return "Por repasar"
    return "Sin intentar"


def borrar_todo() -> None:
    hechos().clear()
    repasar().clear()
    bitacora().clear()
    historial().clear()
    marcas().clear()
    st.session_state.get("ej_res", {}).clear()
    guardar_url()


def copia_json() -> str:
    return _progreso.a_json(hechos(), _ids(), repasar(), bitacora(), historial(), marcas())


def cargar_copia(datos: bytes | str) -> str:
    """Combina un archivo exportado con lo que ya hay. Devuelve un mensaje de resultado; lanza ValueError si el archivo no sirve."""
    from ejercicios import _ruta
    copia = _progreso.leer_copia(datos, _ids(), _ruta.todas_las_marcas())
    antes = len(hechos())
    hechos().update(copia["resueltos"])
    repasar().update(copia["repasar"])
    repasar().difference_update(hechos())
    st.session_state["ej_bitacora"] = _bitacora.combinar(bitacora(), copia["bitacora"])
    historial().extend(x for x in copia["examenes"] if x not in historial())
    marcas().update(copia["ruta"])
    guardar_url()
    return (f"Se cargaron {len(copia['resueltos'])} ejercicios resueltos ({len(hechos()) - antes} nuevos), "
            f"{len(copia['repasar'])} por repasar y {len(copia['examenes'])} exámenes.")
