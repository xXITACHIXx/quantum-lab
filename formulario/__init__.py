"""
formulario — Formulario de constantes, conversiones y fórmulas de QUANTUM LAB
==============================================================================

Consulta rápida para resolver ejercicios y estudiar:

    Constantes     valores CODATA (scipy.constants) con su incertidumbre, combinaciones útiles y unidades atómicas
    Conversor      energía (J, eV, hartree, cm⁻¹, Hz, nm, kJ/mol, K…), longitud, masa y ángulo
    Fórmulas       las expresiones de cada tema del curso, con la definición de cada símbolo y sus condiciones de validez
    Masas atómicas isótopos usados en los ejercicios y calculadora de masa reducida

Cada fórmula con un valor numérico verificable lleva un contraste: la expresión se evalúa y se compara con un valor de referencia
independiente (ver `ejecutar_pruebas` y `test_formulario.py`).

Archivos: _modelo.py (Formula, Bloque, Seccion) · _constantes.py · _conversion.py · _masas.py · _formulas_a.py y _formulas_b.py (contenido)

Cómo añadir una fórmula: agregar `F(nombre, latex, nota, contraste)` al bloque de su sección en `_formulas_a.py` o `_formulas_b.py`.
Si la fórmula produce un número comprobable, escribir el `contraste` (función que devuelve (calculado, referencia)).
"""

from __future__ import annotations

import math

import scipy
import streamlit as st

import ejercicios
import quantum_lab_comun as qc
import teoria
from ejercicios._modelo import TEMAS
from formulario import _constantes, _conversion, _formulas_a as fa, _formulas_b as fb, _masas
from talleres._calificar import leer_numero

SECCIONES = (fa.CUERPO_NEGRO, fa.FOTOELECTRICO, fa.DE_BROGLIE, fa.BOHR, fa.ONDAS, fa.SCHRODINGER, fa.OPERADORES, fa.POSTULADOS,
             fa.LIBRE_PARED, fb.CAJA, fb.CONMUTADORES, fb.OSCILADOR, fb.ESFERA, fb.HIDROGENO, fb.ESPIN, fb.APROXIMADOS, fb.MOLECULARES,
             fb.MATEMATICAS)
_POR_ID = {s.id: s for s in SECCIONES}
TODOS = "Todos los temas"


def edicion_codata() -> str:
    """SciPy 1.15 o posterior incluye CODATA 2022; las versiones anteriores, CODATA 2018."""
    mayor, menor = (int(x) for x in scipy.__version__.split(".")[:2])
    return "2022" if (mayor, menor) >= (1, 15) else "2018"


# ---------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------
def tabla_constantes_markdown() -> str:
    filas = []
    for grupo in _constantes.GRUPOS:
        filas.append(f"\n**{grupo}**\n\n| Símbolo | Nombre | Valor | Unidad | Incertidumbre relativa |\n|:--|:--|--:|:--|--:|")
        for c in (x for x in _constantes.CONSTANTES if x.grupo == grupo):
            filas.append(f"| ${c.simbolo}$ | {c.nombre} | ${_constantes.valor_latex(c)}$ | ${c.unidad}$ | {_constantes.incertidumbre_relativa(c)} |")
    return "\n".join(filas)


def como_markdown(secciones=SECCIONES) -> str:
    """Todo el formulario en Markdown con LaTeX (para imprimir, pegar en un cuaderno o convertir a PDF)."""
    partes = [f"# Formulario de mecánica cuántica\n\nConstantes: valores recomendados por CODATA {edicion_codata()}.\n", "## Constantes fundamentales",
              tabla_constantes_markdown()]
    for s in secciones:
        partes.append(f"\n## {s.titulo}\n\n{s.resumen}")
        for b in s.bloques:
            partes.append(f"\n### {b.titulo}")
            for f in b.formulas:
                partes.append(f"\n**{f.nombre}**\n\n$$\n{f.latex}\n$$" + (f"\n\n{f.nota}" if f.nota else ""))
    return "\n".join(partes) + "\n"


def buscar_formulas(texto: str) -> list[tuple]:
    """[(sección, bloque, fórmula)] cuyo nombre, expresión o nota contienen el texto (sin distinguir mayúsculas)."""
    t = (texto or "").strip().lower()
    if not t:
        return []
    return [(s, b, f) for s in SECCIONES for b in s.bloques for f in b.formulas
            if t in f"{f.nombre} {f.latex} {f.nota} {s.titulo} {b.titulo}".lower()]


