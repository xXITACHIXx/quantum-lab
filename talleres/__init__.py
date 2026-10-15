"""
talleres — Talleres de repaso de QUANTUM LAB
============================================

Problemas al estilo de los talleres evaluativos del curso, con calificación automática y solución justificada.
Los enunciados están reescritos y se verifican numéricamente. Cada taller es una función `construir(datos)` que devuelve sus
preguntas; con «datos nuevos» cada intento usa otra molécula, otro número cuántico u otros valores, y el resultado esperado y la
solución se recalculan con ellos.

Tipos de pregunta (cada pregunta tiene una o varias partes con su peso):
    numérica   se escribe el número (1.256e12, 1,256 x 10^12…); se acepta con tolerancia y se diagnostican errores típicos
    opción     opción múltiple (para diagramas y funciones de onda, que no se califican como texto libre)

Cómo añadir un taller: crear talleres/tN_<tema>.py con un `TALLER = Taller(...)` y añadirlo a TALLERES aquí abajo.
"""

from __future__ import annotations

import functools

import streamlit as st

import quantum_lab_comun as qc
import teoria
from talleres import t1_espectros, t2_orbitales, t3_p_rotor, t4_moleculares
from talleres._calificar import CASI, INVALIDA, MAL, OK, VACIA
from talleres._modelo import NUM, OPC, Calificacion, Datos, Pregunta, Taller, calificar

TALLERES: tuple[Taller, ...] = (t1_espectros.TALLER, t2_orbitales.TALLER, t3_p_rotor.TALLER, t4_moleculares.TALLER)
MODOS = ("Datos del taller original", "Datos nuevos")


def buscar(taller_id: str) -> Taller | None:
    return next((t for t in TALLERES if t.id == taller_id), None)


@functools.lru_cache(maxsize=64)
def preguntas_de(taller_id: str, original: bool, semilla: str) -> tuple:
    """Preguntas de un intento (en caché: construirlas calcula distribuciones radiales)."""
    return tuple(buscar(taller_id).construir(Datos(original, semilla)))


# ---------------------------------------------------------------------
# Estado de una sesión
# ---------------------------------------------------------------------
def _intento(taller_id: str) -> int:
    return int(st.session_state.get(f"tl_int_{taller_id}", 0))


def _original(taller_id: str) -> bool:
    return st.session_state.get(f"tl_modo_{taller_id}", MODOS[0]) == MODOS[0]


def _prefijo(taller_id: str) -> str:
    return f"tl_{taller_id}_{'o' if _original(taller_id) else 'n'}_{_intento(taller_id)}"


def _resultados() -> dict:
    return st.session_state.setdefault("tl_res", {})


def _abrir(taller_id: str) -> None:
    st.session_state["ql_taller"] = taller_id


def _volver() -> None:
    st.session_state["ql_taller"] = ""


def _nuevo_intento(taller_id: str) -> None:
    st.session_state[f"tl_int_{taller_id}"] = _intento(taller_id) + 1


def _clave_resp(prefijo: str, pregunta: Pregunta, parte_clave: str) -> str:
    return f"{prefijo}_{pregunta.id}_{parte_clave}"


def _calificar_pregunta(prefijo: str, pregunta: Pregunta) -> None:
    respuestas = {p.clave: st.session_state.get(_clave_resp(prefijo, pregunta, p.clave)) for p in pregunta.partes}
    _resultados()[(prefijo, pregunta.id)] = calificar(pregunta, respuestas)


# ---------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------
def _formato_esperado(parte) -> str:
    v = parte.esperado
    if v == 0:
        return "0"
    texto = f"{v:.4g}"
    return f"{texto} {parte.unidad}".strip()


def _mensaje(parte, res) -> None:
    if parte.tipo == OPC:
        correcta = parte.opciones[parte.correcta]
        if res.estado == OK:
            st.success(f"Correcto. {parte.explicacion}", icon=":material/check_circle:")
        elif res.estado == VACIA:
            st.warning(f"Sin responder. Respuesta correcta: **{correcta}**. {parte.explicacion}", icon=":material/help:")
        else:
            st.error(f"Incorrecta. Respuesta correcta: **{correcta}**. {parte.explicacion}", icon=":material/cancel:")
        return
    esperado = _formato_esperado(parte)
    if res.estado == OK:
        st.success(f"Correcto (≈ {esperado}). {parte.explicacion}", icon=":material/check_circle:")
    elif res.estado == CASI:
        st.warning(f"{res.mensaje} Valor esperado: **{esperado}**. {parte.explicacion}", icon=":material/lightbulb:")
    elif res.estado in (VACIA, INVALIDA):
        st.warning(f"{res.mensaje} Valor esperado: **{esperado}**. {parte.explicacion}", icon=":material/help:")
    else:
        st.error(f"{res.mensaje} Valor esperado: **{esperado}**. {parte.explicacion}", icon=":material/cancel:")


