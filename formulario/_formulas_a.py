"""formulario/_formulas_a.py — Fórmulas de los orígenes de la teoría cuántica hasta la partícula libre y las barreras."""

from __future__ import annotations

import math

import numpy as np
from scipy import constants as sc
from scipy.integrate import quad
from scipy.optimize import brentq

from formulario._modelo import Bloque, F, Seccion

h, hbar, c, e, me, kB, eps0 = sc.h, sc.hbar, sc.c, sc.e, sc.m_e, sc.k, sc.epsilon_0
a0 = sc.physical_constants["Bohr radius"][0]


def _x_wien() -> float:
    """Raíz de 5(1 − e^{−x}) = x (condición del máximo de la ley de Planck en longitud de onda)."""
    return brentq(lambda x: 5 * (1 - math.exp(-x)) - x, 1, 10)


def _planck_sobre_rj() -> tuple[float, float]:
    T, x = 300.0, 1e-6
    nu = x * kB * T / h
    planck = 8 * math.pi * h * nu ** 3 / c ** 3 / math.expm1(h * nu / (kB * T))
    return planck / (8 * math.pi * nu ** 2 * kB * T / c ** 3), 1.0


def _coef_RT() -> tuple[float, float]:
    k1, k2 = 1.7, 0.9
    return ((k1 - k2) / (k1 + k2)) ** 2 + 4 * k1 * k2 / (k1 + k2) ** 2, 1.0


CUERPO_NEGRO = Seccion("cuerpo_negro", "Radiación del cuerpo negro",
    "Distribución espectral de la radiación térmica y la hipótesis de Planck de la energía cuantizada.", (
    Bloque("Ley de Planck", (
        F("Distribución de Planck (por frecuencia)", r"u(\nu,T)\,d\nu=\frac{8\pi h\nu^{3}}{c^{3}}\,\frac{1}{e^{h\nu/k_BT}-1}\,d\nu",
          "Densidad de energía radiante por unidad de volumen en el intervalo de frecuencias $[\\nu,\\nu+d\\nu]$ dentro de una cavidad a temperatura $T$."),
        F("Distribución de Planck (por longitud de onda)", r"u(\lambda,T)\,d\lambda=\frac{8\pi hc}{\lambda^{5}}\,\frac{1}{e^{hc/\lambda k_BT}-1}\,d\lambda",
          "Misma distribución expresada por longitud de onda."),
        F("Energía cuantizada de los osciladores", r"E_n=nh\nu\qquad n=0,1,2,\dots",
          "Hipótesis de Planck: los osciladores de la pared solo intercambian energía en múltiplos enteros de $h\\nu$."),
    )),
    Bloque("Límites y leyes derivadas", (
        F("Límite de Rayleigh–Jeans", r"u(\nu,T)=\frac{8\pi\nu^{2}k_BT}{c^{3}}",
          "Es el límite de la distribución de Planck para $h\\nu\\ll k_BT$ (frecuencias bajas). Predecir una divergencia en el ultravioleta "
          "(catástrofe ultravioleta), que no se observa.", _planck_sobre_rj, 1e-5),
        F("Ley de desplazamiento de Wien", r"\lambda_{\max}\,T=b=\frac{hc}{4.9651\,k_B}=2.8978\times10^{-3}\ \mathrm{m\,K}",
          "Longitud de onda del máximo de $u(\\lambda,T)$. El número 4.9651 es la raíz de $5\\,(1-e^{-x})=x$.",
          lambda: (h * c / (_x_wien() * kB), sc.physical_constants["Wien wavelength displacement law constant"][0]), 1e-9),
        F("Ley de Stefan–Boltzmann", r"M=\sigma T^{4}\qquad\sigma=\frac{2\pi^{5}k_B^{4}}{15\,h^{3}c^{2}}=5.6704\times10^{-8}\ \mathrm{W\,m^{-2}K^{-4}}",
          "Excitancia radiante total (potencia emitida por unidad de área) de un cuerpo negro.",
          lambda: (2 * math.pi ** 5 * kB ** 4 / (15 * h ** 3 * c ** 2), sc.Stefan_Boltzmann), 1e-9),
    )),
), "cuerpo_negro")


