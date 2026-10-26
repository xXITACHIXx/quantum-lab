"""
Pruebas de las mejoras pedagógicas: laboratorio inverso, instrumentos, informes y preguntas de predicción de los seis
simuladores.

Los valores esperados vienen de constantes CODATA escritas aquí (no de las constantes del programa) y de derivaciones
a mano (leyes de escala, ley de Rydberg, E₁ = 0.376030 eV para un electrón en 1 nm), no de repetir la función evaluada.
"""
import csv
import dataclasses
import io
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import efecto_fotoelectrico as foto
import informes
import instrumentos
import inverso
import modelo_bohr as bohr
import oscilador_armonico as osc
import particula_caja as caja
import particula_esfera as esf
import predice
import principio_incertidumbre as inc

H = 6.62607015e-34
C = 299792458.0
Q = 1.602176634e-19
RH = 1.0967758e7                      # constante de Rydberg del hidrógeno (1/m), valor tabulado
RINF = 1.0973731568e7                 # constante de Rydberg con núcleo infinitamente pesado (1/m)
APP = str(Path(__file__).parent / "quantum_lab.py")


# ---------------------------------------------------------------------------------------------
# Parámetros de prueba por simulador
# ---------------------------------------------------------------------------------------------
def _p_caja():
    return caja.validar_parametros_caja(2, 1.0, 1.0, "SI", 2000)


def _p_osc():
    return osc.validar_parametros_oscilador(1, 1.0, 1.0e15, "SI", 9.0, 3001)


def _p_foto():
    return foto.validar_parametros_foto("Cesio", 2.5, "longitud", 400.0, 1.0, 10.0)


def _p_bohr():
    return bohr.Transicion(3, 2, "H", False)


def _p_esf():
    return esf.validar_parametros_esfera(2, 1, 1.0, "SI", 90, "densidad", "lobulos", 0.4, "Viridis")


def _p_inc():
    return inc.validar_paquete("gaussiano", 1.0, 5.0, 2.0, 6.0)


SIMULADORES = {
    "caja": (caja, _p_caja, {"duplicar_a": 0.25, "duplicar_n": 4.0, "duplicar_masa": 0.5, "lambda_duplicar_a": 2.0}),
    "osc": (osc, _p_osc, {"duplicar_omega": 2.0, "duplicar_masa_energia": 1.0, "duplicar_masa_x0": 2 ** -0.5, "espaciado": 1.0}),
    "foto": (foto, _p_foto, {"intensidad_corriente": 2.0, "intensidad_kmax": 1.0, "frecuencia_fotones": 2.0, "phi_umbral": 2.0}),
    "bohr": (bohr, _p_bohr, {"energia_2n": 0.25, "radio_2n": 4.0, "carga_nuclear": 4.0}),
    "esf": (esf, _p_esf, {"nodales_2l": 2.0, "simetria_m": 1.0}),
    "inc": (inc, _p_inc, {"mitad_delta_p": 2.0, "mitad_producto": 1.0}),
}


# =============================================================================================
# 1. Preguntas de predicción
# =============================================================================================
@pytest.mark.parametrize("clave", SIMULADORES)
def test_las_preguntas_siguen_las_leyes_de_escala(clave):
    modulo, parametros, esperado = SIMULADORES[clave]
    p = parametros()
    assert {q.id for q in modulo.PREGUNTAS_PREDICE} == set(esperado)
    for q in modulo.PREGUNTAS_PREDICE:
        ref, mod, unidad = q.calcular(p)
        assert mod / ref == pytest.approx(esperado[q.id], rel=max(q.tol, 1e-9)), q.id
        assert predice.validar_pregunta(q, p) == [], q.id
        res = predice.evaluar(q, p, None)
        assert q.opciones[res.correcta].razon == pytest.approx(esperado[q.id], rel=1e-9), q.id


def test_pregunta_sin_sentido_bajo_el_umbral_se_explica():
    p = foto.validar_parametros_foto("Cesio", 2.5, "longitud", 900.0, 1.0, 10.0)      # hν = 1.38 eV < 2.14 eV
    q = next(x for x in foto.PREGUNTAS_PREDICE if x.id == "intensidad_corriente")
    with pytest.raises(ValueError, match="umbral"):
        predice.evaluar(q, p, 0)


def test_pregunta_de_l_cero_no_tiene_sentido():
    p = esf.validar_parametros_esfera(0, 0, 1.0, "SI", 90, "densidad", "lobulos", 0.4, "Viridis")
    q = next(x for x in esf.PREGUNTAS_PREDICE if x.id == "nodales_2l")
    with pytest.raises(ValueError):
        predice.evaluar(q, p, 0)


def test_valores_independientes_de_la_caja_en_el_experimento():
    # Electrón en 1 nm, n = 2: E = 4·0.376030 eV; al duplicar a → E/4
    q = next(x for x in caja.PREGUNTAS_PREDICE if x.id == "duplicar_a")
    ref, mod, unidad = q.calcular(_p_caja())
    assert unidad == "eV"
    assert ref == pytest.approx(4 * 0.376030, rel=1e-5)
    assert mod == pytest.approx(ref / 4, rel=1e-12)