def _tema_relacionado(tema_id: str, clave: str) -> None:
    hallado = teoria.buscar(tema_id) if tema_id else None
    if hallado is None:
        return
    _, tema = hallado
    if tema.estado == teoria.DISPONIBLE:
        st.button(f"Repasar la teoría: {tema.titulo}", key=f"tl_teoria_{clave}",
                  icon=":material/menu_book:", on_click=qc.ir_a_tema, args=(tema_id,))
    else:
        st.caption(f"Tema relacionado: {tema.titulo} (en preparación en el Centro de teoría).")


def _pregunta(prefijo: str, i: int, pregunta: Pregunta) -> None:
    resultados = _resultados()
    cal: Calificacion | None = resultados.get((prefijo, pregunta.id))
    with st.container(border=True):
        titulo = f"Pregunta {i}  ·  {pregunta.puntos:g} {'punto' if pregunta.puntos == 1 else 'puntos'}"
        if cal is not None:
            titulo += f"  ·  obtenido: {cal.puntos:.2f}"
        qc.seccion(titulo)
        st.markdown(pregunta.enunciado)
        if pregunta.nota:
            st.caption(pregunta.nota)
        for p in pregunta.partes:
            clave = _clave_resp(prefijo, pregunta, p.clave)
            if p.tipo == OPC:
                st.radio(p.etiqueta, p.opciones, index=None, key=clave)
            else:
                etiqueta = p.etiqueta + (f"  [{p.unidad}]" if p.unidad and f"en {p.unidad}" not in p.etiqueta else "")
                st.text_input(etiqueta, key=clave, placeholder="Escribe un número, por ejemplo 1.256e12 o 1,256 x 10^12")
            if cal is not None:
                _mensaje(p, cal.resultados[p.clave])
        st.text_area("Tu procedimiento (no se califica; escríbelo como lo harías en el taller)", key=f"{prefijo}_{pregunta.id}_proc",
                     height=90)
        c1, c2 = st.columns([1, 3], vertical_alignment="center")
        c1.button("Calificar" if cal is None else "Volver a calificar", key=f"{prefijo}_{pregunta.id}_btn", type="primary",
                  icon=":material/grading:", width="stretch", on_click=_calificar_pregunta, args=(prefijo, pregunta))
        if cal is not None:
            c2.progress(cal.fraccion, text=f"{cal.puntos:.2f} de {cal.maximo:g} puntos")
            with st.expander("Solución completa y justificación", icon=":material/menu_book:"):
                st.markdown(pregunta.solucion)
        _tema_relacionado(pregunta.tema, f"{prefijo}_{pregunta.id}")


def _informe(taller: Taller, prefijo: str, preguntas: tuple) -> str:
    resultados = _resultados()
    lineas = [f"# Taller de repaso: {taller.titulo}", "", f"Datos: {'originales' if _original(taller.id) else 'nuevos'}", ""]
    total = obtenido = 0.0
    for i, q in enumerate(preguntas, 1):
        cal = resultados.get((prefijo, q.id))
        total += q.puntos
        obtenido += cal.puntos if cal else 0.0
        lineas += [f"## Pregunta {i} ({q.puntos:g} pt)", "", q.enunciado, ""]
        for p in q.partes:
            r = st.session_state.get(_clave_resp(prefijo, q, p.clave))
            estado = cal.resultados[p.clave].estado if cal else "sin calificar"
            lineas.append(f"- {p.etiqueta}: **{r if r not in (None, '') else '—'}** → {estado}")
        proc = st.session_state.get(f"{prefijo}_{q.id}_proc")
        if proc:
            lineas += ["", "Procedimiento:", "", proc]
        if cal:
            lineas += ["", f"Puntaje: {cal.puntos:.2f} / {cal.maximo:g}", "", "Solución:", "", q.solucion]
        lineas.append("")
    lineas.insert(3, f"Puntaje total: {obtenido:.2f} / {total:g}")
    return "\n".join(lineas)


