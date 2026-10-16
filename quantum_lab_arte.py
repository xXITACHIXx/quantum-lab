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

import numpy as np
from numpy.polynomial import hermite as _herm

from quantum_lab_tema import PALETA as P, SERIES as S

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
    return f'<path d="{_camino(xs, ys)}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-opacity="{op}" stroke-linejoin="round" {extra}/>'


def _area(xs, ys, base, color, op=0.25) -> str:
    return f'<path d="{_camino(xs, ys)} L{_n(xs[-1])} {_n(base)} L{_n(xs[0])} {_n(base)} Z" fill="{color}" fill-opacity="{op}" stroke="none"/>'


def _texto(x, y, txt, color=None, tam=11, ancla="middle", peso=500) -> str:
    return (f'<text x="{_n(x)}" y="{_n(y)}" fill="{color or P["tenue"]}" font-size="{tam}" font-family="{_FUENTE}" '
            f'font-weight="{peso}" text-anchor="{ancla}">{txt}</text>')


def _envolver(contenido: str, titulo: str, ancho=ANCHO, alto=ALTO) -> str:
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
    partes.append(f'<path d="{_camino(xs, ys, True)}" fill="{S["onda"]}" fill-opacity=".38" stroke="{S["onda"]}" stroke-width="2"/>')
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


ILUSTRACIONES = {"caja": caja, "oscilador": oscilador, "esfera": esfera, "fotoelectrico": fotoelectrico, "bohr": bohr, "incertidumbre": incertidumbre}
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
