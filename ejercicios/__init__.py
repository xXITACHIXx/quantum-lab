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
from ejercicios import _calidad, _estado, _figuras, _progreso, clase_s1_s5, clase_s6_s13, cuaderno, libro
from ejercicios._modelo import CLASE, CUADERNO, FUENTES, LIBRO, TEMAS, Ejercicio, calificar
from talleres._calificar import CASI, INVALIDA, OK, VACIA
from talleres._modelo import NUM, OPC

EJERCICIOS: tuple[Ejercicio, ...] = (*clase_s1_s5.EJERCICIOS, *clase_s6_s13.EJERCICIOS, *cuaderno.EJERCICIOS, *libro.EJERCICIOS)
_POR_ID = {e.id: e for e in EJERCICIOS}
IDS = tuple(e.id for e in EJERCICIOS)
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


def _marcar(ej_id: str) -> None:
    """Callback de la casilla «Marcar como resuelto»."""
    _estado.marcar(ej_id, bool(st.session_state.get(f"ej_hecho_{ej_id}")))


def _clave(ej: Ejercicio, parte: str) -> str:
    return f"ej_{ej.id}_{parte}"


def _comprobar(ej_id: str) -> None:
    ej = buscar(ej_id)
    respuestas = {p.clave: st.session_state.get(_clave(ej, p.clave)) for p in ej.partes}
    cal = _resultados()[ej_id] = calificar(ej, respuestas)
    _estado.registrar_calificacion(ej_id, cal)


def _ver_solucion(ej_id: str) -> None:
    """Callback del interruptor de la solución: abrirla sin haber resuelto el ejercicio lo deja por repasar."""
    if st.session_state.get(f"ej_sol_{ej_id}"):
        _estado.registrar_solucion(ej_id)


def _ir(ej_id: str) -> None:
    st.session_state["ej_sel"] = ej_id


def _siguiente_pendiente(ids: list, actual: str) -> None:
    """Callback: salta al siguiente ejercicio de la lista que aún no está resuelto (da la vuelta al final)."""
    inicio = ids.index(actual) if actual in ids else -1
    for k in range(1, len(ids) + 1):
        candidato = ids[(inicio + k) % len(ids)]
        if candidato not in _estado.hechos():
            st.session_state["ej_sel"] = candidato
            return


def _borrar_progreso() -> None:
    _estado.borrar_todo()


def _cargar_progreso(archivo) -> None:
    try:
        st.session_state["ej_bk_msg"] = ("ok", _estado.cargar_copia(archivo.getvalue()))
    except ValueError as exc:
        st.session_state["ej_bk_msg"] = ("error", str(exc))


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
            st.error("No es esa. Se recomienda revisar la pista o consultar la solución paso a paso.", icon=":material/cancel:")
        return
    if res.estado == OK:
        st.success(f"Correcto (≈ {_formato_esperado(parte)}).", icon=":material/check_circle:")
    elif res.estado == CASI:
        st.warning(f"{res.mensaje}", icon=":material/lightbulb:")
    elif res.estado in (VACIA, INVALIDA):
        st.warning(res.mensaje, icon=":material/help:")
    else:
        st.error("No coincide. Se recomienda revisar la pista o consultar la solución paso a paso.", icon=":material/cancel:")


def _tema_relacionado(ej: Ejercicio) -> None:
    hallado = teoria.buscar(ej.tema)
    if hallado is None:
        return
    _, tema = hallado
    if tema.estado == teoria.DISPONIBLE:
        st.button(f"Repasar la teoría: {tema.titulo}", key=f"ej_teoria_{ej.id}", icon=":material/menu_book:",
                  on_click=qc.ir_a_tema, args=(ej.tema,))


def _figuras_del_ejercicio(ej: Ejercicio) -> None:
    """Gráficas interactivas de este ejercicio (si las tiene), con deslizador cuando la figura depende de un parámetro."""
    for i, fig in enumerate(_figuras.figuras_de(ej.id)):
        with st.expander(f"Gráfica interactiva: {fig.titulo}", icon=":material/show_chart:"):
            st.markdown(fig.descripcion)
            valor = None
            if fig.parametro:
                etiqueta, minimo, maximo, inicial = fig.parametro
                valor = st.slider(etiqueta, minimo, maximo, inicial, key=f"ej_fig_{ej.id}_{i}")
            qc.mostrar_plotly(fig.dibujar(valor), clave=f"ej_plot_{ej.id}_{i}")


def _vista_ejercicio(ej: Ejercicio, numero: int, total: int) -> None:
    cal = _resultados().get(ej.id)
    with st.container(border=True):
        qc.seccion(f"Ejercicio {numero} de {total}  ·  {ej.titulo}")
        st.caption(f"{ej.fuente}  ·  {ej.referencia}  ·  {TEMAS.get(ej.tema, ej.tema)}  ·  Nivel: {ej.dificultad}")
        st.markdown(ej.enunciado)
        if ej.nota:
            st.info(ej.nota, icon=":material/info:")

        if ej.comprobable:
            st.markdown("**Comprobar el resultado** (opcional; la solución puede consultarse sin responder)")
            for p in ej.partes:
                clave = _clave(ej, p.clave)
                if p.tipo == OPC:
                    st.radio(p.etiqueta, p.opciones, index=None, key=clave)
                else:
                    etiqueta = p.etiqueta + (f"  [{p.unidad}]" if p.unidad and "(" not in p.etiqueta else "")
                    st.text_input(etiqueta, key=clave, placeholder="Escribir un número, por ejemplo 3.00e-19 o 3,00 x 10^-19")
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
        st.toggle("Mostrar la solución paso a paso", key=f"ej_sol_{ej.id}", on_change=_ver_solucion, args=(ej.id,),
                  help="Al abrir la solución sin haber resuelto el ejercicio, este queda en «Mi repaso».")
        if st.session_state.get(f"ej_sol_{ej.id}"):
            with st.container(border=True):
                st.markdown(ej.solucion)
        _figuras_del_ejercicio(ej)
        clave_hecho = f"ej_hecho_{ej.id}"
        st.session_state[clave_hecho] = ej.id in _estado.hechos()
        st.checkbox("Marcar como resuelto", key=clave_hecho, on_change=_marcar, args=(ej.id,))
        _tema_relacionado(ej)


