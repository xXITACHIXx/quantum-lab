"""formulario/_formulas_b.py — Fórmulas de los modelos cuánticos (caja, oscilador, rotación, hidrógeno), espín, métodos aproximados, moléculas y matemática."""

from __future__ import annotations

import math

import numpy as np
from scipy import constants as sc
from scipy.integrate import quad
from scipy.linalg import eigh
from scipy.optimize import brentq
from scipy.special import eval_hermite

from formulario import _masas
from formulario._modelo import Bloque, F, Seccion

h, hbar, c, e, me, kB = sc.h, sc.hbar, sc.c, sc.e, sc.m_e, sc.k


# ---------------------------------------------------------------------
# Caja
# ---------------------------------------------------------------------
def _E_caja() -> tuple[float, float]:
    m, L, n = me, 1e-9, 3
    return n ** 2 * h ** 2 / (8 * m * L ** 2), n ** 2 * math.pi ** 2 * hbar ** 2 / (2 * m * L ** 2)


def _x2_caja() -> tuple[float, float]:
    n = 3
    num = quad(lambda x: 2 * x * x * math.sin(n * math.pi * x) ** 2, 0, 1)[0]
    return num, 1 / 3 - 1 / (2 * n ** 2 * math.pi ** 2)


def _dxdp_caja() -> tuple[float, float]:
    n = 2
    x2 = quad(lambda x: 2 * x * x * math.sin(n * math.pi * x) ** 2, 0, 1)[0]
    return math.sqrt(x2 - 0.25) * n * math.pi, 0.5 * math.sqrt(n ** 2 * math.pi ** 2 / 3 - 2)


CAJA = Seccion("caja", "Partícula en una caja",
    "Partícula de masa $m$ confinada en $0\\le x\\le L$ con paredes infinitas ($V=0$ en el interior).", (
    Bloque("Una dimensión", (
        F("Funciones de onda", r"\psi_n(x)=\sqrt{\frac{2}{L}}\,\sin\frac{n\pi x}{L}\qquad n=1,2,3,\dots", "Se anulan en $x=0$ y $x=L$; tienen $n-1$ nodos en el interior."),
        F("Energías", r"E_n=\frac{n^{2}h^{2}}{8mL^{2}}=\frac{n^{2}\pi^{2}\hbar^{2}}{2mL^{2}}", "No hay estado de energía cero: la energía mínima es $E_1=h^2/8mL^2$ (energía de punto cero).", _E_caja, 1e-12),
        F("Separación entre niveles", r"E_{n+1}-E_n=\frac{(2n+1)\,h^{2}}{8mL^{2}}", "Crece con $n$ y disminuye al aumentar $m$ o $L$."),
        F("Transición entre niveles", r"\Delta E=E_{n_2}-E_{n_1}=\frac{(n_2^{2}-n_1^{2})h^{2}}{8mL^{2}}=\frac{hc}{\lambda}", "$\\lambda$: longitud de onda del fotón absorbido o emitido."),
    )),
    Bloque("Valores esperados (una dimensión)", (
        F("Posición", r"\langle x\rangle=\frac{L}{2}\qquad\langle x^{2}\rangle=L^{2}\left(\frac13-\frac{1}{2n^{2}\pi^{2}}\right)", "", _x2_caja, 1e-9),
        F("Momento", r"\langle p\rangle=0\qquad\langle p^{2}\rangle=\frac{n^{2}\pi^{2}\hbar^{2}}{L^{2}}", ""),
        F("Producto de incertidumbres", r"\Delta x\,\Delta p=\frac{\hbar}{2}\sqrt{\frac{n^{2}\pi^{2}}{3}-2}", "Para $n=1$ vale $0.568\\,\\hbar>\\hbar/2$.", _dxdp_caja, 1e-9),
        F("Probabilidad en un intervalo", r"P(x_1\le x\le x_2)=\frac{2}{L}\int_{x_1}^{x_2}\sin^{2}\frac{n\pi x}{L}\,dx", "En el tercio central y con $n=1$ vale $\\tfrac13+\\tfrac{\\sqrt3}{2\\pi}=0.609$."),
    )),
    Bloque("Dos y tres dimensiones", (
        F("Caja rectangular (2D)", r"\psi=\frac{2}{\sqrt{L_xL_y}}\sin\frac{n_x\pi x}{L_x}\sin\frac{n_y\pi y}{L_y}\qquad E=\frac{h^{2}}{8m}\left(\frac{n_x^{2}}{L_x^{2}}+\frac{n_y^{2}}{L_y^{2}}\right)", "Con $L_x=L_y$ aparece degeneración (por ejemplo $E_{1,2}=E_{2,1}$)."),
        F("Caja (3D)", r"E=\frac{h^{2}}{8m}\left(\frac{n_x^{2}}{L_x^{2}}+\frac{n_y^{2}}{L_y^{2}}+\frac{n_z^{2}}{L_z^{2}}\right)", "La energía es la suma de las tres contribuciones independientes (separación de variables)."),
    )),
), "caja")


# ---------------------------------------------------------------------
# Conmutadores e incertidumbre
# ---------------------------------------------------------------------
def _identidad_conmutadores() -> tuple[float, float]:
    rng = np.random.default_rng(1)
    A, B, C = (rng.normal(size=(3, 3)) for _ in range(3))
    com = lambda X, Y: X @ Y - Y @ X
    return float(np.linalg.norm(com(A, B @ C) - (com(A, B) @ C + B @ com(A, C)))), 0.0


