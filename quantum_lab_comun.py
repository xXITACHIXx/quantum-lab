"""
quantum_lab_comun.py — Infraestructura compartida de QUANTUM LAB
=================================================================

Este módulo NO contiene la física de ningún simulador. Solo reúne lo que los
tres programas necesitan para formar una misma "familia visual":

  * constantes físicas (CODATA, vía SciPy),
  * sistemas de unidades (SI / unidades atómicas) y funciones de formato,
  * tema visual (colores, estilo de Matplotlib y de Plotly, CSS de Streamlit),
  * ayudas de interfaz (estado de sesión, restaurar valores, demostraciones),
  * ayuda para animaciones de Plotly (se ejecutan en el navegador),
  * un registro sencillo de pruebas numéricas,
  * la función `lanzar`, que permite ejecutar cada simulador de forma
    independiente (interfaz con `streamlit run`, pruebas con `python`).
"""

from __future__ import annotations

import logging
import sys
from functools import lru_cache

import numpy as np
import matplotlib.pyplot as plt
from scipy import constants as const

# Fuera de Streamlit (p. ej. al ejecutar las pruebas con `python`), Streamlit
# emite avisos de "modo sin servidor" que no aportan nada; se silencian.
for _nombre in ("streamlit.runtime.caching.cache_data_api",
                "streamlit.runtime.scriptrunner_utils.script_run_context",
                "streamlit.runtime.state.session_state_proxy"):
    logging.getLogger(_nombre).setLevel(logging.ERROR)

# =====================================================================
# 1. CONSTANTES FÍSICAS
# =====================================================================
HBAR = const.hbar                                             # J·s
H_PLANCK = const.h                                            # J·s
M_E = const.m_e                                               # kg
E_CARGA = const.e                                             # C  (1 eV = E_CARGA julios)
E_HARTREE = const.physical_constants["Hartree energy"][0]     # J
A0 = const.physical_constants["Bohr radius"][0]               # m
T_ATOMICO = HBAR / E_HARTREE                                  # s  (unidad atómica de tiempo)

# Paleta coherente en los tres simuladores
COLORES = {
    "onda": "#00D4FF",          # función de onda ψ
    "densidad": "#FFB000",      # densidad de probabilidad |ψ|²
    "cinetica": "#22C55E",      # energía cinética
    "potencial": "#8B5CF6",     # energía potencial
    "energia": "#FF4D6D",       # nivel / energía total
    "interferencia": "#00FF9D",  # términos de interferencia, imaginaria
    "gris": "#B8C1D1",
    "fondo": "#0B1020",
    "panel": "#121A33",
    "rejilla": "#2A3558",
    "texto": "#E6EAF5",
}

SISTEMAS = ("SI", "Atómicas")


# =====================================================================
# 2. UNIDADES Y FORMATO
# =====================================================================
def obtener_unidades(sistema: str) -> dict:
    """
    Devuelve los factores para pasar de las unidades de la interfaz a SI.

    Todos los cálculos internos se hacen en SI; el sistema elegido solo
    determina cómo se introducen los parámetros y cómo se muestran los
    resultados:

      SI        : longitud en nm, masa en mₑ, energía en eV (y J), ω en rad/s.
      Atómicas  : longitud en a₀, masa en mₑ, energía en Eₕ, ω en Eₕ/ħ.
    """
    if sistema == "SI":
        return {
            "sistema": "SI",
            "nombre_longitud": "nm",
            "nombre_longitud_tex": r"\mathrm{nm}",
            "factor_longitud": 1e-9,
            "nombre_masa": "mₑ",
            "nombre_energia": "eV",
            "nombre_energia_tex": r"\mathrm{eV}",
            "factor_energia": E_CARGA,
            "nombre_omega": "rad/s",
            "factor_omega": 1.0,
            "nombre_tiempo": "fs",
            "factor_tiempo": 1e-15,
        }
    if sistema == "Atómicas":
        return {
            "sistema": "Atómicas",
            "nombre_longitud": "a₀",
            "nombre_longitud_tex": r"a_0",
            "factor_longitud": A0,
            "nombre_masa": "mₑ",
            "nombre_energia": "Eₕ",
            "nombre_energia_tex": r"E_h",
            "factor_energia": E_HARTREE,
            "nombre_omega": "Eₕ/ħ",
            "factor_omega": E_HARTREE / HBAR,
            "nombre_tiempo": "ħ/Eₕ",
            "factor_tiempo": T_ATOMICO,
        }
    raise ValueError("El sistema de unidades debe ser 'SI' o 'Atómicas'.")


