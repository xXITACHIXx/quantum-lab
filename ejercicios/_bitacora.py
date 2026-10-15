"""
ejercicios/_bitacora.py — Registro de intentos del estudiante (sin Streamlit, probado con pytest).

Por cada ejercicio se guarda cuántas veces se comprobó la respuesta, cuántas fue completamente correcta, cuántas veces se abrió la
solución y qué errores típicos detectó el calificador (el mensaje del diagnóstico → número de veces). Con ese registro se calculan
los temas más débiles y los errores más frecuentes.
"""

from __future__ import annotations

from talleres._calificar import CASI, MAL

SIN_PATRON = "Respuesta incorrecta sin un patrón de error identificado"


def nuevo() -> dict:
    return {"intentos": 0, "aciertos": 0, "solucion": 0, "errores": {}}


def registrar_intento(bitacora: dict, ej_id: str, calificacion) -> bool:
    """Anota una comprobación. Devuelve True si todas las partes fueron correctas."""
    reg = bitacora.setdefault(ej_id, nuevo())
    reg["intentos"] += 1
    completo = calificacion.fraccion >= 0.999
    if completo:
        reg["aciertos"] += 1
    for r in calificacion.resultados.values():
        if r.estado == CASI:
            reg["errores"][r.mensaje] = reg["errores"].get(r.mensaje, 0) + 1
        elif r.estado == MAL:
            reg["errores"][SIN_PATRON] = reg["errores"].get(SIN_PATRON, 0) + 1
    return completo


def registrar_solucion(bitacora: dict, ej_id: str) -> None:
    bitacora.setdefault(ej_id, nuevo())["solucion"] += 1


def errores_frecuentes(bitacora: dict) -> list[tuple[str, int, list[str]]]:
    """[(mensaje, veces, ids de ejercicios)] de mayor a menor frecuencia; excluye las respuestas sin patrón identificado."""
    total: dict[str, int] = {}
    donde: dict[str, list[str]] = {}
    for ej_id, reg in bitacora.items():
        for mensaje, n in reg["errores"].items():
            if mensaje == SIN_PATRON:
                continue
            total[mensaje] = total.get(mensaje, 0) + n
            donde.setdefault(mensaje, []).append(ej_id)
    return sorted(((m, n, sorted(donde[m])) for m, n in total.items()), key=lambda t: (-t[1], t[0]))


def sin_patron(bitacora: dict) -> int:
    return sum(reg["errores"].get(SIN_PATRON, 0) for reg in bitacora.values())


def totales(bitacora: dict) -> tuple[int, int]:
    """(intentos, aciertos) sumados sobre todos los ejercicios."""
    return sum(r["intentos"] for r in bitacora.values()), sum(r["aciertos"] for r in bitacora.values())


def por_tema(bitacora: dict, ejercicios, hechos, repasar) -> list[dict]:
    """Una fila por tema: ejercicios, resueltos, por repasar, intentos, aciertos y precisión (None si no hay intentos)."""
    filas: dict[str, dict] = {}
    for e in ejercicios:
        f = filas.setdefault(e.tema, {"tema": e.tema, "ejercicios": 0, "resueltos": 0, "por_repasar": 0, "intentos": 0, "aciertos": 0})
        f["ejercicios"] += 1
        f["resueltos"] += e.id in hechos
        f["por_repasar"] += e.id in repasar
        reg = bitacora.get(e.id)
        if reg:
            f["intentos"] += reg["intentos"]
            f["aciertos"] += reg["aciertos"]
    for f in filas.values():
        f["precision"] = f["aciertos"] / f["intentos"] if f["intentos"] else None
    return list(filas.values())


def depurar(datos, ids_validos) -> dict:
    """Bitácora leída de un archivo: solo ids conocidos y contadores enteros no negativos."""
    limpia: dict = {}
    if not isinstance(datos, dict):
        return limpia
    validos = set(ids_validos)

    def entero(x) -> int:
        return x if isinstance(x, int) and not isinstance(x, bool) and x >= 0 else 0

    for ej_id, reg in datos.items():
        if ej_id not in validos or not isinstance(reg, dict):
            continue
        errores = reg.get("errores", {})
        intentos = entero(reg.get("intentos"))
        limpia[ej_id] = {"intentos": intentos, "aciertos": min(entero(reg.get("aciertos")), intentos),
                         "solucion": entero(reg.get("solucion")),
                         "errores": {str(k): entero(v) for k, v in errores.items() if entero(v)} if isinstance(errores, dict) else {}}
    return limpia


def combinar(a: dict, b: dict) -> dict:
    """Suma dos bitácoras (para cargar una copia de seguridad sin perder lo ya hecho)."""
    salida = {k: {**v, "errores": dict(v["errores"])} for k, v in a.items()}
    for ej_id, reg in b.items():
        destino = salida.setdefault(ej_id, nuevo())
        for campo in ("intentos", "aciertos", "solucion"):
            destino[campo] += reg[campo]
        for m, n in reg["errores"].items():
            destino["errores"][m] = destino["errores"].get(m, 0) + n
    return salida
