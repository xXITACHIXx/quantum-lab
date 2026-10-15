"""
ejercicios — Ejercicios de práctica de QUANTUM LAB
==================================================

Los ejercicios de las diapositivas de clase (Example Problems y Classwork) y los del libro trabajados en el cuaderno, cada uno
con su solución paso a paso. La solución se puede consultar en cualquier momento; si el ejercicio tiene un resultado numérico o
una opción, el estudiante puede además comprobar su respuesta (con el mismo calificador de los talleres).

Archivos:
    _modelo.py          Ejercicio, fuentes, temas y la plantilla `llenar`
    clase_s1_s5.py      Semanas 1, 2 y 5
    clase_s6_s13.py     Semanas 6, 7, 9, 10, 11 y 13
    libro.py            ejercicios del libro (rotación, oscilador, átomo de hidrógeno)
    cuaderno.py         ejercicios de clase del cuaderno que no están en las diapositivas

Cómo añadir un ejercicio: escribir una función que devuelva un `Ejercicio(...)` en el archivo de su fuente y añadirla a la tupla
EJERCICIOS de ese archivo. Las pruebas comprueban que cada respuesta esperada obtenga la nota completa.
"""

from __future__ import annotations

import math

import streamlit as st

import quantum_lab_comun as qc
import teoria
from ejercicios import clase_s1_s5, clase_s6_s13, cuaderno, libro
from ejercicios._modelo import CLASE, CUADERNO, FUENTES, LIBRO, TEMAS, Ejercicio, calificar
from talleres._calificar import CASI, INVALIDA, OK, VACIA
from talleres._modelo import NUM, OPC

EJERCICIOS: tuple[Ejercicio, ...] = (*clase_s1_s5.EJERCICIOS, *clase_s6_s13.EJERCICIOS, *cuaderno.EJERCICIOS, *libro.EJERCICIOS)
_POR_ID = {e.id: e for e in EJERCICIOS}
TODAS, TODOS = "Todas las fuentes", "Todos los temas"


def buscar(ej_id: str) -> Ejercicio | None:
    return _POR_ID.get(ej_id)


def filtrar(fuente: str = TODAS, tema: str = TODOS, texto: str = "") -> list[Ejercicio]:
    """Ejercicios que cumplen los filtros (tema = título de TEMAS)."""
    texto = (texto or "").strip().lower()
    salida = []
    for e in EJERCICIOS:
        if fuente != TODAS and e.fuente != fuente:
            continue
        if tema != TODOS and TEMAS.get(e.tema) != tema:
            continue
        if texto and texto not in f"{e.titulo} {e.referencia} {e.enunciado}".lower():
            continue
        salida.append(e)
    return salida


# ---------------------------------------------------------------------
# Estado de la sesión
# ---------------------------------------------------------------------
def _resultados() -> dict:
    return st.session_state.setdefault("ej_res", {})


def _clave(ej: Ejercicio, parte: str) -> str:
    return f"ej_{ej.id}_{parte}"


def _comprobar(ej_id: str) -> None:
    ej = buscar(ej_id)
    respuestas = {p.clave: st.session_state.get(_clave(ej, p.clave)) for p in ej.partes}
    _resultados()[ej_id] = calificar(ej, respuestas)


def _ir(ej_id: str) -> None:
    st.session_state["ej_sel"] = ej_id


def _limpiar_filtros() -> None:
    st.session_state["ej_fuente"] = TODAS
    st.session_state["ej_tema"] = TODOS
    st.session_state["ej_buscar"] = ""


# ---------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------
def _formato_esperado(parte) -> str:
    v = parte.esperado
    if v == 0:
        return "0"
    return f"{v:.4g} {parte.unidad}".strip()


