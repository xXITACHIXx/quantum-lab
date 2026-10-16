"""
quantum_lab_portada.py — Página de inicio de QUANTUM LAB: el observatorio
=========================================================================

La portada es una escena (ver `quantum_lab_escena`): el observatorio animado y, debajo, los módulos como **destinos** en cuatro
capítulos. Los simuladores se presentan en una composición asimétrica (un destino mayor y dos menores por capítulo, alternando el lado);
las estaciones de estudio y de verificación, como tarjetas compactas. Cada destino es un contenedor `ql_dest_<clave>` con un `st.button`
real que cubre la tarjeta, de modo que la navegación es la de Streamlit.

`MODULOS` es la única lista de módulos (número, categoría, tipo, título, descripción, ecuación). Las cifras de la franja inferior del
observatorio se calculan con los datos de la aplicación; no hay estadísticas de uso ni indicadores inventados.
"""

from __future__ import annotations

import html

import streamlit as st

import quantum_lab_arte as arte
import quantum_lab_comun as qc
import quantum_lab_escena as escena

SIMULADOR, ESTUDIO, VERIFICACION = "simulador", "estudio", "verificacion"

# (clave, número, categoría, tipo, título, descripción, ecuación o lema)
MODULOS = [
    ("caja", "01", "Mecánica cuántica", SIMULADOR, "Partícula en una caja",
     "Estados estacionarios, energías, longitud de onda de De Broglie, nodos, superposición e interferencia.", "Eₙ = n²π²ħ² / 2ma²"),
    ("oscilador", "02", "Mecánica cuántica", SIMULADOR, "Oscilador armónico",
     "Polinomios de Hermite, energía cinética y potencial, teorema del virial, efecto túnel y superposiciones.", "Eₙ = ħω (n + ½)"),
    ("esfera", "03", "Mecánica cuántica", SIMULADOR, "Partícula en una esfera",
     "Armónicos esféricos en 3D, nodos y simetrías, orbitales complejos y reales, y un modelo confinado con funciones de Bessel.",
     "L² Yₗᵐ = ħ² l(l+1) Yₗᵐ"),
    ("fotoelectrico", "04", "Fundamentos", SIMULADOR, "Efecto fotoeléctrico",
     "Frecuencia umbral, energía de los electrones emitidos, corriente fotoeléctrica y constante de Planck al estilo de Millikan.", "Kₘₐₓ = hν − Φ"),
    ("bohr", "05", "Fundamentos", SIMULADOR, "Átomo de hidrógeno",
     "Modelo de Bohr: niveles, transiciones y series espectrales. Átomo cuántico en 3D con nubes de probabilidad.", "Eₙ = −13.6 eV / n²"),
    ("incertidumbre", "06", "Fundamentos", SIMULADOR, "Principio de incertidumbre",
     "Paquetes de ondas en posición y momento, límite de Heisenberg, ensanchamiento de una partícula libre y difracción por una rendija.", "Δx · Δp ≥ ħ / 2"),
    ("ruta", "07", "Teoría y repaso", ESTUDIO, "Ruta de estudio",
     "Recorrido por dominio de cada tema, con prerrequisitos y siguiente paso sugerido.", ""),
    ("teoria", "08", "Teoría y repaso", ESTUDIO, "Centro de teoría",
     "Teoría de cada tema con enlaces a su simulador, experimentos guiados y autoevaluación.", ""),
    ("formulario", "09", "Teoría y repaso", ESTUDIO, "Formulario",
     "Constantes con incertidumbre, conversor de unidades, fórmulas por tema y masas isotópicas.", ""),
    ("talleres", "10", "Teoría y repaso", ESTUDIO, "Talleres de repaso",
     "Problemas al estilo de los talleres evaluativos, calificados por partes y con solución justificada.", ""),
    ("ejercicios", "11", "Teoría y repaso", ESTUDIO, "Ejercicios de práctica",
     "Problemas de clase y del libro con pistas y solución paso a paso.", ""),
    ("examen", "12", "Teoría y repaso", ESTUDIO, "Modo examen",
     "Evaluación cronometrada con ejercicios del banco, calificada sobre 5.0.", ""),
    ("repaso", "13", "Teoría y repaso", ESTUDIO, "Repaso personalizado",
     "Ejercicios por repasar, temas con menor precisión y errores más frecuentes.", ""),
    ("verificacion", "14", "Verificación", VERIFICACION, "Verificación",
     "Contraste de los resultados con cálculos independientes y con los cuadernos de Colab.", ""),
    ("pruebas", "15", "Verificación", VERIFICACION, "Pruebas numéricas",
     "Ejecución de todas las comprobaciones numéricas de la aplicación.", ""),
]
CATEGORIAS = ("Mecánica cuántica", "Fundamentos", "Teoría y repaso", "Verificación")
CAPITULOS = {
    "Mecánica cuántica": ("01", "Sistemas modelo", "Soluciones exactas de la ecuación de Schrödinger: confinamiento, oscilación y rotación."),
    "Fundamentos": ("02", "Origen de la teoría", "Los experimentos y modelos que obligaron a abandonar la física clásica."),
    "Teoría y repaso": ("03", "Estaciones de estudio", "Teoría, fórmulas, práctica y evaluación conectadas con cada simulador."),
    "Verificación": ("04", "Control de calidad", "Contraste de los resultados con cálculos independientes."),
}
ID_SIMULADORES = "ql-simuladores"
ID_ESTUDIO = "ql-estudio"
_CLASE = {SIMULADOR: "ql-dest-sim", ESTUDIO: "ql-dest-est", VERIFICACION: "ql-dest-ver"}
# Composición asimétrica: proporciones de columna y posición del destino mayor en cada capítulo de simuladores.
COMPOSICION = {"Mecánica cuántica": ([1.55, 1, 1], 0), "Fundamentos": ([1, 1, 1.55], 2)}


