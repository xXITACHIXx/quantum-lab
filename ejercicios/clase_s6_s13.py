"""
ejercicios/clase_s6_s13.py — Ejercicios de las diapositivas de las Semanas 6, 7, 9, 10, 11 y 13.
"""

from __future__ import annotations

import math

from ejercicios._modelo import AVANZADO, BASICO, CLASE, MEDIO, NUM, OPC, Ejercicio, Parte, llenar


# ---------------------------------------------------------------------
# Semana 6 · Partícula en una caja
# ---------------------------------------------------------------------
def _espaciado() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Los niveles de la caja son $E_n=\dfrac{h^2n^2}{8ma^2}$. La separación entre niveles vecinos **crece** con $n$, y eso parece contradecir que a energías altas el espectro debería verse continuo (como en la física clásica). Se pide formar el cociente $\dfrac{E_{n+1}-E_n}{E_n}$ y ver qué pasa cuando $n\to\infty$.

#### Paso 2 · La diferencia entre niveles vecinos
$$E_{n+1}-E_n=\frac{h^2}{8ma^2}\left[(n+1)^2-n^2\right]$$

Se desarrolla el corchete: $(n+1)^2-n^2=n^2+2n+1-n^2=2n+1$. Entonces

$$E_{n+1}-E_n=\frac{h^2}{8ma^2}(2n+1)$$

#### Paso 3 · Dividir entre $E_n$
El factor $\dfrac{h^2}{8ma^2}$ aparece arriba y abajo y se **cancela**:

$$\frac{E_{n+1}-E_n}{E_n}=\frac{\frac{h^2}{8ma^2}(2n+1)}{\frac{h^2}{8ma^2}n^2}=\frac{2n+1}{n^2}$$

#### Paso 4 · Evaluar para varios $n$
| $n$ | $\dfrac{2n+1}{n^2}$ |
|---|---|
| 1 | 3 (el siguiente nivel está al **300 %** de distancia) |
| 10 | 0.21 |
| 100 | 0.0201 |
| 1000 | 0.002 |

Para $n$ grande, $\dfrac{2n+1}{n^2}\approx\dfrac{2}{n}\to0$.

#### Paso 5 · Interpretación (principio de correspondencia)
La separación sí crece (como $n$), pero la energía crece **más rápido** (como $n^2$). Medida **en proporción** a la energía, la separación se vuelve despreciable: el espectro parece continuo y se recupera el resultado clásico. Es un ejemplo del **principio de correspondencia**.
"""
    return Ejercicio(
        "s6_espaciado", "El espectro de la caja se vuelve continuo", CLASE, "Semana 6 · Example Problem 1", "caja",
        "Para la partícula en una caja, $E_n=h^2n^2/8ma^2$ ($n=1,2,3,\\dots$): la separación entre niveles vecinos aumenta con $n$. "
        "Forma el cociente $\\dfrac{E_{n+1}-E_n}{E_n}$ y muestra que se hace cada vez más pequeño cuando $n\\to\\infty$.",
        sol, (Parte("r1", "Valor del cociente para $n=1$", NUM, 3.0), Parte("r100", "Valor del cociente para $n=100$", NUM, 201 / 10000)),
        ("Desarrolla $(n+1)^2-n^2$.", "El factor $h^2/8ma^2$ se cancela."), BASICO)


def _superposicion() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Para $\psi(x)=c\sin\dfrac{\pi x}{a}+d\sin\dfrac{2\pi x}{a}$ (mezcla de los estados $n=1$ y $n=2$ de la caja): **a)** ¿es una función de onda aceptable? **b)** ¿es autofunción del hamiltoniano $\hat H$?

#### Paso 2 · a) Condiciones de una función aceptable
Una función de onda de la caja debe: (1) anularse en las paredes, $\psi(0)=\psi(a)=0$, porque fuera de la caja la partícula no puede estar; (2) ser continua y con derivadas bien comportadas; (3) ser normalizable.

- En $x=0$: $\sin0=0$ en ambos términos → $\psi(0)=0$ ✓
- En $x=a$: $\sin\pi=0$ y $\sin2\pi=0$ → $\psi(a)=0$ ✓
- Senos: continuos y derivables; la integral de $|\psi|^2$ en $[0,a]$ es finita ✓

**Sí es aceptable.**

#### Paso 3 · b) Aplicar el hamiltoniano
Dentro de la caja $V=0$, así que $\hat H=-\dfrac{\hbar^2}{2m}\dfrac{d^2}{dx^2}$. Al derivar dos veces, $\sin(kx)\to-k^2\sin(kx)$:

- $\dfrac{d^2}{dx^2}\sin\dfrac{\pi x}{a}=-\dfrac{\pi^2}{a^2}\sin\dfrac{\pi x}{a}$
- $\dfrac{d^2}{dx^2}\sin\dfrac{2\pi x}{a}=-\dfrac{4\pi^2}{a^2}\sin\dfrac{2\pi x}{a}$

$$\hat H\psi=\frac{\hbar^2\pi^2}{2ma^2}\left(c\sin\frac{\pi x}{a}+\mathbf 4\,d\sin\frac{2\pi x}{a}\right)$$

#### Paso 4 · ¿Es «constante × ψ»?
Dentro del paréntesis el segundo término lleva un **4** que el primero no tiene. No se puede sacar un único número que multiplique a toda $\psi$: **no es autofunción** de $\hat H$ (salvo que $c=0$ o $d=0$).

#### Paso 5 · Interpretación
$\psi$ es un estado válido, pero **sin energía definida**: si se mide la energía se obtiene $E_1$ (con probabilidad $\propto|c|^2$) o $E_2=4E_1$ (probabilidad $\propto|d|^2$). Es la idea de **superposición**.
"""
    return Ejercicio(
        "s6_superposicion", "Superposición de dos estados de la caja", CLASE, "Semana 6 · Example Problem 2", "caja",
        "Considera la función de onda $\\psi(x)=c\\sin(\\pi x/a)+d\\sin(2\\pi x/a)$ para la partícula en una caja de longitud $a$.\n\n"
        "**a)** ¿Es una función de onda aceptable? **b)** ¿Es autofunción del operador de energía total $\\hat H$?",
        sol,
        (Parte("a", "a) ¿Es aceptable?", OPC, opciones=("Sí", "No"), correcta=0, explicacion="Se anula en $x=0$ y $x=a$ y es continua y normalizable."),
         Parte("b", "b) ¿Es autofunción de $\\hat H$?", OPC, opciones=("No", "Sí, con energía $E_1+E_2$", "Sí, con energía $E_1$"), correcta=0,
               explicacion="$\\hat H$ multiplica el término $n=2$ por un factor 4 veces mayor que el del término $n=1$.")),
        ("Comprueba qué pasa en $x=0$ y $x=a$.", "Aplica $-\\frac{\\hbar^2}{2m}\\frac{d^2}{dx^2}$ a cada seno por separado."), BASICO)


def _prob_tercio() -> Ejercicio:
    p = 1 / 3 + math.sqrt(3) / (2 * math.pi)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La probabilidad de encontrar la partícula, en su estado fundamental, en el **tercio central** de la caja: entre $x=a/3$ y $x=2a/3$.

#### Paso 2 · Idea (postulado de Born)
$|\psi(x)|^2dx$ es la probabilidad de hallar la partícula entre $x$ y $x+dx$. Para un intervalo se **suman** todas esas probabilidades, es decir, se integra:

$$P=\int_{a/3}^{2a/3}|\psi_1|^2dx=\frac2a\int_{a/3}^{2a/3}\sin^2\frac{\pi x}{a}\,dx\qquad\left(\psi_1=\sqrt{\tfrac2a}\sin\tfrac{\pi x}{a}\right)$$

