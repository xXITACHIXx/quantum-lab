"""
Pruebas de interfaz con el marco de pruebas de Streamlit (AppTest): cada página se ejecuta sin abrir un navegador
y no debe lanzar ninguna excepción. También se comprueba la «lista rápida» de la superposición en la caja.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parent / "quantum_lab.py")
PAGINAS = ["inicio", "caja", "oscilador", "esfera", "fotoelectrico", "bohr", "incertidumbre", "teoria", "talleres", "ejercicios", "ruta", "formulario", "examen", "repaso", "verificacion",
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


TEMAS_DISPONIBLES = ["cuerpo_negro", "fotoelectrico", "de_broglie", "bohr", "criterios", "ondas", "schrodinger", "operadores",
                     "postulados", "libre_pared", "caja", "oscilador", "esfera", "conmutadores", "incertidumbre"]


@pytest.mark.parametrize("tema", TEMAS_DISPONIBLES)
def test_tema_de_teoria_se_muestra(tema):
    at = _abrir("teoria", ql_tema=tema)
    assert not at.exception, [e.value for e in at.exception]


def test_enlace_de_simulador_lleva_a_su_teoria():
    at = _abrir("bohr")
    at.button(key="ql_teoria_bohr").click().run()
    assert not at.exception
    assert at.session_state["ql_pagina"] == "teoria" and at.session_state["ql_tema"] == "bohr"


def test_enlace_antiguo_a_la_introduccion():
    at = AppTest.from_file(APP, default_timeout=180)
    at.query_params["sim"] = "intro"
    at.run()
    assert not at.exception
    assert at.session_state["ql_pagina"] == "teoria" and at.session_state["ql_tema"] == "schrodinger"


@pytest.mark.parametrize("tema", ["hidrogeno", "espin", "aproximados", "born_oppenheimer", "orbitales_moleculares", "espectroscopia"])
def test_tema_en_preparacion_se_explica(tema):
    at = _abrir("teoria", ql_tema=tema)
    assert not at.exception, [e.value for e in at.exception]
    assert any("en preparación" in w.value for w in at.warning)