# =============================================================================================
# 2. Laboratorio inverso
# =============================================================================================
@pytest.mark.parametrize("modulo", [caja, osc, foto, bohr, inc, esf], ids=lambda m: m.__name__)
def test_retos_bien_construidos(modulo):
    assert modulo.RETOS_INVERSOS
    for r in modulo.RETOS_INVERSOS:
        assert inverso.validar_reto(r) == [], r.id


@pytest.mark.parametrize("n", [1, 2, 5, 10])
def test_caja_toda_la_familia_a_igual_n_por_medio_nm_es_solucion(n):
    r = caja.RETOS_INVERSOS[0]
    assert inverso.evaluar_intento(r, {"n": n, "a": 0.5 * n}).nivel == "exacta"


def test_caja_energia_se_verifica_con_E1_tabulada():
    r = caja.RETOS_INVERSOS[0]
    # E(n=1, a=0.5 nm) = 0.376030 eV · (1/0.5)² = 1.504120 eV (valor tabulado de E₁ para 1 nm)
    assert inverso.evaluar_intento(r, {"n": 1, "a": 0.5}).obtenido == pytest.approx(0.376030 * 4, rel=1e-5)
    assert inverso.evaluar_intento(r, {"n": 1, "a": 1.0}).nivel == "incorrecta"
    assert inverso.evaluar_intento(r, {"n": 1, "a": 0.497}).nivel == "aproximada"
    mal = inverso.evaluar_intento(r, {"n": 1, "a": 1.0})
    assert "menor" in mal.mensaje and "0.25" in mal.mensaje


def test_umbral_del_cesio():
    r = next(x for x in foto.RETOS_INVERSOS if x.id == "foto_umbral")
    nu0 = 2.14 * Q / H / 1e14                                    # Φ/h con Φ = 2.14 eV
    assert r.objetivo == pytest.approx(nu0, rel=1e-9)
    assert inverso.evaluar_intento(r, {"nu": nu0}).nivel == "exacta"
    debajo = inverso.evaluar_intento(r, {"nu": 5.0})
    assert debajo.nivel == "incorrecta" and "No hay emisión" in debajo.mensaje
    assert inverso.evaluar_intento(r, {"nu": 5.3}).nivel == "aproximada"
    assert "mayor" in inverso.evaluar_intento(r, {"nu": 7.0}).mensaje
    assert not r.mostrar_objetivo


def test_kmax_del_zinc():
    r = next(x for x in foto.RETOS_INVERSOS if x.id == "foto_kmax")
    lam = H * C / ((4.30 + 0.5) * Q) * 1e9                      # λ = hc/(φ + K)
    assert inverso.evaluar_intento(r, {"lam": lam}).nivel == "exacta"
    assert "No hay emisión" in inverso.evaluar_intento(r, {"lam": 300.0}).mensaje        # 4.13 eV < 4.30 eV


def test_bohr_dos_soluciones_equivalentes():
    r = bohr.RETOS_INVERSOS[0]
    lam_rydberg = 1.0 / (RH * (1 / 4 - 1 / 16)) * 1e9              # ley de Rydberg con el valor tabulado
    assert r.objetivo == pytest.approx(lam_rydberg, rel=2e-5)
    assert inverso.evaluar_intento(r, {"ni": 4, "nf": 2}).nivel == "exacta"
    assert inverso.evaluar_intento(r, {"ni": 2, "nf": 4}).nivel == "exacta"        # absorción: misma energía
    assert inverso.evaluar_intento(r, {"ni": 3, "nf": 2}).nivel == "incorrecta"
    with pytest.raises(ValueError, match="distintos"):
        inverso.evaluar_intento(r, {"ni": 2, "nf": 2})


@pytest.mark.parametrize("n,nu13", [(0, 5.25), (1, 1.75), (3, 0.75)])
def test_oscilador_una_frecuencia_por_nivel(n, nu13):
    r = osc.RETOS_INVERSOS[0]
    e = (n + 0.5) * H * nu13 * 1e13 / Q                          # Eₙ = (n + ½)hν en eV
    assert e == pytest.approx(0.10856, rel=2e-5)
    assert inverso.evaluar_intento(r, {"n": n, "nu": nu13}).nivel == "exacta"
    assert inverso.evaluar_intento(r, {"n": n, "nu": 2 * nu13}).nivel == "incorrecta"


def test_incertidumbre_ancho_para_delta_k():
    r = inc.RETOS_INVERSOS[0]
    assert inverso.evaluar_intento(r, {"sigma": 2.0}).nivel == "exacta"                # Δk = 1/(2σ) = 0.25
    assert inverso.evaluar_intento(r, {"sigma": 1.0}).nivel == "incorrecta"


def test_entradas_invalidas_de_los_retos():
    r = caja.RETOS_INVERSOS[0]
    for malo in ({"n": 0, "a": 1.0}, {"n": 1, "a": 0.0}, {"n": 1, "a": float("nan")}, {"n": 1.5, "a": 1.0},
                 {"n": 1}, {"n": "x", "a": 1.0}, {"n": 1, "a": float("inf")}, {"n": 100, "a": 1.0}):
        with pytest.raises(ValueError):
            inverso.evaluar_intento(r, malo)


