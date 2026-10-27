"""
redactor — Cuaderno de informes de QUANTUM LAB
==============================================

Un editor de informes y de resoluciones de taller dentro de la web, sin LaTeX: bloques de texto con fórmulas, ecuaciones,
desarrollos paso a paso con revisión simbólica, gráficas propias (funciones y tablas de datos con ajuste lineal), resultados
de los simuladores y preguntas de los talleres con su calificación. Se guarda como archivo .json y se exporta a PDF.

Archivos: _expr.py (lectura segura de expresiones) · _verificar.py (revisión de pasos con SymPy) · _graficas.py (gráficas) ·
_simuladores.py (resultados de los simuladores) · _talleres.py (preguntas de los talleres) · _modelo.py (documento y .json) ·
_pdf.py (maquetación y exportación). Las pruebas están en test_redactor.py.
"""

from __future__ import annotations

import functools
from copy import deepcopy

import streamlit as st

import quantum_lab_comun as qc
from redactor import (
    _graficas,
    _modelo,
    _pdf,
    _simuladores,
    _talleres,
    _unidades,
    _verificar,
)
from redactor._expr import ErrorExpresion
from redactor._modelo import TIPOS, ErrorDocumento

CLAVE_DOC = "rd_doc"
ESTILO_MARCA = {_verificar.OK: ("✓", "green"), _verificar.ERROR: ("✗", "red"), _verificar.NO_VERIFICABLE: ("?", "orange"),
                _verificar.SINTAXIS: ("✗", "red"), _verificar.INICIO: ("·", "gray")}
AYUDA_NOTACION = (
    "**Cómo escribir las líneas de un desarrollo.** Una línea por paso. Potencias con `^` o `**`; multiplicación con `*` o espacio "
    "(`2 pi r`); funciones `sqrt()`, `sin()`, `cos()`, `exp()`, `ln()`; constantes `pi` y `e` (Euler). Los nombres de varias letras "
    "son un solo símbolo (`hbar`, `omega`, `lam`); para multiplicar letras escribe `m c^2` o `m*c^2`. Una cadena como "
    "`x = (a+b)^2 = a^2 + 2 a b + b^2` se revisa expresión por expresión. En «Datos conocidos» escribe `h = 6.626e-34 [J s]` (uno por "
    "línea) para comprobar pasos con números. **Unidades:** van entre corchetes al final de una expresión (`E = 3.97e-19 [J]`, `lam = 500 [nm]`) y "
    "se convierten a SI; declara las de otras variables en «Unidades de otras variables» (`E [J]`). Se revisa que ambos lados de cada "
    "igualdad tengan la misma dimensión, que solo se sumen magnitudes iguales y que sin, exp, ln… reciban números sin unidades; "
    "una variable sin unidad declarada no se revisa. En un cociente con varios factores abajo usa paréntesis: `J/(mol K)`. "
    "Un paso que usa una ley estándar (E = hν, c = λν, p = h/λ…) se acepta indicando cuál; uno que introduce un símbolo o una ley "
    "que no conozco se marca con «?» (no verificable), no como error."
)


# ---------------------------------------------------------------------
# Estado del documento
# ---------------------------------------------------------------------
def _doc() -> dict:
    if CLAVE_DOC not in st.session_state:
        st.session_state[CLAVE_DOC] = _modelo.documento_vacio("Mi informe", "")
    return st.session_state[CLAVE_DOC]


def _limpiar_claves_de_widgets() -> None:
    for k in [k for k in st.session_state if isinstance(k, str) and k.startswith("rd_") and k not in (CLAVE_DOC, "rd_archivo")]:
        del st.session_state[k]


def _reemplazar_documento(doc: dict) -> None:
    _limpiar_claves_de_widgets()
    st.session_state[CLAVE_DOC] = doc


def _mover(i: int, delta: int) -> None:
    b = _doc()["bloques"]
    j = i + delta
    if 0 <= j < len(b):
        b[i], b[j] = b[j], b[i]


def _duplicar(i: int) -> None:
    b = _doc()["bloques"]
    copia = deepcopy(b[i])
    copia["id"] = _modelo.nuevo_id()
    b.insert(i + 1, copia)


