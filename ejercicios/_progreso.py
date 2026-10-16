"""
ejercicios/_progreso.py — Progreso del estudiante (qué ejercicios ya resolvió).

Sin cuentas ni base de datos: el progreso viaja en la **dirección de la página** (parámetro `prog`), de modo que
guardar la página en favoritos o copiar el enlace conserva lo avanzado, y además se puede descargar/cargar un archivo
JSON como copia de seguridad. Cada ejercicio se identifica con 4 caracteres derivados de su id (CRC-32 truncado a 24 bits),
así que añadir o reordenar ejercicios nunca descoloca el progreso guardado.
"""

from __future__ import annotations

import base64
import json
import zlib

VERSION = 2


def token(ej_id: str) -> str:
    """4 caracteres estables (base64 URL-safe de 3 bytes) que representan un id de ejercicio."""
    crc = zlib.crc32(ej_id.encode("utf-8")) & 0xFFFFFF
    return base64.urlsafe_b64encode(crc.to_bytes(3, "big")).decode("ascii")


def codificar(hechos, ids_validos) -> str:
    """Código para la URL: tokens concatenados, en el orden de `ids_validos`."""
    return "".join(token(i) for i in ids_validos if i in hechos)


def decodificar(codigo: str | None, ids_validos) -> set[str]:
    """Ids cuyo token aparece en el código. Un código manipulado o antiguo solo se ignora."""
    if not codigo or not isinstance(codigo, str):
        return set()
    codigo = codigo.strip()
    presentes = {codigo[i:i + 4] for i in range(0, len(codigo) - len(codigo) % 4, 4)}
    return {i for i in ids_validos if token(i) in presentes}


def a_json(hechos, ids_validos, repasar=(), bitacora=None, examenes=None, ruta=()) -> str:
    """Copia de seguridad completa: resueltos, pendientes de repaso, bitácora de intentos e historial de exámenes."""
    return json.dumps({"quantum_lab": "ejercicios", "version": VERSION,
                       "resueltos": [i for i in ids_validos if i in hechos],
                       "repasar": [i for i in ids_validos if i in repasar],
                       "bitacora": bitacora or {}, "examenes": examenes or [], "ruta": sorted(ruta)}, ensure_ascii=False, indent=1)


def leer_copia(datos: bytes | str, ids_validos, marcas_validas=()) -> dict:
    """
    Lee un archivo exportado y devuelve {"resueltos", "repasar", "bitacora", "examenes", "ruta"} ya depurados.
    Admite la versión 1 (solo resueltos). Lanza ValueError si no es un progreso de QUANTUM LAB.
    """
    from ejercicios import _bitacora
    try:
        obj = json.loads(datos)
    except (ValueError, TypeError) as exc:
        raise ValueError("El archivo no es un JSON válido.") from exc
    if not isinstance(obj, dict) or obj.get("quantum_lab") != "ejercicios" or not isinstance(obj.get("resueltos"), list):
        raise ValueError("El archivo no es un progreso de los Ejercicios de práctica.")
    validos = set(ids_validos)

    def ids(clave):
        lista = obj.get(clave, [])
        return {i for i in lista if isinstance(i, str) and i in validos} if isinstance(lista, list) else set()

    examenes = []
    for x in obj.get("examenes", []) if isinstance(obj.get("examenes"), list) else []:
        if isinstance(x, dict) and isinstance(x.get("nota"), (int, float)) and isinstance(x.get("fecha"), str):
            examenes.append({"fecha": x["fecha"][:32], "ejercicios": [i for i in x.get("ejercicios", []) if i in validos],
                             "nota": float(min(max(x["nota"], 0.0), 5.0)),
                             "porcentaje": float(min(max(x.get("porcentaje", 0.0), 0.0), 100.0)),
                             "minutos_usados": float(max(x.get("minutos_usados", 0.0), 0.0)),
                             "minutos_totales": float(max(x.get("minutos_totales", 0.0), 0.0)),
                             "temas": [str(t)[:60] for t in x.get("temas", [])][:20]})
    return {"resueltos": ids("resueltos"), "repasar": ids("repasar"),
            "bitacora": _bitacora.depurar(obj.get("bitacora"), ids_validos), "examenes": examenes,
            "ruta": {m for m in obj.get("ruta", []) if isinstance(m, str) and m in set(marcas_validas)} if isinstance(obj.get("ruta", []), list) else set()}


def desde_json(datos: bytes | str, ids_validos) -> set[str]:
    """Solo los ejercicios resueltos de un archivo exportado (compatibilidad con la versión 1)."""
    return leer_copia(datos, ids_validos)["resueltos"]