def test_clasificacion_por_tolerancias():
    r = caja.RETOS_INVERSOS[0]
    v = inverso.evaluar_intento(r, {"n": 1, "a": 0.5})
    assert v.nivel == "exacta" and v.error_relativo <= r.tol_exacta
    assert len(v.verificacion) == 3 and "Error relativo" in v.verificacion[2]


def test_reto_mal_construido_se_detecta():
    r = replace(caja.RETOS_INVERSOS[0], tol_exacta=0.5, tol_aprox=0.1, pistas=())
    problemas = inverso.validar_reto(r)
    assert any("tolerancias" in p.lower() for p in problemas) and any("pistas" in p.lower() for p in problemas)
    assert inverso.validar_reto(replace(caja.RETOS_INVERSOS[0], objetivo=0.0))


# =============================================================================================
# 3. Instrumentos
# =============================================================================================
def test_cursor_interpola_y_rechaza_fuera_de_dominio():
    x = np.linspace(0, 2, 5)
    assert instrumentos.leer_valor(x, x ** 2, 1.0) == pytest.approx(1.0)
    assert instrumentos.leer_valor(x, 2 * x, 0.3) == pytest.approx(0.6)            # lineal: interpolación exacta
    for fuera in (-0.1, 2.1, float("nan")):
        with pytest.raises(ValueError):
            instrumentos.leer_valor(x, x, fuera)
    with pytest.raises(ValueError):
        instrumentos.leer_valor(x, x[:3], 1.0)


@pytest.mark.parametrize("n", [1, 3, 8])
def test_probabilidad_en_intervalo_frente_a_la_integral_exacta(n):
    a = 1e-9
    x = np.linspace(0, a, 4001)
    rho = 2 / a * np.sin(n * np.pi * x / a) ** 2
    assert instrumentos.probabilidad_intervalo(x, rho, 0.0, a) == pytest.approx(1.0, abs=1e-6)
    # Por simetría de sen², la mitad de la caja contiene exactamente 1/2 (referencia independiente)
    assert instrumentos.probabilidad_intervalo(x, rho, 0.0, a / 2) == pytest.approx(0.5, abs=1e-6)
    pn = instrumentos.probabilidad_intervalo(x, rho, 0.13 * a, 0.61 * a)
    pe = instrumentos.probabilidad_caja_exacta(n, a, 0.13 * a, 0.61 * a)
    assert abs(pn - pe) < 1e-6


def test_probabilidad_de_un_lobulo_es_la_n_esima_parte():
    # Cada máximo de |ψₙ|² está en medio de un lóbulo y cada lóbulo contiene 1/n de la probabilidad.
    for n in (2, 5):
        assert instrumentos.probabilidad_caja_exacta(n, 1.0, 0.0, 1.0 / n) == pytest.approx(1.0 / n, rel=1e-12)


def test_intervalo_invalido():
    x = np.linspace(0, 1, 101)
    for a, b in ((0.5, 0.5), (0.6, 0.4), (-0.1, 0.5), (0.2, 1.5), (float("nan"), 0.5)):
        with pytest.raises(ValueError):
            instrumentos.probabilidad_intervalo(x, x, a, b)
    with pytest.raises(ValueError):
        instrumentos.probabilidad_caja_exacta(0, 1.0, 0.0, 0.5)


def test_foton_caja_6_a_3_para_5_nm():
    # E_n = n²·E₁ con E₁ = 0.376030 eV·(1 nm/a)² ; a = 5 nm → E₁ = 0.0150412 eV; ΔE = (36 − 9)E₁ = 0.406112 eV
    a, m = 5e-9, 9.1093837015e-31
    e = lambda n: n ** 2 * math.pi ** 2 * 1.054571817e-34 ** 2 / (2 * m * a ** 2)   # noqa: E731
    f = instrumentos.foton_entre_niveles(e(6), e(3))
    assert f["tipo"] == "Emisión"
    assert f["energia_ev"] == pytest.approx(27 * 0.376030 / 25, rel=1e-5)
    assert f["longitud_nm"] == pytest.approx(1239.84198 / (27 * 0.376030 / 25), rel=1e-5)
    assert instrumentos.foton_entre_niveles(e(3), e(6))["tipo"] == "Absorción"


def test_foton_lyman_alfa():
    # Lyman α (2 → 1) con niveles de R∞ (13.605693 eV): λ = 1/(R∞·(1 − 1/4)) = 121.502 nm
    f = instrumentos.foton_entre_niveles(-13.605693 / 4 * Q, -13.605693 * Q)
    assert f["longitud_nm"] == pytest.approx(1 / (RINF * 0.75) * 1e9, rel=1e-6)
    assert f["region"].startswith("Ultravioleta")


def test_foton_niveles_iguales_o_no_finitos():
    with pytest.raises(ValueError):
        instrumentos.foton_entre_niveles(1e-19, 1e-19)
    with pytest.raises(ValueError):
        instrumentos.foton_entre_niveles(float("nan"), 1e-19)


