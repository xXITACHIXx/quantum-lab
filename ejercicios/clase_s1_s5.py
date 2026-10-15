"""
ejercicios/clase_s1_s5.py — Ejercicios de las diapositivas de las Semanas 1, 2 y 5.
"""

from __future__ import annotations

import math

from scipy import constants as const

from ejercicios._modelo import BASICO, CLASE, MEDIO, NUM, OPC, Ejercicio, Parte, llenar
from talleres._modelo import tex

H, HBAR, C, ME, E, EPS0, U = const.h, const.hbar, const.c, const.m_e, const.e, const.epsilon_0, const.atomic_mass


# ---------------------------------------------------------------------
# Semana 1
# ---------------------------------------------------------------------
def _fotoelectrico() -> Ejercicio:
    lam, phi_ev = 300e-9, 2.26
    phi = phi_ev * E
    e_foton = H * C / lam
    ek = e_foton - phi
    v = math.sqrt(2 * ek / ME)
    sol = llenar(r"""
#### Paso 1 · Qué se pide y qué datos hay
Se ilumina potasio con luz de $\lambda=300$ nm y se pide la **energía cinética** y la **velocidad** de los electrones arrancados. Datos: $\lambda=300\ \text{nm}=300\times10^{-9}$ m y función trabajo $\phi=2.26$ eV.

#### Paso 2 · Idea física (ecuación de Einstein)
Cada fotón entrega **toda** su energía $h\nu$ a un solo electrón. Una parte, $\phi$, se gasta en sacarlo del metal; lo que sobra queda como energía cinética:

$$E_e=h\nu-\phi=\frac{hc}{\lambda}-\phi$$

(se usó $\nu=c/\lambda$). Para restar, **las dos energías deben estar en las mismas unidades**.

#### Paso 3 · Pasar la función trabajo a julios
$1\ \text{eV}=1.602\times10^{-19}$ J, así que

$$\phi=2.26\ \text{eV}\times\frac{1.602\times10^{-19}\ \text{J}}{1\ \text{eV}}=<<phi>>\ \text{J}$$

#### Paso 4 · Energía del fotón
$$\frac{hc}{\lambda}=\frac{(6.626\times10^{-34}\ \text{J s})(2.998\times10^{8}\ \text{m/s})}{300\times10^{-9}\ \text{m}}=<<ef>>\ \text{J}$$

Unidades: (J s)(m/s)/m = J. ✓ Como $<<ef>>\ \text{J}>\phi$, el fotón **sí** puede arrancar electrones (si fuera menor, no saldría ninguno, por intensa que fuera la luz).

#### Paso 5 · Energía cinética
$$E_e=<<ef>>-<<phi>>=\mathbf{<<ek>>\ \text{J}}\quad(\approx<<ekev>>\ \text{eV})$$

#### Paso 6 · Velocidad
De $E_e=\tfrac12m_ev^2$ se despeja $v$:

$$v=\sqrt{\frac{2E_e}{m_e}}=\sqrt{\frac{2\,(<<ek>>\ \text{J})}{9.109\times10^{-31}\ \text{kg}}}=\mathbf{<<v>>\ \text{m/s}}$$

#### Paso 7 · Comprobación
- $v\approx<<vc>>$ % de la velocidad de la luz: no hace falta corrección relativista. ✓
- *Error típico:* restar $\phi$ en eV a $hc/\lambda$ en J; siempre convierte antes de restar.
""", phi=tex(phi), ef=tex(e_foton), ek=tex(ek), ekev=f"{ek / E:.2f}", v=tex(v), vc=f"{100 * v / C:.2f}")
    return Ejercicio(
        "s1_fotoelectrico", "Electrones arrancados del potasio", CLASE, "Semana 1 · Example Problem 1", "fotoelectrico",
        "Luz de longitud de onda **300 nm** incide sobre una superficie de potasio, cuya función trabajo es $\\phi=2.26$ eV. "
        "Calcula la energía cinética y la velocidad de los electrones emitidos.",
        sol,
        (Parte("ek", "Energía cinética de los electrones (en J)", NUM, ek, "J", tol_rel=0.02,
               confusiones=((1 / E, "parece que diste la energía en eV y no en J (1 eV = 1.602×10⁻¹⁹ J)"),)),
         Parte("v", "Velocidad de los electrones (en m/s)", NUM, v, "m/s", tol_rel=0.02)),
        ("Escribe la ecuación de Einstein del efecto fotoeléctrico: la energía del fotón se reparte entre $\\phi$ y la energía cinética.",
         "Pasa $\\phi$ a julios antes de restar, y usa $E=\\tfrac12mv^2$ para la velocidad."),
        BASICO)


def _radio_bohr() -> Ejercicio:
    r = 4 * math.pi * EPS0 * HBAR ** 2 / (ME * E ** 2)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
El **radio de la órbita** del electrón del hidrógeno en el estado de menor energía ($n=1$) según el modelo de Bohr.

#### Paso 2 · La fórmula y de dónde sale
Bohr igualó la fuerza de Coulomb con la fuerza centrípeta y exigió que el momento angular estuviera cuantizado, $m_evr=n\hbar$. Juntando las dos condiciones:

$$r_n=\frac{4\pi\varepsilon_0\hbar^2\,n^2}{m_e e^2}$$

#### Paso 3 · Sustitución, factor por factor
- Numerador: $4\pi\times(8.854\times10^{-12})\times(1.0546\times10^{-34})^2\times1^2=<<num>>$
- Denominador: $(9.109\times10^{-31})\times(1.602\times10^{-19})^2=<<den>>$

$$r_1=\frac{<<num>>}{<<den>>}=\mathbf{<<r>>\ \text{m}}=52.9\ \text{pm}$$

#### Paso 4 · Unidades (comprobación)
$\dfrac{(\text{C}^2\,\text{N}^{-1}\,\text{m}^{-2})(\text{J}^2\,\text{s}^2)}{\text{kg}\cdot\text{C}^2}=\dfrac{\text{J}^2\text{s}^2}{\text{N m}^2\,\text{kg}}$. Como $\text{J}=\text{N m}$ y $\text{N}=\text{kg m s}^{-2}$, todo se reduce a **metros**. ✓

#### Paso 5 · Interpretación
Este valor es el **radio de Bohr**, $a_0$: la unidad natural de longitud en los átomos. Las órbitas siguientes crecen como $n^2$: $r_2=4a_0$, $r_3=9a_0$…
""", num=tex(4 * math.pi * EPS0 * HBAR ** 2), den=tex(ME * E ** 2), r=tex(r))
    return Ejercicio(
        "s1_radio_bohr", "Radio de la primera órbita de Bohr", CLASE, "Semana 1 · Example Problem 2", "bohr",
        "Calcula el radio de la órbita del electrón del átomo de H en su estado de menor energía ($n=1$), según el modelo de Bohr.",
        sol, (Parte("r", "Radio $r_1$ (en m)", NUM, r, "m", confusiones=((1e12, "diste el valor en pm; se pide en metros"),)),),
        ("La fórmula es $r_n=4\\pi\\varepsilon_0\\hbar^2n^2/(m_ee^2)$. Ojo: usa $\\hbar$, no $h$.",), BASICO)


def _electrones_difraccion() -> Ejercicio:
    lam = 0.30e-9
    p = H / lam
    ek = H ** 2 / (2 * ME * lam ** 2)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Para que haya difracción, la longitud de onda de los electrones debe ser parecida a la distancia entre átomos del cristal: $\lambda\approx0.30$ nm. Se pide la **energía** (en J) que deben tener esos electrones.

#### Paso 2 · Idea: De Broglie + energía cinética
- De Broglie: toda partícula con momento $p$ tiene una longitud de onda $\lambda=h/p$, es decir $p=h/\lambda$.
- La energía cinética escrita con el momento: $E=\dfrac{p^2}{2m}$ (porque $E=\tfrac12mv^2$ y $p=mv$).

Juntándolas:

$$E=\frac{p^2}{2m}=\frac{(h/\lambda)^2}{2m}=\frac{h^2}{2m\lambda^2}$$

#### Paso 3 · Sustitución paso a paso
1. $p=\dfrac{h}{\lambda}=\dfrac{6.626\times10^{-34}}{0.30\times10^{-9}}=<<p>>\ \text{kg m/s}$
2. $p^2=<<p2>>$
3. $E=\dfrac{p^2}{2m_e}=\dfrac{<<p2>>}{2\times9.109\times10^{-31}}=\mathbf{<<ek>>\ \text{J}}$

#### Paso 4 · Comprobación
En eV: $E=<<ek>>/1.602\times10^{-19}\approx<<ekev>>$ eV. Son electrones **lentos** (unas decenas de eV), justo los que se usan en la difracción de electrones de baja energía (LEED) para estudiar superficies.
""", p=tex(p), p2=tex(p ** 2), ek=tex(ek), ekev=f"{ek / E:.1f}")
    return Ejercicio(
        "s1_difraccion", "Electrones para estudiar cristales", CLASE, "Semana 1 · Example Problem 3", "de_broglie",
        "Se usan electrones para estudiar la estructura de la superficie de cristales. Para que haya difracción, su longitud de onda $\\lambda$ "
        "debe ser del orden de la constante de red, típicamente **0.30 nm**. ¿Qué energía (en julios) tienen esos electrones?",
        sol, (Parte("E", "Energía de los electrones (en J)", NUM, ek, "J"),),
        ("Combina $\\lambda=h/p$ con $E=p^2/2m$.",), BASICO)


def _fluor_foton() -> Ejercicio:
    lam = 225e-9
    p = H / lam
    m = 2 * 18.998403 * U
    v = p / m
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La velocidad de una molécula de F₂ que tenga **el mismo momento lineal** que un fotón de $\lambda=225$ nm.

#### Paso 2 · Momento del fotón
Aunque el fotón no tiene masa, sí tiene momento. La relación de De Broglie vale para la luz: $p=\dfrac{h}{\lambda}$.

$$p=\frac{6.626\times10^{-34}\ \text{J s}}{225\times10^{-9}\ \text{m}}=<<p>>\ \text{kg m/s}$$

