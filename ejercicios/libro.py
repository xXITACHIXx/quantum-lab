"""
ejercicios/libro.py — Ejercicios del libro trabajados en el cuaderno (rotación, oscilador armónico y átomo de hidrógeno).

La numeración sigue la del cuaderno. Los enunciados se reescribieron a partir de las fotos; las soluciones se rehicieron y
verificaron, y donde el cuaderno tiene un error o una errata se indica en la nota del ejercicio.
"""

from __future__ import annotations

import math

from scipy import constants as const

from ejercicios._modelo import AVANZADO, BASICO, LIBRO, MEDIO, NUM, OPC, Ejercicio, Parte, llenar
from talleres._modelo import tex

H, HBAR, C, U, KB, E = const.h, const.hbar, const.c, const.atomic_mass, const.k, const.e
G = 9.81
M_H, M_D, M_F, M_CL35, M_I = 1.007825, 2.014102, 18.998403, 34.968853, 126.904473   # u


# ---------------------------------------------------------------------
# Rotación
# ---------------------------------------------------------------------
def _hi() -> Ejercicio:
    mu = M_H * M_I / (M_H + M_I) * U
    r = 160.92e-12
    inercia = mu * r ** 2
    de = HBAR ** 2 / inercia
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La molécula ¹H¹²⁷I (enlace de 160.92 pm) gira en 3D como un **rotor rígido**. **a)** su energía de punto cero de rotación; **b)** la menor energía que puede absorber en una excitación rotacional.

#### Paso 2 · Niveles del rotor rígido
$$E_l=\frac{\hbar^2}{2I}\,l(l+1),\qquad l=0,1,2,\dots\qquad I=\mu r^2$$

#### Paso 3 · a) Energía de punto cero
Es la energía del nivel más bajo, $l=0$:

$$E_0=\frac{\hbar^2}{2I}\cdot0\cdot(0+1)=\mathbf{0}$$

A diferencia del oscilador y de la caja, el rotor **sí puede** tener energía cero: girar no está «confinado» (la función $l=0$ es constante en todas las direcciones y no hay incertidumbre que obligue a moverse).

#### Paso 4 · b) Menor energía absorbida
Por la regla de selección $\Delta l=+1$, la excitación más pequeña es $l=0\to1$:

$$\Delta E=E_1-E_0=\frac{\hbar^2}{2I}(1\cdot2)-0=\frac{\hbar^2}{I}$$

#### Paso 5 · Masa reducida y momento de inercia
- $\mu=\dfrac{m_Hm_I}{m_H+m_I}=\dfrac{(1.0078)(126.904)}{1.0078+126.904}\ \text{u}=<<mu_u>>\ \text{u}=<<mu>>\ \text{kg}$
- $I=\mu r^2=(<<mu>>)(1.6092\times10^{-10})^2=<<I>>\ \text{kg m}^2$

*Ojo:* $\mu$ es **un poco menor** que la masa del H ($1.6735\times10^{-27}$ kg), no igual: es el error del cuaderno.

#### Paso 6 · Sustituir
$$\Delta E=\frac{\hbar^2}{I}=\frac{(1.0546\times10^{-34})^2}{<<I>>}=\mathbf{<<de>>\ \text{J}}$$

En frecuencia, $\nu=\Delta E/h=<<nu>>$ Hz: microondas, como corresponde a la rotación.
""", mu_u=f"{mu / U:.5f}", mu=tex(mu), I=tex(inercia), de=tex(de), nu=tex(de / H))
    return Ejercicio(
        "l01_hi", "Rotación del HI: punto cero y primera excitación", LIBRO, "Libro · ejercicio 1", "esfera",
        "Una molécula de ¹H¹²⁷I en fase gaseosa, con longitud de enlace de **160.92 pm**, rota en el espacio tridimensional.\n\n"
        "**a)** Calcula la energía de punto cero asociada a esa rotación. **b)** ¿Cuál es la menor energía que puede absorber la molécula en una excitación rotacional?",
        sol, (Parte("E0", "a) Energía de punto cero (en J)", NUM, 0.0, "J", tol_rel=0.0, tol_abs=1e-30),
              Parte("dE", "b) Menor energía absorbida (en J)", NUM, de, "J",
                    confusiones=((0.5, "esa es $E_1/2$: la transición $0\\to1$ vale $\\hbar^2/I$, no $\\hbar^2/2I$"),))),
        ("$E_l=\\frac{\\hbar^2}{2I}l(l+1)$.", "La excitación más pequeña es $l=0\\to1$."), BASICO,
        nota="En el cuaderno la masa reducida aparece como 1.6735×10⁻²⁷ kg (la masa del H); el valor correcto es 1.6603×10⁻²⁷ kg. El resultado casi no cambia.")


def _conos_l5() -> Ejercicio:
    ang = {m: math.degrees(math.acos(m / math.sqrt(30))) for m in range(5, -6, -1)}
    filas = "\n".join(f"| {m:+d}".replace("+0", "0") + f" | ${m}/\\sqrt{{30}}={m / math.sqrt(30):.4f}$ | {ang[m]:.2f}° |" for m in range(5, -6, -1))
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Dibujar los conos de momento angular para $l=5$ y calcular el semiángulo de cada uno (el ángulo entre $\vec l$ y el eje $z$).

#### Paso 2 · Longitud del vector
$$|\vec l|=\sqrt{l(l+1)}\,\hbar=\sqrt{5\cdot6}\,\hbar=\sqrt{30}\,\hbar=<<L>>\,\hbar$$

#### Paso 3 · Proyecciones permitidas
$l_z=m_l\hbar$ con $m_l=-5,-4,\dots,4,5$: **11** orientaciones ($2l+1$).

#### Paso 4 · Semiángulo de cada cono
El vector de longitud $\sqrt{30}\hbar$ tiene proyección $m_l\hbar$ sobre $z$, así que

$$\cos\theta=\frac{m_l}{\sqrt{30}}\qquad\theta=\arccos\frac{m_l}{\sqrt{30}}$$

| $m_l$ | $\cos\theta$ | $\theta$ |
|---|---|---|
<<filas>>

#### Paso 5 · Cómo dibujarlos
- Traza el eje $z$ y una semicircunferencia de radio $\sqrt{30}\approx5.48$ (en unidades de $\hbar$).
- Marca en el eje $z$ las alturas $-5,\dots,5$ y une cada una con la circunferencia: son las generatrices de los conos.
- $m_l=0$ ($\theta=90^\circ$) no es un cono sino un **disco** en el plano $xy$. Quedan 5 conos «hacia arriba», 5 «hacia abajo» y el disco: 11 orientaciones.

#### Paso 6 · Comprobación
Ningún cono tiene $\theta=0$: incluso con $m_l=5$ el vector forma 24.09° con el eje. Los ángulos son simétricos: $\theta(-m)=180^\circ-\theta(m)$. ✓
""", L=f"{math.sqrt(30):.3f}", filas=filas)
    return Ejercicio(
        "l04_conos_l5", "Conos de momento angular con l = 5", LIBRO, "Libro · ejercicio 4", "esfera",
        "Dibuja una figura con todos los conos de momento angular compatibles con $l=5$ y calcula el semiángulo de cada uno.",
        sol, (Parte("L", "Longitud $|\\vec l|$ en unidades de $\\hbar$", NUM, math.sqrt(30), "ħ", confusiones=((5 / math.sqrt(30), "la longitud es $\\sqrt{l(l+1)}\\hbar$, no $l\\hbar$"),)),
              Parte("n", "Número de orientaciones ($m_l$ posibles)", NUM, 11.0, tol_rel=0.0, tol_abs=0.1),
              Parte("t5", "Semiángulo para $m_l=5$ (grados)", NUM, ang[5], "°"),
              Parte("t1", "Semiángulo para $m_l=1$ (grados)", NUM, ang[1], "°")),
        ("$\\cos\\theta=m_l/\\sqrt{l(l+1)}$.",), BASICO)


def _px_dxz() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
$p_x$ y $d_{xz}$ son combinaciones **reales** de armónicos esféricos. ¿Siguen siendo autofunciones de $\hat l_z$? Hay que aplicarles el operador.

#### Paso 2 · Las funciones (parte angular)
- $p_x\propto\sin\theta\cos\phi$
- $d_{xz}\propto\sin\theta\cos\theta\cos\phi$

Y el operador: $\hat l_z=-i\hbar\dfrac{\partial}{\partial\phi}$ (solo actúa sobre $\phi$; lo que depende de $\theta$ es una constante para él).

#### Paso 3 · Aplicar a $p_x$
$$\hat l_z(\sin\theta\cos\phi)=-i\hbar\sin\theta\,\frac{\partial\cos\phi}{\partial\phi}=-i\hbar\sin\theta(-\sin\phi)=i\hbar\sin\theta\sin\phi\ \propto\ p_y$$

El resultado es **otra función** ($p_y$), no «constante × $p_x$». **No es autofunción.**

#### Paso 4 · Aplicar a $d_{xz}$
$$\hat l_z(\sin\theta\cos\theta\cos\phi)=i\hbar\sin\theta\cos\theta\sin\phi\ \propto\ d_{yz}$$

Tampoco: **no es autofunción**.

#### Paso 5 · Por qué
Las autofunciones de $\hat l_z$ dependen de $\phi$ como $e^{im\phi}$. Para obtener funciones reales se combinan $m=+1$ y $m=-1$:

$$\cos\phi=\frac{e^{i\phi}+e^{-i\phi}}{2}$$

