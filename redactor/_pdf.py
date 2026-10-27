"""
redactor/_pdf.py — Del documento del cuaderno al PDF (A4), con el mismo motor de maquetación de los informes
============================================================================================================

Cada bloque se dibuja con el motor de `informes` (páginas, tablas que continúan con su encabezado, títulos que no quedan
solos al pie). Si un bloque falla (por ejemplo, una expresión que no se puede graficar) el PDF no se cancela: en su lugar aparece
un recuadro con el motivo, y la interfaz lista esos problemas antes de exportar.

Texto: párrafos con fórmulas entre $…$ (subconjunto de LaTeX que entiende Matplotlib: \\frac, \\sqrt, \\hbar, letras griegas,
\\int, \\sum, ^ y _). Una fórmula que Matplotlib no entiende se escribe como texto literal y se avisa.
"""

from __future__ import annotations

import io
import re
from datetime import datetime

from informes import ALTO_A4, ANCHO_A4, MARGEN, _Lienzo
from redactor import _graficas, _modelo, _simuladores, _talleres, _verificar
from redactor._expr import ErrorExpresion, a_latex, leer_expresion, partes_de_igualdad

MARCAS = {_verificar.OK: ("✓", "#1E8449"), _verificar.ERROR: ("✗", "#B03A2E"), _verificar.NO_VERIFICABLE: ("?", "#CA6F1E"),
          _verificar.SINTAXIS: ("✗", "#B03A2E"), _verificar.INICIO: ("", "#555555")}


def formula_valida(tex: str) -> bool:
    """¿Entiende Matplotlib esta fórmula? (se comprueba antes de dibujar para no perder el PDF por una llave sin cerrar)."""
    from matplotlib import mathtext
    try:
        mathtext.MathTextParser("path").parse(f"${tex}$")
    except (ValueError, RuntimeError):
        return False
    return True