def _vista_taller(taller_id: str) -> None:
    taller = buscar(taller_id)
    if taller is None:
        _volver()
        st.rerun()
    c1, c2 = st.columns([1, 5], vertical_alignment="center")
    with c1:
        st.button("Talleres", key="tl_volver", icon=":material/arrow_back:", on_click=_volver, width="stretch")
    with c2:
        st.caption("Talleres de repaso")
    qc.encabezado_pagina("Taller de repaso", taller.titulo, taller.resumen)

    if taller.variable:
        c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
        with c1:
            st.radio("Valores del problema", MODOS, horizontal=True, key=f"tl_modo_{taller_id}",
                     help="«Datos nuevos» cambia la molécula, el número cuántico o los valores en cada intento para que practiques el método.")
        with c2:
            st.button("Nuevo intento", key=f"tl_nuevo_{taller_id}", icon=":material/restart_alt:", width="stretch",
                      on_click=_nuevo_intento, args=(taller_id,))
    else:
        st.button("Nuevo intento", key=f"tl_nuevo_{taller_id}", icon=":material/restart_alt:", on_click=_nuevo_intento, args=(taller_id,))

    prefijo = _prefijo(taller_id)
    semilla = f"{taller_id}-{_intento(taller_id)}"
    preguntas = preguntas_de(taller_id, _original(taller_id), semilla)
    resultados = _resultados()
    total = sum(q.puntos for q in preguntas)
    calificadas = [(q, resultados[(prefijo, q.id)]) for q in preguntas if (prefijo, q.id) in resultados]
    obtenido = sum(c.puntos for _, c in calificadas)
    qc.metricas([("Puntaje", f"{obtenido:.2f} / {total:g}"), ("Preguntas calificadas", f"{len(calificadas)} / {len(preguntas)}"),
                 ("Porcentaje", f"{100 * obtenido / total:.0f} %" if total else "—")], columnas=3)
    st.info("Escribe tus resultados con sus unidades indicadas (se aceptan «1.256e12» y «1,256 x 10^12»). Cada pregunta se califica por separado con una tolerancia "
            "del 2 % y suma puntos parciales por partes. Después de calificar aparece la solución completa. Es un repaso: la nota no es oficial.",
            icon=":material/info:")
    for i, q in enumerate(preguntas, 1):
        _pregunta(prefijo, i, q)
    st.download_button("Descargar mi taller (Markdown)", _informe(taller, prefijo, preguntas).encode("utf-8"),
                       file_name=f"taller_{taller_id}.md", mime="text/markdown", icon=":material/download:")


def _vista_indice() -> None:
    qc.encabezado_pagina("Repaso", "Talleres de repaso",
                         "Problemas al estilo de los talleres del curso: escribe tus resultados, recibe tu calificación y compara con la solución justificada.")
    qc.metricas([("Talleres", f"{len(TALLERES)}"), ("Preguntas", f"{sum(t.n_preguntas for t in TALLERES)}"),
                 ("Puntos", f"{sum(t.puntos for t in TALLERES):g}")], columnas=3)
    st.info("Los enunciados son una reescritura de talleres de semestres anteriores; las soluciones están verificadas numéricamente. "
            "Con «datos nuevos» puedes repetir cada taller con otros valores.", icon=":material/info:")
    for inicio in range(0, len(TALLERES), 2):
        cols = st.columns(2)
        for col, t in zip(cols, TALLERES[inicio:inicio + 2]):
            with col:
                items = "".join(f"<li>{c}</li>" for c in t.contenidos)
                st.markdown(f'<div class="ql-card" style="min-height:320px"><p class="ql-etiqueta">{t.n_preguntas} preguntas · {t.puntos:g} puntos</p>'
                            f'<h3>{t.titulo}</h3><p>{t.resumen}</p><ul style="margin:.6rem 0 0 1rem;color:var(--ql-tenue)">{items}</ul></div>',
                            unsafe_allow_html=True)
                st.button("Resolver el taller", key=f"tl_abrir_{t.id}", on_click=_abrir, args=(t.id,), width="stretch",
                          icon=":material/edit_note:", type="primary")


