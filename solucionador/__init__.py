"""
solucionador — Solucionador matemático paso a paso de QUANTUM LAB
=================================================================

A partir de los parámetros que escribe el estudiante muestra, en este orden: la ecuación usada, los datos conocidos, la sustitución numérica con
unidades en cada paso, el resultado y su interpretación física. No entrega solo la respuesta final.

Problemas: efecto fotoeléctrico · partícula en una caja · oscilador armónico · transición de Bohr/Rydberg · De Broglie · incertidumbre.

Archivos: _modelo.py (Solucion, formato numérico) · _problemas.py (resolutores; devuelven una `Solucion`)
Las pruebas comparan cada resultado con las funciones de los simuladores (misma física, constantes de scipy.constants).
Cómo añadir un problema: escribir su resolutor en `_problemas.py`, registrarlo en `PROBLEMAS` y añadir su formulario en `_formulario_*` de abajo.
"""

from __future__ import annotations

import streamlit as st

import quantum_lab_comun as qc
import teoria
from solucionador import _problemas as pr
from talleres._calificar import leer_numero


def _abrir(pagina: str) -> None:
    st.session_state["ql_pagina"] = pagina


def _numero(etiqueta: str, clave: str, defecto: str, ayuda: str = "") -> float:
    """Campo de texto que admite notación científica («1,5e-30», «1.5 x 10^-30»)."""
    texto = st.text_input(etiqueta, value=defecto, key=f"sol_{clave}", help=ayuda or None)
    return leer_numero(texto)


def _masa(clave: str, defecto: str = "electron") -> float:
    claves = list(pr.MASAS)
    elegida = st.selectbox("Partícula", claves, index=claves.index(defecto), key=f"sol_{clave}_part", format_func=lambda k: pr.MASAS[k][0])
    if pr.MASAS[elegida][1] is not None:
        return pr.MASAS[elegida][1]
    return _numero("Masa (kg)", f"{clave}_masa", "1e-26", "Se admite notación científica.")


# ---------------------------------------------------------------------
# Formularios (devuelven la Solucion o lanzan ValueError)
# ---------------------------------------------------------------------
def _form_fotoelectrico():
    import efecto_fotoelectrico as ef
    c1, c2 = st.columns(2)
    with c1:
        metal = st.selectbox("Metal", list(ef.METALES) + [ef.PERSONALIZADO], key="sol_fe_metal")
    if metal == ef.PERSONALIZADO:
        with c2:
            phi = _numero("Función de trabajo Φ (eV)", "fe_phi", "2.3")
    else:
        phi = ef.METALES[metal]
        with c2:
            st.metric("Función de trabajo Φ", f"{phi:.2f} eV")
    lam = _numero("Longitud de onda λ (nm)", "fe_lam", "300")
    return pr.fotoelectrico(lam, phi)


def _form_caja():
    c1, c2 = st.columns(2)
    with c1:
        n = st.number_input("Número cuántico n", min_value=1, max_value=200, value=2, step=1, key="sol_caja_n")
    with c2:
        a = _numero("Longitud de la caja a (nm)", "caja_a", "1")
    return pr.caja(n, a, _masa("caja"))


def _form_oscilador():
    n = st.number_input("Número cuántico n", min_value=0, max_value=200, value=3, step=1, key="sol_osc_n")
    m = _masa("osc")
    modo = st.radio("Dato del resorte", ["Frecuencia angular ω (rad/s)", "Constante de fuerza k (N/m)"], key="sol_osc_modo", horizontal=True)
    if modo.startswith("Frecuencia"):
        return pr.oscilador(n, m, omega=_numero("ω (rad/s)", "osc_w", "1e15"))
    return pr.oscilador(n, m, k_resorte=_numero("k (N/m)", "osc_k", "500"))


def _form_rydberg():
    import modelo_bohr as mb
    c1, c2, c3 = st.columns(3)
    with c1:
        nucleo = st.selectbox("Átomo o ion", list(mb.NUCLEOS), key="sol_ry_nuc", format_func=lambda k: mb.NUCLEOS[k][2])
    with c2:
        ni = st.number_input("Nivel inicial nᵢ", min_value=1, max_value=100, value=3, step=1, key="sol_ry_ni")
    with c3:
        nf = st.number_input("Nivel final n_f", min_value=1, max_value=100, value=2, step=1, key="sol_ry_nf")
    red = st.checkbox("Usar masa reducida", value=True, key="sol_ry_red", help="Corrige por el movimiento del núcleo; el efecto relativo en H es de unos 5×10⁻⁴.")
    return pr.rydberg(nucleo, ni, nf, red)


