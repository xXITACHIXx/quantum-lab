"""Pruebas de las herramientas de estudio: Biblioteca científica, Solucionador paso a paso y Tutor de errores conceptuales."""
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import biblioteca
import efecto_fotoelectrico as ef
import modelo_bohr as mb
import oscilador_armonico as oa
import particula_caja as pc
import quantum_lab_comun as qc
import quantum_lab_portada as portada
import solucionador
import teoria
import tutor
from biblioteca import _conexiones, _derivaciones, _glosario, _referencias
from solucionador import _problemas as pr
from tutor import _errores, _preguntas

APP = str(Path(__file__).parent / "quantum_lab.py")
PAGINAS = {m[0] for m in portada.MODULOS}


def _abrir(pagina, **estado):
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["ql_pagina"] = pagina
    for k, v in estado.items():
        at.session_state[k] = v
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


# ------------------------------------------------------------------------------------------------------------- Biblioteca
def test_pruebas_internas_de_cada_herramienta():
    for modulo in (biblioteca, solucionador, tutor):
        reg = modulo.ejecutar_pruebas()
        assert reg.todo_ok(), [r for r in reg.resultados if not r["ok"]]


def test_glosario_es_coherente():
    ids = {t.id for t in _glosario.TERMINOS}
    assert len(ids) == len(_glosario.TERMINOS) >= 40
    for t in _glosario.TERMINOS:
        assert all(r in ids for r in t.relacionados), t.id
        assert not t.tema or teoria.buscar(t.tema), t.id
        assert not t.simulador or t.simulador in PAGINAS, t.id


@pytest.mark.parametrize("consulta,esperado", [("amplitud", "amplitud"), ("FUNCION de onda", "funcion_onda"), ("umbral", "frecuencia_umbral"), ("rydberg", "serie_espectral")])
def test_busqueda_del_glosario(consulta, esperado):
    assert esperado in {t.id for t in _glosario.buscar(consulta)}


def test_busqueda_vacia_devuelve_todo_y_sin_coincidencias_nada():
    assert len(_glosario.buscar("")) == len(_glosario.TERMINOS) and _glosario.buscar("zzzzqq") == []


@pytest.mark.parametrize("d", _derivaciones.DERIVACIONES, ids=lambda d: d.id)
def test_derivacion_coincide_con_la_referencia_independiente(d):
    _, calculado, referencia, _ = d.comprobacion()
    assert abs(calculado - referencia) / abs(referencia) < 1e-5


def test_las_derivaciones_cubren_los_temas_clave():
    assert {d.tema for d in _derivaciones.DERIVACIONES} >= {"caja", "oscilador", "fotoelectrico", "bohr", "incertidumbre", "de_broglie"}


def test_conexiones_validas_y_grafo_dot():
    ids = {t.id for t in _glosario.TERMINOS}
    assert all(r.origen in ids and r.destino in ids for r in _conexiones.RELACIONES)
    dot = _conexiones.dot({"funcion_onda", "amplitud"})
    assert "funcion_onda -> amplitud" in dot and dot.startswith("digraph") and dot.endswith("}")
    sal, ent = _conexiones.vecinos("amplitud")
    assert ("densidad_prob", "su módulo al cuadrado da") in sal and ent


def test_referencias_con_enlaces_seguros():
    assert len(_referencias.REFERENCIAS) >= 12
    assert all(r.enlace.startswith("https://") for r in _referencias.REFERENCIAS if r.enlace)
    tipos = {r.tipo for r in _referencias.REFERENCIAS}
    assert {"Libro de texto", "Simulación de referencia", "Documentación"} <= tipos


def test_pagina_biblioteca_pestanas_y_busqueda():
    at = _abrir("biblioteca")
    assert len(at.tabs) == 4 and any('class="ql-cab-arte"' in m.value for m in at.markdown)
    at.text_input(key="bib_busqueda").set_value("intensidad").run()
    assert not at.exception, [e.value for e in at.exception]
    assert "Intensidad de la luz" in [e.label for e in at.expander]


def test_pagina_biblioteca_derivacion_muestra_comprobacion():
    at = _abrir("biblioteca")
    at.selectbox(key="bib_derivacion").select("foto_einstein").run()
    assert not at.exception, [e.value for e in at.exception]
    textos = " ".join(m.value for m in at.markdown)
    assert "Comprobación numérica" in textos and len(at.metric) >= 3