def test_comparar():
    c = instrumentos.comparar(1.1, 1.0)
    assert c["absoluta"] == pytest.approx(0.1) and c["relativa"] == pytest.approx(0.1)
    assert instrumentos.comparar(-0.5, -1.0)["relativa"] == pytest.approx(0.5)
    with pytest.raises(ValueError):
        instrumentos.comparar(1.0, 0.0)


def test_probabilidad_angular_normalizada_y_aproximacion_local():
    f = lambda th, ph: esf.densidad_probabilidad(2, 1, th, ph)              # noqa: E731
    assert instrumentos.probabilidad_angular(f, 0.0, math.pi, 0.0, 2 * math.pi) == pytest.approx(1.0, abs=1e-6)
    # Región pequeña: P ≈ |Y|²·ΔΩ
    t, ph, d = 1.0, 0.5, 0.02
    exacta = instrumentos.probabilidad_angular(f, t - d / 2, t + d / 2, ph - d / 2, ph + d / 2)
    aprox = float(f(t, ph)) * math.sin(t) * d * d
    assert exacta == pytest.approx(aprox, rel=1e-3)
    # Simetría de la mitad: |Y₂¹|² solo depende de θ → mitad de φ da la mitad
    assert instrumentos.probabilidad_angular(f, 0.0, math.pi, 0.0, math.pi) == pytest.approx(0.5, abs=1e-6)
    for malo in ((0.5, 0.2, 0, 1), (-0.1, 0.5, 0, 1), (0.1, 0.5, 1, 0.5), (0.1, 0.5, 0, 7.0)):
        with pytest.raises(ValueError):
            instrumentos.probabilidad_angular(f, *malo)


# =============================================================================================
# 4. Informes
# =============================================================================================
def _informes_de_prueba():
    pc = _p_caja()
    po = _p_osc()
    pf = _p_foto()
    pb = _p_bohr()
    pe = _p_esf()
    pi = _p_inc()
    return {
        "caja": caja.informe_estado(pc, caja.calcular_estado_individual(pc), "Conclusión de prueba."),
        "osc": osc.informe_estado(po, osc.calcular_estado(po), "Conclusión de prueba."),
        "foto": foto.informe_experimento(pf, foto.calcular_foto(pf), "Conclusión de prueba."),
        "bohr": bohr.informe_transicion(pb, bohr.calcular_transicion(pb), "Conclusión de prueba."),
        "esf": esf.informe_estado_angular(pe, "Conclusión de prueba."),
        "inc": inc.informe_paquete(pi, inc.calcular_paquete(pi), "Conclusión de prueba."),
    }


@pytest.fixture(scope="module")
def informes_listos():
    return _informes_de_prueba()


@pytest.mark.parametrize("clave", list(SIMULADORES))
def test_pdf_valido_y_con_contenido(informes_listos, clave):
    inf = informes_listos[clave]
    pdf = informes.pdf_informe(inf)
    assert pdf.startswith(b"%PDF-") and pdf.rstrip().endswith(b"%%EOF") and len(pdf) > 20000
    assert pdf.count(b"/Type /Page\n") + pdf.count(b"/Type /Page ") >= 1
    pypdf = pytest.importorskip("pypdf")
    lector = pypdf.PdfReader(io.BytesIO(pdf))
    texto = " ".join(pagina.extract_text() for pagina in lector.pages)
    for esperado in ("Objetivo", "Modelo teórico", "Resultados calculados por el simulador", "Conclusiones del estudiante",
                     "Conclusión de prueba."):
        assert esperado in texto, (clave, esperado)
    assert "no son mediciones experimentales" in texto
    assert inf.resultados[0][0] in texto


@pytest.mark.parametrize("clave", list(SIMULADORES))
def test_csv_se_puede_leer_de_vuelta(informes_listos, clave):
    inf = informes_listos[clave]
    crudo = informes.csv_informe(inf)
    assert crudo.startswith("﻿".encode())
    filas = list(csv.reader(io.StringIO(crudo.decode("utf-8-sig"))))
    assert filas[0] == ["Sección", "Magnitud", "Valor", "Unidad"]
    resultados = [f for f in filas if f[0].startswith("Resultados")]
    assert len(resultados) == len(inf.resultados)
    parametros = [f for f in filas if f[0].startswith("Parámetros")]
    assert len(parametros) == len(inf.parametros)


def test_el_informe_de_la_caja_tiene_la_energia_correcta(informes_listos):
    # Electrón en 1 nm, n = 2: E = 4·0.376030 eV (valor tabulado de E₁)
    inf = informes_listos["caja"]
    energia = next(float(v) for m, v, u in inf.resultados if m.startswith("Energía") and u == "eV")
    assert energia == pytest.approx(4 * 0.376030, rel=1e-5)
    assert next(v for m, v, u in inf.resultados if m.startswith("Nodos")) == "1"


def test_informe_distingue_calculado_de_escrito(informes_listos):
    pypdf = pytest.importorskip("pypdf")
    inf = informes_listos["caja"]
    con = " ".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(informes.pdf_informe(inf))).pages)
    sin = " ".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(informes.pdf_informe(replace(inf, conclusiones="")))).pages)
    assert "Conclusión de prueba." in con and "Conclusión de prueba." not in sin
    assert "Conclusiones del estudiante" in sin                                     # la sección existe aunque esté en blanco


