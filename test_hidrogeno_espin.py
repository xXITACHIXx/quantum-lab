"""
Simuladores 07 (hidrógeno, función radial) y 08 (espín de dos electrones): interfaz, enlaces con la teoría y contraste con los
cuadernos de Colab (que son una implementación independiente de la misma física).
"""
import contextlib
import io
import json
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import espin_electrones as ee
import hidrogeno_radial as hr
import quantum_lab_portada as portada
import teoria

APP = str(Path(__file__).parent / "quantum_lab.py")
COLAB = Path(__file__).parent / "colab"
NB_H = "QUANTUM_LAB_hidrogeno_radial_colab.ipynb"
NB_E = "QUANTUM_LAB_espin_dos_electrones_colab.ipynb"


def _abrir(pagina, **estado):
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = pagina
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


def _cargar(nombre, celdas):
    nb = json.loads((COLAB / nombre).read_text(encoding="utf-8"))
    ns = {"__name__": "colab"}
    import matplotlib
    matplotlib.use("Agg")
    with contextlib.redirect_stdout(io.StringIO()):
        for i in celdas:
            exec(compile("".join(nb["cells"][i]["source"]), nombre, "exec"), ns)
    return nb, ns


# ---------------------------------------------------------------- interfaz
@pytest.mark.parametrize("pagina", ["radial", "espin"])
def test_pagina_sin_excepciones(pagina):
    at = _abrir(pagina)
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("n,l", [(1, 0), (2, 1), (5, 4), (20, 2)])
def test_radial_varios_estados(n, l):
    at = _abrir("radial", rad_n=n, rad_l=l)
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error


def test_radial_l_se_ajusta_si_se_baja_n():
    at = _abrir("radial", rad_n=4, rad_l=3)
    at.number_input(key="rad_n").set_value(2).run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["rad_l"] == 1


@pytest.mark.parametrize("psi", [
    "(|1s,α;2s,β⟩ - |1s,β;2s,α⟩)/√2", "|1sα;2sβ⟩", "Slater(1sα, 2sβ)", "|1sα;2sα⟩ + |1sβ;2sβ⟩", "c|1sα;2sβ⟩ + d|1sβ;2sα⟩"])
def test_espin_entradas_validas(psi):
    at = _abrir("espin", esp_psi=psi)
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error


@pytest.mark.parametrize("psi", ["", "|1sα;1pβ⟩", "1sα;2sβ", "|1sα;2sβ⟩*|1sα;2sα⟩", "|1sγ;2sβ⟩"])
def test_espin_entradas_invalidas_se_explican(psi):
    at = _abrir("espin", esp_psi=psi)
    assert not at.exception, [e.value for e in at.exception]
    assert at.error


def test_portada_tiene_el_capitulo_nuevo():
    assert "Estructura atómica" in portada.CATEGORIAS
    assert [m[0] for m in portada.MODULOS if m[2] == "Estructura atómica"] == ["radial", "espin"]
    assert portada.CAT_CLAVE["Teoría y repaso"] == "cat3" and portada.CAT_CLAVE["Estructura atómica"] == "cat6"
    numeros = [m[1] for m in portada.MODULOS]
    assert numeros == [f"{i:02d}" for i in range(1, len(portada.MODULOS) + 1)]
    at = _abrir("cat6")
    assert not at.exception, [e.value for e in at.exception]


def test_teoria_hidrogeno_y_espin_disponibles_con_simulador():
    for tema, sim, prefijo in (("hidrogeno", "radial", "rad"), ("espin", "espin", "esp")):
        u, t = teoria.buscar(tema)
        assert t.estado == teoria.DISPONIBLE and t.simulador == sim and t.prefijo == prefijo
        at = _abrir("teoria", ql_tema=tema)
        assert not at.exception, [e.value for e in at.exception]
        assert len(at.tabs) >= 3 and not at.warning


def test_enlace_de_los_simuladores_con_su_teoria():
    for pagina, tema in (("radial", "hidrogeno"), ("espin", "espin")):
        at = _abrir(pagina)
        at.button(key=f"ql_teoria_{tema}").click().run()
        assert not at.exception
        assert at.session_state["ql_pagina"] == "teoria" and at.session_state["ql_tema"] == tema


# ---------------------------------------------------------------- contraste con Colab
def test_colab_hidrogeno_ejecuta_y_coincide_con_la_web():
    _, ns = _cargar(NB_H, (1, 2, 3, 4, 5))
    with contextlib.redirect_stdout(io.StringIO()):
        assert ns["ejecutar_pruebas"]()
    r = np.linspace(0, 60, 400)
    for n, l in ((1, 0), (2, 1), (3, 2), (6, 3), (9, 0)):
        assert np.allclose(ns["funcion_radial"](n, l, r), hr.funcion_radial(n, l, r), rtol=1e-12, atol=0)
        assert ns["distancia_esperada"](n, l) == hr.distancia_esperada(n, l)
        assert ns["radio_mas_probable"](n, l) == pytest.approx(hr.radio_mas_probable(n, l), rel=1e-9)
        assert np.allclose(ns["nodos_radiales"](n, l), hr.nodos_radiales(n, l))
        assert ns["energia_estado"](n) == hr.energia_estado(n)


@pytest.mark.parametrize("psi", ["(|1s,α;2s,β> - |1s,β;2s,α>)/√2", "|1sα;2sβ>", "Slater(1sα, 2sβ)", "|1sα;2sα> + |1sβ;2sβ>",
                                 "Slater(1sα, 1sβ)", "(|2p0,α;3d+1,β> + |2p0,β;3d+1,α>)/2^(1/2)"])
def test_colab_espin_ejecuta_y_coincide_con_la_web(psi):
    _, ns = _cargar(NB_E, (1, 2, 3, 4))
    c, w = ns["analizar"](psi), ee.analizar(psi)
    assert c["s2"] == w["s2"] and c["sz"] == w["sz"] and c["simetria"] == w["simetria"] and c["p_s2"] == w["p_s2"]
    assert c["psi"] == w["psi"] and c["s2_psi"] == w["s2_psi"]


def test_colab_espin_pruebas_pasan():
    _, ns = _cargar(NB_E, (1, 2, 3, 4, 5))
    with contextlib.redirect_stdout(io.StringIO()):
        assert ns["ejecutar_pruebas"]()