#### Paso 3 · La integral de $\sin^2$
Con la identidad $\sin^2u=\tfrac12(1-\cos2u)$:

$$\int\sin^2(bx)\,dx=\frac x2-\frac{\sin(2bx)}{4b}\qquad(b=\pi/a)$$

#### Paso 4 · Evaluar en los límites
$$P=\frac2a\left[\frac x2-\frac{a}{4\pi}\sin\frac{2\pi x}{a}\right]_{a/3}^{2a/3}$$

- Parte $\dfrac x2$: $\dfrac{2a/3-a/3}{2}=\dfrac a6$
- Parte del seno: $-\dfrac a{4\pi}\left[\sin\dfrac{4\pi}{3}-\sin\dfrac{2\pi}{3}\right]=-\dfrac a{4\pi}\left[-\dfrac{\sqrt3}2-\dfrac{\sqrt3}2\right]=+\dfrac{\sqrt3\,a}{4\pi}$

$$P=\frac2a\left(\frac a6+\frac{\sqrt3\,a}{4\pi}\right)=\frac13+\frac{\sqrt3}{2\pi}=0.3333+0.2757=\mathbf{<<p>>}$$

(la $a$ se cancela: el resultado no depende del tamaño de la caja).

#### Paso 5 · Interpretación
Clásicamente la partícula pasaría el mismo tiempo en cada tercio: $P=1/3$. Cuánticamente, en el estado fundamental la densidad es máxima en el centro, por eso $P\approx61$ % es mayor que 33 %. No se puede predecir una medición individual, pero en muchas mediciones el 60.9 % caerá en el tercio central.
""", p=f"{p:.3f}")
    return Ejercicio(
        "s6_prob_tercio", "Probabilidad en el tercio central de la caja", CLASE, "Semana 6 · Example Problem 3", "caja",
        "¿Cuál es la probabilidad $P$ de encontrar la partícula en el **tercio central** de la caja ($a/3\\le x\\le2a/3$) si está en su estado fundamental?",
        sol, (Parte("P", "Probabilidad $P$", NUM, p, tol_rel=0.01, confusiones=((1 / 3 / p, "1/3 sería el resultado clásico; la densidad cuántica no es uniforme"),)),),
        ("$P=\\int|\\psi|^2dx$ entre $a/3$ y $2a/3$.", "Usa $\\sin^2u=\\tfrac12(1-\\cos2u)$."), MEDIO)


def _x_medio_caja() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Para $\psi=\sqrt{2/a}\,\sin(\pi x/a)$: **a)** ¿es autofunción del operador de posición $\hat x$? **b)** el valor medio $\langle x\rangle$ de muchas mediciones.

#### Paso 2 · a) Operador de posición
El operador posición simplemente **multiplica por $x$**: $\hat x\psi=x\,\psi(x)$. Para ser autofunción tendría que dar «constante × ψ», pero da $x\cdot\psi$, y $x$ **no es constante**. **No es autofunción**: la posición de la partícula no está definida en este estado.

#### Paso 3 · b) Valor esperado
$$\langle x\rangle=\int_0^a\psi^*\,x\,\psi\,dx=\frac2a\int_0^a x\sin^2\frac{\pi x}{a}\,dx$$

Integral de tabla (con $b=\pi/a$):

$$\int x\sin^2(bx)dx=\frac{x^2}{4}-\frac{x\sin(2bx)}{4b}-\frac{\cos(2bx)}{8b^2}$$

#### Paso 4 · Evaluar
- $\dfrac{x^2}{4}$: de 0 a $a$ da $\dfrac{a^2}{4}$.
- $\dfrac{x\sin(2\pi x/a)}{4b}$: vale 0 en ambos límites ($\sin2\pi=\sin0=0$).
- $\dfrac{\cos(2\pi x/a)}{8b^2}$: vale lo mismo en 0 y en $a$ ($\cos0=\cos2\pi=1$), así que su diferencia es 0.

$$\langle x\rangle=\frac2a\cdot\frac{a^2}{4}=\boxed{\frac a2}$$

#### Paso 5 · Atajo por simetría
$|\psi_1|^2$ es **simétrica** respecto al centro de la caja: hay la misma probabilidad a la izquierda y a la derecha de $a/2$, así que el promedio tiene que ser $a/2$. (Vale para **todos** los estados $n$ de la caja.)
"""
    return Ejercicio(
        "s6_x_medio", "Posición media en la caja", CLASE, "Semana 6 · Example Problem 4", "caja",
        "Una partícula está en una caja de longitud $a$ con $\\psi(x)=\\sqrt{2/a}\\,\\sin(\\pi x/a)$.\n\n"
        "**a)** ¿Es este estado una autofunción del operador de posición $\\hat x$? **b)** Calcula el valor medio $\\langle x\\rangle$ de un gran número de mediciones.",
        sol,
        (Parte("a", "a) ¿Es autofunción de $\\hat x$?", OPC, opciones=("No", "Sí"), correcta=0, explicacion="$\\hat x\\psi=x\\psi$ y $x$ no es constante."),
         Parte("x", "b) $\\langle x\\rangle$ en unidades de $a$", NUM, 0.5, "a")),
        ("$\\hat x$ multiplica por $x$.", "Piensa en la simetría de $|\\psi|^2$ respecto a $x=a/2$."), BASICO)


# ---------------------------------------------------------------------
# Semana 7 · Conmutadores e incertidumbre
# ---------------------------------------------------------------------
def _p_t_conmutan() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Saber si el **momento** $\hat p_x$ y la **energía cinética** $\hat T$ se pueden conocer a la vez con exactitud. Eso ocurre si sus operadores **conmutan**: $[\hat p_x,\hat T]=\hat p_x\hat T-\hat T\hat p_x=0$.

#### Paso 2 · Los operadores
$$\hat p_x=-i\hbar\frac{d}{dx}\qquad\hat T=-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}$$

#### Paso 3 · Aplicar el conmutador a una función cualquiera $f(x)$
Un conmutador se calcula **siempre** sobre una función de prueba, para no perder términos.

- $\hat p_x\hat Tf=-i\hbar\dfrac{d}{dx}\left(-\dfrac{\hbar^2}{2m}\dfrac{d^2f}{dx^2}\right)=\dfrac{i\hbar^3}{2m}\dfrac{d^3f}{dx^3}$
- $\hat T\hat p_xf=-\dfrac{\hbar^2}{2m}\dfrac{d^2}{dx^2}\left(-i\hbar\dfrac{df}{dx}\right)=\dfrac{i\hbar^3}{2m}\dfrac{d^3f}{dx^3}$

#### Paso 4 · Restar
$$[\hat p_x,\hat T]f=\frac{i\hbar^3}{2m}f'''-\frac{i\hbar^3}{2m}f'''=0$$

Da igual derivar primero una vez y luego dos, o al revés: en ambos casos se deriva tres veces. Las constantes salen fuera sin problema.

