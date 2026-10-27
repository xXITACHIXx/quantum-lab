"""
redactor/_expr.py — Lectura SEGURA de expresiones matemáticas escritas por el estudiante
========================================================================================

Convierte texto como «hbar^2 pi^2 / (2 m a^2)» en una expresión de SymPy. SymPy interpreta el texto con `eval`, así que
antes de dárselo se aplica una lista blanca estricta: solo caracteres matemáticos, nombres de funciones conocidas y
símbolos que son identificadores simples. Se rechazan atributos (`x.y`), corchetes, comillas, guiones bajos dobles,
palabras clave de Python y exponentes enormes que bloquearían el cálculo. Los errores se explican en español.

Los nombres de varias letras (hbar, omega…) son un único símbolo; la letra `e` es la constante de Euler.
Notación admitida: `^` o `**` para potencias, multiplicación implícita («2x», «2 pi r»), funciones sin, cos, tan, exp, log
(natural), ln, sqrt, asin, acos, atan, sinh, cosh, tanh, abs; constantes `pi` y `e`; nombres griegos (alpha, hbar…).
"""

from __future__ import annotations

import math
import re
from tokenize import TokenError

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    function_exponentiation,
    implicit_multiplication,
    parse_expr,
    standard_transformations,
)

MAX_LONGITUD = 300
FUNCIONES = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh, "abs": sp.Abs,
}
CONSTANTES = {"pi": sp.pi, "e": sp.E}
PROHIBIDAS = {"lambda", "import", "exec", "eval", "open", "class", "def", "global", "yield", "assert", "del", "os", "sys",
              "getattr", "setattr", "compile", "input", "print", "lambdify"}
_CARACTERES = re.compile(r"^[0-9A-Za-z_+\-*/^().,\sΑ-Ωα-ωħ·×−]+$")
# Sin `split_symbols`: «hbar», «omega» o «lambda» son UN símbolo; para multiplicar letras se escribe «m c^2» o «m*c^2».
_TRANSFORMACIONES = standard_transformations + (implicit_multiplication, function_exponentiation, convert_xor)


class ErrorExpresion(ValueError):
    """La expresión no se pudo leer o no es segura. El mensaje está en español y se muestra tal cual."""


def _normalizar(texto: str) -> str:
    t = str(texto).strip()
    t = t.replace("−", "-").replace("×", "*").replace("·", "*").replace("ħ", "hbar").replace("²", "^2").replace("³", "^3")
    t = t.replace("√", "sqrt")
    return t


def _comprobar(t: str) -> None:
    if not t:
        raise ErrorExpresion("La línea está vacía.")
    if len(t) > MAX_LONGITUD:
        raise ErrorExpresion(f"La expresión es demasiado larga (máximo {MAX_LONGITUD} caracteres).")
    if not _CARACTERES.match(t):
        raise ErrorExpresion("Hay caracteres no permitidos. Usa números, letras, + - * / ^ ( ) y funciones como sqrt(), sin(), exp().")
    if "__" in t or re.search(r"(?<!\d)\.(?!\d)", t) or re.search(r"[A-Za-z_]\s*\.", t):
        raise ErrorExpresion("No se permiten puntos fuera de los números decimales (por ejemplo «x.y»).")
    for palabra in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t):
        if palabra.lower() in PROHIBIDAS or palabra.startswith("_"):
            raise ErrorExpresion(f"La palabra «{palabra}» no está permitida en una expresión matemática.")
    if re.search(r"\d[eE][+-]?\d{4,}", t):
        raise ErrorExpresion("El exponente de un número en notación científica es demasiado grande.")
    if re.search(r"\d{16,}", t):
        raise ErrorExpresion("Un número tiene demasiadas cifras; usa notación científica (por ejemplo 1.5e-30).")
    for m in re.finditer(r"(?:\^|\*\*)\s*\(?\s*([+-]?\d+(?:\.\d+)?)", t):
        if abs(float(m.group(1))) > 100:
            raise ErrorExpresion("Un exponente es demasiado grande; la comprobación no se puede hacer con potencias tan altas.")
    if t.count("^") + t.count("**") > 8:
        raise ErrorExpresion("Hay demasiadas potencias anidadas; divide la operación en pasos.")