#### Paso 3 · Masa de una molécula de F₂
La masa atómica del flúor es 18.998 u, así que F₂ tiene $2\times18.998=37.997$ u. En kilogramos (1 u = $1.6605\times10^{-27}$ kg):

$$m=37.997\times1.6605\times10^{-27}=<<m>>\ \text{kg}$$

*Ojo:* es la masa de **una** molécula, no la masa molar (38 g/mol). Si usas 0.038 kg el resultado sale $6\times10^{23}$ veces más pequeño.

#### Paso 4 · Velocidad
Para la molécula, $p=mv$, así que

$$v=\frac{p}{m}=\frac{<<p>>}{<<m>>}=\mathbf{<<v>>\ \text{m/s}}$$

#### Paso 5 · Interpretación
¡Unos <<vcm>> cm/s! El momento de un fotón visible o ultravioleta es diminuto: una molécula lo iguala moviéndose muy despacio. (A temperatura ambiente las moléculas de F₂ se mueven a unos 400 m/s.)
""", p=tex(p), m=tex(m), v=tex(v), vcm=f"{100 * v:.1f}")
    return Ejercicio(
        "s1_fluor", "Molécula de F₂ con el momento de un fotón", CLASE, "Semana 1 · Classwork 1", "de_broglie",
        "¿Qué velocidad (en m/s) tiene una molécula de flúor (F₂) si su momento lineal es igual al de un fotón de longitud de onda **225 nm**?",
        sol, (Parte("v", "Velocidad de la molécula de F₂ (en m/s)", NUM, v, "m/s",
                    confusiones=((1 / 6.02214076e23, "usaste la masa molar en kg/mol: necesitas la masa de una molécula (divide entre $N_A$)"),
                                 (2.0, "usaste la masa de un átomo de F, no la de la molécula F₂"))),),
        ("El momento del fotón es $p=h/\\lambda$.", "Para la molécula $p=mv$, con $m$ = masa de **una** molécula en kg."), BASICO)


def _lyman() -> Ejercicio:
    rh = 109677.58  # cm⁻¹
    lam_nm = 1 / (rh * 100) * 1e9
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La **longitud de onda más corta** de la serie de Lyman del hidrógeno.

#### Paso 2 · Qué es la serie de Lyman
Son todas las líneas de emisión en las que el electrón **termina en $n=1$**: $n_i=2,3,4,\dots\to n_f=1$. La fórmula de Rydberg da el número de onda:

$$\tilde\nu=\frac1\lambda=R_H\left(\frac1{n_f^2}-\frac1{n_i^2}\right)\qquad R_H=109\,677\ \text{cm}^{-1}$$

#### Paso 3 · ¿Cuál transición tiene la $\lambda$ más corta?
$\lambda$ más corta $\Leftrightarrow$ $1/\lambda$ más grande $\Leftrightarrow$ el paréntesis más grande. El término $1/n_i^2$ se hace más pequeño a medida que $n_i$ crece, y en el límite $n_i\to\infty$ vale 0. Es el **límite de la serie**: el electrón llega desde muy lejos (casi libre) hasta $n=1$.

$$\frac1\lambda=R_H\left(\frac11-0\right)=R_H$$

#### Paso 4 · Cálculo con unidades
1. $\dfrac1\lambda=109\,677\ \text{cm}^{-1}$
2. $\lambda=\dfrac{1}{109\,677\ \text{cm}^{-1}}=<<lcm>>\ \text{cm}$
3. Pasando a nm ($1\ \text{cm}=10^{7}$ nm): $\lambda=\mathbf{<<lnm>>\ \text{nm}}$

#### Paso 5 · Comprobación
- Las líneas de Lyman están en el **ultravioleta** (121.6 nm la primera, $2\to1$), y todas son más largas que el límite de <<lnm>> nm. ✓
- Con la constante $R_\infty=109\,737\ \text{cm}^{-1}$ (núcleo infinitamente pesado) sale 91.13 nm: la diferencia es la corrección por la masa del protón.
""", lcm=tex(1 / rh), lnm=f"{lam_nm:.2f}")
    return Ejercicio(
        "s1_lyman", "Límite de la serie de Lyman", CLASE, "Semana 1 · Classwork 2", "bohr",
        "Calcula la longitud de onda más corta (en nm) que se observa en la serie de Lyman del hidrógeno.",
        sol, (Parte("lam", "Longitud de onda más corta (en nm)", NUM, lam_nm, "nm", tol_rel=0.01,
                    confusiones=((4 / 3, "ese es el valor de la transición $2\\to1$, la de mayor longitud de onda; la más corta es $\\infty\\to1$"),)),),
        ("En la serie de Lyman el estado final es $n=1$.", "La $\\lambda$ más corta corresponde a la transición con más energía: $n_i\\to\\infty$."),
        BASICO)


# ---------------------------------------------------------------------
# Semana 2
# ---------------------------------------------------------------------
def _onda_viajera() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Comprobar que $\Psi(x,t)=A\sin(kx-\omega t+\phi)$ **satisface** la ecuación de onda no dispersiva

