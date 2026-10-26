"""
inverso.py — Laboratorio inverso: retos con una condición objetivo y parámetros por descubrir
============================================================================================

Se da un objetivo (o una condición) y la persona debe encontrar los valores que lo cumplen. El sistema NO compara con
una respuesta escrita a mano: calcula la magnitud con las MISMAS funciones del simulador y compara con el objetivo.
Por eso acepta cualquier solución válida (puede haber varias) y explica por qué falla una que no lo es.

Clasificación de un intento (error relativo ε = |obtenido − objetivo| / |objetivo|):

    · exacta      ε ≤ tol_exacta   (la precisión con que se da el objetivo; se indica en cada reto)
    · aproximada  ε ≤ tol_aprox    (útil, pero no cumple la condición con la precisión pedida)
    · incorrecta  en otro caso, o si se incumple la condición del modelo (p. ej. no hay emisión bajo el umbral)

Cuando un reto requiere un cálculo numérico (p. ej. una FFT), su tolerancia lo refleja y se documenta en el propio reto.
No se usa ningún algoritmo de búsqueda: las ecuaciones de estos retos se despejan directamente.

La parte lógica no usa Streamlit; la interfaz (`panel`) está al final.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Variable:
    clave: str
    etiqueta: str
    unidad: str
    minimo: float
    maximo: float
    paso: float
    defecto: float
    entero: bool = False


@dataclass(frozen=True)
class Reto:
    id: str
    titulo: str
    enunciado: str
    magnitud: str                                   # magnitud que se compara con el objetivo
    unidad: str
    objetivo: float
    variables: tuple[Variable, ...]
    evaluar: Callable[[dict], float]                # valores -> magnitud obtenida (misma unidad que el objetivo)
    pistas: tuple[str, ...]
    explicacion: str                                # por qué la solución cumple (física)
    solucion: Callable[[dict], str]                 # fórmula despejada con números; recibe los valores del intento
    dependencia: str                                # cómo depende la magnitud de las variables (para la retroalimentación)
    tol_exacta: float = 5e-5
    tol_aprox: float = 0.02
    mostrar_objetivo: bool = True
    condicion: Callable[[dict, float], str | None] | None = None    # texto si el intento incumple el modelo
    soluciones: str = "Puede haber más de una combinación válida."
    metodo: str = "Cálculo directo con las funciones del simulador."
    notas: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Veredicto:
    nivel: str                  # "exacta" | "aproximada" | "incorrecta"
    obtenido: float
    error_relativo: float
    mensaje: str
    verificacion: tuple[str, ...]


def _validar_valores(reto: Reto, valores: dict) -> dict:
    limpios = {}
    for v in reto.variables:
        if v.clave not in valores:
            raise ValueError(f"Falta el valor de {v.etiqueta}.")
        x = valores[v.clave]
        try:
            x = float(x)
        except (TypeError, ValueError):
            raise ValueError(f"{v.etiqueta} debe ser un número.") from None
        if not math.isfinite(x):
            raise ValueError(f"{v.etiqueta} debe ser un número finito.")
        if not v.minimo <= x <= v.maximo:
            raise ValueError(f"{v.etiqueta} debe estar entre {v.minimo:g} y {v.maximo:g} {v.unidad}.".replace("  ", " "))
        if v.entero:
            if x != int(x):
                raise ValueError(f"{v.etiqueta} debe ser un número entero.")
            x = int(x)
        limpios[v.clave] = x
    return limpios


def validar_reto(reto: Reto) -> list[str]:
    """Comprueba que el reto esté bien construido: objetivo finito, tolerancias ordenadas, solución consistente."""
    problemas = []
    if not math.isfinite(reto.objetivo) or reto.objetivo == 0:
        problemas.append("El objetivo debe ser finito y distinto de cero.")
    if not 0 < reto.tol_exacta < reto.tol_aprox < 1:
        problemas.append("Las tolerancias deben cumplir 0 < tol_exacta < tol_aprox < 1.")
    if not reto.pistas:
        problemas.append("Faltan pistas.")
    if not reto.variables:
        problemas.append("Faltan variables.")
    return problemas


def evaluar_intento(reto: Reto, valores: dict) -> Veredicto:
    """Calcula la magnitud con los valores dados y clasifica el intento. Lanza ValueError si los datos no son válidos."""
    v = _validar_valores(reto, valores)
    obtenido = float(reto.evaluar(v))
    err = abs(obtenido - reto.objetivo) / abs(reto.objetivo)
    ver = [f"{reto.magnitud} calculada = {obtenido:.8g} {reto.unidad}",
           f"Objetivo = {reto.objetivo:.8g} {reto.unidad}",
           f"Error relativo = {err:.3e}  (exacta si ≤ {reto.tol_exacta:g}; aproximada si ≤ {reto.tol_aprox:g})"]
    incumple = reto.condicion(v, obtenido) if reto.condicion else None
    if incumple:
        return Veredicto("incorrecta", obtenido, err, incumple, tuple(ver))
    if err <= reto.tol_exacta:
        return Veredicto("exacta", obtenido, err, "Cumple el objetivo con la precisión pedida.", tuple(ver))
    if err <= reto.tol_aprox:
        return Veredicto("aproximada", obtenido, err,
                         f"Estás cerca ({err * 100:.3g} %), pero no cumple la condición con la precisión pedida. "
                         f"Ajusta el valor con más cifras.", tuple(ver))
    sentido = "mayor" if obtenido > reto.objetivo else "menor"
    return Veredicto("incorrecta", obtenido, err,
                     f"La magnitud obtenida es {sentido} que el objetivo (factor {obtenido / reto.objetivo:.4g}). "
                     f"{reto.dependencia}", tuple(ver))


# =====================================================================
# Interfaz
# =====================================================================
def panel(retos: list[Reto], prefijo: str) -> None:
    """Panel «Laboratorio inverso»: elegir reto, ajustar variables, verificar, pedir pistas y ver la solución."""
    import streamlit as st

    import quantum_lab_comun as qc

    por_id = {r.id: r for r in retos}
    k = lambda *partes: "_".join([prefijo, "inv", *partes])   # claves de sesión

    r_id = st.selectbox("Reto", list(por_id), format_func=lambda i: por_id[i].titulo, key=k("sel"))
    r = por_id[r_id]
    st.markdown(f"**Objetivo.** {r.enunciado}")
    if r.mostrar_objetivo:
        st.markdown(f"Condición: **{f'{r.magnitud} = {r.objetivo:.6g} {r.unidad}'.strip()}**")
    st.caption(r.soluciones)
    columnas = st.columns(len(r.variables))
    valores = {}
    for col, v in zip(columnas, r.variables, strict=True):
        clave = k(r_id, v.clave)
        if v.entero:
            valores[v.clave] = col.number_input(f"{v.etiqueta} [{v.unidad}]" if v.unidad else v.etiqueta,
                                                int(v.minimo), int(v.maximo), int(v.defecto), 1, key=clave)
        else:
            valores[v.clave] = col.number_input(f"{v.etiqueta} [{v.unidad}]", v.minimo, v.maximo, float(v.defecto),
                                                v.paso, format="%.6g", key=clave)
    kp, kv, ks = k(r_id, "pistas"), k(r_id, "verificado"), k(r_id, "solucion")
    for clave in (kp,):
        st.session_state.setdefault(clave, 0)
    st.session_state.setdefault(kv, False)
    st.session_state.setdefault(ks, False)

    def _pista():
        st.session_state[kp] = min(st.session_state[kp] + 1, len(r.pistas))

    def _verificar():
        st.session_state[kv] = True

    def _solucion():
        st.session_state[ks] = True

    c1, c2, c3 = st.columns(3)
    c1.button("Verificar", key=k(r_id, "b_ver"), type="primary", icon=":material/fact_check:", on_click=_verificar,
              width="stretch")
    c2.button("Pedir una pista", key=k(r_id, "b_pista"), icon=":material/lightbulb:", on_click=_pista,
              disabled=st.session_state[kp] >= len(r.pistas), width="stretch")
    c3.button("Ver la solución", key=k(r_id, "b_sol"), icon=":material/visibility:", on_click=_solucion, width="stretch")
    for i in range(st.session_state[kp]):
        st.info(f"Pista {i + 1} de {len(r.pistas)}: {r.pistas[i]}", icon=":material/lightbulb:")

    if st.session_state[kv]:
        try:
            ve = evaluar_intento(r, valores)
        except ValueError as error:
            qc.error(error)
        else:
            if ve.nivel == "exacta":
                st.success(f"Solución exacta. {ve.mensaje}", icon=":material/check_circle:")
            elif ve.nivel == "aproximada":
                st.warning(f"Solución aproximada. {ve.mensaje}", icon=":material/rule:")
            else:
                st.error(f"No cumple. {ve.mensaje}", icon=":material/cancel:")
            with st.expander("Verificación matemática", expanded=ve.nivel != "incorrecta"):
                for linea in ve.verificacion:
                    st.markdown(f"- {linea}")
                if ve.nivel != "incorrecta":
                    st.markdown(f"**Por qué funciona.** {r.explicacion}")
            qc.enlaces_de_estudio(qc.TEMA_DE_PREFIJO.get(prefijo, ""), f"{prefijo}_inv_{r_id}")
    if st.session_state[ks]:
        with st.expander("Solución despejada", expanded=True):
            st.markdown(r.solucion(valores))
            st.caption(f"Método: {r.metodo}")