Es una mezcla de dos estados con $l_z=+\hbar$ y $l_z=-\hbar$: no tiene un $l_z$ definido (su valor medio es 0). En cambio **sí** siguen siendo autofunciones de $\hat H$ y de $\hat l^2$, porque los dos componentes tienen la misma $n$ y la misma $l$.
"""
    return Ejercicio(
        "l06_px_dxz", "¿Son px y dxz autofunciones de lz?", LIBRO, "Libro · ejercicio 6", "esfera",
        "Las funciones $p_x$ y $d_{xz}$ son combinaciones lineales de armónicos esféricos, que son autofunciones de $\\hat H$, $\\hat l^2$ y $\\hat l_z$ "
        "en la rotación 3D. Se eligieron así para obtener funciones reales. ¿Siguen siendo autofunciones de $\\hat l_z$? Aplica el operador.",
        sol, (Parte("px", "¿$p_x$ es autofunción de $\\hat l_z$?", OPC, opciones=("No", "Sí, con $l_z=\\hbar$", "Sí, con $l_z=0$"), correcta=0,
                    explicacion="$\\hat l_z p_x\\propto p_y$."),
              Parte("dxz", "¿$d_{xz}$ es autofunción de $\\hat l_z$?", OPC, opciones=("No", "Sí, con $l_z=\\hbar$", "Sí, con $l_z=2\\hbar$"), correcta=0,
                    explicacion="$\\hat l_z d_{xz}\\propto d_{yz}$.")),
        ("$p_x\\propto\\sin\\theta\\cos\\phi$; deriva respecto de $\\phi$.",), BASICO)


def _y20_nodos() -> Ejercicio:
    t = math.degrees(math.acos(1 / math.sqrt(3)))
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Los valores de $\theta$ donde $Y_2^0=\left(\frac{5}{16\pi}\right)^{1/2}(3\cos^2\theta-1)$ se anula, y qué tipo de superficie forman.

#### Paso 2 · Igualar a cero
La constante $\left(\frac5{16\pi}\right)^{1/2}$ no es cero, así que basta con el paréntesis:

$$3\cos^2\theta-1=0\ \Rightarrow\ \cos^2\theta=\frac13\ \Rightarrow\ \cos\theta=\pm\frac1{\sqrt3}=\pm0.5774$$

#### Paso 3 · Los ángulos
- $\theta=\arccos(0.5774)=\mathbf{<<t1>>^\circ}$
- $\theta=\arccos(-0.5774)=\mathbf{<<t2>>^\circ}$ ($=180^\circ-<<t1>>^\circ$)

#### Paso 4 · ¿Puntos, líneas o superficies?
La condición es «$\theta$ = constante» y **no dice nada** de $r$ ni de $\phi$: vale para cualquier distancia y cualquier giro alrededor de $z$. El conjunto de puntos con $\theta$ fijo es un **cono** con vértice en el núcleo y eje $z$. Los nodos de $Y_2^0$ son **dos superficies cónicas**, una abriéndose hacia $+z$ y otra hacia $-z$.

#### Paso 5 · Comprobación
$l=2$ debe dar 2 nodos angulares ✓. Entre los conos (cerca del plano $xy$) la función es negativa; dentro de ellos, alrededor del eje $z$, es positiva: es la forma del orbital $d_{z^2}$.
""", t1=f"{t:.2f}", t2=f"{180 - t:.2f}")
    return Ejercicio(
        "l07_y20_nodos", "Nodos de Y₂⁰", LIBRO, "Libro · ejercicio 7", "esfera",
        "¿Para qué valores de $\\theta$ tiene nodos la función $Y_2^0(\\theta,\\phi)=\\left(\\frac{5}{16\\pi}\\right)^{1/2}(3\\cos^2\\theta-1)$? "
        "¿Son esos nodos puntos, líneas u otras superficies?",
        sol, (Parte("t1", "Menor ángulo nodal (grados)", NUM, t, "°", tol_rel=0.01),
              Parte("t2", "Mayor ángulo nodal (grados)", NUM, 180 - t, "°", tol_rel=0.01),
              Parte("tipo", "Los nodos son", OPC, opciones=("Superficies cónicas", "Puntos", "Planos", "Esferas"), correcta=0,
                    explicacion="$\\theta$ = constante para todo $r$ y $\\phi$ es un cono.")),
        ("Iguala $3\\cos^2\\theta-1$ a cero.",), BASICO)


def _d2() -> Ejercicio:
    mu = M_D / 2 * U
    nt = 3115.0
    k = (2 * math.pi * C * nt * 100) ** 2 * mu
    x = 1.50 * G / k
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La frecuencia de vibración de la molécula, en número de onda, es $\tilde\nu=3115\ \text{cm}^{-1}$. Se pide **a)** la constante de fuerza $k$ del enlace y **b)** cuánto se estiraría un resorte clásico con esa misma $k$ si se le cuelga una masa de 1.50 kg.

#### Paso 2 · Número de onda → frecuencia
El número de onda es «ondas por centímetro»: $\tilde\nu=\nu/c$. Para usar el SI conviene $c$ en cm/s:

$$\nu=c\,\tilde\nu=(2.998\times10^{10}\ \text{cm/s})(3115\ \text{cm}^{-1})=<<nu>>\ \text{s}^{-1}$$

#### Paso 3 · Masa reducida
Para una molécula homonuclear $\mu=m/2$. Con $m_D=2.0141$ u:

$$\mu=\frac{2.0141}{2}\ \text{u}\times1.6605\times10^{-27}\ \tfrac{\text{kg}}{\text{u}}=<<mu>>\ \text{kg}$$

#### Paso 4 · Constante de fuerza
De $\nu=\dfrac1{2\pi}\sqrt{\dfrac k\mu}$ se despeja elevando al cuadrado:

$$k=(2\pi\nu)^2\mu=(2\pi\times<<nu>>)^2\times<<mu>>=\mathbf{<<k>>\ \text{N/m}}$$

#### Paso 5 · Resorte clásico
Con la masa colgada en equilibrio, la fuerza del resorte iguala al peso: $kx=mg$.

$$x=\frac{mg}{k}=\frac{(1.50\ \text{kg})(9.81\ \text{m/s}^2)}{<<k>>\ \text{N/m}}=\frac{14.7\ \text{N}}{<<k>>\ \text{N/m}}=\mathbf{<<x>>\ \text{m}}\approx<<xcm>>\ \text{cm}$$

#### Paso 6 · Interpretación
Un enlace químico es un resorte «duro»: con 1.5 kg colgado apenas se estiraría unos 2.6 cm. Es un resorte de laboratorio bastante rígido.
""", nu=tex(C * 100 * nt), mu=tex(mu), k=f"{k:.0f}", x=f"{x:.4f}", xcm=f"{100 * x:.2f}")
    return Ejercicio(
        "l08_d2", "Constante de fuerza del D₂", LIBRO, "Libro · ejercicio 8", "oscilador",
        "La frecuencia de vibración de la molécula de **D₂**, expresada como número de onda, es de **3115 cm⁻¹**. ¿Cuál es la constante de fuerza $k$ del enlace? "
        "¿Cuánto se estiraría un resorte clásico con esta misma constante si se le cuelga una masa de 1.50 kg? Usa $g=9.81$ m/s².",
        sol, (Parte("k", "Constante de fuerza (en N/m)", NUM, k, "N/m",
                    confusiones=((1e-4, "usaste el número de onda en m⁻¹ sin convertir (3115 cm⁻¹ = 311 500 m⁻¹) o $c$ en m/s con $\\tilde\\nu$ en cm⁻¹"),
                                 (2.0, "usaste la masa de un átomo en lugar de la masa reducida $\\mu=m/2$"))),
              Parte("x", "Estiramiento del resorte (en m)", NUM, x, "m")),
        ("$\\nu=c\\tilde\\nu$ (con $c$ en cm/s).", "$k=(2\\pi\\nu)^2\\mu$, con $\\mu=m_D/2$."), BASICO,
        nota="En el cuaderno la molécula aparece como «O₂», pero los datos (3115 cm⁻¹ y μ = 1.672×10⁻²⁷ kg) corresponden al D₂, que es la molécula del enunciado del libro.")


def _ortog_anillo() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Demostrar con la integral que $\Phi_m=\frac{1}{\sqrt{2\pi}}e^{im\phi}$ y $\Phi_n=\frac{1}{\sqrt{2\pi}}e^{in\phi}$ son **ortogonales** si $m\ne n$:

$$\int_0^{2\pi}\Phi_m^*\,\Phi_n\,d\phi=0$$

#### Paso 2 · El conjugado
Al conjugar se cambia $i\to-i$: $\Phi_m^*=\frac1{\sqrt{2\pi}}e^{-im\phi}$. (Si no se conjuga, el resultado sale mal.)

#### Paso 3 · Juntar exponentes
$$\int_0^{2\pi}\frac{1}{2\pi}e^{-im\phi}e^{in\phi}d\phi=\frac1{2\pi}\int_0^{2\pi}e^{i(n-m)\phi}d\phi$$

#### Paso 4 · Integrar
Como $n-m\ne0$, la primitiva de $e^{i(n-m)\phi}$ es $\dfrac{e^{i(n-m)\phi}}{i(n-m)}$:

$$\frac1{2\pi}\left[\frac{e^{i(n-m)\phi}}{i(n-m)}\right]_0^{2\pi}=\frac1{2\pi i(n-m)}\left[e^{i(n-m)2\pi}-e^{0}\right]$$

#### Paso 5 · Evaluar con la fórmula de Euler
$n-m$ es un **entero**, así que $e^{i(n-m)2\pi}=\cos(2\pi(n-m))+i\sin(2\pi(n-m))=1+0i=1$:

$$\frac{1}{2\pi i(n-m)}[1-1]=0\quad\checkmark$$

#### Paso 6 · Y si $m=n$
Entonces el integrando es $\frac1{2\pi}e^0=\frac1{2\pi}$ y la integral vale $\frac{2\pi}{2\pi}=1$: las funciones están **normalizadas**. Juntas forman un conjunto **ortonormal**. (La división entre $n-m$ del paso 4 solo vale si $m\ne n$: por eso se trata aparte.)
"""
    return Ejercicio(
        "l10_ortog_anillo", "Ortogonalidad de las funciones del rotor 2D", LIBRO, "Libro · ejercicio 10", "esfera",
        "Demuestra, mediante la integración necesaria, que las autofunciones de la ecuación de Schrödinger para la rotación en dos dimensiones, "
        "$\\frac{1}{\\sqrt{2\\pi}}e^{im_l\\phi}$ y $\\frac{1}{\\sqrt{2\\pi}}e^{in_l\\phi}$ (con $m_l\\ne n_l$), son ortogonales.",
        sol, (Parte("int", "Valor de la integral con $m_l\\ne n_l$", NUM, 0.0, tol_rel=0.0, tol_abs=0.01),
              Parte("norm", "Valor de la integral con $m_l=n_l$", NUM, 1.0, tol_rel=0.0, tol_abs=0.01)),
        ("No olvides conjugar la primera función.", "$e^{i2\\pi k}=1$ para todo entero $k$."), BASICO)