def _contraste_h_sobre_e() -> tuple[float, float]:
    return h / e, 4.135667696923859e-15


FOTOELECTRICO = Seccion("fotoelectrico", "Efecto fotoeléctrico",
    "Emisión de electrones por una superficie iluminada: conservación de la energía con fotones de energía $h\\nu$.", (
    Bloque("Ecuación de Einstein", (
        F("Energía cinética máxima", r"E_{k}^{\max}=h\nu-\Phi",
          "$h\\nu$: energía del fotón incidente; $\\Phi$: función de trabajo del metal. Solo hay emisión si $h\\nu\\ge\\Phi$."),
        F("Frecuencia umbral", r"\Phi=h\nu_{0}\qquad\Longrightarrow\qquad\nu_{0}=\frac{\Phi}{h}",
          "Frecuencia mínima para que haya emisión; no depende de la intensidad de la luz."),
        F("Potencial de frenado", r"eV_{0}=E_{k}^{\max}=h\nu-\Phi\qquad\Longrightarrow\qquad V_{0}=\frac{h}{e}\,\nu-\frac{\Phi}{e}",
          "La pendiente de $V_0$ frente a $\\nu$ es $h/e=4.1357\\times10^{-15}\\ \\mathrm{V\\,s}$ (método de Millikan).", _contraste_h_sobre_e, 1e-9),
        F("Velocidad de los electrones emitidos", r"v_{\max}=\sqrt{\frac{2E_{k}^{\max}}{m_e}}",
          "Válida en el régimen no relativista ($E_k\\ll m_ec^2=511\\ \\mathrm{keV}$)."),
    )),
    Bloque("Energía del fotón", (
        F("Energía, frecuencia y longitud de onda", r"E=h\nu=\frac{hc}{\lambda}=\hbar\omega",
          "$c=\\lambda\\nu$. Para fotones en el vacío."),
        F("Forma práctica", r"E\,[\mathrm{eV}]=\frac{1239.84}{\lambda\,[\mathrm{nm}]}",
          "Resulta de $hc=1239.84\\ \\mathrm{eV\\,nm}$.", lambda: (h * c / e * 1e9, 1239.84198), 1e-7),
    )),
), "fotoelectrico")


def _lambda_electron_1V() -> tuple[float, float]:
    return h / math.sqrt(2 * me * e * 1.0), 1.226426e-9


DE_BROGLIE = Seccion("de_broglie", "Ondas de materia",
    "Dualidad onda-partícula: toda partícula de momento $p$ se asocia con una longitud de onda.", (
    Bloque("Relación de De Broglie", (
        F("Longitud de onda de De Broglie", r"\lambda=\frac{h}{p}=\frac{h}{mv}", "Para una partícula de masa $m$ y velocidad $v$ (no relativista)."),
        F("En función de la energía cinética", r"\lambda=\frac{h}{\sqrt{2mE_k}}", "Resulta de $p=\\sqrt{2mE_k}$."),
        F("Electrón acelerado por una diferencia de potencial", r"\lambda=\frac{h}{\sqrt{2m_e eV}}\approx\frac{1.226\ \mathrm{nm}}{\sqrt{V/\mathrm{V}}}",
          "Es válida para potenciales de aceleración que no alcanzan el régimen relativista (unos 10 kV).", _lambda_electron_1V, 1e-5),
        F("Momento relativista", r"pc=\sqrt{E_k\left(E_k+2mc^{2}\right)}", "Para $E_k$ comparable con $mc^2$; $\\lambda=h/p$ sigue valiendo."),
    )),
    Bloque("Difracción", (
        F("Ley de Bragg", r"n\lambda=2d\sin\theta\qquad n=1,2,3,\dots",
          "Máximos de difracción en un cristal de espaciado $d$; $\\theta$ es el ángulo medido desde los planos."),
    )),
), "de_broglie")