$$\frac{\partial^2\Psi}{\partial x^2}=\frac1{v^2}\frac{\partial^2\Psi}{\partial t^2}$$

«Satisfacer» significa: al calcular el lado izquierdo y el derecho por separado, deben dar **lo mismo**.

#### Paso 2 · Lado izquierdo: derivar dos veces respecto de $x$
Se deriva tratando $t$ como constante (por eso es derivada parcial). Por la regla de la cadena, cada derivada «saca» un factor $k$:

1. $\dfrac{\partial\Psi}{\partial x}=A\cos(kx-\omega t+\phi)\cdot k$
2. $\dfrac{\partial^2\Psi}{\partial x^2}=-A\sin(kx-\omega t+\phi)\cdot k^2=-k^2\,\Psi$

#### Paso 3 · Lado derecho: derivar dos veces respecto de $t$
Ahora $x$ es constante y cada derivada saca un factor $(-\omega)$:

1. $\dfrac{\partial\Psi}{\partial t}=A\cos(kx-\omega t+\phi)\cdot(-\omega)$
2. $\dfrac{\partial^2\Psi}{\partial t^2}=-A\sin(kx-\omega t+\phi)\cdot\omega^2=-\omega^2\,\Psi$

Entonces el lado derecho vale $\dfrac1{v^2}\left(-\omega^2\Psi\right)=-\dfrac{\omega^2}{v^2}\Psi$.

#### Paso 4 · Comparar
Lado izquierdo: $-k^2\Psi$. Lado derecho: $-\dfrac{\omega^2}{v^2}\Psi$. Son iguales si $k^2=\dfrac{\omega^2}{v^2}$, es decir si

$$v=\frac{\omega}{k}$$

Y eso es **justamente** la velocidad de propagación de la onda: $\omega/k=(2\pi\nu)/(2\pi/\lambda)=\lambda\nu$. Por tanto la igualdad se cumple siempre. ✓

#### Paso 5 · Conclusión
La onda viajera es solución de la ecuación de onda para cualquier $A$, $k$, $\omega$ y $\phi$, con tal de que $\omega/k=v$. El signo $-\omega t$ indica que viaja hacia $+x$.
"""
    return Ejercicio(
        "s2_onda_viajera", "La onda viajera cumple la ecuación de onda", CLASE, "Semana 2 · Example Problem 1", "ondas",
        "Demuestra que la onda viajera $\\Psi(x,t)=A\\sin(kx-\\omega t+\\phi)$ es solución de la ecuación de onda no dispersiva "
        "$\\dfrac{\\partial^2\\Psi}{\\partial x^2}=\\dfrac1{v^2}\\dfrac{\\partial^2\\Psi}{\\partial t^2}$.",
        sol, (Parte("cond", "¿Qué condición deben cumplir $k$, $\\omega$ y $v$ para que la igualdad se cumpla?", OPC,
                    opciones=("$v=\\omega/k$", "$v=k/\\omega$", "$v=\\omega k$", "Ninguna: se cumple para cualquier $v$"), correcta=0,
                    explicacion="Las dos derivadas segundas dan $-k^2\\Psi$ y $-(\\omega^2/v^2)\\Psi$: deben ser iguales."),),
        ("Deriva dos veces respecto de $x$ (dejando $t$ fijo) y dos veces respecto de $t$ (dejando $x$ fijo).",), BASICO)


def _complejos() -> Ejercicio:
    a = abs((1 + 1j) * (math.sqrt(2) + 5j))
    b = abs((1 + math.sqrt(3) * 1j) / (11 - 2j))
    c = 0.25
    d = abs((1 + 6j) / 1j)
    sol = llenar(r"""
#### Paso 1 · Las tres reglas que se usan
Para un número complejo $z=a+ib$:

1. **Módulo:** $|z|=\sqrt{a^2+b^2}$ (la distancia al origen en el plano complejo).
2. **Producto y cociente:** $|z_1z_2|=|z_1|\,|z_2|$ y $\left|\dfrac{z_1}{z_2}\right|=\dfrac{|z_1|}{|z_2|}$. No hace falta multiplicar los complejos: basta con multiplicar o dividir los módulos.
3. **Exponencial imaginaria:** $|e^{i\theta}|=1$ para cualquier $\theta$ real, porque $e^{i\theta}=\cos\theta+i\sin\theta$ y $\cos^2\theta+\sin^2\theta=1$.

#### Paso 2 · A) $(1+i)(\sqrt2+5i)$
- $|1+i|=\sqrt{1^2+1^2}=\sqrt2$
- $|\sqrt2+5i|=\sqrt{(\sqrt2)^2+5^2}=\sqrt{2+25}=\sqrt{27}=3\sqrt3$
- Producto: $\sqrt2\cdot3\sqrt3=3\sqrt6=\mathbf{<<a>>}$

#### Paso 3 · B) $\dfrac{1+\sqrt3\,i}{11-2i}$
- Numerador: $|1+\sqrt3i|=\sqrt{1+3}=2$
- Denominador: $|11-2i|=\sqrt{121+4}=\sqrt{125}=5\sqrt5$ (el signo de la parte imaginaria no importa: va al cuadrado)
- Cociente: $\dfrac{2}{5\sqrt5}=\mathbf{<<b>>}$

