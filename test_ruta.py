"""Pruebas de la Ruta de estudio: lógica pura, persistencia en la dirección y recorrido de la página."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ejercicios
from ejercicios import _progreso, _ruta
from ejercicios._modelo import TEMAS

APP = str(Path(__file__).parent / "quantum_lab.py")
DISP = {t: True for t in _ruta.ORDEN}


def _filas(**kw):
    return {t: {"ejercicios": n, "resueltos": r, "por_repasar": 0, "intentos": i, "aciertos": a, "precision": (a / i if i else None), "comprobables": n}
            for t, (n, r, i, a) in kw.items()}


def test_estructura_consistente():
    assert _ruta.validar_estructura(TEMAS) == []
    assert {e.tema for e in ejercicios.EJERCICIOS} <= set(_ruta.ORDEN)


def test_validador_detecta_problemas(monkeypatch):
    monkeypatch.setattr(_ruta, "ORDEN", ("bohr", "fotoelectrico") + _ruta.ORDEN[2:])
    assert any("prerrequisito" in p for p in _ruta.validar_estructura(TEMAS))


def test_requeridos_redondea_hacia_arriba():
    assert [_ruta.requeridos(n) for n in (0, 1, 2, 4, 5, 13)] == [0, 1, 2, 3, 4, 10]


def test_pasos_y_no_aplica():
    est = _ruta.evaluar(set(), _filas(caja=(7, 0, 0, 0)), {**DISP, "hidrogeno": False})
    assert est["caja"].pasos == {"teoria": "pendiente", "ejercicios": "pendiente", "mini": "pendiente"}
    assert est["hidrogeno"].pasos["teoria"] == "no aplica"
    assert est["fotoelectrico"].pasos["ejercicios"] == "no aplica"      # sin ejercicios en las filas
    assert not est["caja"].completo


def test_tema_completo_con_todo_hecho():
    marcas = {_ruta.marca_teoria("caja"), _ruta.marca_mini("caja")}
    est = _ruta.evaluar(marcas, _filas(caja=(4, 3, 0, 0)), DISP)
    assert est["caja"].completo and est["caja"].hechos == 3
    est2 = _ruta.evaluar(marcas, _filas(caja=(4, 2, 0, 0)), DISP)
    assert not est2["caja"].completo and est2["caja"].siguiente_paso == "ejercicios"


def test_sugerencia_prioriza_el_tema_debil():
    est = _ruta.evaluar(set(), _filas(oscilador=(13, 1, 5, 1), caja=(7, 0, 4, 3)), DISP)
    s = _ruta.siguiente(est)
    assert (s.tema, s.paso) == ("oscilador", "ejercicios")


def test_sugerencia_sin_actividad_y_con_avance():
    est = _ruta.evaluar(set(), {}, DISP)
    assert _ruta.siguiente(est).tema == "fotoelectrico"
    marcas = {_ruta.marca_teoria("fotoelectrico"), _ruta.marca_mini("fotoelectrico"), _ruta.marca_teoria("ondas"), _ruta.marca_mini("ondas")}
    est = _ruta.evaluar(marcas, _filas(fotoelectrico=(1, 1, 0, 0), ondas=(2, 2, 0, 0)), DISP)
    s = _ruta.siguiente(est)
    assert s.tema in ("bohr", "operadores")                              # los dos con prerrequisitos cumplidos
    assert est["bohr"].completo is False


def test_ruta_completada():
    marcas = set(_ruta.todas_las_marcas())
    filas = {t: {"ejercicios": 2, "resueltos": 2, "por_repasar": 0, "intentos": 0, "aciertos": 0, "precision": None, "comprobables": 2} for t in _ruta.ORDEN}
    assert _ruta.siguiente(_ruta.evaluar(marcas, filas, DISP)).tema is None


def test_prerrequisitos_flojos():
    est = _ruta.evaluar(set(), _filas(caja=(7, 0, 4, 1)), DISP)
    flojos = dict(_ruta.prerrequisitos_flojos("oscilador", est))
    assert "caja" in flojos and "precisión" in flojos["caja"]
    assert _ruta.prerrequisitos_flojos("ondas", est) == []


def test_marcas_viajan_en_la_url_y_en_la_copia():
    marcas = {_ruta.marca_teoria("caja"), _ruta.marca_mini("oscilador")}
    codigo = _progreso.codificar(marcas, _ruta.todas_las_marcas())
    assert _progreso.decodificar(codigo, _ruta.todas_las_marcas()) == marcas
    datos = _progreso.a_json(set(), ejercicios.IDS, ruta=marcas)
    assert _progreso.leer_copia(datos, ejercicios.IDS, _ruta.todas_las_marcas())["ruta"] == marcas
    assert _progreso.leer_copia(datos, ejercicios.IDS)["ruta"] == set()    # sin universo válido no se acepta nada


def _abrir(**estado) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = "ruta"
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


def test_pagina_abre_y_marca_teoria_en_la_url():
    at = _abrir()
    assert not at.exception, [e.value for e in at.exception]
    at.checkbox(key="ru_t_caja").check().run()
    assert not at.exception, [e.value for e in at.exception]
    assert "t:caja" in at.session_state["ej_ruta"]
    assert _progreso.decodificar(at.query_params["rut"], _ruta.todas_las_marcas()) == {"t:caja"}


def test_marcas_se_recuperan_desde_la_direccion():
    codigo = _progreso.codificar({"t:bohr"}, _ruta.todas_las_marcas())
    at = AppTest.from_file(APP, default_timeout=180)
    at.query_params["rut"] = codigo
    at.query_params["sim"] = "ruta"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["ej_ruta"] == {"t:bohr"}


def test_mini_examen_aprobado_marca_el_tema():
    at = _abrir()
    at.button(key="ru_caja_mini").click().run()
    assert at.session_state["ex_fase"] == "curso" and at.session_state["ex_mini"] == "caja"
    ids = at.session_state["ex_ids"]
    assert len(ids) == _ruta.MINI_N and all(ejercicios.buscar(i).tema == "caja" for i in ids)
    for ej_id in ids:
        for p in ejercicios.buscar(ej_id).partes:
            clave = f"exm_{ej_id}_{p.clave}"
            if p.tipo == ejercicios.NUM:
                at.text_input(key=clave).set_value(f"{p.esperado:.6g}")
            else:
                at.radio(key=clave).set_value(p.opciones[int(p.esperado)])
    at.button(key="ex_entregar").click().run()
    at.button(key="ex_confirmar_si").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert "m:caja" in at.session_state["ej_ruta"]
    assert _progreso.decodificar(at.query_params["rut"], _ruta.todas_las_marcas()) >= {"m:caja"}


def test_mini_examen_en_blanco_no_marca():
    at = _abrir()
    at.button(key="ru_oscilador_mini").click().run()
    at.button(key="ex_entregar").click().run()
    at.button(key="ex_confirmar_si").click().run()
    assert "m:oscilador" not in at.session_state["ej_ruta"]


def test_inicio_muestra_la_sugerencia():
    at = AppTest.from_file(APP, default_timeout=180)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert any(b.key == "ql_abrir_ruta" for b in at.button)


def test_sin_actividad_no_hay_avisos_de_prerrequisitos():
    est = _ruta.evaluar(set(), {}, DISP)
    assert all(_ruta.prerrequisitos_flojos(t, est) == [] for t in _ruta.ORDEN)
    est = _ruta.evaluar(set(), _filas(oscilador=(13, 2, 0, 0)), DISP)
    assert [p for p, _ in _ruta.prerrequisitos_flojos("oscilador", est)] == ["caja"]
