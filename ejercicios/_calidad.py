"""
ejercicios/_calidad.py — Reglas de calidad de los ejercicios (para quien añada o edite uno).

`revisar(ej)` devuelve la lista de problemas encontrados (vacía si cumple todo). Lo usan las pruebas y `python -m ejercicios`.
"""

from __future__ import annotations

import re

from ejercicios._modelo import CLASE, CUADERNO, LIBRO, Ejercicio, TEMAS
from talleres._modelo import NUM

_PREFIJO_REF = {CLASE: "Semana", LIBRO: "Libro", CUADERNO: "Cuaderno"}
_PROHIBIDO = ("TODO", "XXX", "FIXME", "<<", ">>", "lorem")


def _dolares_balanceados(texto: str) -> bool:
    sin_bloques = texto.replace("$$", "")
    return sin_bloques.count("$") % 2 == 0 and texto.count("$$") % 2 == 0


def revisar(ej: Ejercicio) -> list[str]:
    p: list[str] = []
    if not re.fullmatch(r"[a-z][a-z0-9_]*", ej.id):
        p.append("el id debe ir en minúsculas, dígitos y guion bajo")
    if ej.fuente == CLASE:
        semana = re.match(r"Semana (\d+)", ej.referencia)
        if not semana or not ej.id.startswith(f"s{semana.group(1)}_"):
            p.append("el id de un ejercicio de clase empieza por s<semana>_ y debe coincidir con la referencia")
    elif ej.fuente == LIBRO and not re.match(r"[lh]\d", ej.id):
        p.append("el id de un ejercicio del libro empieza por l<N> (rotación y oscilador) o h<N> (hidrógeno)")
    elif ej.fuente == CUADERNO and not ej.id.startswith("c_"):
        p.append("el id de un ejercicio del cuaderno empieza por c_")
    if not ej.referencia.startswith(_PREFIJO_REF[ej.fuente]):
        p.append(f"la referencia de esta fuente debe empezar por «{_PREFIJO_REF[ej.fuente]}»")
    if ej.tema not in TEMAS:
        p.append(f"tema desconocido: {ej.tema}")
    if len(ej.titulo) > 80 or ej.titulo.endswith("."):
        p.append("el título debe tener a lo sumo 80 caracteres y no terminar en punto")
    if len(ej.enunciado.strip()) < 20:
        p.append("enunciado demasiado corto")
    if not ej.pistas or any(not str(x).strip() for x in ej.pistas):
        p.append("necesita al menos una pista y ninguna vacía")
    for texto, nombre in ((ej.enunciado, "enunciado"), (ej.solucion, "solución"), (ej.nota, "nota")):
        if not _dolares_balanceados(texto):
            p.append(f"signos $ desbalanceados en el {nombre}")
        if any(m in texto for m in _PROHIBIDO):
            p.append(f"texto provisional o plantilla sin rellenar en el {nombre}")
    pasos = [int(n) for n in re.findall(r"^#### Paso (\d+)", ej.solucion, flags=re.M)]
    if len(pasos) < 3:
        p.append("la solución debe tener al menos 3 pasos («#### Paso N · título»)")
    elif pasos != list(range(1, len(pasos) + 1)):
        p.append(f"los pasos deben numerarse 1, 2, 3… (hay {pasos})")
    claves = [x.clave for x in ej.partes]
    if len(claves) != len(set(claves)):
        p.append("claves de partes repetidas")
    for x in ej.partes:
        if x.tipo == NUM and not x.etiqueta.strip():
            p.append(f"la parte {x.clave} no tiene etiqueta")
    return p