#### Paso 4 · C) $\dfrac{e^{\sqrt2\,i\pi}\,e^{-3i\pi}}{4e^{i\pi/4}}$
Las tres exponenciales tienen exponente **imaginario puro**, así que cada una tiene módulo 1. Lo único que queda es el 4:

$$\left|\frac{e^{\sqrt2 i\pi}e^{-3i\pi}}{4e^{i\pi/4}}\right|=\frac{1\cdot1}{4\cdot1}=\mathbf{0.25}$$

#### Paso 5 · D) $\dfrac{1+6i}{i}$
- $|1+6i|=\sqrt{1+36}=\sqrt{37}$ y $|i|=1$
- Cociente: $\sqrt{37}=\mathbf{<<d>>}$

*Comprobación alternativa:* $\dfrac{1+6i}{i}=\dfrac{(1+6i)(-i)}{i(-i)}=\dfrac{-i+6}{1}=6-i$, y $|6-i|=\sqrt{36+1}=\sqrt{37}$. ✓
""", a=f"{a:.4f}", b=f"{b:.4f}", d=f"{d:.4f}")
    return Ejercicio(
        "s2_complejos", "Módulo de números complejos", CLASE, "Semana 2 · Example Problem 2", "ondas",
        "Determina el módulo (magnitud) de los siguientes números complejos:\n\n"
        "**A)** $(1+i)(\\sqrt2+5i)$ **B)** $\\dfrac{1+\\sqrt3\\,i}{11-2i}$ **C)** $\\dfrac{e^{\\sqrt2\\,i\\pi}e^{-3i\\pi}}{4e^{i\\pi/4}}$ **D)** $\\dfrac{1+6i}{i}$",
        sol,
        (Parte("A", "A) módulo", NUM, a), Parte("B", "B) módulo", NUM, b), Parte("C", "C) módulo", NUM, c), Parte("D", "D) módulo", NUM, d)),
        ("$|z_1z_2|=|z_1||z_2|$ y $|z_1/z_2|=|z_1|/|z_2|$.", "$|e^{i\\theta}|=1$ para todo $\\theta$ real."), BASICO)


def _autofuncion_ondas() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué significa «autofunción»
$f$ es autofunción de un operador $\hat A$ si al aplicarlo se obtiene **la misma función multiplicada por una constante**: $\hat Af=a\,f$. La constante $a$ es el **autovalor**. Para comprobarlo se aplica el operador y se mira si sale «número × la función original».

#### Paso 2 · Operador $d/dx$
Se deriva término a término ($\frac{d}{dx}e^{ikx}=ik\,e^{ikx}$ y $\frac{d}{dx}e^{-ikx}=-ik\,e^{-ikx}$):

$$\frac{d}{dx}\left(Ae^{ikx}+Be^{-ikx}\right)=ikAe^{ikx}-ikBe^{-ikx}=ik\left(Ae^{ikx}-Be^{-ikx}\right)$$

El paréntesis tiene un **signo menos** que la función original no tiene: no es «constante × $\psi$». **No es autofunción** de $d/dx$ (salvo que $A=0$ o $B=0$).

#### Paso 3 · Operador $d^2/dx^2$
Se deriva una vez más el resultado anterior:

$$\frac{d^2}{dx^2}\psi=ik\left(ikAe^{ikx}+ikBe^{-ikx}\right)=(ik)^2\left(Ae^{ikx}+Be^{-ikx}\right)=-k^2\,\psi$$

(el signo menos se cancela porque $(-ik)(-ik)=(ik)^2$). Sale **la misma función** multiplicada por $-k^2$: **sí es autofunción**, con autovalor $-k^2$.

#### Paso 4 · Interpretación física
- $e^{ikx}$ describe una partícula que va hacia $+x$ y $e^{-ikx}$ una que va hacia $-x$. La suma no tiene un momento definido (no es autofunción de $\hat p_x\propto d/dx$).
- Pero las dos tienen **la misma energía cinética**: $\hat T=-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}$ da $\frac{\hbar^2k^2}{2m}$ para ambas. Por eso la suma sí es autofunción de $d^2/dx^2$.
"""
    return Ejercicio(
        "s2_autofuncion", "¿Autofunción de d/dx y de d²/dx²?", CLASE, "Semana 2 · Example Problem 3", "operadores",
        "Considera los operadores $\\dfrac{d}{dx}$ y $\\dfrac{d^2}{dx^2}$. ¿Es $\\psi(x)=Ae^{ikx}+Be^{-ikx}$ una autofunción de estos operadores? "
        "Si lo es, ¿cuál es el autovalor? ($A$, $B$ y $k$ son reales.)",
        sol,
        (Parte("d1", "¿Es autofunción de $d/dx$ (con $A$ y $B$ distintos de cero)?", OPC,
               opciones=("No", "Sí, con autovalor $ik$", "Sí, con autovalor $-ik$"), correcta=0,
               explicacion="Sale $ik(Ae^{ikx}-Be^{-ikx})$: el signo del segundo término cambia."),
         Parte("d2", "Autovalor de $d^2/dx^2$ (en unidades de $k^2$)", NUM, -1.0, "k²", tol_rel=0.0, tol_abs=0.01)),
        ("Aplica el operador y mira si el resultado es «constante × la función original».", "Recuerda que $i^2=-1$."), BASICO)


