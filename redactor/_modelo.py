"""
redactor/_modelo.py — Documento del cuaderno de informes: bloques, valores por defecto y archivo .json
=====================================================================================================

Un documento es una lista de bloques (título, texto, ecuación, desarrollo paso a paso, gráfica, tabla, simulador, taller).
Se guarda como un archivo .json que la persona descarga y vuelve a cargar. Un archivo cargado NUNCA se ejecuta: se valida
campo por campo (tipos, tamaños, bloques conocidos) y lo que sobra o no es válido se descarta o se rechaza con un mensaje.
"""

from __future__ import annotations

import json
import math
import uuid
from copy import deepcopy

FORMATO = "quantum-lab-cuaderno"
VERSION = 1
MAX_BYTES = 2_000_000
MAX_BLOQUES = 300
MAX_TEXTO = 20_000

# tipo → (nombre en la interfaz, campos con su valor por defecto). El tipo del valor por defecto fija el tipo del campo.
TIPOS: dict[str, tuple[str, dict]] = {
    "titulo": ("Título de sección", {"texto": "Nueva sección", "nivel": 1}),
    "texto": ("Texto", {"texto": ""}),
    "ecuacion": ("Ecuación", {"latex": "E = h\\nu", "etiqueta": ""}),
    "desarrollo": ("Desarrollo paso a paso", {"lineas": "", "datos": "", "tol_pct": 1.0, "comentario": "", "marcas": False}),
    "grafica_funcion": ("Gráfica de una función", {"expresiones": "sin(x)", "variable": "x", "xmin": 0.0, "xmax": 6.28,
                                                   "constantes": "", "titulo": "", "xlabel": "x", "ylabel": "y", "pie": ""}),
    "grafica_datos": ("Gráfica de datos", {"tabla": "", "tipo": "puntos", "titulo": "", "xlabel": "x", "ylabel": "y", "pie": ""}),
    "simulador": ("Resultado de un simulador", {"sim": "caja", "valores": {}, "pie": ""}),
    "taller": ("Pregunta de un taller", {"taller": "", "original": True, "semilla": "1", "pregunta": "", "respuestas": {},
                                          "incluir_solucion": False}),
    "tabla": ("Tabla", {"titulo": "", "encabezados": ["Magnitud", "Valor", "Unidad"], "filas": [["", "", ""]]}),
}


class ErrorDocumento(ValueError):
    """El archivo no es un cuaderno válido. El mensaje está en español y se muestra tal cual."""


def nuevo_id() -> str:
    return uuid.uuid4().hex[:10]


def nuevo_bloque(tipo: str, datos: dict | None = None) -> dict:
    """Bloque nuevo del tipo dado; `datos` reemplaza campos por defecto (los que no existen se ignoran)."""
    if tipo not in TIPOS:
        raise ErrorDocumento(f"Tipo de bloque desconocido: {tipo!r}.")
    base = deepcopy(TIPOS[tipo][1])
    base.update({k: v for k, v in (datos or {}).items() if k in base})
    return {"id": nuevo_id(), "tipo": tipo, "datos": base}


def documento_vacio(titulo: str = "Mi informe", autor: str = "") -> dict:
    return {"formato": FORMATO, "version": VERSION, "titulo": titulo, "autor": autor, "bloques": []}


# ---------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------
def _texto(valor, nombre: str) -> str:
    if not isinstance(valor, str):
        raise ErrorDocumento(f"El campo «{nombre}» debe ser texto.")
    if len(valor) > MAX_TEXTO:
        raise ErrorDocumento(f"El campo «{nombre}» es demasiado largo (máximo {MAX_TEXTO} caracteres).")
    return valor


