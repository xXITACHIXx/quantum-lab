"""
talleres/_soluciones.py — Soluciones paso a paso de los talleres.

Cada solución sigue el mismo guion para que el estudiante aprenda el método y no solo el resultado:
    Qué se pide y qué datos hay  →  idea física  →  fórmula  →  sustitución con unidades  →  resultado  →  comprobación y error típico.
Todos los números se calculan con los mismos valores del enunciado (originales o nuevos) que se están mostrando.
"""

from __future__ import annotations

import math

from talleres import _fisica as f
from talleres._modelo import tex


# ---------------------------------------------------------------------
# Taller 1
# ---------------------------------------------------------------------
def vibracion_rotacion(mol: str, a: str, b: str, k: float, R: float, mu: float, I: float, nu_v: float, nu_r: float, nu_r1: float) -> str:
    ma, mb = f.MASA[a], f.MASA[b]
    mu_kg = mu * f.U
    w = math.sqrt(k / mu_kg)
    B = f.constante_rotacional_hz(I)
    nu_r2 = f.frecuencia_rotacion(2, I)
    return rf"""
#### Paso 1 · Qué se pide y con qué datos
Se piden dos frecuencias: la de la **segunda** transición de vibración pura de menor energía (apartado a) y la de la **segunda** de rotación pura de menor energía (apartado b).
Datos: $k={k:g}$ N/m, $r_e={R}$ pm. Antes de calcular, pasa todo a unidades del SI: $r_e={R}\ \text{{pm}}={R}\times10^{{-12}}\ \text{{m}}={tex(R * 1e-12)}$ m.

#### Paso 2 · Masa reducida
Una molécula diatómica que vibra o gira se comporta como **una sola partícula** de masa $\mu$ (masa reducida):

$$\mu=\frac{{m_1m_2}}{{m_1+m_2}}=\frac{{({ma:.5g}\ \text{{u}})({mb:.5g}\ \text{{u}})}}{{({ma:.5g}+{mb:.5g})\ \text{{u}}}}={mu:.5g}\ \text{{u}}$$

Como $1\ \text{{u}}=1.6605\times10^{{-27}}$ kg: $\mu={mu:.5g}\times1.6605\times10^{{-27}}={tex(mu_kg)}$ kg.
*Comprobar:* $\mu$ siempre es menor que la masa más ligera ({ma:.3f} u); aquí es casi igual porque el otro átomo es mucho más pesado.

#### Paso 3 · Vibración (apartado a)
**Idea.** El enlace es un resorte: oscilador armónico, con niveles $E_n=h\nu\left(n+\tfrac12\right)$, $n=0,1,2,\dots$. Los niveles están **igualmente espaciados** y la regla de selección permite solo $\Delta n=\pm1$. Entonces toda transición pura sube exactamente un escalón:

$$\Delta E=E_{{n+1}}-E_n=h\nu\quad\text{{para cualquier }}n$$

Por eso la transición $0\to1$ (la más baja) y la $1\to2$ (la segunda) **tienen la misma frecuencia**: en el modelo armónico no existe una segunda transición «más alta».

**Fórmula.** $\nu=\dfrac1{{2\pi}}\sqrt{{\dfrac k\mu}}$.

**Sustitución (paso a paso).**

1. $\dfrac k\mu=\dfrac{{{k:g}\ \text{{N/m}}}}{{{tex(mu_kg)}\ \text{{kg}}}}={tex(k / mu_kg)}\ \text{{s}}^{{-2}}$
2. $\omega=\sqrt{{k/\mu}}={tex(w)}\ \text{{rad/s}}$ (esta es la frecuencia **angular**)
3. $\nu=\dfrac{{\omega}}{{2\pi}}=\dfrac{{{tex(w)}}}{{2\pi}}=\mathbf{{{tex(nu_v)}\ \text{{Hz}}}}$

*Error típico:* quedarse en $\omega$ y olvidar dividir entre $2\pi$. Si el resultado obtenido es 6.28 veces mayor, corresponde a este error.

#### Paso 4 · Momento de inercia
Para la rotación se necesita $I=\mu r_e^2$:

$$I=({tex(mu_kg)}\ \text{{kg}})({tex(R * 1e-12)}\ \text{{m}})^2=\mathbf{{{tex(I)}\ \text{{kg m}}^2}}$$

#### Paso 5 · Rotación (apartado b)
**Idea.** Rotor rígido: $E_l=\dfrac{{\hbar^2}}{{2I}}\,l(l+1)$, con $l=0,1,2,\dots$ La regla de selección es $\Delta l=\pm1$. Al **absorber**, $l\to l+1$:

$$\Delta E=E_{{l+1}}-E_l=\frac{{\hbar^2}}{{2I}}\left[(l+1)(l+2)-l(l+1)\right]=\frac{{\hbar^2}}{{I}}(l+1)\ \Rightarrow\ \nu=\frac{{\Delta E}}{{h}}=\frac{{h}}{{4\pi^2I}}(l+1)=2B(l+1)$$

con la **constante rotacional** $B=\dfrac{{h}}{{8\pi^2I}}=\dfrac{{{tex(f.H)}}}{{8\pi^2({tex(I)})}}={tex(B)}\ \text{{Hz}}$.

Aquí **los escalones no son iguales**: cada transición está separada de la anterior por $2B$:

| Transición | Frecuencia | Valor |
|---|---|---|
| $l=0\to1$ (la más baja) | $2B$ | ${tex(nu_r1)}$ Hz |
| $l=1\to2$ (**la segunda**) | $4B$ | $\mathbf{{{tex(nu_r)}}}$ **Hz** |
| $l=2\to3$ (la tercera) | $6B$ | ${tex(nu_r2)}$ Hz |

*Error típico:* tomar $2B$ (la primera) en lugar de $4B$: cuenta bien cuál es la «segunda».

#### Paso 6 · Resultados y comprobación
- **a)** $\nu_{{\text{{vib}}}}={tex(nu_v)}$ Hz (la misma para $0\to1$ y $1\to2$).
- **b)** $\nu_{{\text{{rot}}}}(1\to2)={tex(nu_r)}$ Hz.

*Orden de magnitud:* la vibración es unas **{nu_v / nu_r:.0f} veces** más rápida que la rotación. Por eso la vibración aparece en el infrarrojo ($10^{{13}}$–$10^{{14}}$ Hz) y la rotación en microondas ($10^{{11}}$–$10^{{12}}$ Hz).
"""