def _momento_angular() -> tuple[float, float]:
    s2 = 1 / math.sqrt(2)
    Lx = s2 * np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=complex)
    Ly = s2 * np.array([[0, -1j, 0], [1j, 0, -1j], [0, 1j, 0]])
    Lz = np.diag([1.0, 0.0, -1.0]).astype(complex)
    return float(np.linalg.norm(Lx @ Ly - Ly @ Lx - 1j * Lz)), 0.0


def _gaussiana_minima() -> tuple[float, float]:
    s = 0.8
    psi = lambda x: math.exp(-x * x / (4 * s * s))
    n = quad(lambda x: psi(x) ** 2, -np.inf, np.inf)[0]
    x2 = quad(lambda x: x * x * psi(x) ** 2, -np.inf, np.inf)[0] / n
    p2 = quad(lambda x: (x / (2 * s * s) * psi(x)) ** 2, -np.inf, np.inf)[0] / n     # ⟨p²⟩/ħ² = ∫|ψ'|²
    return math.sqrt(x2 * p2), 0.5


CONMUTADORES = Seccion("conmutadores", "Conmutadores e incertidumbre",
    "Cuándo dos magnitudes se pueden conocer simultáneamente y el límite que impone el principio de incertidumbre.", (
    Bloque("Conmutadores", (
        F("Definición", r"[\hat A,\hat B]=\hat A\hat B-\hat B\hat A", "Si $[\\hat A,\\hat B]=0$, existe un conjunto común de autofunciones y ambas magnitudes se pueden determinar a la vez."),
        F("Posición y momento", r"[\hat x,\hat p_x]=i\hbar", "Al ser distinto de cero, $x$ y $p_x$ no tienen autofunciones comunes."),
        F("Propiedades", r"[\hat A,\hat B]=-[\hat B,\hat A]\qquad[\hat A,\hat B\hat C]=[\hat A,\hat B]\hat C+\hat B[\hat A,\hat C]", "Antisimetría y regla del producto.", _identidad_conmutadores, 1e-9),
        F("Momento angular", r"[\hat L_x,\hat L_y]=i\hbar\hat L_z\ \ \text{(y permutaciones cíclicas)}\qquad[\hat L^{2},\hat L_z]=0", "$\\hat L^2$ y una sola componente se pueden conocer simultáneamente.", _momento_angular, 1e-9),
    )),
    Bloque("Incertidumbre", (
        F("Desviación estándar", r"\sigma_A=\Delta A=\sqrt{\langle A^{2}\rangle-\langle A\rangle^{2}}", ""),
        F("Relación general (Robertson)", r"\sigma_A\,\sigma_B\ge\frac{1}{2}\left|\left\langle[\hat A,\hat B]\right\rangle\right|", ""),
        F("Principio de Heisenberg", r"\Delta x\,\Delta p_x\ge\frac{\hbar}{2}", "Se alcanza la igualdad solo con la gaussiana.", _gaussiana_minima, 1e-7),
        F("Paquete gaussiano", r"\psi(x)\propto e^{-x^{2}/4\sigma^{2}}\qquad\Delta x=\sigma\qquad\Delta p=\frac{\hbar}{2\sigma}", "Es el paquete de mínima incertidumbre."),
        F("Energía y tiempo", r"\Delta E\,\Delta t\gtrsim\frac{\hbar}{2}", "Aquí $\\Delta t$ es un tiempo característico de evolución del sistema, no la desviación estándar de un operador temporal."),
    )),
), "conmutadores")


# ---------------------------------------------------------------------
# Oscilador
# ---------------------------------------------------------------------
def _psi_osc(n: int, alfa: float):
    N = (alfa / math.pi) ** 0.25 / math.sqrt(2.0 ** n * math.factorial(n))
    return lambda x: N * eval_hermite(n, math.sqrt(alfa) * x) * math.exp(-alfa * x * x / 2)


def _norma_osc() -> tuple[float, float]:
    return quad(lambda x: _psi_osc(3, 1.3)(x) ** 2, -np.inf, np.inf)[0], 1.0


def _x2_osc() -> tuple[float, float]:
    n, a = 2, 1.3
    return quad(lambda x: x * x * _psi_osc(n, a)(x) ** 2, -np.inf, np.inf)[0], (2 * n + 1) / (2 * a)


def _hermite_explicitos() -> tuple[float, float]:
    y = 0.7
    explicitos = [1, 2 * y, 4 * y ** 2 - 2, 8 * y ** 3 - 12 * y, 16 * y ** 4 - 48 * y ** 2 + 12]
    return float(np.linalg.norm([explicitos[n] - eval_hermite(n, y) for n in range(5)])), 0.0


def _recurrencia_hermite() -> tuple[float, float]:
    y = 0.7
    return 2 * y * eval_hermite(3, y) - 2 * 3 * eval_hermite(2, y), eval_hermite(4, y)


def _virial_osc() -> tuple[float, float]:
    n, a, mu, w = 2, 1.0, 1.0, 1.0                       # α = μω/ħ = 1 con ħ = μ = ω = 1
    V = 0.5 * mu * w ** 2 * quad(lambda x: x * x * _psi_osc(n, a)(x) ** 2, -np.inf, np.inf)[0]
    return V, 0.5 * w * (n + 0.5)


