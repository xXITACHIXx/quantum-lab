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


def _abrir(pagina=None, vista="Tarjetas"):
    at = AppTest.from_file(APP, default_timeout=180)
    if vista:
        at.session_state["ql_vista"] = (vista == "Tarjetas")
    if pagina:
        at.session_state["ql_pagina"] = pagina
    at.run()
    return at


def test_portada_destinos_y_observatorio():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]
    html = " ".join(m.value for m in at.markdown)
    assert 'id="ql-particulas"' in html and 'class="ql-fondo-atomo"' in html and 'class="ql-atomo"' in html
    assert f'id="{portada.ID_SIMULADORES}"' in html and f'id="{portada.ID_ESTUDIO}"' in html
    etiquetas = {b.key: b.label for b in at.button if b.key and b.key.startswith("ql_abrir_")}
    assert len(etiquetas) == 19 and etiquetas["ql_abrir_caja"] == "Abrir el simulador: Partícula en una caja"
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


import pytest


@pytest.mark.parametrize("archivo", ["particula_caja", "oscilador_armonico", "particula_esfera",
                                     "efecto_fotoelectrico", "modelo_bohr", "principio_incertidumbre"])
def test_ficha_en_los_seis_simuladores(archivo):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(f"{archivo}.py", default_timeout=90).run()
    assert not at.exception
    assert any("Objetivo" in m.value and "Ecuación central" in "".join(x.value for x in at.markdown) for m in at.markdown)
    assert len(at.latex) >= 1
    assert any("Alcance del modelo" in m.value for m in at.markdown)


def test_fondo_vivo_y_microinteracciones_respetan_accesibilidad():
    import quantum_lab_escena as e
    css = e.css()
    movimiento = css[css.index("prefers-reduced-motion: reduce"):]
    assert "#ql-fondo-vivo" in movimiento                       # el fondo se oculta con movimiento reducido
    assert "ql-fondo-vivo" in css and "max-width: 640px" in css  # y en pantallas pequeñas
    assert "pointer-events: none" in css[css.index("#ql-fondo-vivo {"):][:200]   # nunca bloquea el desplazamiento ni los clics
    for k in ("ql-aparece", "ql-relleno", "ql-fundir", "ql-aviso", "ql-resalte"):
        assert f"@keyframes {k}" in css
    assert "ql-abriendo" in e.JS and "ql-aparta" in e.JS and "reducir.matches" in e.JS


def test_trazos_numerados_para_la_secuencia():
    import quantum_lab_arte as a
    svg = a.svg("oscilador")
    indices = [int(x) for x in __import__("re").findall(r'--i:(\d+)', svg)]
    assert indices == list(range(1, len(indices) + 1)) and len(indices) >= 2


def test_emergencia_desde_abajo_y_nube_orbital():
    import quantum_lab_escena as e
    css, js = e.css(), e.JS
    for k in ("ql-em-fondo", "ql-em-sube", "ql-em-baja", "ql-em-texto", "ql-pagina-sube"):
        assert f"@keyframes {k}" in css
    movimiento = css[css.index("prefers-reduced-motion: reduce"):]
    assert "#ql-emerge" in movimiento                              # la emergencia se oculta con movimiento reducido
    assert "if (reducir.matches) { return; }" in js[js.index("function emergerDesde"):][:120]
    assert "pointer-events: none" in css[css.index("#ql-emerge {"):][:260]   # nunca bloquea clics ni desplazamiento
    assert "MAX_EMERGE" in js and "MIN_EMERGE" in js               # se retira sola si la navegación no ocurre
    assert "innerHTML" not in js                                   # el JS no lleva etiquetas HTML (st.html lo descartaba)
    assert "Math.min(90" in js                                     # límite de partículas
    assert "p.orb" in js and "destination-out" in js               # órbitas con estela
    assert "st-key-ql_item_" in js and "ql_volver" in js and "ql_categoria" in js



