"""
guia — Guía de usuario de QUANTUM LAB
=====================================

Diagramas de flujo que explican cómo se usan los simuladores y cómo están hechos los códigos (web y cuadernos de Colab):

    Usar un simulador     ruta de un cálculo en la web, de la portada a la exportación
    Cuadernos de Colab    estructura de las seis celdas y qué pasa al cambiar un dato
    Caja · Oscilador · Esfera   un diagrama por simulador, con las funciones que hacen cada paso

Archivos: _flujos.py (contenido de los diagramas) · _render.py (HTML y CSS).
Cómo añadir un diagrama: crear un `Diagrama` en `_flujos.py`, añadirlo a `TODOS` y a una pestaña de `interfaz`.
`ejecutar_pruebas` comprueba que las funciones citadas existan en la web y en los cuadernos.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

import streamlit as st

import quantum_lab_comun as qc
from guia import _flujos, _render

CARPETA_COLAB = Path(__file__).resolve().parent.parent / "colab"


def _abrir(pagina: str) -> None:
    st.session_state["ql_pagina"] = pagina


def _mostrar(d: _flujos.Diagrama) -> None:
    st.markdown(_render.diagrama_html(d), unsafe_allow_html=True)


def _detalles(d: _flujos.Diagrama) -> None:
    """Botón al simulador, funciones de cada paso y el diagrama en Mermaid (plegados)."""
    if d.simulador:
        import quantum_lab_portada as portada      # no importar quantum_lab aquí: se ejecutaría de nuevo como script
        st.button(f"Abrir el simulador: {portada.modulo(d.simulador)[4]}", key=f"guia_abrir_{d.id}",
                  icon=":material/science:", on_click=_abrir, args=(d.simulador,))
    if any(p.web or p.colab for p in d.pasos):
        with st.expander("Para programadores: funciones de cada paso"):
            qc.tabla_libre([{"Paso": f"{i}. {p.titulo}", "Web": ", ".join(p.web) or "—", "Colab": ", ".join(p.colab) or "—"}
                            for i, p in enumerate(d.pasos, start=1)])
            st.caption(f"Web: {d.modulo_web}.py · Colab: {d.cuaderno}")
    with st.expander("Copiar este diagrama (Mermaid)"):
        st.code(_flujos.mermaid(d), language="text")
        st.caption("Pega el texto en mermaid.live o en draw.io (Insertar → Avanzado → Mermaid) para editarlo y cambiarle el diseño.")


def interfaz() -> None:
    """Página «Guía de usuario»."""
    qc.encabezado_pagina("Herramientas de estudio", "Guía de usuario",
                         "Diagramas de flujo de los simuladores y de sus códigos, en la web y en Colab.")
    qc.escribir_en_url(None)
    st.markdown(_render.CSS, unsafe_allow_html=True)
    tabs = st.tabs(["Usar un simulador", "Cuadernos de Colab", "Partícula en una caja", "Oscilador armónico", "Partícula en una esfera"])
    with tabs[0]:
        _mostrar(_flujos.USAR_SIMULADOR)
        _detalles(_flujos.USAR_SIMULADOR)
    with tabs[1]:
        _mostrar(_flujos.CELDAS_COLAB)
        _mostrar(_flujos.CALCULO_COLAB)
        _detalles(_flujos.CALCULO_COLAB)
    for tab, d in zip(tabs[2:], _flujos.SIMULADORES):
        with tab:
            _mostrar(d)
            _detalles(d)


# ---------------------------------------------------------------------
# Pruebas
# ---------------------------------------------------------------------
def _funciones_cuaderno(nombre: str) -> set[str]:
    nb = json.loads((CARPETA_COLAB / nombre).read_text(encoding="utf-8"))
    codigo = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    return set(re.findall(r"^def (\w+)", codigo, re.M))


def ejecutar_pruebas() -> "qc.RegistroPruebas":
    import quantum_lab_portada as portada
    reg = qc.RegistroPruebas("Guía de usuario")
    ids = [d.id for d in _flujos.TODOS]
    reg.comprobar("Identificadores de diagrama únicos", len(ids) == len(set(ids)), ", ".join(ids))
    reg.comprobar("Cada diagrama tiene entre 3 y 7 pasos y hasta 3 notas «Para recordar»",
                  all(3 <= len(d.pasos) <= 7 and len(d.recordar) <= 3 for d in _flujos.TODOS))
    reg.comprobar("Colores de la paleta en todos los pasos", all(p.tono in _flujos.TONOS for d in _flujos.TODOS for p in d.pasos))
    reg.comprobar("Solo los pasos de decisión tienen rama de error y hay una por diagrama de cálculo",
                  all(sum(bool(p.rama) for p in d.pasos) == 1 for d in (_flujos.USAR_SIMULADOR, _flujos.CALCULO_COLAB, *_flujos.SIMULADORES)))
    claves = {m[0] for m in portada.MODULOS}
    reg.comprobar("Los simuladores enlazados existen", all(d.simulador in claves for d in _flujos.SIMULADORES))
    faltan = []
    for d in _flujos.SIMULADORES:
        modulo = importlib.import_module(d.modulo_web)
        en_colab = _funciones_cuaderno(d.cuaderno)
        faltan += [f"{d.modulo_web}.{f}" for p in d.pasos for f in p.web if not callable(getattr(modulo, f, None))]
        faltan += [f"{d.cuaderno}:{f}" for p in d.pasos for f in p.colab if f not in en_colab]
    reg.comprobar("Las funciones citadas en los diagramas existen en la web y en Colab", not faltan, ", ".join(faltan) or "todas")
    reg.comprobar("Cada simulador cita funciones en los pasos de validación, física, gráficas y pruebas",
                  all(all(p.web and p.colab for p in d.pasos[1:]) for d in _flujos.SIMULADORES))
    m = _flujos.mermaid(_flujos.CAJA)
    reg.comprobar("Exportación a Mermaid: un nodo por paso, flechas entre pasos y la rama «No»",
                  m.startswith("flowchart LR") and m.count("-->") == len(_flujos.CAJA.pasos) and "|No|" in m)
    return reg