def test_informe_incompleto_se_rechaza():
    base = informes.Informe("T", "S", "O", "M", parametros=[("a", "1", "")], resultados=[("b", "2", "")])
    informes.validar(base)
    for malo in (replace(base, titulo=""), replace(base, resultados=[]), replace(base, parametros=[]), replace(base, objetivo=""),
                 replace(base, resultados=[("b", "2")])):
        with pytest.raises(ValueError):
            informes.pdf_informe(malo)
        with pytest.raises(ValueError):
            informes.csv_informe(malo)


def test_ecuacion_invalida_no_rompe_el_informe():
    inf = informes.Informe("T", "S", "O", "M", ecuaciones=[r"\dfrac{rota"], parametros=[("a", "1", "")], resultados=[("b", "2", "")])
    assert informes.pdf_informe(inf).startswith(b"%PDF-")


def test_informe_de_un_experimento_de_prediccion():
    q = caja.PREGUNTAS_PREDICE[0]
    p = _p_caja()
    res = predice.evaluar(q, p, 0)
    datos = {"simulador": "Caja", "modelo": "Pozo infinito.", "parametros": [("n", "2", "")], "ecuaciones": []}
    inf = predice.informe_experimento(q, res, datos, "Me equivoqué.")
    assert dict((m, v) for m, v, _ in inf.resultados)["Comparación"] == "La predicción no coincide"
    assert informes.pdf_informe(inf).startswith(b"%PDF-")


# =============================================================================================
# 5. Interfaz (AppTest)
# =============================================================================================
PREFIJOS = {"caja": "caja", "oscilador": "osc", "esfera": "esf", "fotoelectrico": "foto", "bohr": "bohr", "incertidumbre": "inc"}
RETOS_UI = {"caja": ("caja_energia", {"n": 2, "a": 1.0}), "oscilador": ("osc_energia", {"n": 1, "nu": 1.75}),
            "fotoelectrico": ("foto_umbral", {"nu": 5.1745}), "bohr": ("bohr_lambda", {"ni": 4, "nf": 2}),
            "incertidumbre": ("inc_ancho", {"sigma": 2.0})}


def _abrir(pagina, **estado):
    at = AppTest.from_file(APP, default_timeout=240)
    at.session_state["ql_pagina"] = pagina
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    return at


@pytest.mark.parametrize("pagina", list(PREFIJOS))
def test_cada_simulador_tiene_las_pestanas_nuevas_y_las_pruebas_al_final(pagina):
    at = _abrir(pagina)
    assert not at.exception, [e.value for e in at.exception]
    etiquetas = [t.label for t in at.tabs]
    assert "Predice y experimenta" in etiquetas and etiquetas[-1] == "Pruebas numéricas"
    assert "Laboratorio inverso" in etiquetas


@pytest.mark.parametrize("pagina", list(PREFIJOS))
def test_experimento_de_prediccion_en_cada_simulador(pagina):
    pre = PREFIJOS[pagina]
    modulo = SIMULADORES[pre][0]
    at = _abrir(pagina)
    q = modulo.PREGUNTAS_PREDICE[0]
    at.radio(key=f"{pre}_pd_{q.id}_radio").set_value(q.opciones[0].texto).run()
    at.button(key=f"{pre}_pd_{q.id}_b_run").click().run()
    assert not at.exception, [e.value for e in at.exception]
    # El resultado se muestra (éxito o error con explicación), nunca un fallo silencioso
    assert at.success or at.error or at.info


@pytest.mark.parametrize("pagina", list(RETOS_UI))
def test_reto_inverso_se_verifica_en_la_interfaz(pagina):
    pre = PREFIJOS[pagina]
    r_id, valores = RETOS_UI[pagina]
    at = _abrir(pagina)
    for var, valor in valores.items():
        at.number_input(key=f"{pre}_inv_{r_id}_{var}").set_value(valor)
    at.run()
    at.button(key=f"{pre}_inv_{r_id}_b_ver").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert any(s.value.startswith("Solución exacta") for s in at.success), [w.value for w in at.warning + at.error]
    at.button(key=f"{pre}_inv_{r_id}_b_pista").click().run()
    assert any(i.value.startswith("Pista 1 de") for i in at.info)
    at.button(key=f"{pre}_inv_{r_id}_b_sol").click().run()
    assert not at.exception


def test_reto_incorrecto_explica_por_que_en_la_interfaz():
    at = _abrir("caja")
    at.number_input(key="caja_inv_caja_energia_a").set_value(1.0)
    at.run()
    at.button(key="caja_inv_caja_energia_b_ver").click().run()
    assert any("No cumple" in e.value and "menor" in e.value for e in at.error)


@pytest.mark.parametrize("pagina", ["caja", "oscilador", "fotoelectrico", "bohr", "esfera", "incertidumbre"])
def test_informe_se_prepara_desde_la_interfaz(pagina):
    pre = PREFIJOS[pagina]
    at = _abrir(pagina)
    at.button(key=f"{pre}_inf_prep").click().run()
    assert not at.exception, [e.value for e in at.exception]
    pdf = at.session_state[f"{pre}_inf_pdf"]
    csv_ = at.session_state[f"{pre}_inf_csv"]
    assert pdf.startswith(b"%PDF-") and pdf.rstrip().endswith(b"%%EOF")
    assert csv_.decode("utf-8-sig").splitlines()[0] == "Sección,Magnitud,Valor,Unidad"