#### Paso 5 · Conclusión
$[\hat p_x,\hat T]=0$: **sí se pueden conocer simultáneamente y con exactitud**. Tiene sentido: $T=p^2/2m$ es función de $p$, y un operador siempre conmuta con funciones de sí mismo.
"""
    return Ejercicio(
        "s7_p_t", "¿Momento y energía cinética a la vez?", CLASE, "Semana 7 · Example Problem 1", "conmutadores",
        "Determina si el momento lineal $\\hat p_x$ y la energía cinética $\\hat T$ se pueden conocer simultáneamente con exactitud.",
        sol, (Parte("c", "¿Conmutan?", OPC, opciones=("Sí: $[\\hat p_x,\\hat T]=0$", "No: $[\\hat p_x,\\hat T]=i\\hbar$"), correcta=0,
                    explicacion="Ambos productos dan $\\frac{i\\hbar^3}{2m}f'''$."),),
        ("Calcula $\\hat p_x(\\hat Tf)$ y $\\hat T(\\hat p_xf)$ sobre una función $f(x)$ cualquiera.",), BASICO)


def _x_p() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Demostrar que la posición $\hat x$ y el momento $\hat p_x$ **no conmutan**, y hallar su conmutador.

#### Paso 2 · Plantear sobre una función de prueba $f(x)$
$$[\hat x,\hat p_x]f=\hat x(\hat p_xf)-\hat p_x(\hat xf)\qquad\hat x=x,\quad\hat p_x=\frac{\hbar}{i}\frac{d}{dx}$$

#### Paso 3 · Primer término
$$\hat x(\hat p_xf)=x\cdot\frac\hbar i\frac{df}{dx}$$

#### Paso 4 · Segundo término (aquí está la clave: **regla del producto**)
$\hat p_x$ deriva el producto $x\,f$:

$$\hat p_x(xf)=\frac\hbar i\frac{d(xf)}{dx}=\frac\hbar i\left(\frac{dx}{dx}f+x\frac{df}{dx}\right)=\frac\hbar i\left(f+x\frac{df}{dx}\right)$$

#### Paso 5 · Restar
$$[\hat x,\hat p_x]f=\frac\hbar i\,x\frac{df}{dx}-\frac\hbar i f-\frac\hbar i\,x\frac{df}{dx}=-\frac\hbar i f$$

Como $\dfrac1i=-i$: $-\dfrac\hbar i=i\hbar$. Entonces

$$[\hat x,\hat p_x]f=i\hbar\,f\quad\Rightarrow\quad\boxed{[\hat x,\hat p_x]=i\hbar}$$

#### Paso 6 · Interpretación
No es cero: posición y momento son **observables complementarios**. De aquí sale el principio de incertidumbre $\Delta x\,\Delta p_x\ge\frac12|\langle[\hat x,\hat p_x]\rangle|=\frac\hbar2$. En cambio, $x$, $y$, $z$ conmutan entre sí, y también $p_x$, $p_y$, $p_z$.

*Error típico:* olvidar la regla del producto en el paso 4; entonces todo se cancela y sale (mal) que conmutan.
"""
    return Ejercicio(
        "s7_x_p", "Posición y momento no conmutan", CLASE, "Semana 7 · Example Problem 2", "conmutadores",
        "Demuestra que $\\hat x$ y $\\hat p_x$ no conmutan, de modo que estos dos observables no se pueden especificar simultáneamente. ¿Cuánto vale $[\\hat x,\\hat p_x]$?",
        sol, (Parte("c", "$[\\hat x,\\hat p_x]=$", OPC, opciones=("$i\\hbar$", "$-i\\hbar$", "$0$", "$\\hbar/2$"), correcta=0,
                    explicacion="La regla del producto deja un término $-\\frac\\hbar if=i\\hbar f$."),),
        ("Aplica el conmutador a una función de prueba $f(x)$.", "Al derivar $x f$ usa la regla del producto."), BASICO)


def _dxdp() -> Ejercicio:
    prod = math.sqrt((math.pi ** 2 - 6) / 12)
    sol = llenar(r"""
#### Paso 1 · Qué se pide y receta
$\Delta x\,\Delta p_x$ para el estado fundamental de la caja, $\psi=\sqrt{2/L}\sin(\pi x/L)$. Las incertidumbres son desviaciones estándar:

$$\Delta x=\sqrt{\langle x^2\rangle-\langle x\rangle^2}\qquad\Delta p_x=\sqrt{\langle p_x^2\rangle-\langle p_x\rangle^2}$$

Hacen falta **cuatro** valores esperados.

#### Paso 2 · $\langle x\rangle$
Por simetría de $|\psi|^2$ respecto al centro: $\langle x\rangle=\dfrac L2$.

#### Paso 3 · $\langle x^2\rangle$
$$\langle x^2\rangle=\frac2L\int_0^Lx^2\sin^2\frac{\pi x}{L}dx=L^2\left(\frac13-\frac1{2\pi^2}\right)=\frac{L^2}{6\pi^2}(2\pi^2-3)$$

(integral de tabla; se puede comprobar numéricamente: para $L=1$ vale 0.2827).

#### Paso 4 · $\Delta x$
$$\Delta x^2=L^2\left(\frac13-\frac1{2\pi^2}\right)-\frac{L^2}{4}=L^2\left(\frac1{12}-\frac1{2\pi^2}\right)\ \Rightarrow\ \Delta x=<<dx>>\,L$$

#### Paso 5 · $\langle p_x\rangle$ y $\langle p_x^2\rangle$
- $\langle p_x\rangle=0$: la onda estacionaria es mitad «hacia la derecha» y mitad «hacia la izquierda».
- $\hat p_x^2=-\hbar^2\dfrac{d^2}{dx^2}$, y $\dfrac{d^2}{dx^2}\sin\dfrac{\pi x}L=-\dfrac{\pi^2}{L^2}\sin\dfrac{\pi x}{L}$, así que $\hat p_x^2\psi=\dfrac{\pi^2\hbar^2}{L^2}\psi$ y $\langle p_x^2\rangle=\dfrac{\pi^2\hbar^2}{L^2}$ (como $\psi$ está normalizada, la integral restante vale 1).

$$\Delta p_x=\sqrt{\frac{\pi^2\hbar^2}{L^2}-0}=\frac{\pi\hbar}{L}$$

#### Paso 6 · El producto
$$\Delta x\,\Delta p_x=L\sqrt{\frac1{12}-\frac1{2\pi^2}}\cdot\frac{\pi\hbar}{L}=\hbar\sqrt{\frac{\pi^2}{12}-\frac12}=\hbar\sqrt{\frac{\pi^2-6}{12}}=\mathbf{<<p>>\,\hbar}$$

La $L$ se cancela: el resultado no depende del tamaño de la caja.

#### Paso 7 · Comprobación
$0.568\,\hbar>0.5\,\hbar$: se cumple el principio de incertidumbre $\Delta x\Delta p_x\ge\hbar/2$. ✓ (El mínimo $\hbar/2$ solo lo alcanzan las gaussianas, como el estado fundamental del oscilador armónico.)
""", dx=f"{math.sqrt(1 / 12 - 1 / (2 * math.pi ** 2)):.4f}", p=f"{prod:.3f}")
    return Ejercicio(
        "s7_dxdp", "Incertidumbre en el estado fundamental de la caja", CLASE, "Semana 7 · Example Problem 3", "conmutadores",
        "Calcula $\\Delta x\\,\\Delta p_x$ para el estado fundamental de una partícula de masa $m$ en una caja de longitud $L$, "
        "con $\\psi(x)=(2/L)^{1/2}\\sin(\\pi x/L)$.",
        sol, (Parte("prod", "$\\Delta x\\,\\Delta p_x$ en unidades de $\\hbar$", NUM, prod, "ħ", tol_rel=0.01,
                    confusiones=((0.5 / prod, "$\\hbar/2$ es solo la cota inferior; hay que calcular las desviaciones"),)),),
        ("Necesitas $\\langle x\\rangle$, $\\langle x^2\\rangle$, $\\langle p_x\\rangle$ y $\\langle p_x^2\\rangle$.",
         "$\\langle p_x^2\\rangle$ sale directo: $\\psi$ es autofunción de $d^2/dx^2$."), MEDIO)


# ---------------------------------------------------------------------
# Semana 9 · Oscilador armónico
# ---------------------------------------------------------------------
def _nodos_n4() -> Ejercicio:
    y1 = (48 - math.sqrt(48 ** 2 - 4 * 16 * 12)) / 32
    y2 = (48 + math.sqrt(48 ** 2 - 4 * 16 * 12)) / 32
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La posición de los **nodos** (puntos donde $\psi=0$) del oscilador armónico con $n=4$.