def positivo_finito(valor, nombre: str) -> float:
    """Convierte a float y comprueba que sea positivo y finito."""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser un número (recibido: {valor!r}).")
    if not np.isfinite(v) or v <= 0:
        raise ValueError(f"{nombre} debe ser un número positivo y finito (recibido: {valor}).")
    return v


def entero_en_rango(valor, nombre: str, minimo: int, maximo: int | None = None) -> int:
    """Convierte a entero estricto (rechaza 2.5, 'a', NaN) y comprueba el rango."""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser un número entero (recibido: {valor!r}).")
    if not np.isfinite(v) or v != int(v):
        raise ValueError(f"{nombre} debe ser un número entero (recibido: {valor}).")
    v = int(v)
    if v < minimo:
        raise ValueError(f"{nombre} debe ser ≥ {minimo} (recibido: {v}).")
    if maximo is not None and v > maximo:
        raise ValueError(f"{nombre} debe ser ≤ {maximo} (recibido: {v}).")
    return v


def cientifico(valor: float, cifras: int = 6) -> str:
    """Notación científica compacta: 1.234560e-19."""
    return f"{valor:.{cifras}e}"


def texto_energia(energia_julios: float, sistema: str, cifras: int = 6) -> str:
    """Energía en las unidades del sistema elegido y, además, en eV."""
    ev = energia_julios / E_CARGA
    if sistema == "SI":
        return f"{cientifico(energia_julios, cifras)} J = {cientifico(ev, cifras)} eV"
    return (f"{cientifico(energia_julios / E_HARTREE, cifras)} Eₕ = "
            f"{cientifico(ev, cifras)} eV")


def texto_longitud(longitud_m: float, sistema: str, cifras: int = 6) -> str:
    u = obtener_unidades(sistema)
    return f"{longitud_m / u['factor_longitud']:.{cifras}g} {u['nombre_longitud']}"


def texto_tiempo(tiempo_s: float, sistema: str, cifras: int = 6) -> str:
    u = obtener_unidades(sistema)
    return f"{tiempo_s / u['factor_tiempo']:.{cifras}g} {u['nombre_tiempo']}"


# =====================================================================
# 3. REGISTRO DE PRUEBAS NUMÉRICAS
# =====================================================================
class RegistroPruebas:
    """
    Acumula resultados de pruebas. A diferencia de un `assert`, no se detiene
    en el primer fallo: así la interfaz puede mostrar la tabla completa.
    """

    def __init__(self, nombre: str):
        self.nombre = nombre
        self.resultados: list[dict] = []

    def comprobar(self, descripcion: str, condicion, detalle: str = "") -> bool:
        ok = bool(condicion)
        self.resultados.append({"Prueba": descripcion, "Resultado": "Correcta" if ok else "FALLA",
                                "Detalle": detalle, "ok": ok})
        return ok

    def comprobar_error(self, descripcion: str, funcion, *args, tipo=ValueError, **kwargs) -> bool:
        """Comprueba que `funcion(*args)` lance el tipo de error esperado (validación)."""
        try:
            funcion(*args, **kwargs)
        except tipo as error:
            return self.comprobar(descripcion, True, f"Mensaje: «{error}»")
        except Exception as error:  # error de otro tipo = fallo
            return self.comprobar(descripcion, False, f"Error inesperado: {error!r}")
        return self.comprobar(descripcion, False, "No lanzó ningún error")

    def todo_ok(self) -> bool:
        return all(r["ok"] for r in self.resultados)

    def tabla(self) -> list[dict]:
        return [{k: v for k, v in r.items() if k != "ok"} for r in self.resultados]

    def imprimir(self) -> None:
        print(f"\n=== Pruebas: {self.nombre} ===")
        for r in self.resultados:
            linea = f"{r['Resultado']}  {r['Prueba']}"
            if r["Detalle"]:
                linea += f"   [{r['Detalle']}]"
            print(linea)
        total = len(self.resultados)
        bien = sum(r["ok"] for r in self.resultados)
        print(f"--- {bien}/{total} pruebas superadas ---")


