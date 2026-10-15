"""
talleres/t3_p_rotor.py — Taller 3: orbital 3p_z y rotación plana de una molécula adsorbida.
"""

from __future__ import annotations

import numpy as np

from talleres import _fisica as f
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
    enun = ("Para el orbital **3p$_z$** del átomo de hidrógeno se requiere calcular las zonas de mayor y menor densidad electrónica. Calcula estas zonas:\n\n"
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
    sol = (f"**a) Parte radial.** $R_{{31}}(r)\\propto r\\left(1-\\dfrac r{{6a_0}}\\right)e^{{-r/3a_0}}$. Tiene $n-l-1=1$ nodo en $r=6a_0$. "
           f"La distribución radial $P(r)=r^2R_{{31}}^2$ tiene dos máximos: uno interno en $r={r_interno:.2f}\\,a_0$ y el principal, más alto, en "
           f"$r={r_principal:.2f}\\,a_0$. Las zonas de **mayor densidad radial** son esas dos regiones (la externa domina); "
           "la **menor** es el nodo $r=6a_0$ (donde vale exactamente cero) y el origen $r=0$.\n\n"
           "**b) Parte angular.** Con $m=0$,\n\n$$|Y_1^0|^2=\\frac3{4\\pi}\\cos^2\\theta$$\n\n"
           "es **máxima** a lo largo del eje $z$ ($\\theta=0^\\circ$ y $180^\\circ$: dos lóbulos) y **nula** en el plano $xy$ ($\\theta=90^\\circ$), "
           "que es el plano nodal del 3p$_z$.")
    return Pregunta("q1", enun, 1.0, partes, sol, tema="hidrogeno",
                    nota="Orbitales del átomo de hidrógeno ($Z=1$): las distancias se dan en unidades de $a_0$.")


def _q2(d: Datos) -> Pregunta:
    mol = d.elegir("H2", list(ROTORES))
    m = d.elegir(2, [1, 2, 3, 4])
    mu, R, nombre = ROTORES[mol]
    I = f.momento_de_inercia(mu, R)
    Lz = m * f.HBAR
    E = f.energia_anillo(m, I)
    enun = (f"Considera la molécula de {nombre} sobre una superficie metálica que permite su rotación **2D** alrededor de un vector normal a la superficie "
            f"(el eje $z$). Su longitud de enlace es {R} pm. Si la función que describe la rotación de la molécula es\n\n"
            f"$$\\Phi(\\varphi)=\\left(\\frac1{{2\\pi}}\\right)^{{1/2}}e^{{i{m}\\varphi}}$$\n\nCalcula:\n\n"
            "**a)** Su momento angular en el eje $z$ (en unidades de $\\hbar$ y en J s).\n\n"
            "**b)** Su momento angular total (en unidades de $\\hbar$).\n\n"
            "**c)** Su energía rotacional (en J).")
    partes = (
        Parte("Lz_h", "a) $L_z$ en unidades de $\\hbar$", NUM, float(m), "ħ", tol_rel=0.0, tol_abs=0.01, peso=0.2,
              confusiones=((-1.0, "el signo indica el sentido de giro: $e^{+im\\varphi}$ corresponde a $m>0$"),),
              explicacion="$\\hat L_z=-i\\hbar\\,\\partial/\\partial\\varphi$ actúa sobre $e^{im\\varphi}$ y da $m\\hbar$."),
        Parte("Lz", "a) $L_z$ en J s", NUM, Lz, "J s", peso=0.15,
              explicacion=f"$L_z={m}\\hbar={tex(Lz)}$ J s."),
        Parte("L", "b) $|\\vec L|$ en unidades de $\\hbar$", NUM, float(m), "ħ", tol_rel=0.0, tol_abs=0.01, peso=0.25,
              confusiones=((np.sqrt(m * (m + 1)) / m, "$\\sqrt{l(l+1)}\\hbar$ vale para la rotación en 3D (esfera); aquí la rotación es plana y $\\vec L$ apunta solo en $z$"),),
              explicacion="En la rotación plana $\\vec L$ solo tiene componente $z$: $|\\vec L|=|L_z|$."),
        Parte("E", "c) Energía rotacional $E$ (en J)", NUM, E, "J", peso=0.4,
              confusiones=((2.0, "$E=L^2/2I$: te falta el factor ½"), (1 / m, f"la energía depende de $m^2$ (aquí $m^2={m ** 2}$), no de $m$"),
                           (2 * np.pi, "usa $\\hbar$, no $h$, en $E=m^2\\hbar^2/2I$")),
              explicacion="$E=\\dfrac{m^2\\hbar^2}{2I}$ con $I=\\mu r_e^2$."))
    sol = (f"La función $\\Phi_m(\\varphi)=\\dfrac1{{\\sqrt{{2\\pi}}}}e^{{im\\varphi}}$ es la del rotor plano (partícula en un anillo) con $m={m}$.\n\n"
           f"**a)** $\\hat L_z=-i\\hbar\\dfrac{{\\partial}}{{\\partial\\varphi}}$, luego $\\hat L_z\\Phi=m\\hbar\\,\\Phi$ y $L_z={m}\\hbar={tex(Lz)}$ J s (el signo $+$ indica giro antihorario).\n\n"
           f"**b)** Como la molécula solo rota en el plano perpendicular a $z$, el vector momento angular apunta únicamente en $z$: "
           f"$|\\vec L|=|L_z|={m}\\hbar$. *(En una rotación 3D, en cambio, $|\\vec L|=\\sqrt{{l(l+1)}}\\hbar$ y $L_z$ es solo una componente.)*\n\n"
           f"**c)** $\\mu={tex(mu)}$ u e $I=\\mu r_e^2={tex(I)}$ kg m². Entonces\n\n"
           f"$$E=\\frac{{L^2}}{{2I}}=\\frac{{m^2\\hbar^2}}{{2I}}=\\frac{{{m}^2\\,({tex(f.HBAR)})^2}}{{2\\,({tex(I)})}}={tex(E)}\\ \\text{{J}}\\;({E / f.EV * 1e3:.3g}\\ \\text{{meV}})$$")
    return Pregunta("q2", enun, 1.0, partes, sol, tema="esfera",
                    nota="El enunciado original no da la longitud de enlace del H₂; aquí se usa el valor tabulado de 74.14 pm. "
                         "Si tu profesor consideró $l=m$ como número cuántico del rotor 3D, el momento angular total sería $\\sqrt{l(l+1)}\\hbar$: "
                         "aquí se resuelve como rotación plana, que es lo que indica «rotación 2D».")


def construir(d: Datos) -> list[Pregunta]:
    return [_q1(d), _q2(d)]


TALLER = Taller(
    "p_rotor", "Orbital 3p y rotación plana",
    "Zonas de mayor y menor densidad del orbital 3p (z) (parte radial y angular) y momento angular y energía de una molécula que rota en un plano.",
    ("Átomo hidrogenoide", "Rotor plano", "Momento angular"), construir,
    n_preguntas=2, puntos=2.0)