def test_conclusiones_escritas_llegan_al_informe():
    pypdf = pytest.importorskip("pypdf")
    at = _abrir("caja")
    at.text_area(key="caja_inf_concl").set_value("Observé que E crece como n².").run()
    at.button(key="caja_inf_prep").click().run()
    texto = " ".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(at.session_state["caja_inf_pdf"])).pages)
    assert "Observé que E crece como n²." in texto


def test_pregunta_bajo_el_umbral_muestra_un_error_comprensible():
    at = _abrir("fotoelectrico", foto_lambda=900.0)
    q = foto.PREGUNTAS_PREDICE[0]
    at.button(key=f"foto_pd_{q.id}_b_run").click().run()
    assert not at.exception
    assert any("umbral" in e.value for e in at.error)


def test_los_parametros_fisicos_no_cambian_al_experimentar():
    at = _abrir("caja")
    antes = {k: at.session_state[k] for k in ("caja_n", "caja_longitud", "caja_masa", "caja_sistema", "caja_puntos")}
    at.button(key="caja_pd_duplicar_a_b_run").click().run()
    assert {k: at.session_state[k] for k in antes} == antes


def test_instrumentos_de_la_caja_en_atomicas_y_con_n_alto():
    at = _abrir("caja", caja_sistema="Atómicas", caja_longitud=10.0, caja_n=15, caja_puntos=3000)
    assert not at.exception, [e.value for e in at.exception]


def test_enlaces_de_estudio_navegan_desde_el_laboratorio_completo():
    """Desde un experimento de predicción se llega al solucionador y a los ejercicios del tema."""
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file("quantum_lab.py", default_timeout=240)
    at.session_state["ql_pagina"] = "bohr"
    at.run()
    at.button(key="bohr_pd_energia_2n_b_run").click().run()
    assert not at.exception
    at.button(key="ql_est_bohr_pd_energia_2n_sol").click().run()
    assert at.session_state["ql_pagina"] == "solucionador" and at.session_state["sol_problema"] == "rydberg"
    assert not at.exception


def test_esfera_reto_nodos_solucion_independiente():
    """l = 5, m = ±3 (2 conos + 3 planos) sale de contar a mano: l − |m| = 2 y |m| = 3. Otras parejas con l = 5 no valen."""
    r = next(x for x in esf.RETOS_INVERSOS if x.id == "esf_nodos")
    for m in (3, -3):
        assert inverso.evaluar_intento(r, {"l": 5, "m": m}).nivel == "exacta"
    # l = 5 pero otro reparto de conos y planos: 5 superficies, mal reparto
    assert inverso.evaluar_intento(r, {"l": 5, "m": 1}).nivel == "incorrecta"
    assert inverso.evaluar_intento(r, {"l": 4, "m": 2}).nivel == "incorrecta"
    with pytest.raises(ValueError):
        inverso.evaluar_intento(r, {"l": 2, "m": 5})


def test_esfera_reto_l2_cualquier_m_vale():
    """L²/ħ² = l(l+1) = 12 solo para l = 3 (3·4); m no influye y |m| ≤ 3."""
    r = next(x for x in esf.RETOS_INVERSOS if x.id == "esf_l2")
    for m in range(-3, 4):
        assert inverso.evaluar_intento(r, {"l": 3, "m": m}).nivel == "exacta"
    assert inverso.evaluar_intento(r, {"l": 2, "m": 0}).nivel == "incorrecta"      # 6
    assert inverso.evaluar_intento(r, {"l": 4, "m": 0}).nivel == "incorrecta"      # 20
    with pytest.raises(ValueError):
        inverso.evaluar_intento(r, {"l": 3, "m": 4})


def test_informe_de_prediccion_incluye_figura():
    pypdf = pytest.importorskip("pypdf")
    at = _abrir("caja")
    at.button(key="caja_pd_duplicar_a_b_run").click().run()
    at.button(key="caja_pd_duplicar_a_inf_prep").click().run()
    assert not at.exception, [e.value for e in at.exception]
    pdf = at.session_state["caja_pd_duplicar_a_inf_pdf"]
    assert pdf and pdf.startswith(b"%PDF-")
    texto = " ".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(pdf)).pages)
    assert "cociente" in texto


def test_condicion_del_reto_sin_unidad_no_deja_asteriscos_sueltos():
    """Regresión: con unidad vacía el texto quedaba «**… = 5 **» y Markdown no lo ponía en negrita."""
    at = _abrir("esfera")
    textos = [m.value for m in at.markdown if m.value.startswith("Condición")]
    assert textos and all(not t.rstrip().endswith(" **") for t in textos), textos