def afinidad(Z: int, ion: str, formado: str, E1: float) -> str:
    return rf"""
#### Paso 1 · Qué se pide
La **afinidad electrónica** del {ion} es la energía que se **libera** cuando ese ion captura un electrón. Aquí el electrón termina en el estado fundamental ($n=1$) del ion que se forma, {formado}.

#### Paso 2 · Identificar el ion que se forma
El {ion} ya perdió todos sus electrones: solo queda el núcleo, con carga $+{Z}e$. Al capturar un electrón se forma {formado}: **un solo electrón** alrededor de un núcleo con $Z={Z}$. Es un ion **hidrogenoide**, así que la fórmula del enunciado vale con $Z={Z}$.

#### Paso 3 · Energía del estado fundamental
$$E_n=-\frac{{Z^2e^2}}{{8\pi\varepsilon_0a_0\,n^2}}=-\frac{{Z^2}}{{n^2}}\,(13.606\ \text{{eV}})$$

Con $n=1$ y $Z={Z}$ (nótese que $Z$ se eleva **al cuadrado**, $Z^2={Z ** 2}$):

$$E_1=-\frac{{{Z}^2}}{{1^2}}(13.606\ \text{{eV}})=-{Z ** 2}\times13.606\ \text{{eV}}=\mathbf{{{tex(E1)}\ \text{{eV}}}}$$

#### Paso 4 · De la energía a la afinidad
Tomamos como referencia energía $0$ para el electrón libre y en reposo (lejos del núcleo). Al caer al nivel $n=1$ su energía pasa de $0$ a $E_1<0$, y la diferencia **se libera**:

$$\text{{AE}}=E_{{\text{{inicial}}}}-E_{{\text{{final}}}}=0-E_1=-({tex(E1)})=\mathbf{{+{tex(-E1)}\ \text{{eV}}}}$$

#### Paso 5 · Comprobación
- La afinidad es **positiva** (se libera energía): el electrón queda atrapado.
- Escala como $Z^2$: para $Z=1$ sería $13.6$ eV (el hidrógeno); con $Z={Z}$ es ${Z ** 2}$ veces mayor.
- Es la misma energía que habría que **dar** para ionizar el {formado} desde su estado fundamental: capturar e ionizar son procesos inversos.
"""


# ---------------------------------------------------------------------
# Taller 2
# ---------------------------------------------------------------------
def x_esperado(n: int) -> str:
    detalle_n0 = r"""
Para el estado fundamental la función es una gaussiana, $\psi_0(x)=\left(\dfrac{\alpha}{\sqrt\pi}\right)^{1/2}e^{-\alpha^2x^2/2}$ con $\alpha^2=\mu\omega/\hbar$, y se puede hacer la integral a mano:

$$\langle x\rangle=\frac{\alpha}{\sqrt\pi}\int_{-\infty}^{\infty}x\,e^{-\alpha^2x^2}\,dx=\frac{\alpha}{\sqrt\pi}\left[-\frac{e^{-\alpha^2x^2}}{2\alpha^2}\right]_{-\infty}^{\infty}=\frac{\alpha}{\sqrt\pi}\,(0-0)=0$$

(la primitiva de $x\,e^{-\alpha^2x^2}$ es $-e^{-\alpha^2x^2}/2\alpha^2$, que vale 0 en $+\infty$ y en $-\infty$).
""" if n == 0 else ""
    return rf"""
#### Paso 1 · Qué se pide
El **valor esperado de la posición** es el promedio de $x$ ponderado por la probabilidad. Con la función de onda $\psi_{{{n}}}$ del estado $n={n}$:

$$\langle x\rangle=\int_{{-\infty}}^{{\infty}}\psi_{{{n}}}^*(x)\,x\,\psi_{{{n}}}(x)\,dx=\int_{{-\infty}}^{{\infty}}x\,|\psi_{{{n}}}(x)|^2\,dx$$

La posición $x$ se mide **desde el centro** (la distancia de equilibrio), por eso puede ser positiva o negativa.

#### Paso 2 · Idea: mirar la simetría antes de integrar
La energía potencial $V=\tfrac12kx^2$ es **simétrica** respecto a $x=0$: $V(-x)=V(x)$. Por eso las funciones de onda tienen paridad definida:

$$\psi_n(-x)=(-1)^n\,\psi_n(x)\qquad\Rightarrow\qquad |\psi_n(-x)|^2=|\psi_n(x)|^2\ \ (\text{{la densidad es par}})$$

(para $n={n}$ la función es {"par" if n % 2 == 0 else "impar"}, pero su cuadrado es par en todos los casos).

#### Paso 3 · El integrando es impar
- $x$ es una función **impar**: $(-x)=-x$.
- $|\psi_n|^2$ es **par**.
- Impar × par = **impar**: $x\,|\psi_n|^2$ cambia de signo al reflejar $x\to-x$.

La integral de una función impar sobre un intervalo simétrico $(-\infty,\infty)$ es **cero**: lo que aporta el lado derecho lo cancela el izquierdo.
{detalle_n0}
#### Paso 4 · Resultado
$$\boxed{{\langle x\rangle=0}}$$

#### Paso 5 · Interpretación y error típico
- Significa que, **en promedio**, la molécula está en la distancia de equilibrio: pasa el mismo tiempo estirada que comprimida.
- **No** significa que esté quieta ni que $x=0$ siempre: la dispersión $\sqrt{{\langle x^2\rangle}}$ no es cero (para $n=0$ vale $x_0/\sqrt2$).
- Hábito útil: antes de calcular una integral sobre un intervalo simétrico, **pregunta si el integrando es par o impar**. Si es impar, el resultado es 0 sin hacer cuentas.
"""