# =====================================================================
# 4. ESTILO VISUAL
# =====================================================================
def configurar_matplotlib() -> None:
    """Estilo oscuro científico para todas las figuras de Matplotlib."""
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": COLORES["fondo"],
        "axes.facecolor": COLORES["panel"],
        "savefig.facecolor": COLORES["fondo"],
        "axes.edgecolor": COLORES["rejilla"],
        "axes.labelcolor": COLORES["texto"],
        "text.color": COLORES["texto"],
        "xtick.color": COLORES["gris"],
        "ytick.color": COLORES["gris"],
        "grid.color": COLORES["rejilla"],
        "grid.alpha": 0.5,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "legend.facecolor": COLORES["fondo"],
        "legend.edgecolor": COLORES["rejilla"],
        "legend.framealpha": 0.85,
        "legend.fontsize": 8.5,
        "figure.dpi": 100,
    })


configurar_matplotlib()


def aplicar_tema_plotly(figura, titulo: str | None = None, altura: int = 520):
    """Aplica el tema oscuro de QUANTUM LAB a una figura de Plotly."""
    figura.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORES["fondo"],
        plot_bgcolor=COLORES["panel"],
        font=dict(color=COLORES["texto"], family=FUENTE_TEXTO, size=13),
        title=dict(text=titulo, x=0.01, font=dict(family=FUENTE_TITULOS, size=16)) if titulo else None,
        height=altura,
        margin=dict(l=50, r=20, t=60 if titulo else 30, b=60),
        legend=dict(bgcolor="rgba(11,16,32,0.7)", bordercolor=COLORES["rejilla"], borderwidth=1),
    )
    figura.update_xaxes(gridcolor=COLORES["rejilla"], zerolinecolor=COLORES["rejilla"])
    figura.update_yaxes(gridcolor=COLORES["rejilla"], zerolinecolor=COLORES["rejilla"])
    return figura


def agregar_animacion(figura, nombres_cuadros: list[str], etiquetas: list[str],
                      duracion_ms: int = 60) -> None:
    """
    Añade a una figura de Plotly (que ya tiene `frames`) los botones
    Reproducir/Pausa y un deslizador de tiempo.

    La animación se ejecuta ENTERAMENTE en el navegador: Python no vuelve a
    calcular nada en cada cuadro, por lo que la interfaz no se bloquea.
    """
    # Los controles se colocan a una distancia fija (en píxeles) bajo el área de dibujo, para que no
    # se solapen con el título del eje x sea cual sea la altura de la figura.
    altura = figura.layout.height or 520
    margen_sup = (figura.layout.margin.t if figura.layout.margin.t is not None else 60)
    margen_inf = 165
    alto_dibujo = max(altura - margen_sup - margen_inf, 100)
    y_ctrl = -95 / alto_dibujo
    figura.update_layout(
        margin=dict(b=margen_inf),
        updatemenus=[dict(
            type="buttons", direction="left", x=0.0, y=y_ctrl, xanchor="left", yanchor="top", showactive=False,
            pad=dict(r=8, t=0), bgcolor="#1A2342", bordercolor=COLORES["rejilla"], borderwidth=1,
            font=dict(color=COLORES["texto"], size=12),
            buttons=[
                dict(label="▶  Reproducir", method="animate",
                     args=[None, dict(frame=dict(duration=duracion_ms, redraw=True),
                                      transition=dict(duration=0), fromcurrent=True,
                                      mode="immediate")]),
                dict(label="❚❚  Pausa", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        transition=dict(duration=0), mode="immediate")]),
            ])],
        sliders=[dict(
            active=0, x=0.2, y=y_ctrl + 8 / alto_dibujo, len=0.8, xanchor="left", yanchor="top",
            currentvalue=dict(prefix="", font=dict(size=12, color=COLORES["texto"], family=FUENTE_CIFRAS),
                              xanchor="right", offset=8),
            pad=dict(t=0, b=0), bgcolor="#1A2342", bordercolor=COLORES["rejilla"], activebgcolor=COLORES["onda"],
            tickcolor=COLORES["gris"], font=dict(size=10, color=COLORES["gris"]),
            steps=[dict(label=etq, method="animate",
                        args=[[nom], dict(frame=dict(duration=0, redraw=True),
                                          transition=dict(duration=0), mode="immediate")])
                   for nom, etq in zip(nombres_cuadros, etiquetas)],
        )],
    )