def _borrar(i: int) -> None:
    b = _doc()["bloques"]
    for k in [k for k in st.session_state if isinstance(k, str) and k.startswith(f"rd_{b[i]['id']}_")]:
        del st.session_state[k]
    del b[i]


def _agregar(tipo: str, datos: dict | None = None) -> None:
    _doc()["bloques"].append(_modelo.nuevo_bloque(tipo, datos))


# ---------------------------------------------------------------------
# Widgets enlazados al bloque (el valor vive en el bloque y en la sesión)
# ---------------------------------------------------------------------
def _w(b: dict, campo: str, fabrica, *args, **kw):
    clave = f"rd_{b['id']}_{campo}"
    if clave not in st.session_state:
        st.session_state[clave] = b["datos"][campo]
    valor = fabrica(*args, key=clave, **kw)
    b["datos"][campo] = valor
    return valor


# ---------------------------------------------------------------------
# Cálculos en caché (las vistas previas se recalculan solo cuando cambian los datos)
# ---------------------------------------------------------------------
@functools.lru_cache(maxsize=128)
def _pasos(lineas: str, datos: str, tol_pct: float, unidades: str = ""):
    tabla = _pdf._leer_datos(datos)
    return tuple(_verificar.verificar_pasos([ln for ln in lineas.splitlines() if ln.strip()], tabla, tol_pct / 100.0,
                                            _pdf._leer_unidades(unidades)))


@st.cache_data(show_spinner=False, max_entries=64)
def _png_funcion(*args) -> bytes:
    return _graficas.a_png(_graficas.grafica_funcion(*args))


@st.cache_data(show_spinner=False, max_entries=64)
def _png_datos(*args):
    fig, ajuste = _graficas.grafica_datos(*args)
    return _graficas.a_png(fig), ajuste


@st.cache_data(show_spinner=False, max_entries=32)
def _simulador(clave: str, valores: tuple):
    inf = _simuladores.construir(clave, dict(valores))
    return inf.parametros, inf.resultados, [_graficas.a_png(f) for f in inf.figuras]


# ---------------------------------------------------------------------
# Editores por tipo de bloque
# ---------------------------------------------------------------------
def _editor_titulo(b):
    c1, c2 = st.columns([4, 1])
    with c1:
        _w(b, "texto", st.text_input, "Texto del título")
    with c2:
        _w(b, "nivel", st.selectbox, "Nivel", [1, 2], format_func=lambda n: "Sección" if n == 1 else "Subsección")


def _editor_texto(b):
    _w(b, "texto", st.text_area, "Texto", height=140, help="Las fórmulas van entre $…$ (por ejemplo $E=h\\nu$). Líneas que empiezan con «- » son una lista.")
    if b["datos"]["texto"].strip():
        st.markdown(b["datos"]["texto"])


def _editor_ecuacion(b):
    c1, c2 = st.columns([4, 1])
    with c1:
        _w(b, "latex", st.text_input, "Ecuación (LaTeX)", help="Por ejemplo \\frac{n^2\\pi^2\\hbar^2}{2ma^2}. Se admite el subconjunto de LaTeX de Matplotlib.")
    with c2:
        _w(b, "etiqueta", st.text_input, "Número o etiqueta")
    tex = b["datos"]["latex"].strip()
    if tex:
        if _pdf.formula_valida(tex):
            st.latex(tex)
        else:
            qc.error("Esta fórmula no se puede dibujar en el PDF. Revisa llaves, \\frac{}{} y los comandos usados.")