def test_glosario_largo_se_acota_y_el_interruptor_muestra_todo():
    at = _abrir("biblioteca")
    visibles = [e for e in at.expander if e.label in {t.nombre for t in _glosario.TERMINOS}]
    assert len(visibles) == 12
    at.toggle(key="bib_todos").set_value(True).run()
    visibles = [e for e in at.expander if e.label in {t.nombre for t in _glosario.TERMINOS}]
    assert len(visibles) == len(_glosario.TERMINOS)


# ------------------------------------------------------------------------------------------------------------- Solucionador
def cerca(a, b, tol=1e-9):
    return abs(a - b) <= tol * abs(b)


def test_fotoelectrico_coincide_con_el_simulador():
    s = pr.fotoelectrico(300, 2.28).valores
    assert cerca(s["K_ev"], float(ef.energia_cinetica_maxima(s["nu"], 2.28)))
    assert cerca(s["v_max"], ef.velocidad_maxima(s["K_ev"])) and cerca(s["lambda0_nm"], ef.longitud_umbral_nm(2.28))
    assert cerca(s["nu0"], ef.frecuencia_umbral(2.28))


def test_fotoelectrico_bajo_el_umbral():
    s = pr.fotoelectrico(650, 2.14)                     # luz roja sobre cesio: 1.91 eV < 2.14 eV
    assert not s.valores["emision"] and s.valores["K_ev"] == 0.0 and s.avisos
    assert "no hay" in dict(s.resultados)["Emisión"]


@pytest.mark.parametrize("n,a_nm", [(1, 1.0), (3, 0.5), (10, 5.0)])
def test_caja_coincide_con_el_simulador(n, a_nm):
    s = pr.caja(n, a_nm, qc.M_E).valores
    a = a_nm * 1e-9
    assert cerca(s["E_J"], pc.energia_nivel(n, a, qc.M_E)) and cerca(s["p"], pc.momento_estado(n, a))
    assert cerca(s["lambda"], pc.longitud_onda_de_broglie(n, a)) and s["nodos"] == len(pc.nodos_interiores(n, a))
    assert cerca(s["dE_J"], pc.energia_nivel(n + 1, a, qc.M_E) - pc.energia_nivel(n, a, qc.M_E))


@pytest.mark.parametrize("n", [0, 1, 5])
def test_oscilador_coincide_con_el_simulador(n):
    s = pr.oscilador(n, qc.M_E, omega=1e15).valores
    assert cerca(s["E_J"], oa.energia_teorica(n, 1e15)) and cerca(s["x_ret"], oa.punto_retorno(n, qc.M_E, 1e15))
    assert cerca(s["x0"], oa.longitud_caracteristica(qc.M_E, 1e15))


def test_oscilador_con_k_equivale_a_dar_omega():
    k, m = 480.0, 1.6e-27
    assert cerca(pr.oscilador(2, m, k_resorte=k).valores["omega"], np.sqrt(k / m))
    assert cerca(pr.oscilador(2, m, k_resorte=k).valores["E_J"], pr.oscilador(2, m, omega=np.sqrt(k / m)).valores["E_J"])


@pytest.mark.parametrize("ni,nf", [(3, 2), (2, 1), (5, 3), (2, 7)])
def test_rydberg_coincide_con_el_simulador(ni, nf):
    s = pr.rydberg("H", ni, nf).valores
    assert cerca(s["lambda_nm"], mb.longitud_rydberg(ni, nf, "H") * 1e9)
    assert cerca(s["dE_eV"], float(mb.energia_nivel(nf, "H", True) - mb.energia_nivel(ni, "H", True)))
    assert s["emite"] == (ni > nf)


def test_rydberg_sin_masa_reducida_difiere_poco():
    a, b = pr.rydberg("H", 3, 2, True).valores["lambda_nm"], pr.rydberg("H", 3, 2, False).valores["lambda_nm"]
    assert 1e-4 < abs(a - b) / a < 1e-3


def test_de_broglie_energia_y_velocidad_son_equivalentes():
    s = pr.de_broglie(qc.M_E, "energia", 100).valores
    assert abs(s["lambda"] * 1e9 - 0.12264) < 1e-4
    assert cerca(pr.de_broglie(qc.M_E, "velocidad", s["v"]).valores["lambda"], s["lambda"])


