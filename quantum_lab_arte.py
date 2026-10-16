"""
quantum_lab_arte.py — Ilustraciones SVG de QUANTUM LAB
======================================================

Ilustraciones **conceptuales** (decorativas) de cada simulador y de la portada. Son SVG generados aquí mismo con los colores de
`quantum_lab_tema`; no dependen de imágenes externas ni de conexión a Internet y pesan pocos kilobytes.

Aunque son decorativas, las curvas usan las funciones físicas correctas (ψₙ de la caja, polinomios de Hermite, |P₂(cos θ)|²,
densidad r² e^(−r) cos²θ del orbital 2p, longitudes de onda de Balmer). No representan resultados de ningún cálculo del simulador, y así
se indica en el texto alternativo y en el pie de la portada.

    ILUSTRACIONES   {clave de página: función() → SVG}     (una por simulador)
    portada()       ilustración principal de la página de inicio
    svg(clave)      SVG listo para incrustar, o "" si la página no tiene ilustración
"""

from __future__ import annotations

import math
import re

import numpy as np
from numpy.polynomial import hermite as _herm

from quantum_lab_tema import MAGENTA, PALETA as P, SERIES as S

ANCHO, ALTO = 360, 200
_FUENTE = "system-ui, 'Segoe UI', Roboto, sans-serif"


# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------
def _n(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def _camino(xs, ys, cerrar: bool = False) -> str:
    d = "M" + " L".join(f"{_n(x)} {_n(y)}" for x, y in zip(xs, ys))
    return d + (" Z" if cerrar else "")


def _linea(xs, ys, color, ancho=2.0, op=1.0, extra="") -> str:
    # Los trazos continuos llevan class="ql-trazo" y pathLength="1": el CSS puede «dibujarlos» (stroke-dashoffset 1 → 0) al entrar
    # en una página o al pasar el cursor por una tarjeta. Los discontinuos no, porque pathLength reescalaría su patrón de guiones.
    trazo = '' if "stroke-dasharray" in extra else ' class="ql-trazo" pathLength="1"'
    return f'<path d="{_camino(xs, ys)}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-opacity="{op}" stroke-linejoin="round"{trazo} {extra}/>'


def _area(xs, ys, base, color, op=0.25) -> str:
    return f'<path d="{_camino(xs, ys)} L{_n(xs[-1])} {_n(base)} L{_n(xs[0])} {_n(base)} Z" fill="{color}" fill-opacity="{op}" stroke="none"/>'


def _texto(x, y, txt, color=None, tam=11, ancla="middle", peso=500) -> str:
    return (f'<text x="{_n(x)}" y="{_n(y)}" fill="{color or P["tenue"]}" font-size="{tam}" font-family="{_FUENTE}" '
            f'font-weight="{peso}" text-anchor="{ancla}">{txt}</text>')


def _numerar_trazos(contenido: str) -> str:
    """Añade --i (orden de aparición) a cada trazo animable, para que el CSS los dibuje uno tras otro como una secuencia."""
    contador = iter(range(1, 10_000))
    return re.sub(r'class="ql-trazo"', lambda m: f'class="ql-trazo" style="--i:{next(contador)}"', contenido)


def _envolver(contenido: str, titulo: str, ancho=ANCHO, alto=ALTO) -> str:
    contenido = _numerar_trazos(contenido)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" role="img" aria-label="{titulo}" preserveAspectRatio="xMidYMid meet">'
            f'<title>{titulo}</title>{contenido}</svg>')


def _flecha(x1, y1, x2, y2, color, ancho=1.6) -> str:
    ang = math.atan2(y2 - y1, x2 - x1)
    a1, a2 = ang + math.radians(150), ang - math.radians(150)
    p = f"M{_n(x2)} {_n(y2)} L{_n(x2 + 7 * math.cos(a1))} {_n(y2 + 7 * math.sin(a1))} M{_n(x2)} {_n(y2)} L{_n(x2 + 7 * math.cos(a2))} {_n(y2 + 7 * math.sin(a2))}"
    return (f'<path d="M{_n(x1)} {_n(y1)} L{_n(x2)} {_n(y2)}" stroke="{color}" stroke-width="{ancho}" fill="none"/>'
            f'<path d="{p}" stroke="{color}" stroke-width="{ancho}" fill="none" stroke-linecap="round"/>')


def _onda_fotonica(x1, y1, x2, y2, color, amp=4.0, ciclos=5) -> str:
    """Onda sinusoidal entre dos puntos (representa un fotón)."""
    t = np.linspace(0, 1, 60)
    dx, dy = x2 - x1, y2 - y1
    largo = math.hypot(dx, dy)
    nx, ny = -dy / largo, dx / largo
    off = amp * np.sin(2 * math.pi * ciclos * t) * np.minimum(1, 6 * t) * np.minimum(1, 6 * (1 - t))
    return _linea(x1 + dx * t + nx * off, y1 + dy * t + ny * off, color, 1.8)