def _hcl_numero_onda() -> tuple[float, float]:
    mu = _masas.en_kg(_masas.masa_reducida(_masas.ISOTOPOS["¹H"][0], _masas.ISOTOPOS["³⁵Cl"][0]))
    return math.sqrt(516.0 / mu) / (2 * math.pi * c * 100), 2990.0


OSCILADOR = Seccion("oscilador", "Oscilador armónico",
    "Partícula de masa reducida $\\mu$ con $V=\\tfrac12kx^{2}$: modelo de la vibración molecular.", (
    Bloque("Energías y frecuencia", (
        F("Niveles de energía", r"E_n=\hbar\omega\left(n+\tfrac12\right)=h\nu\left(n+\tfrac12\right)\qquad n=0,1,2,\dots", "Niveles equidistantes; energía de punto cero $E_0=\\tfrac12\\hbar\\omega$."),
        F("Frecuencia", r"\omega=\sqrt{\frac{k}{\mu}}\qquad\nu=\frac{\omega}{2\pi}\qquad\tilde\nu=\frac{\nu}{c}=\frac{1}{2\pi c}\sqrt{\frac{k}{\mu}}",
          "$k$: constante de fuerza ($\\mathrm{N/m}$). Ejemplo: H³⁵Cl con $k\\approx516\\ \\mathrm{N/m}$ da $\\tilde\\nu\\approx2990\\ \\mathrm{cm^{-1}}$.", _hcl_numero_onda, 3e-3),
        F("Masa reducida", r"\mu=\frac{m_1m_2}{m_1+m_2}", "Para una molécula diatómica."),
        F("Regla de selección", r"\Delta n=\pm1", "Para el oscilador armónico; la absorción de infrarrojo exige además que cambie el momento dipolar durante la vibración."),
    )),
    Bloque("Funciones de onda", (
        F("Autofunciones", r"\psi_n(x)=N_nH_n\!\left(\sqrt{\alpha}\,x\right)e^{-\alpha x^{2}/2}\qquad\alpha=\frac{\sqrt{k\mu}}{\hbar}=\frac{\mu\omega}{\hbar}", "$H_n$: polinomio de Hermite. La función tiene $n$ nodos."),
        F("Constante de normalización", r"N_n=\left(\frac{1}{2^{n}n!}\sqrt{\frac{\alpha}{\pi}}\right)^{1/2}", "Garantiza $\\int\\psi_n^2\\,dx=1$.", _norma_osc, 1e-7),
        F("Polinomios de Hermite", r"H_0=1,\ H_1=2y,\ H_2=4y^{2}-2,\ H_3=8y^{3}-12y,\ H_4=16y^{4}-48y^{2}+12\qquad y=\sqrt\alpha\,x",
          "", _hermite_explicitos, 1e-9),
        F("Relación de recurrencia", r"H_{n+1}(y)=2y\,H_n(y)-2n\,H_{n-1}(y)", "", _recurrencia_hermite, 1e-9),
    )),
    Bloque("Propiedades", (
        F("Valores esperados", r"\langle x\rangle=0\qquad\langle x^{2}\rangle=\frac{2n+1}{2\alpha}\qquad\langle p\rangle=0\qquad\langle p^{2}\rangle=\left(n+\tfrac12\right)\hbar\mu\omega", "", _x2_osc, 1e-7),
        F("Teorema del virial", r"\langle T\rangle=\langle V\rangle=\frac{E_n}{2}", "Para un potencial cuadrático.", _virial_osc, 1e-7),
        F("Puntos de retorno clásicos", r"x_{\pm}=\pm\sqrt{\frac{2n+1}{\alpha}}", "Donde $E_n=V(x)$; la función de onda se extiende más allá (penetración en la región clásicamente prohibida)."),
    )),
), "oscilador")


# ---------------------------------------------------------------------
# Rotación
# ---------------------------------------------------------------------
def _armonico(l: int, m: int, theta: float, phi: float) -> complex:
    from scipy import special
    if hasattr(special, "sph_harm_y"):
        return complex(special.sph_harm_y(l, m, theta, phi))
    return complex(special.sph_harm(m, l, phi, theta))


def _armonicos_explicitos() -> tuple[float, float]:
    t, p = 0.7, 0.4
    s, co, ex = math.sin(t), math.cos(t), np.exp
    esperado = {
        (0, 0): 1 / math.sqrt(4 * math.pi),
        (1, 0): math.sqrt(3 / (4 * math.pi)) * co,
        (1, 1): -math.sqrt(3 / (8 * math.pi)) * s * ex(1j * p),
        (1, -1): math.sqrt(3 / (8 * math.pi)) * s * ex(-1j * p),
        (2, 0): math.sqrt(5 / (16 * math.pi)) * (3 * co ** 2 - 1),
        (2, 1): -math.sqrt(15 / (8 * math.pi)) * s * co * ex(1j * p),
        (2, -1): math.sqrt(15 / (8 * math.pi)) * s * co * ex(-1j * p),
        (2, 2): math.sqrt(15 / (32 * math.pi)) * s ** 2 * ex(2j * p),
        (2, -2): math.sqrt(15 / (32 * math.pi)) * s ** 2 * ex(-2j * p),
    }
    return float(max(abs(_armonico(l, m, t, p) - v) for (l, m), v in esperado.items())), 0.0


