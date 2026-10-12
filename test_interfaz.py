"""
Pruebas de interfaz con el marco de pruebas de Streamlit (AppTest): cada página se ejecuta sin abrir un navegador
y no debe lanzar ninguna excepción. También se comprueba la «lista rápida» de la superposición en la caja.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parent / "quantum_lab.py")
PAGINAS = ["inicio", "caja", "oscilador", "esfera", "fotoelectrico", "bohr", "incertidumbre", "intro", "verificacion",
           "pruebas"]


def _abrir(pagina: str, **estado) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = pagina
    for clave, valor in estado.items():
        at.session_state[clave] = valor
    at.run()
    return at


@pytest.mark.parametrize("pagina", PAGINAS)
def test_pagina_sin_excepciones(pagina):
    at = _abrir(pagina)
    assert not at.exception, [e.value for e in at.exception]


def test_caja_lista_rapida_valida():
    at = _abrir("caja")
    at.text_area(key="caja_sup_lista").set_value("1:1; 2:0.5; 7:-0.3; 12:0.2:1.57").run()
    assert not at.exception and not at.error


def test_caja_lista_rapida_con_error_se_explica():
    at = _abrir("caja")
    at.text_area(key="caja_sup_lista").set_value("1:1; 2.5:1").run()
    assert not at.exception
    assert any("debe ser entero" in e.value for e in at.error)


def test_esfera_valores_extremos_no_rompen():
    at = _abrir("esfera", esf_l=20, esf_m=-20)
    assert not at.exception, [e.value for e in at.exception]