def _mensaje(parte, res) -> None:
    if parte.tipo == OPC:
        if res.estado == OK:
            st.success(f"Correcto. {parte.explicacion}", icon=":material/check_circle:")
        elif res.estado == VACIA:
            st.warning("Sin responder.", icon=":material/help:")
        else:
            st.error("No es esa. Revisa la pista o abre la solución paso a paso.", icon=":material/cancel:")
        return
    if res.estado == OK:
        st.success(f"Correcto (≈ {_formato_esperado(parte)}).", icon=":material/check_circle:")
    elif res.estado == CASI:
        st.warning(f"{res.mensaje}", icon=":material/lightbulb:")
    elif res.estado in (VACIA, INVALIDA):
        st.warning(res.mensaje, icon=":material/help:")
    else:
        st.error("No coincide. Revisa la pista o abre la solución paso a paso.", icon=":material/cancel:")


def _tema_relacionado(ej: Ejercicio) -> None:
    hallado = teoria.buscar(ej.tema)
    if hallado is None:
        return
    _, tema = hallado
    if tema.estado == teoria.DISPONIBLE:
        st.button(f"Repasar la teoría: {tema.titulo}", key=f"ej_teoria_{ej.id}", icon=":material/menu_book:",
                  on_click=qc.ir_a_tema, args=(ej.tema,))


def _vista_ejercicio(ej: Ejercicio, numero: int, total: int) -> None:
    cal = _resultados().get(ej.id)
    with st.container(border=True):
        qc.seccion(f"Ejercicio {numero} de {total}  ·  {ej.titulo}")
        st.caption(f"{ej.fuente}  ·  {ej.referencia}  ·  {TEMAS.get(ej.tema, ej.tema)}  ·  Nivel: {ej.dificultad}")
        st.markdown(ej.enunciado)
        if ej.nota:
            st.info(ej.nota, icon=":material/info:")

        if ej.comprobable:
            st.markdown("**Comprueba tu resultado** (opcional: puedes ver la solución sin responder)")
            for p in ej.partes:
                clave = _clave(ej, p.clave)
                if p.tipo == OPC:
                    st.radio(p.etiqueta, p.opciones, index=None, key=clave)
                else:
                    etiqueta = p.etiqueta + (f"  [{p.unidad}]" if p.unidad and "(" not in p.etiqueta else "")
                    st.text_input(etiqueta, key=clave, placeholder="Escribe un número, por ejemplo 3.00e-19 o 3,00 x 10^-19")
                if cal is not None:
                    _mensaje(p, cal.resultados[p.clave])
            c1, c2 = st.columns([1, 3], vertical_alignment="center")
            c1.button("Comprobar", key=f"ej_{ej.id}_btn", type="primary", icon=":material/fact_check:", width="stretch",
                      on_click=_comprobar, args=(ej.id,))
            if cal is not None:
                bien = sum(1 for r in cal.resultados.values() if r.estado == OK)
                c2.progress(cal.fraccion, text=f"{bien} de {len(ej.partes)} {'parte correcta' if len(ej.partes) == 1 else 'partes correctas'}")

        if ej.pistas:
            with st.expander("Pistas (sin revelar la solución)", icon=":material/lightbulb:"):
                for i, pista in enumerate(ej.pistas, 1):
                    st.markdown(f"**Pista {i}.** {pista}")
        with st.expander("Ver la solución paso a paso", icon=":material/menu_book:"):
            st.markdown(ej.solucion)
        _tema_relacionado(ej)


def _navegacion(lista: list[Ejercicio], indice: int) -> None:
    c1, c2, c3 = st.columns([1, 1, 2], vertical_alignment="center")
    anterior = lista[indice - 1].id if indice > 0 else None
    siguiente = lista[indice + 1].id if indice < len(lista) - 1 else None
    c1.button("Anterior", key="ej_ant", icon=":material/arrow_back:", width="stretch", disabled=anterior is None,
              on_click=_ir, args=(anterior,))
    c2.button("Siguiente", key="ej_sig", icon=":material/arrow_forward:", width="stretch", disabled=siguiente is None,
              on_click=_ir, args=(siguiente,))