# ---------------------------------------------------------------------
# Hoja de estilo de la interfaz (Streamlit)
# ---------------------------------------------------------------------
# Tipografía: se usan las tres familias que Streamlit ya trae incluidas
# (funcionan sin Internet): «Source Serif» para títulos, «Source Sans» para
# el texto y «Source Code Pro» para cifras y etiquetas técnicas.
FUENTE_TITULOS = '"Source Serif", "Source Serif Pro", Georgia, "Times New Roman", serif'
FUENTE_TEXTO = '"Source Sans", "Source Sans Pro", "Segoe UI", system-ui, sans-serif'
FUENTE_CIFRAS = '"Source Code Pro", Consolas, "Courier New", monospace'

CSS = """
<style>
:root {
  --ql-fondo: #0B1020; --ql-panel: #10172C; --ql-panel-2: #131B33;
  --ql-borde: #232C47; --ql-texto: #E6EAF5; --ql-tenue: #9AA4BC; --ql-acento: #38BDF8;
  --ql-serif: FUENTE_TITULOS; --ql-mono: FUENTE_CIFRAS;
}
.block-container { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1380px; }
h1, h2, h3, h4 { font-family: var(--ql-serif) !important; letter-spacing: -.005em; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- Encabezado de página ---------- */
.ql-etiqueta { font: 600 .72rem/1.2 var(--ql-mono); letter-spacing: .18em; text-transform: uppercase;
  color: var(--ql-acento); margin: 0; }
.ql-titulo { font-family: var(--ql-serif); font-weight: 600; font-size: 2.05rem; line-height: 1.15;
  color: #F3F5FA; margin: .35rem 0 .3rem 0; }
.ql-subtitulo { color: var(--ql-tenue); font-size: 1.02rem; line-height: 1.5; margin: 0; max-width: 60rem; }
.ql-regla { border: 0; border-top: 1px solid var(--ql-borde); margin: 1.1rem 0 1.3rem 0; }

/* ---------- Títulos de sección (versalitas con filete) ---------- */
.ql-seccion { display: flex; align-items: center; gap: .8rem; margin: .5rem 0 .7rem 0;
  font: 600 .72rem/1 var(--ql-mono); letter-spacing: .16em; text-transform: uppercase; color: var(--ql-tenue); }
.ql-seccion::after { content: ""; flex: 1; border-top: 1px solid var(--ql-borde); }

/* ---------- Paneles y métricas ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--ql-borde) !important; border-radius: 8px; }
div[data-testid="stMetric"] { background: var(--ql-panel); border: 1px solid var(--ql-borde);
  border-radius: 6px; padding: .7rem .9rem .75rem .9rem; min-height: 5.6rem; }
div[data-testid="stMetricLabel"] p { font-size: .8rem; color: var(--ql-tenue); white-space: normal; }
div[data-testid="stMetricValue"] { font-family: var(--ql-mono); font-size: 1.18rem; font-weight: 500;
  color: var(--ql-texto); }
div[data-testid="stMetricDelta"] { font-family: var(--ql-mono); font-size: .76rem; }

/* ---------- Tabla de resultados ---------- */
.ql-tabla { width: 100%; border-collapse: collapse; font-size: .93rem; margin: .2rem 0 .6rem 0; }
.ql-tabla th { text-align: left; font-weight: 600; font-size: .8rem; letter-spacing: .01em;
  color: var(--ql-tenue); border-bottom: 1px solid var(--ql-borde); padding: .5rem .7rem; }
.ql-tabla th.ql-v { text-align: right; }
.ql-tabla td { padding: .45rem .7rem; border-bottom: 1px solid rgba(35,44,71,.65); vertical-align: top; }
.ql-tabla tr:last-child td { border-bottom: 0; }
.ql-tabla.ql-compacta { width: auto; min-width: 55%; }
.ql-tabla.ql-compacta td, .ql-tabla.ql-compacta th { padding-left: 1.1rem; padding-right: 1.1rem; }
.ql-tabla td.ql-v { font-family: var(--ql-mono); text-align: right; white-space: nowrap; color: var(--ql-texto); }
.ql-tabla td.ql-u { color: var(--ql-tenue); white-space: nowrap; width: 1%; }
.ql-tabla td.ql-n { color: var(--ql-tenue); font-size: .86rem; }

/* ---------- Pestañas ---------- */
button[data-baseweb="tab"] p { font-size: .96rem; font-weight: 500; }
div[data-baseweb="tab-list"] { gap: 1.2rem; border-bottom: 1px solid var(--ql-borde); }

/* ---------- Barra lateral ---------- */
section[data-testid="stSidebar"] { border-right: 1px solid var(--ql-borde); }
section[data-testid="stSidebar"] .block-container, section[data-testid="stSidebarContent"] { padding-top: 1rem; }
.ql-marca { padding: .2rem 0 1rem 0; border-bottom: 1px solid var(--ql-borde); margin-bottom: .9rem; }
.ql-marca .ql-marca-nombre { font-family: var(--ql-serif); font-size: 1.35rem; font-weight: 600; color: #F3F5FA;
  letter-spacing: .02em; }
.ql-marca .ql-marca-sub { font: 500 .68rem/1.4 var(--ql-mono); letter-spacing: .14em; text-transform: uppercase;
  color: var(--ql-tenue); margin-top: .2rem; }
section[data-testid="stSidebar"] .stButton button { justify-content: flex-start; text-align: left; border: 0;
  border-radius: 6px; padding: .38rem .7rem; min-height: 2.2rem; font-weight: 400; }
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] { background: transparent; color: var(--ql-texto); }
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover { background: var(--ql-panel-2); color: #FFFFFF; }
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] { background: rgba(56,189,248,.12);
  color: var(--ql-acento); box-shadow: inset 2px 0 0 var(--ql-acento); }
section[data-testid="stSidebar"] .stButton button p { font-size: .93rem; white-space: nowrap; }
section[data-testid="stSidebar"] .stButton button > div { justify-content: flex-start; width: 100%; }
section[data-testid="stSidebar"] .stButton button > div > span { gap: .6rem; }
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"] { gap: .2rem; }
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] { padding: .35rem .5rem .55rem .5rem; }
section[data-testid="stSidebar"] details { border-color: var(--ql-borde) !important; }
section[data-testid="stSidebar"] details summary p { font: 600 .72rem/1 var(--ql-mono); letter-spacing: .14em;
  text-transform: uppercase; color: var(--ql-tenue); }
.ql-pie { font: 400 .72rem/1.5 var(--ql-mono); color: #6F7A95; margin-top: 1.2rem; }

/* ---------- Portada ---------- */
.ql-portada { padding: 2.6rem 2.4rem 2.3rem 2.4rem; border: 1px solid var(--ql-borde); border-radius: 10px;
  background: linear-gradient(180deg, #10172C 0%, #0D1427 100%); margin-bottom: 1.6rem; }
.ql-portada .ql-titulo { font-size: 2.7rem; }
.ql-card { padding: 1.3rem 1.35rem 1.1rem 1.35rem; border: 1px solid var(--ql-borde); border-radius: 8px;
  background: var(--ql-panel); min-height: 15.5rem; display: flex; flex-direction: column; }
.ql-card h3 { font-family: var(--ql-serif); font-size: 1.22rem; font-weight: 600; margin: .45rem 0 .55rem 0; color: #F3F5FA; }
.ql-card p { color: var(--ql-tenue); font-size: .94rem; line-height: 1.5; margin: 0; }
.ql-card .ql-ecuacion { margin-top: auto; padding-top: .9rem; font: 400 .86rem/1.4 var(--ql-mono); color: var(--ql-texto); }

footer { visibility: hidden; }
@media (max-width: 900px) {
  .ql-portada { padding: 1.6rem 1.2rem; } .ql-portada .ql-titulo { font-size: 2rem; }
  .ql-card { min-height: 0; } .block-container { padding-left: 1rem; padding-right: 1rem; }
}
</style>
""".replace("FUENTE_TITULOS", FUENTE_TITULOS).replace("FUENTE_CIFRAS", FUENTE_CIFRAS)