def test_portada_muestra_solo_los_cuatro_capitulos():
    at = _abrir(vista=None)
    assert not at.exception, [e.value for e in at.exception]
    claves = {b.key for b in at.button if b.key and b.key.startswith("ql_menu_")}
    assert claves == {f"ql_menu_{c}" for c in portada.CAT_CLAVE.values()} and len(claves) == 5
    assert not any(b.key and b.key.startswith("ql_abrir_") for b in at.button)       # las tarjetas quedan en la otra vista
    html = " ".join(m.value for m in at.markdown)
    assert html.count('class="ql-esc-item ql-esc-') == 5                              # una escena por capítulo
    assert f'id="{portada.ID_SIMULADORES}"' in html and f'id="{portada.ID_ESTUDIO}"' in html


def test_no_hay_barra_lateral():
    at = _abrir(vista=None)
    assert len(at.sidebar.button) == 0 and len(at.sidebar.markdown) == 0
    assert "collapsed" in open(APP, encoding="utf-8").read()


@pytest.mark.parametrize("categoria", portada.CATEGORIAS)
def test_subportada_lista_los_temas_del_capitulo(categoria):
    at = _abrir(portada.CAT_CLAVE[categoria], vista=None)
    assert not at.exception, [e.value for e in at.exception]
    esperados = {f"ql_menu_{m[0]}" for m in portada.MODULOS if m[2] == categoria}
    assert {b.key for b in at.button if b.key and b.key.startswith("ql_menu_")} == esperados
    assert any(b.key == "ql_volver" for b in at.button)
    assert not any('class="ql-ubicacion"' in m.value for m in at.markdown)


def test_navegacion_completa_inicio_capitulo_tema_y_regreso():
    at = _abrir(vista=None)
    at.button(key="ql_menu_cat2").click().run()
    assert at.session_state["ql_pagina"] == "cat2" and not at.exception
    at.button(key="ql_menu_bohr").click().run()
    assert at.session_state["ql_pagina"] == "bohr" and not at.exception
    at.button(key="ql_categoria").click().run()
    assert at.session_state["ql_pagina"] == "cat2"
    at.button(key="ql_volver").click().run()
    assert at.session_state["ql_pagina"] == "inicio"


def test_menu_css_por_elemento_y_accesibilidad():
    import quantum_lab_escena as e
    css = portada._css_menu(portada._entradas())
    for c in portada.CAT_CLAVE.values():
        assert f".ql-esc-{c}" in css and f"st-key-ql_item_{c}" in css
    assert ":focus-within" in css                         # el teclado enciende el mismo escenario que el cursor
    base = e.css()
    assert "@keyframes ql-menu-entra" in base and "@keyframes ql-esc-entra" in base
    assert ".ql-esc { display: none; }" in base           # en pantallas pequeñas queda solo la lista
    assert "calc(var(--k, 0) * 2.6rem)" in base           # escalera semi-diagonal


def test_atomo_de_fondo_es_conceptual_y_accesible():
    import quantum_lab_arte as a
    s = a.atomo()
    assert 'role="img"' in s and "aria-label=" in s and "<title>" in s
    assert "ILUSTRACIÓN CONCEPTUAL" in s                          # se declara como ilustración, no como resultado
    assert s.count('class="ql-obs-giro ') == 4                    # órbitas de referencia que giran con CSS
    assert "http" not in s.replace("http://www.w3.org/2000/svg", "")   # sin recursos externos
    assert len(s) < 120_000                                       # ligero: nubes como un solo trazo por grupo


def test_inicio_a_pantalla_completa():
    import quantum_lab_escena as e
    css = e.css()
    assert 'stMainBlockContainer"]:has(.st-key-ql_menu)' in css   # solo la portada anula el ancho máximo
    assert "min-height: 100vh" in css and "skewX(-14deg)" in css
    assert ".ql-velo" in css                                      # velo que garantiza el contraste del texto sobre el átomo
    at = _abrir("caja", vista=None)
    html = " ".join(m.value for m in at.markdown)
    assert "stMainBlockContainer" in html and not any(b.key == "ql_menu_caja" for b in at.button)   # el menú solo existe en la portada
