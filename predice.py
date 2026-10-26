"""
predice.py — Modo «Predice, experimenta y explica» (reutilizable por todos los simuladores)
=============================================================================================

Flujo: pregunta conceptual → predicción → experimento → comparación → explicación → repetir.

Este módulo NO contiene física. Cada simulador define sus preguntas (`Pregunta`) y entrega una función
`calcular(parametros)` que usa **las mismas funciones de cálculo del simulador**; la respuesta correcta se
deduce del resultado calculado, nunca se escribe a mano. La predicción no bloquea nada: el experimento puede
ejecutarse sin haberla registrado y los parámetros del simulador no se modifican.

La parte lógica (`evaluar`, `validar_pregunta`) es pura y se prueba sin Streamlit; la interfaz (`panel`) está al final.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Opcion:
    """Una respuesta posible: su texto y el cociente (valor modificado / valor de referencia) que afirma."""
    texto: str
    razon: float


@dataclass(frozen=True)
class Pregunta:
    id: str
    enunciado: str
    cambio: str                       # qué se modifica en el experimento, p. ej. «a → 2a (n y m fijos)»
    opciones: tuple[Opcion, ...]
    pistas: tuple[str, ...]           # de la más general a la más específica
    explicacion: str
    concepto: str                     # tema de teoría al que se vincula (clave de `teoria`)
    magnitud: str                     # nombre de la magnitud comparada, p. ej. «Energía Eₙ»
    calcular: Callable                # calcular(parametros) -> (valor_referencia, valor_modificado, unidad)
    tol: float = 1e-6                 # tolerancia relativa para reconocer la opción correcta (mayor si el cálculo es numérico)


@dataclass(frozen=True)
class Resultado:
    referencia: float
    modificado: float
    unidad: str
    razon: float
    correcta: int                     # índice de la opción que coincide con el cálculo
    elegida: int | None               # None: se ejecutó sin predicción
    acierto: bool | None
    mensaje: str


TOLERANCIA_RELATIVA = 1e-9


def _indice_mas_cercano(opciones: tuple[Opcion, ...], razon: float) -> int:
    distancias = [abs(math.log(o.razon / razon)) for o in opciones]
    return min(range(len(opciones)), key=distancias.__getitem__)


def _razon(q: Pregunta, parametros) -> tuple[float, float, str, float]:
    """(referencia, modificado, unidad, cociente). Lanza ValueError si la magnitud no es positiva y finita."""
    ref, mod, unidad = q.calcular(parametros)
    if not (ref > 0 and mod > 0 and math.isfinite(ref) and math.isfinite(mod)):
        raise ValueError("Con los parámetros actuales la magnitud de esta pregunta es cero o no está definida "
                         "(por ejemplo, por debajo del umbral). Cambia los parámetros del simulador y vuelve a ejecutar.")
    return ref, mod, unidad, mod / ref


def validar_pregunta(q: Pregunta, parametros) -> list[str]:
    """
    Comprueba que la pregunta esté bien construida para los parámetros dados: razones positivas y distintas, y una
    única opción coherente con el cálculo (la respuesta correcta SALE del cálculo). Devuelve la lista de problemas.
    """
    problemas = []
    if len(q.opciones) < 2:
        problemas.append("Hay menos de dos opciones.")
    razones = [o.razon for o in q.opciones]
    if any(not (r > 0 and math.isfinite(r)) for r in razones):
        problemas.append("Alguna razón no es positiva y finita.")
        return problemas
    if len({round(math.log(r), 9) for r in razones}) != len(razones):
        problemas.append("Dos opciones afirman el mismo cociente.")
    try:
        _, _, _, razon = _razon(q, parametros)
    except ValueError:
        problemas.append("El cálculo no entrega valores positivos y finitos.")
        return problemas
    mejor = _indice_mas_cercano(q.opciones, razon)
    if abs(q.opciones[mejor].razon / razon - 1.0) > q.tol:
        problemas.append(f"Ninguna opción coincide con el cociente calculado ({razon:.6g}).")
    if not q.pistas:
        problemas.append("No hay pistas.")
    return problemas


def evaluar(q: Pregunta, parametros, elegida: int | None) -> Resultado:
    """Ejecuta el experimento con los parámetros actuales y compara la predicción (si existe) con el cálculo."""
    ref, mod, unidad, razon = _razon(q, parametros)
    correcta = _indice_mas_cercano(q.opciones, razon)
    if abs(q.opciones[correcta].razon / razon - 1.0) > q.tol:
        raise ValueError("Ninguna opción de la pregunta coincide con el cálculo: la pregunta no es válida "
                         "para estos parámetros.")
    if elegida is None:
        return Resultado(ref, mod, unidad, razon, correcta, None, None,
                         "Ejecutaste el experimento sin registrar una predicción. Puedes registrar una y repetirlo.")
    if not 0 <= elegida < len(q.opciones):
        raise ValueError("La predicción no corresponde a ninguna opción.")
    if elegida == correcta:
        return Resultado(ref, mod, unidad, razon, correcta, elegida, True,
                         f"Tu predicción coincide con el cálculo: el cociente es {razon:.6g}.")
    afirmado = q.opciones[elegida].razon
    return Resultado(ref, mod, unidad, razon, correcta, elegida, False,
                     f"Tu predicción afirmaba un cociente de {afirmado:.6g}, pero el cálculo da {razon:.6g}. "
                     f"Revisa la dependencia de la magnitud con la variable que cambió.")


# =====================================================================
# Interfaz
# =====================================================================
def informe_experimento(q: Pregunta, res: Resultado, datos: dict, conclusiones: str = ""):
    """Informe de un experimento de predicción. `datos`: simulador, modelo, ecuaciones, parametros (filas)."""
    import informes
    fila_pred = q.opciones[res.elegida].texto if res.elegida is not None else "Sin predicción"
    return informes.Informe(
        titulo=f"Predicción y experimento: {q.enunciado}", simulador=datos["simulador"],
        objetivo=f"{q.enunciado} Se compara {q.magnitud} antes y después del cambio: {q.cambio}.",
        modelo=datos["modelo"], ecuaciones=datos.get("ecuaciones", []), parametros=datos["parametros"],
        procedimiento=["Se registra la predicción (opcional).", f"Se calcula {q.magnitud} con los parámetros actuales.",
                       f"Se aplica el cambio: {q.cambio}.", "Se calcula de nuevo y se obtiene el cociente modificado / referencia.",
                       "Se compara el cociente calculado con el que afirma cada opción."],
        resultados=[("Predicción del estudiante", fila_pred, ""), ("Resultado calculado", q.opciones[res.correcta].texto, ""),
                    (f"{q.magnitud} (referencia)", f"{res.referencia:.8g}", res.unidad),
                    (f"{q.magnitud} (modificado)", f"{res.modificado:.8g}", res.unidad),
                    ("Cociente modificado / referencia", f"{res.razon:.8g}", ""),
                    ("Comparación", {True: "La predicción coincide con el cálculo", False: "La predicción no coincide",
                                     None: "Sin predicción"}[res.acierto], "")],
        tablas=[("Opciones de la pregunta", ["Opción", "Cociente que afirma"],
                 [[o.texto, f"{o.razon:.6g}"] for o in q.opciones])],
        preguntas=["¿Qué relación matemática explica el cociente obtenido?",
                   "Repite el experimento con otros parámetros: ¿el cociente cambia o se conserva?"],
        conclusiones=conclusiones)


def panel(preguntas: list[Pregunta], parametros, prefijo: str, formatear: Callable[[float], str] | None = None,
          datos_informe: dict | None = None) -> None:
    """
    Panel «Predice, experimenta y explica». `parametros` son los parámetros YA validados del simulador (solo lectura);
    `prefijo` identifica las claves de sesión. Los resultados se recalculan en cada ejecución de la página, de modo que
    si el estudiante cambia un parámetro del simulador y repite el experimento ve el efecto real.
    """
    import streamlit as st

    import quantum_lab_comun as qc

    fmt = formatear or (lambda v: qc.cientifico(v, 6))
    por_id = {q.id: q for q in preguntas}
    k = lambda nombre: f"{prefijo}_pd_{nombre}"

    q_id = st.selectbox("Pregunta", list(por_id), format_func=lambda i: por_id[i].enunciado, key=k("sel"))
    q = por_id[q_id]
    ka, kp, kr = k(f"{q_id}_radio"), k(f"{q_id}_pistas"), k(f"{q_id}_ejecutado")
    st.session_state.setdefault(kp, 0)
    st.session_state.setdefault(kr, False)

    st.markdown(f"**Experimento.** {q.cambio}. Se compara **{q.magnitud}** antes y después del cambio, "
                f"con los parámetros que tienes ahora en el simulador.")
    st.radio("Tu predicción", [o.texto for o in q.opciones], index=None, key=ka,
             help="Opcional: puedes ejecutar el experimento sin predecir.")

    def _pista():
        st.session_state[kp] = min(st.session_state[kp] + 1, len(q.pistas))

    def _ejecutar():
        st.session_state[kr] = True

    def _reiniciar():
        st.session_state[kr] = False
        st.session_state[kp] = 0
        st.session_state[ka] = None

    c1, c2, c3 = st.columns(3)
    c1.button("Pedir una pista", key=k(f"{q_id}_b_pista"), icon=":material/lightbulb:", on_click=_pista,
              disabled=st.session_state[kp] >= len(q.pistas), width="stretch")
    c2.button("Ejecutar experimento", key=k(f"{q_id}_b_run"), type="primary", icon=":material/play_arrow:",
              on_click=_ejecutar, width="stretch")
    c3.button("Reiniciar pregunta", key=k(f"{q_id}_b_reset"), icon=":material/restart_alt:", on_click=_reiniciar,
              width="stretch")
    for i in range(st.session_state[kp]):
        st.info(f"Pista {i + 1} de {len(q.pistas)}: {q.pistas[i]}", icon=":material/lightbulb:")

    if not st.session_state[kr]:
        return
    elegida_txt = st.session_state.get(ka)
    elegida = [o.texto for o in q.opciones].index(elegida_txt) if elegida_txt in [o.texto for o in q.opciones] else None
    try:
        res = evaluar(q, parametros, elegida)
    except ValueError as error:
        qc.error(error)
        return

    qc.seccion("Resultado del experimento")
    qc.metricas([(f"{q.magnitud} (referencia) [{res.unidad}]", fmt(res.referencia), "Con tus parámetros actuales"),
                 (f"{q.magnitud} (modificado) [{res.unidad}]", fmt(res.modificado), q.cambio),
                 ("Cociente modificado / referencia", f"{res.razon:.6g}", "Calculado, no estimado")], columnas=3)
    qc.tabla([("Predicción", q.opciones[res.elegida].texto if res.elegida is not None else "Sin predicción", ""),
              ("Resultado calculado", q.opciones[res.correcta].texto, ""),
              (f"{q.magnitud} (referencia)", fmt(res.referencia), res.unidad),
              (f"{q.magnitud} (modificado)", fmt(res.modificado), res.unidad),
              ("Cociente modificado / referencia", f"{res.razon:.10g}", "")],
             encabezados=("Concepto", "Valor", "Unidad"), archivo=f"{prefijo}_predice_{q.id}.csv")
    if res.acierto is True:
        st.success(res.mensaje, icon=":material/check_circle:")
    elif res.acierto is False:
        st.error(res.mensaje, icon=":material/cancel:")
    else:
        st.info(res.mensaje, icon=":material/info:")
    st.markdown(f"**Explicación física.** {q.explicacion}")
    qc.enlaces_de_estudio(q.concepto, f"{prefijo}_pd_{q.id}")
    st.caption("Para repetir con otros valores, cambia los parámetros del simulador y pulsa de nuevo «Ejecutar experimento».")
    if datos_informe:
        import informes
        informes.boton_informe(lambda texto: informe_experimento(q, res, datos_informe, texto), f"{prefijo}_pd_{q.id}_inf",
                               f"{prefijo}_predice_{q.id}")
