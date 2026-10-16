"""Pruebas de las ilustraciones SVG, las tarjetas de la portada y el encabezado con ilustración."""
import re
from pathlib import Path
from xml.dom import minidom

import pytest
from streamlit.testing.v1 import AppTest

import quantum_lab
import quantum_lab_arte as arte
import quantum_lab_portada as portada
import quantum_lab_tema as tema

APP = str(Path(__file__).parent / "quantum_lab.py")
PERMITIDOS = {c.upper() for c in tema.PALETA.values()} | {tema.PANEL_2.upper(), tema.SERIES["potencial"].upper(), tema.SERIES["interferencia"].upper()}
SIMULADORES = ["caja", "oscilador", "esfera", "fotoelectrico", "bohr", "incertidumbre"]


def _todas():
    return {**{k: arte.svg(k) for k in SIMULADORES}, "portada": arte.portada()}


@pytest.mark.parametrize("clave", SIMULADORES + ["portada"])
def test_svg_valido_ligero_y_sin_recursos_externos(clave):
    s = _todas()[clave]
    minidom.parseString(s)                                              # XML bien formado
    assert len(s) < 30_000
    assert "http://" not in s.replace("http://www.w3.org/2000/svg", "") and "https://" not in s
    assert "<image" not in s and "<script" not in s and "href" not in s
    assert 'role="img"' in s and "<title>" in s and "Ilustración conceptual" in s


@pytest.mark.parametrize("clave", SIMULADORES + ["portada"])
def test_svg_usa_solo_colores_de_la_paleta(clave):
    colores = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", _todas()[clave])}
    ajenos = colores - PERMITIDOS
    # Las líneas de Balmer usan los colores de longitud de onda (físicos), no los de la paleta.
    if clave == "bohr":
        ajenos = {c for c in ajenos if c not in {x.upper() for x in re.findall(r"stroke=\"(#[0-9A-Fa-f]{6})\" stroke-width=\"2.4\"", _todas()[clave])}}
    assert not ajenos, ajenos


def test_la_portada_es_reproducible():
    assert arte.portada() == arte.portada()


def test_los_iconos_son_validos():
    for clave in ("ruta", "teoria", "formulario", "talleres", "ejercicios", "examen", "repaso", "verificacion", "pruebas"):
        minidom.parseString(arte.icono(clave))
    assert arte.icono("no_existe") == ""


def test_balmer_usa_longitudes_de_onda_reales():
    s = arte.bohr()
    assert s.count('stroke-width="2.4"') == 4                           # H-alfa, H-beta, H-gamma y H-delta


def test_modulos_cubren_todas_las_paginas_una_vez():
    claves = [m[0] for m in portada.MODULOS]
    esperado = [k for k in quantum_lab.PAGINAS if k != "inicio"]
    assert sorted(claves) == sorted(esperado) and len(set(claves)) == len(claves)
    assert [m[1] for m in portada.MODULOS] == [f"{i:02d}" for i in range(1, 16)]
    assert {m[2] for m in portada.MODULOS} == set(portada.CATEGORIAS)


def test_las_categorias_coinciden_con_la_barra_lateral():
    grupos = {titulo: claves for titulo, claves, _ in quantum_lab.GRUPOS}
    for clave, _, categoria, *_ in portada.MODULOS:
        assert clave in grupos[categoria]


def test_tarjeta_escapa_el_texto():
    h = portada.tarjeta_html("caja", "01", "Cat", portada.ESTUDIO, "<b>x</b>", "a & b", "")
    assert "<b>x</b>" not in h and "&lt;b&gt;" in h and "a &amp; b" in h


def test_las_tarjetas_de_simulador_llevan_ilustracion_y_las_demas_icono():
    sim = portada.tarjeta_html(*portada.MODULOS[0])
    est = portada.tarjeta_html(*[m for m in portada.MODULOS if m[0] == "ruta"][0])
    assert "ql-miniatura" in sim and "<svg" in sim
    assert "ql-icono-caja" in est and "ql-miniatura" not in est


def test_la_portada_no_inventa_indicadores():
    texto = " ".join(m[5] for m in portada.MODULOS).lower()
    for prohibido in ("usuarios", "experimentos realizados", "% completado"):
        assert prohibido not in texto


def _abrir(pagina=None):
    at = AppTest.from_file(APP, default_timeout=180)
    if pagina:
        at.session_state["ql_pagina"] = pagina
    at.run()
    return at


def test_inicio_tiene_boton_y_un_boton_por_modulo():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]
    claves = {b.key for b in at.button if b.key and b.key.startswith("ql_abrir_")}
    assert claves == {f"ql_abrir_{m[0]}" for m in portada.MODULOS}
    html = " ".join(m.value for m in at.markdown)
    assert "Explorar simuladores" in html and f'href="#{portada.ID_SIMULADORES}"' in html


@pytest.mark.parametrize("clave", SIMULADORES)
def test_cada_simulador_muestra_su_ilustracion(clave):
    at = _abrir(clave)
    assert not at.exception, [e.value for e in at.exception]
    assert any('class="ql-cab-arte"' in m.value for m in at.markdown)


def test_paginas_sin_ilustracion_no_la_muestran():
    at = _abrir("formulario")
    assert not any('class="ql-cab-arte"' in m.value for m in at.markdown)


def test_el_boton_de_una_tarjeta_navega():
    at = _abrir()
    at.button(key="ql_abrir_oscilador").click().run()
    assert at.session_state["ql_pagina"] == "oscilador"
