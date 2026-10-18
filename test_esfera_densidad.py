"""Criterio del curso: densidad de probabilidad |Y_l^m|² frente a la posición en coordenadas cartesianas (web)."""
from math import pi
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import particula_esfera as pe

APP = str(Path(__file__).parent / "quantum_lab.py")


@pytest.mark.parametrize("l,m,punto,esperado", [
    (0, 0, (1, 2, 3), 1 / (4 * pi)),
    (1, 0, (0, 0, 5), 3 / (4 * pi)),                       # |Y_1^0|² = 3cos²θ/4π
    (1, 0, (1, 1, 0), 0.0),                                # plano nodal z = 0
    (1, 1, (1, 0, 0), 3 / (8 * pi)),                       # |Y_1^1|² = 3sin²θ/8π
    (1, -1, (0, 1, 0), 3 / (8 * pi)),
    (2, 0, (0, 0, 1), 5 / (4 * pi)),                       # |Y_2^0|² = 5(3cos²θ−1)²/16π
    (2, 1, (1, 0, 1), 15 / (8 * pi) * 0.25),               # |Y_2^1|² = 15 sin²θcos²θ/8π, θ = 45°
    (2, 2, (1, 0, 0), 15 / (32 * pi)),                     # |Y_2^2|² = 15 sin⁴θ/32π
])
def test_densidad_en_punto_formas_cerradas(l, m, punto, esperado):
    d = pe.densidad_en_punto(l, m, *punto, radio=2.0)
    assert d["densidad_sr"] == pytest.approx(esperado, abs=1e-12)
    assert d["densidad_area"] == pytest.approx(esperado / 4.0, abs=1e-12)
    assert np.linalg.norm(d["punto_esfera"]) == pytest.approx(2.0)


@pytest.mark.parametrize("m,punto,esperado", [(1, (1, 0, 0), 3 / (4 * pi)), (1, (0, 1, 0), 0.0), (-1, (0, 1, 0), 3 / (4 * pi)),
                                              (-1, (1, 0, 0), 0.0), (0, (0, 0, 1), 3 / (4 * pi))])
def test_combinaciones_reales_p(m, punto, esperado):
    """pₓ ∝ x/r, p_y ∝ y/r, p_z ∝ z/r con |p|² = 3/(4π)·(coordenada/r)²."""
    assert pe.densidad_en_punto(1, m, *punto, radio=1.0, real=True)["densidad_sr"] == pytest.approx(esperado, abs=1e-12)


def test_d_xy_en_cartesianas():
    x, y, z = 0.3, -0.7, 0.4
    r = np.sqrt(x * x + y * y + z * z)
    esperado = 15 / (4 * pi) * (x * y / r ** 2) ** 2          # d_xy = √(15/4π)·xy/r²
    assert pe.densidad_en_punto(2, -2, x, y, z, 1.0, real=True)["densidad_sr"] == pytest.approx(esperado, rel=1e-10)


def test_el_origen_y_valores_no_finitos_se_rechazan():
    with pytest.raises(ValueError):
        pe.densidad_en_punto(1, 0, 0, 0, 0, 1.0)
    with pytest.raises(ValueError):
        pe.densidad_en_punto(1, 0, float("nan"), 0, 1, 1.0)
    with pytest.raises(ValueError):
        pe.densidad_en_punto(1, 0, 0, 0, 1, 0.0)


@pytest.mark.parametrize("l,m,real", [(0, 0, False), (1, 0, False), (2, 1, False), (3, -2, False), (2, 2, True), (3, -1, True)])
def test_la_densidad_esta_normalizada(l, m, real):
    T, P = pe.malla_angular(301)
    integral = pe.integral_angular_malla(pe.densidad_probabilidad(l, m, T, P, real), T[:, 0], P[0])
    assert integral == pytest.approx(1.0, abs=2e-4)


def test_cortes_polares_distancia_igual_a_densidad():
    for plano in pe.PLANOS:
        h, v, dens, _ = pe.curva_densidad_plano(2, 1, plano)
        assert np.allclose(np.hypot(h, v), dens, atol=1e-14)
    h, v, dens, _ = pe.curva_densidad_plano(1, 0, "xz")
    assert v.max() == pytest.approx(3 / (4 * pi)) and v.min() == pytest.approx(-3 / (4 * pi))
    _, _, dens_xy, _ = pe.curva_densidad_plano(1, 0, "xy")
    assert np.allclose(dens_xy, 0, atol=1e-14)                 # p_z se anula en el plano xy


def test_complejo_no_depende_de_phi_y_real_si():
    _, a = pe.densidad_frente_a_z(2, 1, phi=0.0)
    _, b = pe.densidad_frente_a_z(2, 1, phi=1.0)
    assert np.allclose(a, b)
    _, c = pe.densidad_frente_a_z(2, 1, real=True, phi=0.0)
    _, d = pe.densidad_frente_a_z(2, 1, real=True, phi=np.pi / 2)
    assert not np.allclose(c, d)


def test_figuras_se_generan():
    import matplotlib.pyplot as plt
    fig = pe.figura_densidad_cartesiana(2, 1, False)
    assert len(fig.axes) == 4 and "cartesianas" in fig._suptitle.get_text()
    plt.close(fig)
    f3 = pe.figura_densidad_3d(2, 1, True, 1e-9, "SI", n_theta=40)
    assert len(f3.data) == 2


def test_pestana_densidad_en_la_web():
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "esfera"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.tabs[0].label == "Densidad de probabilidad"
    valor = [mm.value for mm in at.metric if mm.label == "|Y|²"][0]
    assert float(valor.split()[0]) == pytest.approx(15 / (8 * pi) * 0.25, rel=1e-5)     # l = 2, m = 1 a 45°
    at.number_input(key="esf_px").set_value(0.0).run()
    at.number_input(key="esf_pz").set_value(0.0).run()
    assert not at.exception and any("origen" in e.value for e in at.error)
    at.number_input(key="esf_pz").set_value(1.0).run()
    at.toggle(key="esf_dens_real").set_value(True).run()
    assert not at.exception, [e.value for e in at.exception]