def _navegacion(lista: list[Ejercicio], indice: int) -> None:
    c1, c2, c3 = st.columns([1, 1, 2], vertical_alignment="center")
    anterior = lista[indice - 1].id if indice > 0 else None
    siguiente = lista[indice + 1].id if indice < len(lista) - 1 else None
    ids = [e.id for e in lista]
    pendientes = [i for i in ids if i not in _estado.hechos()]
    c1.button("Anterior", key="ej_ant", icon=":material/arrow_back:", width="stretch", disabled=anterior is None,
              on_click=_ir, args=(anterior,))
    c2.button("Siguiente", key="ej_sig", icon=":material/arrow_forward:", width="stretch", disabled=siguiente is None,
              on_click=_ir, args=(siguiente,))
    c3.button("Siguiente sin resolver", key="ej_pend", icon=":material/skip_next:", width="stretch",
              disabled=not pendientes or pendientes == [ids[indice]], on_click=_siguiente_pendiente, args=(ids, ids[indice]))


def _tabla(lista: list[Ejercicio]) -> list[dict]:
    bit = _estado.bitacora()
    filas = []
    for i, e in enumerate(lista, 1):
        reg = bit.get(e.id, {"intentos": 0, "aciertos": 0})
        filas.append({"N.º": i, "Ejercicio": e.titulo, "Fuente": e.fuente, "Referencia": e.referencia,
                      "Tema": TEMAS.get(e.tema, e.tema), "Nivel": e.dificultad, "Estado": _estado.estado_de(e.id),
                      "Comprobaciones": reg["intentos"], "Aciertos": reg["aciertos"]})
    return filas


def copia_de_seguridad(clave: str = "ej") -> None:
    """Descarga, carga y borrado del progreso (se usa en Ejercicios y en Mi repaso)."""
    with st.expander("Copia de seguridad de mi progreso", icon=":material/save:"):
        st.markdown("El archivo contiene los ejercicios resueltos, los pendientes de repaso, el registro de intentos y el historial de "
                    "exámenes. No se envía a ningún servidor: queda en su dispositivo. Permite continuar en otro navegador o dispositivo.")
        qc.boton_descarga("Descargar mi progreso (JSON)", _estado.copia_json().encode("utf-8"),
                          "progreso_ejercicios.json", "application/json")
        archivo = st.file_uploader("Cargar un progreso guardado", type=["json"], key=f"{clave}_bk_sub")
        if archivo is not None:
            st.button("Combinar con mi progreso", key=f"{clave}_bk_cargar", icon=":material/upload:", on_click=_cargar_progreso, args=(archivo,))
        mensaje = st.session_state.pop("ej_bk_msg", None)
        if mensaje:
            (st.success if mensaje[0] == "ok" else st.error)(mensaje[1])
        st.button("Borrar todo mi progreso", key=f"{clave}_bk_borrar", icon=":material/delete:", on_click=_borrar_progreso)


def interfaz() -> None:
    """Página «Ejercicios de práctica»."""
    if "ej_sel" not in st.session_state:
        pedido = st.query_params.get("ej")
        st.session_state["ej_sel"] = pedido if pedido and buscar(pedido) else EJERCICIOS[0].id

    qc.encabezado_pagina("Repaso", "Ejercicios de práctica",
                         "Los ejercicios de las diapositivas de clase y del libro, con su solución explicada paso a paso. "
                         "Se recomienda intentar la resolución antes de consultar una pista o la solución completa.")
    hechos = _estado.hechos()
    qc.metricas([("Ejercicios", f"{len(EJERCICIOS)}"),
                 ("De las diapositivas", f"{sum(e.fuente == CLASE for e in EJERCICIOS)}"),
                 ("Del libro y el cuaderno", f"{sum(e.fuente in (LIBRO, CUADERNO) for e in EJERCICIOS)}"),
                 ("Resueltos", f"{len(hechos)} de {len(EJERCICIOS)}"),
                 ("Por repasar", f"{len(_estado.repasar())}")], columnas=5)
    st.progress(len(hechos) / len(EJERCICIOS), text=f"{len(hechos)} de {len(EJERCICIOS)} ejercicios resueltos. "
                "El progreso se conserva en la dirección de esta página: guárdela en favoritos para continuar posteriormente.")

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
    copia_de_seguridad()


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

    reg.comprobar("Reglas de calidad (ids, referencias, pasos numerados, pistas, $ balanceados)",
                  not any(_calidad.revisar(e) for e in EJERCICIOS),
                  "; ".join(f"{e.id}: {m}" for e in EJERCICIOS for m in _calidad.revisar(e))[:300])
    reg.comprobar("Progreso: el código de cada ejercicio es único", len({_progreso.token(i) for i in ids}) == len(ids))
    reg.comprobar("Progreso: guardar y recuperar no pierde nada",
                  _progreso.decodificar(_progreso.codificar(set(ids), ids), ids) == set(ids))
    reg.comprobar("Gráficas: todas pertenecen a un ejercicio existente", all(i in _POR_ID for i in _figuras.FIGURAS))
    reg.comprobar("Gráficas: todas se dibujan",
                  all(len(f.dibujar().data) > 0
                      for fs in _figuras.FIGURAS.values() for f in fs))

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
