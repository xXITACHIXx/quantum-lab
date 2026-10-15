"""
Pruebas del progreso guardado, las gráficas interactivas y las reglas de calidad de los Ejercicios de práctica.
"""
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from streamlit.testing.v1 import AppTest

import ejercicios
from ejercicios import _calidad, _figuras, _progreso

APP = str(Path(__file__).parent / "quantum_lab.py")
EJ = {e.id: e for e in ejercicios.EJERCICIOS}
IDS = ejercicios.IDS


def _esperado(ej_id, clave):
    return next(p.esperado for p in EJ[ej_id].partes if p.clave == clave)


# ---------------------------------------------------------------------
# Progreso: codificación
# ---------------------------------------------------------------------
def test_tokens_unicos_y_estables():
    tokens = [_progreso.token(i) for i in IDS]
    assert len(set(tokens)) == len(IDS)
    assert all(len(t) == 4 for t in tokens)
    assert _progreso.token("s9_nodos") == _progreso.token("s9_nodos")


def test_codificar_y_decodificar_ida_y_vuelta():
    hechos = {"s9_nodos", "l08_d2", "h05_prob"}
    assert _progreso.decodificar(_progreso.codificar(hechos, IDS), IDS) == hechos
    assert _progreso.decodificar(_progreso.codificar(set(IDS), IDS), IDS) == set(IDS)
    assert _progreso.codificar(set(), IDS) == ""


def test_codigo_no_depende_del_orden_de_los_ejercicios():
    hechos = {"s9_nodos", "l08_d2"}
    codigo = _progreso.codificar(hechos, IDS)
    assert _progreso.decodificar(codigo, tuple(reversed(IDS))) == hechos       # si se reordena la lista, el progreso sigue valiendo


def test_codigo_manipulado_se_ignora():
    for basura in (None, "", "!!", "x", "ñññññññ", "AAAA", 12345, "\n"):
        assert _progreso.decodificar(basura, IDS) <= set(IDS)                  # nunca falla
    assert _progreso.decodificar("AAAA", IDS) == set()


def test_json_ida_y_vuelta_y_errores():
    hechos = {"s1_lyman", "l01_hi"}
    assert _progreso.desde_json(_progreso.a_json(hechos, IDS), IDS) == hechos
    assert _progreso.desde_json(json.dumps({"quantum_lab": "ejercicios", "resueltos": ["s1_lyman", "no_existe", 3]}), IDS) == {"s1_lyman"}
    for malo in ("no es json", "[]", json.dumps({"otro": 1}), json.dumps({"quantum_lab": "ejercicios", "resueltos": "x"})):
        with pytest.raises(ValueError):
            _progreso.desde_json(malo, IDS)


# ---------------------------------------------------------------------
# Progreso: interfaz
# ---------------------------------------------------------------------
def _abrir(**estado) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "ejercicios"
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


def test_acertar_marca_resuelto_y_actualiza_la_url():
    at = _abrir(ej_sel="s1_fotoelectrico")
    ej = EJ["s1_fotoelectrico"]
    for p in ej.partes:
        at.text_input(key=f"ej_{ej.id}_{p.clave}").set_value(f"{p.esperado:.6g}")
    at.button(key=f"ej_{ej.id}_btn").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert "s1_fotoelectrico" in at.session_state["ej_hechos"]
    assert at.checkbox(key="ej_hecho_s1_fotoelectrico").value is True
    assert _progreso.decodificar(at.query_params["prog"], IDS) == {"s1_fotoelectrico"}


def test_marcar_y_desmarcar_a_mano():
    at = _abrir(ej_sel="l08_d2")
    at.checkbox(key="ej_hecho_l08_d2").check().run()
    assert at.session_state["ej_hechos"] == {"l08_d2"}
    at.checkbox(key="ej_hecho_l08_d2").uncheck().run()
    assert at.session_state["ej_hechos"] == set()
    assert "prog" not in at.query_params


def test_respuesta_incorrecta_no_marca_resuelto():
    at = _abrir(ej_sel="s1_fotoelectrico")
    ej = EJ["s1_fotoelectrico"]
    for p in ej.partes:
        at.text_input(key=f"ej_{ej.id}_{p.clave}").set_value("123456.789")
    at.button(key=f"ej_{ej.id}_btn").click().run()
    assert at.session_state["ej_hechos"] == set()


def test_el_progreso_se_recupera_desde_la_direccion():
    codigo = _progreso.codificar({"s9_nodos", "h05_prob"}, IDS)
    at = AppTest.from_file(APP, default_timeout=180)
    at.query_params["prog"] = codigo
    at.query_params["sim"] = "ejercicios"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["ej_hechos"] == {"s9_nodos", "h05_prob"}


def test_siguiente_sin_resolver_salta_los_hechos():
    at = _abrir(ej_sel=IDS[0], ej_hechos={IDS[1], IDS[2]})
    at.button(key="ej_pend").click().run()
    assert at.session_state["ej_sel"] == IDS[3]


def test_borrar_progreso():
    at = _abrir(ej_hechos={"s9_nodos"})
    at.button(key="ej_bk_borrar").click().run()
    assert at.session_state["ej_hechos"] == set()


# ---------------------------------------------------------------------
# Gráficas: cada una debe mostrar lo que la solución afirma
# ---------------------------------------------------------------------
def test_toda_figura_pertenece_a_un_ejercicio_y_se_dibuja():
    for ej_id, figuras in _figuras.FIGURAS.items():
        assert ej_id in EJ
        for f in figuras:
            assert f.descripcion and f.titulo
            valores = [None] if f.parametro is None else range(f.parametro[1], f.parametro[2] + 1)
            for v in valores:
                assert len(f.dibujar(v).data) > 0
            if f.parametro:
                assert f.parametro[1] <= f.parametro[3] <= f.parametro[2]