# ---------------------------------------------------------------------
# Oscilador armónico
# ---------------------------------------------------------------------
def _p2_osc() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
$\langle p_x^2\rangle$ para el oscilador armónico en $n=0$, $1$ y $2$. Con $\hat p_x^2=-\hbar^2\dfrac{d^2}{dx^2}$, la integral directa es larga; hay un camino más corto.

#### Paso 2 · Relación con la energía cinética
$E_k=\dfrac{p^2}{2\mu}$, así que $\langle E_k\rangle=\dfrac{\langle p_x^2\rangle}{2\mu}$, es decir $\langle p_x^2\rangle=2\mu\langle E_k\rangle$.

#### Paso 3 · Teorema del virial
Para $V=\tfrac12kx^2$ la energía se reparte **mitad y mitad**: $\langle E_k\rangle=\langle E_p\rangle=\tfrac12E_n$. Entonces

$$\langle p_x^2\rangle=2\mu\cdot\tfrac12E_n=\mu E_n=\mu\left(n+\tfrac12\right)\hbar\omega$$

#### Paso 4 · Escribirlo con $\alpha$
Con $\alpha=\dfrac{\mu\omega}{\hbar}=\dfrac{\sqrt{k\mu}}{\hbar}$ se tiene $\mu\omega=\alpha\hbar$, así que $\mu\hbar\omega=\alpha\hbar^2$:

$$\boxed{\langle p_x^2\rangle=\left(n+\tfrac12\right)\hbar^2\alpha}$$

| $n$ | $\langle p_x^2\rangle$ |
|---|---|
| 0 | $\tfrac12\hbar^2\alpha$ |
| 1 | $\tfrac32\hbar^2\alpha$ |
| 2 | $\tfrac52\hbar^2\alpha$ |

#### Paso 5 · Comprobación directa para $n=0$
$\psi_0=(\alpha/\pi)^{1/4}e^{-\alpha x^2/2}$; $\psi_0''=(\alpha^2x^2-\alpha)\psi_0$, así que

$$\langle p_x^2\rangle=-\hbar^2\int\psi_0\psi_0''dx=\hbar^2\left(\alpha-\alpha^2\langle x^2\rangle\right)=\hbar^2\left(\alpha-\alpha^2\cdot\frac{1}{2\alpha}\right)=\tfrac12\hbar^2\alpha\ \checkmark$$

#### Paso 6 · Interpretación
$\langle p_x\rangle=0$ (oscila igual hacia un lado que hacia el otro), pero $\langle p_x^2\rangle\ne0$: la partícula **se mueve**, incluso en $n=0$. Crece con $n$ porque en los estados excitados oscila con más energía.
"""
    return Ejercicio(
        "l11_p2", "⟨p²⟩ del oscilador en n = 0, 1, 2", LIBRO, "Libro · ejercicio 11", "oscilador",
        "Evalúa el promedio del cuadrado del momento lineal $\\langle p_x^2\\rangle$ del oscilador armónico cuántico para $n=0$ y los dos primeros estados excitados ($n=1$ y $n=2$). "
        "Expresa el resultado en unidades de $\\hbar^2\\alpha$, con $\\alpha=\\sqrt{k\\mu}/\\hbar$.",
        sol, (Parte("p0", "$n=0$ (en $\\hbar^2\\alpha$)", NUM, 0.5, "ħ²α"), Parte("p1", "$n=1$ (en $\\hbar^2\\alpha$)", NUM, 1.5, "ħ²α"),
              Parte("p2", "$n=2$ (en $\\hbar^2\\alpha$)", NUM, 2.5, "ħ²α")),
        ("$\\langle E_k\\rangle=\\langle p^2\\rangle/2\\mu$.", "Virial: $\\langle E_k\\rangle=E_n/2$."), MEDIO)


def _ortog_osc() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Para $\psi_0=\left(\frac\alpha\pi\right)^{1/4}e^{-\alpha x^2/2}$ y $\psi_2=\left(\frac{\alpha}{4\pi}\right)^{1/4}(2\alpha x^2-1)e^{-\alpha x^2/2}$: **a)** son ortogonales; **b)** $\psi_2$ está normalizada (en $-\infty<x<\infty$).

#### Paso 2 · Las integrales que se necesitan
$$\int_{-\infty}^{\infty}e^{-\alpha x^2}dx=\sqrt{\frac\pi\alpha}\qquad\int_{-\infty}^{\infty}x^2e^{-\alpha x^2}dx=\frac{1}{2\alpha}\sqrt{\frac\pi\alpha}\qquad\int_{-\infty}^{\infty}x^4e^{-\alpha x^2}dx=\frac{3}{4\alpha^2}\sqrt{\frac\pi\alpha}$$

#### Paso 3 · a) Ortogonalidad
Producto de constantes: $\left(\frac\alpha\pi\right)^{1/4}\left(\frac\alpha{4\pi}\right)^{1/4}=\left(\frac{\alpha^2}{4\pi^2}\right)^{1/4}=\left(\frac{\alpha}{2\pi}\right)^{1/2}$. Las dos gaussianas $e^{-\alpha x^2/2}$ se multiplican en $e^{-\alpha x^2}$:

$$\int\psi_0\psi_2\,dx=\left(\frac{\alpha}{2\pi}\right)^{1/2}\left[2\alpha\int x^2e^{-\alpha x^2}dx-\int e^{-\alpha x^2}dx\right]$$

$$=\left(\frac{\alpha}{2\pi}\right)^{1/2}\left[2\alpha\cdot\frac{1}{2\alpha}\sqrt{\frac\pi\alpha}-\sqrt{\frac\pi\alpha}\right]=\left(\frac{\alpha}{2\pi}\right)^{1/2}\left[\sqrt{\frac\pi\alpha}-\sqrt{\frac\pi\alpha}\right]=\mathbf 0\ \checkmark$$

*Nota:* aquí **no** basta el argumento par/impar: $\psi_0$ y $\psi_2$ son las dos pares. La ortogonalidad sale de la cancelación exacta.

#### Paso 4 · b) Normalización de $\psi_2$
$(2\alpha x^2-1)^2=4\alpha^2x^4-4\alpha x^2+1$. Con la constante al cuadrado, $\left(\frac{\alpha}{4\pi}\right)^{1/2}$:

$$\int\psi_2^2dx=\left(\frac{\alpha}{4\pi}\right)^{1/2}\left[4\alpha^2\cdot\frac{3}{4\alpha^2}-4\alpha\cdot\frac1{2\alpha}+1\right]\sqrt{\frac\pi\alpha}=\left(\frac{\alpha}{4\pi}\right)^{1/2}\left(\frac{\pi}{\alpha}\right)^{1/2}[3-2+1]$$

$$=\frac12\cdot2=\mathbf 1\ \checkmark$$

#### Paso 5 · Conclusión
$\psi_0$ y $\psi_2$ son ortogonales y $\psi_2$ está normalizada. Es lo esperado: son autofunciones de $\hat H$ con **energías distintas** ($\frac12\hbar\omega$ y $\frac52\hbar\omega$), y las autofunciones de un operador hermítico con autovalores distintos siempre son ortogonales.
"""
    return Ejercicio(
        "l12_ortog_osc", "ψ₀ y ψ₂ del oscilador: ortogonales y normalizadas", LIBRO, "Libro · ejercicio 12", "oscilador",
        "Demuestra mediante la integración apropiada que las funciones del oscilador armónico $\\psi_0(x)=(\\alpha/\\pi)^{1/4}e^{-\\alpha x^2/2}$ y "
        "$\\psi_2(x)=(\\alpha/4\\pi)^{1/4}(2\\alpha x^2-1)e^{-\\alpha x^2/2}$ son ortogonales en $-\\infty<x<\\infty$ y que $\\psi_2$ está normalizada en el mismo intervalo.",
        sol, (Parte("o", "$\\int\\psi_0\\psi_2\\,dx$", NUM, 0.0, tol_rel=0.0, tol_abs=0.01), Parte("n", "$\\int\\psi_2^2\\,dx$", NUM, 1.0)),
        ("Usa las integrales gaussianas de $x^0$, $x^2$ y $x^4$.", "Las dos funciones son pares: la ortogonalidad no sale por simetría."), MEDIO)


def _masas_resorte() -> Ejercicio:
    m = 3.25e-3
    mu = m / 2
    w = math.sqrt(450 / mu)
    e0 = 0.5 * HBAR * w
    kt = KB * 298
    v = math.sqrt(e0 / m)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Dos masas de 3.25 g unidas por un resorte de $k=450\ \text{kg s}^{-2}$ (= N/m): **a)** energía de punto cero; **b)** compararla con $k_BT$ a 298 K; **c)** la velocidad de las masas si esa energía se convirtiera en energía de traslación.

