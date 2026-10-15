"""
Pruebas de los Talleres de repaso: lectura de números, calificación por partes, contrastes numéricos de las soluciones y la
interfaz (con AppTest: se abre un taller, se responde y se califica).
"""
import math
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import talleres
from talleres import _fisica as f
from talleres._calificar import CASI, INVALIDA, MAL, OK, VACIA, evaluar, evaluar_opcion, leer_numero
from talleres._modelo import NUM, OPC, Datos, calificar

APP = str(Path(__file__).parent / "quantum_lab.py")


@pytest.mark.parametrize("texto, valor", [("1.256e12", 1.256e12), ("1,256 x 10^12", 1.256e12), ("1,256×10¹²", 1.256e12),
                                          ("1.256*10**12", 1.256e12), ("−3.57", -3.57), ("10^3", 1e3), ("2,5E-3", 2.5e-3),
                                          ("  42 ", 42.0), (7, 7.0)])
def test_leer_numero(texto, valor):
    assert leer_numero(texto) == pytest.approx(valor, rel=1e-12)


@pytest.mark.parametrize("texto", ["abc", "", "1.2.3", "inf", "nan", "1e999"])
def test_leer_numero_rechaza(texto):
    with pytest.raises(ValueError):
        leer_numero(texto)


def test_evaluar_estados():
    assert evaluar("1.26e12", 1.256e12).estado == OK
    assert evaluar("1.5e12", 1.256e12).estado == MAL
    assert evaluar("", 1.0).estado == VACIA
    assert evaluar("hola", 1.0).estado == INVALIDA
    assert evaluar(1.256e12 * 2 * math.pi, 1.256e12).estado == CASI
    assert evaluar(-5.0, 5.0).estado == CASI
    assert evaluar("0", 0.0, tol_abs=0.01).estado == OK
    assert evaluar("3", 0.0, tol_abs=0.01).estado == MAL


def test_evaluar_confusion_propia_se_explica():
    r = evaluar(1.2e12, 2.4e12, confusiones=((0.5, "esa es la primera transición"),))
    assert r.estado == CASI and "primera transición" in r.mensaje


def test_evaluar_opcion():
    assert evaluar_opcion("b", 1, ["a", "b", "c"]).estado == OK
    assert evaluar_opcion("a", 1, ["a", "b", "c"]).estado == MAL
    assert evaluar_opcion(None, 1, ["a", "b", "c"]).estado == VACIA


def _correctas(q):
    return {p.clave: (p.opciones[p.correcta] if p.tipo == OPC else f"{p.esperado:.10g}") for p in q.partes}


@pytest.mark.parametrize("taller", talleres.TALLERES, ids=lambda t: t.id)
@pytest.mark.parametrize("original", [True, False])
def test_taller_respuestas_correctas_dan_puntaje_completo(taller, original):
    for semilla in range(1 if original else 8):
        qs = taller.construir(Datos(original, str(semilla)))
        assert len(qs) == taller.n_preguntas or not original
        for q in qs:
            cal = calificar(q, _correctas(q))
            assert cal.puntos == pytest.approx(q.puntos), (taller.id, q.id, cal.resultados)


def test_credito_parcial():
    q = talleres.t1_espectros.construir(Datos())[0]
    resp = _correctas(q)
    resp["rot"] = "1"                                    # solo falla la rotación (peso 0.45 de 1.0)
    cal = calificar(q, resp)
    assert cal.puntos == pytest.approx(q.puntos * 0.55)


def test_errores_tipicos_de_hf_se_diagnostican():
    q = talleres.t1_espectros.construir(Datos())[0]
    primera = f"{f.frecuencia_rotacion(0, f.momento_de_inercia(f.masa_reducida_u('H', 'F'), 91.68)):.6g}"
    resp = _correctas(q) | {"rot": primera}
    cal = calificar(q, resp)
    assert cal.resultados["rot"].estado == CASI and "primera" in cal.resultados["rot"].mensaje
    doble = f"{2 * f.frecuencia_vibracion(966.0, f.masa_reducida_u('H', 'F')):.6g}"
    assert calificar(q, _correctas(q) | {"vib": doble}).resultados["vib"].estado == CASI


