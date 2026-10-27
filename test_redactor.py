"""
test_redactor.py — Cuaderno de informes: lectura segura de expresiones, verificación de pasos, modelo, gráficas, PDF e interfaz
=============================================================================================================================

Los valores esperados vienen de cálculos independientes (álgebra hecha a mano, CODATA, ajuste lineal exacto), no de las
funciones que se prueban.
"""

from __future__ import annotations

import time

import pytest

from redactor import _expr, _verificar
from redactor._expr import ErrorExpresion, leer_expresion
from redactor._verificar import (
    ERROR,
    INICIO,
    NO_VERIFICABLE,
    OK,
    SINTAXIS,
    verificar_pasos,
)

DATOS_FOTON = {"h": "6.626e-34", "c": "2.998e8", "lam": "500e-9"}


# =============================================================================================
# 1. Lectura segura de expresiones
# =============================================================================================
@pytest.mark.parametrize("texto", [
    "__import__('os').system('ls')", "().__class__", "x.y", "x.__class__.__bases__", "[1, 2]", "{1: 2}", "a;b", "open('f')",
    "lambda x: x", "exec(1)", "print(1)", "import os", "x$y", "`ls`", "\"a\"", "x**1000", "2^101", "1e999999999",
    "9**9**9", "9**(9**9)", "9^9^9^9", "123456789012345678", "x/0", "1/0", "",
])
def test_expresiones_peligrosas_o_inutiles_se_rechazan_rapido(texto):
    t0 = time.perf_counter()
    with pytest.raises(ErrorExpresion):
        leer_expresion(texto)
    assert time.perf_counter() - t0 < 2.0, "el rechazo debe ser inmediato (sin calcular potencias gigantes)"


def test_expresiones_normales_se_leen_bien():
    import sympy as sp
    x, a, m, hbar = sp.symbols("x a m hbar")
    assert leer_expresion("2x") == 2 * x
    assert leer_expresion("hbar^2/(2 m)") == hbar**2 / (2 * m)
    assert leer_expresion("ħ²/(2m)") == hbar**2 / (2 * m)
    assert leer_expresion("(x+1)(x-1)").expand() == x**2 - 1
    assert leer_expresion("e^(-x^2)") == sp.exp(-(x**2))
    assert leer_expresion("sqrt(2 m a)").subs({m: 2, a: 2}) == sp.sqrt(8)
    assert abs(float(leer_expresion("1.5e-30")) - 1.5e-30) < 1e-45


def test_nombres_de_varias_letras_son_un_solo_simbolo():
    """«hbar» no se debe partir en h·b·a·r (error típico de la multiplicación implícita automática)."""
    assert {s.name for s in leer_expresion("hbar omega").free_symbols} == {"hbar", "omega"}


def test_latex_de_un_desarrollo_usa_los_simbolos_de_fisica():
    assert r"\hbar" in _expr.a_latex(leer_expresion("hbar^2/(2 m)", evaluar=False))
    assert r"\pi" in _expr.a_latex(leer_expresion("2 pi r"))


# =============================================================================================
# 2. Verificación de pasos
# =============================================================================================
def _estados(lineas, datos=None):
    return [p.estado for p in verificar_pasos(lineas, datos)]


def test_derivacion_correcta_de_la_energia_de_la_caja():
    est = _estados(["E = p^2/(2 m)", "p = n pi hbar/a", "E = (n pi hbar/a)^2/(2 m)", "E = n^2 pi^2 hbar^2/(2 m a^2)"])
    # la 2.ª línea es una ley nueva (condición de frontera): no se puede comprobar, pero NO se marca como error
    assert est == [INICIO, NO_VERIFICABLE, OK, OK]


def test_factor_equivocado_se_marca_y_se_explica_con_el_despeje_correcto():
    p = verificar_pasos(["E = p^2/(2 m)", "E = p^2/m"])[1]
    assert p.estado == ERROR and "doble" in p.mensaje
    assert "2 m" in p.esperado_latex and "p^{2}" in p.esperado_latex          # E = p²/(2m), calculado por el despeje


