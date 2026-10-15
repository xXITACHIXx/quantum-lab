"""
ejercicios/cuaderno.py — Ejercicios de clase escritos en el cuaderno que no aparecen en las diapositivas.

(Los del cuaderno que forman los talleres —vibración y rotación del HF, afinidad del Li²⁺, orbitales 3p_z y 3d_z², rotor del H₂,
⟨x⟩ del oscilador, longitud de enlace del HF y determinantes del litio— se practican en «Talleres de repaso».)
"""

from __future__ import annotations

import math

from scipy import constants as const

from ejercicios._modelo import BASICO, CUADERNO, MEDIO, NUM, OPC, Ejercicio, Parte, llenar
from talleres._modelo import tex


def _p_medio() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
El valor medio del momento lineal $\langle p_x\rangle$ de una partícula en una caja de longitud $L$, en cualquier estado $\psi_n=\sqrt{\tfrac2L}\sin\tfrac{n\pi x}{L}$. Es lo que debería devolver el código.

#### Paso 2 · Planteamiento
Valor esperado = $\psi^*$ · operador aplicado a $\psi$, integrado. Con $\hat p_x=-i\hbar\,\dfrac{d}{dx}$ y $\psi$ real ($\psi^*=\psi$):

$$\langle p_x\rangle=\int_0^L\psi_n\left(-i\hbar\frac{d\psi_n}{dx}\right)dx=-i\hbar\int_0^L\psi_n\frac{d\psi_n}{dx}\,dx$$

*Orden de aplicación:* el operador actúa **solo** sobre la $\psi$ de la derecha; no se puede escribir $\frac{d}{dx}\psi^2$ sin más.

#### Paso 3 · Identidad clave: $\psi\,\psi'$ es la derivada de $\tfrac12\psi^2$
Por la regla de la cadena, $\dfrac{d}{dx}\left(\tfrac12\psi^2\right)=\psi\,\dfrac{d\psi}{dx}$. Entonces, por el teorema fundamental del cálculo,

$$\int_0^L\psi_n\frac{d\psi_n}{dx}dx=\left[\tfrac12\psi_n^2\right]_0^L=\tfrac12\left(\psi_n(L)^2-\psi_n(0)^2\right)$$

#### Paso 4 · Evaluar en las paredes
$\psi_n(0)=\sqrt{2/L}\sin0=0$ y $\psi_n(L)=\sqrt{2/L}\sin(n\pi)=0$ para todo $n=1,2,3,\dots$

$$\langle p_x\rangle=-i\hbar\cdot\tfrac12(0-0)=\boxed{0}$$

#### Paso 5 · Interpretación
El código debe devolver **0** (si da un número imaginario o distinto de cero, hay un error de integración). La onda estacionaria $\sin(kx)=\frac{e^{ikx}-e^{-ikx}}{2i}$ es mitad partícula hacia la derecha ($+\hbar k$) y mitad hacia la izquierda ($-\hbar k$): en promedio, momento nulo. Pero $\langle p_x^2\rangle=(n\pi\hbar/L)^2\neq0$: la partícula sí se mueve.
"""
    return Ejercicio(
        "c_p_medio", "Momento medio en la caja", CUADERNO, "Cuaderno · ejercicio de clase", "caja",
        "Se está programando un código para evaluar el valor promedio del momento lineal de una partícula en una caja monodimensional de longitud $L$. "
        "¿Qué valor debe arrojar la salida del código para un estado estacionario $\\psi_n=\\sqrt{2/L}\\sin(n\\pi x/L)$?",
        sol, (Parte("p", "$\\langle p_x\\rangle$ (en unidades de $\\hbar/L$)", NUM, 0.0, "ħ/L", tol_rel=0.0, tol_abs=0.01),),
        ("$\\psi\\,\\psi'=\\frac{d}{dx}\\left(\\frac12\\psi^2\\right)$.", "¿Cuánto vale $\\psi$ en las paredes?"), BASICO)


def _libre_conmutan() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Para una partícula **libre** en el eje $x$, decidir si la energía total y el momento lineal se pueden conocer a la vez, es decir, si $[\hat H,\hat p_x]=0$ actuando sobre una función arbitraria $f(x)$.

#### Paso 2 · Los operadores
Partícula libre: $V=0$, así que toda la energía es cinética.

$$\hat H=-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}\qquad\hat p_x=-i\hbar\frac{d}{dx}$$

#### Paso 3 · $\hat H(\hat p_xf)$
$$\hat H\left(-i\hbar f'\right)=-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}\left(-i\hbar f'\right)=\frac{i\hbar^3}{2m}f'''$$

#### Paso 4 · $\hat p_x(\hat Hf)$
$$\hat p_x\left(-\frac{\hbar^2}{2m}f''\right)=-i\hbar\frac{d}{dx}\left(-\frac{\hbar^2}{2m}f''\right)=\frac{i\hbar^3}{2m}f'''$$

#### Paso 5 · Restar
$$[\hat H,\hat p_x]f=\frac{i\hbar^3}{2m}f'''-\frac{i\hbar^3}{2m}f'''=0$$

**Sí conmutan**: se pueden determinar simultáneamente.

#### Paso 6 · Comprobación con la onda plana $\psi=Ae^{ikx}$
- $\hat p_x\psi=-i\hbar(ik)\psi=\hbar k\,\psi$ → momento definido $\hbar k$.
- $\hat H\psi=-\frac{\hbar^2}{2m}(ik)^2\psi=\frac{\hbar^2k^2}{2m}\psi$ → energía definida $\frac{\hbar^2k^2}{2m}=\frac{p^2}{2m}$.

Es autofunción **de los dos a la vez**, como tiene que pasar cuando los operadores conmutan.

*Precisión en el cálculo:* $(ik)^2=-k^2$, no $k^2$, y al aplicar $\hat H$ no aparece $\hbar^3k^3$: ese término solo aparece al aplicar los **dos** operadores seguidos ($\hat H\hat p_x\psi=\frac{\hbar^3k^3}{2m}\psi$, y lo mismo $\hat p_x\hat H\psi$).
"""
    return Ejercicio(
        "c_libre", "Energía y momento de la partícula libre", CUADERNO, "Cuaderno · ejercicio de clase", "conmutadores",
        "Para evaluar el movimiento de una partícula libre que viaja en el eje $x$ se calculan su energía total y su momento lineal. "
        "Determinar si estos dos observables se pueden determinar simultáneamente para una función de onda arbitraria $f(x)$. "
        "Comprobar el resultado con la onda plana $\\psi=Ae^{ikx}$.",
        sol, (Parte("c", "¿Se pueden conocer simultáneamente?", OPC, opciones=("Sí, $[\\hat H,\\hat p_x]=0$", "No, $[\\hat H,\\hat p_x]=i\\hbar$"),
                    correcta=0, explicacion="Ambos órdenes dan $\\frac{i\\hbar^3}{2m}f'''$."),
              Parte("E", "Energía de $Ae^{ikx}$ en unidades de $\\hbar^2k^2/m$", NUM, 0.5, "ħ²k²/m")),
        ("Para la partícula libre $\\hat H$ solo tiene la energía cinética.",), BASICO)