def test_datos_originales_del_taller_de_la_foto():
    q1, q2 = talleres.t1_espectros.construir(Datos())
    esperado = {p.clave: p.esperado for p in q1.partes}
    assert esperado["rot"] == pytest.approx(2.513e12, rel=1e-3)          # 4B de HF
    assert esperado["vib"] == pytest.approx(1.2408e14, rel=1e-3)
    assert {p.clave: p.esperado for p in q2.partes}["AE"] == pytest.approx(122.45, rel=1e-3)
    q = talleres.t2_orbitales.construir(Datos())[1]
    assert {p.clave: p.esperado for p in q.partes}["R"] == pytest.approx(91.68, rel=5e-4)   # de 1.256×10¹² Hz sale 91.68 pm


def test_las_variantes_nuevas_cambian_los_valores():
    a = talleres.t4_moleculares.construir(Datos(False, "1"))[1]
    distintos = {tuple(round(p.esperado, 6) for p in talleres.t4_moleculares.construir(Datos(False, str(s)))[1].partes) for s in range(12)}
    assert len(distintos) > 1 and a is not None


def test_pruebas_internas():
    reg = talleres.ejecutar_pruebas()
    assert reg.todo_ok(), [r for r in reg.resultados if not r["ok"]]


# ---------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------
def _abrir(taller_id="", **estado) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "talleres"
    at.session_state["ql_taller"] = taller_id
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


def test_indice_sin_excepciones():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("taller", [t.id for t in talleres.TALLERES])
def test_cada_taller_se_abre(taller):
    at = _abrir(taller)
    assert not at.exception, [e.value for e in at.exception]


def test_responder_y_calificar_un_taller():
    at = _abrir("espectros")
    qs = talleres.preguntas_de("espectros", True, "espectros-0")
    q = qs[0]
    for p in q.partes:
        at.text_input(key=f"tl_espectros_o_0_{q.id}_{p.clave}").set_value(f"{p.esperado:.8g}")
    at.button(key=f"tl_espectros_o_0_{q.id}_btn").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.success) >= len(q.partes)
    assert any("2.00 / 3" in m.value for m in at.metric) or any("2.00" in m.value for m in at.metric)


def test_calificar_en_blanco_y_con_error_tipico():
    at = _abrir("espectros")
    q = talleres.preguntas_de("espectros", True, "espectros-0")[0]
    at.text_input(key=f"tl_espectros_o_0_{q.id}_rot").set_value("1.256e12")           # primera transición, no la segunda
    at.button(key=f"tl_espectros_o_0_{q.id}_btn").click().run()
    assert not at.exception
    assert any("primera transición" in w.value for w in at.warning)


def test_opcion_multiple_y_nuevo_intento():
    at = _abrir("moleculares")
    q = talleres.preguntas_de("moleculares", True, "moleculares-0")[0]
    p = next(x for x in q.partes if x.clave == "orden")
    at.radio(key=f"tl_moleculares_o_0_{q.id}_orden").set_value(p.opciones[p.correcta])
    at.button(key=f"tl_moleculares_o_0_{q.id}_btn").click().run()
    assert not at.exception
    at.button(key="tl_nuevo_moleculares").click().run()
    assert not at.exception and at.session_state["tl_int_moleculares"] == 1
    at.radio(key="tl_modo_moleculares").set_value(talleres.MODOS[1]).run()
    assert not at.exception, [e.value for e in at.exception]


def test_rotacion_del_h2_usa_solo_los_datos_del_enunciado():
    q = talleres.t3_p_rotor.construir(Datos())[1]
    esperado = {p.clave: p.esperado for p in q.partes}
    assert esperado == {"Lz": 2.0, "L": pytest.approx(math.sqrt(6)), "E": 3.0}        # l = 2, e^{i2φ}: Lz = 2ħ, |L| = √6 ħ, E = 3ħ²/I
    assert "pm" not in q.enunciado                                                   # no se añaden datos que el enunciado no da
    assert calificar(q, {"Lz": "2", "L": "2.449", "E": "3"}).puntos == pytest.approx(q.puntos)
    assert calificar(q, {"Lz": "2", "L": "2", "E": "3"}).resultados["L"].estado == CASI      # confundió l con √(l(l+1))


def test_oscilador_pide_solo_el_valor_esperado():
    q = talleres.t2_orbitales.construir(Datos())[0]
    assert [p.clave for p in q.partes] == ["x"] and q.partes[0].esperado == 0.0
    assert calificar(q, {"x": "0"}).puntos == pytest.approx(q.puntos)