def modulo(clave: str):
    return next(m for m in MODULOS if m[0] == clave)


def tarjeta_html(clave: str, numero: str, categoria: str, tipo: str, titulo: str, descripcion: str, lema: str,
                 mayor: bool = False, compacta: bool = False) -> str:
    """HTML de un destino (los textos se escapan; los SVG son los generados por `quantum_lab_arte`)."""
    e = html.escape
    clases = " ".join(c for c in ("ql-dest", _CLASE[tipo], "ql-dest-mayor" if mayor else "", "ql-dest-compacta" if compacta else "") if c)
    prefijo = {SIMULADOR: "SIM", ESTUDIO: "EST", VERIFICACION: "VER"}[tipo]
    ecuacion = f'<span class="ql-ecuacion">{e(lema)}</span>' if lema else "<span></span>"
    entrar = "Entrar al simulador" if tipo == SIMULADOR else "Abrir"
    return (f'<div class="{clases}"><span class="ql-dest-luz"></span>'
            f'<div class="ql-dest-arte ql-miniatura">{arte.svg(clave)}</div>'
            f'<div class="ql-dest-cuerpo"><div class="ql-dest-meta"><span class="ql-num">{prefijo}·{e(numero)}</span><span class="ql-chip">{e(categoria)}</span></div>'
            f'<h3>{e(titulo)}</h3><p>{e(descripcion)}</p>'
            f'<div class="ql-dest-pie">{ecuacion}<span class="ql-dest-entrar">{entrar}<i>→</i></span></div></div>'
            f'<span class="ql-dest-linea"></span></div>')


def destino(m, ir_a, mayor: bool = False, compacta: bool = False) -> None:
    """Un destino: contenedor con clave + tarjeta + botón real (el CSS lo extiende sobre la tarjeta)."""
    clave, _, _, tipo, titulo, *_ = m
    with st.container(key=f"ql_dest_{clave}"):
        st.markdown(tarjeta_html(*m, mayor=mayor, compacta=compacta), unsafe_allow_html=True)
        etiqueta = f"Abrir el simulador: {titulo}" if tipo == SIMULADOR else f"Abrir {titulo}"
        st.button(etiqueta, key=f"ql_abrir_{clave}", on_click=ir_a, args=(clave,), width="stretch")