def _revisar_arbol(expr: sp.Basic) -> None:
    """
    Con la expresión SIN evaluar, rechaza potencias numéricas cuyo resultado sería gigantesco («9**9**9»), que bloquearían
    el cálculo. Se recorre de las hojas hacia la raíz: cada potencia interna ya fue comprobada cuando se mide la externa.
    """
    for nodo in sp.postorder_traversal(expr):
        if isinstance(nodo, sp.Pow) and nodo.base.is_number and nodo.exp.is_number:
            try:
                base, exp = abs(float(nodo.base)), float(nodo.exp)
                magnitud = abs(exp) * (abs(math.log10(base)) if base > 0 else 0.0)
            except (TypeError, ValueError, OverflowError):
                raise ErrorExpresion("Una potencia numérica es demasiado grande o no está definida.") from None
            if magnitud > 100:
                raise ErrorExpresion("Una potencia numérica produce un número demasiado grande; divide la operación en pasos.")


def leer_expresion(texto: str, evaluar: bool = True) -> sp.Expr:
    """
    Expresión de SymPy a partir del texto. `evaluar=False` conserva la forma escrita (para mostrarla tal cual).
    Lanza ErrorExpresion con un mensaje comprensible.
    """
    t = _normalizar(texto)
    _comprobar(t)
    if t.count("(") != t.count(")"):
        raise ErrorExpresion("Los paréntesis no están balanceados.")
    local = {**FUNCIONES, **CONSTANTES}
    try:
        expr = parse_expr(t, local_dict=local, global_dict={"Symbol": sp.Symbol, "Integer": sp.Integer, "Float": sp.Float,
                                                             "Rational": sp.Rational, "Mul": sp.Mul, "Add": sp.Add,
                                                             "Pow": sp.Pow},
                          transformations=_TRANSFORMACIONES, evaluate=False)
        _revisar_arbol(expr)
        if evaluar:
            expr = expr.doit()
        if expr.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
            raise ErrorExpresion("La expresión contiene una división entre cero o un valor indefinido.")
    except ErrorExpresion:
        raise
    except ZeroDivisionError:
        raise ErrorExpresion("La expresión divide entre cero.") from None
    except (SyntaxError, TypeError, ValueError, AttributeError, NameError, sp.SympifyError, TokenError) as error:
        raise ErrorExpresion(f"No se entiende la expresión «{texto.strip()}». Revisa los operadores y los paréntesis "
                             f"({type(error).__name__}).") from None
    if not isinstance(expr, sp.Basic):
        raise ErrorExpresion(f"«{texto.strip()}» no es una expresión matemática.")
    return expr


def partes_de_igualdad(texto: str) -> list[str]:
    """Divide «a = b = c» en ['a', 'b', 'c']. Rechaza «==», «<=», etc."""
    t = str(texto)
    if re.search(r"[<>!]=|==|=>|=<", t):
        raise ErrorExpresion("Usa un único signo «=» entre las partes de una igualdad.")
    return [p for p in (x.strip() for x in t.split("=")) if p != ""] if "=" in t else [t.strip()]


# Nombres que en física suelen ser constantes: se muestran con su símbolo en LaTeX.
_NOMBRES_LATEX = {"hbar": r"\hbar", "h": "h", "c": "c", "me": "m_e", "m_e": "m_e", "mp": "m_p", "kB": "k_B", "k_B": "k_B",
                  "lam": r"\lambda", "lambda_": r"\lambda", "nu": r"\nu", "omega": r"\omega", "psi": r"\psi", "Psi": r"\Psi",
                  "theta": r"\theta", "phi": r"\phi", "mu": r"\mu"}


def a_latex(expr: sp.Basic) -> str:
    """LaTeX de una expresión (subconjunto que entiende el motor de PDF: Matplotlib mathtext)."""
    nombres = {s: _NOMBRES_LATEX[s.name] for s in expr.free_symbols if s.name in _NOMBRES_LATEX}
    return sp.latex(expr, symbol_names=nombres, mul_symbol=None, inv_trig_style="power")