#### Paso 2 · Dónde pueden estar los nodos
$\psi_4(x)=N_4\,H_4(\alpha x)\,e^{-\alpha^2x^2/2}$ (con $\alpha=(k\mu/\hbar^2)^{1/4}$). La gaussiana **nunca** vale cero, así que los nodos son los ceros del polinomio de Hermite:

$$H_4(\alpha x)=16(\alpha x)^4-48(\alpha x)^2+12=0$$

Debe haber $n=4$ nodos.

#### Paso 3 · Cambio de variable
Solo aparecen potencias pares; con $y=(\alpha x)^2$ queda una ecuación **cuadrática**:

$$16y^2-48y+12=0$$

#### Paso 4 · Fórmula cuadrática
$$y=\frac{48\pm\sqrt{48^2-4\cdot16\cdot12}}{2\cdot16}=\frac{48\pm\sqrt{2304-768}}{32}=\frac{48\pm\sqrt{1536}}{32}=\frac{48\pm39.19}{32}$$

$$y_1=<<y1>>\qquad y_2=<<y2>>$$

#### Paso 5 · Volver a $x$
$\alpha x=\pm\sqrt y$ (cada $y$ da **dos** nodos, uno a cada lado):

- $\alpha x=\pm\sqrt{<<y1>>}=\pm<<x1>>$
- $\alpha x=\pm\sqrt{<<y2>>}=\pm<<x2>>$

$$x=\pm\frac{<<x1>>}{\alpha}\quad\text{y}\quad x=\pm\frac{<<x2>>}{\alpha}$$

#### Paso 6 · Comprobación
Cuatro nodos ✓, colocados simétricamente porque $\psi_4$ es una función **par**. Ninguno en $x=0$ (solo los estados impares tienen nodo en el centro).
""", y1=f"{y1:.4f}", y2=f"{y2:.4f}", x1=f"{math.sqrt(y1):.4f}", x2=f"{math.sqrt(y2):.4f}")
    return Ejercicio(
        "s9_nodos", "Nodos del oscilador con n = 4", CLASE, "Semana 9 · Example Problem 1", "oscilador",
        "Localiza los nodos de la función de onda del oscilador armónico con $n=4$. Usa $H_4(\\alpha x)=16(\\alpha x)^4-48(\\alpha x)^2+12$.",
        sol, (Parte("x1", "Nodo interior: $\\alpha x$ (valor positivo)", NUM, math.sqrt(y1), tol_rel=0.01),
              Parte("x2", "Nodo exterior: $\\alpha x$ (valor positivo)", NUM, math.sqrt(y2), tol_rel=0.01,
                    confusiones=((y2 / math.sqrt(y2), "ese es $y=(\\alpha x)^2$; falta sacar la raíz"),))),
        ("La gaussiana nunca se anula: busca los ceros de $H_4$.", "Usa $y=(\\alpha x)^2$ para tener una cuadrática."), MEDIO)


def _gaussiana() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Comprobar que $\psi=e^{-\beta x^2}$ es solución de la ecuación de Schrödinger del oscilador, hallar la condición sobre $\beta$ y la energía $E$:

$$-\frac{\hbar^2}{2\mu}\frac{d^2\psi}{dx^2}+\frac12kx^2\psi=E\psi$$

#### Paso 2 · Derivar dos veces (regla de la cadena y del producto)
1. $\dfrac{d\psi}{dx}=-2\beta x\,e^{-\beta x^2}$
2. $\dfrac{d^2\psi}{dx^2}=-2\beta e^{-\beta x^2}+(-2\beta x)(-2\beta x)e^{-\beta x^2}=\left(-2\beta+4\beta^2x^2\right)e^{-\beta x^2}$

#### Paso 3 · Sustituir en el lado izquierdo
$$\hat H\psi=\left[\frac{\hbar^2\beta}{\mu}\;-\;\frac{2\hbar^2\beta^2}{\mu}x^2\;+\;\frac12kx^2\right]e^{-\beta x^2}$$

#### Paso 4 · Condición para que sea autofunción
Para que el resultado sea «constante × ψ», todo lo que depende de $x$ debe **cancelarse**: los dos términos con $x^2$.

$$\frac{2\hbar^2\beta^2}{\mu}=\frac12k\ \Rightarrow\ \beta^2=\frac{k\mu}{4\hbar^2}\ \Rightarrow\ \boxed{\beta=\frac{\sqrt{k\mu}}{2\hbar}}$$

(se toma la raíz positiva: con $\beta<0$ la función crecería sin límite y no se podría normalizar).

#### Paso 5 · La energía
Lo que queda es la constante:

$$E=\frac{\hbar^2\beta}{\mu}=\frac{\hbar^2}{\mu}\cdot\frac{\sqrt{k\mu}}{2\hbar}=\frac\hbar2\sqrt{\frac k\mu}=\boxed{\tfrac12\hbar\omega}$$

#### Paso 6 · Interpretación
Es el **estado fundamental** del oscilador ($n=0$) y su energía es la **energía de punto cero**, $\tfrac12\hbar\omega=\tfrac12h\nu$: el oscilador nunca está completamente quieto.
"""
    return Ejercicio(
        "s9_gaussiana", "La gaussiana es el estado fundamental", CLASE, "Semana 9 · Example Problem 2", "oscilador",
        "Muestra que la función $e^{-\\beta x^2}$ satisface la ecuación de Schrödinger del oscilador armónico cuántico. ¿Qué condición impone esto sobre $\\beta$? ¿Cuánto vale $E$?",
        sol, (Parte("E", "Energía $E$ en unidades de $\\hbar\\omega$", NUM, 0.5, "ħω"),
              Parte("beta", "$\\beta$ es igual a", OPC, opciones=("$\\sqrt{k\\mu}/(2\\hbar)$", "$\\sqrt{k\\mu}/\\hbar$", "$k\\mu/(4\\hbar^2)$", "$\\sqrt{k/\\mu}$"),
                    correcta=0, explicacion="De $2\\hbar^2\\beta^2/\\mu=k/2$.")),
        ("Deriva dos veces $e^{-\\beta x^2}$ (necesitarás la regla del producto en la segunda).",
         "Los términos con $x^2$ deben cancelarse."), MEDIO)


def _energias_psi1() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Los valores medios de la energía **cinética** y **potencial** del oscilador en $\psi_1(x)=\left(\dfrac{4\alpha^3}{\pi}\right)^{1/4}x\,e^{-\alpha x^2/2}$, con $\alpha=\sqrt{k\mu}/\hbar$.

#### Paso 2 · Camino rápido: teorema del virial
Para un potencial $V=ax^s$, el teorema del virial dice $2\langle E_k\rangle=s\langle E_p\rangle$. En el oscilador $V=\tfrac12kx^2$, así que $s=2$ y

$$\langle E_k\rangle=\langle E_p\rangle=\tfrac12E_n$$

Para $n=1$, $E_1=\tfrac32\hbar\omega$:

$$\langle E_k\rangle=\langle E_p\rangle=\boxed{\tfrac34\hbar\omega}$$

#### Paso 3 · Comprobación con la integral (energía potencial)
$$\langle E_p\rangle=\frac k2\langle x^2\rangle=\frac k2\left(\frac{4\alpha^3}{\pi}\right)^{1/2}\int_{-\infty}^{\infty}x^4e^{-\alpha x^2}dx$$

- El integrando es par: $\int_{-\infty}^{\infty}=2\int_0^\infty$.
- Integral de tabla: $\displaystyle\int_0^\infty x^{4}e^{-\alpha x^2}dx=\frac{1\cdot3}{2^{3}\alpha^{2}}\sqrt{\frac\pi\alpha}=\frac38\frac{\sqrt\pi}{\alpha^{5/2}}$
- Entonces $\langle x^2\rangle=\dfrac{2\alpha^{3/2}}{\sqrt\pi}\cdot2\cdot\dfrac38\dfrac{\sqrt\pi}{\alpha^{5/2}}=\dfrac{3}{2\alpha}$