# ---------------------------------------------------------------------
# Pestañas
# ---------------------------------------------------------------------
def _pestana_constantes() -> None:
    st.markdown(f"Valores recomendados por **CODATA {edicion_codata()}**, leídos de `scipy.constants`. Las constantes que el SI define "
                "desde 2019 ($c$, $h$, $e$, $k_B$, $N_A$) son **exactas**; en las demás se indica la incertidumbre relativa. "
                "Las cifras mostradas son las que justifica esa incertidumbre.")
    st.markdown(tabla_constantes_markdown())
    with st.expander("Combinaciones de constantes de uso frecuente", icon=":material/functions:"):
        filas = ["| Expresión | Significado | Valor | Unidad |", "|:--|:--|--:|:--|"]
        for d in _constantes.combinaciones():
            filas.append(f"| ${d.expresion}$ | {d.nombre} | ${_constantes.latex_cientifico(d.valor, 8)}$ | ${d.unidad}$ |")
        st.markdown("\n".join(filas))
    with st.expander("Unidades atómicas (Hartree)", icon=":material/straighten:"):
        st.markdown("En unidades atómicas $\\hbar=m_e=e=4\\pi\\varepsilon_0=1$; entonces $c=1/\\alpha\\approx137.036$.")
        filas = ["| Magnitud | Unidad atómica | Valor en el SI |", "|:--|:--|--:|"]
        for magnitud, simbolo, valor, unidad in _constantes.unidades_atomicas():
            filas.append(f"| {magnitud} | ${simbolo}$ | ${_constantes.latex_cientifico(valor, 9)}\\ {unidad}$ |")
        st.markdown("\n".join(filas))


def _leer(texto: str):
    try:
        return leer_numero(texto), None
    except ValueError as exc:
        return None, str(exc)


def _formato(x: float | None) -> str:
    if x is None:
        return "—"
    if x == 0:
        return "0"
    return f"{x:.7g}" if 1e-4 <= abs(x) < 1e9 else f"{x:.6e}"


def _pestana_conversor() -> None:
    categoria = st.radio("Magnitud", ("Energía", "Longitud", "Masa", "Ángulo"), horizontal=True, key="fm_cat")
    c1, c2 = st.columns([2, 2], vertical_alignment="bottom")
    texto = c1.text_input("Valor", value="1", key="fm_valor", help="Acepta 1.5e-3, 1,5 x 10^-3, etc.")
    valor, error = _leer(texto)
    if error:
        st.warning(error, icon=":material/help:")
        return
    if categoria == "Energía":
        unidad = c2.selectbox("Unidad de origen", _conversion.UNIDADES_ENERGIA, index=1, key="fm_ue")
        try:
            equivalencias = _conversion.equivalencias_energia(valor, unidad)
        except ValueError as exc:
            st.warning(str(exc), icon=":material/help:")
            return
        st.dataframe([{"Unidad": u, "Valor": _formato(v)} for u, v in equivalencias.items()], hide_index=True, width="stretch")
        lam = equivalencias[_conversion.NM]
        if lam:
            st.markdown(f"Región del espectro electromagnético: **{_conversion.region_espectral(lam * 1e-9)}** "
                        "(límites convencionales).")
        st.caption("La longitud de onda es inversamente proporcional a la energía ($E=hc/\\lambda$); las demás unidades son proporcionales. "
                   "1 kcal = 4184 J (termoquímica).")
        return
    tablas = {"Longitud": (_conversion.UNIDADES_LONGITUD, _conversion.convertir_longitud),
              "Masa": (_conversion.UNIDADES_MASA, _conversion.convertir_masa),
              "Ángulo": (_conversion.UNIDADES_ANGULO, _conversion.convertir_angulo)}
    unidades, funcion = tablas[categoria]
    de = c2.selectbox("Unidad de origen", unidades, key=f"fm_u_{categoria}")
    st.dataframe([{"Unidad": u, "Valor": _formato(funcion(valor, de, u))} for u in unidades], hide_index=True, width="stretch")


