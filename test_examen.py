"""Pruebas del modo examen: reglas puras y recorrido completo (configurar, resolver, entregar, corregir)."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ejercicios
from examen import _logica

APP = str(Path(__file__).parent / "quantum_lab.py")
EJ = {e.id: e for e in ejercicios.EJERCICIOS}


def test_seleccion_reproducible_y_acotada():
    ids = sorted(EJ)
    assert _logica.seleccionar(ids, 5, "a") == _logica.seleccionar(list(reversed(ids)), 5, "a")
    assert _logica.seleccionar(ids, 5, "a") != _logica.seleccionar(ids, 5, "b")
    assert len(_logica.seleccionar(ids[:3], 10, "x")) == 3
    assert _logica.seleccionar([], 5, "x") == []


def test_nota_y_tiempo():
    assert _logica.nota([1, 1, 1]) == (5.0, 100.0)
    assert _logica.nota([1, 0]) == (2.5, 50.0)
    assert _logica.nota([]) == (0.0, 0.0)
    assert _logica.restante(0, 600, 700) == 0.0
    assert _logica.formato_tiempo(65) == "01:05"
    assert _logica.formato_tiempo(3725) == "1:02:05"
    assert _logica.duracion_sugerida(1) == 10 and _logica.duracion_sugerida(100) == 240


def _abrir(**estado) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "examen"
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


def test_configuracion_abre_sin_errores():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]
    assert at.button(key="ex_comenzar")


def test_examen_completo_con_todo_correcto():
    at = _abrir(ex_semilla="prueba", ex_n=3)
    at.button(key="ex_comenzar").click().run()
    assert at.session_state["ex_fase"] == "curso" and len(at.session_state["ex_ids"]) == 3
    for ej_id in at.session_state["ex_ids"]:
        for p in EJ[ej_id].partes:
            clave = f"exm_{ej_id}_{p.clave}"
            if p.tipo == ejercicios.NUM:
                at.text_input(key=clave).set_value(f"{p.esperado:.6g}")
            else:
                at.radio(key=clave).set_value(p.opciones[int(p.esperado)])
    at.button(key="ex_entregar").click().run()
    at.button(key="ex_confirmar_si").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["ex_fase"] == "fin"
    assert at.session_state["ex_entrega"]["nota"] == pytest.approx(5.0)


def test_examen_en_blanco_obtiene_cero_y_alimenta_el_repaso():
    at = _abrir(ex_semilla="blanco", ex_n=3)
    at.button(key="ex_comenzar").click().run()
    at.button(key="ex_entregar").click().run()
    at.button(key="ex_confirmar_si").click().run()
    assert at.session_state["ex_entrega"]["nota"] == 0.0
    at.button(key="ex_nuevo").click().run()
    assert at.session_state["ex_fase"] == "config"


def test_tiempo_agotado_entrega_automaticamente(monkeypatch):
    import examen
    reloj = [1000.0]
    monkeypatch.setattr(examen, "RELOJ", lambda: reloj[0])
    at = _abrir(ex_semilla="t", ex_n=3)
    at.button(key="ex_comenzar").click().run()
    reloj[0] += 10 ** 6
    at.run()
    assert at.session_state["ex_fase"] == "fin"
    assert at.session_state["ex_entrega"]["motivo"] != "entrega"