def longitud_desde_nu(mol: str, a: str, b: str, nu: float, mu: float, I: float, R_pm: float) -> str:
    ma, mb = f.MASA[a], f.MASA[b]
    mu_kg = mu * f.U
    B = nu / 2
    return rf"""
#### Paso 1 · Qué se pide y qué transición es
Se da la frecuencia de la transición de rotación pura **de menor energía** y se pide la longitud de enlace. La transición más baja del rotor rígido es $l=0\to1$ (con $\Delta l=+1$). Su frecuencia es

$$\nu=2B\qquad\text{{con}}\qquad B=\frac{{h}}{{8\pi^2I}}$$

Es decir, midiendo $\nu$ se obtiene $I$, y de $I$ la distancia entre los átomos. Dato: $\nu={tex(nu)}$ Hz.

#### Paso 2 · Despejar el momento de inercia
$$\nu=2B=\frac{{h}}{{4\pi^2I}}\ \Rightarrow\ I=\frac{{h}}{{4\pi^2\nu}}$$

Sustituyendo ($h=6.626\times10^{{-34}}$ J s):

$$I=\frac{{{tex(f.H)}\ \text{{J s}}}}{{4\pi^2\,({tex(nu)}\ \text{{s}}^{{-1}})}}=\mathbf{{{tex(I)}\ \text{{kg m}}^2}}$$

*Comprobar las unidades:* J s / s⁻¹ = (kg m² s⁻²)(s)(s) = kg m². ✓

#### Paso 3 · Masa reducida
$$\mu=\frac{{m_1m_2}}{{m_1+m_2}}=\frac{{({ma:.5g})({mb:.5g})}}{{{ma:.5g}+{mb:.5g}}}={mu:.5g}\ \text{{u}}={tex(mu_kg)}\ \text{{kg}}$$

#### Paso 4 · De $I$ a la longitud de enlace
Como $I=\mu r_e^2$:

$$r_e=\sqrt{{\frac{{I}}{{\mu}}}}=\sqrt{{\frac{{{tex(I)}}}{{{tex(mu_kg)}}}}}={tex(R_pm * 1e-12)}\ \text{{m}}$$

#### Paso 5 · Pasar a picómetros
$1\ \text{{pm}}=10^{{-12}}$ m, así que

$$r_e=\frac{{{tex(R_pm * 1e-12)}\ \text{{m}}}}{{10^{{-12}}\ \text{{m/pm}}}}=\mathbf{{{R_pm:.2f}\ \text{{pm}}}}$$

#### Paso 6 · Comprobación
- Un enlace covalente típico mide entre 70 y 250 pm: el resultado es razonable.
- **Prueba inversa:** con $r_e={R_pm:.2f}$ pm se obtiene $I=\mu r_e^2={tex(mu_kg * (R_pm * 1e-12) ** 2)}$ kg m², que coincide con el del paso 2. ✓
- *Errores típicos:* usar $\nu=B$ en lugar de $2B$ (error de factor 2 en $I$, factor $\sqrt2$ en $r_e$) o dejar $r_e$ en metros.
"""


def orbital_d(n: int, l: int, nombre: str, maximos: list, nodos: list, r_max: float, theta_nodal: float, P_en_maximos: list) -> str:
    maxtxt = ", ".join(f"{r:.2f}" for r in maximos)
    if (n, l) == (3, 2):
        radial = r"""
**Función radial.** Para 3d la parte radial es $R_{32}(r)\propto r^2e^{-r/3a_0}$ (no tiene nodos: $n-l-1=0$). La distribución radial es la probabilidad de encontrar el electrón en una **capa esférica** de radio $r$ y grosor $dr$:

$$P(r)=r^2\,R_{32}(r)^2\ \propto\ r^2\cdot r^4e^{-2r/3a_0}=r^6e^{-2r/3a_0}$$

(el factor $r^2$ es el área de la capa esférica, por eso $P(0)=0$ aunque $R_{32}$ sea grande cerca del núcleo).

**Máximo: se deriva e iguala a cero.** Con $r$ en unidades de $a_0$, conviene derivar el logaritmo:

$$\frac{d}{dr}\ln P=\frac6r-\frac23=0\ \Rightarrow\ r=\mathbf{9\,a_0}$$

(es el máximo que da la regla general $r=n^2a_0$ para orbitales con $l=n-1$).

**Menor densidad radial.** $P=0$ en $r=0$ y, para $r\to\infty$, la exponencial $e^{-2r/3}$ domina y $P\to0$. Como no hay nodos radiales, no hay más ceros."""
    else:
        radial = rf"""
**Función radial.** Para {nombre}, $R_{{{n}{l}}}(r)$ tiene $n-l-1={n - l - 1}$ **nodo radial** (una esfera donde $R=0$) en $r={', '.join(f'{x:.2f}' for x in nodos)}\,a_0$. La distribución radial es la probabilidad por capa esférica:

$$P(r)=r^2\,R_{{{n}{l}}}(r)^2$$

**Máximos.** Se buscan los puntos donde $dP/dr=0$ (numéricamente): $r={maxtxt}\,a_0$. Los valores de $P$ en ellos son {', '.join(f'{p:.4f}' for p in P_en_maximos)} (por $a_0$): el mayor es el de $r={r_max:.2f}\,a_0$.

**Menor densidad radial.** En el nodo $r={', '.join(f'{x:.2f}' for x in nodos)}\,a_0$ y en $r=0$ la distribución vale exactamente 0."""
    return rf"""
#### Paso 1 · Qué se pide
Para el orbital {nombre}$_{{z^2}}$ del hidrógeno ($n={n}$, $l={l}$, $m=0$) hay que localizar **dónde hay más y menos densidad electrónica**, en dos partes: la radial (distancia al núcleo) y la angular (dirección). Esto es posible porque el orbital se **separa**:

$$\psi_{{n l m}}(r,\theta,\varphi)=R_{{nl}}(r)\;Y_l^m(\theta,\varphi)$$

La parte radial dice *a qué distancia* y la angular *en qué dirección*.

#### Paso 2 · Parte radial (apartado a)
{radial}

**Resultado a).** Mayor densidad radial en $r=\mathbf{{{r_max:.2f}\,a_0}}$ ($\approx{r_max * 0.0529177:.3f}$ nm); menor en $r=0$, en $r\to\infty$ y en los nodos radiales ({len(nodos)} en este orbital).

#### Paso 3 · Parte angular (apartado b)
**Función.** Para $l=2$, $m=0$:

$$Y_2^0(\theta)=\sqrt{{\frac{{5}}{{16\pi}}}}\,\left(3\cos^2\theta-1\right)\qquad\Rightarrow\qquad|Y_2^0|^2=\frac{{5}}{{16\pi}}\left(3\cos^2\theta-1\right)^2$$

**Máximos.** El paréntesis $(3\cos^2\theta-1)$ es lo más grande en valor absoluto cuando $\cos^2\theta=1$, es decir $\theta=0^\circ$ y $180^\circ$ (el **eje $z$**): ahí vale $2$ y $|Y|^2=\dfrac{{5}}{{4\pi}}\approx0.398$.

**Ceros (nodos angulares).** Se anula cuando

$$3\cos^2\theta-1=0\ \Rightarrow\ \cos\theta=\pm\frac1{{\sqrt3}}=\pm0.5774\ \Rightarrow\ \theta=\mathbf{{{theta_nodal:.2f}^\circ}}\ \text{{y}}\ {180 - theta_nodal:.2f}^\circ$$

Son dos **conos** alrededor del eje $z$ (superficies nodales).

**El anillo del plano $xy$.** En $\theta=90^\circ$, $\cos\theta=0$ y $(3\cdot0-1)^2=1$: la densidad es $\dfrac{{5}}{{16\pi}}\approx0.099$, **un cuarto del máximo**. Es un máximo local más pequeño, en forma de anillo (la «rosquilla» característica del $d_{{z^2}}$).

**Resultado b).** Mayor densidad angular a lo largo del eje $z$; se anula en los conos $\theta={theta_nodal:.2f}^\circ$ y ${180 - theta_nodal:.2f}^\circ$.

#### Paso 4 · Comprobación
- Normalización: la función $Y_2^0$ está normalizada, $\int|Y_2^0|^2\,d\Omega=1$, y $R_{{{n}{l}}}$ también ($\int P\,dr=1$): se comprobó numéricamente.
- Número de nodos: en total hay $n-1={n - 1}$ superficies nodales; $l=2$ son **angulares** (aquí, los dos conos) y $n-l-1={n - l - 1}$ **radiales**. ✓
"""