def _ir_a_ejercicios(tema_id: str) -> None:
    st.session_state.update(ql_pagina="ejercicios", ej_fuente=ejercicios.TODAS, ej_tema=TEMAS[tema_id], ej_buscar="")


def _mostrar_formulas(s, bloques=None) -> None:
    for b in (bloques or s.bloques):
        st.markdown(f"##### {b.titulo}")
        for f in b.formulas:
            with st.container(border=True):
                st.markdown(f"**{f.nombre}**")
                st.latex(f.latex)
                if f.nota:
                    st.caption(f.nota)


def _enlaces(s) -> None:
    c1, c2, _ = st.columns([2, 2, 2])
    hallado = teoria.buscar(s.teoria) if s.teoria else None
    if hallado and hallado[1].estado == teoria.DISPONIBLE:
        c1.button(f"Teoría: {hallado[1].titulo}", key=f"fm_teoria_{s.id}", icon=":material/menu_book:", on_click=qc.ir_a_tema, args=(s.teoria,), width="stretch")
    if s.id in TEMAS and any(e.tema == s.id for e in ejercicios.EJERCICIOS):
        n = sum(e.tema == s.id for e in ejercicios.EJERCICIOS)
        c2.button(f"Ejercicios de este tema ({n})", key=f"fm_ej_{s.id}", icon=":material/calculate:", on_click=_ir_a_ejercicios, args=(s.id,), width="stretch")


def _pestana_formulas() -> None:
    c1, c2 = st.columns([2, 2], vertical_alignment="bottom")
    c1.selectbox("Tema", (TODOS, *(s.id for s in SECCIONES)), key="fm_tema", format_func=lambda i: TODOS if i == TODOS else _POR_ID[i].titulo)
    c2.text_input("Buscar en todas las fórmulas", key="fm_buscar", placeholder="Por ejemplo: energía, Rydberg, Hermite, conmutador…")
    consulta = st.session_state.get("fm_buscar", "")
    if consulta.strip():
        hallazgos = buscar_formulas(consulta)
        st.caption(f"{len(hallazgos)} fórmulas contienen «{consulta.strip()}».")
        actual = None
        for s, b, f in hallazgos:
            if s.id != actual:
                st.markdown(f"#### {s.titulo}")
                actual = s.id
            with st.container(border=True):
                st.markdown(f"**{f.nombre}**  ·  _{b.titulo}_")
                st.latex(f.latex)
                if f.nota:
                    st.caption(f.nota)
        return
    tema = st.session_state.get("fm_tema", TODOS)
    secciones = SECCIONES if tema == TODOS else (_POR_ID[tema],)
    for s in secciones:
        st.markdown(f"#### {s.titulo}")
        st.markdown(s.resumen)
        _mostrar_formulas(s)
        _enlaces(s)
    qc.boton_descarga("Descargar el formulario completo (Markdown)", como_markdown().encode("utf-8"), "formulario_quantum_lab.md", "text/markdown")


def _pestana_masas() -> None:
    st.markdown("Masas isotópicas de los núclidos que aparecen en los ejercicios (evaluación AME2020), en unidades de masa atómica unificada (u), "
                "y abundancias naturales (IUPAC). La masa de un átomo incluye a sus electrones.")
    st.dataframe([{"Núclido": k, "Masa (u)": f"{v[0]:.8f}", "Abundancia natural (%)": v[1]} for k, v in _masas.ISOTOPOS.items()],
                 hide_index=True, width="stretch")
    qc.seccion("Masa reducida de una molécula diatómica")
    nombres = list(_masas.ISOTOPOS)
    c1, c2 = st.columns(2)
    a = c1.selectbox("Átomo 1", nombres, index=nombres.index("¹H"), key="fm_m1")
    b = c2.selectbox("Átomo 2", nombres, index=nombres.index("³⁵Cl"), key="fm_m2")
    mu = _masas.masa_reducida(_masas.ISOTOPOS[a][0], _masas.ISOTOPOS[b][0])
    st.markdown(f"$\\mu=\\dfrac{{m_1m_2}}{{m_1+m_2}}={mu:.8f}\\ \\mathrm{{u}}={_constantes.latex_cientifico(_masas.en_kg(mu), 8)}\\ \\mathrm{{kg}}$")
    st.caption("Se usa en el oscilador armónico ($\\omega=\\sqrt{k/\\mu}$) y en el rotor rígido ($I=\\mu R^2$).")