def test_nodos_del_oscilador_son_los_de_la_solucion():
    nodos = _figuras.nodos_hermite(4)
    assert len(nodos) == 4
    assert nodos[-1] == pytest.approx(_esperado("s9_nodos", "x2"), rel=1e-9)
    assert nodos[-2] == pytest.approx(_esperado("s9_nodos", "x1"), rel=1e-9)
    for n in range(0, 9):
        assert len(_figuras.nodos_hermite(n)) == n
        u = _figuras.nodos_hermite(n)
        assert np.allclose(_figuras.psi_oscilador(n, u), 0, atol=1e-9)
        assert quad(lambda x: _figuras.psi_oscilador(n, np.array([x]))[0] ** 2, -12, 12)[0] == pytest.approx(1.0, rel=1e-6)


def test_oscilador_ortogonal_entre_estados():
    f = lambda m, n: quad(lambda x: _figuras.psi_oscilador(m, np.array([x]))[0] * _figuras.psi_oscilador(n, np.array([x]))[0], -12, 12)[0]
    assert f(0, 2) == pytest.approx(0, abs=1e-8)
    assert f(1, 4) == pytest.approx(0, abs=1e-8)


def test_conos_coinciden_con_las_soluciones():
    angulos = _figuras.angulos_cono(5)
    assert len(angulos) == 11
    assert angulos[0][0] == 5 and angulos[0][1] == pytest.approx(_esperado("l04_conos_l5", "t5"), abs=0.01)
    assert [round(m) for m, _ in angulos] == list(range(5, -6, -1))
    assert angulos[5][1] == pytest.approx(90.0)
    ls = 1000
    assert math.degrees(math.acos(math.sqrt(ls / (ls + 1)))) == pytest.approx(_esperado("s10_conos", "theta"), abs=0.01)


def test_radiales_normalizadas_y_nodos():
    for f in (_figuras.radial_30, _figuras.radial_42, _figuras.radial_21):
        assert quad(lambda r: r * r * f(np.array([r]))[0] ** 2, 0, 200)[0] == pytest.approx(1.0, rel=1e-6)
    n1, n2 = _figuras.nodos_3s()
    assert n1 == pytest.approx(_esperado("s11_nodos3s", "r1"), abs=1e-3)
    assert n2 == pytest.approx(_esperado("s11_nodos3s", "r2"), abs=1e-3)
    assert _figuras.radial_30(np.array([n1, n2])) == pytest.approx([0, 0], abs=1e-12)
    assert _figuras.radial_42(np.array([_esperado("h10_4dz2", "r")]))[0] == pytest.approx(0, abs=1e-12)


def test_maximo_de_2pz_esta_donde_dice_la_solucion():
    fig = _figuras.fig_2pz()
    z = np.array(fig.data[0].y)
    psi = np.array(fig.data[0].z)[:, len(z) // 2]                        # columna x = 0
    assert abs(z[int(np.argmax(np.abs(psi)))]) == pytest.approx(_esperado("s11_2pz", "r"), abs=0.11)


def test_y20_nodos_y_caja():
    crit = math.degrees(math.acos(1 / math.sqrt(3)))
    assert crit == pytest.approx(_esperado("l07_y20_nodos", "t1"), abs=0.01)
    assert 180 - crit == pytest.approx(_esperado("l07_y20_nodos", "t2"), abs=0.01)
    p = quad(lambda x: 2 * math.sin(math.pi * x) ** 2, 1 / 3, 2 / 3)[0]
    assert any("P = %.3f" % p in t.name for t in _figuras.fig_caja_tercio().data)
    assert p == pytest.approx(_esperado("s6_prob_tercio", "P"))


@pytest.mark.parametrize("ej_id", list(_figuras.FIGURAS))
def test_la_pagina_muestra_las_graficas(ej_id):
    at = _abrir(ej_sel=ej_id)
    assert not at.exception, [e.value for e in at.exception]
    titulos = [e.label for e in at.expander if "Gráfica interactiva" in e.label]
    assert len(titulos) == len(_figuras.FIGURAS[ej_id])


def test_deslizador_de_la_grafica_funciona():
    at = _abrir(ej_sel="s9_nodos")
    at.slider(key="ej_fig_s9_nodos_0").set_value(6).run()
    assert not at.exception, [e.value for e in at.exception]


# ---------------------------------------------------------------------
# Calidad
# ---------------------------------------------------------------------
@pytest.mark.parametrize("ej", ejercicios.EJERCICIOS, ids=lambda e: e.id)
def test_reglas_de_calidad(ej):
    assert _calidad.revisar(ej) == []


def test_las_reglas_de_calidad_detectan_problemas():
    from dataclasses import replace
    base = EJ["s9_nodos"]
    assert _calidad.revisar(replace(base, id="Mal Id"))
    assert _calidad.revisar(replace(base, id="s8_nodos"))                    # la semana del id no coincide con la referencia
    assert _calidad.revisar(replace(base, solucion="#### Paso 1\nSolo uno"))
    assert _calidad.revisar(replace(base, solucion=base.solucion.replace("#### Paso 2", "#### Paso 7")))
    assert _calidad.revisar(replace(base, pistas=()))
    assert _calidad.revisar(replace(base, enunciado=base.enunciado + " $x"))
    assert _calidad.revisar(replace(base, nota="TODO revisar"))


def test_informe_de_mantenimiento_sin_fallos(capsys):
    from ejercicios import __main__ as informe
    assert informe.main() == 0
    assert "Pruebas internas" in capsys.readouterr().out


def test_el_readme_cuenta_bien():
    readme = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
    assert f"{len(ejercicios.EJERCICIOS)} ejercicios" in readme, "actualiza el número de ejercicios del README"