def _ortogonales_graf() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué significa ortogonal
Dos funciones son **ortogonales** en un intervalo si la integral de su producto en ese intervalo es cero:

$$\int f(x)\,g(x)\,dx=0$$

Es la versión «para funciones» del producto escalar nulo entre vectores perpendiculares.

#### Paso 2 · La idea gráfica
La integral es el **área con signo** entre la curva $f\cdot g$ y el eje $x$: las zonas por encima cuentan positivo y las de abajo negativo. Si al dibujar $\sin x\cos3x$ las áreas positivas y negativas se compensan exactamente, la integral es cero.

Al graficar $\sin x\cos3x$ se ve que en cada periodo de $2\pi$ hay lóbulos positivos y negativos de **igual tamaño**, colocados de forma simétrica. Sobre $[-2j\pi,2j\pi]$ (muchos periodos completos) todo se cancela.

#### Paso 3 · Confirmación analítica (recomendable)
Con la identidad $\sin a\cos b=\tfrac12\left[\sin(a+b)+\sin(a-b)\right]$:

$$\sin x\cos3x=\tfrac12\left[\sin4x+\sin(-2x)\right]=\tfrac12\left[\sin4x-\sin2x\right]$$

La integral de $\sin(nx)$ sobre un número entero de periodos es cero (tanto $\sin4x$ como $\sin2x$ completan periodos enteros en $[-2j\pi,2j\pi]$):

$$\int_{-2j\pi}^{2j\pi}\sin x\cos3x\,dx=\tfrac12\left[-\frac{\cos4x}{4}+\frac{\cos2x}{2}\right]_{-2j\pi}^{2j\pi}=0$$

porque el coseno toma **el mismo valor** en $2j\pi$ y en $-2j\pi$.

#### Paso 4 · Atajo por simetría
$\sin x$ es **impar** y $\cos3x$ es **par**; el producto impar × par es **impar**, y la integral de una función impar en un intervalo simétrico $[-L,L]$ es cero. ✓

#### Paso 5 · Conclusión
$\sin x$ y $\cos3x$ son ortogonales. Es un caso de un resultado general: senos y cosenos de frecuencias distintas son ortogonales sobre periodos completos, y por eso sirven como base (series de Fourier, y funciones de onda de la caja y del rotor).
"""
    return Ejercicio(
        "s2_ortogonales", "sen x y cos 3x son ortogonales", CLASE, "Semana 2 · Example Problem 4", "operadores",
        "Muestra gráficamente que $\\sin x$ y $\\cos3x$ son funciones ortogonales en el intervalo $[-2j\\pi,2j\\pi]$, donde $j$ es un entero muy grande.",
        sol, (Parte("int", "Valor de $\\displaystyle\\int_{-2j\\pi}^{2j\\pi}\\sin x\\cos3x\\,dx$", NUM, 0.0, tol_rel=0.0, tol_abs=0.01),),
        ("Piensa en la integral como un área con signo.", "$\\sin x$ es impar y $\\cos3x$ es par: ¿qué es el producto?"), BASICO)


def _normalizar_parabola() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Encontrar la constante $N$ que hace que $N\,a(a-x)$ esté **normalizada** en $0\le x\le a$, es decir, que la probabilidad total sea 1:

$$\int_0^a\left|N\,a(a-x)\right|^2dx=1\quad\Rightarrow\quad N^2\int_0^a a^2(a-x)^2\,dx=1$$

#### Paso 2 · Desarrollar el cuadrado
$(a-x)^2=a^2-2ax+x^2$, así que el integrando es $a^2(a^2-2ax+x^2)$:

$$N^2a^2\int_0^a\left(a^2-2ax+x^2\right)dx=1$$

#### Paso 3 · Integrar término a término
| Término | Primitiva | Evaluada en $a$ (en 0 vale 0) |
|---|---|---|
| $a^2$ | $a^2x$ | $a^3$ |
| $-2ax$ | $-ax^2$ | $-a^3$ |
| $x^2$ | $x^3/3$ | $a^3/3$ |

Suma: $a^3-a^3+\dfrac{a^3}{3}=\dfrac{a^3}{3}$.

#### Paso 4 · Despejar $N$
$$N^2a^2\cdot\frac{a^3}{3}=1\ \Rightarrow\ N^2\frac{a^5}{3}=1\ \Rightarrow\ N=\sqrt{\frac{3}{a^5}}$$

#### Paso 5 · Resultado
$$\psi(x)=\sqrt{\frac{3}{a^5}}\;a(a-x)$$

*Comprobación de unidades:* en 1D, $|\psi|^2$ debe tener unidades de 1/longitud. $N^2\sim1/a^5$ y $[a(a-x)]^2\sim a^4$, así que $|\psi|^2\sim1/a$. ✓ Si $a=1$, $N=\sqrt3\approx1.732$.
"""
    return Ejercicio(
        "s2_normalizar", "Normalizar a(a − x)", CLASE, "Semana 2 · Example Problem 5", "operadores",
        "Normaliza la función $a(a-x)$ en el intervalo $0\\le x\\le a$.",
        sol, (Parte("N", "Valor de $N$ cuando $a=1$", NUM, math.sqrt(3), tol_rel=0.01,
                    confusiones=((math.sqrt(3), "olvidaste la raíz: $N^2=3/a^5$, luego $N=\\sqrt3$ para $a=1$"),)),),
        ("Plantea $N^2\\int_0^a[a(a-x)]^2dx=1$.", "Desarrolla $(a-x)^2$ y integra término a término."), BASICO)


