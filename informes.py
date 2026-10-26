"""
informes.py — Informes exportables de un experimento (PDF y CSV)
================================================================

Genera, SIN dependencias nuevas (solo Matplotlib), un informe en PDF y un CSV a partir de los datos que ya calculó
el simulador. El informe separa con claridad dos cosas:

    · «Datos calculados por el simulador»: parámetros, ecuaciones, tablas, gráficas y resultados. No son mediciones
      experimentales: salen de un modelo teórico.
    · «Conclusiones del estudiante»: texto que escribe la persona (o espacio en blanco para escribirlo a mano).

No inventa referencias, fechas experimentales ni conclusiones: solo escribe las referencias que cada simulador
declara y la fecha en que se generó el archivo.

La parte lógica no usa Streamlit; el botón de descarga (`boton_informe`) está al final.
"""

from __future__ import annotations

import csv
import io
import textwrap
from dataclasses import dataclass, field
from datetime import datetime

import matplotlib

matplotlib.use("Agg", force=False)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ANCHO_A4, ALTO_A4 = 8.27, 11.69      # pulgadas
MARGEN = 0.8
Fila = tuple[str, str, str]          # (magnitud, valor, unidad)


@dataclass
class Informe:
    titulo: str
    simulador: str
    objetivo: str
    modelo: str
    ecuaciones: list[str] = field(default_factory=list)          # sintaxis mathtext, sin los signos $
    parametros: list[Fila] = field(default_factory=list)
    procedimiento: list[str] = field(default_factory=list)
    tablas: list[tuple[str, list[str], list[list[str]]]] = field(default_factory=list)   # (título, encabezados, filas)
    figuras: list = field(default_factory=list)                  # figuras de Matplotlib con fondo claro
    resultados: list[Fila] = field(default_factory=list)
    preguntas: list[str] = field(default_factory=list)
    referencias: list[str] = field(default_factory=list)
    conclusiones: str = ""                                        # escrito por el estudiante (puede estar vacío)
    generado: str = ""                                            # fecha de generación (se rellena sola)


def validar(informe: Informe) -> None:
    """Un informe sin título, objetivo, modelo, parámetros o resultados no se genera (evita archivos vacíos)."""
    faltan = [n for n, v in (("título", informe.titulo), ("objetivo", informe.objetivo), ("modelo", informe.modelo),
                             ("parámetros", informe.parametros), ("resultados", informe.resultados)) if not v]
    if faltan:
        raise ValueError("Informe incompleto: falta " + ", ".join(faltan) + ".")
    for nombre, filas in (("parámetros", informe.parametros), ("resultados", informe.resultados)):
        if any(len(f) != 3 for f in filas):
            raise ValueError(f"Las filas de {nombre} deben tener (magnitud, valor, unidad).")


# =====================================================================
# CSV
# =====================================================================
def csv_informe(informe: Informe) -> bytes:
    """CSV (UTF-8 con BOM) con parámetros, resultados y tablas. Columnas: Sección, Magnitud, Valor, Unidad."""
    validar(informe)
    salida = io.StringIO()
    w = csv.writer(salida)
    w.writerow(["Sección", "Magnitud", "Valor", "Unidad"])
    w.writerow(["Informe", informe.titulo, informe.simulador, ""])
    for magnitud, valor, unidad in informe.parametros:
        w.writerow(["Parámetros (entrada)", magnitud, valor, unidad])
    for magnitud, valor, unidad in informe.resultados:
        w.writerow(["Resultados (calculados por el simulador)", magnitud, valor, unidad])
    for titulo, encabezados, filas in informe.tablas:
        w.writerow([f"Tabla: {titulo}", " | ".join(encabezados), "", ""])
        for fila in filas:
            w.writerow([f"Tabla: {titulo}", *[str(c) for c in fila][:3], *[""] * max(0, 3 - len(fila))])
    return ("﻿" + salida.getvalue()).encode("utf-8")