def test_de_broglie_pelota_es_inobservable_y_relativista_avisa():
    assert "inobservables" in pr.de_broglie(0.145, "velocidad", 40).interpretacion
    assert pr.de_broglie(qc.M_E, "velocidad", 1e8).avisos


def test_incertidumbre_cota_minima():
    s = pr.incertidumbre(0.1, qc.M_E).valores
    assert cerca(s["dp"] * 0.1e-9 * 2, qc.HBAR) and cerca(s["dv"], s["dp"] / qc.M_E)


@pytest.mark.parametrize("f,args", [(pr.fotoelectrico, (0, 2)), (pr.fotoelectrico, (300, -1)), (pr.caja, (0, 1, qc.M_E)), (pr.caja, (1, 1, 0)),
                                    (pr.oscilador, (1, qc.M_E)), (pr.oscilador, (1, qc.M_E, 1e15, 3.0)), (pr.rydberg, ("H", 3, 3)),
                                    (pr.rydberg, ("Xx", 3, 2)), (pr.de_broglie, (qc.M_E, "x", 1)), (pr.de_broglie, (qc.M_E, "velocidad", 4e8)),
                                    (pr.incertidumbre, (-1, qc.M_E)), (pr.caja, (float("nan"), 1, qc.M_E))])
def test_entradas_invalidas_se_rechazan(f, args):
    with pytest.raises(ValueError):
        f(*args)


@pytest.mark.parametrize("clave", list(pr.PROBLEMAS))
def test_toda_solucion_tiene_las_cinco_partes(clave):
    s = {"fotoelectrico": lambda: pr.fotoelectrico(300, 2.28), "caja": lambda: pr.caja(2, 1, qc.M_E), "oscilador": lambda: pr.oscilador(2, qc.M_E, omega=1e15),
         "rydberg": lambda: pr.rydberg("H", 3, 2), "de_broglie": lambda: pr.de_broglie(qc.M_E, "energia", 50), "incertidumbre": lambda: pr.incertidumbre(1, qc.M_E)}[clave]()
    assert s.ecuaciones and s.datos and len(s.pasos) >= 3 and s.resultados and len(s.interpretacion) > 40
    assert all(p.texto and p.latex for p in s.pasos)
    assert any(r"\mathrm" in p.latex for p in s.pasos)           # las sustituciones llevan unidades


def test_formato_numerico():
    from solucionador._modelo import num
    assert num(2.28) == "2.28" and num(0) == "0" and num(9.109e-31) == r"9.109\times10^{-31}" and num(1.234567e7) == r"1.235\times10^{7}"


def test_pagina_solucionador_recorre_los_seis_problemas():
    at = _abrir("solucionador")
    assert any("Efecto fotoeléctrico" in s.value for s in at.subheader)
    for clave in pr.PROBLEMAS:
        at.selectbox(key="sol_problema").select(clave).run()
        assert not at.exception, (clave, [e.value for e in at.exception])
        textos = " ".join(m.value for m in at.markdown)
        for seccion in ("1. Ecuaciones", "2. Datos", "3. Sustitución", "4. Resultados", "5. Interpretación"):
            assert seccion in textos.replace("&amp;", "&"), (clave, seccion)


def test_pagina_solucionador_cambia_el_resultado_con_los_datos():
    at = _abrir("solucionador")
    at.text_input(key="sol_fe_lam").set_value("200").run()
    assert not at.exception
    texto = " ".join(m.value for m in at.markdown)
    assert "6.199" in texto and "1.241" not in texto or "3.919" in texto          # 1239.84/200 = 6.199 eV; K = 6.199 − 2.14 (cesio)


def test_pagina_solucionador_muestra_error_amable_con_dato_invalido():
    at = _abrir("solucionador")
    at.text_input(key="sol_fe_lam").set_value("abc").run()
    assert not at.exception and len(at.error) == 1 and "interpretar" in at.error[0].value
    at.text_input(key="sol_fe_lam").set_value("-5").run()
    assert not at.exception and len(at.error) == 1 and "positivo" in at.error[0].value


def test_pagina_solucionador_admite_notacion_cientifica():
    at = _abrir("solucionador")
    at.selectbox(key="sol_problema").select("de_broglie").run()
    at.text_input(key="sol_db_v").set_value("2,5 x 10^6").run()
    assert not at.exception and not at.error


