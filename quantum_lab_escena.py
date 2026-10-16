"""
quantum_lab_escena.py — Movimiento, escena y navegación animada de QUANTUM LAB
===============================================================================

Tres interacciones, diseñadas para sobrevivir al ciclo de renderizado de Streamlit:

1. **Navegación animada.** Cada página se dibuja dentro de `st.container(key="ql_escena_<página>")`. Como la clave cambia solo al
   cambiar de página, React vuelve a montar el contenido únicamente en ese momento: la entrada escalonada, el barrido de la barra de
   ubicación y el trazado de la ilustración se reproducen al navegar, y **no** al mover un control dentro de la misma página.
2. **Destinos interactivos.** Cada tarjeta de la portada es un contenedor con clave `ql_dest_<página>` que contiene la tarjeta (HTML)
   y un `st.button` real extendido sobre toda la superficie: la navegación sigue siendo la de Streamlit (teclado incluido). Al pasar el
   cursor la tarjeta se eleva, se enciende la línea de energía, la luz sigue al puntero y la ilustración se vuelve a trazar.
3. **Observatorio (portada).** Escena por capas: luz ambiental que deriva, plano de medida en perspectiva, partículas en un lienzo
   (Canvas) con paralaje según el puntero, y la nube de probabilidad con órbitas en movimiento.

Todo funciona sin JavaScript (el JS solo añade las partículas, el paralaje y la luz que sigue al cursor) y todo se detiene con
`prefers-reduced-motion: reduce`. En pantallas pequeñas se suprimen el plano en perspectiva y las partículas.
"""

from __future__ import annotations

import html
import inspect

import quantum_lab_tema as tema

P = tema.PALETA

