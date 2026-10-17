"""
tutor — Tutor de errores conceptuales de QUANTUM LAB
====================================================

Identifica confusiones frecuentes (amplitud con probabilidad, intensidad con energía del fotón, estacionario con reposo…) y ofrece primero una pista y
después la explicación. Dos entradas:

    Revisar mi explicación    el estudiante escribe con sus palabras y un detector BASADO EN REGLAS busca formulaciones típicas de cada confusión
    Preguntas de diagnóstico  opción múltiple donde cada distractor corresponde a una confusión concreta; al fallar, pista y explicación de esa confusión

También hay un catálogo de las confusiones y un resumen de progreso (solo durante la sesión; no se guarda al cerrar la pestaña).

Límites declarados: el detector no entiende el lenguaje, solo reconoce formulaciones frecuentes; que no encuentre nada NO significa que la explicación sea correcta.

Archivos: _modelo.py (Concepcion, PreguntaDiag) · _errores.py (catálogo + `detectar`) · _preguntas.py (preguntas de diagnóstico)
Cómo añadir una confusión: agregar una `Concepcion` a `_errores.CONCEPCIONES` con sus reglas, frases_error (deben detectarse) y frases_correctas (no deben);
`ejecutar_pruebas` comprueba ambas listas. Para usarla en una pregunta, apuntar un distractor a su id en `_preguntas.py`.
"""

from __future__ import annotations

import streamlit as st

import quantum_lab_comun as qc
from biblioteca import _botones_enlace, _glosario
from tutor import _errores, _preguntas


def _perfil() -> dict:
    return st.session_state.setdefault("tut_perfil", {})


def _respuestas() -> dict:
    return st.session_state.setdefault("tut_resp", {})


def _anotar(concepcion_id: str) -> None:
    perfil = _perfil()
    perfil[concepcion_id] = perfil.get(concepcion_id, 0) + 1


def _abrir_biblioteca(termino: str) -> None:
    st.session_state["ql_pagina"] = "biblioteca"
    st.session_state["bib_busqueda"] = termino


def _tarjeta(c, prefijo: str, abierta: bool = False, enlaces: bool = True) -> None:
    """Pista primero; la explicación completa queda en un desplegable."""
    st.markdown(f"**{c.concepto}.** Parece que se piensa que: *{c.error}*")
    st.info(f"**Pista.** {c.pista}", icon=":material/tips_and_updates:")
    with st.expander("Ver la explicación", expanded=abierta):
        st.markdown(c.explicacion)
        if c.contraste:
            st.latex(c.contraste)
        if c.glosario and enlaces:
            nombres = [_glosario.POR_ID[g].nombre for g in c.glosario]
            st.caption("Conceptos relacionados: " + " · ".join(nombres))
            st.button("Buscar en la biblioteca", key=f"tut_bib_{prefijo}_{c.id}", icon=":material/local_library:",
                      on_click=_abrir_biblioteca, args=(nombres[0],))
        if enlaces:
            _botones_enlace(f"tut_{prefijo}_{c.id}", c.tema, c.simulador)


# ---------------------------------------------------------------------
# Revisar mi explicación
# ---------------------------------------------------------------------
def _usar_ejemplo() -> None:
    st.session_state["tut_texto"] = st.session_state.get("tut_ejemplo", "")


def _pestana_revisar() -> None:
    st.markdown("Explica con tus palabras un concepto (por ejemplo, qué es la función de onda o qué cambia al aumentar la intensidad de la luz). "
                "El tutor busca formulaciones frecuentes de confusiones y te da una pista.")
    ejemplos = [f for c in _errores.CONCEPCIONES[:8] for f in c.frases_error[:1]]
    with st.expander("¿No sabes qué escribir? Prueba con un ejemplo"):
        st.selectbox("Frase de ejemplo", ejemplos, key="tut_ejemplo")
        st.button("Usar este ejemplo", key="tut_usar", on_click=_usar_ejemplo)
    st.text_area("Tu explicación", key="tut_texto", height=130, max_chars=1500,
                 placeholder="Por ejemplo: «La función de onda es la probabilidad de encontrar la partícula.»")
    if st.button("Revisar", key="tut_revisar", type="primary", icon=":material/fact_check:"):
        texto = st.session_state.get("tut_texto", "")
        if not texto.strip():
            st.warning("Escribe primero una explicación.")
            return
        halladas = _errores.detectar(texto)
        st.session_state["tut_halladas"] = [c.id for c in halladas]
        for c in halladas:
            _anotar(c.id)
        st.session_state["tut_revisado"] = texto
    if "tut_revisado" not in st.session_state:
        return
    ids = st.session_state.get("tut_halladas", [])
    st.divider()
    if not ids:
        st.success("No encontré ninguna de las confusiones del catálogo en tu texto.", icon=":material/check_circle:")
        st.caption("Ojo: el detector solo reconoce formulaciones frecuentes. Que no encuentre nada no significa que la explicación sea correcta. "
                   "Para comprobarlo, contrasta con el glosario o responde las preguntas de diagnóstico.")
        return
    st.markdown(f"**Encontré {len(ids)} posible{'s' if len(ids) != 1 else ''} confusión{'es' if len(ids) != 1 else ''}:**")
    for i in ids:
        with st.container(border=True):
            _tarjeta(_errores.POR_ID[i], "r")


