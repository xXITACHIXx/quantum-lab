"""
ejercicios/_ruta.py — Lógica de la Ruta de estudio (sin Streamlit, probada con pytest).

El curso no avanza por fechas, de modo que la ruta se organiza por dominio de cada tema y por dependencias físicas.
Cada tema tiene tres pasos:

    teoría        el estudiante marca que leyó el tema (no aplica si la teoría aún no está disponible)
    ejercicios    al menos el 75 % de los ejercicios del tema resueltos
    mini-examen   nota de 3.0 o más sobre 5.0 en un examen corto de ese tema (no aplica si no hay ejercicios comprobables)

Las marcas «teoría leída» y «mini-examen aprobado» viajan en la dirección de la página (parámetro `rut`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

FRACCION_EJERCICIOS = 0.75
NOTA_MINI = 3.0
MINI_N = 3
PRECISION_BAJA = 0.60
MIN_INTENTOS = 2

# Orden recomendado y prerrequisitos (ids del Centro de teoría).
ORDEN = ("fotoelectrico", "bohr", "de_broglie", "ondas", "operadores", "libre_pared", "caja", "conmutadores",
         "oscilador", "esfera", "hidrogeno", "espin", "aproximados")
PREREQ = {
    "fotoelectrico": (),
    "bohr": ("fotoelectrico",),
    "de_broglie": ("bohr",),
    "ondas": (),
    "operadores": ("ondas",),
    "libre_pared": ("operadores", "de_broglie"),
    "caja": ("libre_pared",),
    "conmutadores": ("operadores",),
    "oscilador": ("caja",),
    "esfera": ("caja", "conmutadores"),
    "hidrogeno": ("esfera", "bohr"),
    "espin": ("hidrogeno",),
    "aproximados": ("oscilador", "espin"),
}

TEORIA, EJERCICIOS, MINI = "teoria", "ejercicios", "mini"
NOMBRE_PASO = {TEORIA: "Teoría leída", EJERCICIOS: "Ejercicios resueltos", MINI: "Mini-examen aprobado"}
HECHO, PENDIENTE, NA = "hecho", "pendiente", "no aplica"


def marca_teoria(tema: str) -> str:
    return f"t:{tema}"


def marca_mini(tema: str) -> str:
    return f"m:{tema}"


def todas_las_marcas() -> tuple[str, ...]:
    return tuple(f(t) for t in ORDEN for f in (marca_teoria, marca_mini))


def requeridos(total: int) -> int:
    """Ejercicios que deben estar resueltos para dar por cumplido el paso (75 %, redondeado hacia arriba)."""
    return math.ceil(FRACCION_EJERCICIOS * total) if total else 0


@dataclass(frozen=True)
class EstadoTema:
    tema: str
    pasos: dict                    # {paso: HECHO | PENDIENTE | NA}
    resueltos: int
    total: int
    comprobables: int
    por_repasar: int
    precision: float | None
    intentos: int

    @property
    def aplicables(self) -> list[str]:
        return [p for p, e in self.pasos.items() if e != NA]

    @property
    def hechos(self) -> int:
        return sum(e == HECHO for e in self.pasos.values())

    @property
    def completo(self) -> bool:
        return all(e != PENDIENTE for e in self.pasos.values())

    @property
    def iniciado(self) -> bool:
        return self.hechos > 0 or self.resueltos > 0 or self.intentos > 0

    @property
    def debil(self) -> bool:
        return self.precision is not None and self.intentos >= MIN_INTENTOS and self.precision < PRECISION_BAJA

    @property
    def siguiente_paso(self) -> str | None:
        return next((p for p, e in self.pasos.items() if e == PENDIENTE), None)


def evaluar(marcas, filas: dict, teoria_disponible: dict) -> dict[str, EstadoTema]:
    """
    marcas: conjunto de marcas «t:…» y «m:…». filas: {tema: fila de `_bitacora.por_tema` + «comprobables»}.
    teoria_disponible: {tema: bool}. Devuelve {tema: EstadoTema} en el orden de la ruta.
    """
    salida = {}
    for tema in ORDEN:
        f = filas.get(tema, {})
        total, resueltos = f.get("ejercicios", 0), f.get("resueltos", 0)
        comprobables = f.get("comprobables", total)
        pasos = {
            TEORIA: (HECHO if marca_teoria(tema) in marcas else PENDIENTE) if teoria_disponible.get(tema) else NA,
            EJERCICIOS: (HECHO if resueltos >= requeridos(total) else PENDIENTE) if total else NA,
            MINI: (HECHO if marca_mini(tema) in marcas else PENDIENTE) if comprobables else NA,
        }
        salida[tema] = EstadoTema(tema, pasos, resueltos, total, comprobables, f.get("por_repasar", 0),
                                  f.get("precision"), f.get("intentos", 0))
    return salida


def prerrequisitos_flojos(tema: str, estados: dict) -> list[tuple[str, str]]:
    """[(prerrequisito, motivo)] de los prerrequisitos incompletos o con bajo desempeño."""
    flojos = []
    for p in PREREQ[tema]:
        e = estados[p]
        if e.debil:
            flojos.append((p, f"precisión de {100 * e.precision:.0f} % en {e.intentos} comprobaciones"))
        elif not e.completo and (e.iniciado or estados[tema].iniciado):     # sin actividad en ninguno de los dos, basta el «Requiere:»
            flojos.append((p, f"{e.hechos} de {len(e.aplicables)} pasos cumplidos"))
    return flojos


@dataclass(frozen=True)
class Sugerencia:
    tema: str | None
    paso: str | None
    motivo: str


def siguiente(estados: dict) -> Sugerencia:
    """
    Prioridad: 1) el tema con bajo desempeño de menor precisión (repasar sus ejercicios);
    2) el primer tema incompleto cuyos prerrequisitos estén completos; 3) el primer tema incompleto.
    """
    debiles = sorted((e for e in estados.values() if e.debil), key=lambda e: (e.precision, -e.intentos))
    if debiles:
        e = debiles[0]
        return Sugerencia(e.tema, EJERCICIOS, f"precisión de {100 * e.precision:.0f} % en {e.intentos} comprobaciones: conviene repasar antes de avanzar")
    pendientes = [e for e in estados.values() if not e.completo]
    if not pendientes:
        return Sugerencia(None, None, "ruta completada")
    for e in pendientes:
        if all(estados[p].completo for p in PREREQ[e.tema]):
            return Sugerencia(e.tema, e.siguiente_paso, "primer tema pendiente con prerrequisitos cumplidos")
    e = pendientes[0]
    return Sugerencia(e.tema, e.siguiente_paso, "primer tema pendiente de la ruta")


def validar_estructura(temas_validos) -> list[str]:
    """Problemas de la definición de la ruta (vacía si es consistente: ids conocidos, orden topológico, sin ciclos)."""
    problemas = []
    validos = set(temas_validos)
    if set(ORDEN) != set(PREREQ):
        problemas.append("ORDEN y PREREQ no tienen los mismos temas")
    for t in ORDEN:
        if t not in validos:
            problemas.append(f"tema desconocido: {t}")
    visto = set()
    for t in ORDEN:
        for p in PREREQ.get(t, ()):
            if p not in visto:
                problemas.append(f"{t} aparece antes que su prerrequisito {p}")
        visto.add(t)
    if len(set(ORDEN)) != len(ORDEN):
        problemas.append("ORDEN tiene temas repetidos")
    return problemas