#### Paso 2 · Masa reducida
Dos masas iguales: $\mu=\dfrac{m\cdot m}{m+m}=\dfrac m2=\dfrac{3.25\times10^{-3}\ \text{kg}}{2}=1.625\times10^{-3}$ kg.

#### Paso 3 · Frecuencia angular
$$\omega=\sqrt{\frac k\mu}=\sqrt{\frac{450}{1.625\times10^{-3}}}=\sqrt{<<w2>>}=<<w>>\ \text{rad/s}$$

#### Paso 4 · a) Energía de punto cero
$$E_0=\tfrac12\hbar\omega=\tfrac12(1.0546\times10^{-34})(<<w>>)=\mathbf{<<e0>>\ \text{J}}$$

#### Paso 5 · b) Comparación con la energía térmica
$k_BT=(1.381\times10^{-23}\ \text{J/K})(298\ \text{K})=<<kt>>$ J.

$$\frac{E_0}{k_BT}=\frac{<<e0>>}{<<kt>>}=\mathbf{<<r>>}$$

La energía de punto cero es **despreciable** frente a la térmica: un sistema macroscópico se comporta clásicamente.

#### Paso 6 · c) Velocidad
Si la energía se reparte entre las dos masas, cada una con velocidad $v$: $E_0=2\cdot\tfrac12mv^2=mv^2$, así que

$$v=\sqrt{\frac{E_0}{m}}=\sqrt{\frac{<<e0>>}{3.25\times10^{-3}}}=\mathbf{<<v>>\ \text{m/s}}$$

(es lo mismo que usar la masa total $2m$ en $E_0=\tfrac12(2m)v^2$). ¡Unos $10^{-15}$ m/s: imposible de detectar!
""", w2=f"{450 / mu:.4g}", w=f"{w:.2f}", e0=tex(e0), kt=tex(kt), r=tex(e0 / kt), v=tex(v))
    return Ejercicio(
        "l13_masas", "Punto cero de un oscilador macroscópico", LIBRO, "Libro · ejercicio 13", "oscilador",
        "Dos masas de **3.25 g** están unidas por un resorte con constante de fuerza $k=450\\ \\text{kg s}^{-2}$. Calcula la energía de punto cero del sistema y compárala "
        "con la energía térmica $k_BT$ a 298 K. Si la energía de punto cero se convirtiera en energía de traslación, ¿cuál sería la velocidad de las masas?",
        sol, (Parte("E0", "Energía de punto cero (en J)", NUM, e0, "J", confusiones=((math.sqrt(2), "usaste la masa de una partícula y no la masa reducida $m/2$"),)),
              Parte("r", "Cociente $E_0/k_BT$", NUM, e0 / kt),
              Parte("v", "Velocidad (en m/s)", NUM, v, "m/s", tol_rel=0.03)),
        ("Dos masas iguales: $\\mu=m/2$.", "$E_0=\\tfrac12\\hbar\\omega$ con $\\omega=\\sqrt{k/\\mu}$."), BASICO)


def _transicion_osc() -> Ejercicio:
    nu = 3.15e13
    lam = C / nu
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Un oscilador armónico cuántico de frecuencia $\nu=3.15\times10^{13}\ \text{s}^{-1}$ pasa de $n=2$ a $n=3$. Frecuencia y longitud de onda de la radiación absorbida.

#### Paso 2 · Energía de la transición
$E_n=\left(n+\tfrac12\right)h\nu$, así que

$$\Delta E=E_3-E_2=\left(3+\tfrac12\right)h\nu-\left(2+\tfrac12\right)h\nu=h\nu$$

Los niveles del oscilador están **igualmente espaciados**: subir de 2 a 3 cuesta lo mismo que subir de 0 a 1.

#### Paso 3 · Frecuencia de la radiación
El fotón absorbido tiene $h\nu_{\text{luz}}=\Delta E=h\nu$, luego

$$\nu_{\text{luz}}=\nu=\mathbf{3.15\times10^{13}\ \text{s}^{-1}}$$

¡La luz absorbida tiene **exactamente la frecuencia del oscilador**!

#### Paso 4 · Longitud de onda
$$\lambda=\frac c\nu=\frac{2.998\times10^8\ \text{m/s}}{3.15\times10^{13}\ \text{s}^{-1}}=\mathbf{<<lam>>\ \text{m}}=<<lum>>\ \mu\text{m}$$

#### Paso 5 · Interpretación
9.5 μm está en el **infrarrojo**: es donde se miden las vibraciones moleculares (espectroscopía IR).
""", lam=tex(lam), lum=f"{lam * 1e6:.2f}")
    return Ejercicio(
        "l14_transicion", "Radiación absorbida en la transición 2 → 3", LIBRO, "Libro · ejercicio 14", "oscilador",
        "Calcula la frecuencia y la longitud de onda de la radiación absorbida cuando un oscilador armónico cuántico con frecuencia $3.15\\times10^{13}\\ \\text{s}^{-1}$ "
        "realiza una transición del estado $n=2$ al $n=3$.",
        sol, (Parte("nu", "Frecuencia (en s⁻¹)", NUM, nu, "s⁻¹"),
              Parte("lam", "Longitud de onda (en μm)", NUM, lam * 1e6, "μm", confusiones=((1e-6, "diste el valor en metros; se pide en μm"),))),
        ("¿Cuánto vale $E_3-E_2$ en el oscilador armónico?",), BASICO)


def _virial_n0() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Los valores medios de la energía cinética y potencial del oscilador armónico en el estado fundamental ($n=0$).

#### Paso 2 · Energía total
$$E_0=\left(0+\tfrac12\right)\hbar\omega=\tfrac12\hbar\omega$$

#### Paso 3 · Cómo se reparte (teorema del virial)
Para un potencial $V=ax^s$ se cumple $2\langle E_k\rangle=s\langle E_p\rangle$. En el oscilador $V=\tfrac12kx^2$ ($s=2$): $\langle E_k\rangle=\langle E_p\rangle$. Como suman $E_0$:

$$\langle E_k\rangle=\langle E_p\rangle=\tfrac12E_0=\boxed{\tfrac14\hbar\omega}$$

#### Paso 4 · Comprobación con la integral de la energía potencial
$\langle x^2\rangle_0=\dfrac{1}{2\alpha}$ con $\alpha=\mu\omega/\hbar$, así que

$$\langle E_p\rangle=\tfrac12k\langle x^2\rangle=\tfrac12\mu\omega^2\cdot\frac{\hbar}{2\mu\omega}=\tfrac14\hbar\omega\ \checkmark$$

#### Paso 5 · Interpretación
Aun en el estado fundamental hay energía cinética y potencial: la partícula **nunca está quieta en el fondo del pozo** (eso violaría el principio de incertidumbre).
"""
    return Ejercicio(
        "l15_virial", "Energías cinética y potencial en n = 0", LIBRO, "Libro · ejercicio 15", "oscilador",
        "Evalúa la energía cinética promedio y la energía potencial promedio para el estado fundamental ($n=0$) del oscilador armónico.",
        sol, (Parte("Ek", "$\\langle E_k\\rangle$ (en $\\hbar\\omega$)", NUM, 0.25, "ħω"), Parte("Ep", "$\\langle E_p\\rangle$ (en $\\hbar\\omega$)", NUM, 0.25, "ħω")),
        ("$E_0=\\frac12\\hbar\\omega$.", "Virial con $s=2$."), BASICO)


def _cl2_k() -> Ejercicio:
    mu = M_CL35 / 2 * U
    nu = 1.68e13
    k = (2 * math.pi * nu) ** 2 * mu
    f = k * 0.0225
    m = f / G
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La frecuencia de vibración del ³⁵Cl₂ es $1.68\times10^{13}\ \text{s}^{-1}$. **a)** constante de fuerza; **b)** qué masa habría que colgar de un resorte clásico con esa $k$ para estirarlo 2.25 cm.

#### Paso 2 · Masa reducida
Homonuclear: $\mu=\dfrac{m_{Cl}}{2}=\dfrac{34.969\ \text{u}}{2}=17.484$ u $=17.484\times1.6605\times10^{-27}=<<mu>>$ kg.

#### Paso 3 · Constante de fuerza
De $\nu=\frac{1}{2\pi}\sqrt{k/\mu}$:

$$k=4\pi^2\nu^2\mu=4\pi^2(1.68\times10^{13})^2(<<mu>>)=\mathbf{<<k>>\ \text{N/m}}$$

#### Paso 4 · Fuerza para estirar 2.25 cm
Ley de Hooke con $x=2.25\ \text{cm}=0.0225$ m:

$$F=kx=(<<k>>)(0.0225)=<<f>>\ \text{N}$$

#### Paso 5 · Masa
En equilibrio esa fuerza es el peso, $F=mg$:

$$m=\frac Fg=\frac{<<f>>\ \text{N}}{9.81\ \text{m/s}^2}=\mathbf{<<m>>\ \text{kg}}$$
""", mu=tex(mu), k=f"{k:.1f}", f=f"{f:.3f}", m=f"{m:.3f}")
    return Ejercicio(
        "l16_cl2", "Constante de fuerza del ³⁵Cl₂", LIBRO, "Libro · ejercicio 16", "oscilador",
        "La frecuencia de vibración de la molécula de ³⁵Cl₂ es de $1.68\\times10^{13}\\ \\text{s}^{-1}$. Calcula la constante de fuerza de la molécula. "
        "¿Qué masa habría que colgar de un resorte clásico con esta constante para estirarlo **2.25 cm**? Usa $g=9.81$ m/s².",
        sol, (Parte("k", "Constante de fuerza (en N/m)", NUM, k, "N/m", confusiones=((2.0, "usaste la masa de un átomo en lugar de $\\mu=m/2$"),)),
              Parte("m", "Masa colgada (en kg)", NUM, m, "kg")),
        ("$k=4\\pi^2\\nu^2\\mu$.", "$kx=mg$."), BASICO)


