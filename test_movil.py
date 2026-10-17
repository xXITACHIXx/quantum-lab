"""Ajustes para celular: símbolos, botones de regreso y fondo estable."""
import os

import quantum_lab_arte as arte
import quantum_lab_comun as qc
import quantum_lab_escena as escena
from streamlit.testing.v1 import AppTest


def test_fuente_de_simbolos_pregenerada_y_con_familias_de_respaldo():
    assert os.path.exists(qc._ARCHIVO_FUENTE)                     # no depende de fontTools en el servidor
    css = qc.css_fuente_simbolos()
    for familia in ("Source Sans", "Source Code Pro", "QL Simbolos", "QL Simbolos Mono"):
        assert f'font-family: "{familia}"' in css
    assert "U+2070-209C" in css                                    # subíndices y superíndices
    assert '"QL Simbolos"' in qc.FUENTE_TEXTO and '"QL Simbolos Mono"' in qc.FUENTE_CIFRAS and '"QL Simbolos"' in qc.FUENTE_TITULOS


def test_ilustraciones_usan_la_fuente_de_simbolos():
    s = arte.svg("formulario")
    assert "QL Simbolos" in s


def test_botones_de_regreso_sin_icono_material():
    for pagina in ("caja", "cat1"):
        at = AppTest.from_file("quantum_lab.py", default_timeout=120)
        at.session_state["ql_pagina"] = pagina
        at.run()
        assert not at.exception
        volver = next(b for b in at.button if b.key == "ql_volver")
        assert volver.label.startswith("←") and "material" not in str(volver.proto.icon)


def test_fondo_del_atomo_estable_en_celular():
    css = escena.css()
    movil = css[css.index("Fondo estable en el celular"):]
    assert "animation: none" in movil and "100svh" in movil and "will-change: transform" in movil


def test_descripcion_de_figura_usa_solo_lo_que_la_figura_contiene():
    import matplotlib
    matplotlib.use("Agg")
    import particula_caja as pc
    p = pc.validar_parametros_caja(3, 2, 1.0, "SI", 500)
    fig = pc.figura_estado_individual(pc.calcular_estado_individual(p), p)
    d = qc.descripcion_figura(fig)
    assert "estado n = 3" in d and "4 paneles" in d and "Función de onda" in d and "eje x: x [nm]" in d
    assert "\\" not in d and "$" not in d and "mathrm" not in d        # sin restos de LaTeX
    assert "ψ_n(x)" in d


def test_las_imagenes_de_las_graficas_llevan_alt():
    at = AppTest.from_file("quantum_lab.py", default_timeout=120)
    at.session_state["ql_pagina"] = "oscilador"
    at.run()
    assert not at.exception
    imgs = list(at.get("image"))
    assert imgs, "el simulador debe mostrar al menos una gráfica"
    assert all(len(i.proto.imgs) and i.proto.imgs[0].alt for i in imgs)       # cada gráfica lleva texto alternativo


def test_refresco_de_graficas_respeta_movimiento_reducido():
    js = escena.JS
    css = escena.css()
    assert "ql-refresca" in css and "MutationObserver" in js
    bloque = js[js.index("Refresco de gráficas"):][:700]
    assert "reducir.matches" in bloque and "oldValue" in bloque          # solo cambia una imagen existente y no con movimiento reducido
    assert "innerHTML" not in js