def litio() -> str:
    return r"""
#### Paso 1 · Qué se pide
Escribir una función de onda **aproximada** para el litio ($Z=3$, tres electrones) que cumpla el **principio de antisimetría**, para (a) el estado fundamental y (b) un estado excitado en el que el último electrón está en $2p$.

#### Paso 2 · Idea física: los electrones son indistinguibles y fermiones
Si se intercambian dos electrones cualesquiera, la función de onda total debe **cambiar de signo**:

$$\Psi(\ldots,\mathbf{x}_i,\ldots,\mathbf{x}_j,\ldots)=-\Psi(\ldots,\mathbf{x}_j,\ldots,\mathbf{x}_i,\ldots)$$

donde $\mathbf{x}$ incluye posición **y espín**. Un simple producto de orbitales no cumple esto.

#### Paso 3 · Espín-orbitales
Cada electrón se describe con un **espín-orbital** = orbital espacial × función de espín ($\alpha$ = espín arriba, $\beta$ = espín abajo). Para $1s^22s^1$ se necesitan **tres**:

- $1s\alpha$ y $1s\beta$: los dos electrones del $1s$ (mismo orbital, espines opuestos);
- $2s\alpha$ (o $2s\beta$): el tercero, en $2s$.

No pueden estar dos electrones en el mismo espín-orbital: es el **principio de exclusión de Pauli**.

#### Paso 4 · Construir el determinante de Slater
Se coloca cada espín-orbital en una columna y cada electrón en una fila. Con $N=3$ electrones el factor de normalización es $1/\sqrt{N!}=1/\sqrt6$:

$$\Psi_0=\frac1{\sqrt{6}}\begin{vmatrix}1s\alpha(1)&1s\beta(1)&2s\alpha(1)\\1s\alpha(2)&1s\beta(2)&2s\alpha(2)\\1s\alpha(3)&1s\beta(3)&2s\alpha(3)\end{vmatrix}$$

**Por qué funciona:** al intercambiar dos electrones se intercambian dos **filas**, y un determinante cambia de signo al intercambiar filas. ✓ Y si dos espín-orbitales fueran iguales, tendría dos **columnas** idénticas y valdría 0 (Pauli).

#### Paso 5 · Estado excitado (apartado b)
Se excita el último electrón de $2s$ a $2p$: se **sustituye** su espín-orbital y el resto se deja igual ($1s^22p^1$):

$$\Psi_1=\frac1{\sqrt{6}}\begin{vmatrix}1s\alpha(1)&1s\beta(1)&2p\alpha(1)\\1s\alpha(2)&1s\beta(2)&2p\alpha(2)\\1s\alpha(3)&1s\beta(3)&2p\alpha(3)\end{vmatrix}$$

#### Paso 6 · Por qué se descartan las otras opciones
| Opción | Problema |
|---|---|
| Producto simple $1s(1)1s(2)2s(3)$ | No es antisimétrico: al intercambiar electrones no cambia de signo. |
| Determinante con $1s\alpha$ repetido | Dos columnas iguales: vale 0, no es una función de onda posible (viola Pauli). |
| Determinante $1s\alpha$, $2s\alpha$, $2s\beta$ | Deja el $1s$ medio vacío: es el estado $1s^12s^2$, otro estado excitado, no el fundamental. |
| Determinante 2×2 | Describe solo dos electrones; el litio tiene tres. |
"""