def _R_inf() -> tuple[float, float]:
    return me * e ** 4 / (8 * eps0 ** 2 * h ** 3 * c), sc.physical_constants["Rydberg constant"][0]


def _a0() -> tuple[float, float]:
    return 4 * math.pi * eps0 * hbar ** 2 / (me * e ** 2), a0


def _v_bohr() -> tuple[float, float]:
    return sc.alpha * c, sc.physical_constants["atomic unit of velocity"][0]


def _rydberg_eV() -> tuple[float, float]:
    return sc.Rydberg * h * c / e, sc.physical_constants["Rydberg constant times hc in eV"][0]


BOHR = Seccion("bohr", "Espectros atómicos y modelo de Bohr",
    "Niveles de energía del hidrógeno y de los iones hidrogenoides en el modelo de Bohr; series espectrales.", (
    Bloque("Niveles, radios y velocidades", (
        F("Energía de los niveles", r"E_n=-\frac{Z^{2}}{n^{2}}\,hcR_\infty=-\frac{m_eZ^{2}e^{4}}{8\varepsilon_0^{2}h^{2}n^{2}}\qquad hcR_\infty=13.6057\ \mathrm{eV}",
          "$Z$: número atómico; $n=1,2,3,\\dots$. Con la masa reducida del núcleo, $R=R_\\infty\\,\\mu/m_e$ con $\\mu=\\dfrac{m_em_N}{m_e+m_N}$.",
          _rydberg_eV, 1e-8),
        F("Radio de las órbitas", r"r_n=\frac{n^{2}}{Z}\,a_0\qquad a_0=\frac{4\pi\varepsilon_0\hbar^{2}}{m_ee^{2}}=0.52918\ \text{Å}",
          "$a_0$ es el radio de Bohr.", _a0, 1e-8),
        F("Velocidad del electrón", r"v_n=\frac{Z}{n}\,\alpha c\qquad\alpha=\frac{e^{2}}{4\pi\varepsilon_0\hbar c}\approx\frac{1}{137.036}",
          "$\\alpha c=2.1877\\times10^{6}\\ \\mathrm{m/s}$ es la velocidad en la primera órbita del hidrógeno.", _v_bohr, 1e-8),
        F("Cuantización del momento angular", r"L=n\hbar", "Postulado de Bohr."),
        F("Constante de Rydberg", r"R_\infty=\frac{m_ee^{4}}{8\varepsilon_0^{2}h^{3}c}=1.09737\times10^{7}\ \mathrm{m^{-1}}", "", _R_inf, 1e-8),
    )),
    Bloque("Transiciones y series", (
        F("Condición de frecuencia de Bohr", r"h\nu=\left|E_{n_2}-E_{n_1}\right|", "Absorción o emisión de un fotón entre niveles."),
        F("Número de onda de la transición", r"\tilde\nu=\frac{1}{\lambda}=R_\infty Z^{2}\left(\frac{1}{n_1^{2}}-\frac{1}{n_2^{2}}\right)\qquad n_2>n_1",
          "Fórmula de Rydberg. $\\tilde\\nu$ en $\\mathrm{m^{-1}}$ (o $\\mathrm{cm^{-1}}$ con $R_\\infty$ en $\\mathrm{cm^{-1}}$)."),
        F("Series espectrales del hidrógeno", r"n_1=1\ \text{(Lyman, UV)};\quad 2\ \text{(Balmer, visible)};\quad 3\ \text{(Paschen)};\quad 4\ \text{(Brackett)};\quad 5\ \text{(Pfund)}",
          "Paschen, Brackett y Pfund están en el infrarrojo."),
        F("Límite de una serie", r"\tilde\nu_{\lim}=\frac{R_\infty Z^{2}}{n_1^{2}}\qquad(n_2\to\infty)",
          "Corresponde a la ionización desde el nivel $n_1$. Para el hidrógeno en el estado fundamental, con la masa reducida del protón "
          "($R_H=109\\,677.6\\ \\mathrm{cm^{-1}}$): $\\lambda_{\\lim}=91.18\\ \\mathrm{nm}$; con $R_\\infty$ resultaría 91.13 nm.",
          lambda: (1e9 / (sc.Rydberg / (1 + me / sc.m_p)), 91.1763), 1e-5),
    )),
), "bohr")


