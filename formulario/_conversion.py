"""
formulario/_conversion.py — Conversor de energía, longitud, masa y ángulo (sin Streamlit, probado con pytest).

La energía se convierte pasando por julios: la frecuencia, el número de onda, la temperatura y la energía molar son proporcionales a
la energía, y la longitud de onda es inversamente proporcional (E = hc/λ).
"""

from __future__ import annotations

import math

from scipy import constants as sc

H, C, E, KB, NA = sc.h, sc.c, sc.e, sc.k, sc.N_A
EH = sc.physical_constants["Hartree energy"][0]
KCAL = 4184.0                                    # J por kcal termoquímica (exacto)

# unidad → (julios por unidad) para las proporcionales a la energía
_ENERGIA_LINEAL = {
    "J": 1.0,
    "eV": E,
    "meV": E * 1e-3,
    "hartree (Eh)": EH,
    "cm⁻¹ (número de onda)": H * C * 100.0,
    "Hz": H,
    "THz": H * 1e12,
    "kJ/mol": 1000.0 / NA,
    "kcal/mol": KCAL / NA,
    "K (temperatura, E/k_B)": KB,
}
NM = "nm (longitud de onda)"
UNIDADES_ENERGIA = (*_ENERGIA_LINEAL, NM)

_LONGITUD = {"m": 1.0, "cm": 1e-2, "mm": 1e-3, "µm": 1e-6, "nm": 1e-9, "Å": 1e-10, "pm": 1e-12, "fm": 1e-15,
             "bohr (a₀)": sc.physical_constants["Bohr radius"][0]}
_MASA = {"kg": 1.0, "g": 1e-3, "u (unidad de masa atómica)": sc.physical_constants["atomic mass constant"][0],
         "mₑ (masa del electrón)": sc.m_e, "mₚ (masa del protón)": sc.m_p}
_ANGULO = {"grados": math.pi / 180, "radianes": 1.0, "vueltas": 2 * math.pi, "minutos de arco": math.pi / 10800}
UNIDADES_LONGITUD, UNIDADES_MASA, UNIDADES_ANGULO = tuple(_LONGITUD), tuple(_MASA), tuple(_ANGULO)


def a_julios(valor: float, unidad: str) -> float:
    if not math.isfinite(valor):
        raise ValueError("El valor debe ser un número finito.")
    if unidad == NM:
        if valor <= 0:
            raise ValueError("La longitud de onda debe ser positiva.")
        return H * C / (valor * 1e-9)
    return valor * _ENERGIA_LINEAL[unidad]


def desde_julios(energia: float, unidad: str) -> float:
    if unidad == NM:
        if energia <= 0:
            raise ValueError("Una longitud de onda solo corresponde a una energía positiva.")
        return H * C / energia * 1e9
    return energia / _ENERGIA_LINEAL[unidad]


def equivalencias_energia(valor: float, unidad: str) -> dict[str, float | None]:
    """El mismo valor en todas las unidades de energía; None donde no está definido (λ para E ≤ 0)."""
    energia = a_julios(valor, unidad)
    salida: dict[str, float | None] = {}
    for u in UNIDADES_ENERGIA:
        try:
            salida[u] = desde_julios(energia, u)
        except ValueError:
            salida[u] = None
    return salida


def convertir(valor: float, de: str, a: str, tabla: dict) -> float:
    if not math.isfinite(valor):
        raise ValueError("El valor debe ser un número finito.")
    return valor * tabla[de] / tabla[a]


def convertir_longitud(valor: float, de: str, a: str) -> float:
    return convertir(valor, de, a, _LONGITUD)


def convertir_masa(valor: float, de: str, a: str) -> float:
    return convertir(valor, de, a, _MASA)


def convertir_angulo(valor: float, de: str, a: str) -> float:
    return convertir(valor, de, a, _ANGULO)


_REGIONES = ((1e-11, "rayos γ"), (1e-8, "rayos X"), (380e-9, "ultravioleta"), (750e-9, "luz visible"), (2.5e-6, "infrarrojo cercano"),
             (25e-6, "infrarrojo medio"), (1e-3, "infrarrojo lejano"), (1.0, "microondas"), (math.inf, "ondas de radio"))


def region_espectral(longitud_onda_m: float) -> str:
    """Región del espectro electromagnético según los límites convencionales (los bordes varían ligeramente entre autores)."""
    if longitud_onda_m <= 0:
        raise ValueError("La longitud de onda debe ser positiva.")
    for limite, nombre in _REGIONES:
        if longitud_onda_m < limite:
            return nombre
    return "ondas de radio"