$$\langle E_p\rangle=\frac k2\cdot\frac{3}{2\alpha}=\frac{3k}{4\alpha}=\frac{3k\hbar}{4\sqrt{k\mu}}=\frac34\hbar\sqrt{\frac k\mu}=\frac34\hbar\omega\ \checkmark$$

#### Paso 4 · Energía cinética
$\langle E_k\rangle=E_1-\langle E_p\rangle=\tfrac32\hbar\omega-\tfrac34\hbar\omega=\tfrac34\hbar\omega$. Coincide con el virial. ✓

#### Paso 5 · Dos erratas de la diapositiva
- La constante de normalización es $(4\alpha^3/\pi)^{1/4}$, **no** $(4\alpha^3/3)^{1/4}$. Con $\pi$ la función queda normalizada (se comprobó).
- En la integral de tabla el numerador es $1\times3\times5\times\cdots\times(2n-1)$, no $(2n+1)$. Para $n=2$ vale $1\cdot3=3$.
"""
    return Ejercicio(
        "s9_energias", "Energías cinética y potencial en ψ₁", CLASE, "Semana 9 · Example Problem 3", "oscilador",
        "¿Cuáles son los valores medios de la energía cinética y de la energía potencial de un oscilador armónico cuántico en el estado "
        "$\\psi_1(x)=(4\\alpha^3/\\pi)^{1/4}x\\,e^{-(1/2)\\alpha x^2}$? Usa $\\displaystyle\\int_0^\\infty x^{2n}e^{-ax^2}dx=\\frac{1\\cdot3\\cdot5\\cdots(2n-1)}{2^{n+1}a^n}\\sqrt{\\frac\\pi a}$.",
        sol, (Parte("Ek", "$\\langle E_k\\rangle$ en unidades de $\\hbar\\omega$", NUM, 0.75, "ħω"),
              Parte("Ep", "$\\langle E_p\\rangle$ en unidades de $\\hbar\\omega$", NUM, 0.75, "ħω")),
        ("El teorema del virial con $s=2$ da $\\langle E_k\\rangle=\\langle E_p\\rangle$.", "$E_1=\\frac32\\hbar\\omega$."), MEDIO,
        nota="La diapositiva escribe la constante como $(4\\alpha^3/3)^{1/4}$ y la integral con $(2n+1)$; aquí se usan las expresiones correctas, $(4\\alpha^3/\\pi)^{1/4}$ y $(2n-1)$.")


# ---------------------------------------------------------------------
# Semana 10 · Rotación
# ---------------------------------------------------------------------
def _norm_anillo() -> Ejercicio:
    a = 1 / math.sqrt(2 * math.pi)
    sol = llenar(r"""
#### Paso 1 · Qué se pide
La constante $A$ que normaliza $\Phi(\phi)=A\,e^{im_l\phi}$, la función de onda de una partícula en un anillo.

#### Paso 2 · Condición de normalización
La variable $\phi$ va de 0 a $2\pi$ (una vuelta completa):

$$\int_0^{2\pi}\Phi^*\Phi\,d\phi=1$$

#### Paso 3 · El producto $\Phi^*\Phi$
El conjugado cambia $i\to-i$: $\Phi^*=A^*e^{-im_l\phi}$. Al multiplicar, los exponentes se suman y se anulan:

$$\Phi^*\Phi=|A|^2e^{-im_l\phi}e^{im_l\phi}=|A|^2e^{0}=|A|^2$$

¡La densidad de probabilidad es **constante**: la partícula está igual de probable en cualquier punto del anillo!

#### Paso 4 · Integrar y despejar
$$|A|^2\int_0^{2\pi}d\phi=2\pi|A|^2=1\ \Rightarrow\ |A|=\frac1{\sqrt{2\pi}}=\mathbf{<<a>>}$$

Por convención se elige $A$ real y positiva.

#### Paso 5 · Resultado
$$\Phi_{m_l}(\phi)=\frac1{\sqrt{2\pi}}e^{im_l\phi},\qquad m_l=0,\pm1,\pm2,\dots$$
""", a=f"{a:.4f}")
    return Ejercicio(
        "s10_anillo", "Normalización de la partícula en un anillo", CLASE, "Semana 10 · Example Problem 4", "esfera",
        "Determina la constante de normalización $A$ de la función de onda $\\Phi(\\phi)=A\\,e^{im_l\\phi}$ ($0\\le\\phi\\le2\\pi$).",
        sol, (Parte("A", "Valor de $A$", NUM, a, tol_rel=0.01,
                    confusiones=((1 / (2 * math.pi) / a, "ese es $|A|^2$; falta la raíz cuadrada"),)),),
        ("$|e^{i\\theta}|^2=1$.",), BASICO)


def _lambda_y10() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Comprobar que $Y_{1,0}=N\cos\theta$ es autofunción del operador angular $\Lambda^2$ con autovalor $-l(l+1)$, es decir, $\Lambda^2Y_{1,0}=-2\,Y_{1,0}$ (porque $l=1$).

#### Paso 2 · El operador
$$\Lambda^2=\frac1{\sin\theta}\frac{\partial}{\partial\theta}\left(\sin\theta\frac{\partial}{\partial\theta}\right)+\frac{1}{\sin^2\theta}\frac{\partial^2}{\partial\phi^2}$$

$Y_{1,0}$ **no depende de $\phi$**, así que el segundo término da cero.

#### Paso 3 · Derivar de adentro hacia afuera
1. Derivada interna: $\dfrac{\partial}{\partial\theta}(N\cos\theta)=-N\sin\theta$
2. Multiplicar por $\sin\theta$: $\sin\theta\cdot(-N\sin\theta)=-N\sin^2\theta$
3. Derivar otra vez: $\dfrac{\partial}{\partial\theta}(-N\sin^2\theta)=-2N\sin\theta\cos\theta$ (regla de la cadena)
4. Dividir entre $\sin\theta$: $\dfrac{-2N\sin\theta\cos\theta}{\sin\theta}=-2N\cos\theta$

#### Paso 4 · Comparar
$$\Lambda^2Y_{1,0}=-2N\cos\theta=-2\,Y_{1,0}$$

Es la misma función por $-2$, y $-l(l+1)=-1\cdot2=-2$. ✓

#### Paso 5 · Interpretación
$\hat l^2=-\hbar^2\Lambda^2$, así que $\hat l^2Y_{1,0}=2\hbar^2Y_{1,0}$: el momento angular total tiene magnitud $\sqrt2\,\hbar$.
"""
    return Ejercicio(
        "s10_lambda", "Y₁,₀ es autofunción de Λ²", CLASE, "Semana 10 · Example Problem 5", "esfera",
        "Confirma que el armónico esférico $Y_{1,0}=N\\cos\\theta$ es solución de $\\Lambda^2Y_{l,m_l}=-l(l+1)Y_{l,m_l}$.",
        sol, (Parte("aut", "Autovalor de $\\Lambda^2$ para $Y_{1,0}$", NUM, -2.0, tol_rel=0.0, tol_abs=0.01),),
        ("$Y_{1,0}$ no depende de $\\phi$.", "Deriva $\\cos\\theta$, multiplica por $\\sin\\theta$, deriva otra vez y divide entre $\\sin\\theta$."), BASICO)


def _conos_1000() -> Ejercicio:
    theta = math.degrees(math.acos(math.sqrt(1000 / 1001)))
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Para $l=1000$: **a)** cuántos conos (valores de $m_l$) hay; **b)** el menor ángulo posible entre $\vec l$ y el eje $z$.

