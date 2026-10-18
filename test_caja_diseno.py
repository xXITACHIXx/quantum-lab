"""Figura de la caja sin textos encimados y superposición con valores escritos por el usuario."""
import matplotlib
matplotlib.use("Agg")
import pytest
from streamlit.testing.v1 import AppTest

import particula_caja as pc


@pytest.mark.parametrize("longitud", [0.5, 2, 20, 500])
def test_figura_individual_sin_textos_encimados(longitud):
    p = pc.validar_parametros_caja(3, longitud, 1.0, "SI", 1000)
    fig = pc.figura_estado_individual(pc.calcular_estado_individual(p), p)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    ejes = fig.axes
    for ax in ejes:                                    # el título de cada panel no toca el eje x del panel de arriba
        t = ax.title.get_window_extent(r)
        for otro in ejes:
            if otro is not ax and otro.get_position().y0 > ax.get_position().y0:
                assert not t.overlaps(otro.xaxis.label.get_window_extent(r))
    assert fig._suptitle is None                           # sin título general: solo los títulos cortos de cada panel


def test_superposicion_acepta_cantidad_estados_y_coeficientes_escritos():
    at = AppTest.from_file("quantum_lab.py", default_timeout=120)
    at.session_state["ql_pagina"] = "caja"
    at.run()
    at.number_input(key="caja_sup_cantidad").set_value(3).run()
    for i, (n, a, f) in enumerate([(2, 0.6, 0.0), (5, 1.7, 1.2), (9, 0.25, -0.5)], 1):
        at.number_input(key=f"caja_sup_n{i}").set_value(n)
        at.number_input(key=f"caja_sup_A{i}").set_value(a)
        at.number_input(key=f"caja_sup_fase{i}").set_value(f)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["caja_sup_cantidad"] == 3 and at.session_state["caja_sup_A2"] == 1.7   # amplitud mayor que 1 permitida