ONDAS = Seccion("ondas", "Ondas y números complejos",
    "Descripción de ondas clásicas y herramientas con números complejos que usa la mecánica cuántica.", (
    Bloque("Ondas", (
        F("Onda viajera", r"\Psi(x,t)=A\cos(kx-\omega t)", "Se propaga hacia $+x$ con velocidad $v=\\omega/k$."),
        F("Magnitudes de la onda", r"k=\frac{2\pi}{\lambda}\qquad\omega=2\pi\nu\qquad v=\lambda\nu=\frac{\omega}{k}",
          "$k$: número de onda angular; $\\omega$: frecuencia angular."),
        F("Ecuación de onda clásica", r"\frac{\partial^{2}\Psi}{\partial x^{2}}=\frac{1}{v^{2}}\frac{\partial^{2}\Psi}{\partial t^{2}}", ""),
        F("Onda estacionaria", r"A\cos(kx-\omega t)+A\cos(kx+\omega t)=2A\cos(kx)\cos(\omega t)",
          "Superposición de dos ondas idénticas que viajan en sentidos opuestos."),
    )),
    Bloque("Números complejos", (
        F("Fórmula de Euler", r"e^{i\theta}=\cos\theta+i\sin\theta",
          "", lambda: (abs(np.exp(1j * 0.7) - (math.cos(0.7) + 1j * math.sin(0.7))), 0.0), 1e-12),
        F("Forma polar", r"z=a+ib=re^{i\theta}\qquad r=|z|=\sqrt{a^{2}+b^{2}}\qquad\theta=\operatorname{atan2}(b,a)",
          "$\\theta$ debe tomarse en el cuadrante correcto de $(a,b)$."),
        F("Conjugado y módulo", r"z^{*}=a-ib\qquad zz^{*}=|z|^{2}\qquad\left|e^{i\theta}\right|=1", ""),
        F("Coseno y seno con exponenciales", r"\cos\theta=\frac{e^{i\theta}+e^{-i\theta}}{2}\qquad\sin\theta=\frac{e^{i\theta}-e^{-i\theta}}{2i}", ""),
    )),
), "ondas")