def _B_hcl() -> tuple[float, float]:
    mu = _masas.en_kg(_masas.masa_reducida(_masas.ISOTOPOS["¹H"][0], _masas.ISOTOPOS["³⁵Cl"][0]))
    I = mu * (1.2746e-10) ** 2
    return h / (8 * math.pi ** 2 * c * 100 * I), 10.59


def _ortonormal_Y() -> tuple[float, float]:
    f = lambda t, ph, l1, m1, l2, m2: (_armonico(l1, m1, t, ph).conjugate() * _armonico(l2, m2, t, ph)).real * math.sin(t)
    from scipy.integrate import dblquad
    a = dblquad(lambda ph, t: f(t, ph, 2, 1, 2, 1), 0, math.pi, 0, 2 * math.pi)[0]
    b = dblquad(lambda ph, t: f(t, ph, 2, 0, 1, 0), 0, math.pi, 0, 2 * math.pi)[0]
    return a + abs(b), 1.0


ESFERA = Seccion("esfera", "Rotación y momento angular",
    "Rotor rígido (movimiento sobre una circunferencia o una esfera) y armónicos esféricos.", (
    Bloque("Rotor en un plano (una partícula en un anillo)", (
        F("Funciones y energías", r"\psi_m(\phi)=\frac{1}{\sqrt{2\pi}}e^{im\phi}\qquad E_m=\frac{m^{2}\hbar^{2}}{2I}\qquad m=0,\pm1,\pm2,\dots", "$I=\\mu R^2$. Los niveles $\\pm m$ están doblemente degenerados."),
        F("Momento angular", r"\hat L_z=-i\hbar\frac{\partial}{\partial\phi}\qquad L_z=m\hbar", "La periodicidad $\\psi(\\phi+2\\pi)=\\psi(\\phi)$ exige $m$ entero."),
    )),
    Bloque("Rotor rígido en tres dimensiones", (
        F("Energías", r"E_J=\frac{\hbar^{2}}{2I}J(J+1)=hcB\,J(J+1)\qquad J=0,1,2,\dots\qquad g_J=2J+1", "$g_J$: degeneración (valores de $M_J=-J,\\dots,+J$)."),
        F("Constante rotacional", r"B=\frac{h}{8\pi^{2}cI}\qquad I=\mu R^{2}", "$B$ en $\\mathrm{cm^{-1}}$ si $c$ se toma en $\\mathrm{cm/s}$. Ejemplo: H³⁵Cl ($R=127.46$ pm): $B\\approx10.59\\ \\mathrm{cm^{-1}}$.", _B_hcl, 3e-3),
        F("Espectro de rotación pura", r"\tilde\nu(J\to J+1)=2B(J+1)\qquad\Delta J=\pm1", "Líneas igualmente espaciadas $2B$; la molécula debe tener momento dipolar permanente."),
    )),
    Bloque("Armónicos esféricos", (
        F("Ecuaciones de autovalores", r"\hat L^{2}Y_l^{m}=\hbar^{2}l(l+1)Y_l^{m}\qquad\hat L_zY_l^{m}=m\hbar\,Y_l^{m}\qquad|m|\le l", "Hay $2l+1$ valores de $m$ para cada $l$."),
        F("Magnitud y orientaciones del momento angular", r"|\mathbf L|=\hbar\sqrt{l(l+1)}\qquad\cos\theta=\frac{m}{\sqrt{l(l+1)}}", "Ángulo entre $\\mathbf L$ y el eje $z$ (modelo vectorial); el cono más cercano al eje corresponde a $m=l$."),
        F("Operador $\\hat L^2$", r"\hat L^{2}=-\hbar^{2}\left[\frac{1}{\sin\theta}\frac{\partial}{\partial\theta}\left(\sin\theta\frac{\partial}{\partial\theta}\right)+\frac{1}{\sin^{2}\theta}\frac{\partial^{2}}{\partial\phi^{2}}\right]", ""),
        F("Armónicos con $l=0,1$", r"Y_0^{0}=\frac{1}{\sqrt{4\pi}}\quad Y_1^{0}=\sqrt{\frac{3}{4\pi}}\cos\theta\quad Y_1^{\pm1}=\mp\sqrt{\frac{3}{8\pi}}\sin\theta\,e^{\pm i\phi}", "Convención de fase de Condon–Shortley."),
        F("Armónicos con $l=2$", r"Y_2^{0}=\sqrt{\frac{5}{16\pi}}\left(3\cos^{2}\theta-1\right)\quad Y_2^{\pm1}=\mp\sqrt{\frac{15}{8\pi}}\sin\theta\cos\theta\,e^{\pm i\phi}\quad Y_2^{\pm2}=\sqrt{\frac{15}{32\pi}}\sin^{2}\theta\,e^{\pm2i\phi}",
          "$Y_2^0$ se anula en $\\theta=54.74^\\circ$ y $125.26^\\circ$ (dos conos nodales).", _armonicos_explicitos, 1e-9),
        F("Ortonormalidad", r"\int_0^{2\pi}\!\!\int_0^{\pi}Y_{l'}^{m'*}\,Y_l^{m}\,\sin\theta\,d\theta\,d\phi=\delta_{ll'}\delta_{mm'}", "Elemento de ángulo sólido: $d\\Omega=\\sin\\theta\\,d\\theta\\,d\\phi$.", _ortonormal_Y, 1e-6),
    )),
), "esfera")