#### Paso 2 · Número de conos
$m_l$ toma los valores $-l,-l+1,\dots,0,\dots,l-1,l$: en total $2l+1$ valores.

$$2(1000)+1=\mathbf{2001}\ \text{conos}$$

#### Paso 3 · Ángulo de cada cono
El vector $\vec l$ tiene longitud $\sqrt{l(l+1)}\,\hbar$ y su proyección sobre $z$ es $m_l\hbar$. Por trigonometría:

$$\cos\theta=\frac{m_l}{\sqrt{l(l+1)}}$$

#### Paso 4 · El menor ángulo: $m_l=l=1000$
$$\cos\theta=\frac{1000}{\sqrt{1000\times1001}}=\sqrt{\frac{1000}{1001}}=<<c>>$$

$$\theta=\arccos(<<c>>)=\mathbf{<<t>>^\circ}$$

*Ojo con el redondeo:* $\cos\theta$ es casi 1 y el arcocoseno es muy sensible ahí. Hay que conservar varias cifras. La diapositiva da 1.7° porque redondea $\sqrt{1000\cdot1001}$ a 1000.50; con más cifras sale 1.81°.

#### Paso 5 · Interpretación
Aun con $m_l$ máximo, el vector **nunca** apunta exactamente sobre el eje $z$ ($\theta\ne0$): si lo hiciera conoceríamos $l_x=l_y=0$ además de $l_z$, y esas componentes no conmutan. Para $l$ grande el ángulo se hace pequeño y se recupera el comportamiento clásico.
""", c=f"{math.sqrt(1000 / 1001):.7f}", t=f"{theta:.2f}")
    return Ejercicio(
        "s10_conos", "Conos de momento angular con l = 1000", CLASE, "Semana 10 · Example Problem 6", "esfera",
        "¿Cuántos conos (valores de $m_l$) hay para $l=1000$? ¿Cuál es el menor ángulo permitido entre $\\vec l$ y el eje $z$?",
        sol, (Parte("n", "Número de conos", NUM, 2001.0, tol_rel=0.0, tol_abs=0.1),
              Parte("theta", "Menor ángulo (en grados)", NUM, theta, "°", tol_rel=0.02)),
        ("Hay $2l+1$ valores de $m_l$.", "$\\cos\\theta=m_l/\\sqrt{l(l+1)}$; conserva muchas cifras."), BASICO,
        nota="La diapositiva da θ = 1.7° por un redondeo; el valor correcto es 1.81°.")


# ---------------------------------------------------------------------
# Semana 11 · Átomo de hidrógeno
# ---------------------------------------------------------------------
def _decaimiento() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
Mostrar que, lejos del núcleo, las funciones de onda de los estados **ligados** decaen exponencialmente a cero.

#### Paso 2 · La ecuación radial con $u=rR$
Con $u(r)=rR(r)$ la ecuación radial es

$$-\frac{\hbar^2}{2\mu}\frac{d^2u}{dr^2}+\left[\frac{l(l+1)\hbar^2}{2\mu r^2}-\frac{Ze^2}{4\pi\varepsilon_0r}\right]u=Eu$$

#### Paso 3 · Qué términos sobreviven cuando $r\to\infty$
El corchete tiene un término con $1/r^2$ y otro con $1/r$: los dos **tienden a cero**. Queda

$$\frac{d^2u}{dr^2}\simeq-\frac{2\mu E}{\hbar^2}u$$

#### Paso 4 · De $u$ a $R$
$\dfrac{d^2(rR)}{dr^2}=r\dfrac{d^2R}{dr^2}+2\dfrac{dR}{dr}$. Para $r$ grande domina el primer término, así que $\dfrac{d^2u}{dr^2}\simeq r\dfrac{d^2R}{dr^2}$ y

$$\frac{d^2R}{dr^2}\simeq-\frac{2\mu E}{\hbar^2}R=+\frac{2\mu|E|}{\hbar^2}R$$

porque en un estado ligado $E<0$ (el electrón no tiene energía para escapar), y $-E=|E|$.

#### Paso 5 · Resolver
Una función cuya segunda derivada es **un número positivo** por ella misma es una exponencial real: $R\simeq e^{\pm\sqrt{2\mu|E|}\,r/\hbar}$. La de signo $+$ crece sin límite y no se puede normalizar; se descarta:

$$R\simeq e^{-\sqrt{2\mu|E|/\hbar^2}\;r}$$

#### Paso 6 · Interpretación
Toda función de un estado ligado decae como una exponencial, más rápido cuanto más ligada (mayor $|E|$). Es general: a distancias grandes cualquier distribución esférica de carga se ve como una carga puntual. (Si $E>0$, el electrón está libre y la solución oscila en lugar de decaer.)
"""
    return Ejercicio(
        "s11_decaimiento", "Las funciones ligadas decaen exponencialmente", CLASE, "Semana 11 · Example Problem 1", "hidrogeno",
        "Muestra que a grandes distancias del núcleo las funciones de onda atómicas de estados ligados decaen exponencialmente a cero.",
        sol, (Parte("signo", "¿Qué propiedad de $E$ hace que la solución sea una exponencial decreciente y no una onda?", OPC,
                    opciones=("$E<0$ (estado ligado)", "$E>0$", "$E=0$", "$l=0$"), correcta=0,
                    explicacion="Con $E<0$, $R''=+(2\\mu|E|/\\hbar^2)R$: exponenciales reales."),),
        ("¿Qué pasa con los términos $1/r$ y $1/r^2$ cuando $r\\to\\infty$?",), MEDIO)


def _nodos_3s() -> Ejercicio:
    r1, r2 = 1.5 * (3 - math.sqrt(3)), 1.5 * (3 + math.sqrt(3))
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Los **nodos radiales** de la función $R_{30}$ ($n=3$, $l=0$: el orbital 3s). Debe haber $n-l-1=2$.

#### Paso 2 · Dónde se anula $R_{30}$
$R_{30}\propto\left(6-6\rho+\rho^2\right)e^{-\rho/2}$ con $\rho=\dfrac{2Zr}{3a_0}$. La exponencial nunca vale cero, así que los nodos son las raíces del polinomio:

$$\rho^2-6\rho+6=0$$

#### Paso 3 · Fórmula cuadrática
$$\rho=\frac{6\pm\sqrt{36-24}}{2}=\frac{6\pm\sqrt{12}}{2}=\frac{6\pm2\sqrt3}{2}=3\pm\sqrt3$$

$\rho_1=3-\sqrt3=1.268$ y $\rho_2=3+\sqrt3=4.732$.

#### Paso 4 · Volver a $r$
De $\rho=\dfrac{2Zr}{3a_0}$ se despeja $r=\dfrac{3a_0}{2Z}\rho$. Para el hidrógeno ($Z=1$):

- $r_1=1.5\times1.268\,a_0=\mathbf{<<r1>>\,a_0}$
- $r_2=1.5\times4.732\,a_0=\mathbf{<<r2>>\,a_0}$

