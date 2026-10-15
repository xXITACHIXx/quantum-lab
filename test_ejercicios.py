"""
Pruebas de los Ejercicios de práctica: estructura, calificación, contrastes numéricos independientes de las soluciones y la
interfaz (AppTest: filtros, navegación, comprobar una respuesta y abrir la solución).
"""
import math
from pathlib import Path

import pytest
from scipy import constants as const
from scipy.integrate import quad
from streamlit.testing.v1 import AppTest

import ejercicios
from ejercicios._modelo import CLASE, CUADERNO, LIBRO, TEMAS, calificar, llenar
from talleres._calificar import CASI, MAL, OK
from talleres._modelo import NUM, OPC

APP = str(Path(__file__).parent / "quantum_lab.py")
EJ = {e.id: e for e in ejercicios.EJERCICIOS}


def _esperado(ej_id, clave):
    return next(p.esperado for p in EJ[ej_id].partes if p.clave == clave)


# ---------------------------------------------------------------------
# Estructura
# ---------------------------------------------------------------------
def test_registro_interno_sin_fallos():
    reg = ejercicios.ejecutar_pruebas()
    assert reg.todo_ok(), [r for r in reg.resultados if not r["ok"]]


def test_hay_ejercicios_de_las_tres_fuentes():
    fuentes = {e.fuente for e in ejercicios.EJERCICIOS}
    assert fuentes == {CLASE, LIBRO, CUADERNO}
    assert len(ejercicios.EJERCICIOS) >= 55


@pytest.mark.parametrize("ej", ejercicios.EJERCICIOS, ids=lambda e: e.id)
def test_cada_ejercicio_completo(ej):
    assert ej.titulo and ej.enunciado and ej.referencia
    assert ej.tema in TEMAS
    assert ej.solucion.count("#### Paso") >= 3, "la solución debe ir paso a paso"
    assert ej.solucion.count("$$") % 2 == 0, "bloques $$ desbalanceados"
    assert "<<" not in ej.solucion
    assert ej.pistas, "cada ejercicio tiene al menos una pista"
    if ej.comprobable:
        assert calificar(ej, ejercicios.respuestas_correctas(ej)).fraccion == pytest.approx(1.0)


@pytest.mark.parametrize("ej", [e for e in ejercicios.EJERCICIOS if e.comprobable], ids=lambda e: e.id)
def test_respuestas_erroneas_no_puntuan(ej):
    malas = {}
    for p in ej.partes:
        if p.tipo == OPC:
            malas[p.clave] = p.opciones[(p.correcta + 1) % len(p.opciones)]
        else:
            malas[p.clave] = "123456.789" if p.esperado != 123456.789 else "1"
    assert calificar(ej, malas).fraccion == 0.0


def test_llenar_avisa_si_falta_un_valor():
    assert llenar(r"$a=<<a>>$", a=2) == "$a=2$"
    with pytest.raises(KeyError):
        llenar("<<a>> y <<b>>", a=1)


def test_filtros():
    assert all(e.fuente == LIBRO for e in ejercicios.filtrar(fuente=LIBRO))
    assert all(e.tema == "oscilador" for e in ejercicios.filtrar(tema=TEMAS["oscilador"]))
    assert [e.id for e in ejercicios.filtrar(texto="lyman")] == ["s1_lyman"]
    assert ejercicios.filtrar(texto="zzzz-no-existe") == []


# ---------------------------------------------------------------------
# Contrastes numéricos independientes
# ---------------------------------------------------------------------
def test_fotoelectrico_y_bohr():
    ek = const.h * const.c / 300e-9 - 2.26 * const.e
    assert _esperado("s1_fotoelectrico", "ek") == pytest.approx(ek)
    assert _esperado("s1_fotoelectrico", "v") == pytest.approx(8.12e5, rel=2e-3)
    assert _esperado("s1_radio_bohr", "r") == pytest.approx(const.physical_constants["Bohr radius"][0], rel=1e-6)


def test_de_broglie():
    assert _esperado("s1_difraccion", "E") == pytest.approx(2.7e-18, rel=0.01)
    assert _esperado("s1_fluor", "v") == pytest.approx(0.0467, rel=0.01)


def test_normalizaciones_por_integracion():
    n = _esperado("s2_cw_normalizar", "N")
    assert 4 * math.pi * n ** 2 * quad(lambda r: r * r * math.exp(-2 * r), 0, math.inf)[0] == pytest.approx(1.0)
    N = _esperado("s2_normalizar", "N")
    assert N ** 2 * quad(lambda x: (1 - x) ** 2, 0, 1)[0] == pytest.approx(1.0)


def test_caja_y_conmutadores():
    p = quad(lambda x: 2 * math.sin(math.pi * x) ** 2, 1 / 3, 2 / 3)[0]
    assert _esperado("s6_prob_tercio", "P") == pytest.approx(p)
    x2 = quad(lambda x: 2 * x * x * math.sin(math.pi * x) ** 2, 0, 1)[0]
    dx = math.sqrt(x2 - 0.25)
    assert _esperado("s7_dxdp", "prod") == pytest.approx(dx * math.pi)


def test_oscilador_nodos_n4_son_ceros_de_hermite():
    from scipy.special import eval_hermite
    for clave in ("x1", "x2"):
        assert eval_hermite(4, _esperado("s9_nodos", clave)) == pytest.approx(0.0, abs=1e-9)