# =====================================================================
# PDF (maqueta sencilla sobre Matplotlib)
# =====================================================================
class _Lienzo:
    def __init__(self, pie: str):
        self.pie = pie
        self.paginas: list = []
        self.fig = None
        self.y = 0.0
        self.nueva()

    @property
    def ancho_util(self) -> float:
        return ANCHO_A4 - 2 * MARGEN

    def nueva(self) -> None:
        self.fig = plt.figure(figsize=(ANCHO_A4, ALTO_A4), facecolor="white")
        self.paginas.append(self.fig)
        self.y = MARGEN

    def _hay_sitio(self, alto: float) -> None:
        if self.y + alto > ALTO_A4 - MARGEN - 0.2:
            self.nueva()

    def texto(self, s: str, tam: float = 10, peso: str = "normal", color: str = "#111111", sangria: float = 0.0,
              estilo: str = "normal", familia: str = "DejaVu Sans") -> None:
        caracteres = max(20, int((self.ancho_util - sangria) * 72 / (tam * 0.58)))
        lineas = []
        for parrafo in str(s).split("\n"):
            lineas += textwrap.wrap(parrafo, caracteres) or [""]
        paso = tam * 1.5 / 72
        for linea in lineas:
            self._hay_sitio(paso)
            self.fig.text((MARGEN + sangria) / ANCHO_A4, 1 - self.y / ALTO_A4, linea, fontsize=tam, fontweight=peso,
                          color=color, va="top", ha="left", style=estilo, family=familia)
            self.y += paso

    def espacio(self, h: float = 0.12) -> None:
        self.y += h

    def titulo(self, s: str) -> None:
        self.texto(s, 17, "bold", "#0B1020")
        self.espacio(0.04)

    def seccion(self, s: str, reserva: float = 0.8) -> None:
        self._hay_sitio(reserva)
        self.espacio(0.1)
        self.texto(s, 12, "bold", "#1F3A93")
        self.fig.add_artist(plt.Line2D([MARGEN / ANCHO_A4, (ANCHO_A4 - MARGEN) / ANCHO_A4],
                                       [1 - (self.y + 0.02) / ALTO_A4] * 2, color="#1F3A93", lw=0.7))
        self.espacio(0.08)

    def lista(self, items: list[str], numerada: bool = False) -> None:
        for i, t in enumerate(items, 1):
            self.texto(f"{i}. {t}" if numerada else f"•  {t}", 10, sangria=0.15)

    def ecuacion(self, tex: str) -> None:
        self._hay_sitio(0.55)
        try:
            self.fig.text(0.5, 1 - (self.y + 0.05) / ALTO_A4, f"${tex}$", fontsize=13, ha="center", va="top",
                          color="#111111")
            self.fig.canvas.draw()                      # fuerza el análisis: si la sintaxis falla, se avisa aquí
        except ValueError:
            self.fig.texts.pop()
            self.texto(tex, 10, familia="DejaVu Sans Mono", sangria=0.3)
            return
        self.y += 0.5

    def tabla(self, titulo: str, encabezados: list[str], filas: list[list[str]]) -> None:
        columnas = max(len(encabezados), 1)
        anchos = [0.5, 0.3, 0.2][:columnas] if columnas <= 3 else [1.0 / columnas] * columnas
        s = sum(anchos)
        anchos = [a / s * self.ancho_util for a in anchos]

        def medir(celdas):
            envueltas = [textwrap.wrap(str(c), max(8, int(a * 72 / (9 * 0.58)))) or [""] for c, a in zip(celdas, anchos)]
            return envueltas, max(len(e) for e in envueltas) * 9 * 1.45 / 72 + 0.06

        def fila(celdas, peso="normal", fondo=None):
            envueltas, alto = medir(celdas)
            self._hay_sitio(alto)
            if fondo:
                self.fig.add_artist(plt.Rectangle((MARGEN / ANCHO_A4, 1 - (self.y + alto) / ALTO_A4),
                                                  self.ancho_util / ANCHO_A4, alto / ALTO_A4, color=fondo, zorder=0))
            x = MARGEN
            for e, a in zip(envueltas, anchos):
                for k, linea in enumerate(e):
                    self.fig.text((x + 0.04) / ANCHO_A4, 1 - (self.y + 0.03 + k * 9 * 1.45 / 72) / ALTO_A4, linea,
                                  fontsize=9, fontweight=peso, va="top", ha="left", color="#111111")
                x += a
            self.y += alto

        cab = encabezados[:columnas] if encabezados else [""] * columnas
        cuerpo = [list(f) + [""] * (columnas - len(f)) for f in filas]
        alturas = [medir(f)[1] for f in cuerpo]
        alto_cab = medir(cab)[1]
        libre = ALTO_A4 - MARGEN - 0.2 - self.y
        pagina_util = ALTO_A4 - 2 * MARGEN - 0.2
        total = 0.25 + alto_cab + sum(alturas)
        minimo = 0.25 + alto_cab + sum(alturas[:2])          # título + encabezado + al menos dos filas
        if (total > libre and total <= pagina_util) or minimo > libre:
            self.nueva()                                        # tabla corta: entera en la página siguiente
        self.texto(titulo, 10, "bold")
        fila(cab, "bold", "#DDE3F0")
        for i, f in enumerate(cuerpo):
            if self.y + alturas[i] > ALTO_A4 - MARGEN - 0.2:     # tabla larga: continúa con su encabezado
                self.nueva()
                self.texto(f"{titulo} (continuación)", 10, "bold")
                fila(cab, "bold", "#DDE3F0")
            fila(f, fondo="#F4F6FB" if i % 2 else None)
        self.espacio(0.1)

    def imagen(self, figura, ancho: float | None = None) -> None:
        buf = io.BytesIO()
        figura.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(figura)
        buf.seek(0)
        img = plt.imread(buf)
        h_px, w_px = img.shape[:2]
        w = min(ancho or self.ancho_util, self.ancho_util)
        h = w * h_px / w_px
        tope = min(ALTO_A4 - 2 * MARGEN - 0.4, 4.2)          # una figura no ocupa más de ~4 in de alto
        if h > tope:
            h, w = tope, tope * w_px / h_px
        self._hay_sitio(h + 0.1)
        eje = self.fig.add_axes([(MARGEN + (self.ancho_util - w) / 2) / ANCHO_A4, 1 - (self.y + h) / ALTO_A4,
                                 w / ANCHO_A4, h / ALTO_A4])
        eje.imshow(img)
        eje.axis("off")
        self.y += h + 0.1

    def renglones_en_blanco(self, n: int) -> None:
        for _ in range(n):
            self._hay_sitio(0.3)
            self.y += 0.3
            self.fig.add_artist(plt.Line2D([MARGEN / ANCHO_A4, (ANCHO_A4 - MARGEN) / ANCHO_A4],
                                           [1 - self.y / ALTO_A4] * 2, color="#999999", lw=0.5))

    def cerrar(self, pdf: PdfPages) -> None:
        total = len(self.paginas)
        for i, fig in enumerate(self.paginas, 1):
            fig.text(MARGEN / ANCHO_A4, 0.03, self.pie, fontsize=8, color="#555555", ha="left")
            fig.text(1 - MARGEN / ANCHO_A4, 0.03, f"Página {i} de {total}", fontsize=8, color="#555555", ha="right")
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)