SCHRODINGER = Seccion("schrodinger", "La ecuación de Schrödinger",
    "Ecuación fundamental de la dinámica de un sistema cuántico y su forma estacionaria.", (
    Bloque("Ecuación y soluciones", (
        F("Ecuación dependiente del tiempo", r"i\hbar\frac{\partial\Psi(x,t)}{\partial t}=\hat H\Psi(x,t)", "$\\hat H$: operador hamiltoniano."),
        F("Hamiltoniano de una partícula", r"\hat H=-\frac{\hbar^{2}}{2m}\frac{\partial^{2}}{\partial x^{2}}+V(x)", "En tres dimensiones, $\\partial_x^2\\to\\nabla^2$."),
        F("Ecuación independiente del tiempo", r"\hat H\psi(x)=E\psi(x)", "Cuando $V$ no depende del tiempo; $E$ es la energía del estado estacionario."),
        F("Estado estacionario", r"\Psi(x,t)=\psi(x)\,e^{-iEt/\hbar}\qquad|\Psi|^{2}=|\psi|^{2}",
          "La densidad de probabilidad de un estado estacionario no depende del tiempo."),
    )),
    Bloque("Interpretación probabilística", (
        F("Densidad de probabilidad", r"P(x)\,dx=|\Psi(x,t)|^{2}\,dx=\Psi^{*}\Psi\,dx", "Probabilidad de hallar la partícula entre $x$ y $x+dx$."),
        F("Normalización", r"\int_{-\infty}^{\infty}|\Psi|^{2}\,dx=1", "Condición que fija la constante multiplicativa de $\\psi$."),
        F("Probabilidad en un intervalo", r"P(a\le x\le b)=\int_{a}^{b}|\psi(x)|^{2}\,dx", ""),
        F("Densidad de corriente de probabilidad", r"J=\frac{\hbar}{2mi}\left(\psi^{*}\frac{d\psi}{dx}-\psi\frac{d\psi^{*}}{dx}\right)", "Para $\\psi=Ae^{ikx}$: $J=|A|^2\\hbar k/m$."),
        F("Condiciones de buen comportamiento", r"\psi\ \text{finita, univaluada y continua};\quad \frac{d\psi}{dx}\ \text{continua (si } V \text{ es finito)}", ""),
    )),
), "schrodinger")


def _xp_sobre_f() -> tuple[complex, complex]:
    """[x̂, p̂] f = iħ f para f = e^{−x²} en x = 0.8 (con las derivadas escritas a mano)."""
    x = 0.8
    f = math.exp(-x * x)
    xpf = x * (-1j * hbar) * (-2 * x * f)
    pxf = (-1j * hbar) * (f * (1 - 2 * x * x))
    return (xpf - pxf) / f, 1j * hbar


OPERADORES = Seccion("operadores", "Operadores, ortogonalidad y completitud",
    "Operadores lineales hermíticos, autofunciones, expansión en una base y valores esperados.", (
    Bloque("Operadores y autofunciones", (
        F("Ecuación de autovalores", r"\hat A\,\psi_n=a_n\,\psi_n", "$\\psi_n$: autofunción; $a_n$: autovalor."),
        F("Operador hermítico", r"\int f^{*}\,\hat A g\,dx=\int\left(\hat A f\right)^{*}g\,dx", "Sus autovalores son reales y sus autofunciones de autovalores distintos son ortogonales."),
        F("Operadores fundamentales (coordenadas)", r"\hat x=x\qquad\hat p_x=-i\hbar\frac{\partial}{\partial x}\qquad\hat T=\frac{\hat p^{2}}{2m}\qquad\hat H=\hat T+\hat V",
          "Representación en el espacio de posiciones.", _xp_sobre_f, 1e-12),
    )),
    Bloque("Base ortonormal y expansión", (
        F("Ortonormalidad", r"\int\psi_m^{*}\psi_n\,dx=\delta_{mn}", "$\\delta_{mn}=1$ si $m=n$ y $0$ si $m\\neq n$."),
        F("Expansión en autofunciones", r"\psi=\sum_n c_n\psi_n\qquad c_n=\int\psi_n^{*}\psi\,dx", "Las autofunciones de un operador hermítico forman un conjunto completo."),
        F("Normalización de la expansión", r"\sum_n|c_n|^{2}=1", "Si $\\psi$ y las $\\psi_n$ están normalizadas."),
    )),
    Bloque("Valores esperados", (
        F("Valor esperado", r"\langle A\rangle=\int\psi^{*}\hat A\,\psi\,dx\bigg/\int\psi^{*}\psi\,dx", "El denominador vale 1 si $\\psi$ está normalizada."),
        F("Valor esperado en una superposición", r"\langle A\rangle=\sum_n|c_n|^{2}a_n", "$|c_n|^2$ es la probabilidad de obtener $a_n$ en una medición."),
    )),
), "operadores")


