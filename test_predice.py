"""
Pruebas del modo «Predice, experimenta y explica» y de la ecuación con valores de la caja.

Los valores esperados NO salen de las funciones evaluadas: se derivan de las leyes de escala de la caja
(Eₙ ∝ n², Eₙ ∝ 1/a², Eₙ ∝ 1/m, λ = 2a/n) y de E₁ = 0.376030 eV para un electrón en 1 nm (referencia tabulada).
"""
import re
from dataclasses import replace
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import particula_caja as caja
import predice

APP = str(Path(__file__).parent / "quantum_lab.py")
ESPERADO = {"duplicar_a": 0.25, "duplicar_n": 4.0, "duplicar_masa": 0.5, "lambda_duplicar_a": 2.0}


def _p(n=1, a=1.0, m=1.0, sistema="SI"):
    return caja.validar_parametros_caja(n, a, m, sistema, 4000)


@pytest.mark.parametrize("n,a,m,sistema", [(1, 1.0, 1.0, "SI"), (3, 0.5, 1836.15, "SI"), (7, 2.5, 0.067, "Atómicas")])
def test_cociente_calculado_sigue_la_ley_de_escala(n, a, m, sistema):
    p = _p(n, a, m, sistema)
    for q in caja.PREGUNTAS_PREDICE:
        ref, mod, _ = q.calcular(p)
        assert mod / ref == pytest.approx(ESPERADO[q.id], rel=1e-12)
        assert predice.validar_pregunta(q, p) == []


def test_la_respuesta_correcta_sale_del_calculo_y_no_de_una_posicion():
    p = _p(2)
    for q in caja.PREGUNTAS_PREDICE:
        res = predice.evaluar(q, p, None)
        assert q.opciones[res.correcta].razon == pytest.approx(ESPERADO[q.id])


def test_prediccion_correcta_incorrecta_y_ausente():
    q = caja.PREGUNTAS_PREDICE[0]            # duplicar a → cociente 1/4
    p = _p()
    ok = predice.evaluar(q, p, 2)
    mal = predice.evaluar(q, p, 0)
    sin = predice.evaluar(q, p, None)
    assert ok.acierto is True and mal.acierto is False and sin.acierto is None
    assert "2" in mal.mensaje and "0.25" in mal.mensaje          # explica qué afirmaba y qué da el cálculo
    assert sin.elegida is None and sin.modificado > 0             # el experimento corre sin predicción


def test_prediccion_fuera_de_rango_se_rechaza():
    with pytest.raises(ValueError):
        predice.evaluar(caja.PREGUNTAS_PREDICE[0], _p(), 9)


def test_pregunta_mal_construida_se_detecta():
    q = caja.PREGUNTAS_PREDICE[0]
    sin_correcta = replace(q, opciones=(predice.Opcion("a", 2.0), predice.Opcion("b", 3.0)))
    repetida = replace(q, opciones=(predice.Opcion("a", 2.0), predice.Opcion("b", 2.0)))
    negativa = replace(q, opciones=(predice.Opcion("a", -1.0), predice.Opcion("b", 2.0)))
    assert any("coincide" in m for m in predice.validar_pregunta(sin_correcta, _p()))
    assert any("mismo cociente" in m for m in predice.validar_pregunta(repetida, _p()))
    assert any("positiva" in m for m in predice.validar_pregunta(negativa, _p()))
    with pytest.raises(ValueError):
        predice.evaluar(sin_correcta, _p(), 0)


def test_los_parametros_no_se_modifican():
    p = _p(3, 1.7, 2.0)
    antes = replace(p)
    for q in caja.PREGUNTAS_PREDICE:
        predice.evaluar(q, p, 0)
    assert p == antes


def test_ecuacion_con_valores_coincide_con_la_energia_de_referencia():
    # Electrón en 1 nm: E_n = n²·0.376030 eV (valor tabulado, independiente de energia_nivel)
    for n in (1, 3, 10):
        p = _p(n)
        tex = caja.ecuacion_energia_latex(p, caja.energia_nivel(n, p.longitud, p.masa))
        valor = float(re.search(r"=([0-9.]+)\\ \\mathrm\{eV\}$", tex).group(1))
        assert valor == pytest.approx(n ** 2 * 0.376030, rel=1e-4)
        assert f"E_{{{n}}}" in tex


def test_numero_latex():
    assert caja._numero_latex(1.0, 4) == "1"
    assert caja._numero_latex(1836.15, 4) == "1836"
    assert caja._numero_latex(1.5e5, 4) == r"1.5\times10^{5}"
    assert caja._numero_latex(3e-5, 4) == r"3\times10^{-5}"
    assert caja._numero_latex(0.37603, 5) == "0.37603"


# ----------------------------- interfaz -----------------------------
def _abrir_predice():
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "caja"
    at.run()
    return at


def test_flujo_completo_en_la_interfaz():
    at = _abrir_predice()
    assert not at.exception
    assert "Predice y experimenta" in [t.label for t in at.tabs]
    base = (at.session_state["caja_longitud"], at.session_state["caja_masa"], at.session_state["caja_n"])
    # 1. Sin ejecutar no hay resultado
    assert not [m for m in at.markdown if "Resultado del experimento" in m.value]
    # 2. Predicción correcta (cuarta parte) y ejecución
    at.radio(key="caja_pd_duplicar_a_radio").set_value("Se reduce a la cuarta parte").run()
    at.button(key="caja_pd_duplicar_a_b_run").click().run()
    assert not at.exception and not at.error
    assert any("coincide con el cálculo" in s.value for s in at.success)
    # 3. Pistas progresivas
    at.button(key="caja_pd_duplicar_a_b_pista").click().run()
    assert len([i for i in at.info if i.value.startswith("Pista 1 de 3")]) == 1
    # 4. Predicción equivocada y cambio de parámetro: el resultado se recalcula
    at.radio(key="caja_pd_duplicar_a_radio").set_value("Se duplica").run()
    assert at.error and "afirmaba un cociente de 2" in at.error[0].value
    at.number_input(key="caja_longitud").set_value(3.0).run()
    assert not at.exception
    # 5. Los parámetros físicos solo cambian por el usuario, no por el modo de predicción
    assert (at.session_state["caja_masa"], at.session_state["caja_n"]) == base[1:]


def test_ejecutar_sin_prediccion_es_posible():
    at = _abrir_predice()
    at.selectbox(key="caja_pd_sel").set_value("duplicar_n").run()
    at.button(key="caja_pd_duplicar_n_b_run").click().run()
    assert not at.exception
    assert any("sin registrar una predicción" in i.value for i in at.info)


def test_cambiar_de_pregunta_conserva_el_estado_de_cada_una():
    at = _abrir_predice()
    at.selectbox(key="caja_pd_sel").set_value("duplicar_masa").run()
    at.button(key="caja_pd_duplicar_masa_b_run").click().run()
    assert not at.exception
    at.selectbox(key="caja_pd_sel").set_value("duplicar_a").run()
    assert not at.exception
    assert not any("sin registrar" in i.value for i in at.info)       # duplicar_a aún no se ejecutó
