"""
quantum_lab_portada.py — Página de inicio de QUANTUM LAB
========================================================

Cabecera con ilustración y tarjetas de navegación por categoría. `MODULOS` es la única lista de módulos de la portada (número, categoría,
título, descripción); las claves son las de `quantum_lab.PAGINAS`. Las tarjetas solo usan datos reales: no muestran estadísticas de uso
ni indicadores de progreso (el progreso del estudiante vive en la Ruta de estudio).
"""

from __future__ import annotations

import html

import streamlit as st

import quantum_lab_arte as arte
import quantum_lab_comun as qc

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
ACCION = {SIMULADOR: "Abrir simulador", ESTUDIO: "Abrir", VERIFICACION: "Abrir"}
ID_SIMULADORES = "ql-simuladores"


def tarjeta_html(clave: str, numero: str, categoria: str, tipo: str, titulo: str, descripcion: str, lema: str) -> str:
    """HTML de una tarjeta (los textos se escapan; los SVG son los generados por `quantum_lab_arte`)."""
    e = html.escape
    if tipo == SIMULADOR:
        cabecera = f'<div class="ql-miniatura">{arte.svg(clave)}</div>'
    else:
        cabecera = f'<div class="ql-icono-caja">{arte.icono(clave, "var(--ql-verde)" if tipo == VERIFICACION else None)}</div>'
    ecuacion = f'<div class="ql-ecuacion">{e(lema)}</div>' if lema else ""
    return (f'<div class="ql-card ql-card-{tipo}">{cabecera}'
            f'<div class="ql-card-cab"><span class="ql-num">{e(numero)}</span><span class="ql-chip">{e(categoria)}</span></div>'
            f'<h3>{e(titulo)}</h3><p>{e(descripcion)}</p>{ecuacion}</div>')


def _hero() -> None:
    st.markdown(
        '<div class="ql-hero"><div class="ql-hero-texto">'
        f'<div class="ql-hero-marca">{arte.icono("ruta", "var(--ql-violeta)").replace("ql-icono", "ql-icono-marca")}'
        '<span class="ql-etiqueta">Laboratorio interactivo de mecánica cuántica</span></div>'
        '<div class="ql-titulo">Quantum Lab</div>'
        '<p class="ql-subtitulo">Funciones de onda, energías, densidades de probabilidad y armónicos esféricos calculados a partir de parámetros físicos '
        'reales, cada uno con su comprobación numérica.</p>'
        f'<a class="ql-boton" href="#{ID_SIMULADORES}">Explorar simuladores</a></div>'
        f'<div class="ql-hero-arte">{arte.portada()}</div></div>', unsafe_allow_html=True)


def pagina_inicio(ir_a, sugerencia=None) -> None:
    """Portada. `ir_a(clave)` es el callback de navegación; `sugerencia()` dibuja la tarjeta «Siguiente paso sugerido» (opcional)."""
    _hero()
    st.markdown(f'<div id="{ID_SIMULADORES}"></div>', unsafe_allow_html=True)
    for categoria in CATEGORIAS:
        modulos = [m for m in MODULOS if m[2] == categoria]
        qc.seccion(categoria)
        if categoria == "Teoría y repaso" and sugerencia:
            sugerencia()
        ancho = 3 if modulos[0][3] == SIMULADOR else 4
        for i in range(0, len(modulos), ancho):
            columnas = st.columns(ancho)
            for col, m in zip(columnas, modulos[i:i + ancho]):
                with col:
                    st.markdown(tarjeta_html(*m), unsafe_allow_html=True)
                    st.button(ACCION[m[3]], key=f"ql_abrir_{m[0]}", on_click=ir_a, args=(m[0],), icon=":material/arrow_forward:", width="stretch")
    st.markdown("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.expander("Cómo usar la aplicación", icon=":material/help:"):
            st.markdown("1. Seleccionar un simulador o el **Centro de teoría** en la barra lateral o en las tarjetas.\n"
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
                        "- Las ilustraciones de la portada y de las tarjetas son **conceptuales**; no son resultados del simulador.")