# ---------------------------------------------------------------------
# Taller 3
# ---------------------------------------------------------------------
def orbital_3p(r_in: float, r_out: float, nodo: float, p_in: float, p_out: float) -> str:
    return rf"""
#### Paso 1 · Qué se pide
Localizar las zonas de **mayor y menor densidad electrónica** del orbital $3p_z$ ($n=3$, $l=1$, $m=0$) del hidrógeno: primero a lo largo del radio (apartado a) y luego según la dirección (apartado b). Se usa $\psi=R_{{31}}(r)\,Y_1^0(\theta)$.

#### Paso 2 · Parte radial (apartado a)
**Función.** $R_{{31}}(r)\propto r\left(1-\dfrac{{r}}{{6a_0}}\right)e^{{-r/3a_0}}$.

**Nodo radial.** Se anula cuando el paréntesis es cero:

$$1-\frac{{r}}{{6a_0}}=0\ \Rightarrow\ r=\mathbf{{6\,a_0}}$$

(hay $n-l-1=1$ nodo radial; $r=0$ no cuenta porque ahí $P=0$ por el factor $r^2$.)

**Distribución radial.** Probabilidad por capa esférica: $P(r)=r^2R_{{31}}^2\propto r^4\left(1-\dfrac r6\right)^2e^{{-2r/3}}$ (con $r$ en $a_0$).

**Máximos.** Se deriva $\ln P=4\ln r+2\ln\left(1-\frac r6\right)-\frac{{2r}}{{3}}$ y se iguala a cero:

$$\frac4r-\frac{{2}}{{6-r}}-\frac23=0$$

Multiplicando por $3r(6-r)$ y ordenando:

$$12(6-r)-6r-2r(6-r)=0\ \Rightarrow\ 2r^2-30r+72=0\ \Rightarrow\ r^2-15r+36=0\ \Rightarrow\ (r-3)(r-12)=0$$

$$r=\mathbf{{3\,a_0}}\ \text{{(máximo interno)}}\qquad r=\mathbf{{12\,a_0}}\ \text{{(máximo externo)}}$$

**Cuál es el principal.** Se evalúa $P\propto r^4(1-r/6)^2e^{{-2r/3}}$: $P(3)\propto{p_in:.2f}$ y $P(12)\propto{p_out:.2f}$. El máximo **externo ($12\,a_0$) es más alto**: es la zona de mayor densidad radial.

**Resumen a).** Mayor densidad radial en $12\,a_0$ (principal) y $3\,a_0$ (secundaria); **menor** en el nodo $r=6\,a_0$ y en $r=0$.

#### Paso 3 · Parte angular (apartado b)
Para $l=1$, $m=0$: $Y_1^0=\sqrt{{\dfrac{{3}}{{4\pi}}}}\cos\theta$, de modo que

$$|Y_1^0|^2=\frac{{3}}{{4\pi}}\cos^2\theta$$

- **Máximo** cuando $\cos^2\theta=1$: $\theta=0^\circ$ y $180^\circ$, es decir **a lo largo del eje $z$** (los dos lóbulos del $3p_z$), con valor $3/4\pi\approx0.239$.
- **Cero** cuando $\cos\theta=0$: $\theta=90^\circ$, el **plano $xy$**. Es el **plano nodal**: la probabilidad de encontrar el electrón en ese plano es exactamente 0.

#### Paso 4 · Comprobación
- Nodos totales: $n-1=2$. Uno es **radial** (la esfera $r=6a_0$) y uno **angular** ($l=1$: el plano $xy$). ✓
- Esa es la forma del $3p_z$: dos lóbulos sobre el eje $z$, **cada uno con dos capas** (interna y externa) separadas por la esfera nodal.
"""


def rotor(l: int, m: int, L: float, E: float) -> str:
    return rf"""
#### Paso 1 · Qué se pide y qué datos da el enunciado
Hay que calcular tres cantidades de una molécula que gira alrededor del eje $z$ (la normal a la superficie): su momento angular en $z$, su momento angular total y su energía de rotación. El enunciado da:

- el número cuántico del nivel: $l={l}$;
- la función de onda de la rotación: $\Phi(\varphi)=\dfrac{{1}}{{\sqrt{{2\pi}}}}e^{{i\,{m}\,\varphi}}$.

Con eso es suficiente, no hace falta ningún dato más.

#### Paso 2 · Componente $z$ (apartado a)
**Idea.** El momento angular en $z$ se obtiene aplicando su operador a la función de onda. Si la función es una **autofunción**, el resultado es la misma función multiplicada por un número: ese número es el valor medible.

$$\hat L_z=-i\hbar\frac{{\partial}}{{\partial\varphi}}$$

**Desarrollo paso a paso.** Se deriva respecto de $\varphi$ (el $i\,{m}$ del exponente baja multiplicando):

$$\hat L_z\Phi=-i\hbar\,\frac{{\partial}}{{\partial\varphi}}\left[\frac{{1}}{{\sqrt{{2\pi}}}}e^{{i{m}\varphi}}\right]=-i\hbar\,(i\,{m})\,\frac{{1}}{{\sqrt{{2\pi}}}}e^{{i{m}\varphi}}=(-i\cdot i)\,{m}\,\hbar\,\Phi$$

Como $-i\cdot i=-i^2=+1$:

$$\hat L_z\Phi={m}\,\hbar\,\Phi\ \Rightarrow\ \boxed{{L_z={m}\,\hbar}}$$

**Criterio práctico:** en $e^{{i m\varphi}}$ el número que multiplica a $\varphi$ **es** $m$, y $L_z=m\hbar$. El signo indica el sentido del giro (positivo: antihorario visto desde $+z$).

#### Paso 3 · Momento angular total (apartado b)
**Idea.** La **magnitud** del momento angular la fija el número cuántico $l$, no $m$. El operador $\hat L^2$ tiene valores propios $l(l+1)\hbar^2$:

$$|\vec L|=\sqrt{{l(l+1)}}\,\hbar=\sqrt{{{l}\cdot{l + 1}}}\,\hbar=\sqrt{{{l * (l + 1)}}}\,\hbar=\boxed{{{L:.4f}\,\hbar}}$$

**Comprobación de coherencia:** la componente $z$ nunca puede superar la magnitud total: $|L_z|={abs(m)}\hbar\le|\vec L|={L:.3f}\hbar$. ✓ (por eso $|m|\le l$).
*Error típico:* responder $l\hbar={l}\hbar$. La magnitud es $\sqrt{{l(l+1)}}\hbar$, siempre ligeramente mayor que $l\hbar$.

#### Paso 4 · Energía de rotación (apartado c)
**Idea.** Toda la energía es **cinética de rotación**, y para un cuerpo que gira con momento angular $L$ y momento de inercia $I$:

$$E=\frac{{L^2}}{{2I}}=\frac{{|\vec L|^2}}{{2I}}$$

Como $|\vec L|^2=l(l+1)\hbar^2$:

$$E=\frac{{l(l+1)\hbar^2}}{{2I}}=\frac{{{l * (l + 1)}\,\hbar^2}}{{2I}}=\boxed{{{E:g}\,\frac{{\hbar^2}}{{I}}}}$$

El enunciado no da la longitud de enlace ni la masa, así que **no se puede dar un número en julios**: el resultado se deja en unidades de $\hbar^2/I$, donde $I=\mu r_e^2$ es el momento de inercia de la molécula.

#### Paso 5 · Resumen
| Magnitud | Fórmula | Resultado |
|---|---|---|
| $L_z$ | $m\hbar$ (del exponente de $\Phi$) | ${m}\,\hbar$ |
| $\lvert\vec L\rvert$ | $\sqrt{{l(l+1)}}\,\hbar$ | ${L:.3f}\,\hbar$ |
| $E$ | $l(l+1)\hbar^2/2I$ | ${E:g}\,\hbar^2/I$ |
"""


