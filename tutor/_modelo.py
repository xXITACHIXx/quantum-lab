"""tutor/_modelo.py — Estructuras del tutor de errores conceptuales."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Concepcion:
    """Una confusión frecuente: qué se cree, por qué es incorrecta, cómo orientarla y cómo detectarla en un texto."""
    id: str
    concepto: str            # concepto que se confunde (título corto)
    error: str               # lo que el estudiante cree, dicho en una frase
    pista: str               # pregunta orientadora que no revela la respuesta
    explicacion: str         # explicación correcta
    contraste: str           # ecuación o dato que permite comprobarlo (LaTeX; puede ir vacío)
    glosario: tuple = ()     # ids de biblioteca._glosario
    tema: str = ""           # id de teoría
    simulador: str = ""      # clave de PAGINAS
    reglas: tuple = ()       # cada regla = tupla de regex (todas deben cumplirse en la misma oración); basta una regla
    con_negacion: bool = False   # True si el error mismo se expresa con «no» (no se descarta la oración por negación)
    excluye: str = ""        # regex: si aparece en la oración, no se marca (evita falsos positivos)
    frases_error: tuple = () # frases que SÍ deben detectarse (se usan como ejemplos y en las pruebas)
    frases_correctas: tuple = ()  # frases correctas parecidas que NO deben detectarse (pruebas)


@dataclass(frozen=True)
class PreguntaDiag:
    """Pregunta de opción múltiple donde cada distractor corresponde a una confusión concreta (o a ninguna: None)."""
    id: str
    tema: str
    enunciado: str
    opciones: tuple          # ((texto, concepcion_id | None), ...)
    correcta: int            # índice de la opción correcta
    explicacion: str         # por qué es correcta
    pista_general: str       # se muestra si el error no corresponde a una confusión catalogada