def _x2_osc() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
$\langle x^2\rangle$ para el oscilador armónico en $n=0,1,2$. Se puede integrar, pero el teorema del virial lo da en dos líneas.

#### Paso 2 · Energía potencial media
$$\langle E_p\rangle=\left\langle\tfrac12kx^2\right\rangle=\tfrac12k\langle x^2\rangle\quad\Rightarrow\quad\langle x^2\rangle=\frac{2\langle E_p\rangle}{k}$$

#### Paso 3 · Virial
$\langle E_p\rangle=\tfrac12E_n$, así que

$$\langle x^2\rangle=\frac{E_n}{k}=\frac{\left(n+\frac12\right)\hbar\omega}{\mu\omega^2}=\left(n+\tfrac12\right)\frac{\hbar}{\mu\omega}$$

(se usó $k=\mu\omega^2$).

#### Paso 4 · Con $\alpha=\mu\omega/\hbar$
$\dfrac{\hbar}{\mu\omega}=\dfrac1\alpha$:

$$\boxed{\langle x^2\rangle=\frac{n+\frac12}{\alpha}}$$

| $n$ | $\langle x^2\rangle$ |
|---|---|
| 0 | $\dfrac{1}{2\alpha}$ |
| 1 | $\dfrac{3}{2\alpha}$ |
| 2 | $\dfrac{5}{2\alpha}$ |

#### Paso 5 · Comprobación para $n=0$ con la integral
$$\langle x^2\rangle=\sqrt{\frac\alpha\pi}\int x^2e^{-\alpha x^2}dx=\sqrt{\frac\alpha\pi}\cdot\frac{1}{2\alpha}\sqrt{\frac\pi\alpha}=\frac1{2\alpha}\ \checkmark$$

#### Paso 6 · Interpretación
$\langle x\rangle=0$ pero $\langle x^2\rangle\ne0$: la molécula oscila alrededor del equilibrio y la amplitud típica, $\sqrt{\langle x^2\rangle}$, crece con $n$. *Ojo con la notación:* en el cuaderno aparece «$\hbar/2a$»; el resultado correcto es $1/(2\alpha)=\hbar/(2\mu\omega)$.
"""
    return Ejercicio(
        "l17_x2", "⟨x²⟩ del oscilador en n = 0, 1, 2", LIBRO, "Libro · ejercicio 17", "oscilador",
        "Evalúa $\\langle x^2\\rangle$ para $n=0$ y los dos primeros estados excitados ($n=1$ y $n=2$) del oscilador armónico cuántico. "
        "Expresa el resultado en unidades de $1/\\alpha$, con $\\alpha=\\mu\\omega/\\hbar$.",
        sol, (Parte("x0", "$n=0$ (en $1/\\alpha$)", NUM, 0.5, "1/α"), Parte("x1", "$n=1$ (en $1/\\alpha$)", NUM, 1.5, "1/α"),
              Parte("x2", "$n=2$ (en $1/\\alpha$)", NUM, 2.5, "1/α")),
        ("$\\langle E_p\\rangle=\\frac12k\\langle x^2\\rangle$.", "Virial: $\\langle E_p\\rangle=E_n/2$."), MEDIO)


def _moneda() -> Ejercicio:
    m, nu, amp = 8.31e-3, 7.50, 0.725e-2
    k = (2 * math.pi * nu) ** 2 * m
    e0 = 0.5 * H * nu
    et = 0.5 * k * amp ** 2
    n = et / (H * nu) - 0.5
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Una moneda de 8.31 g colgada de una banda elástica vibra a $\nu=7.50\ \text{s}^{-1}$. **a)** $k$ de la banda; **b)** energía de punto cero; **c)** energía de vibración total si la amplitud es 0.725 cm; **d)** el número cuántico $n$ que corresponde a esa energía.

#### Paso 2 · a) Constante de fuerza
Aquí la moneda cuelga de un soporte fijo: la masa que oscila es la de la moneda ($\mu=m$).

$$k=4\pi^2\nu^2m=4\pi^2(7.50)^2(8.31\times10^{-3})=\mathbf{<<k>>\ \text{N/m}}$$

#### Paso 3 · b) Energía de punto cero
$$E_0=\tfrac12h\nu=\tfrac12(6.626\times10^{-34})(7.50)=\mathbf{<<e0>>\ \text{J}}$$

#### Paso 4 · c) Energía total clásica
En el punto de máximo desplazamiento (amplitud $A$) la velocidad es cero y toda la energía es potencial:

$$E=\tfrac12kA^2=\tfrac12(<<k>>)(0.725\times10^{-2})^2=\mathbf{<<et>>\ \text{J}}$$

(¡ojo! la amplitud en **metros**: 0.725 cm = $7.25\times10^{-3}$ m).

#### Paso 5 · d) Número cuántico
Se iguala con la energía cuántica, $E=\left(n+\tfrac12\right)h\nu$:

$$n=\frac{E}{h\nu}-\frac12=\frac{<<et>>}{(6.626\times10^{-34})(7.50)}-\frac12=\mathbf{<<n>>}$$

#### Paso 6 · Interpretación
$n\sim10^{29}$: un número cuántico gigantesco. Los niveles están tan juntos (separados $h\nu\approx5\times10^{-33}$ J) que la energía parece continua. Es el **principio de correspondencia**: para objetos macroscópicos la mecánica cuántica reproduce la clásica.
""", k=f"{k:.2f}", e0=tex(e0), et=tex(et), n=tex(n))
    return Ejercicio(
        "l18_moneda", "Una moneda colgada de una banda elástica", LIBRO, "Libro · ejercicio 18", "oscilador",
        "Una moneda de **8.31 g** suspendida de una banda de caucho tiene una frecuencia de vibración de **7.50 s⁻¹**. Calcula: "
        "**a)** la constante de fuerza del caucho; **b)** la energía de punto cero; **c)** la energía vibracional total si el desplazamiento máximo es de **0.725 cm**; "
        "**d)** el número cuántico vibracional correspondiente a la energía del inciso c.",
        sol, (Parte("k", "a) $k$ (en N/m)", NUM, k, "N/m"), Parte("E0", "b) $E_0$ (en J)", NUM, e0, "J"),
              Parte("E", "c) Energía total (en J)", NUM, et, "J", confusiones=((1e4, "usaste la amplitud en cm; pásala a metros"),)),
              Parte("n", "d) Número cuántico $n$", NUM, n)),
        ("$k=4\\pi^2\\nu^2m$.", "Energía total = $\\frac12kA^2$ (amplitud en metros).", "$n=E/h\\nu-\\frac12$."), BASICO,
        nota="En el cuaderno aparece n ≈ 9.76×10²⁰; con los datos del enunciado el resultado es 9.76×10²⁸.")


def _cm_hf() -> Ejercicio:
    R = 91.68
    d_f = M_H * R / (M_H + M_F)
    d_h = M_F * R / (M_H + M_F)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La posición del **centro de masa** de la molécula ¹H¹⁹F, con longitud de enlace 91.68 pm.

#### Paso 2 · Elegir el origen
Se pone un átomo en el origen y el otro a la distancia $R$ sobre el eje $x$. Por ejemplo, el **F en $x=0$** y el **H en $x=R$**.

#### Paso 3 · Fórmula del centro de masa
$$x_{cm}=\frac{m_Fx_F+m_Hx_H}{m_F+m_H}=\frac{m_F\cdot0+m_H\cdot R}{m_F+m_H}=\frac{m_H}{m_F+m_H}R$$

#### Paso 4 · Sustituir
$$x_{cm}=\frac{1.0078}{18.9984+1.0078}\times91.68\ \text{pm}=\frac{1.0078}{20.006}\times91.68=\mathbf{<<df>>\ \text{pm}}\ \text{desde el F}$$

Medido desde el H: $91.68-<<df>>=\mathbf{<<dh>>\ \text{pm}}$ (que es $\frac{m_F}{m_F+m_H}R$).

#### Paso 5 · Interpretación
El centro de masa está **casi encima del átomo de flúor**, porque el F es 19 veces más pesado. Al rotar, el F apenas se mueve y el H gira a su alrededor: por eso el momento de inercia $I=\mu R^2$ es prácticamente $m_HR^2$.

