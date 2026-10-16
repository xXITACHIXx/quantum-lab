"""Pruebas del sistema visual: paleta única, contraste suficiente y coherencia con .streamlit/config.toml."""
import tomllib
from pathlib import Path

import pytest

import quantum_lab_comun as qc
import quantum_lab_tema as t

CONFIG = tomllib.loads((Path(__file__).parent / ".streamlit" / "config.toml").read_text(encoding="utf-8"))


def test_paleta_pedida():
    assert t.PALETA == {"fondo": "#0B1020", "panel": "#151F35", "cian": "#42D9FF", "violeta": "#A78BFA", "verde": "#39D98A",
                        "amarillo": "#FFBD59", "rojo": "#FF647C", "texto": "#F2F5FC", "tenue": "#A7B4CE", "borde": "#263550"}


def test_config_toml_coincide_con_la_paleta():
    tema = CONFIG["theme"]
    assert tema["primaryColor"].upper() == t.PALETA["cian"]
    assert tema["backgroundColor"].upper() == t.PALETA["fondo"]
    assert tema["secondaryBackgroundColor"].upper() == t.PALETA["panel"]
    assert tema["textColor"].upper() == t.PALETA["texto"]
    assert tema["borderColor"].upper() == t.PALETA["borde"]
    assert CONFIG["theme"]["sidebar"]["backgroundColor"].upper() == t.LATERAL


@pytest.mark.parametrize("color", ["texto", "tenue", "cian", "violeta", "verde", "amarillo", "rojo"])
def test_contraste_sobre_el_fondo_y_el_panel(color):
    assert t.contraste(t.PALETA[color], t.PALETA["fondo"]) >= 4.5
    assert t.contraste(t.PALETA[color], t.PALETA["panel"]) >= 4.5


def test_pie_y_series_legibles():
    assert t.contraste(t.PIE, t.PALETA["fondo"]) >= 4.5
    for nombre, c in t.SERIES.items():
        assert t.contraste(c, t.PALETA["panel"]) >= 4.5, nombre


def test_las_series_son_distintas():
    assert len(set(t.SERIES.values())) == len(t.SERIES)


def test_css_sin_marcadores_sin_resolver():
    for marcador in ("FONDO", "PANEL2", "CIAN", "VIOLETA", "FUENTE_TITULOS", "PIE;"):
        assert marcador not in qc.CSS.replace("--ql-fondo", "")
    assert t.PALETA["cian"] in qc.CSS and t.PALETA["violeta"] in qc.CSS


def test_colores_de_graficas_salen_de_la_paleta():
    assert qc.COLORES["onda"] == t.PALETA["violeta"] and qc.COLORES["densidad"] == t.PALETA["cian"]
    assert qc.COLORES["energia"] == t.PALETA["amarillo"] and qc.COLORES["fondo"] == t.PALETA["fondo"]