def _editor_desarrollo(b):
    d = b["datos"]
    _w(b, "comentario", st.text_input, "Enunciado o comentario (opcional)")
    c1, c2 = st.columns([3, 2])
    with c1:
        _w(b, "lineas", st.text_area, "Desarrollo (una línea por paso)", height=190,
           placeholder="E = p^2/(2 m)\np = n pi hbar/a\nE = (n pi hbar/a)^2/(2 m)\nE = n^2 pi^2 hbar^2/(2 m a^2)")
    with c2:
        _w(b, "datos", st.text_area, "Datos conocidos (opcional)", height=110, placeholder="h = 6.626e-34 [J s]\nc = 2.998e8 [m/s]",
           help="Valores de las variables para comprobar pasos con números. La unidad va entre corchetes y se convierte a SI.")
        _w(b, "unidades", st.text_area, "Unidades de otras variables (opcional)", height=80, placeholder="E [J]\np [kg m/s]",
           help="Unidad de variables sin valor numérico, para revisar la coherencia dimensional de cada línea.")
        _w(b, "tol_pct", st.number_input, "Tolerancia al sustituir números [%]", min_value=0.001, max_value=50.0, step=0.1, format="%.3g")
    _w(b, "marcas", st.checkbox, "Mostrar las marcas de revisión (✓ ✗ ?) en el PDF")
    with st.expander("Cómo escribir un desarrollo"):
        st.markdown(AYUDA_NOTACION)
    if not d["lineas"].strip():
        return
    pasos = _pasos(d["lineas"], d["datos"], float(d["tol_pct"]), d["unidades"])
    r = _verificar.resumen(list(pasos))
    st.markdown(f"**Revisión:** :green[{r[_verificar.OK]} correctos] · :red[{r[_verificar.ERROR] + r[_verificar.SINTAXIS]} con error] · "
                f":orange[{r[_verificar.NO_VERIFICABLE]} no verificables]")
    for p in pasos:
        simbolo, color = ESTILO_MARCA[p.estado]
        c1, c2 = st.columns([1, 12])
        c1.markdown(f":{color}[**{simbolo}**]")
        with c2:
            tex = _pdf._latex_de_linea(p.texto)
            if tex and _pdf.formula_valida(tex):
                st.latex(tex)
            else:
                st.code(p.texto, language=None)
            if p.mensaje and p.estado != _verificar.INICIO:
                st.caption(f":{color}[{p.mensaje}]")
            if p.unidades and p.estado != _verificar.ERROR:
                st.caption(f":green[{p.unidades}]")
            if p.prueba == "simbolica":
                st.caption(":green[Igualdad demostrada por simplificación simbólica exacta.]")
            elif p.prueba == "numerica" and p.estado == _verificar.OK:
                st.caption("Comprobada numéricamente en varios puntos (no es una demostración formal).")
            if p.esperado_latex and _pdf.formula_valida(p.esperado_latex):
                st.caption("Calculado a partir de la línea anterior:")
                st.latex(p.esperado_latex)


def _editor_grafica_funcion(b):
    d = b["datos"]
    _w(b, "expresiones", st.text_area, "Curvas (una por línea; «nombre = expresión» o solo la expresión)", height=90,
       help="Hasta 6 curvas. Ejemplo: ψ² = (2/a) sin(n pi x/a)^2")
    c1, c2, c3 = st.columns(3)
    with c1:
        _w(b, "variable", st.text_input, "Variable independiente")
    with c2:
        _w(b, "xmin", st.number_input, "Mínimo", format="%.6g")
    with c3:
        _w(b, "xmax", st.number_input, "Máximo", format="%.6g")
    _w(b, "constantes", st.text_area, "Constantes (nombre = valor, una por línea)", height=70, placeholder="n = 2\na = 1e-9")
    c1, c2, c3 = st.columns(3)
    with c1:
        _w(b, "titulo", st.text_input, "Título de la gráfica")
    with c2:
        _w(b, "xlabel", st.text_input, "Rótulo del eje x")
    with c3:
        _w(b, "ylabel", st.text_input, "Rótulo del eje y")
    _w(b, "pie", st.text_input, "Pie de figura")
    try:
        st.image(_png_funcion(d["expresiones"], d["variable"], d["xmin"], d["xmax"], d["constantes"], d["titulo"], d["xlabel"], d["ylabel"]),
                 width=520)
    except (_graficas.ErrorGrafica, ErrorExpresion) as error:
        qc.error(error)