#### Paso 5 · Comprobación
Dos nodos ✓. En cada uno la función **cambia de signo** (es una raíz simple del polinomio), por eso son nodos verdaderos. Para un ion con $Z$ mayor los nodos se acercan al núcleo como $1/Z$.
""", r1=f"{r1:.3f}", r2=f"{r2:.3f}")
    return Ejercicio(
        "s11_nodos3s", "Nodos radiales del orbital 3s", CLASE, "Semana 11 · Example Problem 2", "hidrogeno",
        "Encuentra los nodos de la función radial con $n=3$ y $l=0$. Sus ceros ocurren donde $6-6\\rho+\\rho^2=0$, con $\\rho=2Zr/3a_0$. "
        "Da los resultados para el hidrógeno ($Z=1$) en unidades de $a_0$.",
        sol, (Parte("r1", "Nodo interior (en $a_0$)", NUM, r1, "a₀", tol_rel=0.01,
                    confusiones=((1 / 1.5, "ese es el valor de $\\rho$; falta pasar a $r=\\frac{3a_0}{2Z}\\rho$"),)),
              Parte("r2", "Nodo exterior (en $a_0$)", NUM, r2, "a₀", tol_rel=0.01,
                    confusiones=((1 / 1.5, "ese es el valor de $\\rho$; falta pasar a $r=\\frac{3a_0}{2Z}\\rho$"),))),
        ("Resuelve la cuadrática en $\\rho$.", "Después despeja $r$ de $\\rho=2Zr/3a_0$."), BASICO)


def _punto_2pz() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide y qué función usar
El **punto del espacio** donde es más probable encontrar un electrón $2p_z$. Ojo: se pide el punto donde $|\psi|^2$ es máxima (densidad de probabilidad), **no** el máximo de la distribución radial $r^2R^2$. La función es

$$\psi_{210}=R_{21}(r)\,Y_{10}(\theta)\qquad R_{21}\propto\rho\,e^{-\rho/2},\ \ \rho=\frac{Zr}{a_0}\qquad Y_{10}\propto\cos\theta$$

Como se separa en un factor radial y uno angular, se maximiza cada uno por separado.

#### Paso 2 · Parte angular
$|\cos\theta|$ es máximo (vale 1) en $\theta=0$ y $\theta=\pi$: **a lo largo del eje $z$**, a ambos lados del núcleo.

#### Paso 3 · Parte radial: derivar e igualar a cero
$$\frac{d}{d\rho}\left(\rho\,e^{-\rho/2}\right)=e^{-\rho/2}+\rho\left(-\tfrac12\right)e^{-\rho/2}=\left(1-\frac\rho2\right)e^{-\rho/2}=0$$

La exponencial no se anula, así que $1-\dfrac\rho2=0\Rightarrow\rho=2$, es decir

$$r=\frac{2a_0}{Z}$$

(es un máximo: para $\rho<2$ la derivada es positiva y para $\rho>2$ es negativa).

#### Paso 4 · Resultado
Hay **dos** puntos de máxima probabilidad: $r=2a_0/Z$ sobre el eje $z$ positivo ($\theta=0$) y sobre el negativo ($\theta=\pi$). Para el hidrógeno, a $2a_0=105.8$ pm del núcleo.

#### Paso 5 · Comparación útil
La **distribución radial** $P(r)=r^2R_{21}^2\propto r^4e^{-r/a_0}$ tiene su máximo en $4a_0$. No es contradicción: $P(r)$ cuenta toda una capa esférica (el factor $r^2$ crece con el área), mientras que aquí se pregunta por **un punto**.
"""
    return Ejercicio(
        "s11_2pz", "Punto más probable de un electrón 2pz", CLASE, "Semana 11 · Example Problem 3", "hidrogeno",
        "¿Cuál es el punto del espacio más probable en el que se encontrará un electrón $2p_z$ hidrogenoide? "
        "(Usa $R_{21}\\propto\\rho e^{-\\rho/2}$ con $\\rho=Zr/a_0$ y $Y_{10}\\propto\\cos\\theta$.)",
        sol, (Parte("r", "Distancia al núcleo $r$ (en unidades de $a_0/Z$)", NUM, 2.0, "a₀/Z",
                    confusiones=((2.0, "4 a₀ es el máximo de la distribución radial $r^2R^2$; aquí se pide el punto de máxima $|\\psi|^2$"),)),
              Parte("dir", "Dirección", OPC, opciones=("Sobre el eje $z$ ($\\theta=0$ y $\\pi$)", "En el plano $xy$", "Sobre los conos de 54.7°"),
                    correcta=0, explicacion="$|\\cos\\theta|$ es máximo en los polos.")),
        ("Maximiza por separado la parte angular y la radial.", "Deriva $\\rho e^{-\\rho/2}$ e iguala a cero."), MEDIO)


# ---------------------------------------------------------------------
# Semana 13 · Espín y método variacional
# ---------------------------------------------------------------------
def _helio_excitado() -> Ejercicio:
    sol = r"""
#### Paso 1 · Qué se pide
El primer estado excitado del helio es $1s^12s^1$: un electrón en $1s$ y otro en $2s$. Como cada uno puede tener espín $\alpha$ (↑) o $\beta$ (↓), hay **cuatro** combinaciones (los cuatro dibujos). Hay que escribir el determinante de Slater de cada una.

#### Paso 2 · Por qué un determinante
Los electrones son indistinguibles y la función total debe cambiar de signo al intercambiarlos. Un determinante de Slater lo garantiza: intercambiar dos electrones = intercambiar dos **filas**, y eso cambia el signo del determinante. Para 2 electrones el factor de normalización es $1/\sqrt{2!}=1/\sqrt2$.

#### Paso 3 · Cómo se arma
Cada **columna** es un espín-orbital ocupado y cada **fila** un electrón. Solo hay que leer en cada dibujo qué espín tiene el electrón de $1s$ y cuál el de $2s$:

| Dibujo | 1s | 2s | Columnas |
|---|---|---|---|
| 1 | ↑ | ↓ | $1s\alpha$, $2s\beta$ |
| 2 | ↑ | ↑ | $1s\alpha$, $2s\alpha$ |
| 3 | ↓ | ↓ | $1s\beta$, $2s\beta$ |
| 4 | ↓ | ↑ | $1s\beta$, $2s\alpha$ |

#### Paso 4 · Los cuatro determinantes
$$\psi^1=\frac1{\sqrt2}\begin{vmatrix}1s(1)\alpha(1)&2s(1)\beta(1)\\1s(2)\alpha(2)&2s(2)\beta(2)\end{vmatrix}\qquad\psi^2=\frac1{\sqrt2}\begin{vmatrix}1s(1)\alpha(1)&2s(1)\alpha(1)\\1s(2)\alpha(2)&2s(2)\alpha(2)\end{vmatrix}$$

$$\psi^3=\frac1{\sqrt2}\begin{vmatrix}1s(1)\beta(1)&2s(1)\beta(1)\\1s(2)\beta(2)&2s(2)\beta(2)\end{vmatrix}\qquad\psi^4=\frac1{\sqrt2}\begin{vmatrix}1s(1)\beta(1)&2s(1)\alpha(1)\\1s(2)\beta(2)&2s(2)\alpha(2)\end{vmatrix}$$

#### Paso 5 · Desarrollar uno para ver qué significa
$$\psi^2=\frac1{\sqrt2}\left[1s(1)2s(2)-2s(1)1s(2)\right]\alpha(1)\alpha(2)$$

Al cambiar $1\leftrightarrow2$ el corchete cambia de signo. ✓

#### Paso 6 · Comentario
$\psi^2$ y $\psi^3$ (espines paralelos) son estados **triplete**. $\psi^1$ y $\psi^4$ no son, por separado, estados de espín total definido: sus combinaciones $\psi^1\pm\psi^4$ dan el singlete y el tercer componente del triplete. Aquí no se pide, pero explica por qué los dibujos «no deben tomarse literalmente».
"""
    return Ejercicio(
        "s13_helio", "Determinantes del helio 1s¹2s¹", CLASE, "Semana 13 · Example Problem 1", "espin",
        "El primer estado excitado del helio se describe con la configuración $1s^12s^1$. Hay cuatro orientaciones de espín compatibles: "
        "(1) 1s↑ 2s↓, (2) 1s↑ 2s↑, (3) 1s↓ 2s↓, (4) 1s↓ 2s↑. Escribe las funciones de onda (determinantes) que corresponden a cada una.",
        sol, (Parte("n", "¿Cuántos determinantes distintos hay?", NUM, 4.0, tol_rel=0.0, tol_abs=0.1),
              Parte("d2", "Columnas del determinante de la orientación (2), 1s↑ 2s↑", OPC,
                    opciones=("$1s\\alpha$ y $2s\\alpha$", "$1s\\alpha$ y $1s\\beta$", "$1s\\alpha$ y $2s\\beta$", "$2s\\alpha$ y $2s\\beta$"), correcta=0,
                    explicacion="Cada columna es el espín-orbital de un electrón: 1s con α y 2s con α.")),
        ("Una columna por espín-orbital ocupado, una fila por electrón.", "Normalización: $1/\\sqrt{2}$."), BASICO)