def test_signo_equivocado_en_un_despeje():
    p = verificar_pasos(["E = h c/lam", "lam = -h c/E"])[1]
    assert p.estado == ERROR and "signo" in p.mensaje


def test_despeje_correcto_y_multiplicacion_de_ambos_lados():
    assert _estados(["E = p^2/(2 m)", "p = sqrt(2 m E)"]) == [INICIO, OK]
    assert _estados(["E = p^2/(2 m)", "2 m E = p^2"]) == [INICIO, OK]
    assert _estados(["E = h c/lam", "lam = h c/E"]) == [INICIO, OK]


def test_cadenas_de_igualdades_se_revisan_expresion_por_expresion():
    assert _estados(["x = (a+b)^2 = a^2 + 2 a b + b^2"]) == [INICIO]
    p = verificar_pasos(["x = (a+b)^2 = a^2 + b^2"])[0]
    assert p.estado == ERROR and "(a+b)^2" in p.mensaje
    assert _estados(["y = sin(x)^2 + cos(x)^2 = 1"]) == [INICIO]
    assert _estados(["y = sin(x)^2 + cos(x)^2 = 2"]) == [ERROR]


def test_expresion_sola_continua_la_anterior():
    est = _estados(["(a+b)^2", "a^2 + 2 a b + b^2", "a^2 + b^2"])
    assert est == [INICIO, OK, ERROR]


def test_numeros_con_datos_comparan_en_relativo_y_no_dan_por_buena_una_cifra_equivocada():
    """E = hc/λ con los valores de DATOS_FOTON es 3.9730e-19 J (cuenta hecha a mano: 6.626e-34·2.998e8/5e-7)."""
    bien = ["E = h c/lam", "E = h c/lam = 6.626e-34*2.998e8/(500e-9)", "E = 3.973e-19"]
    assert _estados(bien, DATOS_FOTON) == [INICIO, OK, OK]
    mal = ["E = h c/lam", "E = 3.2e-19"]
    assert _estados(mal, DATOS_FOTON) == [INICIO, ERROR]                   # 19 % de diferencia
    assert _estados(["E = h c/lam", "E = 4.9e-19"], DATOS_FOTON)[1] == ERROR
    # a escala 1e-19 la tolerancia es relativa: 3.99e-19 está a 0.4 % → pasa; 4.1e-19 está a 3 % → falla
    assert _estados(["E = h c/lam", "E = 3.99e-19"], DATOS_FOTON)[1] == OK
    assert _estados(["E = h c/lam", "E = 4.1e-19"], DATOS_FOTON)[1] == ERROR


def test_sintaxis_incorrecta_no_rompe_la_revision_de_las_demas_lineas():
    pasos = verificar_pasos(["E = p^2/(2 m", "E = 3 +", "x = 2 y"])
    assert [p.estado for p in pasos] == [SINTAXIS, SINTAXIS, INICIO]
    assert "paréntesis" in pasos[0].mensaje


def test_lineas_con_simbolos_nuevos_no_se_dan_por_erroneas():
    """Una línea que introduce símbolos nuevos puede ser una ley o un dato: se avisa, no se acusa de error."""
    assert _estados(["E = p^2/(2 m)", "E = k T"])[1] == NO_VERIFICABLE


def test_datos_mal_escritos_se_informan():
    pasos = verificar_pasos(["x = 2"], {"h": "no es un número"})
    assert pasos and pasos[0].estado == SINTAXIS and "Datos conocidos" in pasos[0].mensaje


def test_resumen_cuenta_los_estados():
    pasos = verificar_pasos(["E = p^2/(2 m)", "E = p^2/m", "p = sqrt(2 m E)"])
    r = _verificar.resumen(pasos)
    assert r[INICIO] == 1 and r[ERROR] == 1 and r[OK] == 1