# ---------------------------------------------------------------------
# Fuente de símbolos (compatibilidad con celulares)
# ---------------------------------------------------------------------
# Algunos teléfonos no tienen en sus fuentes los subíndices de letras (ₙ, ₗ, ₕ…), los corchetes ⟨ ⟩ o
# ciertos operadores, y muestran un recuadro vacío. Para evitarlo se genera, una sola vez, una fuente
# mínima con SOLO esos símbolos a partir de DejaVu (incluida en Matplotlib, licencia libre) y se
# incrusta en la página. Con `unicode-range` el navegador la usa únicamente para esos caracteres;
# el resto del texto sigue con las fuentes Source de Streamlit.
_RANGOS_SIMBOLOS = [
    (0x02E1, 0x02E1),   # ˡ
    (0x1D43, 0x1D5B),   # superíndices de letras (ᵃ … ᵐ … ᵛ)
    (0x2034, 0x2034),   # ‴
    (0x2070, 0x209C),   # superíndices y subíndices (⁰…⁹ ⁺ ⁻ ⁿ ₀…₉ ₊ ₋ ₐ ₑ ₒ ₓ ₕ ₖ ₗ ₘ ₙ ₚ ₛ ₜ)
    (0x210F, 0x210F),   # ℏ
    (0x2190, 0x2194),   # ← ↑ → ↓ ↔
    (0x21D2, 0x21D2),   # ⇒
    (0x2202, 0x2202), (0x2207, 0x2208), (0x2211, 0x2212), (0x221A, 0x221E),   # ∂ ∇ ∈ ∑ − √ ∝ ∞
    (0x222B, 0x222C), (0x2248, 0x2248), (0x2260, 0x2261), (0x2264, 0x2265),   # ∫ ∬ ≈ ≠ ≡ ≤ ≥
    (0x25B6, 0x25B6), (0x26A0, 0x26A0), (0x275A, 0x275A),                     # ▶ ⚠ ❚
    (0x27E8, 0x27E9),   # ⟨ ⟩
]