def pdf_informe(informe: Informe, fecha: datetime | None = None) -> bytes:
    """Informe en PDF (A4). Lanza ValueError si el informe está incompleto."""
    validar(informe)
    informe.generado = (fecha or datetime.now().astimezone()).strftime("%Y-%m-%d %H:%M")
    lienzo = _Lienzo(f"Quantum Lab · {informe.simulador}")
    # El tema de la aplicación es oscuro y se aplica a Matplotlib globalmente: el informe usa su propio estilo claro.
    with plt.style.context("default"), plt.rc_context({"text.usetex": False, "font.family": "DejaVu Sans",
                                                         "mathtext.fontset": "dejavusans", "savefig.facecolor": "white"}):
        lienzo.titulo(informe.titulo)
        lienzo.texto(f"Simulador: {informe.simulador}   ·   Archivo generado el {informe.generado}", 9, color="#555555")
        lienzo.texto("Los valores de este informe los calcula un modelo teórico: no son mediciones experimentales.",
                     9, estilo="italic", color="#555555")
        lienzo.seccion("1. Objetivo")
        lienzo.texto(informe.objetivo)
        lienzo.seccion("2. Modelo teórico")
        lienzo.texto(informe.modelo)
        if informe.ecuaciones:
            lienzo.seccion("3. Ecuaciones")
            for e in informe.ecuaciones:
                lienzo.ecuacion(e)
        lienzo.seccion("4. Datos y parámetros utilizados (entrada)")
        lienzo.tabla("Parámetros", ["Magnitud", "Valor", "Unidad"], [list(f) for f in informe.parametros])
        if informe.procedimiento:
            lienzo.seccion("5. Procedimiento de cálculo")
            lienzo.lista(informe.procedimiento, numerada=True)
        lienzo.seccion("6. Resultados calculados por el simulador")
        lienzo.tabla("Resultados", ["Magnitud", "Valor", "Unidad"], [list(f) for f in informe.resultados])
        for titulo, enc, filas in informe.tablas:
            lienzo.tabla(titulo, enc, filas)
        if informe.figuras:
            lienzo.seccion("7. Gráficas", reserva=3.6)
            for fig in informe.figuras:
                lienzo.imagen(fig)
        if informe.preguntas:
            lienzo.seccion("8. Preguntas de análisis")
            lienzo.lista(informe.preguntas, numerada=True)
        lienzo.seccion("9. Conclusiones del estudiante")
        lienzo.texto("Esta sección la escribe la persona que realiza el experimento; el simulador no la rellena.",
                     9, estilo="italic", color="#555555")
        if informe.conclusiones.strip():
            lienzo.texto(informe.conclusiones.strip())
        else:
            lienzo.renglones_en_blanco(8)
        if informe.referencias:
            lienzo.seccion("Referencias")
            lienzo.lista(informe.referencias)
        buf = io.BytesIO()
        with PdfPages(buf, metadata={"Title": informe.titulo, "Creator": "Quantum Lab", "Subject": informe.simulador}) as pdf:
            lienzo.cerrar(pdf)
    return buf.getvalue()


