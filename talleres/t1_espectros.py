"""
talleres/t1_espectros.py — Taller 1: vibración y rotación de moléculas diatómicas e iones hidrogenoides.
"""

from __future__ import annotations

import math

from talleres import _fisica as f
from talleres import _soluciones as _s
from talleres._modelo import NUM, OPC, Datos, Parte, Pregunta, Taller, tex

NOMBRES = {"HF": r"HF ($^{1}$H y $^{19}$F)", "HCl": r"HCl ($^{1}$H y $^{35}$Cl)", "HBr": r"HBr ($^{1}$H y $^{79}$Br)"}
IONES = {2: "He²⁺", 3: "Li³⁺", 4: "Be⁴⁺"}
FORMADOS = {2: "He⁺", 3: "Li²⁺", 4: "Be³⁺"}


def _q1(d: Datos) -> Pregunta:
    mol = d.elegir("HF", ["HF", "HCl", "HBr"])
    a, b, k, R = f.DIATOMICAS[mol]
    mu = f.masa_reducida_u(a, b)
    I = f.momento_de_inercia(mu, R)
    nu_v = f.frecuencia_vibracion(k, mu)
    nu_r = f.frecuencia_rotacion(1, I)
    nu_r1 = f.frecuencia_rotacion(0, I)
    enun = (f"La molécula {NOMBRES[mol]} tiene una constante de fuerza de {k:g} N m⁻¹ y una longitud de enlace de {R} pm. "
            "Considerar la vibración como un oscilador armónico y la rotación como un rotor rígido, con las reglas de selección "
            "habituales ($\\Delta n=\\pm1$ en la vibración, $\\Delta l=\\pm1$ en la rotación).\n\n"
            "**a)** Calcular la frecuencia de la luz que corresponde a la **segunda** transición de vibración pura de menor energía.\n\n"
            "**b)** Calcular la frecuencia de la luz que corresponde a la **segunda** transición de rotación pura de menor energía.")
    partes = (
        Parte("mu", "Paso previo: masa reducida $\\mu$ (en u)", NUM, mu, "u", tol_rel=0.01, peso=0.1,
              explicacion="$\\mu=m_1m_2/(m_1+m_2)$."),
        Parte("I", "Paso previo: momento de inercia $I=\\mu r^2$ (en kg m²)", NUM, I, "kg m²", peso=0.1,
              explicacion="Pasa los pm a metros ($10^{-12}$) y la masa reducida a kg (1 u = 1.6605×10⁻²⁷ kg) antes de multiplicar."),
        Parte("vib", "a) Frecuencia de la 2.ª transición de vibración pura (en Hz)", NUM, nu_v, "Hz", peso=0.35,
              confusiones=((2.0, "en el oscilador armónico los niveles están igualmente espaciados: todas las transiciones puras "
                                 "$n\\to n+1$ tienen la misma frecuencia, así que la segunda no es el doble de la primera"),
                           (3.0, "los niveles están igualmente espaciados: no hay una transición «más alta» con frecuencia múltiplo")),
              explicacion="Todas las transiciones puras $n\\to n+1$ del oscilador armónico tienen la misma frecuencia "
                          "$\\nu=\\frac1{2\\pi}\\sqrt{k/\\mu}$: la segunda es igual a la primera."),
        Parte("rot", "b) Frecuencia de la 2.ª transición de rotación pura (en Hz)", NUM, nu_r, "Hz", peso=0.45,
              confusiones=((0.5, "ese es el valor de la primera transición ($l=0\\to1$, $2B$); la segunda es $l=1\\to2$, con $4B$"),
                           (0.25, "ese es $B$; la segunda transición $l=1\\to2$ cae en $4B$"),
                           (1.5, "verificar cuáles son los niveles: $E_l=hB\\,l(l+1)$ y la transición $l=1\\to2$ vale $4B$")),
              explicacion="La transición $l\\to l+1$ tiene frecuencia $2B(l+1)$; para $l=1\\to2$ resulta $4B$."))
    sol = _s.vibracion_rotacion(mol, a, b, k, R, mu, I, nu_v, nu_r, nu_r1)
    return Pregunta("q1", enun, 2.0, partes, sol, tema="espectroscopia",
                    nota="La vibración cae en el infrarrojo y la rotación en microondas: la frecuencia de vibración es decenas de veces mayor.")


def _q2(d: Datos) -> Pregunta:
    Z = d.elegir(3, [2, 3, 4])
    E1 = f.energia_hidrogenoide_ev(Z)
    enun = (f"La energía de un ion de un solo electrón (He⁺, Li²⁺, Be³⁺…) es "
            "$E_n=-\\dfrac{Z^2e^2}{8\\pi\\varepsilon_0a_0\\,n^2}$, con $n=1,2,\\dots$ "
            f"Calcular la afinidad electrónica (en eV) del {IONES[Z]}, es decir, la energía que se libera cuando captura un electrón y queda "
            f"en el estado fundamental ({FORMADOS[Z]}). Usar $e^2/(8\\pi\\varepsilon_0a_0)=13.606$ eV.")
    partes = (
        Parte("E1", f"Paso previo: energía del estado fundamental de {FORMADOS[Z]} (en eV)", NUM, E1, "eV", tol_rel=0.01, peso=0.4,
              confusiones=((1 / Z ** 2, f"no se elevó $Z$ al cuadrado: aquí $Z={Z}$"),
                           (1 / Z, f"el factor es $Z^2={Z ** 2}$, no $Z={Z}$")),
              explicacion=f"$E_1=-Z^2\\cdot13.606\\text{{ eV}}$ con $Z={Z}$."),
        Parte("AE", f"Afinidad electrónica del {IONES[Z]} (en eV)", NUM, -E1, "eV", tol_rel=0.01, peso=0.6,
              confusiones=((-1.0, "la afinidad es la energía que se *libera*, así que es positiva"),),
              explicacion="El electrón libre en reposo tiene energía 0; al caer a $n=1$ se libera $0-E_1=-E_1$."))
    sol = _s.afinidad(Z, IONES[Z], FORMADOS[Z], E1)
    return Pregunta("q2", enun, 1.0, partes, sol, tema="hidrogeno")


def construir(d: Datos) -> list[Pregunta]:
    return [_q1(d), _q2(d)]


TALLER = Taller(
    "espectros", "Vibración, rotación e iones hidrogenoides",
    "Frecuencias de las transiciones puras de vibración y rotación de una molécula diatómica, y afinidad electrónica de un ion de un solo electrón.",
    ("Oscilador armónico y rotor rígido", "Reglas de selección", "Iones hidrogenoides"), construir,
    n_preguntas=2, puntos=3.0)