def _autofuncion_ddx() -> Ejercicio:
    sol = r"""
#### Paso 1 · Criterio
$f$ es autofunción de $\dfrac{d}{dx}$ si $\dfrac{df}{dx}=(\text{constante})\times f$. La constante **no puede depender de $x$**.

#### Paso 2 · a) $e^{-ix}$
Regla de la cadena: la derivada de $e^{u}$ es $e^{u}\,u'$. Aquí $u=-ix$ y $u'=-i$:

$$\frac{d}{dx}e^{-ix}=-i\,e^{-ix}$$

Es la misma función por la constante $-i$. **Sí es autofunción**, con autovalor $-i$.

#### Paso 3 · b) $e^{-ix^2}$
Ahora $u=-ix^2$ y $u'=-2ix$:

$$\frac{d}{dx}e^{-ix^2}=-2ix\,e^{-ix^2}$$

El factor $-2ix$ **depende de $x$**: no es una constante. **No es autofunción**.

#### Paso 4 · Regla general
Las únicas autofunciones de $d/dx$ son las exponenciales $e^{cx}$ (con $c$ constante, real o compleja), con autovalor $c$. Por eso las ondas planas $e^{ikx}$ son las funciones con momento bien definido, $\hat p_x e^{ikx}=\hbar k\,e^{ikx}$.
"""
    return Ejercicio(
        "s2_cw_autofuncion", "¿Cuáles son autofunciones de d/dx?", CLASE, "Semana 2 · Classwork 1", "operadores",
        "¿Cuáles de las siguientes funciones son autofunciones del operador $\\dfrac{d}{dx}$? **a)** $e^{-ix}$ **b)** $e^{-ix^2}$",
        sol, (Parte("cual", "Respuesta", OPC, opciones=("Solo a)", "Solo b)", "Las dos", "Ninguna"), correcta=0,
                    explicacion="$e^{-ix}\\to-ie^{-ix}$ (constante); $e^{-ix^2}\\to-2ix\\,e^{-ix^2}$ (depende de $x$)."),),
        ("Deriva con la regla de la cadena y mira si el factor que sale depende de $x$.",), BASICO)


def _normalizar_e_r() -> Ejercicio:
    n = 1 / math.sqrt(math.pi)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Hallar $N$ para que $\psi=N\,e^{-r}$ esté normalizada **en todo el espacio** (tres dimensiones), usando coordenadas esféricas.

#### Paso 2 · El elemento de volumen en esféricas
En 3D no se integra solo en $dr$: el pequeño volumen de la figura es un «ladrillo» de lados $dr$, $r\,d\theta$ y $r\sin\theta\,d\phi$:

$$d\tau=r^2\sin\theta\,dr\,d\theta\,d\phi$$

Olvidar el factor $r^2\sin\theta$ es el error más frecuente.

#### Paso 3 · Plantear la condición
$$N^2\int_0^{2\pi}d\phi\int_0^{\pi}\sin\theta\,d\theta\int_0^\infty e^{-2r}\,r^2\,dr=1$$

(el cuadrado de $e^{-r}$ es $e^{-2r}$). Como la función no depende de los ángulos, la integral se **separa** en tres factores.

#### Paso 4 · Calcular cada factor
1. $\displaystyle\int_0^{2\pi}d\phi=2\pi$
2. $\displaystyle\int_0^{\pi}\sin\theta\,d\theta=[-\cos\theta]_0^\pi=-(-1)-(-1)=2$
3. Con la fórmula $\displaystyle\int_0^\infty r^ne^{-br}dr=\frac{n!}{b^{n+1}}$ ($n=2$, $b=2$): $\displaystyle\int_0^\infty r^2e^{-2r}dr=\frac{2!}{2^3}=\frac{2}{8}=\frac14$

Los dos factores angulares juntos dan $4\pi$, el ángulo sólido de una esfera completa.

#### Paso 5 · Despejar $N$
$$N^2\cdot2\pi\cdot2\cdot\frac14=N^2\pi=1\ \Rightarrow\ N=\frac{1}{\sqrt\pi}=\mathbf{<<n>>}$$