def _tabla(lista: list[Ejercicio]) -> list[dict]:
    resultados = _resultados()
    filas = []
    for i, e in enumerate(lista, 1):
        cal = resultados.get(e.id)
        estado = "—" if not e.comprobable else ("Sin comprobar" if cal is None else ("Correcto" if cal.fraccion >= 0.999 else f"{100 * cal.fraccion:.0f} %"))
        filas.append({"N.º": i, "Ejercicio": e.titulo, "Fuente": e.fuente, "Referencia": e.referencia,
                      "Tema": TEMAS.get(e.tema, e.tema), "Nivel": e.dificultad, "Mi resultado": estado})
    return filas


def interfaz() -> None:
    """Página «Ejercicios de práctica»."""
    if "ej_sel" not in st.session_state:
        pedido = st.query_params.get("ej")
        st.session_state["ej_sel"] = pedido if pedido and buscar(pedido) else EJERCICIOS[0].id

    qc.encabezado_pagina("Repaso", "Ejercicios de práctica",
                         "Los ejercicios de las diapositivas de clase y del libro, con su solución explicada paso a paso. "
                         "Intenta resolverlos; si te atascas, abre una pista o la solución completa.")
    resultados = _resultados()
    correctos = sum(1 for c in resultados.values() if c.fraccion >= 0.999)
    qc.metricas([("Ejercicios", f"{len(EJERCICIOS)}"),
                 ("De las diapositivas", f"{sum(e.fuente == CLASE for e in EJERCICIOS)}"),
                 ("Del libro y el cuaderno", f"{sum(e.fuente in (LIBRO, CUADERNO) for e in EJERCICIOS)}"),
                 ("Resueltos bien (esta sesión)", f"{correctos}")], columnas=4)

    c1, c2, c3, c4 = st.columns([2, 2, 2, 1], vertical_alignment="bottom")
    with c1:
        st.selectbox("Fuente", (TODAS, *FUENTES), key="ej_fuente")
    with c2:
        temas_presentes = [t for k, t in TEMAS.items() if any(e.tema == k for e in EJERCICIOS)]
        st.selectbox("Tema", (TODOS, *temas_presentes), key="ej_tema")
    with c3:
        st.text_input("Buscar", key="ej_buscar", placeholder="Por ejemplo: oscilador, Lyman, Semana 9…")
    with c4:
        st.button("Limpiar", key="ej_limpiar", icon=":material/filter_alt_off:", on_click=_limpiar_filtros, width="stretch")

    lista = filtrar(st.session_state.get("ej_fuente", TODAS), st.session_state.get("ej_tema", TODOS),
                    st.session_state.get("ej_buscar", ""))
    if not lista:
        st.warning("Ningún ejercicio coincide con los filtros.", icon=":material/search_off:")
        return
    ids = [e.id for e in lista]
    if st.session_state.get("ej_sel") not in ids:
        st.session_state["ej_sel"] = ids[0]
    st.selectbox("Ejercicio", ids, key="ej_sel",
                 format_func=lambda i: f"{ids.index(i) + 1}. {buscar(i).titulo}  —  {buscar(i).referencia}")
    ej = buscar(st.session_state["ej_sel"])
    indice = ids.index(ej.id)
    qc.escribir_en_url(None, extra={"ej": ej.id})

    _navegacion(lista, indice)
    _vista_ejercicio(ej, indice + 1, len(lista))
    with st.expander(f"Lista de los {len(lista)} ejercicios de esta selección", icon=":material/list:"):
        st.dataframe(_tabla(lista), hide_index=True, width="stretch")


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def respuestas_correctas(ej: Ejercicio) -> dict:
    return {p.clave: (p.opciones[p.correcta] if p.tipo == OPC else f"{p.esperado:.10g}") for p in ej.partes}