def _caja2d() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Partícula en una caja **cuadrada** de lado $L$ en el estado $(n_x,n_y)=(1,2)$:

$$\psi_{12}(x,y)=\frac2L\sin\frac{\pi x}{L}\sin\frac{2\pi y}{L}\qquad E_{n_xn_y}=\frac{h^2}{8mL^2}\left(n_x^2+n_y^2\right)$$

**a)** estados degenerados; **b)** posición de los nodos; **c)** máximos de la densidad de probabilidad.

#### Paso 2 · a) Energía y degeneración
$$E_{12}=\frac{h^2}{8mL^2}(1^2+2^2)=\frac{5h^2}{8mL^2}$$

Como la caja es cuadrada, intercambiar $n_x$ y $n_y$ da la **misma** suma de cuadrados:

$$E_{21}=\frac{h^2}{8mL^2}(2^2+1^2)=\frac{5h^2}{8mL^2}$$

No hay otra pareja de enteros positivos con $n_x^2+n_y^2=5$. El nivel es **doblemente degenerado**: $\psi_{12}$ y $\psi_{21}$. (Si la caja fuera rectangular, $a\ne b$, la degeneración desaparecería.)

#### Paso 3 · b) Nodos
$\psi=0$ cuando se anula alguno de los dos senos (sin contar las paredes, donde siempre vale cero):

- $\sin\frac{\pi x}{L}=0$ solo en $x=0$ y $x=L$ (paredes): ningún nodo interior en $x$.
- $\sin\frac{2\pi y}{L}=0$ en $\frac{2\pi y}{L}=0,\pi,2\pi$, o sea $y=0,\ \mathbf{L/2},\ L$.

Hay una **línea nodal** horizontal en $y=L/2$, que cruza toda la caja. (En 2D los nodos son líneas, no puntos.) Regla: $n_x-1=0$ líneas verticales y $n_y-1=1$ horizontal.

#### Paso 4 · c) Máximos de $|\psi|^2$
$$|\psi_{12}|^2=\frac4{L^2}\sin^2\frac{\pi x}L\,\sin^2\frac{2\pi y}L$$

Cada $\sin^2$ alcanza su máximo (1) cuando su argumento es $\pi/2$ más un múltiplo de $\pi$:

- $\frac{\pi x}{L}=\frac\pi2\Rightarrow x=\frac L2$
- $\frac{2\pi y}{L}=\frac\pi2,\frac{3\pi}2\Rightarrow y=\frac L4,\ \frac{3L}4$

**Dos máximos**: en $\left(\frac L2,\frac L4\right)$ y en $\left(\frac L2,\frac{3L}4\right)$, uno a cada lado de la línea nodal, con valor $\frac{4}{L^2}$.