# ---------------------------------------------------------------------
# Hidrógeno
# ---------------------------------------------------------------------
_R = {
    "10": lambda r: 2 * math.exp(-r),
    "20": lambda r: (1 / (2 * math.sqrt(2))) * (2 - r) * math.exp(-r / 2),
    "21": lambda r: (1 / (2 * math.sqrt(6))) * r * math.exp(-r / 2),
    "30": lambda r: (2 / (81 * math.sqrt(3))) * (27 - 18 * r + 2 * r * r) * math.exp(-r / 3),
    "31": lambda r: (8 / (27 * math.sqrt(6))) * r * (1 - r / 6) * math.exp(-r / 3),
    "32": lambda r: (4 / (81 * math.sqrt(30))) * r * r * math.exp(-r / 3),
    "42": lambda r: (1 / (64 * math.sqrt(5))) * r * r * (1 - r / 12) * math.exp(-r / 4),
}


def _normas_radiales() -> tuple[float, float]:
    return float(sum(abs(quad(lambda r: r * r * f(r) ** 2, 0, np.inf)[0] - 1) for f in _R.values())), 0.0


def _ortogonales_radiales() -> tuple[float, float]:
    a = quad(lambda r: r * r * _R["10"](r) * _R["20"](r), 0, np.inf)[0]
    b = quad(lambda r: r * r * _R["20"](r) * _R["30"](r), 0, np.inf)[0]
    return abs(a) + abs(b), 0.0


def _r_medio() -> tuple[float, float]:
    n, l = 3, 1
    return quad(lambda r: r ** 3 * _R["31"](r) ** 2, 0, np.inf)[0], 0.5 * (3 * n ** 2 - l * (l + 1))


def _virial_hidrogeno() -> tuple[float, float]:
    V = quad(lambda r: r * r * _R["10"](r) ** 2 * (-1 / r), 0, np.inf)[0]      # en hartree: ⟨V⟩ = −1 = 2E₁
    return V, 2 * (-0.5)


HIDROGENO = Seccion("hidrogeno", "Átomo de hidrógeno",
    "Átomo hidrogenoide (un electrón y un núcleo de carga $Ze$): números cuánticos, funciones radiales y propiedades.", (
    Bloque("Energías y números cuánticos", (
        F("Energías", r"E_n=-\frac{Z^{2}}{n^{2}}\cdot\frac{e^{2}}{8\pi\varepsilon_0a_0}=-\frac{13.606\ \mathrm{eV}}{n^{2}}\,Z^{2}", "Dependen solo de $n$: la degeneración es $n^2$ (sin espín) o $2n^2$ (con espín)."),
        F("Números cuánticos", r"n=1,2,3,\dots\qquad l=0,1,\dots,n-1\qquad m=-l,\dots,+l", "$l=0,1,2,3\\ \\leftrightarrow\\ s,p,d,f$."),
        F("Nodos de un orbital", r"\text{radiales}=n-l-1\qquad\text{angulares}=l\qquad\text{totales}=n-1", "Sin contar el origen ni el infinito."),
        F("Función de onda", r"\psi_{nlm}(r,\theta,\phi)=R_{nl}(r)\,Y_l^{m}(\theta,\phi)", ""),
    )),
    Bloque("Funciones radiales (con $Z=1$ y $a_0=1$; $r$ en unidades de $a_0$)", (
        F("Estados 1s, 2s y 2p", r"R_{10}=2e^{-r}\qquad R_{20}=\tfrac{1}{2\sqrt2}(2-r)\,e^{-r/2}\qquad R_{21}=\tfrac{1}{2\sqrt6}\,r\,e^{-r/2}", "Para $Z>1$: sustituir $r\\to Zr$ y multiplicar por $Z^{3/2}$."),
        F("Estados 3s, 3p y 3d", r"R_{30}=\tfrac{2}{81\sqrt3}\left(27-18r+2r^{2}\right)e^{-r/3}\quad R_{31}=\tfrac{8}{27\sqrt6}\,r\left(1-\tfrac{r}{6}\right)e^{-r/3}\quad R_{32}=\tfrac{4}{81\sqrt{30}}\,r^{2}e^{-r/3}", ""),
        F("Estado 4d", r"R_{42}=\tfrac{1}{64\sqrt5}\,r^{2}\left(1-\tfrac{r}{12}\right)e^{-r/4}", "Su único nodo radial está en $r=12\\,a_0$.", _normas_radiales, 1e-7),
        F("Normalización y ortogonalidad radiales", r"\int_0^\infty R_{nl}^{2}\,r^{2}dr=1\qquad\int_0^\infty R_{nl}R_{n'l}\,r^{2}dr=0\ \ (n\neq n')", "Los $R$ de arriba cumplen $\\int_0^\\infty R^2r^2dr=1$.", _ortogonales_radiales, 1e-7),
    )),
    Bloque("Propiedades", (
        F("Distribución radial de probabilidad", r"P(r)=r^{2}R_{nl}^{2}(r)\qquad P(r_1<r<r_2)=\int_{r_1}^{r_2}r^{2}R_{nl}^{2}\,dr", "$P(r)\\,dr$: probabilidad de hallar al electrón en una capa esférica de espesor $dr$."),
        F("Elemento de volumen", r"d\tau=r^{2}\sin\theta\,dr\,d\theta\,d\phi", ""),
        F("Radio medio", r"\langle r\rangle_{nl}=\frac{a_0}{2Z}\left[3n^{2}-l(l+1)\right]", "Para 1s: $\\langle r\\rangle=\\tfrac32a_0$; el máximo de $P(r)$ está en $a_0$.", _r_medio, 1e-7),
        F("Energía potencial y cinética", r"\langle V\rangle=2E_n\qquad\langle T\rangle=-E_n", "Teorema del virial para el potencial de Coulomb.", _virial_hidrogeno, 1e-7),
        F("Orbitales reales", r"p_z\propto R_{21}\cos\theta\quad p_x\propto R_{21}\sin\theta\cos\phi\quad p_y\propto R_{21}\sin\theta\sin\phi\quad d_{z^2}\propto R_{n2}\left(3\cos^{2}\theta-1\right)",
          "Combinaciones lineales reales de los orbitales complejos con $\\pm m$."),
    )),
), "hidrogeno")


