"""
formulario/_constantes.py — Constantes fundamentales (CODATA vía scipy.constants), unidades atómicas y combinaciones útiles.

Los valores no se escriben a mano: se leen de `scipy.constants.physical_constants`, que contiene los valores recomendados por CODATA.
Las pruebas los contrastan con los valores exactos que fija el SI desde 2019 y con las relaciones entre constantes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy import constants as sc

_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


@dataclass(frozen=True)
class Constante:
    simbolo: str            # LaTeX
    nombre: str
    clave: str              # clave de scipy.constants.physical_constants
    unidad: str             # LaTeX
    grupo: str

    @property
    def valor(self) -> float:
        return sc.physical_constants[self.clave][0]

    @property
    def incertidumbre(self) -> float:
        return sc.physical_constants[self.clave][2]

    @property
    def exacta(self) -> bool:
        return self.incertidumbre == 0.0


def cifras_significativas(c: Constante) -> int:
    """Cifras que justifica la incertidumbre (mínimo 4, máximo 10); las constantes exactas se muestran con 10."""
    if c.exacta:
        return 10
    rel = c.incertidumbre / abs(c.valor)
    return int(min(max(math.floor(-math.log10(rel)) + 1, 4), 10))


def latex_cientifico(x: float, cifras: int) -> str:
    """6.62607015\\times10^{-34}; sin potencia si el exponente es 0."""
    mant, exp = f"{x:.{cifras - 1}e}".split("e")
    if "." in mant:
        mant = mant.rstrip("0").rstrip(".")
    return mant if int(exp) == 0 else rf"{mant}\times10^{{{int(exp)}}}"


def valor_latex(c: Constante) -> str:
    return latex_cientifico(c.valor, cifras_significativas(c))


def incertidumbre_relativa(c: Constante) -> str:
    if c.exacta:
        return "exacta"
    return rf"${latex_cientifico(c.incertidumbre / abs(c.valor), 2)}$"


GRUPOS = ("Universales", "Partículas", "Átomo y estructura electrónica", "Radiación y estadística")

CONSTANTES = (
    Constante("c", "Velocidad de la luz en el vacío", "speed of light in vacuum", r"\mathrm{m\,s^{-1}}", "Universales"),
    Constante("h", "Constante de Planck", "Planck constant", r"\mathrm{J\,s}", "Universales"),
    Constante(r"\hbar=h/2\pi", "Constante de Planck reducida", "reduced Planck constant", r"\mathrm{J\,s}", "Universales"),
    Constante("e", "Cargar elemental", "elementary charge", r"\mathrm{C}", "Universales"),
    Constante(r"\varepsilon_0", "Permitividad del vacío", "vacuum electric permittivity", r"\mathrm{F\,m^{-1}}", "Universales"),
    Constante(r"\mu_0", "Permeabilidad del vacío", "vacuum mag. permeability", r"\mathrm{N\,A^{-2}}", "Universales"),
    Constante("k_B", "Constante de Boltzmann", "Boltzmann constant", r"\mathrm{J\,K^{-1}}", "Universales"),
    Constante("N_A", "Constante de Avogadro", "Avogadro constant", r"\mathrm{mol^{-1}}", "Universales"),
    Constante("R", "Constante de los gases", "molar gas constant", r"\mathrm{J\,mol^{-1}K^{-1}}", "Universales"),
    Constante("m_e", "Masa del electrón", "electron mass", r"\mathrm{kg}", "Partículas"),
    Constante("m_p", "Masa del protón", "proton mass", r"\mathrm{kg}", "Partículas"),
    Constante("m_n", "Masa del neutrón", "neutron mass", r"\mathrm{kg}", "Partículas"),
    Constante("u", "Unidad de masa atómica unificada", "atomic mass constant", r"\mathrm{kg}", "Partículas"),
    Constante(r"\mu_B", "Magnetón de Bohr", "Bohr magneton", r"\mathrm{J\,T^{-1}}", "Partículas"),
    Constante(r"\mu_N", "Magnetón nuclear", "nuclear magneton", r"\mathrm{J\,T^{-1}}", "Partículas"),
    Constante(r"\lambda_C", "Longitud de onda de Compton del electrón", "Compton wavelength", r"\mathrm{m}", "Partículas"),
    Constante("a_0", "Radio de Bohr", "Bohr radius", r"\mathrm{m}", "Átomo y estructura electrónica"),
    Constante(r"\alpha", "Constante de estructura fina", "fine-structure constant", "", "Átomo y estructura electrónica"),
    Constante("R_\\infty", "Constante de Rydberg", "Rydberg constant", r"\mathrm{m^{-1}}", "Átomo y estructura electrónica"),
    Constante("hcR_\\infty", "Energía de Rydberg", "Rydberg constant times hc in eV", r"\mathrm{eV}", "Átomo y estructura electrónica"),
    Constante("E_h", "Energía de Hartree", "Hartree energy", r"\mathrm{J}", "Átomo y estructura electrónica"),
    Constante("E_h", "Energía de Hartree", "Hartree energy in eV", r"\mathrm{eV}", "Átomo y estructura electrónica"),
    Constante(r"\sigma", "Constante de Stefan–Boltzmann", "Stefan-Boltzmann constant", r"\mathrm{W\,m^{-2}K^{-4}}", "Radiación y estadística"),
    Constante("b", "Constante de desplazamiento de Wien", "Wien wavelength displacement law constant", r"\mathrm{m\,K}", "Radiación y estadística"),
    Constante("F", "Constante de Faraday", "Faraday constant", r"\mathrm{C\,mol^{-1}}", "Radiación y estadística"),
)


def _pc(clave: str) -> float:
    return sc.physical_constants[clave][0]


@dataclass(frozen=True)
class Derivada:
    expresion: str          # LaTeX de la combinación
    nombre: str
    valor: float
    unidad: str


def combinaciones() -> tuple[Derivada, ...]:
    """Productos y cocientes de constantes que se usan constantemente, calculados con los valores de scipy."""
    h, c, e, kB, hb, me, eps0, NA = sc.h, sc.c, sc.e, sc.k, sc.hbar, sc.m_e, sc.epsilon_0, sc.N_A
    return (
        Derivada("hc", "Constante de Planck por la velocidad de la luz", h * c, r"\mathrm{J\,m}"),
        Derivada("hc", "Ídem, en eV nm (conversión energía ↔ longitud de onda)", h * c / e * 1e9, r"\mathrm{eV\,nm}"),
        Derivada(r"\hbar c", "Constante de Planck reducida por la velocidad de la luz", hb * c / e * 1e9, r"\mathrm{eV\,nm}"),
        Derivada(r"e^{2}/4\pi\varepsilon_0", "Interacción de Coulomb entre dos cargas elementales", e ** 2 / (4 * math.pi * eps0) / e * 1e9, r"\mathrm{eV\,nm}"),
        Derivada("h/e", "Pendiente del potencial de frenado frente a la frecuencia", h / e, r"\mathrm{V\,s}"),
        Derivada(r"m_ec^{2}", "Energía en reposo del electrón", me * c ** 2 / e / 1e6, r"\mathrm{MeV}"),
        Derivada(r"k_BT\ (T=298.15\ \mathrm{K})", "Energía térmica a temperatura ambiente", kB * 298.15 / e, r"\mathrm{eV}"),
        Derivada(r"RT\ (T=298.15\ \mathrm{K})", "Energía térmica molar a temperatura ambiente", sc.R * 298.15 / 1000, r"\mathrm{kJ\,mol^{-1}}"),
        Derivada(r"k_BT/hc\ (T=298.15\ \mathrm{K})", "Energía térmica expresada como número de onda", kB * 298.15 / (h * c * 100), r"\mathrm{cm^{-1}}"),
        Derivada(r"\dfrac{h^{2}}{8m_e}\cdot\dfrac{1}{(1\ \mathrm{nm})^{2}}", "Energía $E_1$ de un electrón en una caja de 1 nm", h ** 2 / (8 * me * 1e-18) / e, r"\mathrm{eV}"),
    )


def unidades_atomicas() -> tuple[tuple[str, str, float, str], ...]:
    """(magnitud, símbolo, valor SI, unidad SI) de las unidades atómicas de Hartree."""
    return (
        ("Longitud (radio de Bohr)", "a_0", _pc("Bohr radius"), r"\mathrm{m}"),
        ("Energía (hartree)", "E_h", _pc("Hartree energy"), r"\mathrm{J}"),
        ("Masa (masa del electrón)", "m_e", sc.m_e, r"\mathrm{kg}"),
        ("Cargar (carga elemental)", "e", sc.e, r"\mathrm{C}"),
        ("Tiempo", r"\hbar/E_h", _pc("atomic unit of time"), r"\mathrm{s}"),
        ("Velocidad", r"a_0E_h/\hbar=\alpha c", _pc("atomic unit of velocity"), r"\mathrm{m\,s^{-1}}"),
        ("Momento lineal", r"\hbar/a_0", _pc("atomic unit of momentum"), r"\mathrm{kg\,m\,s^{-1}}"),
        ("Momento angular", r"\hbar", sc.hbar, r"\mathrm{J\,s}"),
    )
