"""
quantum_lab_tema.py — Fuente única de los colores de QUANTUM LAB
================================================================

Todos los colores de la aplicación salen de aquí: el CSS de Streamlit, los gráficos de Matplotlib y Plotly, las ilustraciones SVG
y `.streamlit/config.toml` (que no puede importar Python, por eso `test_tema.py` comprueba que coincidan).

Significado de cada color (se usan siempre así):

    cian      controles y elementos interactivos; también la densidad de probabilidad |ψ|²
    violeta   funciones de onda, orbitales y fenómenos ondulatorios
    verde     validaciones satisfactorias; energía cinética
    amarillo  energía, advertencias y atención
    rojo      errores y condiciones inválidas
"""

PALETA = {
    "fondo": "#0B1020",
    "panel": "#151F35",
    "cian": "#42D9FF",
    "violeta": "#A78BFA",
    "verde": "#39D98A",
    "amarillo": "#FFBD59",
    "rojo": "#FF647C",
    "texto": "#F2F5FC",
    "tenue": "#A7B4CE",
    "borde": "#263550",
}

# Derivados de la paleta base (mezclas con el fondo o el panel).
PANEL_2 = "#1B2744"          # al pasar el cursor y fondos de controles flotantes
LATERAL = "#0E1528"          # barra lateral
PIE = "#7B89A8"
MAGENTA = "#F472D0"          # acento puntual de la escena (órbitas, luz ambiental); nunca para estados
PROFUNDO = "#070B17"         # fondo de la escena de la portada, más profundo que el fondo general              # texto de pie de página (contraste 4.6:1 sobre el fondo)

# Series de las gráficas científicas (nombre semántico → color).
SERIES = {
    "onda": PALETA["violeta"],           # función de onda ψ
    "densidad": PALETA["cian"],          # densidad de probabilidad |ψ|²
    "cinetica": PALETA["verde"],         # energía cinética
    "potencial": "#F58FD0",              # energía potencial
    "energia": PALETA["amarillo"],       # nivel de energía / energía total
    "interferencia": "#5EEAD4",          # términos de interferencia, parte imaginaria
}


def contraste(hex_a: str, hex_b: str) -> float:
    """Relación de contraste WCAG entre dos colores «#RRGGBB» (4.5 o más es suficiente para texto)."""
    def luminancia(h: str) -> float:
        canales = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    a, b = sorted((luminancia(hex_a), luminancia(hex_b)), reverse=True)
    return (a + 0.05) / (b + 0.05)