# --------------------------------------------------------------------------------------------------------------------- Tutor
def test_el_catalogo_es_coherente():
    ids = [c.id for c in _errores.CONCEPCIONES]
    assert len(ids) == len(set(ids)) >= 20
    for c in _errores.CONCEPCIONES:
        assert c.reglas and c.frases_error and c.pista and c.explicacion, c.id
        assert all(g in _glosario.POR_ID for g in c.glosario), c.id


@pytest.mark.parametrize("c", _errores.CONCEPCIONES, ids=lambda c: c.id)
def test_el_detector_reconoce_las_frases_de_error_y_no_las_correctas(c):
    for f in c.frases_error:
        assert c in _errores.detectar(f), f
    for f in c.frases_correctas:
        assert c not in _errores.detectar(f), f


@pytest.mark.parametrize("frase,esperado", [
    ("La función de onda es la probabilidad de encontrar la partícula.", "amplitud_prob"),
    ("Si aumento la intensidad, los electrones salen con más energía.", "intensidad_energia_foton"),
    ("Un estado estacionario es cuando la partícula está quieta.", "estacionario_reposo"),
    ("El estado fundamental del oscilador tiene energía cero.", "energia_cero"),
])
def test_detector_en_oraciones_libres(frase, esperado):
    assert esperado in {c.id for c in _errores.detectar(frase)}


@pytest.mark.parametrize("frase", [
    "La amplitud de probabilidad es compleja y su módulo al cuadrado es la densidad.",
    "La intensidad indica cuántos fotones llegan por segundo, pero no cambia la energía de cada uno.",
    "El valor esperado es el promedio de muchas medidas y puede no ser un valor posible.",
    "La fase global no importa, pero la relativa sí.",
    "En el modelo de Bohr los niveles son correctos pero las órbitas no existen.",
    "",
])
def test_explicaciones_correctas_no_activan_el_detector(frase):
    assert _errores.detectar(frase) == []


def test_normalizar_quita_tildes_y_transcribe_griegas():
    assert _errores.normalizar("Ψ² |ψ|  Densidad ÓN") == "psi2 psi densidad on"


def test_cada_confusion_aparece_en_alguna_pregunta_y_las_opciones_son_validas():
    usadas = {c for q in _preguntas.PREGUNTAS for _, c in q.opciones if c}
    assert usadas == {c.id for c in _errores.CONCEPCIONES}
    for q in _preguntas.PREGUNTAS:
        assert 2 <= len(q.opciones) <= 4 and q.opciones[q.correcta][1] is None
        assert len({t for t, _ in q.opciones}) == len(q.opciones)
        assert teoria.buscar(q.tema)


def test_las_preguntas_numericas_son_correctas():
    # Q umbral: 650 nm → 1.907 eV < 2.14 eV; λ máx para el cesio ≈ 579 nm
    assert abs(1239.841984 / 650 - 1.91) < 0.005 and abs(1239.841984 / 2.14 - 579) < 1
    # Q coeficientes: 0.6² + 0.8² = 1
    assert abs(0.36 + 0.64 - 1) < 1e-12
    # Q pelota: λ = h/(m v) ≈ 1.1e-34 m
    assert abs(qc.H_PLANCK / (0.145 * 40) - 1.14e-34) < 1e-35
    # Q interferencia: |ψ1 e^{-iE1t} + ψ2 e^{-iE2t}|²/2 = ½ψ1² + ½ψ2² + ψ1ψ2 cos((E2−E1)t)
    rng = np.random.default_rng(3)
    p1, p2, dE, t = rng.normal(size=4)
    Psi = (p1 * np.exp(-1j * 0 * t) + p2 * np.exp(-1j * dE * t)) / np.sqrt(2)
    assert abs(abs(Psi) ** 2 - (0.5 * p1 ** 2 + 0.5 * p2 ** 2 + p1 * p2 * np.cos(dE * t))) < 1e-12


def test_pagina_tutor_revisar_detecta_y_registra():
    at = _abrir("tutor")
    assert len(at.tabs) == 4
    at.text_area(key="tut_texto").set_value("La función de onda es la probabilidad de encontrar la partícula.").run()
    [b for b in at.button if b.key == "tut_revisar"][0].click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["tut_halladas"] == ["amplitud_prob"] and at.session_state["tut_perfil"] == {"amplitud_prob": 1}
    assert any("Amplitud y probabilidad" in m.value for m in at.markdown)