def _editor_grafica_datos(b):
    d = b["datos"]
    _w(b, "tabla", st.text_area, "Datos (x y [incertidumbre de y], una fila por línea)", height=150, placeholder="1 2.1\n2 3.9\n3 6.2\n4 7.8",
       help="Columnas separadas por espacios o «;». La coma es decimal. Las líneas con # se ignoran.")
    _w(b, "tipo", st.selectbox, "Tipo de gráfica", ["puntos", "linea", "ajuste"],
       format_func={"puntos": "Puntos", "linea": "Línea con puntos", "ajuste": "Puntos con ajuste lineal"}.get)
    c1, c2, c3 = st.columns(3)
    with c1:
        _w(b, "titulo", st.text_input, "Título de la gráfica")
    with c2:
        _w(b, "xlabel", st.text_input, "Rótulo del eje x")
    with c3:
        _w(b, "ylabel", st.text_input, "Rótulo del eje y")
    _w(b, "pie", st.text_input, "Pie de figura")
    try:
        png, ajuste = _png_datos(d["tabla"], d["tipo"], d["titulo"], d["xlabel"], d["ylabel"])
    except _graficas.ErrorGrafica as error:
        qc.error(error)
        return
    st.image(png, width=520)
    if ajuste:
        u_m = f" ± {ajuste['u_pendiente']:.2g}" if ajuste["u_pendiente"] is not None else ""
        st.caption(f"Ajuste por mínimos cuadrados: pendiente = {ajuste['pendiente']:.5g}{u_m} · ordenada = {ajuste['ordenada']:.5g} · "
                   f"R² = {ajuste['r2']:.5f} · n = {ajuste['n']}")


def _editor_simulador(b):
    d = b["datos"]
    sim_clave = _w(b, "sim", st.selectbox, "Simulador", list(_simuladores.SIMULADORES), format_func=lambda k: _simuladores.SIMULADORES[k].nombre)
    sim = _simuladores.SIMULADORES[sim_clave]
    valores = {**_simuladores.valores_por_defecto(sim_clave), **d["valores"]}
    columnas = st.columns(min(3, len(sim.campos)))
    for i, c in enumerate(sim.campos):
        clave = f"rd_{b['id']}_v_{sim_clave}_{c.clave}"
        with columnas[i % len(columnas)]:
            if c.tipo == "opciones":
                valores_op = [v for v, _ in c.opciones]
                etiquetas = dict(c.opciones)
                if clave not in st.session_state:
                    st.session_state[clave] = valores[c.clave] if valores[c.clave] in valores_op else c.defecto
                valores[c.clave] = st.selectbox(c.etiqueta, valores_op, format_func=etiquetas.get, key=clave)
            elif c.tipo == "int":
                if clave not in st.session_state:
                    st.session_state[clave] = int(min(max(valores[c.clave], c.minimo), c.maximo))
                valores[c.clave] = st.number_input(c.etiqueta, int(c.minimo), int(c.maximo), step=1, key=clave, help=c.ayuda or None)
            else:
                if clave not in st.session_state:
                    st.session_state[clave] = float(min(max(valores[c.clave], c.minimo), c.maximo))
                valores[c.clave] = st.number_input(c.etiqueta, float(c.minimo), float(c.maximo), format="%.6g", key=clave, help=c.ayuda or None)
    d["valores"] = {c.clave: valores[c.clave] for c in sim.campos}
    _w(b, "pie", st.text_input, "Pie de figura (opcional)")
    try:
        parametros, resultados, figuras = _simulador(sim_clave, tuple(sorted(d["valores"].items())))
    except ValueError as error:
        qc.error(error)
        return
    c1, c2 = st.columns(2)
    with c1:
        qc.tabla([(m, v, u) for m, v, u in parametros], encabezados=("Parámetro", "Valor", "Unidad"))
    with c2:
        qc.tabla([(m, v, u) for m, v, u in resultados], encabezados=("Resultado", "Valor", "Unidad"))
    for png in figuras:
        st.image(png, width=520)
    st.caption("Es el mismo cálculo del simulador con estos parámetros; se guarda el valor de cada parámetro, no la imagen.")


