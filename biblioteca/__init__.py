"""
biblioteca — Biblioteca científica de QUANTUM LAB
=================================================

Material de consulta conectado con el resto del laboratorio:

    Glosario        48 conceptos con definición, ecuación, advertencia de error frecuente y enlaces a teoría y simulador
    Derivaciones    9 deducciones paso a paso; cada una termina con una comprobación numérica contra el código del laboratorio
    Conexiones      mapa de relaciones entre conceptos (qué lleva a qué) y vecindad de cada concepto
    Referencias     libros, artículos originales, datos y simulaciones de referencia
    Búsqueda        un solo cuadro que consulta glosario y formulario

Archivos: _modelo.py (dataclasses) · _glosario.py · _derivaciones.py · _referencias.py · _conexiones.py
Cómo añadir un término: agregar `T(id, nombre, definicion, ecuacion, relacionados, tema, simulador, cuidado)` a `_glosario.TERMINOS`;
`ejecutar_pruebas` comprueba que las referencias cruzadas, temas y simuladores existan.
"""

from __future__ import annotations

import streamlit as st

import quantum_lab_comun as qc
import teoria
from biblioteca import _conexiones, _derivaciones, _glosario, _referencias


TODOS = "Todos los temas"
MAX_VISIBLES = 12      # el glosario completo se muestra con un interruptor: cada concepto lleva ecuación y botones


def _abrir(pagina: str) -> None:
    st.session_state["ql_pagina"] = pagina


def _nombre_pagina(pagina: str) -> str:
    import quantum_lab_portada as portada      # no importar quantum_lab aquí: se ejecutaría de nuevo como script
    return portada.modulo(pagina)[4]


def _botones_enlace(prefijo: str, tema: str, simulador: str) -> None:
    """Botones «Ver la teoría» y «Abrir el simulador», solo si el destino existe y tiene contenido."""
    hallado = teoria.buscar(tema) if tema else None
    hay_teoria = hallado is not None and hallado[1].estado == teoria.DISPONIBLE
    if not (hay_teoria or simulador):
        return
    cols = st.columns(2)
    if hay_teoria:
        cols[0].button("Ver la teoría", key=f"bib_t_{prefijo}", icon=":material/menu_book:", on_click=qc.ir_a_tema, args=(tema,))
    if simulador:
        cols[1].button(f"Abrir: {_nombre_pagina(simulador)}", key=f"bib_s_{prefijo}", icon=":material/science:",
                       on_click=_abrir, args=(simulador,))


# ---------------------------------------------------------------------
# Glosario
# ---------------------------------------------------------------------
def _tarjeta_termino(t, prefijo: str) -> None:
    st.markdown(t.definicion)
    if t.ecuacion:
        st.latex(t.ecuacion)
    if t.cuidado:
        st.warning(t.cuidado, icon=":material/priority_high:")
    if t.relacionados:
        nombres = [_glosario.POR_ID[r].nombre for r in t.relacionados]
        st.caption("Relacionado con: " + " · ".join(nombres))
    _botones_enlace(f"{prefijo}_{t.id}", t.tema, t.simulador)


def _pestana_glosario() -> None:
    texto = st.text_input("Buscar en la biblioteca", key="bib_busqueda", placeholder="Por ejemplo: fase, intensidad, nodo, hamiltoniano",
                          help="Busca en el glosario (nombre, definición y ecuación) y en el formulario.")
    terminos = _glosario.buscar(texto)
    temas = sorted({t.tema for t in terminos if t.tema})
    tema = st.selectbox("Filtrar por tema", [TODOS] + temas, key="bib_tema", format_func=lambda i: i if i == TODOS else teoria.buscar(i)[1].titulo)
    if tema != TODOS:
        terminos = [t for t in terminos if t.tema == tema]
    terminos = sorted(terminos, key=lambda x: x.nombre.lower())
    todos = st.toggle("Mostrar todos los resultados", key="bib_todos", value=False) if len(terminos) > MAX_VISIBLES else True
    st.caption(f"{len(terminos)} de {len(_glosario.TERMINOS)} conceptos" + (f" para «{texto.strip()}»" if texto.strip() else "")
               + ("" if todos or len(terminos) <= MAX_VISIBLES else f" · se muestran {MAX_VISIBLES}"))
    for t in (terminos if todos else terminos[:MAX_VISIBLES]):
        with st.expander(t.nombre):
            _tarjeta_termino(t, "g")
    if texto.strip():
        import formulario
        hallazgos = formulario.buscar_formulas(texto)
        if hallazgos:
            qc.seccion(f"En el formulario ({len(hallazgos)})")
            for s, b, f in hallazgos[:12]:
                with st.expander(f"{f.nombre}  ·  {s.titulo}"):
                    st.latex(f.latex)
                    if f.nota:
                        st.caption(f.nota)
            if len(hallazgos) > 12:
                st.caption("Hay más resultados: se pueden ver todos en la página Formulario.")
            st.button("Abrir el formulario", key="bib_formulario", icon=":material/functions:", on_click=_abrir, args=("formulario",))
        if not terminos and not hallazgos:
            st.info("Sin resultados. Prueba con una palabra más corta o sin tildes.")


