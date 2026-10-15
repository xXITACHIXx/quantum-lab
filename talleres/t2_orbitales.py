"""
talleres/t2_orbitales.py — Taller 2: oscilador armónico, rotor rígido, orbital d hidrogenoide y átomo de litio.
"""

from __future__ import annotations

import numpy as np

from talleres import _fisica as f
from talleres._modelo import NUM, OPC, Datos, Parte, Pregunta, Taller, tex
from talleres.t1_espectros import NOMBRES

ORBITALES_D = {(3, 2): "3d", (4, 2): "4d"}


def _q1(d: Datos) -> Pregunta:
    n = d.elegir(0, [0, 1, 2, 3])
    opciones = ("0", "$x_0/2$, con $x_0=\\sqrt{\\hbar/\\mu\\omega}$", "$x_0$", "$\\hbar\\omega/2$ (la energía de punto cero)")
    enun = ("Para explicar el comportamiento de la energía potencial de una molécula diatómica homonuclear se supone que se comporta como un "
            f"oscilador armónico unidimensional. Si la molécula está en el estado **$n={n}$**, halla el valor esperado de la posición "
            "$x$ respecto al centro de la molécula (la distancia de equilibrio).\n\n"
            "**a)** ¿Cuánto vale $\\langle x\\rangle$?\n\n"
            f"**b)** *(Ampliación)* Calcula $\\langle x^2\\rangle$ en unidades de $x_0^2$, con $x_0^2=\\hbar/(\\mu\\omega)$.")
    partes = (
        Parte("x", "a) $\\langle x\\rangle$ =", OPC, opciones=opciones, correcta=0, peso=0.6,
              explicacion="$|\\psi_n|^2$ es simétrica respecto al centro (par), así que el integrando $x|\\psi_n|^2$ es impar y su integral es 0."),
        Parte("x2", "b) $\\langle x^2\\rangle/x_0^2$ =", NUM, n + 0.5, "", tol_rel=0.02, peso=0.4,
              confusiones=((2.0, "$\\langle x^2\\rangle=(n+\\tfrac12)x_0^2$: ese es el valor sin el factor ½ de $\\langle x^2\\rangle$"),
                           (0.5, "el factor es $n+\\tfrac12$ (virial: $\\langle V\\rangle=\\tfrac12 E$ con $V=\\tfrac12\\mu\\omega^2x^2$)")),
              explicacion="Del teorema del virial, $\\langle V\\rangle=\\frac12\\mu\\omega^2\\langle x^2\\rangle=\\frac12E_n$, y $E_n=\\hbar\\omega(n+\\frac12)$."))
    sol = (f"**a)** Las funciones del oscilador tienen paridad definida: $\\psi_n(-x)=(-1)^n\\psi_n(x)$. Por tanto $|\\psi_n|^2$ es **par** y\n\n"
           f"$$\\langle x\\rangle=\\int_{{-\\infty}}^{{\\infty}}x\\,|\\psi_n(x)|^2\\,dx=0$$\n\n"
           f"porque el integrando es impar. La partícula pasa tanto tiempo a un lado como al otro del centro, para todo $n$ (en particular para $n={n}$).\n\n"
           f"**b)** Con el teorema del virial, $\\langle V\\rangle=\\langle T\\rangle=E_n/2$:\n\n"
           f"$$\\tfrac12\\mu\\omega^2\\langle x^2\\rangle=\\tfrac12\\hbar\\omega\\left(n+\\tfrac12\\right)\\;\\Rightarrow\\;"
           f"\\langle x^2\\rangle=\\left(n+\\tfrac12\\right)\\frac{{\\hbar}}{{\\mu\\omega}}={n + 0.5:g}\\,x_0^2$$\n\n"
           "Aunque $\\langle x\\rangle=0$, la partícula no está quieta en el centro: la dispersión $\\sqrt{\\langle x^2\\rangle}$ crece con $n$.")
    return Pregunta("q1", enun, 1.0, partes, sol, tema="oscilador",
                    nota="El enunciado original pide el valor esperado de la posición en el estado fundamental; el apartado b) es una ampliación.")


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
    sol = (f"La transición de menor energía es $l=0\\to1$, cuya frecuencia es $\\nu=2B$ con $B=\\dfrac{{h}}{{8\\pi^2I}}$. Entonces\n\n"
           f"$$I=\\frac{{h}}{{4\\pi^2\\nu}}=\\frac{{{tex(f.H)}}}{{4\\pi^2\\,({tex(nu)})}}={tex(I)}\\ \\text{{kg m}}^2$$\n\n"
           f"La masa reducida es $\\mu=\\dfrac{{m_1m_2}}{{m_1+m_2}}={tex(mu)}$ u $={tex(mu * f.U)}$ kg y $I=\\mu r_e^2$, de modo que\n\n"
           f"$$r_e=\\sqrt{{\\frac I\\mu}}=\\sqrt{{\\frac{{{tex(I)}}}{{{tex(mu * f.U)}}}}}={tex(R_pm * 1e-12)}\\ \\text{{m}}={R_pm:.2f}\\ \\text{{pm}}$$")
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
    maxtxt = ", ".join(f"{r:.2f}" for r in maximos)
    nodotxt = "ninguno" if not nodos else ", ".join(f"$r={x:.2f}\\,a_0$" for x in nodos)
    sol = (f"**a) Parte radial.** Para {nombre} ($n={n}$, $l={l}$) la distribución radial $P(r)=r^2R_{{{n}{l}}}^2$ tiene "
           f"$n-l-1={n - l - 1}$ nodos radiales ({nodotxt}). Sus máximos están en $r={maxtxt}\\,a_0$; el mayor, que es la zona de "
           f"**mayor densidad radial**, está en $r={r_max:.2f}\\,a_0$"
           + (f" (en general, para $l=n-1$ el máximo está en $r=n^2a_0$)" if l == n - 1 else "") + ". "
           "La **menor** densidad radial se da en $r=0$, donde $P\\to0$ por el factor $r^2$ (y de nuevo $r\\to\\infty$), y en los nodos.\n\n"
           "**b) Parte angular.** Con $m=0$, $d_{z^2}$ tiene\n\n"
           "$$|Y_2^0|^2=\\frac{5}{16\\pi}\\left(3\\cos^2\\theta-1\\right)^2$$\n\n"
           f"La densidad es **máxima en el eje $z$** ($\\theta=0^\\circ$ y $180^\\circ$, valor $5/4\\pi$) y se anula en los conos $\\cos\\theta=\\pm1/\\sqrt3$, es decir "
           f"$\\theta={theta_nodal:.2f}^\\circ$ y ${180 - theta_nodal:.2f}^\\circ$. En el plano $xy$ ($\\theta=90^\\circ$) hay un máximo local más pequeño "
           "(un cuarto del máximo): es el «anillo» característico del $d_{z^2}$.")
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
    sol = ("Un estado de varios electrones debe ser **antisimétrico** frente al intercambio de dos electrones. La forma de lograrlo con espín-orbitales "
           "(orbital espacial × espín) es el **determinante de Slater**, que además cumple el principio de exclusión de Pauli (dos filas iguales dan determinante nulo).\n\n"
           "**a) Fundamental ($1s^22s^1$):**\n\n"
           "$$\\Psi_0=\\frac1{\\sqrt{3!}}\\begin{vmatrix}1s\\alpha(1)&1s\\beta(1)&2s\\alpha(1)\\\\1s\\alpha(2)&1s\\beta(2)&2s\\alpha(2)\\\\1s\\alpha(3)&1s\\beta(3)&2s\\alpha(3)\\end{vmatrix}$$\n\n"
           "**b) Excitado ($1s^22p^1$):** el mismo determinante cambiando $2s\\alpha$ por $2p\\alpha$:\n\n"
           "$$\\Psi_1=\\frac1{\\sqrt{3!}}\\begin{vmatrix}1s\\alpha(1)&1s\\beta(1)&2p\\alpha(1)\\\\1s\\alpha(2)&1s\\beta(2)&2p\\alpha(2)\\\\1s\\alpha(3)&1s\\beta(3)&2p\\alpha(3)\\end{vmatrix}$$\n\n"
           "Los otros candidatos fallan: un producto simple no es antisimétrico; un determinante con un espín-orbital repetido vale cero; "
           "y un determinante 2×2 describe solo dos electrones.")
    return Pregunta("q4", enun, 1.0, partes, sol, tema="espin")


def construir(d: Datos) -> list[Pregunta]:
    return [_q1(d), _q2(d), _q3(d), _q4(d)]


TALLER = Taller(
    "orbitales", "Oscilador, rotor, orbital d y átomo de litio",
    "Valor esperado de la posición del oscilador armónico, longitud de enlace a partir del espectro de rotación, zonas de densidad del orbital 3d (z²) y funciones de onda antisimétricas del litio.",
    ("Oscilador armónico", "Rotor rígido", "Átomo hidrogenoide", "Principio de antisimetría"), construir,
    n_preguntas=4, puntos=5.0)