def test_un_error_no_arrastra_a_las_lineas_siguientes_correctas():
    """La 3.ª línea es correcta respecto de la 1.ª aunque la 2.ª esté mal: se compara con la última línea válida."""
    est = _estados(["E = p^2/(2 m)", "E = p^2/m", "p = sqrt(2 m E)"])
    assert est == [INICIO, ERROR, OK]
    # y si el estudiante continúa desde el error, se le dice que no sigue de la línea correcta
    p = verificar_pasos(["E = p^2/(2 m)", "E = p^2/m", "p = sqrt(m E)"])[2]
    assert p.estado == ERROR and "última línea correcta" in p.mensaje


def test_verificacion_es_reproducible():
    lineas = ["E = p^2/(2 m)", "E = p^2/m", "p = sqrt(2 m E)"]
    assert verificar_pasos(lineas) == verificar_pasos(lineas)


# =============================================================================================
# 2. Modelo, archivo .json
# =============================================================================================
import json

from redactor import _graficas, _modelo, _pdf, _simuladores, _talleres
from redactor._modelo import ErrorDocumento


def _doc_completo():
    d = _modelo.documento_vacio("Prueba ñ", "Ana")
    for t in _modelo.TIPOS:
        d["bloques"].append(_modelo.nuevo_bloque(t))
    return d


def test_json_ida_y_vuelta_conserva_todo():
    d = _doc_completo()
    d["bloques"][2]["datos"]["latex"] = r"\frac{a}{b}"
    d2 = _modelo.desde_json(_modelo.a_json(d))
    assert d2["titulo"] == "Prueba ñ" and d2["autor"] == "Ana"
    assert [b["datos"] for b in d2["bloques"]] == [b["datos"] for b in d["bloques"]]
    assert [b["tipo"] for b in d2["bloques"]] == list(_modelo.TIPOS)


@pytest.mark.parametrize("contenido", [b"no es json", b"[]", b'{"formato": "otro"}', b'{"formato": "quantum-lab-cuaderno", "version": 99, "bloques": []}',
                                      b'{"formato": "quantum-lab-cuaderno", "version": 1, "bloques": [{"tipo": "inventado", "datos": {}}]}',
                                      b'{"formato": "quantum-lab-cuaderno", "version": 1, "bloques": "x"}', b"\xff\xfe", b"x" * 2_100_000])
def test_json_malo_se_rechaza_con_mensaje(contenido):
    with pytest.raises(ErrorDocumento) as e:
        _modelo.desde_json(contenido)
    assert str(e.value)


def test_json_descarta_campos_desconocidos_y_tipos_incorrectos():
    base = {"formato": "quantum-lab-cuaderno", "version": 1, "titulo": "t", "autor": "",
            "bloques": [{"tipo": "texto", "datos": {"texto": "hola", "extra": "x"}}]}
    d = _modelo.desde_json(json.dumps(base))
    assert d["bloques"][0]["datos"] == {"texto": "hola"}
    base["bloques"][0]["datos"]["texto"] = 5
    with pytest.raises(ErrorDocumento):
        _modelo.desde_json(json.dumps(base))


def test_json_demasiados_bloques():
    base = {"formato": "quantum-lab-cuaderno", "version": 1, "bloques": [{"tipo": "texto", "datos": {}}] * 301}
    with pytest.raises(ErrorDocumento):
        _modelo.desde_json(json.dumps(base))


# =============================================================================================
# 3. Gráficas
# =============================================================================================
def test_ajuste_lineal_recta_exacta():
    a = _graficas.ajuste_lineal([0, 1, 2, 3], [1, 3, 5, 7])           # y = 2x + 1
    assert a["pendiente"] == pytest.approx(2.0) and a["ordenada"] == pytest.approx(1.0) and a["r2"] == pytest.approx(1.0)


def test_ajuste_lineal_con_ruido_valor_hecho_a_mano():
    # x = 1,2,3,4 ; y = 2,4,5,8: medias 2.5 y 4.75; Sxx = 5, Sxy = 9.5 -> m = 1.9, b = 4.75 - 1.9*2.5 = 0
    # ajustados 1.9, 3.8, 5.7, 7.6 -> SSres = 0.01+0.04+0.49+0.16 = 0.70 ; Syy = 18.75 -> R² = 1 - 0.70/18.75
    a = _graficas.ajuste_lineal([1, 2, 3, 4], [2, 4, 5, 8])
    assert a["pendiente"] == pytest.approx(1.9) and a["ordenada"] == pytest.approx(0.0, abs=1e-12)
    assert a["r2"] == pytest.approx(1 - 0.70 / 18.75)