def test_tabla_larga_repite_encabezado_y_tabla_corta_no_se_parte():
    """Una tabla de 70 filas continúa en otra página con su encabezado; una tabla corta cerca del final pasa entera."""
    pypdf = pytest.importorskip("pypdf")
    base = _informes_de_prueba()["caja"]
    larga = [(f"Magnitud {i}", f"{i}", "u") for i in range(70)]
    inf = dataclasses.replace(base, resultados=larga, tablas=[("Tabla corta", ["A", "B"], [["1", "2"], ["3", "4"], ["5", "6"]])])
    paginas = [p.extract_text() for p in pypdf.PdfReader(io.BytesIO(informes.pdf_informe(inf))).pages]
    assert len(paginas) >= 3
    assert any("(continuación)" in p for p in paginas)
    for p in paginas[1:]:                              # cada página con filas de la tabla larga arranca con título y encabezado
        lineas = p.strip().splitlines()
        if any(x.startswith("Magnitud ") and x != "Magnitud Valor Unidad" for x in lineas[:3]):
            assert lineas[0] == "Resultados (continuación)" and lineas[1] == "Magnitud Valor Unidad", lineas[:3]
    corta = next(p for p in paginas if "Tabla corta" in p)
    assert all(fila in corta for fila in ("1 2", "3 4", "5 6"))       # la tabla corta no se parte


# =============================================================================================
# Lecturas de los instrumentos dentro del informe
# =============================================================================================
def _csv_lecturas(at, prefijo):
    at.button(key=f"{prefijo}_inf_prep").click().run()
    assert not at.exception, [e.value for e in at.exception]
    filas = list(csv.reader(at.session_state[f"{prefijo}_inf_csv"].decode("utf-8-sig").splitlines()))
    return {f[1]: f for f in filas if f[0].startswith("Lecturas de instrumentos")}


def test_informe_de_la_caja_incluye_cursor_intervalo_y_foton_con_valores_independientes():
    at = _abrir("caja")
    lec = _csv_lecturas(at, "caja")
    # n = 1, a = 1 nm, intervalo (0.25, 0.5) nm: P = [x/a − sen(2πx/a)/(2π)] evaluado a mano
    primitiva = lambda x: x - math.sin(2 * math.pi * x) / (2 * math.pi)
    p_exacta = primitiva(0.5) - primitiva(0.25)
    clave = next(k for k in lec if k.endswith("exacta"))
    assert float(lec[clave][2]) == pytest.approx(p_exacta, abs=1e-9)
    # fotón 6 → 3: ΔE = (36 − 9)·E₁, λ = hc/ΔE con E₁ = 0.376030 eV y hc = 1239.84198 eV·nm
    lam = next(v for k, v in lec.items() if "longitud de onda" in k)
    assert float(lam[2]) == pytest.approx(1239.84198 / (27 * 0.376030), rel=2e-5)
    assert any(k.startswith("Cursor: ψ") for k in lec)


def test_informe_de_bohr_incluye_el_foton_calculado():
    at = _abrir("bohr")
    lec = _csv_lecturas(at, "bohr")
    lam = next(v for k, v in lec.items() if "longitud de onda" in k)
    assert 656.0 < float(lam[2]) < 656.6                       # Hα del hidrógeno (656.28 nm en el vacío, ± masa reducida)
    assert next(v for k, v in lec.items() if k.endswith("tipo"))[2] == "Emisión"


@pytest.mark.parametrize("pagina,prefijo", [("oscilador", "osc"), ("fotoelectrico", "foto"), ("esfera", "esf"),
                                            ("incertidumbre", "inc")])
def test_informes_incluyen_lecturas_de_instrumentos(pagina, prefijo):
    pypdf = pytest.importorskip("pypdf")
    at = _abrir(pagina)
    lec = _csv_lecturas(at, prefijo)
    assert lec, "el informe no trae lecturas de instrumentos"
    texto = " ".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(at.session_state[f"{prefijo}_inf_pdf"])).pages)
    assert "Lecturas de los instrumentos" in texto


def test_figura_del_informe_de_la_caja_marca_cursor_e_intervalo():
    pc = _p_caja()
    d = caja.calcular_estado_individual(pc)
    inf = caja.informe_estado(pc, d, "", [("a", "1", "")], {"x0": 0.4, "x1": 0.25, "x2": 0.5})
    ax2 = inf.figuras[0].axes[1]
    assert len(ax2.patches) == 1                                # axvspan del intervalo
    assert any(abs(l.get_xdata()[0] - 0.4) < 1e-12 for l in ax2.lines if len(set(l.get_xdata())) == 1)
    assert inf.lecturas == [("a", "1", "")]


def test_ningun_titulo_de_seccion_queda_solo_al_pie_de_pagina():
    """Regresión: «6. Resultados…» quedaba como última línea de la página 1 y su tabla en la página 2."""
    pypdf = pytest.importorskip("pypdf")
    pc = _p_caja()
    d = caja.calcular_estado_individual(pc)
    lec = [(f"Lectura {i}", "1", "u") for i in range(5)]
    for extra in range(0, 12):
        inf = caja.informe_estado(pc, d, "", lec[:extra % 6] or None)
        inf = dataclasses.replace(inf, parametros=inf.parametros + [(f"Extra {i}", "1", "") for i in range(extra)])
        for pag in pypdf.PdfReader(io.BytesIO(informes.pdf_informe(inf))).pages:
            lineas = [x for x in pag.extract_text().splitlines() if x.strip() and not x.startswith("Quantum Lab ·")
                      and not x.startswith("Página")]
            titulos = ("1. Objetivo", "2. Modelo", "3. Ecuaciones", "4. Datos", "5. Procedimiento", "6. Resultados",
                       "7. Gráficas", "8. Preguntas", "9. Conclusiones")
            assert not (lineas and lineas[-1].startswith(titulos)), lineas[-2:]