# ---------------------------------------------------------------------
# Espín
# ---------------------------------------------------------------------
def _slater() -> tuple[float, float]:
    f = lambda x: math.exp(-x)
    g = lambda x: x * math.exp(-x)
    D = lambda a, b: (f(a) * g(b) - g(a) * f(b)) / math.sqrt(2)
    return D(0.3, 1.1) + D(1.1, 0.3) + abs(D(0.7, 0.7)), 0.0


ESPIN = Seccion("espin", "Espín y determinantes de Slater",
    "Momento angular intrínseco del electrón y antisimetría de la función de onda de varios electrones.", (
    Bloque("Espín del electrón", (
        F("Autovalores", r"\hat S^{2}\chi=\hbar^{2}s(s+1)\chi\qquad\hat S_z\chi=m_s\hbar\chi\qquad s=\tfrac12\qquad m_s=\pm\tfrac12", "Las funciones de espín se denotan $\\alpha$ ($m_s=+\\tfrac12$) y $\\beta$ ($m_s=-\\tfrac12$)."),
        F("Magnitud del espín", r"|\mathbf S|=\hbar\sqrt{s(s+1)}=\frac{\sqrt3}{2}\hbar", ""),
        F("Espín-orbital", r"\chi_{nlm\,m_s}(\mathbf r,\sigma)=\psi_{nlm}(\mathbf r)\,\sigma(m_s)", "Producto de un orbital espacial por una función de espín."),
    )),
    Bloque("Principio de Pauli", (
        F("Antisimetría", r"\Psi(1,2,\dots)=-\Psi(2,1,\dots)", "La función de onda de electrones cambia de signo al intercambiar las coordenadas (espaciales y de espín) de dos de ellos."),
        F("Determinante de Slater", r"\Psi=\frac{1}{\sqrt{N!}}\begin{vmatrix}\chi_1(1)&\chi_2(1)&\cdots&\chi_N(1)\\\chi_1(2)&\chi_2(2)&\cdots&\chi_N(2)\\\vdots&\vdots&&\vdots\\\chi_1(N)&\chi_2(N)&\cdots&\chi_N(N)\end{vmatrix}",
          "Filas: electrones; columnas: espín-orbitales. Dos espín-orbitales iguales anulan el determinante (principio de exclusión).", _slater, 1e-9),
        F("Helio: hamiltoniano", r"\hat H=-\frac{\hbar^{2}}{2m_e}\left(\nabla_1^{2}+\nabla_2^{2}\right)-\frac{Ze^{2}}{4\pi\varepsilon_0}\left(\frac{1}{r_1}+\frac{1}{r_2}\right)+\frac{e^{2}}{4\pi\varepsilon_0r_{12}}",
          "El último término (repulsión electrónica) impide una solución exacta; se recurre a métodos aproximados."),
        F("Multiplicidad de espín", r"2S+1\qquad S=\sum_i m_{s,i}\ \text{(máximo)}", "Singlete ($S=0$), doblete ($S=\\tfrac12$), triplete ($S=1$)."),
    )),
), "espin")


# ---------------------------------------------------------------------
# Métodos aproximados
# ---------------------------------------------------------------------
def _huckel_alilo() -> tuple[float, float]:
    x = np.sort(np.linalg.eigvalsh(np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)))
    return float(np.linalg.norm(x - np.array([-math.sqrt(2), 0.0, math.sqrt(2)]))), 0.0


def _lcao_dos_orbitales() -> tuple[float, float]:
    a, b, s = -0.5, -0.3, 0.25
    w = eigh(np.array([[a, b], [b, a]]), np.array([[1, s], [s, 1]]), eigvals_only=True)
    return float(np.linalg.norm(np.sort(w) - np.sort([(a + b) / (1 + s), (a - b) / (1 - s)]))), 0.0


def _perturbacion_2() -> tuple[float, float]:
    v = 0.01
    exacto = 0.5 * (1 - math.sqrt(1 + 4 * v * v)) - 0.0              # nivel inferior de [[0, v], [v, 1]]
    return -v * v / (1 - 0), exacto