def test_variacional_es_minimo_y_cota_superior():
    from scipy.optimize import minimize_scalar

    def e(a):  # en h²/ma²: E(α) con ħ²/ma² = 1/(4π²)
        num = 5352851 * a * a / 12 + 608855 * a + 969969
        den = 15897 * a * a + 71060 * a + 184756
        return num / den / (4 * math.pi ** 2)
    res = minimize_scalar(e, bounds=(-2, 2), method="bounded")
    assert res.x == pytest.approx(_esperado("s13_variacional", "alfa"), rel=1e-3)
    assert res.fun == pytest.approx(_esperado("s13_variacional", "Emin"), rel=1e-6)
    assert e(0) == pytest.approx(_esperado("s13_variacional", "E0"), rel=1e-6)
    assert res.fun > 0.125


def test_rotacion():
    assert _esperado("s10_conos", "theta") == pytest.approx(1.81, abs=0.01)
    assert _esperado("l04_conos_l5", "t5") == pytest.approx(24.09, abs=0.01)
    assert _esperado("l01_hi", "dE") == pytest.approx(2.587e-22, rel=2e-3)
    assert _esperado("l19_cm_hf", "dF") == pytest.approx(4.62, abs=0.01)


def test_oscilador_libro():
    assert _esperado("l08_d2", "k") == pytest.approx(576, rel=2e-3)
    assert _esperado("l16_cl2", "m") == pytest.approx(0.742, rel=2e-3)
    assert _esperado("l18_moneda", "k") == pytest.approx(18.45, rel=2e-3)
    assert _esperado("l13_masas", "v") == pytest.approx(2.92e-15, rel=5e-3)
    assert _esperado("l22_cl2_v", "v") / _esperado("l22_cl2_v", "vr") == pytest.approx(0.946, abs=1e-3)
    assert _esperado("l14_transicion", "lam") == pytest.approx(9.517, rel=1e-3)


def test_ortogonalidad_oscilador_por_integracion():
    a = 1.7
    p0 = lambda x: (a / math.pi) ** 0.25 * math.exp(-a * x * x / 2)
    p2 = lambda x: (a / (4 * math.pi)) ** 0.25 * (2 * a * x * x - 1) * math.exp(-a * x * x / 2)
    assert quad(lambda x: p0(x) * p2(x), -math.inf, math.inf)[0] == pytest.approx(0.0, abs=1e-10)
    assert quad(lambda x: p2(x) ** 2, -math.inf, math.inf)[0] == pytest.approx(1.0)


def test_hidrogeno():
    ang = quad(lambda t: 5 / (16 * math.pi) * (3 * math.cos(t) ** 2 - 1) ** 2 * math.sin(t),
               math.acos(1 / math.sqrt(3)), math.pi - math.acos(1 / math.sqrt(3)))[0] * 2 * math.pi
    assert _esperado("h03_negativo", "P") == pytest.approx(ang)
    v = quad(lambda r: 4 * r * r * math.exp(-2 * r) * (-1 / r), 0, math.inf)[0] * 2 * 13.605693122994
    assert _esperado("h04_potencial", "V") == pytest.approx(v)
    assert _esperado("h05_prob", "P") == pytest.approx(quad(lambda r: 4 * r * r * math.exp(-2 * r), 1, 2)[0])
    assert _esperado("s11_nodos3s", "r1") == pytest.approx(1.902, abs=1e-3)


def test_errores_tipicos_se_diagnostican():
    from ejercicios._modelo import calificar as cal
    ej = EJ["s1_lyman"]
    r = cal(ej, {"lam": f"{_esperado('s1_lyman', 'lam') * 4 / 3:.6g}"}).resultados["lam"]
    assert r.estado == CASI and "2" in r.mensaje
    ej = EJ["l08_d2"]
    r = cal(ej, {"k": f"{_esperado('l08_d2', 'k') * 2:.6g}", "x": ""}).resultados["k"]
    assert r.estado == CASI and "masa reducida" in r.mensaje


# ---------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------
def _abrir(**estado) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "ejercicios"
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


def test_pagina_sin_excepciones():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]
    assert any("solución paso a paso" in t.label for t in at.toggle)


@pytest.mark.parametrize("ej_id", [e.id for e in ejercicios.EJERCICIOS])
def test_cada_ejercicio_se_muestra(ej_id):
    at = _abrir(ej_sel=ej_id)
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["ej_sel"] == ej_id


def test_comprobar_respuesta_y_navegar():
    at = _abrir(ej_sel="s1_fotoelectrico")
    ej = EJ["s1_fotoelectrico"]
    for p in ej.partes:
        at.text_input(key=f"ej_{ej.id}_{p.clave}").set_value(f"{p.esperado:.6g}")
    at.button(key=f"ej_{ej.id}_btn").click().run()
    assert not at.exception
    assert at.session_state["ej_res"][ej.id].fraccion == pytest.approx(1.0)
    at.button(key="ej_sig").click().run()
    assert at.session_state["ej_sel"] == ejercicios.EJERCICIOS[1].id


def test_filtro_por_fuente():
    at = _abrir()
    at.selectbox(key="ej_fuente").set_value(LIBRO).run()
    assert not at.exception
    assert ejercicios.buscar(at.session_state["ej_sel"]).fuente == LIBRO