# ---------------------------------------------------------------------
# Preguntas de diagnóstico
# ---------------------------------------------------------------------
def _comprobar(q) -> None:
    op = st.session_state.get(f"tut_op_{q.id}")
    if op is None:
        return
    _, concepcion = q.opciones[op]
    ok = op == q.correcta
    _respuestas()[q.id] = {"op": op, "ok": ok}
    if not ok and concepcion:
        _anotar(concepcion)


def _pestana_preguntas() -> None:
    resp = _respuestas()
    st.markdown(f"{len(_preguntas.PREGUNTAS)} preguntas cortas. Cada respuesta incorrecta corresponde a una confusión frecuente: si te equivocas, primero "
                "recibes una pista y puedes volver a intentarlo.")
    ids = [q.id for q in _preguntas.PREGUNTAS]

    def etiqueta(i: str) -> str:
        n = ids.index(i) + 1
        marca = "" if i not in resp else ("✓ " if resp[i]["ok"] else "· ")
        return f"{marca}{n}. {_preguntas.POR_ID[i].enunciado[:70]}…"

    elegida = st.selectbox("Pregunta", ids, key="tut_pregunta", format_func=etiqueta)
    q = _preguntas.POR_ID[elegida]
    st.markdown(f"**{q.enunciado}**")
    op = st.radio("Respuesta", range(len(q.opciones)), index=None, key=f"tut_op_{q.id}", format_func=lambda i: q.opciones[i][0], label_visibility="collapsed")
    st.button("Comprobar", key=f"tut_comp_{q.id}", type="primary", icon=":material/check:", on_click=_comprobar, args=(q,), disabled=op is None)
    previo = resp.get(q.id)
    if previo is None or previo["op"] != op:
        return
    if previo["ok"]:
        st.success("Correcto.", icon=":material/check_circle:")
        st.markdown(q.explicacion)
        return
    concepcion = q.opciones[op][1]
    if concepcion:
        st.warning("Esa respuesta refleja una confusión frecuente.", icon=":material/priority_high:")
        _tarjeta(_errores.POR_ID[concepcion], f"q_{q.id}")
    else:
        st.warning("No es correcta.", icon=":material/priority_high:")
        st.info(f"**Pista.** {q.pista_general}", icon=":material/tips_and_updates:")
    with st.expander("Ver la solución de esta pregunta"):
        st.markdown(f"**Respuesta correcta:** {q.opciones[q.correcta][0]}")
        st.markdown(q.explicacion)
        _botones_enlace(f"tut_sol_{q.id}", q.tema, "")


# ---------------------------------------------------------------------
# Catálogo y progreso
# ---------------------------------------------------------------------
def _pestana_catalogo() -> None:
    st.markdown(f"Las {len(_errores.CONCEPCIONES)} confusiones que reconoce el tutor. Léelas como una lista de comprobación antes de un examen.")
    for c in _errores.CONCEPCIONES:
        with st.expander(c.concepto):
            _tarjeta(c, "c", enlaces=False)


def _reiniciar() -> None:
    for k in ("tut_perfil", "tut_resp", "tut_halladas", "tut_revisado"):
        st.session_state.pop(k, None)