def _rango_css() -> str:
    return ", ".join(f"U+{a:04X}" if a == b else f"U+{a:04X}-{b:04X}" for a, b in _RANGOS_SIMBOLOS)


@lru_cache(maxsize=1)
def css_fuente_simbolos() -> str:
    """Reglas @font-face con la fuente de símbolos incrustada (base64). Cadena vacía si algo falla."""
    try:
        import base64
        import io
        import os

        import matplotlib
        from fontTools import subset
        from fontTools.ttLib import TTFont

        carpeta = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
        codigos = [c for a, b in _RANGOS_SIMBOLOS for c in range(a, b + 1)]

        def woff_b64(archivo: str) -> str:
            opciones = subset.Options()
            opciones.flavor = "woff"
            opciones.notdef_outline = True
            # La tabla MATH de DejaVu no sobrevive al recorte: el validador de fuentes del navegador la rechazaría.
            opciones.drop_tables += ["MATH", "FFTM"]
            fuente = TTFont(os.path.join(carpeta, archivo))
            sub = subset.Subsetter(opciones)
            sub.populate(unicodes=codigos)
            sub.subset(fuente)
            fuente.flavor = "woff"
            datos = io.BytesIO()
            fuente.save(datos)
            return base64.b64encode(datos.getvalue()).decode("ascii")

        logging.getLogger("fontTools").setLevel(logging.ERROR)
        sans, mono = woff_b64("DejaVuSans.ttf"), woff_b64("DejaVuSansMono.ttf")
        rango = _rango_css()
        reglas = []
        for familia, datos in (("Source Sans", sans), ("Source Code Pro", mono)):
            reglas.append(f'@font-face {{ font-family: "{familia}"; src: url(data:font/woff;base64,{datos}) '
                          f'format("woff"); font-weight: 100 900; font-style: normal; font-display: swap; '
                          f'unicode-range: {rango}; }}')
        return "<style>" + "\n".join(reglas) + "</style>"
    except Exception:                       # sin fontTools o sin DejaVu: la app funciona igual
        return ""


