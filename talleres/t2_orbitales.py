"""
talleres/t2_orbitales.py — Taller 2: oscilador armónico, rotor rígido, orbital d hidrogenoide y átomo de litio.
"""

from __future__ import annotations

import numpy as np

from talleres import _fisica as f
from talleres import _soluciones as _s
from talleres._modelo import NUM, OPC, Datos, Parte, Pregunta, Taller, tex
from talleres.t1_espectros import NOMBRES

ORBITALES_D = {(3, 2): "3d", (4, 2): "4d"}


def _q1(d: Datos) -> Pregunta:
    n = d.elegir(0, [0, 1, 2, 3])
    estado = "fundamental ($n=0$)" if n == 0 else f"$n={n}$"
    enun = ("Para explicar el comportamiento de la energía potencial de una molécula diatómica homonuclear se supone que se comporta como un "
            f"oscilador armónico unidimensional. Si la molécula está en el estado {estado}, halla el valor esperado para la posición "
            "$\\langle x\\rangle$ respecto al centro de la molécula (la distancia de equilibrio).\n\n"
            "Escribe el valor de $\\langle x\\rangle$ (en unidades de $x_0=\\sqrt{\\hbar/\\mu\\omega}$) y muestra el cálculo en tu procedimiento.")
    partes = (
        Parte("x", "$\\langle x\\rangle$ (en unidades de $x_0$)", NUM, 0.0, "x₀", tol_rel=0.0, tol_abs=0.01, peso=1.0,
              explicacion="$\\langle x\\rangle=\\int\\psi_n^*\\,x\\,\\psi_n\\,dx=0$ porque el integrando es impar."),)
    sol = _s.x_esperado(n)
    return Pregunta("q1", enun, 1.0, partes, sol, tema="oscilador")


def _q2(d: Datos) -> Pregunta:
    mol = d.elegir("HF", ["HF", "HCl", "HBr"])
    a, b, k, R = f.DIATOMICAS[mol]
    mu = f.masa_reducida_u(a, b)
    nu = 1.256e12 if mol == "HF" and d.original else float(f"{f.frecuencia_rotacion(0, f.momento_de_inercia(mu, R)):.4g}")
    I = f.H / (4 * np.pi ** 2 * nu)
    R_pm = f.longitud_de_enlace_desde_nu(nu, mu)
    enun = (f"Para la molécula {NOMBRES[mol]}, la frecuencia de la luz que corresponde a la transición de rotación pura de **menor energía** "
            f"es ${tex(nu)}$ Hz. Con base en este valor, calcula la longitud de enlace de la molécula (en pm).")
    partes = (
        Parte("mu", "Paso previo: masa reducida $\\mu$ (en u)", NUM, mu, "u", tol_rel=0.01, peso=0.2),
        Parte("I", "Paso previo: momento de inercia $I$ (en kg m²)", NUM, I, "kg m²", peso=0.3,
              confusiones=((4.0, "la transición $l=0\\to1$ tiene frecuencia $2B$ y $B=h/(8\\pi^2I)$: no es $B$"),
                           (2.0, "con $\\nu=2B$ y $B=h/(8\\pi^2I)$ resulta $I=h/(4\\pi^2\\nu)$")),
              explicacion="La transición más baja es $l=0\\to1$, de frecuencia $\\nu=2B=h/(4\\pi^2I)$."),
        Parte("R", "Longitud de enlace $r_e$ (en pm)", NUM, R_pm, "pm", peso=0.5,
              confusiones=((1e12, "diste el resultado en metros: pásalo a pm"), (1e10, "diste el resultado en ángstrom: 1 Å = 100 pm"),
                           (1e-3, "diste el resultado en nm: 1 nm = 1000 pm")),
              explicacion="$r_e=\\sqrt{I/\\mu}$ con $\\mu$ en kg y el resultado pasado a pm."))
    sol = _s.longitud_desde_nu(mol, a, b, nu, mu, I, R_pm)
    return Pregunta("q2", enun, 1.0, partes, sol, tema="esfera")