# ---------------------------------------------------------------------
# Derivaciones
# ---------------------------------------------------------------------
def _comprobacion(d) -> None:
    descripcion, calculado, referencia, unidad = d.comprobacion()
    dif = abs(calculado - referencia) / abs(referencia) if referencia else abs(calculado - referencia)
    qc.seccion("Comprobación numérica")
    st.caption(descripcion)
    c1, c2, c3 = st.columns(3)
    c1.metric("Código del laboratorio", f"{calculado:.6g}")
    c2.metric("Referencia independiente", f"{referencia:.6g}")
    c3.metric("Diferencia relativa", f"{dif:.1e}")
    st.caption("Unidad: " + (f"${unidad}$" if unidad else "adimensional") + ". La referencia se calcula por otra vía "
               "(otra expresión equivalente, una integral numérica o un valor medido), no repitiendo la misma fórmula.")


def _pestana_derivaciones() -> None:
    ids = [d.id for d in _derivaciones.DERIVACIONES]
    elegido = st.selectbox("Derivación", ids, key="bib_derivacion", format_func=lambda i: _derivaciones.POR_ID[i].titulo)
    d = _derivaciones.POR_ID[elegido]
    for i, paso in enumerate(d.pasos, 1):
        st.markdown(f"**Paso {i}.** {paso.texto}")
        st.latex(paso.latex)
    st.success(d.conclusion, icon=":material/check_circle:")
    if d.comprobacion:
        _comprobacion(d)
    _botones_enlace(f"d_{d.id}", d.tema, d.simulador)


# ---------------------------------------------------------------------
# Conexiones
# ---------------------------------------------------------------------
def _pestana_conexiones() -> None:
    st.markdown("Cada flecha dice cómo se relacionan dos conceptos. Elige uno para ver de dónde viene y a dónde lleva.")
    ids = sorted(_glosario.POR_ID, key=lambda i: _glosario.POR_ID[i].nombre.lower())
    elegido = st.selectbox("Concepto", ids, key="bib_concepto", format_func=lambda i: _glosario.POR_ID[i].nombre)
    sal, ent = _conexiones.vecinos(elegido)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Se apoya en**")
        for otro, et in ent:
            st.markdown(f"- {_glosario.POR_ID[otro].nombre} *({et})*")
        if not ent:
            st.caption("Es un concepto de partida en este mapa.")
    with c2:
        st.markdown("**Lleva a**")
        for otro, et in sal:
            st.markdown(f"- *{et}* → {_glosario.POR_ID[otro].nombre}")
        if not sal:
            st.caption("No tiene conexiones salientes en este mapa.")
    vecindad = {elegido} | {o for o, _ in sal} | {o for o, _ in ent}
    if len(vecindad) > 1:
        st.graphviz_chart(_conexiones.dot(vecindad), width="stretch")
    with st.expander("Ver el mapa completo"):
        st.graphviz_chart(_conexiones.dot(), width="stretch")
    st.caption("El mapa es una guía de estudio elaborada para este curso, no una clasificación oficial.")