def _form_de_broglie():
    m = _masa("db")
    modo = st.radio("Dato", ["Rapidez v (m/s)", "Energía cinética K (eV)"], key="sol_db_modo", horizontal=True)
    if modo.startswith("Rapidez"):
        return pr.de_broglie(m, "velocidad", _numero("v (m/s)", "db_v", "1e6"))
    return pr.de_broglie(m, "energia", _numero("K (eV)", "db_k", "100"))


def _form_incertidumbre():
    dx = _numero("Incertidumbre en la posición Δx (nm)", "in_dx", "0.1")
    return pr.incertidumbre(dx, _masa("in"))


FORMULARIOS = {"fotoelectrico": _form_fotoelectrico, "caja": _form_caja, "oscilador": _form_oscilador, "rydberg": _form_rydberg,
               "de_broglie": _form_de_broglie, "incertidumbre": _form_incertidumbre}
ENLACES = {"fotoelectrico": ("fotoelectrico", "fotoelectrico"), "caja": ("caja", "caja"), "oscilador": ("oscilador", "oscilador"),
           "rydberg": ("bohr", "bohr"), "de_broglie": ("de_broglie", None), "incertidumbre": ("incertidumbre", "incertidumbre")}


# ---------------------------------------------------------------------
def mostrar_solucion(s) -> None:
    qc.seccion("1. Ecuaciones que se usan")
    for nombre, ecuacion in s.ecuaciones:
        st.markdown(f"{nombre}:")
        st.latex(ecuacion)
    qc.seccion("2. Datos conocidos")
    st.markdown("  \n".join(f"${d}$" for d in s.datos))
    qc.seccion("3. Sustitución numérica, paso a paso")
    for i, paso in enumerate(s.pasos, 1):
        st.markdown(f"**Paso {i}.** {paso.texto}")
        st.latex(paso.latex)
    for aviso in s.avisos:
        st.warning(aviso, icon=":material/info:")
    qc.seccion("4. Resultados")
    filas = ["| Magnitud | Valor |", "|:--|:--|"] + [f"| {n} | ${v}$ |" for n, v in s.resultados]
    st.markdown("\n".join(filas))
    qc.seccion("5. Interpretación física")
    st.info(s.interpretacion, icon=":material/lightbulb:")


