"""
talleres/_calificar.py — Lectura de respuestas numéricas y calificación (sin Streamlit, probada con pytest).

Una respuesta numérica se acepta si coincide con el valor esperado dentro de una tolerancia relativa (por defecto 2 %,
porque se admiten masas atómicas y constantes redondeadas). Si no coincide, se busca el error típico que la explicaría:
un factor de 2π (ω frente a ν, h frente a ħ), un cambio de unidades (potencias de 10), un factor 2 o el signo.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

OK, CASI, MAL, VACIA, INVALIDA = "ok", "casi", "mal", "vacia", "invalida"

_SUPERINDICES = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")


def leer_numero(texto) -> float:
    """
    Lee un número escrito como lo haría un estudiante: «1,256e12», «1.256 x 10^12», «1,256×10¹²», «−3.57».
    Lanza ValueError con un mensaje claro si no se entiende o no es finito.
    """
    if isinstance(texto, (int, float)):
        valor = float(texto)
    else:
        t = str(texto).strip().lower().replace("−", "-").replace("–", "-").replace(" ", "")
        if not t:
            raise ValueError("Escribe un número.")
        t = t.replace(",", ".")
        # ×10¹² y x10^12 y *10**12 y ·10^-3  →  e12
        t = re.sub(r"([\d.])(?:×|x|\*|·)10(?:\^|\*\*)?([+-]?[\d⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)",
                   lambda m: f"{m.group(1)}e{m.group(2).translate(_SUPERINDICES)}", t)
        t = re.sub(r"(?<![\d.e])10(?:\^|\*\*)([+-]?\d+)", r"1e\1", t)         # «10^12» solo
        try:
            valor = float(t)
        except ValueError:
            raise ValueError("No entendí el número. Usa por ejemplo 1.256e12 o 1,256 x 10^12.") from None
    if not math.isfinite(valor):
        raise ValueError("El número debe ser finito.")
    return valor


@dataclass(frozen=True)
class Resultado:
    estado: str                 # ok | casi | mal | vacia | invalida
    mensaje: str = ""

    @property
    def correcto(self) -> bool:
        return self.estado == OK


def _factores_comunes() -> list[tuple[float, str]]:
    f = [(2 * math.pi, "te falta dividir entre 2π (o confundiste ω con ν, o h con ħ)"),
         (1 / (2 * math.pi), "te sobra dividir entre 2π: revisa si debías usar ħ en lugar de h, o ν en lugar de ω"),
         (2.0, "tu resultado es el doble: revisa un factor 2 (por ejemplo ½ en la energía o 2B frente a B)"),
         (0.5, "tu resultado es la mitad: revisa un factor 2 (por ejemplo ½ en la energía o 2B frente a B)"),
         (4.0, "tu resultado es 4 veces el esperado: revisa un cuadrado o un factor 2²"),
         (0.25, "tu resultado es la cuarta parte: revisa un cuadrado o un factor 2²")]
    for n in (3, 6, 9, 12, 2, 1):
        f.append((10.0 ** n, f"parece un problema de unidades: tu valor es 10^{n} veces el esperado"))
        f.append((10.0 ** -n, f"parece un problema de unidades: tu valor es 10^-{n} veces el esperado"))
    return f


_FACTORES = _factores_comunes()


def evaluar(texto, esperado: float, tol_rel: float = 0.02, tol_abs: float = 0.0,
            confusiones: tuple = ()) -> Resultado:
    """
    Compara la respuesta escrita con `esperado`. `confusiones` = ((factor, mensaje), …) con errores propios de la pregunta
    (se miran antes que los genéricos).
    """
    if texto is None or str(texto).strip() == "":
        return Resultado(VACIA, "Sin responder.")
    try:
        x = leer_numero(texto)
    except ValueError as e:
        return Resultado(INVALIDA, str(e))
    if abs(x - esperado) <= max(tol_abs, tol_rel * abs(esperado)):
        return Resultado(OK, "Correcto.")
    if esperado != 0 and x != 0:
        razon = x / esperado
        if razon < 0 and abs(abs(razon) - 1) <= tol_rel:
            return Resultado(CASI, "El valor es correcto pero el signo es contrario.")
        for factor, mensaje in (*confusiones, *_FACTORES):
            if abs(razon - factor) <= max(tol_rel, 0.03) * abs(factor):
                return Resultado(CASI, f"No coincide, pero {mensaje}.")
    return Resultado(MAL, "No coincide con el valor esperado.")


def evaluar_opcion(elegida, correcta: int, opciones) -> Resultado:
    if elegida is None:
        return Resultado(VACIA, "Sin responder.")
    return Resultado(OK, "Correcto.") if list(opciones).index(elegida) == correcta else Resultado(MAL, "Incorrecta.")