*Error típico:* poner $m_F$ en el numerador con el F en el origen; eso da la distancia desde el H.
""", df=f"{d_f:.2f}", dh=f"{d_h:.2f}")
    return Ejercicio(
        "l19_cm_hf", "Centro de masa del HF", LIBRO, "Libro · ejercicio 19", "esfera",
        "Calcula la posición del centro de masa de la molécula ¹H¹⁹F, que tiene una longitud de enlace de **91.68 pm**.",
        sol, (Parte("dF", "Distancia del centro de masa al núcleo de F (en pm)", NUM, d_f, "pm",
                    confusiones=((d_h / d_f, "esa es la distancia desde el H"),)),
              Parte("dH", "Distancia del centro de masa al núcleo de H (en pm)", NUM, d_h, "pm")),
        ("$x_{cm}=\\frac{m_1x_1+m_2x_2}{m_1+m_2}$.", "Pon uno de los átomos en el origen."), BASICO)


def _y20_norm() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Demostrar que $Y_2^0=\left(\frac{5}{16\pi}\right)^{1/2}(3\cos^2\theta-1)$ está **normalizada** en $0\le\theta\le\pi$, $0\le\phi\le2\pi$.

#### Paso 2 · Condición con el elemento de ángulo sólido
En la esfera, el elemento de área (ángulo sólido) es $d\Omega=\sin\theta\,d\theta\,d\phi$. Hay que comprobar

$$\int_0^{2\pi}d\phi\int_0^\pi|Y_2^0|^2\sin\theta\,d\theta=1$$

#### Paso 3 · Separar
$|Y_2^0|^2=\frac{5}{16\pi}(3\cos^2\theta-1)^2$ no depende de $\phi$:

$$\frac{5}{16\pi}\cdot2\pi\cdot\int_0^\pi(3\cos^2\theta-1)^2\sin\theta\,d\theta=\frac58\int_0^\pi(3\cos^2\theta-1)^2\sin\theta\,d\theta$$

#### Paso 4 · Cambio de variable $x=\cos\theta$
$dx=-\sin\theta\,d\theta$; cuando $\theta=0$, $x=1$, y cuando $\theta=\pi$, $x=-1$. El signo menos invierte los límites:

$$\int_0^\pi(3\cos^2\theta-1)^2\sin\theta\,d\theta=\int_{-1}^{1}(3x^2-1)^2dx=\int_{-1}^{1}(9x^4-6x^2+1)dx$$

#### Paso 5 · Integrar
$$\left[\frac{9x^5}{5}-2x^3+x\right]_{-1}^{1}=\left(\frac95-2+1\right)-\left(-\frac95+2-1\right)=\frac45+\frac45=\frac85$$

#### Paso 6 · Resultado
$$\frac58\cdot\frac85=\mathbf 1\ \checkmark$$

Está normalizada. *Error típico:* olvidar el $\sin\theta$ de $d\Omega$; la integral no daría 1.
"""
    return Ejercicio(
        "l20_y20_norm", "Y₂⁰ está normalizada", LIBRO, "Libro · ejercicio 20", "esfera",
        "Demuestra que la función $Y_2^0(\\theta,\\phi)=\\left(\\frac{5}{16\\pi}\\right)^{1/2}(3\\cos^2\\theta-1)$ está normalizada en $0\\le\\theta\\le\\pi$, $0\\le\\phi\\le2\\pi$.",
        sol, (Parte("I", "Valor de $\\displaystyle\\int_0^\\pi(3\\cos^2\\theta-1)^2\\sin\\theta\\,d\\theta$", NUM, 1.6),
              Parte("N", "Valor de la integral de normalización completa", NUM, 1.0)),
        ("$d\\Omega=\\sin\\theta\\,d\\theta\\,d\\phi$.", "Haz $x=\\cos\\theta$."), BASICO)


def _phi_lz() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
¿Se pueden conocer **a la vez** la orientación angular $\phi$ de una molécula que gira en un plano y su momento angular $l_z$? Se responde calculando el conmutador $\left[\hat\phi,\ -i\hbar\frac{\partial}{\partial\phi}\right]$.

#### Paso 2 · Aplicar a una función de prueba $f(\phi)$
$$[\hat\phi,\hat l_z]f=\hat\phi(\hat l_zf)-\hat l_z(\hat\phi f)$$

- Primer término: $\phi\left(-i\hbar\dfrac{\partial f}{\partial\phi}\right)$
- Segundo término, con **regla del producto**: $-i\hbar\dfrac{\partial(\phi f)}{\partial\phi}=-i\hbar\left(f+\phi\dfrac{\partial f}{\partial\phi}\right)$

#### Paso 3 · Restar
$$[\hat\phi,\hat l_z]f=-i\hbar\phi f'+i\hbar f+i\hbar\phi f'=i\hbar f$$

$$\boxed{[\hat\phi,\hat l_z]=i\hbar}$$

#### Paso 4 · Conclusión
No es cero: **no conmutan**, así que **no** se pueden conocer simultáneamente con exactitud. Es el mismo resultado que $[\hat x,\hat p_x]=i\hbar$: el ángulo y el momento angular son variables complementarias, igual que la posición y el momento lineal.

#### Paso 5 · Ejemplo concreto
En el estado $\Phi_m=\frac{1}{\sqrt{2\pi}}e^{im\phi}$, $l_z=m\hbar$ está perfectamente definido, y la probabilidad $|\Phi_m|^2=\frac1{2\pi}$ es la **misma para todo $\phi$**: la orientación es completamente desconocida.
"""
    return Ejercicio(
        "l21_phi_lz", "Orientación y momento angular del rotor 2D", LIBRO, "Libro · ejercicio 21", "conmutadores",
        "¿Es posible conocer simultáneamente la orientación angular de una molécula que rota en un espacio bidimensional y su momento angular? "
        "Calcula el conmutador $\\left[\\phi,\\ -i\\hbar\\,\\partial/\\partial\\phi\\right]$.",
        sol, (Parte("c", "$[\\hat\\phi,\\hat l_z]=$", OPC, opciones=("$i\\hbar$", "$0$", "$-i\\hbar$", "$\\hbar$"), correcta=0,
                    explicacion="La regla del producto deja $+i\\hbar f$."),),
        ("Aplica el conmutador a una función $f(\\phi)$ y usa la regla del producto.",), BASICO)


def _cl2_velocidad() -> Ejercicio:
    mu = M_CL35 / 2 * U
    nu = math.sqrt(323 / mu) / (2 * math.pi)
    e0 = 0.5 * H * nu
    M = 2 * M_CL35 * U
    v = math.sqrt(2 * e0 / M)
    vr = math.sqrt(3 * KB * 300 / M)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Para el ³⁵Cl₂ con $k=323$ N/m: **a)** energía vibracional de punto cero; **b)** si toda esa energía se convirtiera en traslación, la velocidad de la molécula; **c)** compararla con la velocidad cuadrática media $v_{rms}$ a 300 K.

#### Paso 2 · Frecuencia de vibración
Masa reducida: $\mu=\frac{34.969}{2}$ u $=<<mu>>$ kg.

$$\nu=\frac1{2\pi}\sqrt{\frac k\mu}=\frac1{2\pi}\sqrt{\frac{323}{<<mu>>}}=<<nu>>\ \text{s}^{-1}$$

#### Paso 3 · a) Energía de punto cero
$$E_0=\tfrac12h\nu=\tfrac12(6.626\times10^{-34})(<<nu>>)=\mathbf{<<e0>>\ \text{J}}$$

#### Paso 4 · b) Convertir en traslación
Ahora se mueve **la molécula entera**, así que se usa su masa total $M=2\times34.969$ u $=<<M>>$ kg (no la masa reducida):

$$E_0=\tfrac12Mv^2\ \Rightarrow\ v=\sqrt{\frac{2E_0}{M}}=\sqrt{\frac{2(<<e0>>)}{<<M>>}}=\mathbf{<<v>>\ \text{m/s}}$$

#### Paso 5 · c) Velocidad cuadrática media a 300 K
De la teoría cinética, $\tfrac12Mv_{rms}^2=\tfrac32k_BT$:

$$v_{rms}=\sqrt{\frac{3k_BT}{M}}=\sqrt{\frac{3(1.381\times10^{-23})(300)}{<<M>>}}=\mathbf{<<vr>>\ \text{m/s}}$$

#### Paso 6 · Comparación
$$\frac{v}{v_{rms}}=\frac{<<v>>}{<<vr>>}=\mathbf{<<r>>}$$

¡Casi iguales! Para el Cl₂ la energía de punto cero ($\approx<<e0>>$ J) es comparable a la energía térmica de traslación ($\tfrac32k_BT=<<et>>$ J). A diferencia del ejercicio 13 (masas de gramos), aquí la energía cuántica de punto cero **no** es despreciable.
""", mu=tex(mu), nu=tex(nu), e0=tex(e0), M=tex(M), v=f"{v:.1f}", vr=f"{vr:.1f}", r=f"{v / vr:.3f}", et=tex(1.5 * KB * 300))
    return Ejercicio(
        "l22_cl2_v", "Punto cero del Cl₂ frente a la agitación térmica", LIBRO, "Libro · ejercicio 22", "oscilador",
        "La constante de fuerza del ³⁵Cl₂ es de **323 N m⁻¹**. Calcula la energía vibracional de punto cero de esta molécula. Si esta energía se convirtiera en energía "
        "de traslación, ¿qué tan rápido se movería la molécula? Compara esta velocidad con la velocidad cuadrática media $v_{rms}$ a 300 K.",
        sol, (Parte("E0", "Energía de punto cero (en J)", NUM, e0, "J"), Parte("v", "Velocidad de traslación (en m/s)", NUM, v, "m/s",
                    confusiones=((2.0, "usaste la masa reducida; al trasladarse se mueve toda la molécula (masa $M=2m$)"),)),
              Parte("vr", "$v_{rms}$ a 300 K (en m/s)", NUM, vr, "m/s")),
        ("$E_0=\\frac12h\\nu$ con $\\nu=\\frac1{2\\pi}\\sqrt{k/\\mu}$.", "Para la traslación usa la masa total de la molécula."), MEDIO)


# ---------------------------------------------------------------------
# Átomo de hidrógeno
# ---------------------------------------------------------------------
def _psi320_negativo() -> Ejercicio:
    p = 2 / (3 * math.sqrt(3))
    t0 = math.degrees(math.acos(1 / math.sqrt(3)))
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La probabilidad de encontrar al electrón en la región donde $\psi_{320}$ es **negativa** (la región toroidal, alrededor del plano $xy$).

#### Paso 2 · ¿Dónde es negativa?
$\psi_{320}=R_{32}(r)\,Y_2^0(\theta)$. La parte radial $R_{32}\propto r^2e^{-r/3a_0}$ es **positiva** para todo $r>0$. El signo lo da $Y_2^0\propto3\cos^2\theta-1$, negativo cuando $\cos^2\theta<\tfrac13$, es decir

$$\theta_0<\theta<\pi-\theta_0\qquad\theta_0=\arccos\frac1{\sqrt3}=<<t0>>^\circ$$

