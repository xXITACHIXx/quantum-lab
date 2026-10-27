"""
redactor/_unidades.py — Análisis dimensional de los desarrollos del cuaderno
============================================================================

Una unidad se escribe entre corchetes después de un número o de una expresión: «3.97e-19 [J]», «500 [nm]», «h = 6.626e-34 [J s]».
Cada unidad se reduce a (factor a SI, dimensión) con siete exponentes: kg, m, s, A, K, mol, cd. Con eso se comprueba que
  · en una igualdad, los dos lados tengan la misma dimensión;
  · solo se sumen o resten magnitudes de la misma dimensión;
  · el argumento de sin, cos, exp, ln… sea adimensional.
Un símbolo sin unidad declarada es «desconocido»: no se inventa su dimensión y esa parte no se revisa. Es análisis dimensional:
coincidir en dimensión no prueba que la ecuación sea física, pero no coincidir sí delata un error.

Unidades admitidas: m, g, s, A, K, mol, cd, N, J, W, Pa, Hz, C, V, T, eV, Å, u, rad, deg y los prefijos y…Y (µ o u para micro). En un
cociente con varios factores abajo usa paréntesis: «J/(mol K)».
"""

from __future__ import annotations

import math
import re
from fractions import Fraction

import sympy as sp

CERO = (Fraction(0),) * 7                           # kg, m, s, A, K, mol, cd


class ErrorUnidades(ValueError):
    """Unidad mal escrita o magnitudes incompatibles. El mensaje está en español y se muestra tal cual."""


def _d(kg=0, m=0, s=0, a=0, k=0, mol=0, cd=0):
    return tuple(Fraction(x) for x in (kg, m, s, a, k, mol, cd))


# nombre → (factor al SI, dimensión). El gramo es 1e-3 kg porque el SI usa el kilogramo.
BASE = {
    "m": (1.0, _d(m=1)), "g": (1e-3, _d(kg=1)), "s": (1.0, _d(s=1)), "A": (1.0, _d(a=1)), "K": (1.0, _d(k=1)),
    "mol": (1.0, _d(mol=1)), "cd": (1.0, _d(cd=1)),
    "N": (1.0, _d(kg=1, m=1, s=-2)), "J": (1.0, _d(kg=1, m=2, s=-2)), "W": (1.0, _d(kg=1, m=2, s=-3)),
    "Pa": (1.0, _d(kg=1, m=-1, s=-2)), "Hz": (1.0, _d(s=-1)), "C": (1.0, _d(a=1, s=1)),
    "V": (1.0, _d(kg=1, m=2, s=-3, a=-1)), "T": (1.0, _d(kg=1, s=-2, a=-1)),
    "eV": (1.602176634e-19, _d(kg=1, m=2, s=-2)),            # e exacta (SI 2019)
    "Å": (1e-10, _d(m=1)), "u": (1.66053906660e-27, _d(kg=1)),   # CODATA 2018
    "rad": (1.0, CERO), "deg": (math.pi / 180.0, CERO),
}
PREFIJOS = {"y": -24, "z": -21, "a": -18, "f": -15, "p": -12, "n": -9, "µ": -6, "μ": -6, "u": -6, "m": -3, "c": -2, "d": -1,
            "k": 3, "M": 6, "G": 9, "T": 12, "P": 15}
# Dimensiones que tienen nombre propio (para escribir «J» en vez de «kg·m²/s²» en los mensajes)
NOMBRADAS = {_d(kg=1, m=2, s=-2): "J", _d(kg=1, m=1, s=-2): "N", _d(kg=1, m=2, s=-3): "W", _d(kg=1, m=-1, s=-2): "Pa",
             _d(s=-1): "Hz", _d(a=1, s=1): "C", _d(kg=1, m=2, s=-3, a=-1): "V", _d(kg=1, s=-2, a=-1): "T"}