APROXIMADOS = Seccion("aproximados", "Métodos aproximados",
    "Método variacional, ecuación secular, Hückel y teoría de perturbaciones.", (
    Bloque("Método variacional", (
        F("Teorema variacional", r"E[\phi]=\frac{\int\phi^{*}\hat H\phi\,d\tau}{\int\phi^{*}\phi\,d\tau}\ \ge\ E_0", "La energía calculada con cualquier función de prueba admisible es una cota superior de la energía del estado fundamental. Se minimiza respecto de los parámetros de $\\phi$."),
        F("Combinación lineal de funciones base", r"\phi=\sum_{i}c_i\chi_i\qquad\det\left(H_{ij}-ES_{ij}\right)=0", "$H_{ij}=\\int\\chi_i^{*}\\hat H\\chi_j\\,d\\tau$ y $S_{ij}=\\int\\chi_i^{*}\\chi_j\\,d\\tau$. Las raíces $E$ son cotas superiores de los niveles exactos."),
    )),
    Bloque("Hückel y orbitales moleculares", (
        F("Hückel simple", r"H_{ii}=\alpha\qquad H_{ij}=\beta\ \text{(átomos enlazados)}\ \text{o }0\qquad S_{ij}=\delta_{ij}", "$\\alpha$: integral de Coulomb; $\\beta$ (negativa): integral de resonancia. Si $E=\\alpha+x\\beta$, las $x$ son los autovalores de la matriz de conectividad.", _huckel_alilo, 1e-9),
        F("Alilo", r"E=\alpha+\sqrt2\,\beta\ ,\ \ \alpha\ ,\ \ \alpha-\sqrt2\,\beta", "Como $\\beta<0$, el orbital de menor energía es el de $x=+\\sqrt2$."),
        F("Dos orbitales atómicos (con solapamiento)", r"E_{\pm}=\frac{H_{AA}\pm H_{AB}}{1\pm S}\qquad\psi_{\pm}=\frac{1}{\sqrt{2(1\pm S)}}\left(\phi_A\pm\phi_B\right)", "Para dos orbitales equivalentes; $+$: enlazante, $-$: antienlazante.", _lcao_dos_orbitales, 1e-9),
    )),
    Bloque("Teoría de perturbaciones", (
        F("Corrección de primer orden", r"E_n^{(1)}=\langle\psi_n^{(0)}|\hat H'|\psi_n^{(0)}\rangle", "$\\hat H=\\hat H^{(0)}+\\hat H'$ con $\\hat H'$ pequeño."),
        F("Corrección de segundo orden", r"E_n^{(2)}=\sum_{k\neq n}\frac{\left|\langle\psi_k^{(0)}|\hat H'|\psi_n^{(0)}\rangle\right|^{2}}{E_n^{(0)}-E_k^{(0)}}", "Rebaja el nivel más bajo, pues todos los demás denominadores son negativos.", _perturbacion_2, 1e-3),
    )),
), "aproximados")


# ---------------------------------------------------------------------
# Moléculas y espectroscopía
# ---------------------------------------------------------------------
def _j_mas_poblado() -> tuple[float, float]:
    B, T = 10.59, 298.15
    t = kB * T / (h * c * 100)                                 # k_BT/hc en cm⁻¹
    f = lambda J: 2 - (2 * J + 1) ** 2 * B / t                 # derivada de ln[(2J+1)e^{−BJ(J+1)/t}] × (2J+1)
    return brentq(f, 0, 50), math.sqrt(t / (2 * B)) - 0.5


def _ramas_vib_rot() -> tuple[float, float]:
    B, v0 = 10.59, 2886.0
    F_ = lambda J: B * J * (J + 1)
    R = v0 + F_(3) - F_(2)
    P = v0 + F_(1) - F_(2)
    return (R - v0) + (v0 - P), 2 * B * 3 + 2 * B * 2


MOLECULARES = Seccion("orbitales_moleculares", "Moléculas y espectroscopía",
    "Aproximación de Born–Oppenheimer, orbitales moleculares y espectros de rotación y vibración de moléculas diatómicas.", (
    Bloque("Aproximación de Born–Oppenheimer", (
        F("Separación de movimientos", r"\Psi(\mathbf r,\mathbf R)\approx\psi_{\text{el}}(\mathbf r;\mathbf R)\,\chi_{\text{nuc}}(\mathbf R)", "Los núcleos, mucho más pesados, se mueven lentamente respecto de los electrones: estos se ajustan a cada configuración nuclear."),
        F("Energía total", r"E\approx E_{\text{el}}+E_{\text{vib}}+E_{\text{rot}}", "Órdenes de magnitud: electrónica, 1–10 eV; vibración, 0.05–0.5 eV; rotación, $10^{-4}$–$10^{-2}$ eV."),
    )),
    Bloque("Orbitales moleculares", (
        F("Combinación lineal de orbitales atómicos", r"\psi_{\pm}=c_A\phi_A\pm c_B\phi_B", "Enlazante (aumenta la densidad entre los núcleos) y antienlazante (nodo entre los núcleos)."),
        F("Orden de enlace", r"\text{O.E.}=\tfrac12\left(n_{\text{enlazantes}}-n_{\text{antienlazantes}}\right)", "Un orden mayor que cero indica una molécula estable en este modelo (por ejemplo, O₂: 2)."),
    )),
    Bloque("Espectroscopía de rotación y vibración", (
        F("Términos de rotación", r"F(J)=BJ(J+1)\qquad\tilde\nu(J\to J+1)=2B(J+1)", "$B$ en $\\mathrm{cm^{-1}}$."),
        F("Vibración-rotación (rotor rígido y oscilador armónico)", r"\tilde\nu_R(J)=\tilde\nu_0+2B(J+1)\qquad\tilde\nu_P(J)=\tilde\nu_0-2BJ", "$J$ es el número cuántico del nivel inferior; las ramas R ($\\Delta J=+1$) y P ($\\Delta J=-1$) quedan a ambos lados del hueco central $\\tilde\\nu_0$.", _ramas_vib_rot, 1e-9),
        F("Población de los niveles rotacionales", r"N_J\propto(2J+1)\,e^{-BJ(J+1)hc/k_BT}\qquad J_{\max}=\sqrt{\frac{k_BT}{2hcB}}-\frac12", "Nivel más poblado (valor continuo; el entero más próximo es el nivel real).", _j_mas_poblado, 1e-8),
    )),
), "orbitales_moleculares")


