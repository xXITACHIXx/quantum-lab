"""Pruebas de la guía de usuario: diagramas de flujo, coherencia con el código y la página."""
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import guia
from guia import _flujos, _render

APP = str(Path(__file__).parent / "quantum_lab.py")
SIMULADORES_WEB = ["particula_caja", "oscilador_armonico", "particula_esfera", "efecto_fotoelectrico", "modelo_bohr", "principio_incertidumbre"]


class _Balance(HTMLParser):
    VACIOS = {"br", "img", "hr", "input", "meta", "link"}

    def __init__(self):
        super().__init__()
        self.pila, self.errores = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VACIOS:
            self.pila.append(tag)

    def handle_endtag(self, tag):
        if not self.pila or self.pila.pop() != tag:
            self.errores.append(tag)


def test_pruebas_internas():
    reg = guia.ejecutar_pruebas()
    assert all(f["Resultado"] == "Correcta" for f in reg.tabla()), reg.tabla()


@pytest.mark.parametrize("d", _flujos.TODOS, ids=lambda d: d.id)
def test_html_bien_formado_accesible_y_en_una_linea(d):
    h = _render.diagrama_html(d)
    p = _Balance()
    p.feed(h)
    assert not p.errores and not p.pila
    assert "\n" not in h                                         # Markdown no lo convierte en bloque de código
    assert f'aria-label="Diagrama de flujo: {d.titulo}"' in h
    assert len(re.findall(r'<li class="ql-paso(?: ql-decision)?"', h)) == len(d.pasos) and h.count(">Paso ") == len(d.pasos)
    assert "<script" not in h and "http" not in h


def test_texto_corto_en_cada_paso():
    for d in _flujos.TODOS:
        for p in d.pasos:
            assert len(p.titulo) <= 24 and len(p.puntos) <= 3 and all(len(t) <= 60 for t in p.puntos), (d.id, p.titulo)


def test_las_pestanas_citadas_existen_en_los_seis_simuladores():
    for nombre in SIMULADORES_WEB:
        fuente = Path(nombre + ".py").read_text(encoding="utf-8")
        pestanas = re.search(r"tabs = st\.tabs\(\[(.*?)\]\)", fuente, re.S).group(1)
        assert "Guía de práctica" in pestanas and "Autoevaluación" in pestanas
        assert pestanas.rstrip().rstrip('"').endswith("Pruebas numéricas"), nombre


def test_el_contraste_del_texto_es_suficiente():
    from quantum_lab_tema import PALETA, contraste
    assert contraste(PALETA["texto"], PALETA["panel"]) >= 4.5 and contraste(PALETA["tenue"], PALETA["panel"]) >= 4.5
    for tono in _flujos.TONOS:                                   # número oscuro sobre el círculo de color
        assert contraste(PALETA["fondo"], PALETA[tono]) >= 4.5, tono


def test_la_pagina_abre_con_sus_pestanas_y_navega_al_simulador():
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["ql_pagina"] = "guia"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert [t.label for t in at.tabs][:5] == ["Usar un simulador", "Cuadernos de Colab", "Partícula en una caja",
                                              "Oscilador armónico", "Partícula en una esfera"]
    textos = " ".join(m.value for m in at.markdown)
    assert all(f"Diagrama de flujo: {d.titulo}" in textos for d in _flujos.TODOS)
    at.button(key="guia_abrir_esfera").click().run()
    assert at.session_state["ql_pagina"] == "esfera"