Es la región entre los dos conos nodales: un «anillo grueso» alrededor del plano $xy$.

#### Paso 3 · Plantear la probabilidad
$$P=\underbrace{\int_0^\infty R_{32}^2r^2dr}_{=1\ (\text{normalizada})}\cdot\int_0^{2\pi}d\phi\int_{\theta_0}^{\pi-\theta_0}\frac{5}{16\pi}(3\cos^2\theta-1)^2\sin\theta\,d\theta$$

La región incluye **todos** los $r$, así que la parte radial completa vale 1.

#### Paso 4 · Parte angular
$\int d\phi=2\pi$, y con $x=\cos\theta$ los límites pasan a $x=\pm\frac1{\sqrt3}$:

$$P=2\pi\cdot\frac{5}{16\pi}\int_{-1/\sqrt3}^{1/\sqrt3}(9x^4-6x^2+1)dx=\frac58\cdot2\left[\frac{9x^5}{5}-2x^3+x\right]_0^{1/\sqrt3}$$

(el integrando es par: se duplica la mitad).

#### Paso 5 · Evaluar en $x=1/\sqrt3$
- $x=\frac1{\sqrt3}$, $x^3=\frac1{3\sqrt3}$, $x^5=\frac1{9\sqrt3}$
- $\frac95x^5=\frac{1}{5\sqrt3}$, $\ -2x^3=-\frac{2}{3\sqrt3}$, $\ x=\frac{1}{\sqrt3}$
- Suma: $\frac1{\sqrt3}\left(\frac15-\frac23+1\right)=\frac{1}{\sqrt3}\cdot\frac{8}{15}$

$$P=\frac58\cdot2\cdot\frac{8}{15\sqrt3}=\frac{2}{3\sqrt3}=\mathbf{<<p>>}$$

#### Paso 6 · Interpretación
El electrón está en el anillo negativo un **38.5 %** del tiempo y en los dos lóbulos positivos (a lo largo de $z$) el 61.5 % restante. El signo de $\psi$ no se mide, pero sí define regiones con probabilidades distintas.
""", t0=f"{t0:.2f}", p=f"{p:.4f}")
    return Ejercicio(
        "h03_negativo", "Probabilidad en la región negativa de ψ₃₂₀", LIBRO, "Libro (hidrógeno) · ejercicio 3", "hidrogeno",
        "Determina la probabilidad de encontrar al electrón en la región en la que la función de onda $\\psi_{320}$ es negativa (la región toroidal).",
        sol, (Parte("P", "Probabilidad", NUM, p, tol_rel=0.01),),
        ("El signo lo da $3\\cos^2\\theta-1$; la parte radial está normalizada.", "Haz $x=\\cos\\theta$ y usa límites $\\pm1/\\sqrt3$."), AVANZADO)


def _potencial_1s() -> Ejercicio:
    v_ev = -2 * 13.605693122994
    sol = llenar(r"""
#### Paso 1 · Qué se pide
El valor esperado de la energía potencial $\langle V\rangle$ del electrón 1s del hidrógeno, y compararlo con la energía total.

#### Paso 2 · Planteamiento
$$\psi_{1s}=\frac{1}{\sqrt{\pi a_0^3}}e^{-r/a_0}\qquad\hat V=-\frac{e^2}{4\pi\varepsilon_0r}\qquad\langle V\rangle=\int\psi_{1s}^*\hat V\psi_{1s}\,d\tau$$

con $d\tau=r^2\sin\theta\,dr\,d\theta\,d\phi$.

#### Paso 3 · Separar la parte angular
$\psi_{1s}$ no depende de los ángulos: $\int\sin\theta\,d\theta\,d\phi=4\pi$. Entonces

$$\langle V\rangle=4\pi\cdot\frac{1}{\pi a_0^3}\left(-\frac{e^2}{4\pi\varepsilon_0}\right)\int_0^\infty e^{-2r/a_0}\,\frac1r\,r^2\,dr=-\frac{4}{a_0^3}\frac{e^2}{4\pi\varepsilon_0}\int_0^\infty r\,e^{-2r/a_0}dr$$

(el $1/r$ del potencial cancela una $r$ del $r^2$).

#### Paso 4 · La integral radial
Con $\int_0^\infty r^ne^{-br}dr=\dfrac{n!}{b^{n+1}}$, $n=1$, $b=2/a_0$:

$$\int_0^\infty r\,e^{-2r/a_0}dr=\frac{1!}{(2/a_0)^2}=\frac{a_0^2}{4}$$

#### Paso 5 · Juntar
$$\langle V\rangle=-\frac{4}{a_0^3}\cdot\frac{a_0^2}{4}\cdot\frac{e^2}{4\pi\varepsilon_0}=-\frac{e^2}{4\pi\varepsilon_0a_0}=\mathbf{<<v>>\ \text{eV}}$$

#### Paso 6 · Comparación con la energía total
$E_1=-\dfrac{e^2}{8\pi\varepsilon_0a_0}=-13.6$ eV. Entonces

$$\langle V\rangle=2E_1\qquad\text{y}\qquad\langle T\rangle=E_1-\langle V\rangle=-E_1=+13.6\ \text{eV}=-\tfrac12\langle V\rangle$$

Es el **teorema del virial** para el potencial de Coulomb ($s=-1$): $2\langle T\rangle=-\langle V\rangle$.
""", v=f"{v_ev:.2f}")
    return Ejercicio(
        "h04_potencial", "Energía potencial media del electrón 1s", LIBRO, "Libro (hidrógeno) · ejercicio 4", "hidrogeno",
        "Calcula el valor esperado de la energía potencial del átomo de H con el electrón en el orbital 1s. Compara el resultado con la energía total.",
        sol, (Parte("V", "$\\langle V\\rangle$ (en eV)", NUM, v_ev, "eV", confusiones=((0.5, "ese es $E_1$; $\\langle V\\rangle=2E_1$"),)),
              Parte("T", "$\\langle T\\rangle$ (en eV)", NUM, -v_ev / 2, "eV")),
        ("$\\int_0^\\infty r^ne^{-br}dr=n!/b^{n+1}$.", "La parte angular aporta $4\\pi$."), MEDIO)


def _prob_1s() -> Ejercicio:
    p = 5 * math.exp(-2) - 13 * math.exp(-4)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La probabilidad de que el electrón 1s del H esté entre $r=a_0$ y $r=2a_0$ (en cualquier dirección).

#### Paso 2 · Usar la distribución radial
Como la pregunta solo es sobre la distancia, se usa la **distribución radial**, que ya incluye el $4\pi r^2$ de la capa esférica:

$$P(r)=r^2R_{10}^2=\frac{4}{a_0^3}r^2e^{-2r/a_0}\qquad P=\int_{a_0}^{2a_0}\frac{4}{a_0^3}r^2e^{-2r/a_0}dr$$

#### Paso 3 · Cambio de variable
$x=\dfrac{2r}{a_0}$, así que $r=\dfrac{a_0x}{2}$ y $dr=\dfrac{a_0}{2}dx$. Límites: $r=a_0\to x=2$; $r=2a_0\to x=4$.

$$P=\frac{4}{a_0^3}\int_2^4\frac{a_0^2x^2}{4}e^{-x}\frac{a_0}{2}dx=\frac12\int_2^4x^2e^{-x}dx$$

(las $a_0$ se cancelan, como debe ser para una probabilidad).

#### Paso 4 · Primitiva (integración por partes dos veces)
$$\int x^2e^{-x}dx=-e^{-x}\left(x^2+2x+2\right)$$

*Comprobación derivando:* $e^{-x}(x^2+2x+2)-e^{-x}(2x+2)=x^2e^{-x}$ ✓

#### Paso 5 · Evaluar
- En $x=4$: $-e^{-4}(16+8+2)=-26e^{-4}$
- En $x=2$: $-e^{-2}(4+4+2)=-10e^{-2}$

$$P=\frac12\left[-26e^{-4}+10e^{-2}\right]=5e^{-2}-13e^{-4}=0.6767-0.2381=\mathbf{<<p>>}$$

#### Paso 6 · Interpretación
Casi un **44 %** de probabilidad en esa capa, que contiene el máximo de la distribución radial ($r=a_0$) y la zona de mayor peso justo después.
""", p=f"{p:.4f}")
    return Ejercicio(
        "h05_prob", "Probabilidad entre a₀ y 2a₀ (1s)", LIBRO, "Libro (hidrógeno) · ejercicio 5", "hidrogeno",
        "Calcula la probabilidad de que el electrón 1s del átomo de H se encuentre entre $r=a_0$ y $r=2a_0$.",
        sol, (Parte("P", "Probabilidad", NUM, p, tol_rel=0.01),),
        ("Usa la distribución radial $P(r)=r^2R_{10}^2$.", "Cambio $x=2r/a_0$ y $\\int x^2e^{-x}dx=-e^{-x}(x^2+2x+2)$."), MEDIO,
        nota="En el cuaderno el resultado aparece como 0.4366; el valor exacto de 5e⁻² − 13e⁻⁴ es 0.4386.")


def _max_2p() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Las distancias al núcleo de los máximos (principal y secundario, si los hay) de la distribución radial del orbital 2p.

#### Paso 2 · Distribución radial
$$R_{21}=\frac{1}{\sqrt{24}}\left(\frac1{a_0}\right)^{3/2}\frac{r}{a_0}e^{-r/2a_0}\qquad P(r)=r^2R_{21}^2=\frac{1}{24a_0^5}\,r^4e^{-r/a_0}$$

(al elevar al cuadrado, $e^{-r/2a_0}$ se convierte en $e^{-r/a_0}$).