def _q3(d: Datos) -> Pregunta:
    n, l = d.elegir((3, 2), list(ORBITALES_D))
    nombre = ORBITALES_D[(n, l)]
    maximos = f.maximos_radiales(n, l)
    P = [float(f.distribucion_radial(n, l, r)) for r in maximos]
    r_max = maximos[int(np.argmax(P))]
    nodos = f.nodos_radiales_numericos(n, l)
    theta_nodal = f.angulos_nodales_m0(l)[0]
    enun = (f"Para el orbital **{nombre}$_{{z^2}}$** del átomo de hidrógeno se requiere calcular las zonas de mayor y menor densidad electrónica. "
            "Calcula estas zonas:\n\n"
            "**a)** Con base en la función de distribución radial $P(r)=r^2R_{nl}(r)^2$ (usa $r$ en unidades de $a_0$).\n\n"
            "**b)** Con base en la densidad de probabilidad angular $|Y_l^0(\\theta)|^2$.")
    partes = (
        Parte("rmax", "a) Distancia $r$ del máximo (principal) de $P(r)$, en unidades de $a_0$", NUM, r_max, "a₀", tol_rel=0.03, peso=0.35,
              explicacion=f"Se maximiza $P(r)=r^2R_{{{n}{l}}}^2$ (para $l=n-1$ resulta $r=n^2a_0$)."),
        Parte("nodos", "a) Número de nodos radiales (superficies esféricas donde $P=0$, sin contar $r=0$)", NUM, float(len(nodos)), "",
              tol_rel=0.0, tol_abs=0.01, peso=0.15,
              explicacion=f"Hay $n-l-1={n - l - 1}$ nodos radiales."),
        Parte("angmax", "b) ¿Dónde es mayor la densidad angular de este orbital?", OPC,
              opciones=("A lo largo del eje $z$ ($\\theta=0^\\circ$ y $180^\\circ$)", "En el plano $xy$ ($\\theta=90^\\circ$)",
                        "Sobre los conos $\\theta\\approx54.7^\\circ$", "Es igual en todas las direcciones"),
              correcta=0, peso=0.25,
              explicacion="$|Y_2^0|^2\\propto(3\\cos^2\\theta-1)^2$ vale 4 en los polos y solo 1 en el plano $xy$ (un máximo local más pequeño)."),
        Parte("theta", "b) Ángulo $\\theta$ (en grados, menor de 90°) del cono donde la densidad angular se anula", NUM, theta_nodal, "°",
              tol_rel=0.0, tol_abs=0.6, peso=0.25,
              confusiones=((90.0 / theta_nodal, "90° es el plano $xy$, donde la densidad no se anula para este orbital"),),
              explicacion="Las raíces de $P_2(\\cos\\theta)=\\tfrac12(3\\cos^2\\theta-1)$ dan $\\cos\\theta=\\pm1/\\sqrt3$."))
    sol = _s.orbital_d(n, l, nombre, list(maximos), list(nodos), r_max, theta_nodal, P)
    return Pregunta("q3", enun, 2.0, partes, sol, tema="hidrogeno",
                    nota="Orbitales del átomo de hidrógeno ($Z=1$): las distancias se dan en unidades del radio de Bohr $a_0$.")


def _q4(d: Datos) -> Pregunta:
    enun = ("Para el litio ($1s^22s^1$ en el estado fundamental), ¿qué función de onda aproximada y aceptable, teniendo en cuenta el principio de "
            "antisimetría, describe:\n\n**a)** su estado electrónico fundamental?\n\n**b)** un estado electrónico excitado en el que el último electrón pasa al orbital $2p$?")
    op_a = ("Determinante de Slater 3×3 con los espín-orbitales $1s\\alpha$, $1s\\beta$ y $2s\\alpha$",
            "Producto simple $1s(1)\\,1s(2)\\,2s(3)$ con espines asignados, sin determinante",
            "Determinante de Slater 3×3 con $1s\\alpha$, $1s\\beta$ y $1s\\alpha$",
            "Determinante de Slater 3×3 con $1s\\alpha$, $2s\\alpha$ y $2s\\beta$")
    op_b = ("Determinante de Slater 3×3 con $1s\\alpha$, $1s\\beta$ y $2p\\alpha$",
            "Producto simple $1s(1)\\,1s(2)\\,2p(3)$, sin antisimetrizar",
            "Determinante 2×2 con $1s\\alpha$ y $2p\\alpha$",
            "Determinante 3×3 con $1s\\alpha$, $1s\\alpha$ y $2p\\alpha$")
    partes = (
        Parte("fund", "a) Estado fundamental", OPC, opciones=op_a, correcta=0, peso=0.5,
              explicacion="Hay tres electrones: un determinante 3×3. $1s\\alpha,1s\\beta$ llenan el 1s y el tercero va al $2s$."),
        Parte("exc", "b) Estado excitado ($2s\\to2p$)", OPC, opciones=op_b, correcta=0, peso=0.5,
              explicacion="Se sustituye el espín-orbital del tercer electrón: $2s\\alpha\\to2p\\alpha$."))
    sol = _s.litio()
    return Pregunta("q4", enun, 1.0, partes, sol, tema="espin")


def construir(d: Datos) -> list[Pregunta]:
    return [_q1(d), _q2(d), _q3(d), _q4(d)]


TALLER = Taller(
    "orbitales", "Oscilador, rotor, orbital d y átomo de litio",
    "Valor esperado de la posición del oscilador armónico, longitud de enlace a partir del espectro de rotación, zonas de densidad del orbital 3d (z²) y funciones de onda antisimétricas del litio.",
    ("Oscilador armónico", "Rotor rígido", "Átomo hidrogenoide", "Principio de antisimetría"), construir,
    n_preguntas=4, puntos=5.0)
