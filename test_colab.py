"""Los cuadernos de Colab se ejecutan (celdas 1–5), sus pruebas pasan y la densidad de la esfera coincide con la web."""
import contextlib
import io
import json
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("ipywidgets")
pytest.importorskip("IPython")

import matplotlib

matplotlib.use("Agg")

import particula_esfera as pe

COLAB = Path(__file__).parent / "colab"
CUADERNOS = ["QUANTUM_LAB_particula_caja_colab.ipynb", "QUANTUM_LAB_oscilador_armonico_colab.ipynb",
             "QUANTUM_LAB_particula_esfera_colab.ipynb"]


def _cargar(nombre):
    nb = json.loads((COLAB / nombre).read_text(encoding="utf-8"))
    ns = {"__name__": "colab"}
    with contextlib.redirect_stdout(io.StringIO()):
        for celda in nb["cells"][1:6]:
            exec(compile("".join(celda["source"]), nombre, "exec"), ns)
    return nb, ns


@pytest.mark.parametrize("nombre", CUADERNOS)
def test_el_cuaderno_ejecuta_y_sus_pruebas_pasan(nombre):
    _, ns = _cargar(nombre)
    with contextlib.redirect_stdout(io.StringIO()):
        correctas, total = ns["ejecutar_pruebas"]()
    assert correctas == total and total > 20


@pytest.mark.parametrize("nombre", CUADERNOS)
def test_el_cuaderno_declara_los_criterios_del_curso(nombre):
    nb = json.loads((COLAB / nombre).read_text(encoding="utf-8"))
    assert "Criterio" in "".join(nb["cells"][0]["source"])


@pytest.mark.parametrize("l,m,real", [(0, 0, False), (1, 0, False), (2, 1, False), (3, -2, False), (1, 1, True), (2, -2, True), (3, 2, True)])
def test_densidad_de_la_esfera_coincide_con_la_web(l, m, real):
    _, ns = _cargar(CUADERNOS[2])
    rng = np.random.default_rng(l * 10 + m)
    for x, y, z in rng.normal(size=(5, 3)):
        _, th, ph = ns["a_esfericas"](x, y, z)
        colab = float(ns["densidad_probabilidad"](l, m, th, ph, real)[0])
        web = pe.densidad_en_punto(l, m, x, y, z, 1.0, real)["densidad_sr"]
        assert colab == pytest.approx(web, rel=1e-9, abs=1e-14)


def test_informe_de_densidad_evalua_el_punto():
    _, ns = _cargar(CUADERNOS[2])
    with contextlib.redirect_stdout(io.StringIO()) as salida:
        r = ns["informe_densidad"](2, 1, False, 1.0, 0.0, 1.0, 1.0, dibujar=False)
    assert r["densidad"] == pytest.approx(15 / (32 * np.pi), rel=1e-12)
    assert "DENSIDAD EN EL PUNTO ELEGIDO" in salida.getvalue()