def figura_clara(ancho: float = 7.0, alto: float = 3.2, **kw):
    """Figura para el informe: fondo blanco y estilo claro (se imprime bien). Úsala dentro de `with estilo_claro():`."""
    return plt.subplots(figsize=(ancho, alto), facecolor="white", **kw)


def estilo_claro():
    """Contexto de Matplotlib con estilo claro, independiente del tema oscuro de la aplicación."""
    return plt.style.context("default")


# =====================================================================
# Interfaz
# =====================================================================
def boton_informe(construir, clave: str, archivo: str) -> None:
    """
    Sección «Informe del experimento»: caja de conclusiones del estudiante y botones PDF/CSV.
    `construir(conclusiones: str) -> Informe` se llama solo al pulsar para preparar los archivos.
    """
    import streamlit as st

    import quantum_lab_comun as qc

    with st.expander("Informe del experimento (PDF y CSV)", expanded=False):
        st.markdown("El informe reúne objetivo, modelo, ecuaciones, parámetros, tablas, gráficas y resultados "
                    "**calculados por el simulador**, más tus conclusiones. Lo que escribas abajo se incluye en el PDF "
                    "como texto del estudiante; si lo dejas vacío, el PDF trae renglones para escribirlo a mano.")
        texto = st.text_area("Conclusiones (opcional)", key=f"{clave}_concl", height=100,
                             placeholder="Escribe aquí tu interpretación de los resultados…")
        if st.button("Preparar informe", key=f"{clave}_prep", icon=":material/description:"):
            try:
                inf = construir(texto)
                st.session_state[f"{clave}_pdf"] = pdf_informe(inf)
                st.session_state[f"{clave}_csv"] = csv_informe(inf)
            except ValueError as error:
                qc.error(error)
                return
        if st.session_state.get(f"{clave}_pdf"):
            c1, c2 = st.columns(2)
            c1.download_button("Descargar informe (PDF)", st.session_state[f"{clave}_pdf"], file_name=f"{archivo}.pdf",
                               mime="application/pdf", key=f"{clave}_dl_pdf", icon=":material/picture_as_pdf:",
                               width="stretch")
            c2.download_button("Descargar datos (CSV)", st.session_state[f"{clave}_csv"], file_name=f"{archivo}.csv",
                               mime="text/csv", key=f"{clave}_dl_csv", icon=":material/table:", width="stretch")
            st.caption("El informe se preparó con los parámetros del momento de pulsar «Preparar informe». "
                       "Si cambias algo, vuelve a prepararlo.")