def test_ajuste_lineal_rechaza_x_constante():
    with pytest.raises(_graficas.ErrorGrafica):
        _graficas.ajuste_lineal([2, 2, 2], [1, 2, 3])


@pytest.mark.parametrize("texto,esperado", [("1 2\n2 4", [[1, 2], [2, 4]]), ("1;2\n3;4", [[1, 2], [3, 4]]), ("1,5 2,5\n2 3", [[1.5, 2.5], [2, 3]]),
                                              ("# c\n1 2\n\n3 4", [[1, 2], [3, 4]]), ("1e-3 2\n2e-3 3", [[1e-3, 2], [2e-3, 3]])])
def test_leer_tabla_formatos(texto, esperado):
    assert _graficas.leer_tabla(texto).ravel().tolist() == pytest.approx([v for f in esperado for v in f])


@pytest.mark.parametrize("texto", ["", "1 2", "1 2\n3", "1 2\n3 x", "1 2 3 4\n5 6 7 8", "1 2\n3 4 5"])
def test_leer_tabla_errores(texto):
    with pytest.raises(_graficas.ErrorGrafica):
        _graficas.leer_tabla(texto)


def test_grafica_funcion_valores_y_errores():
    curvas = _graficas.evaluar_funciones("2*x + 1", "x", 0, 4, {})
    assert curvas, "debe devolver curvas"
    fig = _graficas.grafica_funcion("sin(n x)", "x", 0, 3.14, "n = 2")
    assert _graficas.a_png(fig).startswith(b"\x89PNG")
    for malo in (("__import__('os')", "x", 0, 1, ""), ("x", "x", 1, 1, ""), ("y + 1", "x", 0, 1, ""), ("x", "x", 0, 1, "n = ")):
        with pytest.raises((_graficas.ErrorGrafica, ErrorExpresion)):
            _graficas.grafica_funcion(*malo)


def test_grafica_datos_devuelve_ajuste():
    fig, ajuste = _graficas.grafica_datos("0 1\n1 3\n2 5\n3 7", "ajuste")
    assert ajuste["pendiente"] == pytest.approx(2.0)
    assert _graficas.a_png(fig).startswith(b"\x89PNG")
    _, sin = _graficas.grafica_datos("0 1\n1 3", "puntos")
    assert sin is None


# =============================================================================================
# 4. Simuladores y talleres
# =============================================================================================
def test_simuladores_todos_construyen_y_rechazan_valores_invalidos():
    for k in _simuladores.SIMULADORES:
        inf = _simuladores.construir(k, {})
        assert inf.resultados and inf.figuras


def test_simulador_caja_coincide_con_el_calculo_a_mano():
    # E1 = h²/(8 m L²) con CODATA 2018 (h, mₑ, e) y L = 1 nm: 0.37603 eV
    h, me, q = 6.62607015e-34, 9.1093837015e-31, 1.602176634e-19
    esperado = h ** 2 / (8 * me * (1e-9) ** 2) / q
    inf = _simuladores.construir("caja", {})
    assert float(inf.resultados[0][1]) == pytest.approx(esperado, rel=1e-6)
    inf3 = _simuladores.construir("caja", {"n": 3})
    assert float(inf3.resultados[0][1]) == pytest.approx(9 * esperado, rel=1e-6)


def test_talleres_calificacion_del_bloque():
    cat = _talleres.catalogo()
    assert cat
    tid = cat[0][0]
    qs = _talleres.preguntas(tid, True, "1")
    datos = {"taller": tid, "original": True, "semilla": "1", "pregunta": qs[0].id, "respuestas": {}, "incluir_solucion": False}
    cal = _talleres.calificar_bloque(datos)
    assert cal["puntos"] == 0 and cal["maximo"] > 0
    with pytest.raises(ValueError):
        _talleres.preguntas("no_existe", True, "1")


