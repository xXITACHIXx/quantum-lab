"""Pruebas del formulario: constantes exactas, conversiones, contrastes numéricos de cada fórmula y la interfaz."""
import math
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import formulario
from formulario import _conversion, _masas

APP = str(Path(__file__).parent / "quantum_lab.py")
FORMULAS = [(s, f) for s in formulario.SECCIONES for f in s.todas()]


def _abrir() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "formulario"
    at.run()
    return at


def test_pruebas_internas():
    reg = formulario.ejecutar_pruebas()
    assert all(r["ok"] for r in reg.resultados), [r for r in reg.resultados if not r["ok"]]


@pytest.mark.parametrize("seccion,formula", [x for x in FORMULAS if x[1].contraste], ids=lambda x: getattr(x, "nombre", getattr(x, "id", "")))
def test_contraste_numerico(seccion, formula):
    calculado, referencia = formula.contraste()
    assert math.isclose(abs(calculado), abs(referencia), rel_tol=formula.tol, abs_tol=formula.tol if referencia == 0 else 0.0)


def test_conversiones_basicas():
    e = _conversion.equivalencias_energia(1, "eV")
    assert e["cm⁻¹ (número de onda)"] == pytest.approx(8065.5439, rel=1e-7)
    assert e[_conversion.NM] == pytest.approx(1239.84198, rel=1e-7)
    assert _conversion.equivalencias_energia(1, "hartree (Eh)")["eV"] == pytest.approx(27.211386, rel=1e-7)


def test_masa_reducida_simetrica():
    a, b = _masas.ISOTOPOS["¹H"][0], _masas.ISOTOPOS["³⁵Cl"][0]
    assert _masas.masa_reducida(a, b) == pytest.approx(_masas.masa_reducida(b, a))


def test_busqueda_y_markdown():
    assert formulario.buscar_formulas("Rydberg")
    assert formulario.buscar_formulas("") == []
    md = formulario.como_markdown()
    assert md.startswith("# Formulario") and md.count("$$") >= 2 * len(FORMULAS)


def test_pagina_abre_sin_errores():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.tabs) == 4


def test_busqueda_en_la_pagina():
    at = _abrir()
    at.text_input(key="fm_buscar").set_value("Hermite").run()
    assert not at.exception, [e.value for e in at.exception]


def test_conversor_valor_invalido_no_falla():
    at = _abrir()
    at.text_input(key="fm_valor").set_value("abc").run()
    assert not at.exception, [e.value for e in at.exception]