def _pestana_progreso() -> None:
    resp, perfil = _respuestas(), _perfil()
    total = len(_preguntas.PREGUNTAS)
    correctas = sum(1 for r in resp.values() if r["ok"])
    qc.metricas([("Preguntas contestadas", f"{len(resp)} de {total}"), ("Con respuesta correcta", str(correctas)),
                 ("Confusiones detectadas", str(sum(perfil.values())))], columnas=3)
    if not perfil:
        st.info("Aún no hay confusiones registradas. Responde preguntas o revisa una explicación.", icon=":material/info:")
    else:
        qc.seccion("Conceptos para reforzar")
        for i, n in sorted(perfil.items(), key=lambda kv: -kv[1]):
            c = _errores.POR_ID[i]
            st.markdown(f"- **{c.concepto}** ({n} {'vez' if n == 1 else 'veces'}): {c.pista}")
    st.caption("El progreso vive solo en esta sesión del navegador; se pierde al cerrar o recargar la pestaña.")
    st.button("Reiniciar progreso", key="tut_reiniciar", on_click=_reiniciar, icon=":material/restart_alt:")


def interfaz() -> None:
    """Página «Tutor de errores conceptuales»."""
    qc.encabezado_pagina("Herramientas de estudio", "Tutor de errores conceptuales",
                         "Detecta confusiones frecuentes, como tomar la amplitud por una probabilidad o la intensidad por la energía del fotón, "
                         "y ofrece primero una pista y luego la explicación.")
    qc.escribir_en_url(None)
    t1, t2, t3, t4 = st.tabs(["Revisar mi explicación", "Preguntas de diagnóstico", "Catálogo", "Mi progreso"])
    with t1:
        _pestana_revisar()
    with t2:
        _pestana_preguntas()
    with t3:
        _pestana_catalogo()
    with t4:
        _pestana_progreso()


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def _llaves_balanceadas(latex: str) -> bool:
    limpio = latex.replace(r"\{", "").replace(r"\}", "")
    return limpio.count("{") == limpio.count("}") and latex.count(r"\left") == latex.count(r"\right")


def ejecutar_pruebas() -> "qc.RegistroPruebas":
    import quantum_lab_portada as portada
    import teoria

    paginas = {m[0] for m in portada.MODULOS}

    reg = qc.RegistroPruebas("Tutor de errores conceptuales")
    ids = [c.id for c in _errores.CONCEPCIONES]
    reg.comprobar("Los identificadores de confusiones son únicos", len(ids) == len(set(ids)))
    reg.comprobar("Cada confusión tiene pista, explicación y al menos una frase de ejemplo",
                  all(c.pista and len(c.explicacion) > 60 and c.frases_error for c in _errores.CONCEPCIONES))
    reg.comprobar("Las confusiones citan conceptos, temas y simuladores existentes",
                  all(all(g in _glosario.POR_ID for g in c.glosario) and (not c.tema or teoria.buscar(c.tema)) and (not c.simulador or c.simulador in paginas)
                      for c in _errores.CONCEPCIONES))
    reg.comprobar("Los contrastes tienen LaTeX balanceado", all(_llaves_balanceadas(c.contraste) for c in _errores.CONCEPCIONES))
    fallos_error = [(c.id, f) for c in _errores.CONCEPCIONES for f in c.frases_error if c not in _errores.detectar(f)]
    reg.comprobar("El detector reconoce todas las frases de error de ejemplo", not fallos_error, str(fallos_error[:3]))
    falsos = [(c.id, f) for c in _errores.CONCEPCIONES for f in c.frases_correctas if c in _errores.detectar(f)]
    reg.comprobar("El detector no marca las frases correctas parecidas", not falsos, str(falsos[:3]))
    reg.comprobar("Un texto vacío no detecta nada", _errores.detectar("") == [])
    reg.comprobar("Las preguntas tienen identificador único", len({q.id for q in _preguntas.PREGUNTAS}) == len(_preguntas.PREGUNTAS))
    reg.comprobar("En cada pregunta la opción correcta no apunta a ninguna confusión y los distractores citan confusiones existentes",
                  all(q.opciones[q.correcta][1] is None and all(c is None or c in _errores.POR_ID for _, c in q.opciones) for q in _preguntas.PREGUNTAS))
    reg.comprobar("Toda pregunta tiene al menos un distractor ligado a una confusión", all(any(c for _, c in q.opciones) for q in _preguntas.PREGUNTAS))
    reg.comprobar("Toda confusión del catálogo aparece como distractor de alguna pregunta",
                  set(ids) <= {c for q in _preguntas.PREGUNTAS for _, c in q.opciones if c})
    reg.comprobar("Los temas de las preguntas existen", all(teoria.buscar(q.tema) for q in _preguntas.PREGUNTAS))
    return reg