# ---------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------
_CSS = r"""
<style>
/* =============== Movimiento: definiciones =============== */
@keyframes ql-entrada { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes ql-barrido { 0% { transform: scaleX(0); opacity: 1; } 70% { transform: scaleX(1); opacity: 1; } 100% { transform: scaleX(1); opacity: .35; } }
@keyframes ql-trazar { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes ql-portal { from { opacity: 0; transform: translateY(12px) scale(.92); filter: blur(6px); } to { opacity: 1; transform: none; filter: none; } }
@keyframes ql-titulo { from { opacity: 0; letter-spacing: .12em; filter: blur(10px); } to { opacity: 1; letter-spacing: -.01em; filter: none; } }
@keyframes ql-subir { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes ql-deriva-a { 0% { transform: translate3d(-6%, -4%, 0) scale(1); } 100% { transform: translate3d(8%, 6%, 0) scale(1.15); } }
@keyframes ql-deriva-b { 0% { transform: translate3d(6%, 4%, 0) scale(1.1); } 100% { transform: translate3d(-8%, -6%, 0) scale(.95); } }
@keyframes ql-plano { from { background-position: 0 0; } to { background-position: 0 56px; } }
@keyframes ql-giro { to { transform: rotate(360deg); } }
@keyframes ql-respira { 0%, 100% { opacity: .82; transform: scale(1); } 50% { opacity: 1; transform: scale(1.025); } }
@keyframes ql-escaneo { 0% { top: 4%; opacity: 0; } 8% { opacity: .8; } 92% { opacity: .8; } 100% { top: 96%; opacity: 0; } }
@keyframes ql-energia { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes ql-latido { 0%, 100% { opacity: .85; } 50% { opacity: 1; } }

/* =============== 1. Navegación animada =============== */
/* Entrada escalonada: solo se reproduce cuando cambia la clave del contenedor (es decir, al cambiar de página). */
[class*="st-key-ql_escena_"] > * { animation: ql-entrada .62s cubic-bezier(.2, .7, .2, 1) both; }
[class*="st-key-ql_escena_"] > *:nth-child(1) { animation-delay: 0s; }
[class*="st-key-ql_escena_"] > *:nth-child(2) { animation-delay: .06s; }
[class*="st-key-ql_escena_"] > *:nth-child(3) { animation-delay: .12s; }
[class*="st-key-ql_escena_"] > *:nth-child(4) { animation-delay: .18s; }
[class*="st-key-ql_escena_"] > *:nth-child(5) { animation-delay: .24s; }
[class*="st-key-ql_escena_"] > *:nth-child(n+6) { animation-delay: .3s; }

/* Barra de ubicación: dónde está el usuario, con un barrido de energía al llegar. */
.ql-ubicacion { position: relative; display: flex; align-items: center; gap: .9rem; padding: .55rem 0 .7rem 0;
  font: 500 .72rem/1.2 var(--ql-mono); letter-spacing: .16em; text-transform: uppercase; color: var(--ql-tenue); }
.ql-ubicacion b { color: var(--ql-texto); font-weight: 600; }
.ql-ubicacion .ql-ub-sep { color: var(--ql-borde); }
.ql-ubicacion .ql-ub-num { margin-left: auto; color: var(--ql-cian); }
.ql-ubicacion::before { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 1px; background: var(--ql-borde); }
.ql-ubicacion::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 2px; transform-origin: left;
  background: linear-gradient(90deg, var(--ql-cian), var(--ql-violeta) 60%, transparent); animation: ql-barrido 1.1s cubic-bezier(.3, .7, .2, 1) both; }
.st-key-ql_volver button { font: 600 .74rem/1 var(--ql-mono) !important; letter-spacing: .12em; text-transform: uppercase; }

/* Barra lateral: la línea de energía se desplaza hasta la sección activa. */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] { position: relative; box-shadow: none !important;
  background: linear-gradient(90deg, rgba(66, 217, 255, .14), rgba(167, 139, 250, .04) 70%, transparent) !important; }
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]::before { content: ""; position: absolute; left: 0; top: 14%;
  height: 72%; width: 2px; border-radius: 2px; background: linear-gradient(180deg, var(--ql-cian), var(--ql-violeta));
  box-shadow: 0 0 10px var(--ql-cian); transform-origin: center; animation: ql-energia .45s cubic-bezier(.2, .8, .2, 1) both; }

/* Cabecera de cada página: la ilustración «se abre» como un portal y sus trazos se dibujan. */
.ql-cab-arte { animation: ql-portal .9s cubic-bezier(.2, .7, .2, 1) both; }
.ql-cab-arte svg { box-shadow: 0 0 0 1px rgba(167, 139, 250, .12), 0 20px 50px -30px var(--ql-violeta); }
.ql-cab-arte .ql-trazo { stroke-dasharray: 1; stroke-dashoffset: 0; animation: ql-trazar 1.6s .25s cubic-bezier(.4, .1, .2, 1) both; }
.ql-seccion::after { transform-origin: left; animation: ql-barrido 1s .15s cubic-bezier(.3, .7, .2, 1) both; }

/* Instrumentos de los simuladores: indicadores que responden al cursor y destellan cuando su valor cambia. */
@keyframes ql-destello { 0% { color: var(--ql-cian); text-shadow: 0 0 14px rgba(66, 217, 255, .8); } 100% { color: var(--ql-texto); text-shadow: none; } }
div[data-testid="stMetric"] { position: relative; overflow: hidden; transition: border-color .35s, transform .35s, box-shadow .35s; }
div[data-testid="stMetric"]::after { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 2px; transform: scaleX(0); transform-origin: left;
  background: linear-gradient(90deg, var(--ql-cian), var(--ql-violeta), transparent); transition: transform .5s cubic-bezier(.2, .7, .2, 1); }
@media (hover: hover) {
  div[data-testid="stMetric"]:hover { border-color: rgba(66, 217, 255, .45); transform: translateY(-2px); box-shadow: 0 14px 30px -22px var(--ql-cian); }
  div[data-testid="stMetric"]:hover::after { transform: scaleX(1); }
}
div[data-testid="stMetricValue"].ql-actualizado, div[data-testid="stMetricValue"].ql-actualizado * { animation: ql-destello .9s ease-out both; }

/* =============== 2. Destinos interactivos =============== */
[class*="st-key-ql_dest_"] { position: relative; gap: 0 !important; }
/* El botón real de Streamlit cubre toda la tarjeta: clic, toque y teclado navegan como siempre. */
[class*="st-key-ql_dest_"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]) {
  position: absolute !important; inset: 0; z-index: 5; margin: 0 !important; width: auto !important; }
[class*="st-key-ql_dest_"] div[data-testid="stButton"], [class*="st-key-ql_dest_"] div[data-testid="stButton"] button {
  width: 100% !important; height: 100% !important; }
[class*="st-key-ql_dest_"] div[data-testid="stButton"] button { opacity: 0; cursor: pointer; }

.ql-dest { --acento: var(--ql-cian); --halo: rgba(66, 217, 255, .16); position: relative; overflow: hidden; border-radius: 14px;
  border: 1px solid var(--ql-borde); background: linear-gradient(165deg, var(--ql-panel) 0%, #0F1629 60%, var(--ql-fondo) 100%);
  transition: transform .45s cubic-bezier(.2, .7, .2, 1), border-color .45s, box-shadow .45s; height: 100%; }
.ql-dest-sim { --acento: var(--ql-violeta); --halo: rgba(167, 139, 250, .2); }
.ql-dest-ver { --acento: var(--ql-verde); --halo: rgba(57, 217, 138, .16); }
.ql-dest-luz { position: absolute; inset: 0; pointer-events: none; opacity: 0; transition: opacity .45s;
  background: radial-gradient(520px circle at var(--mx, 50%) var(--my, 0%), var(--halo), transparent 55%); }
.ql-dest-linea { position: absolute; left: 0; right: 0; bottom: 0; height: 2px; transform: scaleX(0); transform-origin: left;
  background: linear-gradient(90deg, var(--ql-cian), var(--acento), transparent); transition: transform .6s cubic-bezier(.2, .7, .2, 1); }
.ql-dest-arte { position: relative; overflow: hidden; border-bottom: 1px solid var(--ql-borde); background: var(--ql-fondo); }
.ql-dest-arte svg { display: block; width: 100%; height: auto; transform-origin: 50% 60%; transition: transform .8s cubic-bezier(.2, .7, .2, 1); }
.ql-dest-cuerpo { position: relative; padding: 1rem 1.15rem 1.05rem 1.15rem; }
.ql-dest-meta { display: flex; align-items: center; justify-content: space-between; gap: .4rem .6rem; flex-wrap: wrap; }
.ql-dest h3 { font-family: var(--ql-serif); font-weight: 600; font-size: 1.22rem; line-height: 1.2; margin: .55rem 0 .4rem 0; color: var(--ql-texto); }
.ql-dest p { color: var(--ql-tenue); font-size: .9rem; line-height: 1.5; margin: 0; }
.ql-dest-pie { display: flex; align-items: center; justify-content: space-between; gap: .8rem; margin-top: .85rem; flex-wrap: wrap; }
.ql-dest-pie .ql-ecuacion { font: 400 .82rem/1.3 var(--ql-mono); color: var(--ql-texto); }
.ql-dest-entrar { font: 600 .7rem/1 var(--ql-mono); letter-spacing: .16em; text-transform: uppercase; color: var(--acento); white-space: nowrap; }
.ql-dest-entrar i { display: inline-block; font-style: normal; margin-left: .35rem; transition: transform .45s cubic-bezier(.2, .7, .2, 1); }
.ql-dest .ql-chip { color: var(--acento); border-color: color-mix(in srgb, var(--acento) 55%, transparent); }
.ql-dest-mayor h3 { font-size: 1.65rem; }
.ql-dest-mayor p { font-size: .97rem; }
/* Estaciones compactas: ilustración a la izquierda y texto a la derecha. */
.ql-dest-compacta { display: grid; grid-template-columns: minmax(118px, 38%) 1fr; }
.ql-dest-compacta .ql-dest-arte { border-bottom: 0; border-right: 1px solid var(--ql-borde); display: flex; align-items: center; }
.ql-dest-compacta h3 { font-size: 1.08rem; margin-top: .45rem; }
.ql-dest-compacta p { font-size: .85rem; }
[class*="st-key-ql_dest_"] { margin-bottom: .9rem; }

@media (hover: hover) {
  [class*="st-key-ql_dest_"]:hover .ql-dest { transform: translateY(-6px); border-color: color-mix(in srgb, var(--acento) 70%, transparent);
    box-shadow: 0 24px 50px -28px var(--acento), 0 0 0 1px color-mix(in srgb, var(--acento) 30%, transparent) inset; }
  [class*="st-key-ql_dest_"]:hover .ql-dest-luz { opacity: 1; }
  [class*="st-key-ql_dest_"]:hover .ql-dest-linea { transform: scaleX(1); }
  [class*="st-key-ql_dest_"]:hover .ql-dest-arte svg { transform: scale(1.05); }
  [class*="st-key-ql_dest_"]:hover .ql-dest-entrar i { transform: translateX(5px); }
  [class*="st-key-ql_dest_"]:hover .ql-trazo { stroke-dasharray: 1; animation: ql-trazar 1.1s cubic-bezier(.4, .1, .2, 1) both; }
}
/* Teclado: el mismo estado visual que el cursor, con un contorno visible. */
[class*="st-key-ql_dest_"]:has(button:focus-visible) .ql-dest { transform: translateY(-6px); outline: 2px solid var(--ql-cian); outline-offset: 3px; }
[class*="st-key-ql_dest_"]:has(button:focus-visible) .ql-dest-linea { transform: scaleX(1); }
[class*="st-key-ql_dest_"]:active .ql-dest { transform: translateY(-2px) scale(.99); transition-duration: .12s; }

/* Capítulos de la portada */
.ql-capitulo { display: grid; grid-template-columns: auto 1fr; gap: 1.1rem; align-items: center; margin: 2.6rem 0 1.2rem 0; }
.ql-capitulo-num { font: 500 3rem/0.9 var(--ql-mono); color: transparent; -webkit-text-stroke: 1px var(--ql-tenue); opacity: .55; letter-spacing: -.02em; }
.ql-capitulo h2 { font-family: var(--ql-serif) !important; font-size: 1.9rem !important; font-weight: 600; margin: .2rem 0 .1rem 0 !important; padding: 0 !important; color: var(--ql-texto); }
.ql-capitulo p { margin: 0; color: var(--ql-tenue); font-size: .95rem; }

/* =============== 3. Observatorio (portada) =============== */
.ql-obs { --px: 0; --py: 0; position: relative; overflow: hidden; isolation: isolate; border-radius: 18px; border: 1px solid var(--ql-borde);
  background: §profundo; min-height: 560px; margin-bottom: .4rem; }
.ql-obs-capa { position: absolute; inset: 0; pointer-events: none; transition: transform 1.2s cubic-bezier(.2, .7, .2, 1); }
.ql-obs-luz { position: absolute; border-radius: 50%; filter: blur(60px); opacity: .55; will-change: transform; }
.ql-obs-luz.a { width: 46%; height: 70%; left: -8%; top: -20%; background: radial-gradient(circle, rgba(66, 217, 255, .55), transparent 65%);
  animation: ql-deriva-a 26s ease-in-out infinite alternate; }
.ql-obs-luz.b { width: 52%; height: 80%; right: -10%; top: 5%; background: radial-gradient(circle, rgba(167, 139, 250, .6), transparent 65%);
  animation: ql-deriva-b 32s ease-in-out infinite alternate; }
.ql-obs-luz.c { width: 30%; height: 40%; right: 22%; bottom: -18%; background: radial-gradient(circle, rgba(244, 114, 208, .45), transparent 65%);
  animation: ql-deriva-a 38s ease-in-out infinite alternate-reverse; }
.ql-obs-fondo { transform: translate3d(calc(var(--px) * -10px), calc(var(--py) * -8px), 0); }
.ql-obs-plano { position: absolute; left: -25%; right: -25%; bottom: -8%; height: 46%; transform-origin: 50% 100%;
  transform: perspective(520px) rotateX(64deg); opacity: .5;
  background-image: linear-gradient(rgba(66, 217, 255, .28) 1px, transparent 1px), linear-gradient(90deg, rgba(66, 217, 255, .22) 1px, transparent 1px);
  background-size: 56px 56px; animation: ql-plano 6s linear infinite;
  -webkit-mask-image: linear-gradient(to top, #000 10%, transparent 95%); mask-image: linear-gradient(to top, #000 10%, transparent 95%); }
.ql-obs-particulas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.ql-obs-contenido { position: relative; z-index: 2; display: grid; grid-template-columns: minmax(0, .95fr) minmax(0, 1.05fr);
  gap: 1rem; align-items: center; padding: 2.6rem 2.4rem 1rem 2.6rem; min-height: 480px; }
.ql-obs-marca { display: flex; align-items: center; gap: .7rem; font: 600 .72rem/1 var(--ql-mono); letter-spacing: .22em;
  text-transform: uppercase; color: var(--ql-cian); animation: ql-subir .8s .1s both; }
.ql-obs-marca::before { content: ""; width: 34px; height: 1px; background: linear-gradient(90deg, transparent, var(--ql-cian)); }
.ql-obs-titulo { font-family: var(--ql-serif); font-weight: 600; font-size: clamp(2.8rem, 6.2vw, 5.4rem); line-height: .95;
  color: var(--ql-texto); margin: 1rem 0 .9rem 0; letter-spacing: -.01em; text-shadow: 0 0 40px rgba(167, 139, 250, .35);
  animation: ql-titulo 1.4s .15s cubic-bezier(.2, .7, .2, 1) both; }
.ql-obs-titulo span { display: block; font-size: .36em; line-height: 1.25; letter-spacing: .01em; color: var(--ql-tenue); font-weight: 400; margin-top: .5rem; }
.ql-obs-texto p.ql-obs-desc { color: var(--ql-tenue); font-size: 1.04rem; line-height: 1.6; max-width: 32rem; margin: 0 0 1.6rem 0; animation: ql-subir .8s .45s both; }
.ql-obs-acciones { display: flex; flex-wrap: wrap; gap: .8rem; animation: ql-subir .8s .6s both; }
a.ql-boton-2, a.ql-boton-2:visited { display: inline-block; padding: .7rem 1.2rem; border-radius: 8px; border: 1px solid var(--ql-borde);
  color: var(--ql-texto) !important; text-decoration: none; font-weight: 600; background: rgba(21, 31, 53, .6); backdrop-filter: blur(6px);
  transition: border-color .3s, background .3s; }
a.ql-boton-2:hover { border-color: var(--ql-violeta); background: rgba(167, 139, 250, .1); }
a.ql-boton { box-shadow: 0 0 0 0 rgba(66, 217, 255, .5); transition: box-shadow .4s, background .3s, color .3s; }
a.ql-boton:hover { box-shadow: 0 0 30px -4px rgba(66, 217, 255, .65); }
.ql-obs-escena { position: relative; transform: translate3d(calc(var(--px) * 14px), calc(var(--py) * 10px), 0);
  transition: transform 1.2s cubic-bezier(.2, .7, .2, 1); animation: ql-portal 1.4s .3s cubic-bezier(.2, .7, .2, 1) both; }
.ql-obs-escena svg { display: block; width: 100%; height: auto; overflow: visible; }
.ql-obs-escena::after { content: ""; position: absolute; left: 4%; right: 4%; top: 0; height: 1px; pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(66, 217, 255, .55) 30%, rgba(167, 139, 250, .55) 70%, transparent);
  box-shadow: 0 0 12px rgba(66, 217, 255, .45); animation: ql-escaneo 11s 2.5s linear infinite; }
.ql-obs-giro { transform-origin: 0 0; animation: ql-giro 28s linear infinite; }
.ql-obs-giro-2 { animation-duration: 21s; animation-direction: reverse; }
.ql-obs-giro-3 { animation-duration: 36s; }
.ql-obs-electron { filter: drop-shadow(0 0 6px currentColor); }
.ql-obs-nube { transform-box: fill-box; transform-origin: center; animation: ql-respira 7s ease-in-out infinite; }
.ql-obs-halo { transform-box: fill-box; transform-origin: center; animation: ql-respira 9s ease-in-out infinite reverse; }
.ql-obs-nucleo { animation: ql-latido 3s ease-in-out infinite; }
.ql-obs-reticula { opacity: .8; }
.ql-obs-lectura { position: relative; z-index: 2; display: flex; flex-wrap: wrap; gap: .4rem 1.6rem; padding: .95rem 2.6rem 1.2rem 2.6rem;
  border-top: 1px solid rgba(38, 53, 80, .7); background: linear-gradient(180deg, transparent, rgba(11, 16, 32, .7));
  font: 500 .72rem/1.4 var(--ql-mono); letter-spacing: .14em; text-transform: uppercase; color: var(--ql-tenue); animation: ql-subir .8s .8s both; }
.ql-obs-lectura b { color: var(--ql-texto); font-weight: 600; margin-right: .35rem; }
.ql-obs-lectura .ql-obs-pulso { color: var(--ql-verde); }
.ql-obs-lectura .ql-obs-pulso::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: .5rem;
  background: var(--ql-verde); box-shadow: 0 0 8px var(--ql-verde); vertical-align: middle; animation: ql-latido 2.4s ease-in-out infinite; }

/* =============== Adaptación y accesibilidad =============== */
/* Composición asimétrica en pantallas medianas: el destino mayor ocupa toda la fila y los otros dos se reparten la siguiente. */
@media (max-width: 1150px) {
  div[data-testid="stHorizontalBlock"]:has(.ql-dest) { flex-wrap: wrap !important; row-gap: 0 !important; }
  div[data-testid="stHorizontalBlock"]:has(.ql-dest) > div[data-testid="stColumn"] { min-width: calc(50% - .6rem) !important; flex: 1 1 calc(50% - .6rem) !important; }
  div[data-testid="stHorizontalBlock"]:has(.ql-dest) > div[data-testid="stColumn"]:has(.ql-dest-mayor) { min-width: 100% !important; flex-basis: 100% !important; }
  div[data-testid="stHorizontalBlock"]:has(.ql-dest-compacta) > div[data-testid="stColumn"] { min-width: 100% !important; }
  .ql-dest-mayor { display: grid; grid-template-columns: 1.1fr 1fr; }
  .ql-dest-mayor .ql-dest-arte { border-bottom: 0; border-right: 1px solid var(--ql-borde); display: flex; align-items: center; }
}
@media (max-width: 900px) {
  .ql-obs { min-height: 0; }
  .ql-obs-contenido { grid-template-columns: 1fr; padding: 1.8rem 1.3rem .6rem 1.3rem; min-height: 0; }
  .ql-obs-escena { max-width: 520px; margin: 0 auto; }
  .ql-obs-lectura { padding: .9rem 1.3rem 1.1rem 1.3rem; }
  .ql-capitulo-num { font-size: 2.4rem; }
}
@media (max-width: 640px) {
  .ql-obs-plano, .ql-obs-particulas, .ql-obs-luz.c { display: none; }
  .ql-obs-escena::after { display: none; }
  .ql-dest-compacta { grid-template-columns: 1fr; }
  .ql-dest-compacta .ql-dest-arte { border-right: 0; border-bottom: 1px solid var(--ql-borde); }
  .ql-dest-mayor h3 { font-size: 1.3rem; }
  .ql-capitulo h2 { font-size: 1.5rem !important; }
  .ql-capitulo { grid-template-columns: 1fr; gap: .2rem; margin-top: 2rem; }
  .ql-capitulo-num { font-size: 1.6rem; }
  .ql-dest-mayor { display: block; }
  .ql-dest-mayor .ql-dest-arte { border-right: 0; border-bottom: 1px solid var(--ql-borde); }
  .ql-ubicacion { letter-spacing: .1em; font-size: .66rem; flex-wrap: wrap; }
}

/* =============== 4. Narración de la ilustración =============== */
/* Los trazos se dibujan en el orden en que están construidos (--i): primero el potencial o el dominio, después los estados. */
@keyframes ql-aparece { from { opacity: 0; } to { opacity: 1; } }
@keyframes ql-relleno { from { fill-opacity: 0; } }
.ql-cab-arte .ql-trazo { animation-duration: 1.15s; animation-delay: calc(.35s + (var(--i, 1) - 1) * .55s); }
.ql-cab-arte path.ql-trazo:not([fill="none"]) { animation: ql-trazar 1.15s calc(.35s + (var(--i, 1) - 1) * .55s) cubic-bezier(.4, .1, .2, 1) both,
  ql-relleno 1s calc(1.2s + (var(--i, 1) - 1) * .55s) ease-out both; }
.ql-cab-arte svg text, .ql-cab-arte svg circle, .ql-cab-arte svg line, .ql-cab-arte svg path:not(.ql-trazo) { animation: ql-aparece .8s 1.1s ease-out both; }

/* =============== 5. Fondo vivo =============== */
/* Capa fija detrás de todo el contenido: dos luces que derivan despacio y, si hay JavaScript, unas pocas partículas. */
[data-testid="stApp"]::before { content: ""; position: fixed; inset: -10%; z-index: 0; pointer-events: none;
  background: radial-gradient(40vw 40vw at 15% 10%, rgba(66, 217, 255, .07), transparent 70%),
              radial-gradient(45vw 45vw at 90% 85%, rgba(167, 139, 250, .08), transparent 70%);
  animation: ql-deriva-a 28s ease-in-out infinite alternate; }
#ql-fondo-vivo { position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 0; pointer-events: none; opacity: .75; }
[data-testid="stMain"] { position: relative; z-index: 1; }

/* =============== 6. Elección de una tarjeta =============== */
/* Al pulsar un destino, su ilustración se expande y las demás tarjetas se apartan mientras Streamlit carga la página. */
[class*="st-key-ql_dest_"].ql-abriendo { z-index: 8; }
[class*="st-key-ql_dest_"].ql-abriendo .ql-dest { transform: translateY(-8px) scale(1.035); border-color: var(--acento); box-shadow: 0 30px 70px -26px var(--acento); }
[class*="st-key-ql_dest_"].ql-abriendo .ql-dest-arte svg { transform: scale(1.18); filter: brightness(1.25); }
[class*="st-key-ql_dest_"].ql-abriendo .ql-dest-luz { opacity: 1; }
[class*="st-key-ql_dest_"].ql-abriendo .ql-dest-linea { transform: scaleX(1); }
[class*="st-key-ql_dest_"].ql-aparta .ql-dest { opacity: .38; filter: blur(1.5px) saturate(.7); transform: scale(.975); transition: all .5s cubic-bezier(.2, .7, .2, 1); }

/* =============== 7. Microinteracciones de la interfaz =============== */
@keyframes ql-resalte { from { box-shadow: 0 0 0 0 rgba(66, 217, 255, .55); } to { box-shadow: 0 0 0 10px rgba(66, 217, 255, 0); } }
@keyframes ql-aviso { from { opacity: 0; transform: translateX(-14px); } to { opacity: 1; transform: none; } }
@keyframes ql-fundir { from { opacity: 0; transform: translateY(10px) scale(.992); } to { opacity: 1; transform: none; } }
/* Gráficas y tablas se funden al montarse (no se reproducen al mover un parámetro: el nodo se conserva). */
[data-testid="stImage"], [data-testid="stPlotlyChart"], [data-testid="stDataFrame"], [data-testid="stTable"] { animation: ql-fundir .7s cubic-bezier(.2, .7, .2, 1) both; }
div[data-testid="stAlert"] { animation: ql-aviso .5s cubic-bezier(.2, .7, .2, 1) both; }
/* Botones: elevación y brillo; pulso al pulsar. */
.stButton > button, .stDownloadButton > button { transition: transform .25s cubic-bezier(.2, .7, .2, 1), box-shadow .3s, border-color .3s, background .3s; }
@media (hover: hover) {
  .stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 26px -16px var(--ql-cian); border-color: rgba(66, 217, 255, .6); }
  section[data-testid="stSidebar"] .stButton > button:hover { transform: translateX(4px); box-shadow: none; }
}
.stButton > button:active, .stDownloadButton > button:active { transform: scale(.97); animation: ql-resalte .5s ease-out; }
/* Pestañas: el indicador se desliza y el texto se ilumina. */
button[data-baseweb="tab"] { transition: color .3s, transform .3s; }
@media (hover: hover) { button[data-baseweb="tab"]:hover { transform: translateY(-1px); color: var(--ql-cian); } }
div[data-baseweb="tab-highlight"] { transition: left .4s cubic-bezier(.2, .8, .2, 1), width .4s cubic-bezier(.2, .8, .2, 1) !important;
  box-shadow: 0 0 12px var(--ql-cian); }
/* Campos: halo al enfocar. */
div[data-baseweb="input"], div[data-baseweb="select"] > div { transition: box-shadow .3s, border-color .3s; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within { box-shadow: 0 0 0 3px rgba(66, 217, 255, .22); }
/* Desplegables: encabezado que se ilumina. */
[data-testid="stExpander"] details { transition: border-color .35s, box-shadow .35s; }
@media (hover: hover) { [data-testid="stExpander"] details:hover { border-color: rgba(66, 217, 255, .4) !important; box-shadow: 0 10px 28px -22px var(--ql-cian); } }
/* Deslizadores: la perilla crece al arrastrar. */
div[data-baseweb="slider"] div[role] { transition: transform .2s, box-shadow .3s; }
div[data-baseweb="slider"] div[role]:hover, div[data-baseweb="slider"] div[role]:focus { transform: scale(1.25); box-shadow: 0 0 0 6px rgba(66, 217, 255, .2); }
@media (max-width: 640px) { [data-testid="stApp"]::before { animation: none; } #ql-fondo-vivo { display: none; } }

/* =============== 8. Emergencia desde abajo =============== */
@keyframes ql-em-fondo { from { opacity: 0; } to { opacity: 1; } }
@keyframes ql-em-sube { from { transform: translate(-50%, 100%); } to { transform: translate(-50%, 87%); } }
@keyframes ql-em-baja { from { transform: translate(-50%, 87%); } to { transform: translate(-50%, 102%); } }
@keyframes ql-em-texto { from { opacity: 0; transform: translateY(26px); letter-spacing: .42em; } to { opacity: 1; transform: none; letter-spacing: .16em; } }
@keyframes ql-em-sale { to { opacity: 0; transform: translateY(-14px); } }
@keyframes ql-pagina-sube { from { opacity: 0; transform: translateY(72px); } to { opacity: 1; transform: none; } }
#ql-emerge { --acento: var(--ql-cian); position: fixed; inset: 0; z-index: 1000010; pointer-events: none; opacity: 0; visibility: hidden; overflow: hidden;
  background: radial-gradient(70% 60% at 50% 100%, color-mix(in srgb, var(--acento) 18%, #070B16), #070B16 70%); }
#ql-emerge.ql-em-sube { visibility: visible; animation: ql-em-fondo .35s ease-out forwards; }
#ql-emerge.ql-em-baja { animation: ql-em-fondo .55s .15s ease-in reverse forwards; }
.ql-em-cuerpo { position: absolute; left: 50%; bottom: 0; width: 170vmax; height: 170vmax; border-radius: 50%; transform: translate(-50%, 100%);
  background: radial-gradient(circle at 50% 0%, color-mix(in srgb, var(--acento) 55%, #0B1020) 0%, #101A2E 22%, #070B16 60%);
  box-shadow: inset 0 3px 0 color-mix(in srgb, var(--acento) 80%, #fff), inset 0 30px 90px -30px var(--acento), 0 -30px 110px -20px color-mix(in srgb, var(--acento) 60%, transparent); }
#ql-emerge.ql-em-sube .ql-em-cuerpo { animation: ql-em-sube 1s cubic-bezier(.16, .8, .2, 1) both; }
#ql-emerge.ql-em-baja .ql-em-cuerpo { animation: ql-em-baja .7s cubic-bezier(.5, 0, .8, .4) both; }
.ql-em-texto { position: absolute; left: 0; right: 0; top: 30%; text-align: center; padding: 0 1rem; }
.ql-em-tipo { display: block; font: 600 .74rem/1 var(--ql-mono); letter-spacing: .3em; text-transform: uppercase; color: var(--acento); }
.ql-em-titulo { margin-top: .9rem; font-family: var(--ql-serif); font-weight: 600; font-size: clamp(1.5rem, 4.6vw, 3.4rem); line-height: 1.12; text-transform: uppercase; text-wrap: balance;
  max-width: 22ch; margin-left: auto; margin-right: auto; color: var(--ql-texto); }
.ql-em-linea { display: block; width: 74px; height: 2px; margin: 1.2rem auto 0; background: var(--acento); box-shadow: 0 0 14px var(--acento); }
#ql-emerge.ql-em-sube .ql-em-tipo, #ql-emerge.ql-em-sube .ql-em-titulo, #ql-emerge.ql-em-sube .ql-em-linea { animation: ql-em-texto .8s .3s cubic-bezier(.2, .8, .2, 1) both; }
#ql-emerge.ql-em-baja .ql-em-texto { animation: ql-em-sale .35s ease-in both; }
/* La página nueva emerge también desde abajo, con suavidad. */
[class*="st-key-ql_escena_"] { animation: ql-pagina-sube .8s cubic-bezier(.16, .8, .2, 1) both; }

/* =============== 9. Menú cinético =============== */
/* Barras angulares que se desplazan y se encienden al apuntarlas; a la derecha, el escenario con la ilustración del tema. */
@keyframes ql-menu-entra { from { opacity: 0; transform: translateX(-46px) skewX(-14deg); } to { opacity: 1; transform: skewX(-14deg); } }
@keyframes ql-esc-entra { from { opacity: 0; transform: translateY(70px); clip-path: ellipse(70% 45% at 50% 100%); }
                          to { opacity: 1; transform: none; clip-path: ellipse(150% 160% at 50% 100%); } }
@keyframes ql-corte { 0% { transform: translateX(-120%) skewX(-24deg); } 100% { transform: translateX(260%) skewX(-24deg); } }
.ql-menu-cab { display: flex; align-items: baseline; gap: .7rem; margin: 0; padding: 1rem 0 .35rem .3rem; font: 600 .72rem/1 var(--ql-mono);
  letter-spacing: .22em; text-transform: uppercase; color: var(--ql-tenue); }
.ql-menu-cab b { color: var(--ql-cian); font-weight: 600; }
.ql-menu-cab::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, var(--ql-borde), transparent); transform: skewX(-40deg); }
[class*="st-key-ql_item_"] { margin: 0 0 .42rem 0; animation: ql-menu-entra .55s cubic-bezier(.2, .8, .2, 1) calc(var(--n, 0) * 45ms) both;
  transform: skewX(-14deg); transform-origin: 0 50%; }
[class*="st-key-ql_item_"] button { position: relative; overflow: hidden; width: 100%; min-height: 2.9rem; border: 0 !important; border-radius: 0 !important;
  justify-content: flex-start !important; padding: 0 1.1rem 0 1.5rem !important; background: linear-gradient(95deg, #17233C 0%, #101A2E 100%) !important;
  box-shadow: inset 4px 0 0 var(--acento, var(--ql-cian)); color: var(--ql-texto) !important;
  transition: transform .32s cubic-bezier(.2, .8, .2, 1), background .32s, box-shadow .32s, color .2s; }
[class*="st-key-ql_item_"] button > div { justify-content: flex-start !important; width: 100%; }
[class*="st-key-ql_item_"] button p { transform: skewX(14deg); text-align: left; font: 600 .98rem/1 var(--ql-mono) !important; letter-spacing: .04em; margin: 0; white-space: pre; }
[class*="st-key-ql_item_"] button::after { content: ""; position: absolute; top: 0; bottom: 0; left: 0; width: 22%; pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, .34), transparent); transform: translateX(-120%) skewX(-24deg); }
[class*="st-key-ql_item_"]:is(:hover, :focus-within) button { transform: translateX(20px); color: var(--ql-fondo) !important;
  background: linear-gradient(95deg, var(--acento, var(--ql-cian)), color-mix(in srgb, var(--acento, var(--ql-cian)) 55%, #ffffff)) !important;
  box-shadow: 0 0 0 1px var(--acento, var(--ql-cian)), 14px 10px 0 -2px rgba(244, 114, 208, .75); }
[class*="st-key-ql_item_"]:is(:hover, :focus-within) button::after { animation: ql-corte .7s cubic-bezier(.3, .7, .2, 1) both; }
[class*="st-key-ql_item_"]:has(button:focus-visible) button { outline: 2px solid var(--ql-texto); outline-offset: 3px; }
[class*="st-key-ql_item_"] button:active { transform: translateX(26px) scale(.985); transition-duration: .1s; }

/* Escenario: sticky para acompañar la lectura de la lista; ilustración dentro de un marco diagonal. */
[class*="st-key-ql_menu"] [data-testid="stColumn"]:last-child { position: sticky; top: 3.4rem; align-self: flex-start; }
.ql-esc { position: relative; min-height: 31rem; }
.ql-esc-item { position: absolute; inset: 0; visibility: hidden; opacity: 0; display: flex; flex-direction: column; gap: 1rem; }
.ql-esc-marco { position: relative; padding: 0; filter: drop-shadow(0 22px 40px rgba(0, 0, 0, .45)) drop-shadow(0 0 22px color-mix(in srgb, var(--acento) 35%, transparent)); }
.ql-esc-arte { background: var(--ql-fondo); clip-path: polygon(5% 0, 100% 0, 95% 100%, 0 100%); padding: 1.1rem 1.6rem;
  border-bottom: 3px solid var(--acento); }
.ql-esc-arte svg { display: block; width: 100%; height: auto; }
.ql-esc-fantasma { position: absolute; right: .4rem; top: -1.4rem; font: 600 7.5rem/1 var(--ql-serif); color: transparent; pointer-events: none;
  -webkit-text-stroke: 1px color-mix(in srgb, var(--acento) 45%, transparent); }
.ql-esc-info { position: relative; padding: 0 .4rem 0 1.1rem; border-left: 3px solid var(--acento); }
.ql-esc-tipo { font: 600 .72rem/1 var(--ql-mono); letter-spacing: .2em; text-transform: uppercase; color: var(--acento); }
.ql-esc-info h3 { font-family: var(--ql-serif); font-weight: 600; font-size: 1.8rem; line-height: 1.1; margin: .5rem 0 .45rem 0; color: var(--ql-texto); }
.ql-esc-info p { color: var(--ql-tenue); font-size: .95rem; line-height: 1.55; margin: 0 0 .7rem 0; }
.ql-esc-ecuacion { display: inline-block; font: 500 .9rem/1.3 var(--ql-mono); color: var(--ql-texto); padding: .25rem .6rem; background: rgba(255, 255, 255, .04);
  clip-path: polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%); margin-right: .8rem; }
.ql-esc-entrar { font: 600 .7rem/1 var(--ql-mono); letter-spacing: .16em; text-transform: uppercase; color: var(--acento); }
.ql-esc-entrar i { font-style: normal; margin-left: .4rem; }
@media (max-width: 900px) {
  .ql-esc { display: none; }
  [class*="st-key-ql_menu"] [data-testid="stColumn"]:last-child { display: none; }
  [class*="st-key-ql_item_"]:is(:hover, :focus-within) button { transform: translateX(8px); }
}


/* =============== 10. Portada a pantalla completa y barra lateral angular =============== */
/* La portada ocupa toda la ventana: se anulan el ancho máximo y el relleno solo mientras existe la escena de inicio. */
[data-testid="stMainBlockContainer"]:has(.st-key-ql_menu) { max-width: none !important; padding: 0 !important; }
.st-key-ql_menu { position: relative; isolation: isolate; min-height: 100vh; overflow: hidden; gap: 0 !important;
  padding: 3.6rem clamp(1rem, 4vw, 4.5rem) 2.4rem clamp(1rem, 4vw, 4.5rem); }
.st-key-ql_menu > [data-testid="stElementContainer"]:has(.ql-fondo-atomo) { position: absolute !important; inset: 0; z-index: 0; margin: 0 !important;
  width: auto !important; height: auto !important; pointer-events: none; }
.st-key-ql_menu > [data-testid="stHorizontalBlock"] { position: relative; z-index: 2; }
.ql-fondo-atomo { --px: 0; --py: 0; position: absolute; inset: 0; overflow: hidden; background:
  radial-gradient(60% 70% at 78% 48%, rgba(167, 139, 250, .16), transparent 70%), radial-gradient(40% 50% at 20% 100%, rgba(66, 217, 255, .1), transparent 70%), #0B1020; }
.ql-atomo { position: absolute; inset: 0; transform: translate3d(calc(var(--px) * -14px), calc(var(--py) * -9px), 0) scale(1.03); transition: transform .9s cubic-bezier(.2, .7, .2, 1); }
.ql-atomo svg { display: block; width: 100%; height: 100%; }
.ql-fondo-atomo .ql-obs-particulas { position: absolute; inset: 0; width: 100%; height: 100%; }
.ql-velo { position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(90deg, rgba(11, 16, 32, .94) 0%, rgba(11, 16, 32, .72) 30%, rgba(11, 16, 32, .1) 62%, transparent 100%),
              linear-gradient(0deg, rgba(11, 16, 32, .85) 0%, transparent 22%); }
.ql-lectura-inicio { position: absolute; right: clamp(1rem, 4vw, 4.5rem); bottom: 1.2rem; display: flex; flex-wrap: wrap; justify-content: flex-end; gap: .3rem 1.4rem;
  font: 500 .7rem/1.2 var(--ql-mono); letter-spacing: .14em; text-transform: uppercase; color: var(--ql-tenue); }
.ql-lectura-inicio b { color: var(--ql-texto); font-weight: 600; margin-right: .35rem; }
.ql-lectura-inicio .ql-obs-pulso { color: var(--ql-verde); }
.ql-lectura-inicio .ql-obs-pulso::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: .5rem; background: var(--ql-verde);
  box-shadow: 0 0 10px var(--ql-verde); animation: ql-latido 2.4s ease-in-out infinite; }
.ql-inicio-marca { margin: 0 0 1.1rem .3rem; }
.ql-inicio-eyebrow { display: block; font: 600 .72rem/1 var(--ql-mono); letter-spacing: .26em; text-transform: uppercase; color: var(--ql-cian); margin-bottom: .6rem; }
.ql-inicio-titulo { font-family: var(--ql-serif); font-weight: 600; font-size: clamp(2.4rem, 4.2vw, 3.8rem); line-height: .95; letter-spacing: -.02em; color: var(--ql-texto);
  animation: ql-titulo 1s .15s cubic-bezier(.2, .7, .2, 1) both; }
.ql-inicio-sub { margin: .6rem 0 0 0; color: var(--ql-tenue); font-size: 1rem; max-width: 26rem; }
/* En la portada las barras son más compactas para que los 15 destinos quepan en la primera pantalla. */
.st-key-ql_menu [class*="st-key-ql_item_"] { margin-bottom: 0; max-width: 25rem; }
.st-key-ql_menu [data-testid="stColumn"]:first-child > [data-testid="stVerticalBlock"] { gap: .2rem; }
.st-key-ql_menu [data-testid="stColumn"]:first-child [data-testid="stElementContainer"] { flex-shrink: 0; }
.st-key-ql_menu [class*="st-key-ql_item_"] button { min-height: 1.95rem; padding-top: 0 !important; padding-bottom: 0 !important; }
.st-key-ql_menu [class*="st-key-ql_item_"] button p { font-size: .86rem !important; }
.st-key-ql_menu .ql-menu-cab { padding: .75rem 0 .25rem .3rem; }
.st-key-ql_menu [data-testid="stColumn"]:last-child { position: static; align-self: stretch; display: flex; flex-direction: column; justify-content: flex-end; }
.st-key-ql_menu [data-testid="stColumn"]:last-child [data-testid="stElementContainer"] { position: sticky; bottom: 1.4rem; }
.st-key-ql_menu .ql-esc { min-height: 30.5rem; max-width: 30rem; margin-left: auto; }
.st-key-ql_menu .ql-esc-item { justify-content: flex-end; }
.st-key-ql_menu .ql-esc-info { background: linear-gradient(90deg, rgba(11, 16, 32, .82), rgba(11, 16, 32, .35)); padding: .7rem .9rem .8rem 1.1rem; }
[class*="st-key-ql_inicio_resto"] { padding: 2.2rem clamp(1rem, 4vw, 4.5rem) 3rem clamp(1rem, 4vw, 4.5rem); }

/* Barra lateral: las mismas barras angulares de la portada, con la sección activa invertida. */
section[data-testid="stSidebar"] [class*="st-key-nav_"] { margin: .14rem .9rem .14rem .25rem; transform: skewX(-14deg); transform-origin: 0 50%;
  animation: ql-menu-entra .5s cubic-bezier(.2, .8, .2, 1) calc(var(--n, 0) * 30ms) both; }
section[data-testid="stSidebar"] [class*="st-key-nav_"] button { position: relative; overflow: hidden; border: 0 !important; border-radius: 0 !important; min-height: 2.2rem;
  justify-content: flex-start !important; padding: 0 .8rem 0 1.1rem !important; color: var(--ql-texto) !important; box-shadow: inset 3px 0 0 var(--acento, var(--ql-cian)) !important;
  background: linear-gradient(95deg, #17233C 0%, #101A2E 100%) !important; transition: transform .3s cubic-bezier(.2, .8, .2, 1), background .3s, color .2s; }
section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div { justify-content: flex-start !important; width: 100%; }
section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div > span, section[data-testid="stSidebar"] [class*="st-key-nav_"] button p { transform: skewX(14deg); }
section[data-testid="stSidebar"] [class*="st-key-nav_"] button p { font: 600 .74rem/1 var(--ql-mono) !important; letter-spacing: .03em; margin: 0; }
section[data-testid="stSidebar"] [class*="st-key-nav_"] button::before { display: none; }
section[data-testid="stSidebar"] [class*="st-key-nav_"] button::after { content: ""; position: absolute; top: 0; bottom: 0; left: 0; width: 22%; pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, .34), transparent); transform: translateX(-120%) skewX(-24deg); }
section[data-testid="stSidebar"] [class*="st-key-nav_"]:is(:hover, :focus-within) button, section[data-testid="stSidebar"] [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] {
  color: var(--ql-fondo) !important; transform: translateX(5px);
  background: linear-gradient(95deg, var(--acento, var(--ql-cian)), color-mix(in srgb, var(--acento, var(--ql-cian)) 55%, #ffffff)) !important; }
section[data-testid="stSidebar"] [class*="st-key-nav_"]:is(:hover, :focus-within) button::after { animation: ql-corte .7s cubic-bezier(.3, .7, .2, 1) both; }
section[data-testid="stSidebar"] [class*="st-key-nav_"]:has(button:focus-visible) button { outline: 2px solid var(--ql-texto); outline-offset: 2px; }
section[data-testid="stSidebar"] .ql-menu-cab { padding: 1rem 0 .3rem .3rem; }

/* Capítulos de la portada: barras grandes en escalera (semi-diagonal) y sub-portadas de cada capítulo. */
.st-key-ql_cats { margin-top: 1.6rem; gap: .7rem !important; }
.st-key-ql_cats [class*="st-key-ql_item_"] { max-width: 27rem; margin-left: calc(var(--k, 0) * 2.6rem); }
.st-key-ql_menu .st-key-ql_cats [class*="st-key-ql_item_"] button { min-height: 4rem; padding-left: 1.6rem !important; }
.st-key-ql_menu .st-key-ql_cats [class*="st-key-ql_item_"] button p { font-size: 1.25rem !important; letter-spacing: .06em; }
.st-key-ql_temas { margin-top: .8rem; }
.st-key-ql_menu .st-key-ql_temas [class*="st-key-ql_item_"] button { min-height: 2.6rem; }
.st-key-ql_menu .st-key-ql_temas [class*="st-key-ql_item_"] button p { font-size: .98rem !important; }
.ql-sub-titulo { font-size: clamp(2rem, 3.4vw, 3rem); }
.st-key-ql_sub_volver { margin: 0 0 .6rem .1rem; }
.st-key-ql_sub_volver button { color: var(--ql-tenue) !important; }
.st-key-ql_pie { padding: 1.2rem clamp(1rem, 4vw, 4.5rem) 1.6rem; margin-top: 1rem; border-top: 1px solid var(--ql-borde); gap: .4rem; }
.st-key-ql_pie .ql-pie { margin: 0; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] { display: none !important; }
@media (max-width: 900px) {
  .st-key-ql_cats [class*="st-key-ql_item_"] { margin-left: calc(var(--k, 0) * .9rem); }
  .st-key-ql_menu .st-key-ql_cats [class*="st-key-ql_item_"] button { min-height: 3.4rem; }
}
@media (max-width: 900px) {
  .st-key-ql_menu { padding-top: 3.8rem; }
  .ql-velo { background: linear-gradient(0deg, rgba(11, 16, 32, .5), rgba(11, 16, 32, .12)); }
  .ql-lectura-inicio { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
  .ql-trazo { stroke-dasharray: none !important; }
  .ql-obs-particulas, #ql-fondo-vivo, #ql-emerge { display: none; }
  .ql-atomo { transform: none; }
  [data-testid="stApp"]::before { animation: none; }
}
html { scroll-behavior: smooth; }
[class*="st-key-ql_ficha"] .katex-display{overflow-x:auto;overflow-y:hidden;margin:.2rem 0}
[class*="st-key-ql_ficha"]{background:linear-gradient(160deg,rgba(66,217,255,.06),rgba(167,139,250,.05));
  border:1px solid var(--ql-borde,#263550);border-left:3px solid #42D9FF;border-radius:12px;padding:.9rem 1.1rem;margin:.2rem 0 1rem}
.ql-ficha-et{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:#42D9FF;margin-bottom:.35rem}
.ql-ficha-tx{margin:0;font-size:.92rem;color:#F2F5FC}
.ql-ficha-ls{margin:0;padding-left:1.1rem;font-size:.86rem;color:#A7B4CE}
.ql-ficha-ls b{color:#F2F5FC;margin-right:.3rem}
.ql-ficha-mod{margin:.6rem 0 0;font-size:.8rem;color:#A7B4CE;border-top:1px solid #263550;padding-top:.5rem}
</style>
"""