#### Paso 5 · Imagen mental
Dos «montañas» iguales apiladas en la dirección $y$, separadas por el valle (nodo) de $y=L/2$. El estado $\psi_{21}$ es la misma imagen girada 90°.
"""
    return Ejercicio(
        "c_caja2d", "Caja cuadrada en el estado (1, 2)", CUADERNO, "Cuaderno · ejercicio de clase", "caja",
        "Para una partícula en una caja bidimensional cuadrada de lado $L$ en el estado $(n_x=1,\\ n_y=2)$, identifica: "
        "**a)** los estados degenerados; **b)** la posición de los nodos; **c)** los máximos de la densidad de probabilidad. "
        "$\\psi(x,y)=\\frac2L\\sin\\frac{n_x\\pi x}{L}\\sin\\frac{n_y\\pi y}{L}$.",
        sol, (Parte("E", "a) Energía en unidades de $h^2/8mL^2$", NUM, 5.0, "h²/8mL²"),
              Parte("g", "a) Degeneración del nivel", NUM, 2.0, tol_rel=0.0, tol_abs=0.1),
              Parte("nodo", "b) Nodo interior", OPC, opciones=("La recta $y=L/2$", "La recta $x=L/2$", "El punto $(L/2,L/2)$", "No tiene nodos interiores"),
                    correcta=0, explicacion="$\\sin(2\\pi y/L)=0$ en $y=L/2$."),
              Parte("ymax", "c) Coordenada $y$ del máximo inferior (en unidades de $L$)", NUM, 0.25, "L")),
        ("$E\\propto n_x^2+n_y^2$: ¿qué otra pareja da 5?", "Buscar dónde cada seno vale 0 y dónde vale ±1."), BASICO)


def _hf_caja() -> Ejercicio:
    h, me = const.h, const.m_e
    nu = 3.0e13
    L = math.sqrt(3 * h / (8 * me * nu))
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Se modelan los electrones del enlace como una **partícula en una caja** de longitud $L$ (la longitud del enlace). La transición de menor energía, $n=1\to2$, tiene frecuencia $\nu=3.0\times10^{13}\ \text{s}^{-1}$. Se pide $L$.

#### Paso 2 · Energía de la transición
$E_n=\dfrac{n^2h^2}{8m_eL^2}$, así que

$$\Delta E=E_2-E_1=\frac{h^2}{8m_eL^2}(2^2-1^2)=\frac{3h^2}{8m_eL^2}$$

#### Paso 3 · Igualar con la energía del fotón
El fotón absorbido tiene $\Delta E=h\nu$:

$$h\nu=\frac{3h^2}{8m_eL^2}\ \Rightarrow\ \nu=\frac{3h}{8m_eL^2}\ \Rightarrow\ L^2=\frac{3h}{8m_e\nu}\ \Rightarrow\ L=\sqrt{\frac{3h}{8m_e\nu}}$$

(una $h$ se cancela). La partícula es un **electrón**: $m_e=9.109\times10^{-31}$ kg.

#### Paso 4 · Sustitución paso a paso
1. Numerador: $3h=3\times6.626\times10^{-34}=<<num>>\ \text{J s}$
2. Denominador: $8m_e\nu=8\times9.109\times10^{-31}\times3.0\times10^{13}=<<den>>\ \text{kg s}^{-1}$
3. $L^2=<<l2>>\ \text{m}^2$
4. $L=\mathbf{<<L>>\ \text{m}}\approx<<Lnm>>$ nm

Unidades: J s/(kg s⁻¹) = (kg m² s⁻²)(s)(s)/kg = m². ✓

#### Paso 5 · Comentario crítico
El resultado es unas 30 veces mayor que el enlace real del HF (91.7 pm). La frecuencia dada ($3\times10^{13}$ Hz, infrarrojo) es típica de **vibraciones**, no de transiciones electrónicas (que están en el visible o el UV, $\sim10^{15}$ Hz). Con una frecuencia electrónica realista la caja saldría del tamaño de un enlace. El ejercicio sirve para practicar el modelo, no como descripción fiel del HF.
""", num=tex(3 * h), den=tex(8 * me * nu), l2=tex(L ** 2), L=tex(L), Lnm=f"{L * 1e9:.2f}")
    return Ejercicio(
        "c_hf_caja", "Longitud de una «caja» a partir de una transición", CUADERNO, "Cuaderno · ejercicio de clase", "caja",
        "En un laboratorio se encontró que la frecuencia de la transición de menor energía entre estados electrónicos del HF es $3.0\\times10^{13}\\ \\text{s}^{-1}$. "
        "Con el modelo de la partícula en una caja monodimensional (transición $n=1\\to2$), determina la longitud del enlace suponiendo que es igual a la longitud de la caja.",
        sol, (Parte("L", "Longitud de la caja (en nm)", NUM, L * 1e9, "nm", tol_rel=0.02,
                    confusiones=((1e-9, "valor expresado en metros; se solicita en nm"), (1 / math.sqrt(3), "se empleó $\\Delta E=h^2/8mL^2$; para $1\\to2$ es $3h^2/8mL^2$"))),),
        ("$\\Delta E=E_2-E_1=3h^2/8mL^2$.", "La partícula es un electrón."), BASICO)


EJERCICIOS = (_p_medio(), _libre_conmutan(), _caja2d(), _hf_caja())
