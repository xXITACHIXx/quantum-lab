"""
ejercicios/_modelo.py — Modelo de un ejercicio de práctica.

Un ejercicio tiene enunciado, una o varias partes que el estudiante puede comprobar (opcional), pistas y una solución
paso a paso que se puede consultar en cualquier momento. Las partes reutilizan el calificador de los talleres
(`talleres._modelo.Parte`): numéricas con tolerancia y diagnóstico de errores típicos, o de opción múltiple.
"""

from __future__ import annotations

from dataclasses import dataclass

from talleres._modelo import NUM, OPC, Parte, calificar as _calificar_pregunta, Pregunta

# Fuentes
CLASE = "Diapositivas de clase"
LIBRO = "Libro (cuaderno)"
CUADERNO = "Ejercicios de clase (cuaderno)"
FUENTES = (CLASE, LIBRO, CUADERNO)

# Dificultad orientativa
BASICO, MEDIO, AVANZADO = "Básico", "Intermedio", "Avanzado"

# Temas (id del Centro de teoría, título corto)
TEMAS = {
    "fotoelectrico": "Efecto fotoeléctrico",
    "bohr": "Modelo de Bohr y espectros",
    "de_broglie": "Ondas de materia",
    "ondas": "Ondas y números complejos",
    "operadores": "Operadores, autofunciones y normalización",
    "libre_pared": "Partícula libre y barreras",
    "caja": "Partícula en una caja",
    "conmutadores": "Conmutadores e incertidumbre",
    "oscilador": "Oscilador armónico",
    "esfera": "Rotación y momento angular",
    "hidrogeno": "Átomo de hidrógeno",
    "espin": "Espín y determinantes de Slater",
    "aproximados": "Método variacional",
}


@dataclass(frozen=True)
class Ejercicio:
    id: str
    titulo: str
    fuente: str                         # CLASE, LIBRO o CUADERNO
    referencia: str                     # «Semana 1 · Example Problem 1», «Libro · ejercicio 8»…
    tema: str                           # clave de TEMAS (id del Centro de teoría)
    enunciado: str                      # Markdown
    solucion: str                       # Markdown: solución paso a paso
    partes: tuple = ()                  # Parte(...) comprobables; vacío si es una demostración
    pistas: tuple = ()                  # Markdown, de menos a más
    dificultad: str = MEDIO
    nota: str = ""                      # aclaraciones (erratas de la fuente, datos añadidos)

    @property
    def comprobable(self) -> bool:
        return bool(self.partes)


def llenar(texto: str, **valores) -> str:
    """Sustituye «<<nombre>>» por el valor dado. Permite escribir LaTeX con llaves sin duplicarlas como en un f-string."""
    for k, v in valores.items():
        texto = texto.replace(f"<<{k}>>", str(v))
    if "<<" in texto:
        raise KeyError(f"Falta un valor en la plantilla: {texto[texto.index('<<'):texto.index('<<') + 30]}")
    return texto


def calificar(ej: Ejercicio, respuestas: dict):
    """Califica las partes comprobables (sobre 1 punto)."""
    return _calificar_pregunta(Pregunta(ej.id, ej.enunciado, 1.0, ej.partes, ej.solucion), respuestas)


__all__ = ["Ejercicio", "llenar", "Parte", "NUM", "OPC", "CLASE", "LIBRO", "CUADERNO", "FUENTES", "TEMAS",
           "BASICO", "MEDIO", "AVANZADO", "calificar"]
