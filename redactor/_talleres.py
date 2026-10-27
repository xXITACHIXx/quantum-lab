"""
redactor/_talleres.py — Preguntas de los talleres dentro del cuaderno (misma calificación que la página de Talleres)
===================================================================================================================

El bloque guarda el taller, si usa los datos originales o nuevos (con su semilla), la pregunta y las respuestas escritas. Al
abrir el cuaderno se reconstruye la pregunta con `talleres.preguntas_de` y se califica con `talleres.calificar`: el valor
esperado y los diagnósticos son los de siempre. La solución oficial solo entra al PDF si la persona lo pide.
"""

from __future__ import annotations

import talleres
from talleres._calificar import OK
from talleres._modelo import NUM, calificar

ESTADOS = {"ok": "Correcta", "casi": "Casi", "mal": "Incorrecta", "vacia": "Sin responder", "invalida": "No se entiende"}


def catalogo() -> list[tuple[str, str]]:
    return [(t.id, t.titulo) for t in talleres.TALLERES]


def preguntas(taller_id: str, original: bool, semilla: str) -> tuple:
    if talleres.buscar(taller_id) is None:
        raise ValueError(f"Taller desconocido: {taller_id!r}.")
    return talleres.preguntas_de(taller_id, bool(original), str(semilla) or "1")


def pregunta(datos: dict):
    """La pregunta elegida en el bloque (o None si todavía no se eligió)."""
    if not datos.get("taller"):
        return None
    for q in preguntas(datos["taller"], datos.get("original", True), datos.get("semilla", "1")):
        if q.id == datos.get("pregunta"):
            return q
    return None


def calificar_bloque(datos: dict) -> dict | None:
    """Calificación de las respuestas guardadas: {enunciado, puntos, maximo, partes: [...], solucion}. None sin pregunta."""
    q = pregunta(datos)
    if q is None:
        return None
    respuestas = {k: (v if v != "" else None) for k, v in (datos.get("respuestas") or {}).items()}
    cal = calificar(q, respuestas)
    partes = []
    for p in q.partes:
        r = cal.resultados[p.clave]
        partes.append({"clave": p.clave, "etiqueta": p.etiqueta, "tipo": p.tipo, "unidad": p.unidad if p.tipo == NUM else "",
                       "respuesta": respuestas.get(p.clave) or "", "estado": r.estado, "estado_texto": ESTADOS.get(r.estado, r.estado),
                       "mensaje": r.mensaje, "correcta": p.respuesta_correcta() if r.estado == OK or datos.get("incluir_solucion") else "",
                       "explicacion": p.explicacion})
    return {"id": q.id, "enunciado": q.enunciado, "puntos": cal.puntos, "maximo": cal.maximo, "partes": partes,
            "solucion": q.solucion if datos.get("incluir_solucion") else "", "nota": q.nota}