def css() -> str:
    reemplazos = {"§profundo": tema.PROFUNDO}
    texto = _CSS
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto


# ---------------------------------------------------------------------
# JavaScript (mejora progresiva: la página funciona igual sin él)
# ---------------------------------------------------------------------
JS = r"""
<script>
(function () {
  var W = window;
  if (W.__qlEfectos) { return; }          // se instala una sola vez por pestaña, aunque Streamlit vuelva a ejecutar el guion
  W.__qlEfectos = true;
  var reducir = W.matchMedia ? W.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  // Luz que sigue al puntero en los destinos y paralaje del observatorio (delegación: sirve para elementos creados después).
  document.addEventListener('pointermove', function (e) {
    if (reducir.matches || !e.target || !e.target.closest) { return; }
    var d = e.target.closest('[class*="st-key-ql_dest_"]');
    if (d) {
      var r = d.getBoundingClientRect();
      d.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
      d.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
    }
    var f = document.querySelector('.ql-fondo-atomo');     // el fondo de la portada no recibe el puntero: se usa la ventana completa
    if (f) {
      f.style.setProperty('--px', ((e.clientX / W.innerWidth) * 2 - 1).toFixed(3));
      f.style.setProperty('--py', ((e.clientY / W.innerHeight) * 2 - 1).toFixed(3));
    }
    var o = e.target.closest('.ql-obs');
    if (o) {
      var q = o.getBoundingClientRect();
      o.style.setProperty('--px', (((e.clientX - q.left) / q.width) * 2 - 1).toFixed(3));
      o.style.setProperty('--py', (((e.clientY - q.top) / q.height) * 2 - 1).toFixed(3));
    }
  }, { passive: true });

  // Nube de electrones del observatorio: la mayoría de las partículas orbita en elipses inclinadas alrededor de la ilustración (más lentas
  // cuanto más lejos, con estela), y el resto deriva como polvo de fondo. Es una ilustración, no una simulación física.
  // Límite de 90 partículas; se pausa fuera de pantalla o con la pestaña oculta; no se inicia con movimiento reducido ni en pantallas pequeñas.
  var lienzo = null, ctx = null, puntos = [], anima = 0, dpr = 1, ancho = 0, alto = 0, obs = null, escenaEl = null, tPrev = 0;
  var COLORES = ['66,217,255', '167,139,250', '244,114,208'];
  function preparar(c) {
    lienzo = c; ctx = c.getContext('2d'); obs = c.closest('.ql-obs, .ql-fondo-atomo'); escenaEl = obs ? obs.querySelector('.ql-obs-escena, .ql-atomo') : null;
    dpr = Math.min(W.devicePixelRatio || 1, 2);
    medir(); tPrev = 0;
    var n = Math.round(Math.min(90, Math.max(36, ancho * alto / 9000)));
    puntos = [];
    for (var i = 0; i < n; i++) {
      var orbita = i % 10 < 7;
      var z = 0.3 + Math.random() * 0.7;
      var rx = 0.28 + Math.random() * 0.5;
      puntos.push({
        orb: orbita, z: z, c: COLORES[i % 3], f: Math.random() * 6.28,
        x: Math.random() * ancho, y: Math.random() * alto, vx: (Math.random() - .5) * .06 * z, vy: -(.03 + Math.random() * .1) * z,
        th: Math.random() * 6.2832, rx: rx, ry: rx * (0.25 + Math.random() * 0.55), tilt: (Math.random() - .5) * 2.2,
        w: (Math.random() < .5 ? -1 : 1) * (0.00018 + 0.00022 / (0.4 + rx)) , px: 0, py: 0, listo: false
      });
    }
  }
  function medir() {
    var r = lienzo.getBoundingClientRect();
    ancho = Math.max(1, r.width); alto = Math.max(1, r.height);
    lienzo.width = Math.round(ancho * dpr); lienzo.height = Math.round(alto * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function cuadro(t) {
    anima = 0;
    if (!lienzo || !lienzo.isConnected) { lienzo = null; return; }
    var r = lienzo.getBoundingClientRect();
    if (document.hidden || r.bottom < 0 || r.top > W.innerHeight) { tPrev = 0; anima = W.requestAnimationFrame(cuadro); return; }
    if (Math.abs(r.width - ancho) > 2 || Math.abs(r.height - alto) > 2) { medir(); }
    var dt = tPrev ? Math.min(60, t - tPrev) : 16; tPrev = t;
    var estilo = obs ? getComputedStyle(obs) : null;
    var px = estilo ? parseFloat(estilo.getPropertyValue('--px')) || 0 : 0;
    var py = estilo ? parseFloat(estilo.getPropertyValue('--py')) || 0 : 0;
    // Centro y tamaño de la ilustración, en coordenadas del lienzo.
    var cx = ancho * 0.72, cy = alto * 0.5, ex = ancho * 0.34, ey = alto * 0.42, esc = 1;
    if (escenaEl) {
      var q = escenaEl.getBoundingClientRect();
      cx = q.left - r.left + q.width * (escenaEl.classList.contains('ql-atomo') ? 0.7214 : 0.5); cy = q.top - r.top + q.height / 2;
      ex = Math.min(q.width, q.height * 1.55) * 0.5; ey = Math.min(q.height, q.width / 1.55) * 0.5;
    }
    // Las estelas se obtienen desvaneciendo el cuadro anterior en lugar de borrarlo.
    ctx.globalCompositeOperation = 'destination-out'; ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(0, 0, ancho, alto);
    ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
    for (var i = 0; i < puntos.length; i++) {
      var p = puntos[i], x, y;
      if (p.orb) {
        p.th += p.w * dt;
        var u = p.rx * ex * Math.cos(p.th), v = p.ry * ey * Math.sin(p.th) * (1 + 0.08 * Math.sin(t / 2600 + p.f));
        x = cx + u * Math.cos(p.tilt) - v * Math.sin(p.tilt) - px * 18 * p.z;
        y = cy + u * Math.sin(p.tilt) + v * Math.cos(p.tilt) - py * 12 * p.z;
      } else {
        p.x += p.vx * dt / 16; p.y += p.vy * dt / 16;
        if (p.y < -10) { p.y = alto + 10; p.x = Math.random() * ancho; }
        if (p.x < -10) { p.x = ancho + 10; } else if (p.x > ancho + 10) { p.x = -10; }
        x = p.x - px * 22 * p.z; y = p.y - py * 16 * p.z;
      }
      var brillo = 0.3 + 0.5 * p.z * (0.75 + 0.25 * Math.sin(t / 1100 + p.f));
      var col = 'rgba(' + p.c + ',' + brillo.toFixed(3) + ')';
      if (p.listo && p.orb) {
        ctx.beginPath(); ctx.moveTo(p.px, p.py); ctx.lineTo(x, y);
        ctx.strokeStyle = col; ctx.lineWidth = 0.8 + 1.4 * p.z; ctx.stroke();
      }
      ctx.beginPath(); ctx.arc(x, y, 0.6 + 1.4 * p.z, 0, 6.2832); ctx.fillStyle = col; ctx.fill();
      p.px = x; p.py = y; p.listo = true;
    }
    ctx.globalCompositeOperation = 'source-over';
    anima = W.requestAnimationFrame(cuadro);
  }
  // Al cambiar de página (cambia la clave del contenedor de escena) se vuelve al principio: Streamlit conserva el desplazamiento.
  var escenaActual = null;
  function seguirEscena() {
    var e = document.querySelector('[class*="st-key-ql_escena_"]');
    var nombre = e ? (e.className.match(/st-key-ql_escena_[a-z_]+/) || [''])[0] : null;
    if (nombre && escenaActual !== null && nombre !== escenaActual) {
      var m = document.querySelector('[data-testid="stMain"]');
      var modo = reducir.matches ? 'auto' : 'smooth';
      if (m && m.scrollTop > 0) { m.scrollTo({ top: 0, behavior: modo }); }
      if (W.scrollY > 0) { W.scrollTo({ top: 0, behavior: modo }); }
    }
    if (nombre && escenaActual !== null && nombre !== escenaActual && emergeVisible) {
      W.clearTimeout(emergeTimer);
      (function esperar() {
        if (!emergeVisible) { return; }
        if (!emergeListo || Date.now() - emergeInicio < MIN_EMERGE) { emergeTimer = W.setTimeout(esperar, 80); } else { retirarEmergencia(); }
      })();
    }
    if (nombre) { escenaActual = nombre; }
    W.setTimeout(seguirEscena, 150);
  }
  seguirEscena();

  // Indicadores (st.metric): cuando su valor cambia por un parámetro nuevo, destellan brevemente para señalar el resultado actualizado.
  // Solo se marcan los valores que ya existían (un indicador que aparece por primera vez no destella).
  if (W.MutationObserver) {
    new MutationObserver(function (lista) {
      if (reducir.matches) { return; }
      for (var i = 0; i < lista.length; i++) {
        var n = lista[i].target;
        var el = n.nodeType === 1 ? n : n.parentElement;
        var v = el && el.closest ? el.closest('[data-testid="stMetricValue"]') : null;
        if (v) {
          v.classList.remove('ql-actualizado'); void v.offsetWidth; v.classList.add('ql-actualizado');
          (function (x) { W.setTimeout(function () { x.classList.remove('ql-actualizado'); }, 950); })(v);
        }
      }
    }).observe(document.body, { subtree: true, characterData: true, childList: true });
  }

  // Fondo vivo: una capa fija con pocas partículas lentas detrás de todas las páginas. Se omite con movimiento reducido o pantalla pequeña,
  // se pausa con la pestaña oculta y no intercepta el puntero ni el desplazamiento.
  var fondo = null, fctx = null, fpts = [], fanim = 0, fw = 0, fh = 0, fdpr = 1;
  function fondoPreparar() {
    var app = document.querySelector('[data-testid="stApp"]');
    if (!app) { return; }
    fondo = document.createElement('canvas'); fondo.id = 'ql-fondo-vivo'; fondo.setAttribute('aria-hidden', 'true');
    app.insertBefore(fondo, app.firstChild);
    fctx = fondo.getContext('2d'); fdpr = Math.min(W.devicePixelRatio || 1, 2); fondoMedir();
    var n = Math.round(Math.min(46, Math.max(18, fw * fh / 30000)));
    fpts = [];
    for (var i = 0; i < n; i++) {
      var z = 0.25 + Math.random() * 0.75;
      fpts.push({ x: Math.random() * fw, y: Math.random() * fh, z: z, vx: (Math.random() - .5) * .05 * z, vy: -(.03 + Math.random() * .08) * z,
                  c: COLORES[i % 3], f: Math.random() * 6.28 });
    }
  }
  function fondoMedir() {
    fw = W.innerWidth; fh = W.innerHeight;
    fondo.width = Math.round(fw * fdpr); fondo.height = Math.round(fh * fdpr); fctx.setTransform(fdpr, 0, 0, fdpr, 0, 0);
  }
  function fondoCuadro(t) {
    fanim = 0;
    if (!fondo || !fondo.isConnected) { fondo = null; return; }
    if (document.hidden) { return; }
    if (fw !== W.innerWidth || fh !== W.innerHeight) { fondoMedir(); }
    fctx.clearRect(0, 0, fw, fh);
    for (var i = 0; i < fpts.length; i++) {
      var p = fpts[i];
      p.x += p.vx; p.y += p.vy;
      if (p.y < -10) { p.y = fh + 10; p.x = Math.random() * fw; }
      if (p.x < -10) { p.x = fw + 10; } else if (p.x > fw + 10) { p.x = -10; }
      var b = 0.12 + 0.3 * p.z * (0.7 + 0.3 * Math.sin(t / 1800 + p.f));
      fctx.beginPath(); fctx.arc(p.x, p.y, 0.5 + 1.2 * p.z, 0, 6.2832);
      fctx.fillStyle = 'rgba(' + p.c + ',' + b.toFixed(3) + ')'; fctx.fill();
    }
    fanim = W.requestAnimationFrame(fondoCuadro);
  }
  document.addEventListener('visibilitychange', function () { if (!document.hidden && fondo && !fanim) { fanim = W.requestAnimationFrame(fondoCuadro); } });

  // Emergencia desde abajo (inspirada en los menús de «explorador» en CSS): al elegir un tema, un cuerpo de luz sube sobre un horizonte
  // curvo desde el borde inferior y aparece el nombre del tema; cuando la página nueva está montada, el cuerpo baja y el contenido emerge
  // también desde abajo. Dura al menos ~1,1 s para que se vea aunque el servidor responda rápido y se retira solo si la navegación falla.
  var emergeEl = null, emergeTimer = 0, emergeInicio = 0, emergeVisible = false, emergeListo = false;
  var MIN_EMERGE = 1100, MAX_EMERGE = 4000;
  function crearEmergencia() {
    emergeEl = document.createElement('div'); emergeEl.id = 'ql-emerge'; emergeEl.setAttribute('aria-hidden', 'true');
    function pieza(padre, tag, clase) { var n = document.createElement(tag); n.className = clase; padre.appendChild(n); return n; }
    pieza(emergeEl, 'div', 'ql-em-cuerpo');
    var texto = pieza(emergeEl, 'div', 'ql-em-texto');
    pieza(texto, 'span', 'ql-em-tipo'); pieza(texto, 'div', 'ql-em-titulo'); pieza(texto, 'span', 'ql-em-linea');
    document.body.appendChild(emergeEl);
  }
  function emergerDesde(boton) {
    if (reducir.matches) { return; }
    if (!emergeEl) { crearEmergencia(); }
    var texto = (boton.innerText || boton.textContent || '').replace(/\s+/g, ' ').trim();
    var m = texto.match(/^(\d{2})\s+(.*)$/);
    var titulo = m ? m[2] : texto;
    var cont = boton.closest('[class*="st-key-ql_dest_"]');
    if (cont) { var h = cont.querySelector('h3'); if (h) { titulo = h.textContent.trim(); } }
    if (boton.closest('.st-key-ql_volver')) { titulo = 'Inicio'; }
    var esCat = !!boton.closest('[class*="st-key-ql_item_cat"]');
    var host = boton.closest('[class*="st-key-ql_item_"], [class*="st-key-nav_"], [class*="st-key-ql_dest_"]');
    var acento = host ? getComputedStyle(host).getPropertyValue('--acento').trim() : '';
    emergeEl.style.setProperty('--acento', acento && acento.indexOf('var(') < 0 ? acento : '');
    if (!acento || acento.indexOf('var(') === 0) { emergeEl.style.removeProperty('--acento'); }
    emergeEl.querySelector('.ql-em-tipo').textContent = m ? (esCat ? 'Capítulo ' + m[1] + ' · 04' : 'Destino ' + m[1] + ' · 15') : 'Quantum Lab';
    emergeEl.querySelector('.ql-em-titulo').textContent = titulo;
    emergeEl.classList.remove('ql-em-baja'); void emergeEl.offsetWidth; emergeEl.classList.add('ql-em-sube');
    emergeVisible = true; emergeListo = false; emergeInicio = Date.now();
    // El tiempo mínimo se cuenta desde el primer cuadro realmente pintado: si el navegador está ocupado dibujando la página, no se acorta.
    W.requestAnimationFrame(function () { W.requestAnimationFrame(function () { emergeInicio = Date.now(); emergeListo = true; }); });
    W.clearTimeout(emergeTimer); emergeTimer = W.setTimeout(retirarEmergencia, MAX_EMERGE);
  }
  function retirarEmergencia() {
    if (!emergeEl || !emergeVisible) { return; }
    emergeVisible = false; W.clearTimeout(emergeTimer);
    emergeEl.classList.add('ql-em-baja');
    emergeTimer = W.setTimeout(function () { emergeEl.classList.remove('ql-em-sube', 'ql-em-baja'); }, 800);
  }
  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('button') : null;
    if (!t || t.disabled) { return; }
    var navegacion = t.closest('[class*="st-key-nav_"], [class*="st-key-ql_item_"], .st-key-ql_volver, .st-key-ql_categoria, [class*="st-key-ql_dest_"]');
    if (navegacion) { emergerDesde(t); }
  }, true);

  // Elección de una tarjeta: se expande la elegida y se apartan las demás mientras Streamlit carga la página destino.
  // Si la navegación no ocurre (p. ej., error de red), el estado se retira solo.
  document.addEventListener('click', function (e) {
    if (!e.target || !e.target.closest) { return; }
    var d = e.target.closest('[class*="st-key-ql_dest_"]');
    if (!d || reducir.matches) { return; }
    var todas = document.querySelectorAll('[class*="st-key-ql_dest_"]');
    d.classList.add('ql-abriendo');
    for (var i = 0; i < todas.length; i++) { if (todas[i] !== d) { todas[i].classList.add('ql-aparta'); } }
    W.setTimeout(function () {
      for (var j = 0; j < todas.length; j++) { todas[j].classList.remove('ql-abriendo', 'ql-aparta'); }
    }, 2500);
  }, true);

  function vigilar() {
    if (!fondo && !reducir.matches && W.innerWidth >= 640) { fondoPreparar(); }
    if (fondo && !fanim) { fanim = W.requestAnimationFrame(fondoCuadro); }
    var c = document.getElementById('ql-particulas');
    if (c && c !== lienzo && !reducir.matches && W.innerWidth >= 640) { preparar(c); }
    if (lienzo && !anima) { anima = W.requestAnimationFrame(cuadro); }
    W.setTimeout(vigilar, 800);
  }
  vigilar();
})();
</script>
"""