POSTULADOS = Seccion("postulados", "Los cinco postulados",
    "Enunciado operacional de la mecánica cuántica.", (
    Bloque("Postulados", (
        F("1. Estado del sistema", r"\Psi(\mathbf r,t)", "Contiene toda la información del sistema; $|\\Psi|^2$ es la densidad de probabilidad."),
        F("2. Observables", r"A\ \longleftrightarrow\ \hat A\ \text{(operador lineal hermítico)}", "A cada magnitud física medible le corresponde un operador."),
        F("3. Resultados de una medición", r"\text{solo se obtiene un autovalor:}\quad\hat A\psi_n=a_n\psi_n", "Tras la medición, el estado colapsa a la autofunción correspondiente."),
        F("4. Valor medio", r"\langle A\rangle=\int\Psi^{*}\hat A\Psi\,d\tau", "Promedio de muchas mediciones sobre sistemas idénticos."),
        F("5. Evolución temporal", r"i\hbar\frac{\partial\Psi}{\partial t}=\hat H\Psi", "La ecuación de Schrödinger gobierna la evolución entre mediciones."),
    )),
    Bloque("Momento angular y energía", (
        F("Momento angular orbital", r"\hat{\mathbf L}=\mathbf r\times\hat{\mathbf p}\qquad\hat L_z=x\hat p_y-y\hat p_x=-i\hbar\frac{\partial}{\partial\phi}", ""),
        F("Probabilidad de un resultado", r"P(a_n)=|c_n|^{2}=\left|\int\psi_n^{*}\Psi\,d\tau\right|^{2}", "Para un autovalor no degenerado."),
    )),
), "postulados")


def _escalon_E_mayor() -> tuple[float, float]:
    return _coef_RT()


LIBRE_PARED = Seccion("libre_pared", "Partícula libre y pared de potencial",
    "Partícula sin fuerzas y su comportamiento ante un escalón o una barrera de potencial.", (
    Bloque("Partícula libre", (
        F("Función de onda y energía", r"\psi_k=Ae^{ikx}\qquad E=\frac{\hbar^{2}k^{2}}{2m}\qquad p=\hbar k", "Autofunción de $\\hat p$ con autovalor $\\hbar k$; no es normalizable en $\\mathbb R$."),
        F("Longitud de onda", r"\lambda=\frac{2\pi}{k}=\frac{h}{p}", ""),
    )),
    Bloque("Escalón de potencial de altura $V_0$", (
        F("Vectores de onda", r"k_1=\frac{\sqrt{2mE}}{\hbar}\qquad k_2=\frac{\sqrt{2m(E-V_0)}}{\hbar}\quad(E>V_0)", "$k_1$: región $x<0$; $k_2$: región $x>0$."),
        F("Coeficientes de reflexión y transmisión", r"R=\left(\frac{k_1-k_2}{k_1+k_2}\right)^{2}\qquad T=\frac{4k_1k_2}{(k_1+k_2)^{2}}\qquad R+T=1",
          "Clásicamente $R=0$ si $E>V_0$.", _escalon_E_mayor, 1e-12),
        F("Energía por debajo del escalón", r"\kappa=\frac{\sqrt{2m(V_0-E)}}{\hbar}\qquad\psi(x>0)\propto e^{-\kappa x}\quad(E<V_0)",
          "La partícula penetra en la región prohibida con probabilidad decreciente; $R=1$."),
        F("Profundidad de penetración", r"\delta=\frac{1}{\kappa}", "Distancia a la que la amplitud $\\psi$ cae por un factor $e$ (la densidad $|\\psi|^2$, por $e^{2}$)."),
    )),
    Bloque("Efecto túnel", (
        F("Transmisión a través de una barrera ancha", r"T\approx e^{-2\kappa L}\qquad(\kappa L\gg1)",
          "Barrera rectangular de altura $V_0>E$ y anchura $L$. Es una aproximación: el prefactor exacto depende de $E/V_0$."),
    )),
), "libre_pared")