def _editor_taller(b):
    d = b["datos"]
    catalogo = _talleres.catalogo()
    ids = [i for i, _ in catalogo]
    if d["taller"] not in ids:
        d["taller"] = ids[0]
        st.session_state.pop(f"rd_{b['id']}_taller", None)
    nombres = dict(catalogo)
    _w(b, "taller", st.selectbox, "Taller", ids, format_func=nombres.get)
    c1, c2 = st.columns(2)
    with c1:
        _w(b, "original", st.radio, "Datos", [True, False], format_func=lambda v: "Datos del taller original" if v else "Datos nuevos", horizontal=True)
    with c2:
        if not d["original"]:
            _w(b, "semilla", st.text_input, "Semilla (misma semilla = mismos datos)")
    try:
        preguntas = _talleres.preguntas(d["taller"], d["original"], d["semilla"])
    except ValueError as error:
        qc.error(error)
        return
    ids_p = [q.id for q in preguntas]
    if d["pregunta"] not in ids_p:
        d["pregunta"] = ids_p[0]
        st.session_state.pop(f"rd_{b['id']}_pregunta", None)
    _w(b, "pregunta", st.selectbox, "Pregunta", ids_p, format_func=lambda i: f"Pregunta {i}")
    q = next(x for x in preguntas if x.id == d["pregunta"])
    st.markdown(q.enunciado)
    respuestas = dict(d["respuestas"])
    for p in q.partes:
        clave = f"rd_{b['id']}_r_{d['taller']}_{d['original']}_{d['semilla']}_{q.id}_{p.clave}"
        st.markdown(p.etiqueta)
        if p.tipo == "opcion":
            if clave not in st.session_state:
                st.session_state[clave] = respuestas.get(p.clave) if respuestas.get(p.clave) in p.opciones else None
            respuestas[p.clave] = st.radio("Respuesta", list(p.opciones), index=None, key=clave, label_visibility="collapsed")
        else:
            if clave not in st.session_state:
                st.session_state[clave] = respuestas.get(p.clave, "")
            respuestas[p.clave] = st.text_input(f"Respuesta ({p.unidad})" if p.unidad else "Respuesta", key=clave, placeholder="1.256e12  o  1,256 x 10^12")
    d["respuestas"] = {k: v for k, v in respuestas.items() if v}
    _w(b, "incluir_solucion", st.checkbox, "Incluir la solución del taller en el PDF (y mostrar las respuestas correctas)")
    cal = _talleres.calificar_bloque(d)
    if cal:
        estilo = {"ok": "green", "casi": "orange", "mal": "red", "vacia": "gray", "invalida": "red"}
        for p in cal["partes"]:
            if p["estado"] != "vacia":
                st.markdown(f":{estilo.get(p['estado'], 'gray')}[**{p['estado_texto']}.**] {p['mensaje']}")
        st.markdown(f"**Puntaje: {cal['puntos']:.3g} de {cal['maximo']:.3g}**")
        if d["incluir_solucion"] and cal["solucion"]:
            with st.expander("Solución del taller", expanded=False):
                st.markdown(cal["solucion"])


def _editor_tabla(b):
    d = b["datos"]
    _w(b, "titulo", st.text_input, "Título de la tabla")
    import pandas as pd
    columnas = d["encabezados"] or ["Columna"]
    filas = [list(f) + [""] * (len(columnas) - len(f)) for f in d["filas"]] or [[""] * len(columnas)]
    df = pd.DataFrame([f[: len(columnas)] for f in filas], columns=columnas)
    editado = st.data_editor(df, num_rows="dynamic", key=f"rd_{b['id']}_editor", width="stretch")
    d["encabezados"] = [str(c) for c in editado.columns]
    d["filas"] = [["" if v is None else str(v) for v in fila] for fila in editado.values.tolist()]
    nueva = st.text_input("Encabezados (separados por coma)", value=", ".join(d["encabezados"]), key=f"rd_{b['id']}_enc")
    nuevos = [c.strip() for c in nueva.split(",") if c.strip()]
    if nuevos and nuevos != d["encabezados"] and len(nuevos) <= 8:
        d["encabezados"] = nuevos
        d["filas"] = [(list(f) + [""] * len(nuevos))[: len(nuevos)] for f in d["filas"]]
        st.session_state.pop(f"rd_{b['id']}_editor", None)
        st.rerun()


EDITORES = {"titulo": _editor_titulo, "texto": _editor_texto, "ecuacion": _editor_ecuacion, "desarrollo": _editor_desarrollo,
            "grafica_funcion": _editor_grafica_funcion, "grafica_datos": _editor_grafica_datos, "simulador": _editor_simulador,
            "taller": _editor_taller, "tabla": _editor_tabla}