def instalar_efectos(st) -> bool:
    """
    Inserta el JavaScript de efectos (una vez por pestaña). Requiere `st.html(..., unsafe_allow_javascript=True)`; si la versión de
    Streamlit no lo admite, no hace nada y la aplicación conserva todas las animaciones CSS. Devuelve True si se instaló.
    """
    try:
        if "unsafe_allow_javascript" not in inspect.signature(st.html).parameters:
            return False
        st.html(JS, unsafe_allow_javascript=True)
        return True
    except Exception:            # cualquier problema con el JS no debe impedir que la aplicación funcione
        return False


# ---------------------------------------------------------------------
# Piezas de HTML
# ---------------------------------------------------------------------
def observatorio_html(escena_svg: str, lecturas: list[tuple[str, str]], ancla: str, ancla_estudio: str) -> str:
    """Portada cinematográfica. `lecturas` son pares (valor, etiqueta) con datos reales de la aplicación."""
    e = html.escape
    lectura = "".join(f"<span><b>{e(v)}</b>{e(k)}</span>" for v, k in lecturas)
    return (
        '<div class="ql-obs">'
        '<div class="ql-obs-capa ql-obs-fondo"><span class="ql-obs-luz a"></span><span class="ql-obs-luz b"></span><span class="ql-obs-luz c"></span></div>'
        '<div class="ql-obs-plano" aria-hidden="true"></div>'
        '<canvas id="ql-particulas" class="ql-obs-particulas" aria-hidden="true"></canvas>'
        '<div class="ql-obs-contenido"><div class="ql-obs-texto">'
        '<div class="ql-obs-marca">Observatorio cuántico</div>'
        '<div class="ql-obs-titulo">Quantum Lab<span>Laboratorio interactivo de mecánica cuántica</span></div>'
        '<p class="ql-obs-desc">Sistemas cuánticos que se exploran como instrumentos: funciones de onda, niveles de energía y densidades de '
        'probabilidad calculados a partir de parámetros físicos reales, cada uno con su comprobación numérica.</p>'
        f'<div class="ql-obs-acciones"><a class="ql-boton" href="#{ancla}">Explorar simuladores</a>'
        f'<a class="ql-boton-2" href="#{ancla_estudio}">Estaciones de estudio</a></div></div>'
        f'<div class="ql-obs-escena">{escena_svg}</div></div>'
        f'<div class="ql-obs-lectura"><span class="ql-obs-pulso">Inventario del laboratorio</span>{lectura}</div>'
        '</div>')