def inyectar_css() -> None:
    import streamlit as st
    st.markdown(css_fuente_simbolos() + CSS, unsafe_allow_html=True)


# =====================================================================
# 5. AYUDAS DE INTERFAZ (Streamlit)
# =====================================================================
def _esc(texto) -> str:
    import html
    return html.escape(str(texto))


def encabezado_pagina(etiqueta: str, titulo: str, subtitulo: str) -> None:
    """Encabezado sobrio: etiqueta en versalitas, título con serifa, descripción y filete."""
    import streamlit as st
    st.markdown(f'<p class="ql-etiqueta">{_esc(etiqueta)}</p><div class="ql-titulo">{_esc(titulo)}</div>'
                f'<p class="ql-subtitulo">{_esc(subtitulo)}</p><hr class="ql-regla">', unsafe_allow_html=True)


def seccion(titulo: str) -> None:
    """Título de sección pequeño, en versalitas, con un filete hasta el margen derecho."""
    import streamlit as st
    st.markdown(f'<div class="ql-seccion">{_esc(titulo)}</div>', unsafe_allow_html=True)


def metricas(items, columnas: int = 4) -> None:
    """
    Rejilla regular de indicadores. `items` = lista de (etiqueta, valor) o (etiqueta, valor, ayuda).
    Todas las tarjetas tienen el mismo ancho; la última fila se completa con huecos.
    """
    import streamlit as st
    items = list(items)
    for inicio in range(0, len(items), columnas):
        cols = st.columns(columnas)
        for col, item in zip(cols, items[inicio:inicio + columnas]):
            etiqueta, valor = item[0], item[1]
            ayuda = item[2] if len(item) > 2 else None
            col.metric(etiqueta, valor, help=ayuda)


def tabla(filas, encabezados=("Magnitud", "Valor", "Unidad")) -> None:
    """
    Tabla de resultados con cifras alineadas a la derecha en tipografía monoespaciada.
    Cada fila: (magnitud, valor, unidad) o (magnitud, valor, unidad, nota).
    """
    import streamlit as st
    con_nota = any(len(f) > 3 for f in filas)
    cab = "".join(f'<th class="{"ql-v" if i == 1 else ""}">{_esc(h)}</th>' for i, h in enumerate(encabezados)) + ("<th>Nota</th>" if con_nota and len(encabezados) < 4 else "")
    cuerpo = []
    for f in filas:
        celdas = f'<td>{_esc(f[0])}</td><td class="ql-v">{_esc(f[1])}</td><td class="ql-u">{_esc(f[2])}</td>'
        if con_nota:
            celdas += f'<td class="ql-n">{_esc(f[3]) if len(f) > 3 else ""}</td>'
        cuerpo.append(f"<tr>{celdas}</tr>")
    st.markdown(f'<table class="ql-tabla"><thead><tr>{cab}</tr></thead><tbody>{"".join(cuerpo)}</tbody></table>',
                unsafe_allow_html=True)


def tabla_libre(filas: list[dict], numericas: tuple[str, ...] = ()) -> None:
    """Tabla genérica (lista de diccionarios). Las columnas en `numericas` se alinean como cifras."""
    import streamlit as st
    if not filas:
        return
    claves = list(filas[0].keys())
    cab = "".join(f'<th class="{"ql-v" if k in numericas else ""}">{_esc(k)}</th>' for k in claves)
    cuerpo = "".join("<tr>" + "".join(f'<td class="{"ql-v" if k in numericas else ""}">{_esc(f[k])}</td>' for k in claves)
                     + "</tr>" for f in filas)
    st.markdown(f'<table class="ql-tabla ql-compacta"><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table>',
                unsafe_allow_html=True)


def error(mensaje) -> None:
    import streamlit as st
    st.error(str(mensaje), icon=":material/error:")