def _campo(valor, defecto, nombre: str):
    """Valida `valor` con el tipo de `defecto`; devuelve el valor limpio."""
    if isinstance(defecto, bool):
        if not isinstance(valor, bool):
            raise ErrorDocumento(f"El campo «{nombre}» debe ser verdadero o falso.")
        return valor
    if isinstance(defecto, int):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ErrorDocumento(f"El campo «{nombre}» debe ser un número entero.")
        return valor
    if isinstance(defecto, float):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
            raise ErrorDocumento(f"El campo «{nombre}» debe ser un número finito.")
        return float(valor)
    if isinstance(defecto, str):
        return _texto(valor, nombre)
    if isinstance(defecto, dict):
        if not isinstance(valor, dict) or len(valor) > 200:
            raise ErrorDocumento(f"El campo «{nombre}» no es válido.")
        salida = {}
        for k, v in valor.items():
            if not isinstance(k, str) or len(k) > 100 or isinstance(v, (dict, list)):
                raise ErrorDocumento(f"El campo «{nombre}» contiene valores no válidos.")
            salida[k] = _texto(v, nombre) if isinstance(v, str) else v
            if not isinstance(salida[k], (str, int, float, bool)):
                raise ErrorDocumento(f"El campo «{nombre}» contiene valores no válidos.")
        return salida
    if isinstance(defecto, list):
        if not isinstance(valor, list) or len(valor) > 500:
            raise ErrorDocumento(f"El campo «{nombre}» no es válido.")
        if defecto and isinstance(defecto[0], list):                      # lista de filas
            filas = []
            for fila in valor:
                if not isinstance(fila, list) or len(fila) > 20:
                    raise ErrorDocumento(f"El campo «{nombre}» no es una tabla válida.")
                filas.append([_texto(c, nombre) for c in fila])
            return filas
        return [_texto(c, nombre) for c in valor]
    raise ErrorDocumento(f"Campo desconocido: {nombre}.")                  # no debería ocurrir


def validar_documento(doc) -> dict:
    """Devuelve un documento limpio o lanza ErrorDocumento."""
    if not isinstance(doc, dict) or doc.get("formato") != FORMATO:
        raise ErrorDocumento("El archivo no es un cuaderno de QUANTUM LAB (falta o no coincide el campo «formato»).")
    if not isinstance(doc.get("version"), int) or doc["version"] > VERSION or doc["version"] < 1:
        raise ErrorDocumento(f"Versión de cuaderno no compatible: {doc.get('version')!r} (esta aplicación entiende hasta la {VERSION}).")
    bloques = doc.get("bloques")
    if not isinstance(bloques, list):
        raise ErrorDocumento("El cuaderno no tiene una lista de bloques.")
    if len(bloques) > MAX_BLOQUES:
        raise ErrorDocumento(f"El cuaderno tiene demasiados bloques (máximo {MAX_BLOQUES}).")
    limpio = documento_vacio(_texto(doc.get("titulo", ""), "titulo"), _texto(doc.get("autor", ""), "autor"))
    vistos = set()
    for i, b in enumerate(bloques, 1):
        if not isinstance(b, dict) or b.get("tipo") not in TIPOS or not isinstance(b.get("datos", {}), dict):
            raise ErrorDocumento(f"El bloque {i} no es válido (tipo desconocido o sin datos).")
        defecto = TIPOS[b["tipo"]][1]
        datos = deepcopy(defecto)
        for clave, valor in b.get("datos", {}).items():
            if clave in defecto:                                           # los campos desconocidos se descartan
                datos[clave] = _campo(valor, defecto[clave], f"bloque {i}: {clave}")
        bid = b.get("id") if isinstance(b.get("id"), str) and 0 < len(b["id"]) <= 32 and b["id"].isalnum() else nuevo_id()
        if bid in vistos:
            bid = nuevo_id()
        vistos.add(bid)
        limpio["bloques"].append({"id": bid, "tipo": b["tipo"], "datos": datos})
    return limpio


# ---------------------------------------------------------------------
# Archivo
# ---------------------------------------------------------------------
def a_json(doc: dict) -> bytes:
    """Cuaderno como bytes UTF-8 (JSON con sangría, legible)."""
    return json.dumps(validar_documento(doc), ensure_ascii=False, indent=1).encode("utf-8")


def desde_json(contenido: bytes | str) -> dict:
    if isinstance(contenido, str):
        contenido = contenido.encode("utf-8")
    if len(contenido) > MAX_BYTES:
        raise ErrorDocumento(f"El archivo es demasiado grande (máximo {MAX_BYTES // 1_000_000} MB).")
    try:
        doc = json.loads(contenido.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ErrorDocumento("El archivo no es un JSON válido. Carga un cuaderno descargado de QUANTUM LAB.") from None
    return validar_documento(doc)