# =============================================================================================
# Marcas de los instrumentos en las figuras de los informes
# =============================================================================================
def test_figura_de_bohr_marca_los_niveles_del_instrumento_de_foton():
    pb = _p_bohr()                                              # 3 → 2
    d = bohr.calcular_transicion(pb)
    igual = bohr.informe_transicion(pb, d, "", [("a", "1", "")], (3, 2)).figuras[0].axes[0]
    otro = bohr.informe_transicion(pb, d, "", [("a", "1", "")], (4, 2)).figuras[0].axes[0]
    assert igual.get_legend() is None                           # mismos niveles: no se duplica la flecha
    textos = [t.get_text() for t in otro.get_legend().get_texts()]
    assert any("4 → 2" in t for t in textos) and any("3 → 2" in t for t in textos)
    assert len(otro.texts) == len(igual.texts) + 1               # una flecha adicional


def test_figura_de_la_esfera_marca_la_direccion_solo_si_esta_en_el_plano_xz():
    pe = esf.validar_parametros_esfera(2, 1, 1.0, "SI", 90, "densidad", "lobulos", 0.4, "Viridis")
    th = math.pi / 4
    ax = esf.informe_estado_angular(pe, "", [("a", "1", "")], (th, 0.0)).figuras[0].axes[0]
    punto = next(l for l in ax.lines if l.get_marker() == "o")
    rho = 15 / (8 * math.pi) * math.sin(th) ** 2 * math.cos(th) ** 2          # |Y₂¹|² con la fórmula cerrada
    assert punto.get_xdata()[0] == pytest.approx(rho * math.sin(th), rel=1e-9)
    assert punto.get_ydata()[0] == pytest.approx(rho * math.cos(th), rel=1e-9)
    fuera = esf.informe_estado_angular(pe, "", [("a", "1", "")], (th, 0.7)).figuras[0].axes[0]
    assert not any(l.get_marker() == "o" for l in fuera.lines)                 # φ = 0.7 rad no está en el plano xz
    sin = esf.informe_estado_angular(pe, "", None, None).figuras[0].axes[0]
    assert not any(l.get_marker() == "o" for l in sin.lines)


def test_figura_de_incertidumbre_sombrea_media_mas_menos_la_desviacion():
    pi_ = _p_inc()
    d = inc.calcular_paquete(pi_)
    con = inc.informe_paquete(pi_, d, "", [("a", "1", "")]).figuras[0].axes
    sin = inc.informe_paquete(pi_, d, "").figuras[0].axes
    assert all(len(a.patches) == 1 for a in con) and all(len(a.patches) == 0 for a in sin)
    assert con[0].patches[0].get_width() == pytest.approx(2 * d["delta_x"], rel=1e-9)
    assert con[0].patches[0].get_x() == pytest.approx(d["x_medio"] - d["delta_x"], rel=1e-9, abs=1e-12)
    assert con[1].patches[0].get_width() == pytest.approx(2 * d["delta_k"], rel=1e-9)


@pytest.mark.parametrize("clave", list(SIMULADORES))
def test_titulos_y_conclusiones_nunca_quedan_partidos_en_ningun_simulador(informes_listos, clave):
    """Con distintas cantidades de filas: ningún título de sección queda al pie y «Conclusiones» va en una sola página."""
    pypdf = pytest.importorskip("pypdf")
    titulos = ("1. Objetivo", "2. Modelo", "3. Ecuaciones", "4. Datos", "5. Procedimiento", "6. Resultados",
               "7. Gráficas", "8. Preguntas", "9. Conclusiones")
    base = informes_listos[clave]
    for extra in range(0, 16):
        inf = dataclasses.replace(base, conclusiones="",
                                  lecturas=[(f"Lectura {i}", "1", "u") for i in range(extra)],
                                  resultados=base.resultados + [(f"Extra {i}", "1", "") for i in range(extra % 7)])
        lector = pypdf.PdfReader(io.BytesIO(informes.pdf_informe(inf)))
        paginas = [p.extract_text() for p in lector.pages]
        for pagina, pag in zip(lector.pages, paginas, strict=True):
            lineas = [x for x in pag.splitlines() if x.strip() and not x.startswith(("Quantum Lab ·", "Página"))]
            if lineas and lineas[-1].startswith("7. Gráficas"):          # la figura es una imagen: debe estar en esa página
                assert len(pagina.images) >= 1, (clave, extra, "título de gráficas sin figura")
                continue
            assert not (lineas and lineas[-1].startswith(titulos)), (clave, extra, lineas[-2:])
        assert "9. Conclusiones del estudiante" in paginas[-1] or "9. Conclusiones del estudiante" in paginas[-2], (clave, extra)