def aviso(mensaje) -> None:
    import streamlit as st
    st.warning(str(mensaje), icon=":material/warning:")


def nota(mensaje) -> None:
    import streamlit as st
    st.info(str(mensaje), icon=":material/info:")


def pie_de_parametros(demos: dict, clave_demo: str, al_elegir_demo, valores_iniciales: dict, clave_reset: str) -> None:
    """Fila final del panel de parámetros: demostraciones (izquierda) y restaurar (derecha), alineadas abajo."""
    import streamlit as st
    c1, _, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
    c1.selectbox("Configuración de ejemplo", ["Seleccionar…"] + list(demos), key=clave_demo,
                 on_change=al_elegir_demo)
    c3.button("Restaurar valores iniciales", on_click=restaurar_estado, args=(valores_iniciales,),
              key=clave_reset, icon=":material/restart_alt:", width="stretch")


def boton_pruebas(modulo_pruebas, clave: str) -> None:
    """Contenido común de la pestaña «Pruebas numéricas»."""
    import streamlit as st
    st.markdown("Comprobaciones automáticas de la física y de la validación de datos de este simulador.")
    if st.button("Ejecutar pruebas", key=clave, type="primary", icon=":material/play_arrow:"):
        registro = modulo_pruebas()
        ok = sum(r["ok"] for r in registro.resultados)
        (st.success if registro.todo_ok() else st.error)(f"{ok} de {len(registro.resultados)} pruebas superadas")
        st.dataframe(registro.tabla(), hide_index=True, width="stretch")


def _acepta(funcion, parametro: str) -> bool:
    import inspect
    try:
        return parametro in inspect.signature(funcion).parameters
    except (TypeError, ValueError):
        return False


def mostrar_pyplot(figura) -> None:
    """Muestra una figura de Matplotlib ocupando el ancho (compatible con varias versiones de Streamlit)."""
    import streamlit as st
    if _acepta(st.pyplot, "width"):
        st.pyplot(figura, clear_figure=True, width="stretch")
    else:
        st.pyplot(figura, clear_figure=True, use_container_width=True)
    plt.close(figura)


def mostrar_plotly(figura, clave: str | None = None) -> None:
    """Muestra una figura de Plotly ocupando el ancho (compatible con varias versiones de Streamlit)."""
    import streamlit as st
    config = {"displaylogo": False}
    if _acepta(st.plotly_chart, "width"):
        st.plotly_chart(figura, width="stretch", key=clave, config=config)
    else:
        st.plotly_chart(figura, use_container_width=True, key=clave, config=config)


def iniciar_estado(valores_iniciales: dict) -> None:
    """Crea en `st.session_state` las claves que aún no existan."""
    import streamlit as st
    for clave, valor in valores_iniciales.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def restaurar_estado(valores_iniciales: dict) -> None:
    """Callback del botón «Restaurar valores iniciales»."""
    import streamlit as st
    for clave, valor in valores_iniciales.items():
        st.session_state[clave] = valor


def fijar_estado(valores: dict) -> None:
    """Callback para cargar una demostración o un experimento."""
    import streamlit as st
    for clave, valor in valores.items():
        st.session_state[clave] = valor


# =====================================================================
# 6. EJECUCIÓN INDEPENDIENTE DE CADA SIMULADOR
# =====================================================================
def lanzar(ejecutar_pruebas, interfaz_pagina, titulo_pagina: str, icono: str,
           nombre_archivo: str) -> None:
    """
    Punto de entrada común de cada simulador:

      * `streamlit run particula_caja.py` → abre la interfaz de ese simulador.
      * `python particula_caja.py`        → ejecuta sus pruebas numéricas.
    """
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    if get_script_run_ctx() is not None:        # estamos dentro de Streamlit
        import streamlit as st
        st.set_page_config(page_title=titulo_pagina, page_icon=icono, layout="wide")
        inyectar_css()
        interfaz_pagina()
        return

    registro = ejecutar_pruebas()
    registro.imprimir()
    print(f"\nPara abrir la interfaz gráfica:  streamlit run {nombre_archivo}")
    sys.exit(0 if registro.todo_ok() else 1)