# ---------------------------------------------------------------------
# Simuladores
# ---------------------------------------------------------------------
def caja() -> str:
    x0, x1, suelo = 44, 316, 176
    x = np.linspace(x0, x1, 160)
    u = (x - x0) / (x1 - x0)
    partes = [f'<path d="M{x0} 18 V{suelo} H{x1} V18" fill="none" stroke="{P["tenue"]}" stroke-width="2.2" stroke-linejoin="round"/>']
    for n, nivel in ((1, 150), (2, 112), (3, 62)):
        partes.append(f'<line x1="{x0}" y1="{nivel}" x2="{x1}" y2="{nivel}" stroke="{P["amarillo"]}" stroke-width="1" stroke-dasharray="4 4" stroke-opacity=".7"/>')
        psi = math.sqrt(2) * np.sin(n * math.pi * u)
        partes.append(_area(x, nivel - 17 * psi ** 2, nivel, S["densidad"], 0.22))
        partes.append(_linea(x, nivel - 17 * psi, S["onda"], 2.2))
        partes.append(_texto(x0 - 8, nivel + 4, f"n={n}", P["amarillo"], 10, "end"))
        for k in range(1, n):
            partes.append(f'<circle cx="{_n(x0 + (x1 - x0) * k / n)}" cy="{nivel}" r="2.6" fill="{P["fondo"]}" stroke="{P["cian"]}" stroke-width="1.4"/>')
    partes.append(_texto((x0 + x1) / 2, 194, "V = 0 en el interior, V → ∞ en las paredes", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: partícula en una caja con tres estados estacionarios, sus nodos y densidades de probabilidad")


def oscilador() -> str:
    x = np.linspace(-3.3, 3.3, 220)
    sx, base = 38, 182
    X = 180 + sx * x
    # potencial V = ½ x² en unidades de ħω (altura: E / escala)
    V = 0.5 * x ** 2
    partes = [_linea(X, base - 30 * V, P["tenue"], 2.2)]
    for n in range(3):
        E = n + 0.5
        yl = base - 30 * E
        xt = math.sqrt(2 * E)
        partes.append(f'<line x1="{_n(180 - sx * xt)}" y1="{_n(yl)}" x2="{_n(180 + sx * xt)}" y2="{_n(yl)}" stroke="{S["energia"]}" stroke-width="1" stroke-dasharray="4 4" stroke-opacity=".8"/>')
        coef = np.zeros(n + 1); coef[n] = 1
        psi = _herm.hermval(x, coef) * np.exp(-x ** 2 / 2) / math.sqrt(2 ** n * math.factorial(n) * math.sqrt(math.pi))
        partes.append(_area(X, yl - 70 * psi ** 2, yl, S["densidad"], 0.2))
        partes.append(_linea(X, yl - 34 * psi, S["onda"], 2))
        partes.append(_texto(180 - sx * 3.3 - 4, yl + 4, f"n={n}", S["energia"], 10, "end"))
    partes.append(_texto(180, 197, "V = ½ mω²x²   ·   Eₙ = ħω(n + ½)", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: potencial parabólico del oscilador armónico con tres niveles, funciones de onda y densidades")


def esfera() -> str:
    cx, cy, R = 180, 98, 78
    th = np.linspace(0, 2 * math.pi, 240)
    partes = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{P["tenue"]}" stroke-width="2"/>',
              f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{R * 0.3}" fill="none" stroke="{P["borde"]}" stroke-width="1.4"/>',
              f'<ellipse cx="{cx}" cy="{cy}" rx="{R * 0.3}" ry="{R}" fill="none" stroke="{P["borde"]}" stroke-width="1.4"/>']
    # |P2(cos θ)|² = ((3cos²θ − 1)/2)²: lóbulos polares y anillo ecuatorial (θ medido desde el eje z, vertical)
    r = 0.95 * R * ((3 * np.cos(th) ** 2 - 1) / 2) ** 2 / 1.0
    r = np.clip(r, 0, None)
    xs, ys = cx + r * np.sin(th), cy - r * np.cos(th)
    partes.append(f'<path d="{_camino(xs, ys, True)}" fill="{S["onda"]}" fill-opacity=".38" stroke="{S["onda"]}" stroke-width="2" class="ql-trazo" pathLength="1"/>')
    partes.append(f'<line x1="{cx}" y1="{cy - R - 10}" x2="{cx}" y2="{cy + R + 10}" stroke="{P["tenue"]}" stroke-width="1" stroke-dasharray="3 4"/>')
    partes.append(_texto(cx + 8, cy - R - 12, "z", P["tenue"], 11, "start"))
    partes.append(_texto(cx, 197, "Yₗᵐ(θ, φ) sobre la esfera  ·  ejemplo: |Y₂⁰|²", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: dominio esférico y distribución angular de un armónico esférico")


def fotoelectrico() -> str:
    partes = [f'<rect x="30" y="140" width="300" height="34" rx="4" fill="{P["borde"]}" stroke="{P["tenue"]}" stroke-width="1.2"/>',
              _texto(180, 162, "superficie metálica  (función de trabajo Φ)", P["tenue"], 11)]
    for x in (104, 156, 208):
        partes.append(_onda_fotonica(x - 34, 18, x, 126, S["energia"], 4.5, 6))
        partes.append(f'<circle cx="{x}" cy="132" r="3" fill="{S["energia"]}"/>')
    partes.append(_texto(16, 60, "fotones", S["energia"], 11, "start", 600)); partes.append(_texto(16, 74, "hν", S["energia"], 11, "start", 600))
    for x, dy in ((256, 70), (292, 52), (326, 84)):
        partes.append(_flecha(x - 14, 134, x + 18, 134 - dy, P["cian"], 1.8))
        partes.append(f'<circle cx="{x - 14}" cy="134" r="4.5" fill="{P["cian"]}"/>')
    partes.append(_texto(344, 22, "electrones emitidos", P["cian"], 11, "end", 600))
    partes.append(_texto(344, 38, "K_máx = hν − Φ", P["texto"], 11, "end"))
    partes.append(_texto(180, 195, "emisión solo si hν ≥ Φ", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: fotones incidiendo sobre un metal y electrones emitidos")


def bohr() -> str:
    from quantum_lab_comun import color_longitud_onda
    cx, cy = 100, 96
    partes = []
    for n in (1, 2, 3):
        partes.append(f'<circle cx="{cx}" cy="{cy}" r="{8 * n * n}" fill="none" stroke="{P["borde"] if n != 2 else P["tenue"]}" stroke-width="1.6" stroke-dasharray="{"" if n == 2 else "3 4"}"/>')
        partes.append(_texto(cx + 8 * n * n * 0.71 + 6, cy - 8 * n * n * 0.71 - 2, f"n={n}", P["tenue"], 9, "start"))
    partes.append(f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="{P["amarillo"]}"/>')
    partes.append(f'<circle cx="{cx + 32}" cy="{cy}" r="4.5" fill="{P["cian"]}"/>')
    partes.append(f'<path d="M{cx + 51} {cy - 30} Q{cx + 40} {cy - 14} {cx + 34} {cy - 6}" stroke="{P["tenue"]}" stroke-width="1.4" fill="none" stroke-dasharray="2 3"/>')
    partes.append(_onda_fotonica(cx + 56, cy - 36, 242, 34, S["energia"], 3.5, 4))
    partes.append(_texto(250, 36, "hν", S["energia"], 11, "start", 600))
    # espectro de emisión (serie de Balmer, longitudes de onda en nm)
    sx0, sx1, sy0, sy1 = 214, 340, 118, 168
    partes.append(f'<rect x="{sx0}" y="{sy0}" width="{sx1 - sx0}" height="{sy1 - sy0}" rx="3" fill="{P["fondo"]}" stroke="{P["borde"]}" stroke-width="1.2"/>')
    for lam in (656.28, 486.13, 434.05, 410.17):
        x = sx0 + (lam - 380) / (720 - 380) * (sx1 - sx0)
        partes.append(f'<line x1="{_n(x)}" y1="{sy0 + 4}" x2="{_n(x)}" y2="{sy1 - 4}" stroke="{color_longitud_onda(lam)}" stroke-width="2.4"/>')
    partes.append(_texto((sx0 + sx1) / 2, sy1 + 14, "espectro de emisión (Balmer)", P["tenue"], 10))
    partes.append(_texto(sx0, sy0 - 5, "380 nm", P["tenue"], 8, "start")); partes.append(_texto(sx1, sy0 - 5, "720 nm", P["tenue"], 8, "end"))
    partes.append(_texto(cx, 190, "Eₙ = −13.6 eV / n²", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: niveles del átomo de hidrógeno, una transición con emisión de un fotón y las líneas de Balmer")


def incertidumbre() -> str:
    def gauss(x, mu, sigma):
        return np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    xa, xb = np.linspace(20, 170, 160), np.linspace(190, 340, 160)
    base = 150
    estrecha, ancha = gauss(xa, 95, 12), gauss(xb, 265, 38)
    partes = [f'<line x1="20" y1="{base}" x2="170" y2="{base}" stroke="{P["tenue"]}" stroke-width="1.2"/>',
              f'<line x1="190" y1="{base}" x2="340" y2="{base}" stroke="{P["tenue"]}" stroke-width="1.2"/>',
              _area(xa, base - 100 * estrecha, base, S["densidad"], 0.22), _linea(xa, base - 100 * estrecha, S["onda"], 2.4),
              _area(xb, base - 100 * ancha, base, S["densidad"], 0.22), _linea(xb, base - 100 * ancha, S["onda"], 2.4)]
    partes.append(_flecha(83, 40, 107, 40, P["amarillo"], 1.5)); partes.append(_flecha(107, 40, 83, 40, P["amarillo"], 1.5))
    partes.append(_flecha(227, 40, 303, 40, P["amarillo"], 1.5)); partes.append(_flecha(303, 40, 227, 40, P["amarillo"], 1.5))
    partes.append(_texto(95, 30, "Δx", P["amarillo"], 12, peso=600)); partes.append(_texto(265, 30, "Δp", P["amarillo"], 12, peso=600))
    partes.append(_texto(95, 168, "posición x", P["tenue"], 10)); partes.append(_texto(265, 168, "momento p", P["tenue"], 10))
    partes.append(_texto(180, 192, "Δx · Δp ≥ ħ / 2", P["texto"], 12, peso=600))
    return _envolver("".join(partes), "Ilustración conceptual: paquete estrecho en posición y ancho en momento, con el límite de Heisenberg")


def _caja_texto(x, y, w, h, color=None, rx=6, relleno=None) -> str:
    return f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="{rx}" fill="{relleno or "none"}" stroke="{color or P["borde"]}" stroke-width="1.4"/>'


def _lineas_texto(x, y, ancho, n, paso=11, color=None) -> str:
    color = color or P["borde"]
    return "".join(f'<line x1="{_n(x)}" y1="{_n(y + i * paso)}" x2="{_n(x + ancho * (0.55 if i == n - 1 else 1))}" y2="{_n(y + i * paso)}" stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>' for i in range(n))


def ruta() -> str:
    """Grafo de dependencias entre los temas, calculado con los prerrequisitos reales de la Ruta de estudio."""
    from ejercicios import _ruta
    prof: dict[str, int] = {}
    for t in _ruta.ORDEN:
        prof[t] = 1 + max((prof[q] for q in _ruta.PREREQ[t]), default=-1)
    niveles = max(prof.values()) + 1
    columnas: dict[int, list[str]] = {}
    for t in _ruta.ORDEN:
        columnas.setdefault(prof[t], []).append(t)
    pos = {}
    for d, temas in columnas.items():
        for i, t in enumerate(temas):
            pos[t] = (34 + d * (292 / (niveles - 1)), 100 + (i - (len(temas) - 1) / 2) * 38)
    partes = []
    for t in _ruta.ORDEN:
        for q in _ruta.PREREQ[t]:
            (x1, y1), (x2, y2) = pos[q], pos[t]
            partes.append(f'<path d="M{_n(x1)} {_n(y1)} C{_n((x1 + x2) / 2)} {_n(y1)} {_n((x1 + x2) / 2)} {_n(y2)} {_n(x2)} {_n(y2)}" fill="none" stroke="{P["borde"]}" stroke-width="1.6"/>')
    for t, (x, y) in pos.items():
        raiz = not _ruta.PREREQ[t]
        partes.append(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="7" fill="{P["panel"]}" stroke="{P["violeta"] if raiz else P["cian"]}" stroke-width="2"/>')
    partes.append(_texto(180, 192, "temas y prerrequisitos (orden de dependencias)", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: grafo de dependencias entre los temas de la ruta de estudio")


def teoria() -> str:
    x = np.linspace(40, 168, 80)
    partes = [f'<path d="M180 40 C150 30 90 30 40 40 V158 C90 148 150 148 180 158 Z" fill="{P["fondo"]}" stroke="{P["tenue"]}" stroke-width="1.8"/>',
              f'<path d="M180 40 C210 30 270 30 320 40 V158 C270 148 210 148 180 158 Z" fill="{P["fondo"]}" stroke="{P["tenue"]}" stroke-width="1.8"/>',
              _linea(x, 96 - 26 * np.sin((x - 40) / 128 * 3 * math.pi) * np.sin((x - 40) / 128 * math.pi) ** 0.5, S["onda"], 2.4),
              f'<line x1="44" y1="96" x2="172" y2="96" stroke="{P["borde"]}" stroke-width="1" stroke-dasharray="3 4"/>',
              _texto(250, 70, "Ĥψ = Eψ", P["texto"], 18, peso=600), _lineas_texto(200, 92, 100, 4), _lineas_texto(200, 140, 70, 1),
              _texto(180, 190, "teoría de cada tema, con su simulador", P["tenue"], 10)]
    return _envolver("".join(partes), "Ilustración conceptual: libro abierto con una función de onda y la ecuación de Schrödinger")


def formulario() -> str:
    partes = []
    constantes = (("h", "6.626×10⁻³⁴ J s"), ("c", "2.998×10⁸ m/s"), ("ħ", "1.055×10⁻³⁴ J s"), ("k_B", "1.381×10⁻²³ J/K"))
    for i, (sim, val) in enumerate(constantes):
        y = 30 + i * 32
        partes.append(_caja_texto(24, y, 190, 26, P["borde"], 5, P["panel"]))
        partes.append(_texto(40, y + 18, sim, P["violeta"], 14, "start", 700)); partes.append(_texto(206, y + 18, val, P["tenue"], 10, "end"))
    partes.append(_flecha(224, 99, 262, 99, P["cian"], 1.8))
    for i, u in enumerate(("eV", "cm⁻¹", "nm", "kJ/mol")):
        partes.append(_caja_texto(268, 30 + i * 32, 70, 26, P["cian"], 5)); partes.append(_texto(303, 48 + i * 32, u, P["texto"], 11, peso=600))
    partes.append(_texto(180, 192, "constantes, conversiones y fórmulas", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: constantes fundamentales y conversión entre unidades de energía")


def talleres() -> str:
    partes = [_caja_texto(60, 12, 190, 164, P["tenue"], 8, P["panel"]), _lineas_texto(78, 36, 150, 3),
              _texto(78, 92, "a)", P["texto"], 12, "start", 600), _caja_texto(98, 80, 130, 16, P["cian"], 4),
              _texto(78, 120, "b)", P["texto"], 12, "start", 600), _caja_texto(98, 108, 130, 16, P["cian"], 4),
              _texto(78, 148, "c)", P["texto"], 12, "start", 600), _caja_texto(98, 136, 130, 16, P["cian"], 4)]
    partes.append(f'<g transform="rotate(38 300 70)"><rect x="288" y="20" width="14" height="96" rx="3" fill="{P["amarillo"]}"/><path d="M288 116h14l-7 16z" fill="{P["tenue"]}"/></g>')
    partes.append(_texto(180, 197, "preguntas por partes con resultado numérico", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: hoja de taller con preguntas por partes y un lápiz")


def ejercicios() -> str:
    partes = []
    for i, (txt, col) in enumerate((("Paso 1 · Planteamiento", P["cian"]), ("Paso 2 · Desarrollo", P["cian"]), ("Paso 3 · Resultado", P["verde"]))):
        y = 22 + i * 52
        partes.append(_caja_texto(30, y, 210, 40, col, 7, P["panel"]))
        partes.append(_texto(46, y + 25, txt, P["texto"], 12, "start", 600))
        if i < 2:
            partes.append(_flecha(135, y + 41, 135, y + 51, P["tenue"], 1.4))
    partes.append(f'<circle cx="300" cy="62" r="22" fill="{P["panel"]}" stroke="{P["amarillo"]}" stroke-width="2"/><path d="M292 70h16M294 76h12M300 44a12 12 0 0 0-7 22h14a12 12 0 0 0-7-22z" fill="none" stroke="{P["amarillo"]}" stroke-width="1.8" stroke-linecap="round" transform="translate(0 -2)"/>')
    partes.append(_texto(300, 104, "pistas", P["amarillo"], 11, peso=600))
    partes.append(_texto(180, 197, "solución explicada paso a paso", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: solución en tres pasos y una pista")


def examen() -> str:
    cx, cy, R = 110, 100, 62
    th = np.linspace(0, 2 * math.pi, 120)
    partes = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{P["panel"]}" stroke="{P["tenue"]}" stroke-width="2"/>',
              f'<rect x="{cx - 10}" y="{cy - R - 14}" width="20" height="8" rx="2" fill="{P["tenue"]}"/>']
    for k in range(12):
        a = k * math.pi / 6
        partes.append(f'<line x1="{_n(cx + (R - 6) * math.sin(a))}" y1="{_n(cy - (R - 6) * math.cos(a))}" x2="{_n(cx + (R - 12) * math.sin(a))}" y2="{_n(cy - (R - 12) * math.cos(a))}" stroke="{P["tenue"]}" stroke-width="1.6"/>')
    partes.append(f'<path d="M{cx} {cy} L{cx} {cy - R + 16}" stroke="{P["cian"]}" stroke-width="3" stroke-linecap="round"/><path d="M{cx} {cy} L{_n(cx + 34)} {_n(cy + 14)}" stroke="{P["amarillo"]}" stroke-width="3" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="4" fill="{P["texto"]}"/>')
    partes.append(_texto(250, 70, "0 – 5.0", P["texto"], 18, peso=600))
    partes.append(_caja_texto(205, 92, 120, 12, P["borde"], 6))
    partes.append(_texto(265, 126, "cronometrado, sin pistas", P["tenue"], 10))
    partes.append(_texto(265, 142, "corrección al entregar", P["tenue"], 10))
    partes.append(_texto(180, 197, "evaluación con tiempo límite", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: cronómetro y escala de calificación de 0 a 5")


def repaso() -> str:
    base = 150
    partes = [f'<line x1="40" y1="{base}" x2="330" y2="{base}" stroke="{P["tenue"]}" stroke-width="1.4"/>', f'<line x1="40" y1="30" x2="40" y2="{base}" stroke="{P["tenue"]}" stroke-width="1.4"/>']
    for i, h in enumerate((92, 58, 108, 40, 76)):
        x = 62 + i * 54
        partes.append(f'<rect x="{x}" y="{base - h}" width="34" height="{h}" rx="3" fill="{P["violeta"]}" fill-opacity=".28" stroke="{P["violeta"]}" stroke-width="1.6" stroke-dasharray="5 3"/>')
        partes.append(_texto(x + 17, base + 14, f"tema {i + 1}", P["tenue"], 9))
    partes.append(f'<line x1="40" y1="{base - 60}" x2="330" y2="{base - 60}" stroke="{P["amarillo"]}" stroke-width="1.4" stroke-dasharray="4 4"/>')
    partes.append(_texto(330, 20, "- - umbral de repaso", P["amarillo"], 10, "end"))
    partes.append(_texto(180, 197, "temas con menor precisión y errores frecuentes", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: barras de precisión por tema con un umbral de repaso (valores ilustrativos)")


def verificacion() -> str:
    x = np.linspace(30, 330, 200)
    u = (x - 30) / 300
    f = 100 - 56 * np.sin(2.5 * math.pi * u) * np.exp(-1.2 * u)
    g = f + 1.5 * np.sin(14 * math.pi * u)
    partes = [f'<line x1="30" y1="170" x2="330" y2="170" stroke="{P["tenue"]}" stroke-width="1.2"/>',
              _linea(x, f, S["onda"], 3.2), _linea(x, g, S["densidad"], 1.6, 1.0, 'stroke-dasharray="5 3"'),
              _texto(46, 24, "simulador", S["onda"], 11, "start", 600), _texto(46, 40, "referencia independiente", S["densidad"], 11, "start", 600)]
    partes.append(f'<circle cx="296" cy="34" r="16" fill="{P["panel"]}" stroke="{P["verde"]}" stroke-width="2"/><path d="M288 34l6 6 11-12" fill="none" stroke="{P["verde"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    partes.append(_texto(180, 192, "diferencia dentro de la tolerancia", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: curva del simulador y curva de referencia que coinciden dentro de la tolerancia")


def pruebas() -> str:
    partes = []
    filas = ("Eₙ de la caja", "normalización ∫|ψ|²dx = 1", "ortogonalidad ⟨ψₘ|ψₙ⟩ = 0", "Kₘₐₓ = hν − Φ", "Δx·Δp ≥ ħ/2")
    for i, txt in enumerate(filas):
        y = 18 + i * 34
        partes.append(_caja_texto(40, y, 280, 28, P["borde"], 5, P["panel"]))
        partes.append(_texto(56, y + 19, txt, P["texto"], 11, "start"))
        partes.append(f'<circle cx="298" cy="{y + 14}" r="9" fill="none" stroke="{P["verde"]}" stroke-width="1.8"/><path d="M293 {y + 14}l4 4 7-8" fill="none" stroke="{P["verde"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    partes.append(_texto(180, 195, "comprobaciones numéricas con su tolerancia", P["tenue"], 10))
    return _envolver("".join(partes), "Ilustración conceptual: lista de comprobaciones numéricas superadas")


ILUSTRACIONES = {"caja": caja, "oscilador": oscilador, "esfera": esfera, "fotoelectrico": fotoelectrico, "bohr": bohr, "incertidumbre": incertidumbre,
                 "ruta": ruta, "teoria": teoria, "formulario": formulario, "talleres": talleres, "ejercicios": ejercicios, "examen": examen,
                 "repaso": repaso, "verificacion": verificacion, "pruebas": pruebas}
_CACHE: dict[str, str] = {}


def svg(clave: str) -> str:
    """SVG de la ilustración de un simulador (cadena vacía si la página no tiene)."""
    if clave not in ILUSTRACIONES:
        return ""
    if clave not in _CACHE:
        _CACHE[clave] = ILUSTRACIONES[clave]()
    return _CACHE[clave]


# ---------------------------------------------------------------------
# Portada
# ---------------------------------------------------------------------
def _nube_2p(n: int = 900, semilla: int = 7):
    """Puntos (x, z) muestreados de la densidad del orbital 2p_z, ρ ∝ r² e^(−r) cos²θ, por rechazo (r en unidades arbitrarias)."""
    rng = np.random.default_rng(semilla)
    puntos = []
    while len(puntos) < n:
        r = rng.gamma(3.0, 1.0)                       # r² e^(−r): distribución radial del 2p con escala 1
        c = rng.uniform(-1, 1)                        # cos θ uniforme
        if rng.uniform() < c * c:                     # factor angular cos²θ
            fi = rng.uniform(0, 2 * math.pi)
            s = math.sqrt(1 - c * c)
            puntos.append((r * s * math.cos(fi), r * c))
    return np.array(puntos)


def portada() -> str:
    ancho, alto = 560, 330
    pts = _nube_2p()
    cx, cy, esc = 290, 165, 21.0
    xs, ys = cx + esc * pts[:, 0], cy - esc * pts[:, 1]
    ok = (xs > 20) & (xs < ancho - 10) & (ys > 12) & (ys < alto - 12)
    xs, ys = xs[ok], ys[ok]
    mitad = len(xs) // 2
    partes = []
    x = np.linspace(0, ancho, 300)
    for k, (amp, fase, color) in enumerate(((22, 0.0, P["violeta"]), (16, 1.2, P["cian"]), (10, 2.4, P["violeta"]))):
        y = 238 + amp * np.sin(2 * math.pi * (x / 190) * (k + 1) + fase) * np.exp(-((x - 120) / 190) ** 2 * 0.2)
        partes.append(_linea(x, y + 12 * k, color, 1.6, 0.35 - 0.07 * k))
    pa = "".join(f"M{_n(a)} {_n(b)}h0" for a, b in zip(xs[:mitad], ys[:mitad]))
    pb = "".join(f"M{_n(a)} {_n(b)}h0" for a, b in zip(xs[mitad:], ys[mitad:]))
    partes.append(f'<path d="{pa}" stroke="{P["violeta"]}" stroke-width="3.4" stroke-linecap="round" stroke-opacity=".75"/>')
    partes.append(f'<path d="{pb}" stroke="{P["cian"]}" stroke-width="3.4" stroke-linecap="round" stroke-opacity=".6"/>')
    partes.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{P["amarillo"]}"/>')
    partes.append(f'<line x1="{cx}" y1="{cy - 135}" x2="{cx}" y2="{cy + 135}" stroke="{P["borde"]}" stroke-width="1" stroke-dasharray="3 5"/>')
    partes.append(f'<line x1="{cx - 150}" y1="{cy}" x2="{cx + 150}" y2="{cy}" stroke="{P["borde"]}" stroke-width="1" stroke-dasharray="3 5"/>')
    partes.append(_texto(ancho - 12, alto - 10, "Ilustración conceptual: nube de probabilidad tipo 2p y ondas", P["tenue"], 10, "end"))
    return _envolver("".join(partes), "Ilustración conceptual: nube de probabilidad de un orbital tipo 2p y ondas estacionarias", ancho, alto)


# ---------------------------------------------------------------------
# Iconos de línea (24 × 24) para los módulos de teoría, repaso y verificación
# ---------------------------------------------------------------------
_ICONOS = {
    "ruta": '<circle cx="5" cy="19" r="2"/><circle cx="19" cy="5" r="2"/><path d="M5 17C5 10 19 14 19 7"/>',
    "teoria": '<path d="M4 5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4z"/><path d="M20 5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z"/>',
    "formulario": '<path d="M18 5H6l7 7-7 7h12"/>',
    "talleres": '<path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M14 7l3 3"/>',
    "ejercicios": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h2M14 12h2M8 16h2M14 16h2"/>',
    "examen": '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M9 3h6"/>',
    "repaso": '<path d="M4 12a8 8 0 1 0 3-6.2M4 4v4h4M12 8v4l3 2"/>',
    "verificacion": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "pruebas": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3M8 15h8"/>',
}


def icono(clave: str, color: str | None = None) -> str:
    """Icono de línea decorativo (SVG de 24 × 24); cadena vacía si no existe."""
    if clave not in _ICONOS:
        return ""
    return (f'<svg class="ql-icono" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color or P["cian"]}" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ICONOS[clave]}</svg>')


# ---------------------------------------------------------------------
# Observatorio: escena principal de la portada (animada con CSS)
# ---------------------------------------------------------------------
def observatorio() -> str:
    """
    Escena de la portada: nube de probabilidad del orbital 2p_z (muestreada de ρ ∝ r² e^(−r) cos²θ), tres órbitas de referencia con un
    punto luminoso que las recorre y una retícula de medida. Las clases ql-obs-* reciben su movimiento del CSS de `quantum_lab_escena`;
    sin CSS (o con «reducir movimiento») la escena queda estática y completa. Es una ilustración conceptual, no un resultado calculado.
    """
    ancho, alto = 640, 460
    cx, cy, esc = 330, 228, 25.0
    pts = _nube_2p(1100, semilla=11)
    xs, ys = cx + esc * pts[:, 0], cy - esc * pts[:, 1]
    ok = (xs > 16) & (xs < ancho - 16) & (ys > 16) & (ys < alto - 16)
    xs, ys = xs[ok], ys[ok]
    superior = ys < cy
    def nube(mask, color, op):
        d = "".join(f"M{_n(a)} {_n(b)}h0" for a, b in zip(xs[mask], ys[mask]))
        return f'<path d="{d}" stroke="{color}" stroke-width="3.2" stroke-linecap="round" stroke-opacity="{op}"/>'
    partes = [
        '<defs><radialGradient id="ql-obs-halo" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0" stop-color="{P["violeta"]}" stop-opacity=".45"/><stop offset=".55" stop-color="{P["violeta"]}" stop-opacity=".08"/>'
        f'<stop offset="1" stop-color="{P["violeta"]}" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="ql-obs-nucleo" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0" stop-color="#FFFFFF"/><stop offset=".35" stop-color="{P["amarillo"]}"/><stop offset="1" stop-color="{P["amarillo"]}" stop-opacity="0"/></radialGradient></defs>',
        f'<circle cx="{cx}" cy="{cy}" r="210" fill="url(#ql-obs-halo)" class="ql-obs-halo"/>',
    ]
    # retícula de medida (anillos y ejes con marcas)
    ret = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{P["borde"]}" stroke-width="1" stroke-dasharray="2 6"/>' for r in (70, 140, 210)]
    ret.append(f'<line x1="{cx - 230}" y1="{cy}" x2="{cx + 230}" y2="{cy}" stroke="{P["borde"]}" stroke-width="1"/>')
    ret.append(f'<line x1="{cx}" y1="{cy - 215}" x2="{cx}" y2="{cy + 215}" stroke="{P["borde"]}" stroke-width="1"/>')
    for k in range(-4, 5):
        if k:
            ret.append(f'<line x1="{cx + 50 * k}" y1="{cy - 4}" x2="{cx + 50 * k}" y2="{cy + 4}" stroke="{P["tenue"]}" stroke-width="1" stroke-opacity=".6"/>')
            ret.append(f'<line x1="{cx - 4}" y1="{cy + 50 * k}" x2="{cx + 4}" y2="{cy + 50 * k}" stroke="{P["tenue"]}" stroke-width="1" stroke-opacity=".6"/>')
    partes.append('<g class="ql-obs-reticula">' + "".join(ret) + "</g>")
    # órbitas de referencia: cada una es un círculo aplastado e inclinado; el grupo interior gira con CSS
    for i, (inclinacion, aplastado, radio, color, dur) in enumerate(((-24, .30, 190, P["cian"], 1), (38, .24, 150, MAGENTA, 2), (90, .18, 120, P["cian"], 3))):
        partes.append(f'<g transform="translate({cx} {cy}) rotate({inclinacion}) scale(1 {aplastado})"><g class="ql-obs-giro ql-obs-giro-{dur}">'
                      f'<circle r="{radio}" fill="none" stroke="{color}" stroke-width="{1.2 / aplastado ** .5:.2f}" stroke-opacity=".38"/>'
                      f'<circle cx="{radio}" r="{5 / aplastado ** .5:.1f}" fill="{color}" class="ql-obs-electron"/></g></g>')
    partes.append(f'<g class="ql-obs-nube">{nube(superior, P["violeta"], .8)}{nube(~superior, P["cian"], .7)}</g>')
    partes.append(f'<circle cx="{cx}" cy="{cy}" r="16" fill="url(#ql-obs-nucleo)" class="ql-obs-nucleo"/>')
    # rótulos técnicos
    mono = "'Source Code Pro', Consolas, monospace"
    def rot(x, y, t, c, ancla="start"):
        return f'<text x="{x}" y="{y}" fill="{c}" font-size="11" font-family="{mono}" letter-spacing="1.5" text-anchor="{ancla}">{t}</text>'
    partes += [rot(24, 34, "ORBITAL 2p  ·  n = 2  ·  l = 1  ·  m = 0", P["tenue"]),
               rot(24, 52, "ρ(r, θ) ∝ r² e^(−r) cos²θ", P["violeta"]),
               rot(ancho - 24, alto - 22, "ILUSTRACIÓN CONCEPTUAL", P["tenue"], "end"),
               f'<line x1="{cx + 140}" y1="{cy - 120}" x2="{cx + 210}" y2="{cy - 170}" stroke="{P["tenue"]}" stroke-width="1"/>',
               rot(cx + 214, cy - 174, "|ψ|² máx.", P["texto"])]
    return _envolver("".join(partes), "Ilustración conceptual: nube de probabilidad de un orbital 2p con órbitas de referencia y retícula de medida", ancho, alto)