def _resumen_bloque(b: dict) -> str:
    d = b["datos"]
    t = b["tipo"]
    if t in ("titulo", "texto"):
        return (d["texto"].strip().splitlines() or [""])[0][:60]
    if t == "ecuacion":
        return d["latex"][:50]
    if t == "desarrollo":
        return f"{len([x for x in d['lineas'].splitlines() if x.strip()])} líneas"
    if t == "simulador":
        return _simuladores.SIMULADORES[d["sim"]].nombre
    if t == "taller":
        return f"{d['taller']} · {d['pregunta']}"
    return d.get("titulo", "")[:50]


# ---------------------------------------------------------------------
# Plantillas
# ---------------------------------------------------------------------
def _plantilla_laboratorio() -> dict:
    doc = _modelo.documento_vacio("Informe de laboratorio", "")
    for tipo, datos in (
        ("titulo", {"texto": "1. Objetivo", "nivel": 1}), ("texto", {"texto": "Escribe aquí qué se quiere comprobar."}),
        ("titulo", {"texto": "2. Marco teórico", "nivel": 1}), ("texto", {"texto": "Resume el modelo y escribe las ecuaciones con $…$."}),
        ("ecuacion", {"latex": r"E_n=\frac{n^2\pi^2\hbar^2}{2ma^2}", "etiqueta": "1"}),
        ("titulo", {"texto": "3. Procedimiento y datos", "nivel": 1}), ("texto", {"texto": "Describe cómo usaste el simulador."}),
        ("simulador", {"sim": "caja"}),
        ("titulo", {"texto": "4. Análisis", "nivel": 1}), ("desarrollo", {"lineas": "", "comentario": "Desarrollo de los cálculos:"}),
        ("grafica_datos", {"tabla": "", "xlabel": "x", "ylabel": "y"}),
        ("titulo", {"texto": "5. Conclusiones", "nivel": 1}), ("texto", {"texto": "¿Qué aprendiste? ¿Coincide con la teoría?"}),
    ):
        doc["bloques"].append(_modelo.nuevo_bloque(tipo, datos))
    return doc


def _plantilla_taller(taller_id: str) -> dict:
    titulo = dict(_talleres.catalogo()).get(taller_id, taller_id)
    doc = _modelo.documento_vacio(f"Taller: {titulo}", "")
    for q in _talleres.preguntas(taller_id, True, "1"):
        doc["bloques"].append(_modelo.nuevo_bloque("titulo", {"texto": f"Pregunta {q.id}", "nivel": 1}))
        doc["bloques"].append(_modelo.nuevo_bloque("taller", {"taller": taller_id, "original": True, "semilla": "1", "pregunta": q.id}))
        doc["bloques"].append(_modelo.nuevo_bloque("desarrollo", {"comentario": "Mi desarrollo:"}))
    return doc


# ---------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------
def _barra_documento() -> None:
    doc = _doc()
    c1, c2 = st.columns([3, 2])
    with c1:
        doc["titulo"] = st.text_input("Título del informe", value=doc["titulo"], key="rd_titulo_doc")
    with c2:
        doc["autor"] = st.text_input("Autor (opcional)", value=doc["autor"], key="rd_autor_doc")
    with st.expander("Archivo y plantillas", expanded=not doc["bloques"]):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("Descargar cuaderno (.json)", _modelo.a_json(doc), file_name=f"{_nombre_archivo(doc)}.json",
                               mime="application/json", icon=":material/download:", width="stretch", key="rd_dl_json")
        with c2:
            subido = st.file_uploader("Cargar un cuaderno (.json)", type=["json"], key="rd_subida", label_visibility="collapsed")
            if subido is not None and st.session_state.get("rd_archivo") != subido.file_id:
                try:
                    _reemplazar_documento(_modelo.desde_json(subido.getvalue()))
                    st.session_state["rd_archivo"] = subido.file_id
                    st.rerun()
                except ErrorDocumento as error:
                    st.session_state["rd_archivo"] = subido.file_id
                    qc.error(error)
        with c3:
            if st.button("Empezar un cuaderno nuevo", key="rd_nuevo", icon=":material/note_add:", width="stretch"):
                _reemplazar_documento(_modelo.documento_vacio("Mi informe", ""))
                st.rerun()
        st.caption("El cuaderno vive en esta sesión: **descárgalo (.json) para no perder tu trabajo** y vuelve a cargarlo cuando quieras seguir.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Plantilla: informe de laboratorio", key="rd_pl_lab", icon=":material/science:", width="stretch"):
                _reemplazar_documento(_plantilla_laboratorio())
                st.rerun()
        with c2:
            taller = st.selectbox("Taller", [i for i, _ in _talleres.catalogo()], format_func=dict(_talleres.catalogo()).get,
                                  key="rd_pl_taller_sel", label_visibility="collapsed")
            if st.button("Plantilla: responder este taller", key="rd_pl_taller", icon=":material/edit_note:", width="stretch"):
                _reemplazar_documento(_plantilla_taller(taller))
                st.rerun()


