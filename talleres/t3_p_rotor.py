"""
talleres/t3_p_rotor.py — Taller 3: orbital 3p_z y rotación plana de una molécula adsorbida.
"""

from __future__ import annotations

import math

import numpy as np

from talleres import _fisica as f
from talleres import _soluciones as _s
from talleres._modelo import NUM, OPC, Datos, Parte, Pregunta, Taller, tex

# molécula: (masa reducida [u], longitud de enlace [pm], nombre con formato)
ROTORES = {"H2": (f.MASA["H"] / 2, 74.14, "hidrógeno (H₂)"),
           "D2": (f.MASA["D"] / 2, 74.14, "deuterio (D₂)"),
           "N2": (f.MASA["N"] / 2, 109.77, "nitrógeno (N₂)")}


def _q1(d: Datos) -> Pregunta:
    n, l = 3, 1
    maximos = f.maximos_radiales(n, l)
    P = [float(f.distribucion_radial(n, l, r)) for r in maximos]
    r_principal = maximos[int(np.argmax(P))]
    r_interno = maximos[int(np.argmin(P))]
    nodo = f.nodos_radiales_numericos(n, l)[0]
    enun = ("Para el orbital **3p$_z$** del átomo de hidrógeno se requiere calcular las zonas de mayor y menor densidad electrónica. Calcular estas zonas:\n\n"
            "**a)** Con base en la función de distribución radial $P(r)=r^2R_{31}(r)^2$ (con $r$ en unidades de $a_0$).\n\n"
            "**b)** Con base en la densidad de probabilidad angular $|Y_1^0(\\theta)|^2$.")
    partes = (
        Parte("nodo", "a) Distancia $r$ (en $a_0$) del nodo radial, donde $P(r)=0$", NUM, nodo, "a₀", tol_rel=0.02, peso=0.2,
              explicacion="$R_{31}\\propto r\\left(1-\\frac r6\\right)e^{-r/3}$ se anula en $r=6a_0$."),
        Parte("rin", "a) Distancia (en $a_0$) del máximo interno de $P(r)$", NUM, r_interno, "a₀", tol_rel=0.03, peso=0.2,
              explicacion="Máximo menor, antes del nodo."),
        Parte("rout", "a) Distancia (en $a_0$) del máximo principal (el más alto) de $P(r)$", NUM, r_principal, "a₀", tol_rel=0.03, peso=0.25,
              explicacion="El máximo más alto es el externo, después del nodo."),
        Parte("ang", "b) ¿Dónde es mayor y dónde nula la densidad angular?", OPC,
              opciones=("Mayor a lo largo del eje $z$; nula en el plano $xy$ ($\\theta=90^\\circ$)",
                        "Mayor en el plano $xy$; nula a lo largo del eje $z$",
                        "Mayor en los conos $\\theta=54.7^\\circ$; nula en el eje $z$",
                        "Uniforme en todas las direcciones"),
              correcta=0, peso=0.35,
              explicacion="$|Y_1^0|^2=\\frac3{4\\pi}\\cos^2\\theta$: máximo en $\\theta=0^\\circ,180^\\circ$ y nulo en $\\theta=90^\\circ$ (plano nodal $xy$)."))
    p_in = r_interno ** 4 * (1 - r_interno / 6) ** 2 * math.exp(-2 * r_interno / 3)
    p_out = r_principal ** 4 * (1 - r_principal / 6) ** 2 * math.exp(-2 * r_principal / 3)
    sol = _s.orbital_3p(r_interno, r_principal, nodo, p_in, p_out)
    return Pregunta("q1", enun, 1.0, partes, sol, tema="hidrogeno",
                    nota="Orbitales del átomo de hidrógeno ($Z=1$): las distancias se dan en unidades de $a_0$.")


def _q2(d: Datos) -> Pregunta:
    nombre = d.elegir("hidrógeno (H₂)", [r[2] for r in ROTORES.values()])
    l = d.elegir(2, [1, 2, 3, 4])
    m = d.elegir(2, list(range(-l, l + 1)))
    L = math.sqrt(l * (l + 1))
    E = l * (l + 1) / 2
    enun = (f"Considerar la molécula de {nombre} en un nivel rotacional con $l={l}$ que se absorbe sobre una superficie metálica que permite su "
            "rotación 2D alrededor de un vector normal a la superficie (el eje $z$). Si la función que describe la rotación de la molécula es\n\n"
            f"$$\\Phi(\\varphi)=\\left(\\frac1{{2\\pi}}\\right)^{{1/2}}e^{{i{m}\\varphi}}$$\n\nCalcula:\n\n"
            "**a)** Su momento angular en el eje $z$ (en unidades de $\\hbar$).\n\n"
            "**b)** Su momento angular total (en unidades de $\\hbar$).\n\n"
            "**c)** Su energía rotacional (en unidades de $\\hbar^2/I$, donde $I$ es el momento de inercia de la molécula).")
    partes = (
        Parte("Lz", "a) $L_z$ en unidades de $\\hbar$", NUM, float(m), "ħ", tol_rel=0.0, tol_abs=0.01, peso=0.3,
              confusiones=((-1.0, "el signo indica el sentido de giro: $e^{+im\\varphi}$ corresponde a $m>0$"),),
              explicacion="$\\hat L_z=-i\\hbar\\,\\partial/\\partial\\varphi$ actúa sobre $e^{im\\varphi}$ y da $m\\hbar$: el número que multiplica a $\\varphi$ en el exponente."),
        Parte("L", "b) $|\\vec L|$ en unidades de $\\hbar$", NUM, L, "ħ", tol_rel=0.01, peso=0.3,
              confusiones=((l / L, "$l\\hbar$ no es la magnitud: $\\hat L^2$ tiene valor propio $l(l+1)\\hbar^2$, luego $|\\vec L|=\\sqrt{l(l+1)}\\hbar$"),),
              explicacion=f"$|\\vec L|=\\sqrt{{l(l+1)}}\\,\\hbar=\\sqrt{{{l * (l + 1)}}}\\hbar$."),
        Parte("E", "c) Energía rotacional $E$ (en unidades de $\\hbar^2/I$)", NUM, E, "ħ²/I", tol_rel=0.01, peso=0.4,
              confusiones=((2.0, "$E=L^2/2I$: falta el factor ½"),),
              explicacion="$E=\\dfrac{|\\vec L|^2}{2I}=\\dfrac{l(l+1)\\hbar^2}{2I}$."))
    sol = _s.rotor(l, m, L, E)
    return Pregunta("q2", enun, 1.0, partes, sol, tema="esfera",
                    nota="Se resuelve solo con los datos del enunciado: el número cuántico $l$ y la función $\\Phi$.")


def construir(d: Datos) -> list[Pregunta]:
    return [_q1(d), _q2(d)]


TALLER = Taller(
    "p_rotor", "Orbital 3p y rotación plana",
    "Zonas de mayor y menor densidad del orbital 3p (z) (parte radial y angular) y momento angular y energía de una molécula que rota en un plano.",
    ("Átomo hidrogenoide", "Rotor plano", "Momento angular"), construir,
    n_preguntas=2, puntos=2.0)
