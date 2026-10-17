"""biblioteca/_modelo.py — Estructuras de datos de la Biblioteca científica."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Termino:
    id: str
    nombre: str
    definicion: str                  # 1–3 frases, Markdown
    ecuacion: str = ""               # LaTeX (sin $$)
    relacionados: tuple = ()         # ids de otros términos
    tema: str = ""                   # id del Centro de teoría (ejercicios._modelo.TEMAS)
    simulador: str = ""              # clave de página de un simulador
    cuidado: str = ""                # confusión frecuente (Markdown)


@dataclass(frozen=True)
class Paso:
    """Un paso de una derivación: qué se hace (texto) y la expresión resultante (LaTeX)."""
    texto: str
    latex: str


@dataclass(frozen=True)
class Derivacion:
    id: str
    titulo: str
    tema: str                        # id del Centro de teoría
    parte_de: str                    # hipótesis de partida (Markdown)
    pasos: tuple                     # tuple[Paso]
    conclusion: str                  # resultado y su significado físico (Markdown)
    comprobacion: object = None      # función () -> (descripcion, calculado, referencia, unidad_latex) o None
    simulador: str = ""


@dataclass(frozen=True)
class Referencia:
    id: str
    tipo: str                        # «Libro», «Artículo original», «Datos», «Simulación educativa», «Documentación»
    cita: str
    para: str                        # para qué sirve en este laboratorio
    enlace: str = ""


@dataclass(frozen=True)
class Relacion:
    origen: str                      # id de término
    destino: str
    etiqueta: str                    # «se calcula con», «implica», «se mide con»…