def _nombre_archivo(doc: dict) -> str:
    base = "".join(c if c.isalnum() else "_" for c in (doc["titulo"] or "cuaderno").lower()).strip("_")
    return base[:50] or "cuaderno"


def _bloques() -> None:
    doc = _doc()
    for i, b in enumerate(doc["bloques"]):
        nombre = TIPOS[b["tipo"]][0]
        with st.container(border=True, key=f"rd_caja_{b['id']}"):
            c0, c1, c2, c3, c4 = st.columns([8, 1, 1, 1, 1])
            c0.markdown(f"**{i + 1}. {nombre}**" + (f" — {_resumen_bloque(b)}" if _resumen_bloque(b) else ""))
            c1.button("", key=f"rd_{b['id']}_up", icon=":material/arrow_upward:", on_click=_mover, args=(i, -1), disabled=i == 0, help="Subir")
            c2.button("", key=f"rd_{b['id']}_dn", icon=":material/arrow_downward:", on_click=_mover, args=(i, 1),
                      disabled=i == len(doc["bloques"]) - 1, help="Bajar")
            c3.button("", key=f"rd_{b['id']}_dup", icon=":material/content_copy:", on_click=_duplicar, args=(i,), help="Duplicar")
            c4.button("", key=f"rd_{b['id']}_del", icon=":material/delete:", on_click=_borrar, args=(i,), help="Eliminar")
            EDITORES[b["tipo"]](b)


def _agregar_bloques() -> None:
    c1, c2 = st.columns([3, 1])
    with c1:
        tipo = st.selectbox("Agregar un bloque", list(TIPOS), format_func=lambda k: TIPOS[k][0], key="rd_tipo_nuevo")
    with c2:
        st.write("")
        st.button("Agregar", key="rd_agregar", icon=":material/add:", on_click=_agregar, args=(tipo,), width="stretch", type="primary")


def _exportar() -> None:
    doc = _doc()
    qc.seccion("Vista previa y PDF")
    if not doc["bloques"]:
        st.info("Agrega bloques para poder exportar el informe.")
        return
    problemas = _pdf.problemas_del_documento(doc)
    for i, mensaje in problemas:
        st.warning(f"Bloque {i}: {mensaje}", icon=":material/warning:")
    if not problemas:
        st.success("Todos los bloques se pueden dibujar en el PDF.", icon=":material/check_circle:")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Ver cómo queda (vista previa)", key="rd_prev", icon=":material/preview:", width="stretch"):
            st.session_state["rd_vista"] = _pdf.paginas_png(doc)
    with c2:
        if st.button("Preparar el PDF", key="rd_pdf", icon=":material/picture_as_pdf:", type="primary", width="stretch"):
            st.session_state["rd_pdf_bytes"] = _pdf.pdf_cuaderno(doc)
    if st.session_state.get("rd_pdf_bytes"):
        st.download_button("Descargar el PDF", st.session_state["rd_pdf_bytes"], file_name=f"{_nombre_archivo(doc)}.pdf", mime="application/pdf",
                           key="rd_dl_pdf", icon=":material/download:", width="stretch")
        st.caption("El PDF se preparó con el contenido del momento de pulsar el botón; si cambias algo, vuelve a prepararlo.")
    vista = st.session_state.get("rd_vista")
    if vista:
        columnas = st.columns(min(2, len(vista)))
        for i, png in enumerate(vista):
            columnas[i % len(columnas)].image(png, caption=f"Página {i + 1} de {len(vista)}")