# ---------------------------------------------------------------------
# Referencias
# ---------------------------------------------------------------------
def _pestana_referencias() -> None:
    tipos = []
    for r in _referencias.REFERENCIAS:
        if r.tipo not in tipos:
            tipos.append(r.tipo)
    for tipo in tipos:
        qc.seccion(tipo)
        for r in (x for x in _referencias.REFERENCIAS if x.tipo == tipo):
            enlace = f" [Abrir]({r.enlace})" if r.enlace else ""
            st.markdown(f"{r.cita}{enlace}  \n*Para qué sirve:* {r.para}")
    st.caption("Las referencias de simulaciones indican qué idea didáctica se adoptó; el diseño y el código de QUANTUM LAB son propios.")


# ---------------------------------------------------------------------
def interfaz() -> None:
    """Página «Biblioteca científica»."""
    qc.encabezado_pagina("Herramientas de estudio", "Biblioteca científica",
                         "Glosario, deducciones paso a paso con comprobación numérica, mapa de conexiones entre conceptos y referencias.")
    qc.escribir_en_url(None)
    t1, t2, t3, t4 = st.tabs(["Glosario", "Derivaciones", "Conexiones", "Referencias"])
    with t1:
        _pestana_glosario()
    with t2:
        _pestana_derivaciones()
    with t3:
        _pestana_conexiones()
    with t4:
        _pestana_referencias()


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def _llaves_balanceadas(latex: str) -> bool:
    limpio = latex.replace(r"\{", "").replace(r"\}", "")
    return limpio.count("{") == limpio.count("}") and latex.count(r"\left") == latex.count(r"\right")


def ejecutar_pruebas() -> "qc.RegistroPruebas":
    import quantum_lab_portada as portada
    paginas = {m[0] for m in portada.MODULOS}
    reg = qc.RegistroPruebas("Biblioteca científica")
    ids = {t.id for t in _glosario.TERMINOS}
    reg.comprobar("Los identificadores del glosario son únicos", len(ids) == len(_glosario.TERMINOS))
    reg.comprobar("Las referencias cruzadas del glosario existen", all(r in ids for t in _glosario.TERMINOS for r in t.relacionados))
    reg.comprobar("Los temas de teoría citados existen", all(not t.tema or teoria.buscar(t.tema) for t in _glosario.TERMINOS))
    reg.comprobar("Los simuladores citados existen", all(not t.simulador or t.simulador in paginas for t in _glosario.TERMINOS))
    reg.comprobar("Toda definición tiene al menos 40 caracteres", all(len(t.definicion) >= 40 for t in _glosario.TERMINOS))
    reg.comprobar("Las ecuaciones del glosario tienen llaves balanceadas", all(_llaves_balanceadas(t.ecuacion) for t in _glosario.TERMINOS))
    reg.comprobar("Las relaciones del mapa usan conceptos existentes",
                  all(r.origen in ids and r.destino in ids and r.origen != r.destino for r in _conexiones.RELACIONES))
    reg.comprobar("El mapa no repite aristas", len({(r.origen, r.destino) for r in _conexiones.RELACIONES}) == len(_conexiones.RELACIONES))
    reg.comprobar("La búsqueda ignora tildes y mayúsculas", {t.id for t in _glosario.buscar("DENSIDAD")} == {t.id for t in _glosario.buscar("densidad")}
                  and bool(_glosario.buscar("funcion de onda")))
    for d in _derivaciones.DERIVACIONES:
        reg.comprobar(f"Derivación «{d.id}»: pasos con LaTeX balanceado", len(d.pasos) >= 3 and all(_llaves_balanceadas(p.latex) for p in d.pasos))
        reg.comprobar(f"Derivación «{d.id}»: tema y simulador existen", bool(teoria.buscar(d.tema)) and d.simulador in paginas)
        if d.comprobacion:
            _, calculado, referencia, _u = d.comprobacion()
            dif = abs(calculado - referencia) / abs(referencia)
            reg.comprobar(f"Derivación «{d.id}»: el código coincide con la referencia independiente", dif < 1e-5, f"diferencia relativa {dif:.1e}")
    reg.comprobar("Las referencias tienen identificador único", len({r.id for r in _referencias.REFERENCIAS}) == len(_referencias.REFERENCIAS))
    reg.comprobar("Los enlaces de referencias son https", all(r.enlace.startswith("https://") for r in _referencias.REFERENCIAS if r.enlace))
    return reg