# ---------------------------------------------------------------------
# Taller 4
# ---------------------------------------------------------------------
def moleculares_cn(esp: str) -> str:
    return rf"""
#### Paso 1 · Contar los electrones de valencia
Los orbitales moleculares de valencia se llenan con los electrones de valencia de ambos átomos (más o menos la carga):

| Especie | Cuenta | Total |
|---|---|---|
| CN⁻ | C (4) + N (5) + 1 de la carga negativa | **10** |
| CO | C (4) + O (6) | **10** |
| NO⁺ | N (5) + O (6) − 1 de la carga positiva | **10** |

{esp} tiene **10 electrones de valencia**: es **isoelectrónica con el N₂**, así que usa el mismo diagrama.

#### Paso 2 · Orbitales moleculares que se forman
Con los orbitales $2s$ y $2p$ de cada átomo se forman 8 orbitales moleculares: $\sigma_{{2s}}$, $\sigma^*_{{2s}}$, $\sigma_{{2p}}$, dos $\pi_{{2p}}$ ($\pi_x$ y $\pi_y$, degenerados), dos $\pi^*_{{2p}}$ y $\sigma^*_{{2p}}$.

#### Paso 3 · El orden de energía (apartado a)
Cuando los orbitales $2s$ y $2p$ de los átomos tienen energías **parecidas** (como en C, N y sus vecinos hasta N₂), el $\sigma_{{2s}}$ se mezcla con el $\sigma_{{2p}}$ y empuja al $\sigma_{{2p}}$ hacia **arriba**, por encima de los $\pi_{{2p}}$. Entonces:

$$\sigma_{{2s}}<\sigma^*_{{2s}}<\pi_{{2p}}\,(\pi_x,\pi_y)<\sigma_{{2p}}<\pi^*_{{2p}}\,(\pi^*_x,\pi^*_y)<\sigma^*_{{2p}}$$

(En O₂ y F₂ la separación $s$–$p$ es grande, no hay mezcla y el $\sigma_{{2p}}$ queda **debajo** de los $\pi$: ese es el orden que **no** corresponde a esta especie.)

#### Paso 4 · Llenar los orbitales (apartado b)
Se llenan de abajo arriba, 2 electrones por orbital (principio de exclusión) y los orbitales degenerados uno a uno (regla de Hund):

| Orbital | Electrones | Acumulado |
|---|---|---|
| $\sigma_{{2s}}$ | 2 | 2 |
| $\sigma^*_{{2s}}$ | 2 | 4 |
| $\pi_x$ y $\pi_y$ | 2 + 2 | 8 |
| $\sigma_{{2p}}$ | 2 | **10** ✓ |

$$\text{{Configuración: }}(\sigma_{{2s}})^2(\sigma^*_{{2s}})^2(\pi_{{2p}})^4(\sigma_{{2p}})^2$$

**Orden de enlace** = ½ (electrones enlazantes − antienlazantes). Enlazantes: $2+4+2=8$. Antienlazantes: $2$.

$$\text{{OE}}=\frac{{8-2}}{{2}}=\boxed{{3}}\ \ (\text{{triple enlace}})$$

Todos los electrones están apareados: la especie es **diamagnética**.

#### Paso 5 · Función de onda de los electrones $\pi$ (apartado c)
Los 4 electrones del conjunto $\pi_{{2p}}$ ocupan **cuatro espín-orbitales**: $\pi_x\alpha$, $\pi_x\beta$, $\pi_y\alpha$ y $\pi_y\beta$. Para que la función sea antisimétrica se usa un **determinante de Slater** (4 electrones: normalización $1/\sqrt{{4!}}=1/\sqrt{{24}}$):

$$\Psi_\pi=\frac1{{\sqrt{{24}}}}\begin{{vmatrix}}\pi_x\alpha(1)&\pi_x\beta(1)&\pi_y\alpha(1)&\pi_y\beta(1)\\\pi_x\alpha(2)&\pi_x\beta(2)&\pi_y\alpha(2)&\pi_y\beta(2)\\\pi_x\alpha(3)&\pi_x\beta(3)&\pi_y\alpha(3)&\pi_y\beta(3)\\\pi_x\alpha(4)&\pi_x\beta(4)&\pi_y\alpha(4)&\pi_y\beta(4)\end{{vmatrix}}$$

#### Paso 6 · Por qué se descartan las otras opciones de $\pi$
| Opción | Problema |
|---|---|
| Incluye $\pi^*$ | Los $\pi^*$ están **vacíos** en el estado fundamental. |
| Producto simple | No es antisimétrico. |
| Determinante 2×2 con $\pi_x\alpha,\pi_y\alpha$ | Describe solo 2 electrones, no los 4 del conjunto $\pi$. |
"""