_NOMBRES_BASE = ("kg", "m", "s", "A", "K", "mol", "cd")
_ATOMO = re.compile(r"\s*(?:([A-Za-zµμÅ]+)|(\d+)|(.))")


def _buscar(nombre: str) -> tuple[float, tuple]:
    if nombre in BASE:
        return BASE[nombre]
    if nombre == "kg":
        return 1.0, _d(kg=1)
    if len(nombre) > 1 and nombre[0] in PREFIJOS and nombre[1:] in BASE:
        f, dim = BASE[nombre[1:]]
        return f * 10.0 ** PREFIJOS[nombre[0]], dim
    raise ErrorUnidades(f"No conozco la unidad «{nombre}».")


def _sumar(a, b, signo=1):
    return tuple(x + signo * y for x, y in zip(a, b, strict=True))


class _Lector:
    """Gramática: expr := término ((* | / | espacio) término)* ; término := átomo [^ [-]entero] ; átomo := nombre | 1 | ( expr )."""

    def __init__(self, texto: str):
        self.t = texto.replace("·", "*").replace("−", "-").replace("²", "^2").replace("³", "^3").replace("⁻¹", "^-1").strip()
        self.i = 0

    def _ver(self):
        m = _ATOMO.match(self.t, self.i)
        return m

    def _saltar(self):
        while self.i < len(self.t) and self.t[self.i].isspace():
            self.i += 1

    def expr(self):
        f, dim = self.termino()
        while True:
            self._saltar()
            if self.i >= len(self.t) or self.t[self.i] == ")":
                return f, dim
            op = "*"
            if self.t[self.i] in "*/":
                op = self.t[self.i]
                self.i += 1
            f2, d2 = self.termino()
            f, dim = (f * f2, _sumar(dim, d2)) if op == "*" else (f / f2, _sumar(dim, d2, -1))

    def termino(self):
        f, dim = self.atomo()
        self._saltar()
        if self.i < len(self.t) and self.t[self.i] == "^":
            self.i += 1
            m = re.compile(r"\s*([+-]?\d+)").match(self.t, self.i)
            if not m:
                raise ErrorUnidades("Después de «^» va un número entero (por ejemplo m^2 o s^-1).")
            self.i = m.end()
            n = int(m.group(1))
            if abs(n) > 12:
                raise ErrorUnidades("El exponente de una unidad es demasiado grande.")
            return f ** n, tuple(x * n for x in dim)
        return f, dim

    def atomo(self):
        self._saltar()
        if self.i >= len(self.t):
            raise ErrorUnidades("Falta una unidad.")
        if self.t[self.i] == "(":
            self.i += 1
            r = self.expr()
            self._saltar()
            if self.i >= len(self.t) or self.t[self.i] != ")":
                raise ErrorUnidades("Falta cerrar un paréntesis en la unidad.")
            self.i += 1
            return r
        m = self._ver()
        if m and m.group(1):
            self.i = m.end()
            return _buscar(m.group(1))
        if m and m.group(2) == "1":
            self.i = m.end()
            return 1.0, CERO
        raise ErrorUnidades(f"No entiendo «{self.t[self.i:self.i + 8]}» en la unidad.")


def leer_unidad(texto: str) -> tuple[float, tuple]:
    """«kg m/s^2» → (factor al SI, dimensión). Lanza ErrorUnidades."""
    texto = str(texto).strip()
    if not texto or len(texto) > 60:
        raise ErrorUnidades("La unidad está vacía o es demasiado larga.")
    lector = _Lector(texto)
    f, dim = lector.expr()
    lector._saltar()
    if lector.i < len(lector.t):
        raise ErrorUnidades(f"Sobra «{lector.t[lector.i:]}» en la unidad «{texto}».")
    return f, dim


def escribir(dim: tuple) -> str:
    """Dimensión como texto («J», «kg·m²/s²», «sin unidades»)."""
    if all(x == 0 for x in dim):
        return "adimensional"
    if dim in NOMBRADAS:
        return f"{NOMBRADAS[dim]} (= {_texto_base(dim)})"
    return _texto_base(dim)