def interfaz() -> None:
    """Página «Solucionador paso a paso»."""
    qc.encabezado_pagina("Herramientas de estudio", "Solucionador paso a paso",
                         "Escribe los datos de un problema y obtén la ecuación usada, los datos, la sustitución numérica con unidades, el resultado "
                         "y su interpretación física.")
    qc.escribir_en_url(None)
    clave = st.selectbox("Tipo de problema", list(pr.PROBLEMAS), key="sol_problema", format_func=lambda k: pr.PROBLEMAS[k])
    try:
        solucion = FORMULARIOS[clave]()
    except ValueError as error:
        st.error(str(error), icon=":material/error:")
        return
    st.divider()
    st.subheader(solucion.titulo)
    mostrar_solucion(solucion)
    tema, sim = ENLACES[clave]
    hallado = teoria.buscar(tema)
    cols = st.columns(2)
    if hallado and hallado[1].estado == teoria.DISPONIBLE:
        cols[0].button("Ver la teoría de este tema", key="sol_teoria", icon=":material/menu_book:", on_click=qc.ir_a_tema, args=(tema,))
    if sim:
        cols[1].button("Abrir el simulador", key="sol_sim", icon=":material/science:", on_click=_abrir, args=(sim,))
    st.caption("Las constantes son las recomendadas por CODATA (scipy.constants). Los resultados coinciden con los de los simuladores del laboratorio.")


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def ejecutar_pruebas() -> "qc.RegistroPruebas":
    import numpy as np
    import efecto_fotoelectrico as ef
    import modelo_bohr as mb
    import oscilador_armonico as oa
    import particula_caja as pc

    reg = qc.RegistroPruebas("Solucionador paso a paso")

    def cerca(a, b, tol=1e-9):
        return abs(a - b) <= tol * max(abs(b), 1e-300)

    s = pr.fotoelectrico(300, 2.28)
    v = s.valores
    reg.comprobar("Fotoeléctrico: K_máx coincide con el simulador", cerca(v["K_ev"], float(ef.energia_cinetica_maxima(v["nu"], 2.28))))
    reg.comprobar("Fotoeléctrico: λ umbral coincide con el simulador", cerca(v["lambda0_nm"], ef.longitud_umbral_nm(2.28)))
    reg.comprobar("Fotoeléctrico: rapidez máxima coincide con el simulador", cerca(v["v_max"], ef.velocidad_maxima(v["K_ev"])))
    reg.comprobar("Fotoeléctrico: bajo el umbral no hay emisión ni K_máx", not pr.fotoelectrico(600, 2.28).valores["emision"] and pr.fotoelectrico(600, 2.28).valores["K_ev"] == 0.0)
    s = pr.caja(2, 1.0, qc.M_E)
    reg.comprobar("Caja: energía coincide con el simulador", cerca(s.valores["E_J"], pc.energia_nivel(2, 1e-9, qc.M_E)))
    reg.comprobar("Caja: λ y momento coinciden con el simulador", cerca(s.valores["lambda"], pc.longitud_onda_de_broglie(2, 1e-9)) and cerca(s.valores["p"], pc.momento_estado(2, 1e-9)))
    reg.comprobar("Caja: nodos = n − 1", s.valores["nodos"] == 1 and len(pc.nodos_interiores(5, 1.0)) == pr.caja(5, 1, qc.M_E).valores["nodos"])
    s = pr.oscilador(3, qc.M_E, omega=1e15)
    reg.comprobar("Oscilador: energía y punto de retorno coinciden con el simulador",
                  cerca(s.valores["E_J"], oa.energia_teorica(3, 1e15)) and cerca(s.valores["x_ret"], oa.punto_retorno(3, qc.M_E, 1e15)))
    reg.comprobar("Oscilador: ω = √(k/m) da el mismo resultado que dar ω", cerca(pr.oscilador(2, 1e-26, k_resorte=500).valores["omega"], float(np.sqrt(500 / 1e-26))))
    s = pr.rydberg("H", 3, 2)
    reg.comprobar("Rydberg: Hα coincide con el simulador (masa reducida)", cerca(s.valores["lambda_nm"], mb.longitud_rydberg(3, 2, "H") * 1e9))
    reg.comprobar("Rydberg: 3 → 2 es emisión y 2 → 3 es absorción con la misma λ",
                  s.valores["emite"] and not pr.rydberg("H", 2, 3).valores["emite"] and cerca(pr.rydberg("H", 2, 3).valores["lambda_nm"], s.valores["lambda_nm"]))
    reg.comprobar("De Broglie: velocidad y energía equivalentes dan la misma λ",
                  cerca(pr.de_broglie(qc.M_E, "energia", 100).valores["lambda"], pr.de_broglie(qc.M_E, "velocidad", pr.de_broglie(qc.M_E, "energia", 100).valores["v"]).valores["lambda"]))
    reg.comprobar("De Broglie: electrón de 100 eV ≈ 0.1226 nm", abs(pr.de_broglie(qc.M_E, "energia", 100).valores["lambda"] * 1e9 - 0.12264) < 1e-4)
    reg.comprobar("Incertidumbre: Δp = ħ/(2Δx)", cerca(pr.incertidumbre(0.1, qc.M_E).valores["dp"], qc.HBAR / (2 * 1e-10)))
    for descripcion, f, args in (("λ ≤ 0", pr.fotoelectrico, (-1, 2.0)), ("n no entero", pr.caja, (1.5, 1, qc.M_E)), ("masa negativa", pr.caja, (1, 1, -1.0)),
                                 ("ω y k a la vez", pr.oscilador, (1, qc.M_E, 1e15, 5.0)), ("nᵢ = n_f", pr.rydberg, ("H", 2, 2)),
                                 ("v ≥ c", pr.de_broglie, (qc.M_E, "velocidad", 4e8)), ("Δx = 0", pr.incertidumbre, (0, qc.M_E))):
        reg.comprobar_error(f"Validación: {descripcion}", f, *args)
    return reg