def interfaz() -> None:
    """Página «Formulario»."""
    qc.encabezado_pagina("Consulta", "Formulario de constantes y fórmulas",
                         "Constantes fundamentales con su incertidumbre, conversor de unidades, fórmulas de cada tema con la definición de sus símbolos "
                         "y condiciones de validez, y masas isotópicas.")
    qc.escribir_en_url(None)
    t1, t2, t3, t4 = st.tabs(["Constantes", "Conversor", "Fórmulas", "Masas atómicas"])
    with t1:
        _pestana_constantes()
    with t2:
        _pestana_conversor()
    with t3:
        _pestana_formulas()
    with t4:
        _pestana_masas()


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def _llaves_balanceadas(latex: str) -> bool:
    limpio = latex.replace(r"\{", "").replace(r"\}", "")
    return limpio.count("{") == limpio.count("}") and latex.count(r"\left") == latex.count(r"\right")


def ejecutar_pruebas() -> "qc.RegistroPruebas":
    from scipy import constants as sc

    reg = qc.RegistroPruebas("Formulario")
    exactas = {"c": (_constantes.CONSTANTES[0], 299792458.0), "h": (_constantes.CONSTANTES[1], 6.62607015e-34),
               "e": (_constantes.CONSTANTES[3], 1.602176634e-19), "k_B": (_constantes.CONSTANTES[6], 1.380649e-23),
               "N_A": (_constantes.CONSTANTES[7], 6.02214076e23)}
    for nombre, (c, valor) in exactas.items():
        reg.comprobar(f"Constante exacta del SI: {nombre}", c.valor == valor and c.exacta)
    reg.comprobar("ħ = h / 2π", math.isclose(sc.hbar, sc.h / (2 * math.pi), rel_tol=1e-15))
    reg.comprobar("Todas las constantes se resuelven en scipy", all(c.valor > 0 for c in _constantes.CONSTANTES))
    reg.comprobar("1 eV = 8065.544 cm⁻¹", math.isclose(_conversion.equivalencias_energia(1, "eV")["cm⁻¹ (número de onda)"], 8065.543937, rel_tol=1e-8))
    reg.comprobar("1 eV ↔ 1239.842 nm", math.isclose(_conversion.equivalencias_energia(1, "eV")[_conversion.NM], 1239.841984, rel_tol=1e-8))
    reg.comprobar("1 hartree = 27.2114 eV", math.isclose(_conversion.equivalencias_energia(1, "hartree (Eh)")["eV"], 27.211386, rel_tol=1e-7))
    reg.comprobar("Ida y vuelta de conversión", math.isclose(_conversion.desde_julios(_conversion.a_julios(2.5, "kJ/mol"), "kJ/mol"), 2.5, rel_tol=1e-12))
    reg.comprobar("μ(H³⁵Cl) = 0.97959 u", math.isclose(_masas.masa_reducida(_masas.ISOTOPOS["¹H"][0], _masas.ISOTOPOS["³⁵Cl"][0]), 0.9795925, rel_tol=1e-6))
    ids = [s.id for s in SECCIONES]
    reg.comprobar("Secciones con id único", len(ids) == len(set(ids)), f"{len(ids)} secciones")
    todas = [f for s in SECCIONES for f in s.todas()]
    reg.comprobar("Todas las fórmulas tienen nombre y expresión", all(f.nombre and f.latex for f in todas), f"{len(todas)} fórmulas")
    reg.comprobar("Llaves y \\left/\\right balanceadas en LaTeX", all(_llaves_balanceadas(f.latex) for f in todas))
    malos = []
    for s in SECCIONES:
        for f in s.todas():
            if f.contraste is None:
                continue
            calculado, referencia = f.contraste()
            bien = math.isclose(abs(calculado), abs(referencia), rel_tol=f.tol, abs_tol=f.tol if referencia == 0 else 0.0)
            if not bien:
                malos.append(f"{s.id}: {f.nombre} ({calculado:.6g} frente a {referencia:.6g})")
    contrastadas = sum(f.contraste is not None for f in todas)
    reg.comprobar(f"Contrastes numéricos de las fórmulas ({contrastadas})", not malos, "; ".join(malos)[:300])
    return reg
