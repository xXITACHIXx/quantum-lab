"""Pruebas de la escena: navegación animada, destinos interactivos y observatorio (estructura, accesibilidad y respaldo sin JS)."""
import re
from pathlib import Path
from xml.dom import minidom

import pytest
from streamlit.testing.v1 import AppTest

import quantum_lab
import quantum_lab_arte as arte
import quantum_lab_escena as escena
import quantum_lab_portada as portada
import quantum_lab_tema as tema

APP = str(Path(__file__).parent / "quantum_lab.py")
CSS = escena.css()


def test_toda_animacion_usada_esta_definida():
    definidas = set(re.findall(r"@keyframes\s+([\w-]+)", CSS))
    usadas = {n for n in re.findall(r"animation:\s*([\w-]+)", CSS) if n != "none"}
    assert usadas <= definidas, usadas - definidas


def test_respeta_reducir_movimiento():
    bloque = CSS[CSS.index("prefers-reduced-motion: reduce"):]
    assert "animation: none !important" in bloque and "transition: none !important" in bloque
    assert "matchMedia('(prefers-reduced-motion: reduce)')" in escena.JS


def test_en_movil_se_suprimen_las_capas_costosas():
    bloque = CSS[CSS.index("@media (max-width: 640px)"):]
    assert ".ql-obs-plano" in bloque.split("}")[0] and ".ql-obs-particulas" in bloque.split("}")[0]


def test_sin_marcadores_ni_recursos_externos():
    assert "§" not in CSS and tema.PROFUNDO in CSS
    for texto in (CSS, escena.JS):
        assert "http://" not in texto and "https://" not in texto and "@import" not in texto


def test_el_js_se_instala_una_sola_vez_y_no_toca_la_fisica():
    assert "window.__qlEfectos" in escena.JS.replace("W.__qlEfectos", "window.__qlEfectos")
    for prohibido in ("fetch(", "XMLHttpRequest", "localStorage", "eval(", "innerHTML"):
        assert prohibido not in escena.JS


class _StSinJS:
    def html(self, cuerpo, width="stretch"):
        raise AssertionError("no debería llamarse")


class _StConJS:
    def __init__(self):
        self.llamadas = []

    def html(self, cuerpo, width="stretch", unsafe_allow_javascript=False):
        self.llamadas.append(unsafe_allow_javascript)


def test_instalar_efectos_tiene_respaldo():
    assert escena.instalar_efectos(_StSinJS()) is False          # Streamlit sin JS en st.html: solo CSS
    st = _StConJS()
    assert escena.instalar_efectos(st) is True and st.llamadas == [True]


def test_observatorio_es_svg_valido_y_conceptual():
    s = arte.observatorio()
    minidom.parseString(s)
    assert "ILUSTRACIÓN CONCEPTUAL" in s and "<script" not in s and "href" not in s
    assert s.count('class="ql-obs-giro ') == 3 and "ql-obs-nube" in s


def test_las_lecturas_son_datos_reales():
    import ejercicios
    import formulario
    lect = dict((k, v) for v, k in portada.lecturas())
    assert lect["simuladores"] == "6"
    assert lect["ejercicios"] == str(len(ejercicios.EJERCICIOS))
    assert lect["fórmulas"] == str(sum(len(s.todas()) for s in formulario.SECCIONES))


def test_ubicacion_escapa_y_numera():
    h = escena.ubicacion_html("A & B", "<x>", "05", 15)
    assert "&amp;" in h and "&lt;x&gt;" in h and "05 · 15" in h and 'aria-label="Ubicación"' in h


def test_composicion_asimetrica():
    for categoria, (proporciones, mayor) in portada.COMPOSICION.items():
        assert len(proporciones) == 3 and proporciones[mayor] == max(proporciones)
        assert proporciones.count(max(proporciones)) == 1
    assert portada.COMPOSICION["Mecánica cuántica"][1] != portada.COMPOSICION["Fundamentos"][1]


def test_tarjeta_mayor_y_compacta():
    m = portada.modulo("caja")
    assert "ql-dest-mayor" in portada.tarjeta_html(*m, mayor=True)
    assert "ql-dest-compacta" in portada.tarjeta_html(*portada.modulo("ruta"), compacta=True)


def _abrir(pagina=None):
    at = AppTest.from_file(APP, default_timeout=180)
    if pagina:
        at.session_state["ql_pagina"] = pagina
    at.run()
    return at


def test_portada_destinos_y_observatorio():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]
    html = " ".join(m.value for m in at.markdown)
    assert 'id="ql-particulas"' in html and 'class="ql-obs"' in html
    assert f'id="{portada.ID_SIMULADORES}"' in html and f'id="{portada.ID_ESTUDIO}"' in html
    etiquetas = {b.key: b.label for b in at.button if b.key and b.key.startswith("ql_abrir_")}
    assert len(etiquetas) == 15 and etiquetas["ql_abrir_caja"] == "Abrir el simulador: Partícula en una caja"
    assert not any("ql-ubicacion" in m.value and "role=" in m.value for m in at.markdown)


@pytest.mark.parametrize("pagina", [k for k in quantum_lab.PAGINAS if k != "inicio"])
def test_cada_pagina_muestra_su_ubicacion_y_vuelve_al_observatorio(pagina):
    at = _abrir(pagina)
    assert not at.exception, [e.value for e in at.exception]
    m = portada.modulo(pagina)
    assert any('class="ql-ubicacion"' in x.value and m[1] in x.value for x in at.markdown)
    at.button(key="ql_volver").click().run()
    assert at.session_state["ql_pagina"] == "inicio"


def test_un_parametro_no_cambia_de_escena():
    """Mover un control no cambia de página: la clave de la escena (y por tanto la animación de entrada) se conserva."""
    at = _abrir("caja")
    at.number_input(key=at.number_input[0].key).set_value(2).run()
    assert not at.exception and at.session_state["ql_pagina"] == "caja"


def test_ficha_simulador_caja_es_estatica():
    """La ficha del simulador de la caja aparece y no depende de los parámetros."""
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file("particula_caja.py", default_timeout=60).run()
    assert not at.exception
    assert any("Objetivo" in m.value for m in at.markdown)
    assert any("n_{" in l.value or "E_n" in l.value for l in at.latex)
    antes = [m.value for m in at.markdown if "Objetivo" in m.value]
    at.session_state["caja_n"] = 3
    at.run()
    assert not at.exception
    assert antes == [m.value for m in at.markdown if "Objetivo" in m.value]