def interfaz() -> None:
    """Página «Cuaderno de informes»."""
    qc.encabezado_pagina("Herramientas de estudio", "Cuaderno de informes",
                         "Escribe informes y resuelve talleres sin salir de la web: texto con fórmulas, desarrollos paso a paso con revisión, "
                         "gráficas propias, resultados de los simuladores y preguntas de los talleres. Exporta a PDF.")
    qc.escribir_en_url(None)
    _barra_documento()
    _bloques()
    _agregar_bloques()
    _exportar()


# ---------------------------------------------------------------------
# Pruebas (Verificación)
# ---------------------------------------------------------------------
def ejecutar_pruebas() -> qc.RegistroPruebas:
    import math

    from redactor._expr import leer_expresion
    r = qc.RegistroPruebas("Cuaderno de informes")
    for malo in ("__import__('os')", "x.__class__", "9**9**9", "open('f')", "x**1000"):
        try:
            leer_expresion(malo)
            r.comprobar(f"Rechaza la expresión peligrosa «{malo}»", False)
        except ErrorExpresion:
            r.comprobar(f"Rechaza la expresión peligrosa «{malo}»", True)
    pasos = _verificar.verificar_pasos(["E = p^2/(2 m)", "E = p^2/m"])
    r.comprobar("Detecta un factor 2 equivocado en un paso", pasos[1].estado == _verificar.ERROR and "doble" in pasos[1].mensaje)
    pasos = _verificar.verificar_pasos(["E = p^2/(2 m)", "p = sqrt(2 m E)"])
    r.comprobar("Acepta un despeje correcto", pasos[1].estado == _verificar.OK)
    pasos = _verificar.verificar_pasos(["E = h c/lam", "E = 3.2e-19"], {"h": "6.626e-34", "c": "2.998e8", "lam": "500e-9"})
    r.comprobar("Con datos, una cifra equivocada (3.2e-19 en vez de 3.97e-19) se marca como error", pasos[1].estado == _verificar.ERROR)
    pasos = _verificar.verificar_pasos(["E = h nu", "E = h lam"], None, 0.01, {"E": "J", "h": "J s", "nu": "Hz", "lam": "m"})
    r.comprobar("Detecta una ecuación con unidades incoherentes (E = hλ: J ≠ kg·m³/s)", pasos[1].estado == _verificar.ERROR)
    r.comprobar("1 eV = 1.602176634e-19 J (valor exacto del SI)", math.isclose(_unidades.leer_unidad("eV")[0], 1.602176634e-19, rel_tol=1e-12))
    datos = _graficas.ajuste_lineal([0, 1, 2, 3], [1, 3, 5, 7])
    r.comprobar("Ajuste lineal exacto: y = 2x + 1 con R² = 1", math.isclose(datos["pendiente"], 2.0) and math.isclose(datos["ordenada"], 1.0)
                and math.isclose(datos["r2"], 1.0))
    doc = _modelo.documento_vacio("Prueba", "")
    doc["bloques"] += [_modelo.nuevo_bloque("texto", {"texto": "Hola $x^2$"}), _modelo.nuevo_bloque("desarrollo", {"lineas": "x = 2 y"}),
                       _modelo.nuevo_bloque("simulador", {"sim": "bohr"})]
    ida_vuelta = _modelo.desde_json(_modelo.a_json(doc))
    r.comprobar("El archivo .json se guarda y se vuelve a cargar sin cambios", [b["datos"] for b in ida_vuelta["bloques"]] == [b["datos"] for b in doc["bloques"]])
    r.comprobar("El PDF del cuaderno se genera y es un PDF válido", _pdf.pdf_cuaderno(doc).startswith(b"%PDF-"))
    r.comprobar("Todos los simuladores se pueden insertar con sus valores por defecto",
                all(_simuladores.construir(k, {}).figuras for k in _simuladores.SIMULADORES))
    return r