def lecturas() -> list[tuple[str, str]]:
    """Cifras reales de la aplicación para la franja del observatorio."""
    import ejercicios
    import formulario
    import talleres
    import teoria
    temas = [t for _, t in teoria.todos_los_temas() if t.estado == teoria.DISPONIBLE]
    formulas = sum(len(s.todas()) for s in formulario.SECCIONES)
    return [(str(sum(m[3] == SIMULADOR for m in MODULOS)), "simuladores"), (str(len(temas)), "temas de teoría"),
            (str(len(ejercicios.EJERCICIOS)), "ejercicios"), (str(formulas), "fórmulas"), (str(len(talleres.TALLERES)), "talleres")]


def _hero() -> None:
    st.markdown(escena.observatorio_html(arte.observatorio(), lecturas(), ID_SIMULADORES, ID_ESTUDIO), unsafe_allow_html=True)


def pagina_inicio(ir_a, sugerencia=None) -> None:
    """Portada. `ir_a(clave)` es el callback de navegación; `sugerencia()` dibuja la tarjeta «Siguiente paso sugerido» (opcional)."""
    _hero()
    for categoria in CATEGORIAS:
        modulos = [m for m in MODULOS if m[2] == categoria]
        num, etiqueta, descripcion = CAPITULOS[categoria]
        ancla = {"Mecánica cuántica": ID_SIMULADORES, "Teoría y repaso": ID_ESTUDIO}.get(categoria, "")
        st.markdown(escena.capitulo_html(num, etiqueta, categoria, descripcion, ancla), unsafe_allow_html=True)
        if categoria in COMPOSICION:
            proporciones, mayor = COMPOSICION[categoria]
            for i, (col, m) in enumerate(zip(st.columns(proporciones, gap="medium"), modulos)):
                with col:
                    destino(m, ir_a, mayor=(i == mayor))
            continue
        if categoria == "Teoría y repaso" and sugerencia:
            sugerencia()
        for i in range(0, len(modulos), 2):
            for col, m in zip(st.columns(2, gap="medium"), modulos[i:i + 2]):
                with col:
                    destino(m, ir_a, compacta=True)
    st.markdown("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.expander("Cómo usar la aplicación", icon=":material/help:"):
            st.markdown("1. Seleccionar un destino en esta página o una sección en la barra lateral.\n"
                        "2. Ajustar los **parámetros del sistema** en el panel superior; los resultados se recalculan al instante.\n"
                        "3. Recorrer las **pestañas**: resultados, visualización, valores detallados e interpretación.\n"
                        "4. «Configuración de ejemplo» carga casos típicos; «Restaurar valores iniciales» vuelve al comienzo.\n"
                        "5. **Ver la teoría de este tema** abre su explicación; **Guía de práctica** propone experimentos; **Autoevaluación** corrige preguntas de opción múltiple.\n"
                        "6. Las gráficas y tablas se pueden **descargar** y «Compartir configuración» da un enlace con los parámetros exactos.")
    with c2:
        with st.expander("Alcance del modelo", icon=":material/info:"):
            st.markdown("- Las **fórmulas** (ψₙ, Eₙ, Hermite, Yₗᵐ…) son exactas; las **integrales y derivadas** se calculan en mallas numéricas con el error documentado en cada simulador.\n"
                        "- Las deformaciones y «lóbulos» de la esfera son recursos geométricos, no objetos físicos.\n"
                        "- Herramienta **educativa**: una partícula, sin espín ni interacciones; no describe átomos reales.\n"
                        "- El observatorio, las ilustraciones y sus animaciones son **conceptuales**; no son resultados del simulador.")
