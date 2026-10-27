"""
redactor/_leyes.py — Leyes de la física de las que se puede partir en un desarrollo
===================================================================================

Cuando un paso introduce símbolos o relaciones que no vienen de las líneas anteriores, antes de marcarlo «no verificable» se prueba si
se deduce de la línea anterior más UNA de estas leyes. Son relaciones estándar del curso (las mismas de la sección de fórmulas); los
símbolos son los nombres habituales (h, nu, lam, hbar, omega, E, p, m, v, c, a, n, K, phi) y la ley solo se aplica con ese significado.
Si el paso se deduce usando una ley, el mensaje dice cuál, para que la persona confirme que sus símbolos significan lo mismo.
"""

from __future__ import annotations

# (nombre, ecuación escrita como la escribiría el estudiante)
LEYES: tuple[tuple[str, str], ...] = (
    ("Planck–Einstein: E = hν", "E = h nu"),
    ("Onda: c = λν", "c = lam nu"),
    ("De Broglie: p = h/λ", "p = h/lam"),
    ("ħ = h/2π", "hbar = h/(2 pi)"),
    ("Frecuencia angular: ω = 2πν", "omega = 2 pi nu"),
    ("Cuanto de energía: E = ħω", "E = hbar omega"),
    ("Energía cinética: E = p²/2m", "E = p^2/(2 m)"),
    ("Momento lineal: p = mv", "p = m v"),
    ("Energía en reposo: E = mc²", "E = m c^2"),
    ("Efecto fotoeléctrico: K = hν − φ", "K = h nu - phi"),
    ("Partícula en una caja: E = n²π²ħ²/2ma²", "E = n^2 pi^2 hbar^2/(2 m a^2)"),
    ("Oscilador armónico: E = (n + ½)ħω", "E = (n + 1/2) hbar omega"),
)