def ejecutar_pruebas() -> "qc.RegistroPruebas":
    """Estructura de los ejercicios, calificación de las respuestas correctas y contrastes numéricos independientes."""
    from scipy import constants as const
    from scipy.integrate import quad

    reg = qc.RegistroPruebas("Ejercicios de práctica")
    ids = [e.id for e in EJERCICIOS]
    reg.comprobar("Identificadores únicos", len(ids) == len(set(ids)), f"{len(ids)} ejercicios")
    reg.comprobar("Temas válidos (existen en el Centro de teoría)",
                  all(e.tema in TEMAS and teoria.buscar(e.tema) is not None for e in EJERCICIOS))
    reg.comprobar("Fuentes válidas", all(e.fuente in FUENTES for e in EJERCICIOS))
    reg.comprobar("Toda solución está escrita paso a paso", all(e.solucion.count("#### Paso") >= 3 for e in EJERCICIOS))
    reg.comprobar("Ninguna plantilla quedó sin rellenar", all("<<" not in e.solucion and "<<" not in e.enunciado for e in EJERCICIOS))
    reg.comprobar("Las opciones correctas existen",
                  all(0 <= p.correcta < len(p.opciones) for e in EJERCICIOS for p in e.partes if p.tipo == OPC))
    reg.comprobar("Respuestas correctas → nota completa en todos los ejercicios comprobables",
                  all(calificar(e, respuestas_correctas(e)).fraccion > 0.999 for e in EJERCICIOS if e.comprobable))

    # Contrastes numéricos independientes (fórmulas cerradas o integración numérica)
    h, hb, me, e, c = const.h, const.hbar, const.m_e, const.e, const.c
    esp = {(ej.id, p.clave): p.esperado for ej in EJERCICIOS for p in ej.partes if p.tipo == NUM}
    casos = [
        ("Fotoeléctrico: v = 8.12×10⁵ m/s", esp[("s1_fotoelectrico", "v")], 8.12e5, 0.005),
        ("Radio de Bohr = 52.9 pm", esp[("s1_radio_bohr", "r")], const.physical_constants["Bohr radius"][0], 1e-6),
        ("Límite de Lyman ≈ 91.2 nm", esp[("s1_lyman", "lam")], 91.18, 0.002),
        ("Penetración ≈ 0.195 nm", esp[("s5_penetracion", "d")], 0.1952, 0.002),
        ("Caja: P(tercio central) = 0.609", esp[("s6_prob_tercio", "P")], quad(lambda x: 2 * math.sin(math.pi * x) ** 2, 1 / 3, 2 / 3)[0], 1e-9),
        ("Caja: ΔxΔp = 0.568 ħ", esp[("s7_dxdp", "prod")], math.sqrt((math.pi ** 2 - 6) / 12), 1e-9),
        ("Oscilador n = 4: nodo exterior 1.6507/α", esp[("s9_nodos", "x2")], 1.650680123885784, 1e-9),
        ("Cono más cercano con l = 1000: 1.81°", esp[("s10_conos", "theta")], math.degrees(math.acos(math.sqrt(1000 / 1001))), 1e-9),
        ("3s: nodos en 1.902 a₀ y 7.098 a₀", esp[("s11_nodos3s", "r2")], 1.5 * (3 + math.sqrt(3)), 1e-9),
        ("Variacional: E mínima = 0.1270 h²/ma²", esp[("s13_variacional", "Emin")], 0.12701790140, 1e-6),
        ("D₂: k = 576 N/m", esp[("l08_d2", "k")], 575.7, 0.002),
        ("³⁵Cl₂: k = 323.5 N/m", esp[("l16_cl2", "k")], 323.5, 0.002),
        ("Moneda: n ≈ 9.76×10²⁸", esp[("l18_moneda", "n")], 9.759e28, 0.002),
        ("ψ₃₂₀ negativo: P = 2/(3√3)", esp[("h03_negativo", "P")], 2 / (3 * math.sqrt(3)), 1e-9),
        ("1s: P(a₀<r<2a₀) = 0.4386", esp[("h05_prob", "P")], quad(lambda x: 4 * x * x * math.exp(-2 * x), 1, 2)[0], 1e-9),
        ("1s: ⟨V⟩ = −27.21 eV", esp[("h04_potencial", "V")], -2 * 13.605693, 1e-4),
    ]
    for nombre, valor, ref, tol in casos:
        reg.comprobar(nombre, math.isclose(valor, ref, rel_tol=tol), f"{valor:.6g} frente a {ref:.6g}")
    return reg