def lcao(S: float, H11: float, K: float, r: dict) -> str:
    H12 = r["H12"]
    Eb, Ea = r["E_enlazante"], r["E_antienlazante"]
    cb, ca = r["c_enlazante"], r["c_antienlazante"]
    return rf"""
#### Paso 1 · Qué se pide y cómo se plantea
Dos orbitales atómicos $\phi_1$ y $\phi_2$ (un $2p_z$ de cada átomo) se combinan linealmente (método **LCAO**):

$$\psi=c_1\phi_1+c_2\phi_2$$

Hay que hallar las **energías** de los dos orbitales moleculares que resultan y sus **coeficientes**. Datos: $S_{{12}}={S}$ (solapamiento), $H_{{11}}=H_{{22}}={H11}$ eV (energía de cada orbital atómico) y $H_{{12}}=-{K}\,S_{{12}}\sqrt{{H_{{11}}H_{{22}}}}$.

#### Paso 2 · Calcular $H_{{12}}$ (la «interacción»)
$$\sqrt{{H_{{11}}H_{{22}}}}=\sqrt{{({H11})({H11})}}=\sqrt{{{H11 ** 2:.5g}}}={abs(H11)}\ \text{{eV}}\quad(\text{{la raíz es positiva}})$$

$$H_{{12}}=-{K}\times{S}\times{abs(H11)}=\mathbf{{{H12:.4g}\ \text{{eV}}}}$$

Es **negativo**: la interacción entre los orbitales baja la energía del orbital enlazante.

#### Paso 3 · La ecuación secular
El principio variacional lleva a dos ecuaciones lineales para $c_1$ y $c_2$; tienen solución distinta de cero solo si el determinante es cero:

$$\begin{{vmatrix}}H_{{11}}-E&H_{{12}}-ES\\H_{{12}}-ES&H_{{22}}-E\end{{vmatrix}}=0\ \Rightarrow\ (H_{{11}}-E)^2=(H_{{12}}-ES)^2$$

(se usó $H_{{22}}=H_{{11}}$). Sacando raíz cuadrada hay **dos** casos, que dan los dos orbitales:

- **Signo $+$:** $H_{{11}}-E=-(H_{{12}}-ES)\ \Rightarrow\ H_{{11}}+H_{{12}}=E(1+S)\ \Rightarrow\ E_+=\dfrac{{H_{{11}}+H_{{12}}}}{{1+S}}$
- **Signo $-$:** $H_{{11}}-E=+(H_{{12}}-ES)\ \Rightarrow\ H_{{11}}-H_{{12}}=E(1-S)\ \Rightarrow\ E_-=\dfrac{{H_{{11}}-H_{{12}}}}{{1-S}}$

#### Paso 4 · Sustituir
$$E_+=\frac{{{H11}+({H12:.4g})}}{{1+{S}}}=\frac{{{H11 + H12:.4g}}}{{{1 + S:.4g}}}=\mathbf{{{Eb:.4g}\ \text{{eV}}}}\quad(\text{{enlazante}})$$

$$E_-=\frac{{{H11}-({H12:.4g})}}{{1-{S}}}=\frac{{{H11 - H12:.4g}}}{{{1 - S:.4g}}}=\mathbf{{{Ea:.4g}\ \text{{eV}}}}\quad(\text{{antienlazante}})$$

#### Paso 5 · Coeficientes
**Relación entre $c_1$ y $c_2$.** De la primera ecuación, $c_1(H_{{11}}-E)+c_2(H_{{12}}-ES)=0$. Para $E_+$ se tiene $H_{{11}}-E_+=-(H_{{12}}-E_+S)$, y entonces $c_2=c_1$ (**en fase**). Para $E_-$ resulta $c_2=-c_1$ (**en oposición de fase**, con un nodo entre los núcleos).

**Normalización con solapamiento.** Como los orbitales no son ortogonales ($S\ne0$):

$$\int\psi^2\,d\tau=c_1^2+c_2^2+2c_1c_2S=1$$

- **Enlazante** ($c_2=c_1=c$): $2c^2(1+S)=1\ \Rightarrow\ c=\dfrac1{{\sqrt{{2(1+S)}}}}=\dfrac1{{\sqrt{{{2 * (1 + S):.4g}}}}}=\mathbf{{{cb:.4f}}}$
- **Antienlazante** ($c_2=-c$): $2c^2(1-S)=1\ \Rightarrow\ c=\dfrac1{{\sqrt{{2(1-S)}}}}=\dfrac1{{\sqrt{{{2 * (1 - S):.4g}}}}}=\mathbf{{{ca:.4f}}}$

$$\psi_+={cb:.4f}\,(\phi_1+\phi_2)\qquad\psi_-={ca:.4f}\,(\phi_1-\phi_2)$$

*Error típico:* usar $1/\sqrt2=0.7071$ para ambos. Eso solo vale si $S=0$.

#### Paso 6 · Interpretación y comprobación
- El enlazante queda **{abs(Eb - H11):.3g} eV por debajo** del orbital atómico ({H11} eV) y el antienlazante **{abs(Ea - H11):.3g} eV por encima**.
- El antienlazante sube **más** de lo que baja el enlazante. Es el efecto del solapamiento: con $S>0$ la repulsión de los electrones en el orbital antienlazante pesa más que la estabilización del enlazante.
- Si pusiéramos $S=0$ obtendríamos $E_\pm=H_{{11}}\pm H_{{12}}$, simétricos. Aquí no lo son.
- Comprobación numérica: resolver el problema de autovalores generalizado $H\mathbf c=E\,S\,\mathbf c$ con SciPy da los mismos dos valores.
"""


