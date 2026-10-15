"""Pruebas del repaso personalizado y de la bitácora de intentos."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ejercicios
from ejercicios import _bitacora, _progreso
from repaso import temas_debiles

APP = str(Path(__file__).parent / "quantum_lab.py")
IDS = ejercicios.IDS


class _Cal:
    def __init__(self, fraccion, mensajes=()):
        self.fraccion = fraccion
        self.resultados = []
        self.mensajes = list(mensajes)


def test_bitacora_vacia_y_totales():
    assert _bitacora.errores_frecuentes({}) == []
    assert _bitacora.nuevo()["intentos"] == 0


def test_depurar_descarta_basura():
    bruta = {"no_existe": {"intentos": 3}, IDS[0]: {"intentos": "x"}, IDS[1]: {"intentos": 2, "aciertos": 9, "solucion": -1, "errores": {"m": 2}}}
    limpia = _bitacora.depurar(bruta, IDS)
    assert "no_existe" not in limpia and limpia[IDS[0]]["intentos"] == 0
    assert limpia[IDS[1]]["aciertos"] <= limpia[IDS[1]]["intentos"]
    assert _bitacora.depurar("basura", IDS) == {}


def test_copia_de_seguridad_v2_ida_y_vuelta():
    bit = {IDS[0]: {"intentos": 2, "aciertos": 1, "solucion": 1, "errores": {"Error típico": 1}}}
    ex = [{"fecha": "2026-10-15 10:00", "ejercicios": [IDS[0]], "nota": 3.5, "porcentaje": 70.0, "minutos_usados": 12, "minutos_totales": 30, "temas": ["Oscilador armónico"]}]
    datos = _progreso.a_json({IDS[0]}, IDS, repasar={IDS[1]}, bitacora=bit, examenes=ex)
    leido = _progreso.leer_copia(datos, IDS)
    assert leido["resueltos"] == {IDS[0]} and leido["repasar"] == {IDS[1]}
    assert leido["examenes"][0]["nota"] == pytest.approx(3.5)
    assert leido["bitacora"][IDS[0]]["intentos"] == 2


def test_copia_v1_sigue_valiendo():
    import json
    assert _progreso.leer_copia(json.dumps({"quantum_lab": "ejercicios", "resueltos": [IDS[0]]}), IDS)["resueltos"] == {IDS[0]}


def test_temas_debiles_ordena_y_exige_minimo():
    filas = [{"intentos": 5, "precision": 0.2}, {"intentos": 1, "precision": 0.0}, {"intentos": 4, "precision": 0.9}, {"intentos": 3, "precision": None}]
    r = temas_debiles(filas)
    assert [f["precision"] for f in r] == [0.2, 0.9]


def _abrir(**estado) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "repaso"
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


def test_pagina_vacia_abre_sin_errores():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]


def test_pagina_con_datos_abre_sin_errores():
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "ejercicios"
    at.session_state["ej_sel"] = "s1_fotoelectrico"
    at.run()
    ej = ejercicios.buscar("s1_fotoelectrico")
    for p in ej.partes:
        at.text_input(key=f"ej_{ej.id}_{p.clave}").set_value("123456.789")
    at.button(key=f"ej_{ej.id}_btn").click().run()
    at.session_state["ql_pagina"] = "repaso"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