def interfaz() -> None:
    """Página «Talleres»: índice o un taller."""
    if "ql_taller" not in st.session_state:
        pedido = st.query_params.get("taller")
        st.session_state["ql_taller"] = pedido if pedido and buscar(pedido) else ""
    taller_id = st.session_state.get("ql_taller") or ""
    qc.escribir_en_url(None, extra={"taller": taller_id})
    if taller_id:
        _vista_taller(taller_id)
    else:
        _vista_indice()


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def _respuestas_correctas(q: Pregunta) -> dict:
    return {p.clave: (p.opciones[p.correcta] if p.tipo == OPC else f"{p.esperado:.10g}") for p in q.partes}


def _respuestas_malas(q: Pregunta) -> dict:
    return {p.clave: (p.opciones[(p.correcta + 1) % len(p.opciones)] if p.tipo == OPC else f"{p.esperado * 7.31 + 13.7:.10g}")
            for p in q.partes}


def ejecutar_pruebas() -> "qc.RegistroPruebas":
    """Consistencia de los talleres: construcción, calificación de las respuestas correctas y erróneas, y contraste numérico."""
    import math

    import numpy as np
    from talleres import _fisica as f
    from talleres._calificar import evaluar, leer_numero

    r = qc.RegistroPruebas("Talleres de repaso")
    r.comprobar("Identificadores de taller únicos", len({t.id for t in TALLERES}) == len(TALLERES))
    intentos = [(t, original, str(s)) for t in TALLERES for original in (True, False) for s in range(6 if not original else 1)]
    construidos = {}
    ok_construye = ok_correctas = ok_malas = ok_opciones = ok_pesos = ok_temas = True
    for t, original, semilla in intentos:
        try:
            qs = tuple(t.construir(Datos(original, semilla)))
        except Exception as error:
            r.comprobar(f"Construcción de «{t.id}»", False, repr(error))
            ok_construye = False
            continue
        construidos[(t.id, original, semilla)] = qs
        for q in qs:
            if calificar(q, _respuestas_correctas(q)).puntos < q.puntos - 1e-9:
                ok_correctas = False
            if calificar(q, _respuestas_malas(q)).puntos > 1e-9:
                ok_malas = False
            ok_pesos &= all(p.peso > 0 for p in q.partes) and q.puntos > 0
            ok_opciones &= all(0 <= p.correcta < len(p.opciones) for p in q.partes if p.tipo == OPC)
            ok_temas &= (not q.tema) or teoria.buscar(q.tema) is not None
    r.comprobar("Todos los talleres se construyen (datos originales y nuevos)", ok_construye)
    r.comprobar("Las respuestas correctas obtienen el puntaje completo en todas las variantes", ok_correctas)
    r.comprobar("Respuestas erróneas no obtienen puntos", ok_malas)
    r.comprobar("Pesos y puntajes positivos", ok_pesos)
    r.comprobar("La respuesta correcta de cada opción múltiple existe", ok_opciones)
    r.comprobar("Cada tema relacionado existe en el Centro de teoría", ok_temas)
    r.comprobar("Número de preguntas y puntos declarados coinciden con los construidos",
                all(len(construidos[(t.id, True, "0")]) == t.n_preguntas
                    and abs(sum(q.puntos for q in construidos[(t.id, True, "0")]) - t.puntos) < 1e-9 for t in TALLERES))

    # Lectura de números y calificación
    r.comprobar("Lectura de números escritos de varias formas",
                all(math.isclose(leer_numero(s), v, rel_tol=1e-12) for s, v in
                    (("1.256e12", 1.256e12), ("1,256 x 10^12", 1.256e12), ("1,256×10¹²", 1.256e12), ("−3.57", -3.57), ("10^3", 1e3),
                     ("2,5E-3", 2.5e-3))))
    r.comprobar_error("Texto que no es número se rechaza", leer_numero, "abc")
    r.comprobar("Respuesta dentro de la tolerancia es correcta", evaluar("1.26e12", 1.256e12).estado == OK)
    r.comprobar("Respuesta fuera de tolerancia es incorrecta", evaluar("1.5e12", 1.256e12).estado == MAL)
    r.comprobar("Se detecta el factor 2π", evaluar(1.256e12 * 2 * math.pi, 1.256e12).estado == CASI)
    r.comprobar("Se detecta un error de unidades (10⁻¹²)", evaluar(91.7e-12, 91.7).estado == CASI)
    r.comprobar("Se detecta el signo contrario", evaluar(-3.57, 3.57).estado == CASI)

    # Contrastes numéricos independientes de las soluciones
    mu = f.masa_reducida_u("H", "F")
    r.comprobar("HF: 2B = 1.256×10¹² Hz (primera transición, dato del enunciado original)",
                math.isclose(f.frecuencia_rotacion(0, f.momento_de_inercia(mu, 91.68)), 1.256e12, rel_tol=5e-4))
    r.comprobar("HF: de 1.256×10¹² Hz sale r = 91.7 pm", math.isclose(f.longitud_de_enlace_desde_nu(1.256e12, mu), 91.68, rel_tol=5e-4))
    r.comprobar("Vibración de HF con k = 966 N/m: ν̃ = 4138 cm⁻¹ (valor espectroscópico ωe del 1H19F)",
                math.isclose(f.frecuencia_vibracion(966.0, mu) / (f.C * 100), 4138.0, rel_tol=5e-3))
    from scipy import constants as const
    e2_8pe0a0 = const.e ** 2 / (8 * math.pi * const.epsilon_0 * f.A0) / const.e        # e²/(8πε₀a₀) calculado desde las constantes fundamentales
    r.comprobar("Li³⁺ → Li²⁺: afinidad 122.45 eV = 9 e²/(8πε₀a₀)", math.isclose(-f.energia_hidrogenoide_ev(3), 9 * e2_8pe0a0, rel_tol=1e-6))
    r.comprobar("3d: máximo radial en 9 a₀ y sin nodos",
                math.isclose(f.maximos_radiales(3, 2)[0], 9.0, rel_tol=1e-6) and f.nodos_radiales_numericos(3, 2) == [])
    r.comprobar("3p: nodo en 6 a₀; máximos en 3 y 12 a₀",
                math.isclose(f.nodos_radiales_numericos(3, 1)[0], 6.0, rel_tol=1e-3)
                and np.allclose(f.maximos_radiales(3, 1), [3.0, 12.0], rtol=1e-6))
    from scipy.integrate import trapezoid
    rr = np.linspace(0, 150, 300001)
    r.comprobar("Las distribuciones radiales 3p y 3d están normalizadas",
                all(math.isclose(trapezoid(f.distribucion_radial(n, l, rr), rr), 1.0, rel_tol=1e-6) for n, l in ((3, 1), (3, 2), (4, 2))))
    r.comprobar("d_z²: nodos angulares en 54.74° y 125.26°; p_z: plano nodal en 90°",
                np.allclose(f.angulos_nodales_m0(2), [math.degrees(math.acos(1 / math.sqrt(3))), 180 - math.degrees(math.acos(1 / math.sqrt(3)))])
                and np.allclose(f.angulos_nodales_m0(1), [90.0]))
    th = np.linspace(0, math.pi, 200001)
    r.comprobar("|Y₂⁰|² integra 1 sobre la esfera", math.isclose(trapezoid(f.densidad_angular_m0(2, th) * 2 * math.pi * np.sin(th), th), 1.0, rel_tol=1e-9))
    lcao = f.energias_lcao_homonuclear(-13.6, 0.15)
    num = f.energias_lcao_numericas(-13.6, 0.15)
    r.comprobar("LCAO: E± analíticas = autovalores generalizados de SciPy",
                np.allclose(sorted([lcao["E_enlazante"], lcao["E_antienlazante"]]), num, rtol=1e-12))
    c = lcao["c_enlazante"]
    r.comprobar("LCAO: el enlazante está normalizado con solapamiento (2c² + 2c²S = 1)", math.isclose(2 * c * c * (1 + 0.15), 1.0, rel_tol=1e-12))
    x, C = f.huckel_alilo()
    r.comprobar("Hückel del alilo: x = √2, 0, −√2", np.allclose(x, [math.sqrt(2), 0, -math.sqrt(2)], atol=1e-12))
    r.comprobar("Hückel del alilo: ψ₁ = (½, 1/√2, ½)", np.allclose(C[:, 0], [0.5, 1 / math.sqrt(2), 0.5], atol=1e-12))
    I_h2 = f.momento_de_inercia(f.MASA["H"] / 2, 74.14)
    r.comprobar("Rotor plano del H₂, m = 2: E = 4.84×10⁻²¹ J (30.2 meV)",
                math.isclose(f.energia_anillo(2, I_h2), 4.836e-21, rel_tol=2e-3))
    return r