def test_pagina_tutor_texto_correcto_no_marca_nada():
    at = _abrir("tutor")
    at.text_area(key="tut_texto").set_value("La probabilidad es el módulo al cuadrado de la amplitud.").run()
    [b for b in at.button if b.key == "tut_revisar"][0].click().run()
    assert not at.exception and at.session_state["tut_halladas"] == [] and not at.session_state["tut_perfil"]


def test_pagina_tutor_pregunta_incorrecta_da_pista_y_correcta_confirma():
    at = _abrir("tutor")
    q = _preguntas.PREGUNTAS[1]                                        # intensidad y energía del fotón
    at.selectbox(key="tut_pregunta").select(q.id).run()
    at.radio(key=f"tut_op_{q.id}").set_value(0).run()
    [b for b in at.button if b.key == f"tut_comp_{q.id}"][0].click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["tut_resp"][q.id] == {"op": 0, "ok": False} and at.session_state["tut_perfil"] == {"intensidad_energia_foton": 1}
    assert any("Pista" in i.value for i in at.info)
    at.radio(key=f"tut_op_{q.id}").set_value(q.correcta).run()
    [b for b in at.button if b.key == f"tut_comp_{q.id}"][0].click().run()
    assert at.session_state["tut_resp"][q.id]["ok"] and any("Correcto" in s.value for s in at.success)
    assert at.session_state["tut_perfil"] == {"intensidad_energia_foton": 1}      # acertar no suma confusiones


def test_pagina_tutor_progreso_y_reinicio():
    at = _abrir("tutor", tut_perfil={"amplitud_prob": 2}, tut_resp={"q_signo": {"op": 2, "ok": False}})
    textos = " ".join(m.value for m in at.markdown)
    assert "Amplitud y probabilidad" in textos and "2 veces" in textos
    [b for b in at.button if b.key == "tut_reiniciar"][0].click().run()
    assert not at.exception and "tut_perfil" not in at.session_state or not at.session_state["tut_perfil"]


def test_tutor_enlaza_con_la_biblioteca():
    at = _abrir("tutor", tut_halladas=["amplitud_prob"], tut_revisado="x")
    [b for b in at.button if b.key == "tut_bib_r_amplitud_prob"][0].click().run()
    assert not at.exception and at.session_state["ql_pagina"] == "biblioteca" and at.session_state["bib_busqueda"] == "Amplitud de probabilidad"
    assert "Amplitud de probabilidad" in [e.label for e in at.expander]


# ------------------------------------------------------------------------------------------------------ Integración global
def test_la_portada_incluye_el_capitulo_y_las_tres_herramientas():
    assert "Herramientas de estudio" in portada.CATEGORIAS and portada.CAPITULOS["Herramientas de estudio"][0] == "04"
    assert [m[0] for m in portada.MODULOS if m[2] == "Herramientas de estudio"] == ["biblioteca", "solucionador", "tutor", "guia"]
    at = _abrir("cat4")
    claves = {b.key for b in at.button if b.key and b.key.startswith("ql_menu_")}
    assert claves == {"ql_menu_biblioteca", "ql_menu_solucionador", "ql_menu_tutor", "ql_menu_guia"}


def test_el_clic_del_capitulo_lleva_a_su_subportada_y_de_ahi_a_la_herramienta():
    at = _abrir("inicio")
    [b for b in at.button if b.key == "ql_menu_cat4"][0].click().run()
    assert at.session_state["ql_pagina"] == "cat4"
    [b for b in at.button if b.key == "ql_menu_tutor"][0].click().run()
    assert not at.exception and at.session_state["ql_pagina"] == "tutor"


def test_el_javascript_recibe_los_totales_reales():
    import quantum_lab_escena as escena

    class _St:
        llamadas = []

        def html(self, contenido, unsafe_allow_javascript=False):
            self.llamadas.append(contenido)
    st = _St()
    assert escena.instalar_efectos(st, len(portada.CATEGORIAS), len(portada.MODULOS))
    js = st.llamadas[0]
    assert "__NCAP__" not in js and "__NDEST__" not in js and "· 05'" in js and "· 19'" in js


def test_pruebas_globales_incluyen_las_herramientas():
    import quantum_lab
    nombres = {r.nombre for r in quantum_lab.ejecutar_todas_las_pruebas()}
    assert {"Biblioteca científica", "Solucionador paso a paso", "Tutor de errores conceptuales", "Guía de usuario"} <= nombres