# =============================================================================================
# 5. PDF
# =============================================================================================
def test_pdf_es_valido_y_contiene_el_texto():
    d = _doc_completo()
    d["bloques"][1]["datos"]["texto"] = "Resultado sobre la energía $E=h\\nu$"
    d["bloques"][3]["datos"]["lineas"] = "E = p^2/(2 m)\nE = p^2/m"
    d["bloques"][3]["datos"]["marcas"] = True
    pdf = _pdf.pdf_cuaderno(d)
    assert pdf.startswith(b"%PDF-") and len(pdf) > 5000
    assert len(_pdf.paginas_png(d)) >= 1


def test_bloque_roto_no_cancela_el_pdf_y_se_informa():
    d = _modelo.documento_vacio("x", "")
    d["bloques"] = [_modelo.nuevo_bloque("texto", {"texto": "ok"}), _modelo.nuevo_bloque("ecuacion", {"latex": r"\frac{a"}),
                    _modelo.nuevo_bloque("grafica_funcion", {"expresiones": "__import__('os')"})]
    assert _pdf.pdf_cuaderno(d).startswith(b"%PDF-")
    assert [i for i, _ in _pdf.problemas_del_documento(d)] == [2, 3]


def test_formula_valida():
    assert _pdf.formula_valida(r"\frac{a}{b}") and not _pdf.formula_valida(r"\frac{a")


# =============================================================================================
# 6. Interfaz (AppTest)
# =============================================================================================
def _pagina():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(__import__("pathlib").Path(__file__).parent / "quantum_lab.py"), default_timeout=90)
    at.session_state["ql_pagina"] = "redactor"
    at.run()
    return at


def _agregar(at, tipo):
    at.selectbox(key="rd_tipo_nuevo").set_value(tipo).run()
    at.button(key="rd_agregar").click().run()


def test_pagina_agrega_los_nueve_tipos_sin_errores():
    at = _pagina()
    assert not at.exception
    for t in _modelo.TIPOS:
        _agregar(at, t)
        assert not at.exception, t
    assert [b["tipo"] for b in at.session_state["rd_doc"]["bloques"]] == list(_modelo.TIPOS)


def test_pagina_marca_un_paso_con_error():
    at = _pagina()
    _agregar(at, "desarrollo")
    bid = at.session_state["rd_doc"]["bloques"][0]["id"]
    at.text_area(key=f"rd_{bid}_lineas").set_value("E = p^2/(2 m)\nE = p^2/m").run()
    assert not at.exception
    textos = " ".join(m.value for m in at.markdown)
    assert ":red[**✗**]" in textos and ":red[1 con error]" in textos and ":gray[**·**]" in textos


def test_pagina_mover_duplicar_borrar():
    at = _pagina()
    _agregar(at, "titulo")
    _agregar(at, "texto")
    ids = [b["id"] for b in at.session_state["rd_doc"]["bloques"]]
    at.button(key=f"rd_{ids[1]}_up").click().run()
    assert [b["id"] for b in at.session_state["rd_doc"]["bloques"]] == [ids[1], ids[0]]
    at.button(key=f"rd_{ids[0]}_dup").click().run()
    assert len(at.session_state["rd_doc"]["bloques"]) == 3
    at.button(key=f"rd_{ids[0]}_del").click().run()
    assert len(at.session_state["rd_doc"]["bloques"]) == 2 and not at.exception


def test_pagina_plantillas_y_pdf():
    at = _pagina()
    at.button(key="rd_pl_lab").click().run()
    assert not at.exception and len(at.session_state["rd_doc"]["bloques"]) > 5
    at.button(key="rd_pdf").click().run()
    assert at.session_state["rd_pdf_bytes"].startswith(b"%PDF-")
    at.button(key="rd_pl_taller").click().run()
    assert not at.exception and any(b["tipo"] == "taller" for b in at.session_state["rd_doc"]["bloques"])