def _variacional() -> Ejercicio:
    e0, emin, alfa = 0.13298405353, 0.12701790140, -0.34464713938
    sol = llenar(r"""
#### Paso 1 · Qué se pide
Aplicar el **método variacional** a la partícula en la caja con la función de prueba

$$\Phi(x)=\left(\frac xa-\frac{x^3}{a^3}\right)+\alpha\left(\frac{x^5}{a^5}-\frac12\left(\frac{x^7}{a^7}+\frac{x^9}{a^9}\right)\right),\qquad0<x<a$$

Primero con $\alpha=0$ y después con el $\alpha$ óptimo. Comparar con el valor exacto $E_0=\dfrac{h^2}{8ma^2}=0.125\,\dfrac{h^2}{ma^2}$.

#### Paso 2 · El teorema variacional
Para **cualquier** función de prueba que cumpla las condiciones de frontera,

$$E[\Phi]=\frac{\int\Phi^*\hat H\Phi\,dx}{\int\Phi^*\Phi\,dx}\ \ge\ E_0$$

El denominador está porque $\Phi$ no tiene por qué estar normalizada. Cuanto mejor sea $\Phi$, más cerca de $E_0$.

*Comprobación de frontera:* en $x=0$ todo vale 0; en $x=a$ el primer paréntesis da $1-1=0$ y el segundo $1-\tfrac12(1+1)=0$. ✓

#### Paso 3 · Caso $\alpha=0$
$\Phi=\dfrac xa-\dfrac{x^3}{a^3}$. Con $u=x/a$:

- $\dfrac{d^2\Phi}{dx^2}=-\dfrac{6x}{a^3}=-\dfrac{6u}{a^2}$ y $dx=a\,du$, así que $-\dfrac{\hbar^2}{2m}\displaystyle\int_0^a\Phi\,\Phi''dx=\dfrac{\hbar^2}{2m}\cdot\dfrac{6}{a}\int_0^1(u-u^3)\,u\,du=\dfrac{3\hbar^2}{ma}\left(\frac13-\frac15\right)=\dfrac{2\hbar^2}{5ma}$
- $\displaystyle\int_0^a\Phi^2dx=a\int_0^1(u-u^3)^2du=a\left(\frac13-\frac25+\frac17\right)=\frac{8a}{105}$

$$E=\frac{2\hbar^2/5ma}{8a/105}=\frac{2\cdot105}{5\cdot8}\frac{\hbar^2}{ma^2}=\frac{21}{4}\frac{\hbar^2}{ma^2}=\frac{21}{16\pi^2}\frac{h^2}{ma^2}=\mathbf{<<e0>>\,\frac{h^2}{ma^2}}$$

Es **mayor** que 0.125, como exige el teorema (error del 6.4 %).

#### Paso 4 · Energía en función de $\alpha$
Haciendo las mismas integrales con el $\alpha$ general:

$$E(\alpha)=\frac{\hbar^2}{2ma^2}\;\frac{\frac45+\frac{116\alpha}{231}+\frac{40247\alpha^2}{109395}}{\frac8{105}+\frac{8\alpha}{273}+\frac{1514\alpha^2}{230945}}$$

(con $\alpha=0$ da $\frac{\hbar^2}{2ma^2}\cdot\frac{4/5}{8/105}=\frac{21}{4}\frac{\hbar^2}{ma^2}$, igual que en el paso 3 ✓).

#### Paso 5 · Minimizar
Se deriva respecto de $\alpha$ y se iguala a cero. Es un cociente de dos cuadráticas, así que la condición resulta una ecuación de segundo grado con dos raíces:

$$\alpha=-5.74\qquad\text{y}\qquad\alpha=<<al>>$$

Se evalúa $E$ en las dos: la primera es un **máximo** ($E\approx1.03\,h^2/ma^2$) y la segunda el **mínimo**:

$$E_{\min}=E(<<al>>)=\mathbf{<<em>>\,\frac{h^2}{ma^2}}$$

#### Paso 6 · Comparación y conclusión
| Función de prueba | $E$ (en $h^2/ma^2$) | Error |
|---|---|---|
| $\alpha=0$ | <<e0>> | <<err0>> % |
| $\alpha$ óptimo | <<em>> | <<err1>> % |
| Exacta | 0.1250 | — |

Siempre por **encima** del valor exacto. Optimizar el parámetro mejora mucho la energía, pero no se puede bajar más con esta familia de funciones: es la limitación del método.

*Errata de la diapositiva:* en el primer enunciado aparece $-\tfrac12(x^7/a^7-x^9/a^9)$; el signo correcto es **+**, el de la fórmula grande. Solo con **+** la función se anula en $x=a$ y salen los $\alpha$ de la diapositiva.
""", e0=f"{e0:.4f}", em=f"{emin:.4f}", al=f"{alfa:.3f}", err0=f"{100 * (e0 / 0.125 - 1):.1f}", err1=f"{100 * (emin / 0.125 - 1):.1f}")
    return Ejercicio(
        "s13_variacional", "Método variacional en la caja", CLASE, "Semana 13 · ejemplo del método variacional", "aproximados",
        "Para la partícula en una caja de longitud $a$ se usa la función de prueba "
        "$\\Phi(x)=\\left(\\dfrac xa-\\dfrac{x^3}{a^3}\\right)+\\alpha\\left(\\dfrac{x^5}{a^5}-\\dfrac12\\left(\\dfrac{x^7}{a^7}+\\dfrac{x^9}{a^9}\\right)\\right)$.\n\n"
        "**a)** Calcula la energía variacional con $\\alpha=0$. **b)** Encuentra el valor óptimo de $\\alpha$ y la energía mínima. "
        "Compara con el valor exacto $E_0=0.125\\,h^2/ma^2$.",
        sol, (Parte("E0", "a) $E$ con $\\alpha=0$ (en $h^2/ma^2$)", NUM, e0, "h²/ma²", tol_rel=0.01),
              Parte("alfa", "b) $\\alpha$ óptimo", NUM, alfa, tol_rel=0.02,
                    confusiones=((-5.74 / alfa, "esa raíz corresponde a un máximo de $E(\\alpha)$; evalúa la energía en las dos"),)),
              Parte("Emin", "b) Energía mínima (en $h^2/ma^2$)", NUM, emin, "h²/ma²", tol_rel=0.005)),
        ("$E=\\int\\Phi\\hat H\\Phi\\,dx/\\int\\Phi^2dx$ (la función no está normalizada).", "Para minimizar, $dE/d\\alpha=0$; comprueba cuál raíz da la menor energía."),
        AVANZADO, nota="En la diapositiva la primera vez aparece −½(x⁷/a⁷ − x⁹/a⁹); el signo correcto es +, que es el que cumple Φ(a) = 0.")


EJERCICIOS = (_espaciado(), _superposicion(), _prob_tercio(), _x_medio_caja(),
              _p_t_conmutan(), _x_p(), _dxdp(),
              _nodos_n4(), _gaussiana(), _energias_psi1(),
              _norm_anillo(), _lambda_y10(), _conos_1000(),
              _decaimiento(), _nodos_3s(), _punto_2pz(),
              _helio_excitado(), _variacional())