#### Paso 6 · Conexión
$\psi=\dfrac{1}{\sqrt\pi}e^{-r}$ es exactamente el orbital $1s$ del hidrógeno con $r$ en unidades de $a_0$: $\psi_{1s}=\dfrac{1}{\sqrt{\pi a_0^3}}e^{-r/a_0}$.
""", n=f"{n:.4f}")
    return Ejercicio(
        "s2_cw_normalizar", "Normalizar e^(−r) en todo el espacio", CLASE, "Semana 2 · Classwork 2", "operadores",
        "Encuentra el valor de $N$ que normaliza la función $e^{-r}$ en $0\\le r\\le\\infty$, $0\\le\\theta\\le\\pi$ y $0\\le\\phi\\le2\\pi$ "
        "(coordenadas esféricas: $x=r\\sin\\theta\\cos\\phi$, $y=r\\sin\\theta\\sin\\phi$, $z=r\\cos\\theta$).",
        sol, (Parte("N", "Valor de $N$", NUM, n, tol_rel=0.01,
                    confusiones=((2 * math.sqrt(math.pi), "olvidaste los factores angulares: integrar en $\\theta$ y $\\phi$ aporta $4\\pi$"),
                                 (1 / math.sqrt(2), "olvidaste el factor $r^2$ del elemento de volumen (sin él la integral radial vale 1/2)"))),),
        ("El elemento de volumen es $d\\tau=r^2\\sin\\theta\\,dr\\,d\\theta\\,d\\phi$.", "$\\int_0^\\infty r^ne^{-br}dr=n!/b^{n+1}$."), MEDIO)


# ---------------------------------------------------------------------
# Semana 5
# ---------------------------------------------------------------------
def _penetracion() -> Ejercicio:
    d = HBAR / math.sqrt(2 * ME * (2.0 - 1.0) * E)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Un electrón con energía $E=1.0$ eV llega a una barrera de altura $V=2.0$ eV. Clásicamente **no puede** entrar (le falta energía). Cuánticamente la función de onda **penetra** en la barrera decayendo exponencialmente: $\psi\propto e^{-\kappa x}$. Se pide la **profundidad de penetración** $1/\kappa$, la distancia en la que la amplitud cae a $1/e\approx37$ % de su valor en el borde.

#### Paso 2 · De dónde sale $\kappa$
Dentro de la barrera la ecuación de Schrödinger es $-\frac{\hbar^2}{2m}\psi''=(E-V)\psi$. Como $V>E$, la solución es $e^{-\kappa x}$ con

$$\kappa=\frac{\sqrt{2m(V-E)}}{\hbar}\qquad\Rightarrow\qquad\frac1\kappa=\frac{\hbar}{\sqrt{2m(V-E)}}$$

#### Paso 3 · Pasar $V-E$ a julios
$V-E=2.0-1.0=1.0$ eV $=1.0\times1.602\times10^{-19}$ J.

#### Paso 4 · Sustitución paso a paso
1. $2m(V-E)=2\times9.109\times10^{-31}\times1.602\times10^{-19}=<<arg>>\ \text{kg J}$
2. $\sqrt{2m(V-E)}=<<raiz>>\ \text{kg m/s}$
3. $\dfrac1\kappa=\dfrac{1.055\times10^{-34}\ \text{J s}}{<<raiz>>\ \text{kg m/s}}=\mathbf{<<d>>\ \text{m}}\approx<<dnm>>\ \text{nm}$

Unidades: J s / (kg m s⁻¹) = (kg m² s⁻¹)/(kg m s⁻¹) = m. ✓

#### Paso 5 · Interpretación
La onda penetra unas décimas de nanómetro, **del orden del tamaño de un átomo**. Por eso la penetración (y el efecto túnel) importa en procesos a escala atómica: superficies, electrodos, el microscopio de efecto túnel. Para un objeto macroscópico $1/\kappa$ sería ridículamente pequeño.
""", arg=tex(2 * ME * E), raiz=tex(math.sqrt(2 * ME * E)), d=tex(d), dnm=f"{d * 1e9:.2f}")
    return Ejercicio(
        "s5_penetracion", "Profundidad de penetración en una barrera", CLASE, "Semana 5 · Example Problem 3", "libre_pared",
        "Un electrón acelerado por una diferencia de potencial de 1.0 V (energía 1.0 eV) incide sobre una barrera de potencial de **2.0 eV**. "
        "Calcula la profundidad de penetración $1/\\kappa$ de su función de onda en la barrera.",
        sol, (Parte("d", "Profundidad de penetración (en nm)", NUM, d * 1e9, "nm", tol_rel=0.03,
                    confusiones=((1 / math.sqrt(2), "usaste $V=2$ eV en lugar de $V-E=1$ eV"), (1e-9, "diste el valor en metros; se pide en nm"))),),
        ("$1/\\kappa=\\hbar/\\sqrt{2m(V-E)}$.", "Convierte $V-E$ de eV a J."), BASICO)


EJERCICIOS = (_fotoelectrico(), _radio_bohr(), _electrones_difraccion(), _fluor_foton(), _lyman(),
              _onda_viajera(), _complejos(), _autofuncion_ondas(), _ortogonales_graf(), _normalizar_parabola(),
              _autofuncion_ddx(), _normalizar_e_r(), _penetracion())