def _texto_base(dim: tuple) -> str:
    def pot(n, e):
        return n if e in (1, -1) else f"{n}^{e if e.denominator != 1 else int(e)}"
    arriba = [pot(n, e) for n, e in zip(_NOMBRES_BASE, dim, strict=True) if e > 0]
    abajo = [pot(n, -e) for n, e in zip(_NOMBRES_BASE, dim, strict=True) if e < 0]
    num = "·".join(arriba) or "1"
    return num if not abajo else f"{num}/" + ("·".join(abajo) if len(abajo) == 1 else "(" + "·".join(abajo) + ")")


# ---------------------------------------------------------------------
# Corchetes «[unidad]» en el texto
# ---------------------------------------------------------------------
_CORCHETES = re.compile(r"\[([^\[\]]*)\]\s*$")


def separar_unidad(parte: str) -> tuple[str, tuple[float, tuple] | None]:
    """«500 [nm]» → («500», (1e-9, dim m)). Sin corchetes → (parte, None). Lanza ErrorUnidades."""
    m = _CORCHETES.search(parte)
    resto = parte[: m.start()].strip() if m else parte
    if "[" in resto or "]" in resto:
        raise ErrorUnidades("Los corchetes de unidad van una sola vez y al final de cada expresión, por ejemplo «3.97e-19 [J]».")
    return (resto, leer_unidad(m.group(1))) if m else (parte, None)


# ---------------------------------------------------------------------
# Dimensión de una expresión
# ---------------------------------------------------------------------
_ADIMENSIONALES = (sp.sin, sp.cos, sp.tan, sp.asin, sp.acos, sp.atan, sp.sinh, sp.cosh, sp.tanh, sp.exp, sp.log)


def dimension(expr, tabla: dict) -> tuple | None:
    """
    Dimensión de la expresión según `tabla` {Symbol: dimensión}; None si algún símbolo no tiene unidad declarada.
    Lanza ErrorUnidades si la expresión suma magnitudes distintas o pone unidades dentro de una función trascendente.
    """
    if expr.is_number:
        return CERO
    if isinstance(expr, sp.Symbol):
        return tabla.get(expr)
    if isinstance(expr, sp.Add):
        dims = [(a, dimension(a, tabla)) for a in expr.args]
        conocidas = [(a, d) for a, d in dims if d is not None]
        for a, d in conocidas[1:]:
            if d != conocidas[0][1]:
                raise ErrorUnidades(f"Se suman magnitudes distintas: «{conocidas[0][0]}» es {escribir(conocidas[0][1])} y «{a}» es {escribir(d)}.")
        return None if len(conocidas) < len(dims) else conocidas[0][1]
    if isinstance(expr, sp.Mul):
        total = CERO
        for a in expr.args:
            d = dimension(a, tabla)
            if d is None:
                return None
            total = _sumar(total, d)
        return total
    if isinstance(expr, sp.Pow):
        d = dimension(expr.base, tabla)
        e = dimension(expr.exp, tabla)
        if e is not None and e != CERO:
            raise ErrorUnidades(f"El exponente «{expr.exp}» tiene unidades; debe ser un número.")
        if d is None:
            return None
        if d == CERO:
            return CERO
        if not expr.exp.is_Rational:
            raise ErrorUnidades(f"«{expr.base}» tiene unidades y su exponente «{expr.exp}» no es un número racional.")
        n = Fraction(int(expr.exp.p), int(expr.exp.q))
        return tuple(x * n for x in d)
    if isinstance(expr, sp.Abs):
        return dimension(expr.args[0], tabla)
    if isinstance(expr, _ADIMENSIONALES):
        d = dimension(expr.args[0], tabla)
        if d is not None and d != CERO:
            raise ErrorUnidades(f"El argumento de {expr.func.__name__} debe ser adimensional y «{expr.args[0]}» es {escribir(d)}.")
        return CERO
    return None