# ---------------------------------------------------------------------
# Matemática
# ---------------------------------------------------------------------
MATEMATICAS = Seccion("matematicas", "Matemática de uso frecuente",
    "Integrales, identidades y coordenadas que aparecen en los ejercicios.", (
    Bloque("Integrales", (
        F("Gaussiana", r"\int_{-\infty}^{\infty}e^{-ax^{2}}dx=\sqrt{\frac{\pi}{a}}\qquad\int_{-\infty}^{\infty}x^{2}e^{-ax^{2}}dx=\frac{1}{2}\sqrt{\frac{\pi}{a^{3}}}", "$a>0$; las integrales de potencias impares son nulas por simetría.",
          lambda: (quad(lambda x: x * x * math.exp(-1.7 * x * x), -np.inf, np.inf)[0], 0.5 * math.sqrt(math.pi / 1.7 ** 3)), 1e-8),
        F("Exponencial con potencia", r"\int_0^\infty x^{n}e^{-ax}\,dx=\frac{n!}{a^{n+1}}", "$a>0$, $n$ entero no negativo. Útil en la parte radial del hidrógeno.",
          lambda: (quad(lambda x: x ** 3 * math.exp(-2.5 * x), 0, np.inf)[0], math.factorial(3) / 2.5 ** 4), 1e-8),
        F("Producto de senos en una caja", r"\int_0^{L}\sin\frac{m\pi x}{L}\sin\frac{n\pi x}{L}\,dx=\frac{L}{2}\,\delta_{mn}", "",
          lambda: (quad(lambda x: math.sin(2 * math.pi * x) ** 2, 0, 1)[0], 0.5), 1e-9),
        F("Integrales angulares", r"\int_0^{\pi}\sin\theta\,d\theta=2\qquad\int_0^{2\pi}e^{i(m-n)\phi}d\phi=2\pi\,\delta_{mn}\qquad\int_{-1}^{1}u^{2}du=\frac23", "Con $u=\\cos\\theta$ se cumple $\\sin\\theta\\,d\\theta=-du$.",
          lambda: (quad(math.sin, 0, math.pi)[0], 2.0), 1e-9),
    )),
    Bloque("Identidades y desarrollos", (
        F("Ángulo doble", r"\sin^{2}u=\frac{1-\cos2u}{2}\qquad\cos^{2}u=\frac{1+\cos2u}{2}\qquad\sin2u=2\sin u\cos u", "",
          lambda: (math.sin(0.9) ** 2, (1 - math.cos(1.8)) / 2), 1e-12),
        F("Series de Taylor", r"e^{x}\approx1+x+\frac{x^{2}}{2}\qquad\sin x\approx x-\frac{x^{3}}{6}\qquad\cos x\approx1-\frac{x^{2}}{2}\qquad(1+x)^{p}\approx1+px", "Para $|x|\\ll1$.",
          lambda: (math.exp(0.01), 1 + 0.01 + 0.01 ** 2 / 2), 1e-6),
        F("Derivación", r"\frac{d}{dx}e^{ax^{2}}=2ax\,e^{ax^{2}}\qquad\frac{d}{dx}\left[f(x)g(x)\right]=f'g+fg'", "",
          lambda: ((math.exp(1.3 * (0.5 + 1e-6) ** 2) - math.exp(1.3 * (0.5 - 1e-6) ** 2)) / 2e-6, 2 * 1.3 * 0.5 * math.exp(1.3 * 0.25)), 1e-6),
    )),
    Bloque("Coordenadas esféricas", (
        F("Definición", r"x=r\sin\theta\cos\phi\qquad y=r\sin\theta\sin\phi\qquad z=r\cos\theta\qquad r\ge0,\ 0\le\theta\le\pi,\ 0\le\phi<2\pi", ""),
        F("Laplaciano", r"\nabla^{2}=\frac{1}{r^{2}}\frac{\partial}{\partial r}\left(r^{2}\frac{\partial}{\partial r}\right)-\frac{\hat L^{2}}{\hbar^{2}r^{2}}", "Con $\\hat L^2$ el operador de momento angular al cuadrado."),
    )),
), "")