def alilo(ne: int, nombre: str, formula: str, x, C) -> str:
    llenado = {2: "los 2 electrones llenan el orbital más bajo ($E_1$)",
               3: "2 electrones llenan $E_1$ y el tercero va al orbital no enlazante $E_2$",
               4: "2 electrones llenan $E_1$ y los otros 2 llenan el no enlazante $E_2$"}[ne]
    energia = {2: r"2(\alpha+\sqrt2\beta)", 3: r"2(\alpha+\sqrt2\beta)+\alpha", 4: r"2(\alpha+\sqrt2\beta)+2\alpha"}[ne]
    total = {2: r"2\alpha+2\sqrt2\beta", 3: r"3\alpha+2\sqrt2\beta", 4: r"4\alpha+2\sqrt2\beta"}[ne]
    return rf"""
#### Paso 1 · Qué se pide
Para el {nombre} ({formula}) hay que (a) calcular la energía de sus electrones $\pi$ con el **método de Hückel** y (b) escribir el orbital molecular $\pi$ de menor energía con sus coeficientes. El sistema tiene 3 carbonos, cada uno con un orbital $p$ perpendicular al plano ($\phi_1,\phi_2,\phi_3$), y **{ne} electrones $\pi$**.

#### Paso 2 · Las reglas de Hückel
1. Cada orbital molecular es $\psi=c_1\phi_1+c_2\phi_2+c_3\phi_3$.
2. $H_{{ii}}=\alpha$ (energía de un electrón en un $p$ del carbono).
3. $H_{{ij}}=\beta$ si los carbonos $i$ y $j$ son **vecinos**, y $0$ si no lo son (aquí $C_1$–$C_2$ y $C_2$–$C_3$).
4. $S_{{ij}}=0$ (no se considera solapamiento) y $S_{{ii}}=1$.
5. $\beta<0$: una energía **más negativa** es más estable.

#### Paso 3 · Ecuación secular
Se escribe la energía como $E=\alpha+x\beta$ (así $x$ es «cuántas $\beta$ suma la energía»). Entonces $\alpha-E=-x\beta$, y al dividir cada fila entre $\beta$ la ecuación secular queda:

$$\begin{{vmatrix}}\alpha-E&\beta&0\\\beta&\alpha-E&\beta\\0&\beta&\alpha-E\end{{vmatrix}}=0\ \Rightarrow\ \begin{{vmatrix}}-x&1&0\\1&-x&1\\0&1&-x\end{{vmatrix}}=0$$

Se desarrolla el determinante por la primera fila:

$$-x\,(x^2-1)-1\,(-x-0)=-x^3+x+x=-x^3+2x=-x\,(x^2-2)=0$$

Las raíces son $x=\sqrt2,\ 0,\ -\sqrt2$. Con $\beta<0$, el mayor $x$ da la menor energía:

| Orbital | $x$ | Energía | Tipo |
|---|---|---|---|
| $\psi_1$ | $+\sqrt2$ | $E_1=\alpha+\sqrt2\,\beta$ | **enlazante** (el más bajo) |
| $\psi_2$ | $0$ | $E_2=\alpha$ | no enlazante |
| $\psi_3$ | $-\sqrt2$ | $E_3=\alpha-\sqrt2\,\beta$ | antienlazante |

(Como $\beta<0$, $\alpha+\sqrt2\beta$ es **menor** que $\alpha$: por eso es el más estable. $\sqrt2=1.4142$.)

#### Paso 4 · Llenar los orbitales y sumar la energía (apartado a)
Con {ne} electrones: {llenado}.

$$E_\pi={energia}={total}\approx{ne}\alpha+2.828\,\beta$$

**Observación:** el electrón (o par) del orbital no enlazante aporta $\alpha$ pero **ningún $\beta$**. Por eso el catión, el radical y el anión del alilo tienen el **mismo** término $2\sqrt2\beta$: lo que cambia es solo cuántos $\alpha$ hay ($n_\alpha={ne}$ aquí).

#### Paso 5 · Los coeficientes del orbital más bajo (apartado b)
Se sustituye $x=\sqrt2$ en las ecuaciones $-x\,c_1+c_2=0$, $c_1-x\,c_2+c_3=0$ y $c_2-x\,c_3=0$. Con $E_1$ el sistema es

$$-\sqrt2\,c_1+c_2=0\ \Rightarrow\ c_2=\sqrt2\,c_1\qquad c_2-\sqrt2\,c_3=0\ \Rightarrow\ c_3=\frac{{c_2}}{{\sqrt2}}=c_1$$

Se **normaliza** ($c_1^2+c_2^2+c_3^2=1$, porque $S=0$):

$$c_1^2+(\sqrt2c_1)^2+c_1^2=4c_1^2=1\ \Rightarrow\ c_1=\frac12,\quad c_2=\frac{{\sqrt2}}{{2}}=\frac1{{\sqrt2}}=0.7071,\quad c_3=\frac12$$

$$\boxed{{\psi_1=\tfrac12\,\phi_1+\tfrac1{{\sqrt2}}\,\phi_2+\tfrac12\,\phi_3}}$$

*Comprobación:* $\tfrac14+\tfrac12+\tfrac14=1$ ✓. Todos los coeficientes tienen el **mismo signo**: no hay nodos, el electrón está deslocalizado sobre los tres carbonos, con más probabilidad en el central ($c_2^2=\tfrac12$ frente a $\tfrac14$ en cada extremo).

#### Paso 6 · Los otros dos orbitales (para completar la imagen)
- $\psi_2=\dfrac1{{\sqrt2}}(\phi_1-\phi_3)$: **un nodo** en el carbono central (energía $\alpha$, no enlazante).
- $\psi_3=\tfrac12\phi_1-\tfrac1{{\sqrt2}}\phi_2+\tfrac12\phi_3$: **dos nodos** (el más alto, antienlazante).

Más nodos significan más energía: 0, 1 y 2 nodos para $E_1<E_2<E_3$.
"""