def fondo_atomo_html(atomo_svg: str, lecturas: list[tuple[str, str]]) -> str:
    """Capa de fondo de la portada a pantalla completa: átomo ilustrado, lienzo de partículas y cifras reales del laboratorio."""
    e = html.escape
    lectura = "".join(f"<span><b>{e(v)}</b>{e(k)}</span>" for v, k in lecturas)
    return ('<div class="ql-fondo-atomo" aria-hidden="false">'
            f'<div class="ql-atomo">{atomo_svg}</div>'
            '<canvas id="ql-particulas" class="ql-obs-particulas" aria-hidden="true"></canvas>'
            '<div class="ql-velo" aria-hidden="true"></div>'
            f'<div class="ql-lectura-inicio"><span class="ql-obs-pulso">Inventario del laboratorio</span>{lectura}</div></div>')


def capitulo_html(numero: str, etiqueta: str, titulo: str, descripcion: str, ancla: str = "") -> str:
    e = html.escape
    id_ = f' id="{e(ancla)}"' if ancla else ""
    return (f'<div class="ql-capitulo"{id_}><div class="ql-capitulo-num">{e(numero)}</div><div><p class="ql-etiqueta">{e(etiqueta)}</p>'
            f'<h2>{e(titulo)}</h2><p>{e(descripcion)}</p></div></div>')


def ubicacion_html(categoria: str, titulo: str, numero: str, total: int) -> str:
    e = html.escape
    return (f'<div class="ql-ubicacion" role="navigation" aria-label="Ubicación"><span>Quantum Lab</span><span class="ql-ub-sep">/</span>'
            f'<span>{e(categoria)}</span><span class="ql-ub-sep">/</span><b>{e(titulo)}</b>'
            f'<span class="ql-ub-num">{e(numero)} · {total:02d}</span></div>')