def _limpiar_markdown(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", s)
    s = s.replace("`", "")
    s = s.replace("\\$", "＄")
    return s


def segmentos(texto: str) -> list[tuple[str, bool]]:
    """Divide un párrafo en [(trozo, es_formula)] según los pares $…$. Una fórmula inválida pasa a texto literal."""
    texto = _limpiar_markdown(texto)
    partes, salida = re.split(r"(\$[^$\n]+\$)", texto), []
    for p in partes:
        if len(p) >= 3 and p.startswith("$") and p.endswith("$"):
            if formula_valida(p[1:-1]):
                salida.append((p, True))
            else:
                salida.append((p[1:-1], False))
        elif p:
            salida.append((p.replace("＄", "$"), False))
    return salida


class Lienzo(_Lienzo):
    """Lienzo de informes con párrafos que mezclan texto y fórmulas."""

    def parrafo(self, texto: str, tam: float = 10.0, sangria: float = 0.0, color: str = "#111111", estilo: str = "normal") -> None:
        caracteres = max(20, int((self.ancho_util - sangria) * 72 / (tam * 0.58)))
        for bloque in str(texto).split("\n"):
            if not bloque.strip():
                self.espacio(0.08)
                continue
            fichas = []                                   # (palabra, longitud estimada); «$x$.» es UNA palabra (sin espacio antes del punto)
            for palabra in re.findall(r"(?:\$[^$\n]+\$|[^\s$])+", _limpiar_markdown(bloque)):
                partes = segmentos(palabra)
                texto_palabra = "".join(p if es_f else p.replace("$", "") for p, es_f in partes)
                n = sum(int(len(p) * 0.7) if es_f else len(p) for p, es_f in partes)
                fichas.append((texto_palabra, n))
            lineas, actual, largo = [], [], 0
            for ficha, n in fichas:
                if actual and largo + 1 + n > caracteres:
                    lineas.append(" ".join(actual))
                    actual, largo = [], 0
                actual.append(ficha)
                largo += n + (1 if len(actual) > 1 else 0)
            if actual:
                lineas.append(" ".join(actual))
            paso = tam * 1.5 / 72
            for linea in lineas:
                alta = any(c in linea for c in ("\\frac", "\\sqrt", "\\int", "\\sum"))      # fracciones en línea: más aire
                if alta:
                    self.y += 0.07
                self._hay_sitio(paso * (1.4 if alta else 1.0))
                self.fig.text((MARGEN + sangria) / ANCHO_A4, 1 - self.y / ALTO_A4, linea, fontsize=tam, color=color, va="top",
                              ha="left", style=estilo)
                self.y += paso * (1.4 if alta else 1.0)

    def aviso(self, mensaje: str) -> None:
        self.parrafo(f"No se pudo generar este bloque: {mensaje}", 9.0, 0.15, "#B03A2E", "italic")

    def pie_figura(self, prefijo: str, numero: int, pie: str) -> None:
        etiqueta = f"{prefijo} {numero}." + (f" {pie.strip()}" if pie.strip() else "")
        self.parrafo(etiqueta, 9.0, 0.0, "#444444", "italic")
        self.espacio(0.06)


# ---------------------------------------------------------------------
# Bloques
# ---------------------------------------------------------------------
def _latex_de_linea(texto: str) -> str | None:
    try:
        partes = partes_de_igualdad(texto)
        return " = ".join(a_latex(leer_expresion(p, evaluar=False)) for p in partes)
    except ErrorExpresion:
        return None


def _desarrollo(lienzo: Lienzo, datos: dict) -> None:
    lineas = [ln for ln in datos["lineas"].splitlines() if ln.strip()]
    if datos.get("comentario", "").strip():
        lienzo.parrafo(datos["comentario"])
    tabla_datos = _leer_datos(datos.get("datos", ""))
    pasos = _verificar.verificar_pasos(lineas, tabla_datos, datos.get("tol_pct", 1.0) / 100.0) if datos.get("marcas") else None
    if datos.get("datos", "").strip():
        lienzo.parrafo("Datos: " + "; ".join(f"${_latex_nombre(k)} = {v}$" if formula_valida(f"{_latex_nombre(k)} = {v}") else f"{k} = {v}"
                                              for k, v in tabla_datos.items()), 9.5)
    for i, linea in enumerate(lineas):
        tex = _latex_de_linea(linea)
        paso = pasos[i] if pasos else None
        if tex and formula_valida(tex):
            lienzo.ecuacion(tex)
        else:
            lienzo.texto(linea, 10, familia="DejaVu Sans Mono", sangria=0.3)
        if paso:
            marca, color = MARCAS[paso.estado]
            if marca:
                lienzo.fig.text((ANCHO_A4 - MARGEN) / ANCHO_A4, 1 - (lienzo.y - 0.38) / ALTO_A4, marca, fontsize=13, color=color,
                                ha="right", va="top", fontweight="bold")
            if paso.estado in (_verificar.ERROR, _verificar.NO_VERIFICABLE, _verificar.SINTAXIS):
                lienzo.parrafo(paso.mensaje, 8.5, 0.3, color, "italic")
                if paso.esperado_latex and formula_valida(paso.esperado_latex):
                    lienzo.parrafo(f"Revisión: se esperaba ${paso.esperado_latex}$", 8.5, 0.3, color, "italic")


def _latex_nombre(nombre: str) -> str:
    try:
        return a_latex(leer_expresion(nombre, evaluar=False))
    except ErrorExpresion:
        return nombre


def _leer_datos(texto: str) -> dict:
    salida = {}
    for ln in re.split(r"[\n;]", texto or ""):
        if "=" in ln:
            k, v = (p.strip() for p in ln.split("=", 1))
            if k and v:
                salida[k] = v
    return salida


def _celda(texto: str) -> str:
    """Texto de una celda: conserva las fórmulas válidas ($…$) y deja literales las que Matplotlib no entiende."""
    t = re.sub(r"\s+", " ", _limpiar_markdown(texto)).strip()
    return "".join(p if es_f else p.replace("$", "") for p, es_f in segmentos(t))


def _bloque(lienzo: Lienzo, bloque: dict, contador: dict) -> None:
    t, d = bloque["tipo"], bloque["datos"]
    if t == "titulo":
        if d["nivel"] == 1:
            lienzo.seccion(d["texto"], reserva=1.2)
        else:
            lienzo.espacio(0.08)
            lienzo.texto(d["texto"], 11, "bold", "#1F3A93")
    elif t == "texto":
        lienzo.parrafo(d["texto"])
        lienzo.espacio(0.06)
    elif t == "ecuacion":
        if not d["latex"].strip():
            return
        if not formula_valida(d["latex"]):
            raise ValueError(f"la fórmula «{d['latex'][:60]}» no es válida para el PDF (revisa llaves y comandos).")
        lienzo.ecuacion(d["latex"])
        if d["etiqueta"].strip():
            lienzo.fig.text((ANCHO_A4 - MARGEN) / ANCHO_A4, 1 - (lienzo.y - 0.33) / ALTO_A4, f"({d['etiqueta'].strip()})",
                            fontsize=10, color="#444444", ha="right", va="top")
    elif t == "desarrollo":
        _desarrollo(lienzo, d)
    elif t == "grafica_funcion":
        fig = _graficas.grafica_funcion(d["expresiones"], d["variable"], d["xmin"], d["xmax"], d["constantes"], d["titulo"],
                                        d["xlabel"], d["ylabel"])
        contador["fig"] += 1
        lienzo.imagen(fig, ancho=5.2)
        lienzo.pie_figura("Figura", contador["fig"], d["pie"])
    elif t == "grafica_datos":
        fig, ajuste = _graficas.grafica_datos(d["tabla"], d["tipo"], d["titulo"], d["xlabel"], d["ylabel"])
        contador["fig"] += 1
        lienzo.imagen(fig, ancho=5.2)
        extra = ""
        if ajuste:
            extra = f" Ajuste lineal: pendiente = {ajuste['pendiente']:.5g}, ordenada = {ajuste['ordenada']:.5g}, R² = {ajuste['r2']:.5f}."
            if ajuste["u_pendiente"] is not None:
                extra += f" Incertidumbres estándar: u(m) = {ajuste['u_pendiente']:.2g}, u(b) = {ajuste['u_ordenada']:.2g}."
        lienzo.pie_figura("Figura", contador["fig"], d["pie"] + extra)
    elif t == "simulador":
        sim = _simuladores.SIMULADORES[d["sim"]]
        inf = _simuladores.construir(d["sim"], d["valores"])
        lienzo.texto(f"Simulador: {sim.nombre}", 10.5, "bold", "#1F3A93")
        lienzo.tabla("Parámetros", ["Magnitud", "Valor", "Unidad"], [list(f) for f in inf.parametros])
        lienzo.tabla("Resultados calculados por el simulador", ["Magnitud", "Valor", "Unidad"], [list(f) for f in inf.resultados])
        for fig in inf.figuras:
            contador["fig"] += 1
            lienzo.imagen(fig, ancho=5.4)
            lienzo.pie_figura("Figura", contador["fig"], d["pie"] or f"Generada con el simulador «{sim.nombre}».")
    elif t == "taller":
        cal = _talleres.calificar_bloque(d)
        if cal is None:
            lienzo.aviso("no hay una pregunta de taller elegida.")
            return
        lienzo.texto(f"Taller — pregunta {cal['id']}", 10.5, "bold", "#1F3A93")
        lienzo.parrafo(cal["enunciado"])
        filas = [[_celda(p["etiqueta"]), (p["respuesta"] + " " + p["unidad"]).strip() or "—", p["estado_texto"]]
                 for p in cal["partes"]]
        lienzo.tabla("Respuestas y calificación", ["Parte", "Respuesta", "Resultado"], filas)
        lienzo.parrafo(f"Puntaje: {cal['puntos']:.3g} de {cal['maximo']:.3g}.", 9.5)
        if d.get("incluir_solucion") and cal["solucion"]:
            lienzo.parrafo("Solución del taller:", 9.5, color="#444444")
            lienzo.parrafo(cal["solucion"], 9.0)
    elif t == "tabla" and d["encabezados"] and d["filas"]:
        lienzo.tabla(d["titulo"] or "Tabla", d["encabezados"], [list(f) for f in d["filas"]])


def _construir(doc: dict) -> tuple[Lienzo, list[tuple[int, str]]]:
    doc = _modelo.validar_documento(doc)
    lienzo = Lienzo(f"Quantum Lab · {doc['titulo'] or 'Informe'}")
    problemas: list[tuple[int, str]] = []
    fecha = datetime.now().astimezone().strftime("%Y-%m-%d")
    lienzo.titulo(doc["titulo"] or "Informe")
    lienzo.texto((f"{doc['autor']}   ·   " if doc["autor"].strip() else "") + f"Generado con QUANTUM LAB el {fecha}", 9, color="#555555")
    contador = {"fig": 0}
    for i, bloque in enumerate(doc["bloques"], 1):
        try:
            _bloque(lienzo, bloque, contador)
        except (_graficas.ErrorGrafica, ValueError, ErrorExpresion) as error:
            problemas.append((i, str(error)))
            lienzo.aviso(f"bloque {i} ({_modelo.TIPOS[bloque['tipo']][0].lower()}): {error}")
    return lienzo, problemas


def problemas_del_documento(doc: dict) -> list[tuple[int, str]]:
    """Bloques que no se pueden dibujar y por qué (para avisar en la interfaz antes de exportar)."""
    lienzo, problemas = _construir(doc)
    import matplotlib.pyplot as plt
    for fig in lienzo.paginas:
        plt.close(fig)
    return problemas


def pdf_cuaderno(doc: dict) -> bytes:
    """PDF del cuaderno completo."""
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    with plt.style.context("default"), plt.rc_context({"text.usetex": False, "font.family": "DejaVu Sans",
                                                         "mathtext.fontset": "dejavusans", "savefig.facecolor": "white"}):
        lienzo, _ = _construir(doc)
        buf = io.BytesIO()
        with PdfPages(buf, metadata={"Title": doc.get("titulo", "Informe"), "Creator": "Quantum Lab"}) as pdf:
            lienzo.cerrar(pdf)
    return buf.getvalue()


def paginas_png(doc: dict, dpi: int = 70) -> list[bytes]:
    """Vista previa: cada página del PDF como PNG."""
    import matplotlib.pyplot as plt
    with plt.style.context("default"), plt.rc_context({"text.usetex": False, "font.family": "DejaVu Sans",
                                                         "mathtext.fontset": "dejavusans", "savefig.facecolor": "white"}):
        lienzo, _ = _construir(doc)
        total, imagenes = len(lienzo.paginas), []
        for i, fig in enumerate(lienzo.paginas, 1):
            fig.text(MARGEN / ANCHO_A4, 0.03, lienzo.pie, fontsize=8, color="#555555", ha="left")
            fig.text(1 - MARGEN / ANCHO_A4, 0.03, f"Página {i} de {total}", fontsize=8, color="#555555", ha="right")
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
            imagenes.append(buf.getvalue())
            plt.close(fig)
    return imagenes

