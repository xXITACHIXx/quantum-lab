"""
quantum_lab_portada.py — Página de inicio de QUANTUM LAB: el observatorio
=========================================================================

La portada es una escena (ver `quantum_lab_escena`): el observatorio animado y, debajo, los módulos como **destinos** en cinco
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
    ("biblioteca", "14", "Herramientas de estudio", ESTUDIO, "Biblioteca científica",
     "Glosario, derivaciones con comprobación numérica, mapa de conexiones entre conceptos y referencias.", ""),
    ("solucionador", "15", "Herramientas de estudio", ESTUDIO, "Solucionador paso a paso",
     "Ecuación, datos, sustitución numérica con unidades, resultado e interpretación física de un problema.", ""),
    ("tutor", "16", "Herramientas de estudio", ESTUDIO, "Tutor de errores conceptuales",
     "Detecta confusiones frecuentes, como amplitud con probabilidad, y ofrece una pista y una explicación.", ""),
    ("verificacion", "17", "Verificación", VERIFICACION, "Verificación",
     "Contraste de los resultados con cálculos independientes y con los cuadernos de Colab.", ""),
    ("pruebas", "18", "Verificación", VERIFICACION, "Pruebas numéricas",
     "Ejecución de todas las comprobaciones numéricas de la aplicación.", ""),
]
CATEGORIAS = ("Mecánica cuántica", "Fundamentos", "Teoría y repaso", "Herramientas de estudio", "Verificación")
CAPITULOS = {
    "Mecánica cuántica": ("01", "Sistemas modelo", "Soluciones exactas de la ecuación de Schrödinger: confinamiento, oscilación y rotación."),
    "Fundamentos": ("02", "Origen de la teoría", "Los experimentos y modelos que obligaron a abandonar la física clásica."),
    "Teoría y repaso": ("03", "Estaciones de estudio", "Teoría, fórmulas, práctica y evaluación conectadas con cada simulador."),
    "Herramientas de estudio": ("04", "Consulta, cálculo y corrección", "Biblioteca, solucionador paso a paso y tutor que detecta confusiones conceptuales."),
    "Verificación": ("05", "Control de calidad", "Contraste de los resultados con cálculos independientes."),
}
CAT_CLAVE = {c: f"cat{i}" for i, c in enumerate(CATEGORIAS, start=1)}      # página de cada capítulo (sub-portada)
CLAVE_CAT = {v: k for k, v in CAT_CLAVE.items()}
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


_ACENTO = {SIMULADOR: "var(--ql-cian)", ESTUDIO: "var(--ql-violeta)", VERIFICACION: "var(--ql-verde)"}


def _entradas(categoria: str | None = None) -> list[dict]:
    """Elementos del menú: los cinco capítulos en la portada, o los temas de un capítulo en su sub-portada."""
    prefijo = {SIMULADOR: "Simulador", ESTUDIO: "Estación de estudio", VERIFICACION: "Verificación"}
    if categoria is None:
        salida = []
        for c in CATEGORIAS:
            ms = [m for m in MODULOS if m[2] == c]
            num, etiqueta, desc = CAPITULOS[c]
            salida.append(dict(clave=CAT_CLAVE[c], boton=f"{num}   {c}", acento=_ACENTO[ms[0][3]], arte=ms[0][0], tipo=f"Capítulo · {num} · {etiqueta}",
                               titulo=c, desc=desc, lema=f"{len(ms)} destinos: " + ", ".join(m[4] for m in ms[:3]) + ("…" if len(ms) > 3 else ""),
                               destino=CAT_CLAVE[c]))
        return salida
    return [dict(clave=m[0], boton=f"{m[1]}   {m[4]}", acento=_ACENTO[m[3]], arte=m[0], tipo=f"{prefijo[m[3]]} · {m[1]}", titulo=m[4], desc=m[5],
                 lema=m[6], destino=m[0]) for m in MODULOS if m[2] == categoria]


def _css_menu(entradas: list[dict], por_defecto: bool = False) -> str:
    """Reglas por elemento del menú: color de acento, orden de entrada y qué escenario se muestra al apuntar a cada barra."""
    reglas = []
    for i, en in enumerate(entradas):
        k = en["clave"]
        reglas.append(f'.st-key-ql_item_{k}{{--n:{i};--k:{i};--acento:{en["acento"]};}}')
        reglas.append(f'.st-key-ql_menu:has(.st-key-ql_item_{k}:is(:hover,:focus-within)) .ql-esc-{k}{{visibility:visible;opacity:1;'
                      f'animation:ql-esc-entra .6s cubic-bezier(.2,.7,.2,1) both;z-index:2}}')
        reglas.append(f'.st-key-ql_menu:has(.st-key-ql_item_{k}:is(:hover,:focus-within)) .ql-esc-{k} .ql-trazo{{animation:ql-trazar 1s .1s cubic-bezier(.4,.1,.2,1) both}}')
    if por_defecto:
        primero = entradas[0]["clave"]
        reglas.append(f'.st-key-ql_menu:not(:has([class*="st-key-ql_item_"]:is(:hover,:focus-within))) .ql-esc-{primero}{{visibility:visible;opacity:1;z-index:2}}')
    return "<style>" + "".join(reglas) + "</style>"


def css_navegacion() -> str:
    """Color de acento y orden de entrada de las barras de navegación de una página."""
    reglas = [f'.st-key-nav_inicio{{--n:0;--acento:var(--ql-cian);}}']
    for i, m in enumerate(MODULOS, start=1):
        reglas.append(f'.st-key-nav_{m[0]}{{--n:{i};--acento:{_ACENTO[m[3]]};}}')
    return "<style>" + "".join(reglas) + "</style>"


def _escenario_html(entradas: list[dict], por_defecto: bool = False) -> str:
    """Escenario del menú: una ilustración grande por elemento, apiladas; el CSS muestra la de la barra apuntada."""
    e = html.escape
    piezas = []
    for en in entradas:
        ecuacion = f'<span class="ql-esc-ecuacion">{e(en["lema"])}</span>' if en["lema"] else ""
        piezas.append(
            f'<div class="ql-esc-item ql-esc-{en["clave"]}" style="--acento:{en["acento"]}">'
            f'<div class="ql-esc-marco"><div class="ql-esc-arte">{arte.svg(en["arte"])}</div></div>'
            f'<div class="ql-esc-fantasma" aria-hidden="true">{e(en["boton"][:2])}</div>'
            f'<div class="ql-esc-info"><span class="ql-esc-tipo">{e(en["tipo"])}</span>'
            f'<h3>{e(en["titulo"])}</h3><p>{e(en["desc"])}</p>{ecuacion}'
            f'<span class="ql-esc-entrar">Enter o clic para abrir<i>→</i></span></div></div>')
    return f'<div class="ql-esc">{"".join(piezas)}</div>' + _css_menu(entradas, por_defecto)


def menu_cinetico(ir_a, categoria: str | None = None) -> None:
    """
    Portada (`categoria=None`): el átomo ilustrado a pantalla completa y, sobre él, los cinco capítulos como barras angulares en escalera.
    Sub-portada (`categoria="Fundamentos"`, por ejemplo): los temas de ese capítulo con el mismo estilo. Al apuntar una barra (cursor o
    teclado) aparece, abajo a la derecha, su ilustración. Cada barra es un `st.button` real (clic, toque y Enter); en pantallas pequeñas
    queda solo la lista sobre el fondo.
    """
    entradas = _entradas(categoria)
    with st.container(key="ql_menu"):
        st.markdown(escena.fondo_atomo_html(arte.atomo(), lecturas()), unsafe_allow_html=True)
        izq, der = st.columns([1.35, 1] if categoria is None else [1, 1.3], gap="large")
        with izq:
            if categoria is None:
                st.markdown('<div class="ql-inicio-marca"><span class="ql-inicio-eyebrow">Observatorio cuántico</span>'
                            '<div class="ql-inicio-titulo" role="heading" aria-level="1">Quantum Lab</div>'
                            '<p class="ql-inicio-sub">Laboratorio interactivo de mecánica cuántica</p>'
                            f'<span id="{ID_SIMULADORES}"></span><span id="{ID_ESTUDIO}"></span></div>', unsafe_allow_html=True)
            else:
                num, etiqueta, desc = CAPITULOS[categoria]
                with st.container(key="ql_sub_volver"):
                    st.button("\u2190 Inicio", key="ql_volver", type="tertiary", on_click=ir_a, args=("inicio",))
                st.markdown(f'<div class="ql-inicio-marca"><span class="ql-inicio-eyebrow">Capítulo {html.escape(num)} · {html.escape(etiqueta)}</span>'
                            f'<div class="ql-inicio-titulo ql-sub-titulo" role="heading" aria-level="1">{html.escape(categoria)}</div>'
                            f'<p class="ql-inicio-sub">{html.escape(desc)}</p></div>', unsafe_allow_html=True)
            with st.container(key="ql_cats" if categoria is None else "ql_temas"):
                for en in entradas:
                    with st.container(key=f"ql_item_{en['clave']}"):
                        st.button(en["boton"], key=f"ql_menu_{en['clave']}", on_click=ir_a, args=(en["destino"],), width="stretch")
        with der:
            st.markdown(_escenario_html(entradas, por_defecto=categoria is not None), unsafe_allow_html=True)


def pagina_subinicio(ir_a, categoria: str) -> None:
    """Sub-portada de un capítulo: sus temas como barras angulares sobre el átomo, con la misma animación de entrada."""
    menu_cinetico(ir_a, categoria)


def pagina_inicio(ir_a, sugerencia=None) -> None:
    """
    Portada. Primera pantalla: átomo a pantalla completa con el menú de destinos (`menu_cinetico`). Debajo: el siguiente paso sugerido,
    la vista alternativa en tarjetas y las ayudas. `ir_a(clave)` es el callback de navegación.
    """
    menu_cinetico(ir_a)
    with st.container(key="ql_inicio_resto"):
        if sugerencia:
            sugerencia()
        tarjetas = st.toggle("Ver también los destinos como tarjetas", key="ql_vista")
        _resto(ir_a, tarjetas)


def _resto(ir_a, tarjetas: bool) -> None:
    for categoria in (CATEGORIAS if tarjetas else ()):
        modulos = [m for m in MODULOS if m[2] == categoria]
        num, etiqueta, descripcion = CAPITULOS[categoria]
        st.markdown(escena.capitulo_html(num, etiqueta, categoria, descripcion), unsafe_allow_html=True)
        if categoria in COMPOSICION:
            proporciones, mayor = COMPOSICION[categoria]
            for i, (col, m) in enumerate(zip(st.columns(proporciones, gap="medium"), modulos)):
                with col:
                    destino(m, ir_a, mayor=(i == mayor))
            continue
        for i in range(0, len(modulos), 2):
            for col, m in zip(st.columns(2, gap="medium"), modulos[i:i + 2]):
                with col:
                    destino(m, ir_a, compacta=True)
    st.markdown("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.expander("Cómo usar la aplicación", icon=":material/help:"):
            st.markdown("1. Elegir un capítulo en la portada y, dentro de él, el tema que se quiere abrir.\n"
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