#### Paso 3 · Derivar e igualar a cero
$$\frac{dP}{dr}\propto4r^3e^{-r/a_0}-\frac{r^4}{a_0}e^{-r/a_0}=r^3e^{-r/a_0}\left(4-\frac{r}{a_0}\right)=0$$

Soluciones: $r=0$ (es un mínimo, $P(0)=0$) y

$$4-\frac{r}{a_0}=0\ \Rightarrow\ \mathbf{r=4a_0}$$

#### Paso 4 · ¿Hay máximo secundario?
**No.** El 2p tiene $n-l-1=2-1-1=0$ nodos radiales, y la distribución radial tiene tantos máximos como (nodos radiales + 1) = **1**. Solo hay un máximo, en $4a_0\approx212$ pm.

#### Paso 5 · Comprobación con la regla general
Para orbitales con $l=n-1$ (1s, 2p, 3d…) el único máximo está en $r=n^2a_0$: $2^2a_0=4a_0$ ✓ (1s en $a_0$, 3d en $9a_0$).
"""
    return Ejercicio(
        "h06_2p", "Máximos de la distribución radial 2p", LIBRO, "Libro (hidrógeno) · ejercicio 6", "hidrogeno",
        "Calcula la distancia desde el núcleo a la cual la función de distribución radial del orbital 2p tiene su máximo principal y su máximo secundario, si los hay.",
        sol, (Parte("r", "Máximo principal (en $a_0$)", NUM, 4.0, "a₀", confusiones=((0.5, "ese es el punto de máxima $|\\psi|^2$; la distribución radial lleva el factor $r^2$"),)),
              Parte("n", "Número de máximos", NUM, 1.0, tol_rel=0.0, tol_abs=0.1)),
        ("$P(r)=r^2R_{21}^2\\propto r^4e^{-r/a_0}$.", "¿Cuántos nodos radiales tiene el 2p?"), BASICO)


def _hidrogenoides() -> Ejercicio:
    ry = 13.605693122994
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Los iones de un solo electrón (He⁺, Li²⁺…) se describen con las funciones del H cambiando $1/a_0$ por $Z/a_0$. Para el 1s:

$$\psi(r)=\frac{1}{\sqrt\pi}\left(\frac{Z}{a_0}\right)^{3/2}e^{-Zr/a_0}$$

Hay que **sustituir** en la ecuación de Schrödinger y obtener $E$ para H, He⁺ y Li²⁺.

#### Paso 2 · La ecuación
Con núcleo de carga $+Ze$, $V=-\dfrac{Ze^2}{4\pi\varepsilon_0r}$. Para $l=0$ solo hay parte radial del laplaciano:

$$-\frac{\hbar^2}{2m_e}\frac{1}{r^2}\frac{d}{dr}\left(r^2\frac{d\psi}{dr}\right)-\frac{Ze^2}{4\pi\varepsilon_0r}\psi=E\psi$$

#### Paso 3 · Derivadas
1. $\dfrac{d\psi}{dr}=-\dfrac Z{a_0}\psi$
2. $r^2\dfrac{d\psi}{dr}=-\dfrac Z{a_0}r^2\psi$
3. $\dfrac{d}{dr}\left(-\dfrac Z{a_0}r^2\psi\right)=-\dfrac Z{a_0}\left(2r\psi-\dfrac Z{a_0}r^2\psi\right)$
4. Dividir entre $r^2$: $\nabla^2\psi=\left(\dfrac{Z^2}{a_0^2}-\dfrac{2Z}{a_0r}\right)\psi$

#### Paso 4 · Sustituir
$$\left[-\frac{\hbar^2Z^2}{2m_ea_0^2}+\frac{\hbar^2Z}{m_ea_0}\cdot\frac1r-\frac{Ze^2}{4\pi\varepsilon_0}\cdot\frac1r\right]\psi=E\psi$$

#### Paso 5 · Los términos con $1/r$ se cancelan
Para que $E$ sea una constante, lo que depende de $r$ debe desaparecer: $\dfrac{\hbar^2Z}{m_ea_0}=\dfrac{Ze^2}{4\pi\varepsilon_0}$. Esto se cumple **exactamente** porque $a_0=\dfrac{4\pi\varepsilon_0\hbar^2}{m_ee^2}$. Lo que queda:

$$E=-\frac{\hbar^2Z^2}{2m_ea_0^2}=-Z^2\frac{e^2}{8\pi\varepsilon_0a_0}=-Z^2\,(13.606\ \text{eV})$$

#### Paso 6 · Los tres casos
| Especie | $Z$ | $E_{1s}$ (eV) | $E_{1s}$ (J) |
|---|---|---|---|
| H | 1 | <<eh>> | <<jh>> |
| He⁺ | 2 | <<ehe>> | <<jhe>> |
| Li²⁺ | 3 | <<eli>> | <<jli>> |

Crece como $Z^2$: un núcleo con más carga atrae más al electrón, y además lo acerca ($\langle r\rangle\propto1/Z$).
""", eh=f"{-ry:.2f}", ehe=f"{-4 * ry:.2f}", eli=f"{-9 * ry:.2f}", jh=tex(-ry * E), jhe=tex(-4 * ry * E), jli=tex(-9 * ry * E))
    return Ejercicio(
        "h09_hidrogenoides", "Energía 1s de H, He⁺ y Li²⁺ por sustitución", LIBRO, "Libro (hidrógeno) · ejercicio 9", "hidrogeno",
        "Los iones de un solo electrón, como He⁺, Li²⁺ y Be³⁺, se describen con las funciones de onda del átomo de H cambiando $1/a_0$ por $Z/a_0$, "
        "donde $Z$ es la carga nuclear. La función 1s es $\\psi(r)=\\frac{1}{\\sqrt\\pi}(Z/a_0)^{3/2}e^{-Zr/a_0}$. Usando este resultado, calcula la energía total "
        "del estado 1s del H, el He⁺ y el Li²⁺ sustituyendo en la ecuación de Schrödinger.",
        sol, (Parte("H", "H (en eV)", NUM, -ry, "eV"), Parte("He", "He⁺ (en eV)", NUM, -4 * ry, "eV", confusiones=((0.5, "el factor es $Z^2=4$, no $Z=2$"),)),
              Parte("Li", "Li²⁺ (en eV)", NUM, -9 * ry, "eV", confusiones=((1 / 3, "el factor es $Z^2=9$, no $Z=3$"),))),
        ("Deriva $\\psi$ y sustituye; los términos con $1/r$ deben cancelarse.", "$a_0=4\\pi\\varepsilon_0\\hbar^2/m_ee^2$."), MEDIO,
        nota="En el cuaderno la exponencial aparece como e^(−2r/a₀); la función 1s correcta es e^(−Zr/a₀).")


def _nodos_4dz2() -> Ejercicio:
    t = math.degrees(math.acos(1 / math.sqrt(3)))
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Los nodos **radiales** y **angulares** del orbital $4d_{z^2}$ ($n=4$, $l=2$, $m_l=0$).

#### Paso 2 · Cuántos debe haber
- Nodos totales: $n-1=3$
- Angulares: $l=2$
- Radiales: $n-l-1=4-2-1=1$

#### Paso 3 · La función
$$\psi_{420}=\frac{1}{384\sqrt\pi}\left(\frac1{a_0}\right)^{3/2}\left(\frac{r}{2a_0}\right)^2\left(6-\frac{r}{2a_0}\right)e^{-r/4a_0}\cdot(3\cos^2\theta-1)$$

(con la constante de $Y_2^0$ incluida).

#### Paso 4 · Nodo radial
La exponencial nunca se anula; $\left(\frac r{2a_0}\right)^2$ solo en $r=0$ (que no cuenta como nodo). Queda el paréntesis:

$$6-\frac{r}{2a_0}=0\ \Rightarrow\ \frac{r}{2a_0}=6\ \Rightarrow\ \mathbf{r=12a_0}$$

Es una **esfera** de radio $12a_0\approx635$ pm.

#### Paso 5 · Nodos angulares
$3\cos^2\theta-1=0\Rightarrow\cos\theta=\pm\frac{1}{\sqrt3}$:

$$\theta=\mathbf{<<t1>>^\circ}\quad\text{y}\quad\theta=\mathbf{<<t2>>^\circ}$$

Son **dos conos** con vértice en el núcleo (los mismos de cualquier orbital $d_{z^2}$).

#### Paso 6 · Comprobación
1 esfera + 2 conos = 3 superficies nodales = $n-1$ ✓.
""", t1=f"{t:.2f}", t2=f"{180 - t:.2f}")
    return Ejercicio(
        "h10_4dz2", "Nodos del orbital 4dz²", LIBRO, "Libro (hidrógeno) · ejercicio 10", "hidrogeno",
        "Localiza los nodos angulares y radiales del orbital $4d_{z^2}$, $\\psi_{420}(r,\\theta,\\phi)$.",
        sol, (Parte("r", "Nodo radial (en $a_0$)", NUM, 12.0, "a₀", confusiones=((0.5, "ese es el valor de $r/2a_0$; el nodo está en $r=12a_0$"),)),
              Parte("t", "Menor ángulo nodal (grados)", NUM, t, "°")),
        ("Nodos radiales: $n-l-1$; angulares: $l$.", "El nodo radial sale de $6-r/2a_0=0$."), BASICO)


EJERCICIOS = (_hi(), _conos_l5(), _px_dxz(), _y20_nodos(), _d2(), _ortog_anillo(), _p2_osc(), _ortog_osc(),
              _masas_resorte(), _transicion_osc(), _virial_n0(), _cl2_k(), _x2_osc(), _moneda(), _cm_hf(), _y20_norm(),
              _phi_lz(), _cl2_velocidad(),
              _psi320_negativo(), _potencial_1s(), _prob_1s(), _max_2p(), _hidrogenoides(), _nodos_4dz2())
