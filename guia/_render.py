"""
Dibujo de los diagramas de flujo en HTML + CSS (sin imágenes ni scripts).

- Semántica: cada diagrama es una lista ordenada (<ol>) con un nombre accesible; las flechas son decorativas (aria-hidden).
- Escritorio: los pasos van en una fila con flechas a la derecha. Pantallas estrechas (≤ 1100 px): columna con flechas hacia abajo.
- Colores: solo la paleta de QUANTUM LAB (contraste del texto ≥ 4.5:1 sobre el panel).
- Sin animaciones, así que no hace falta atender a `prefers-reduced-motion`.
"""

from __future__ import annotations

import html

from quantum_lab_tema import PALETA

from ._flujos import Diagrama, Paso

_e = html.escape

CSS = f"""
<style>
.ql-flujo{{margin:.4rem 0 1.4rem;}}
.ql-sr{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}}
.ql-flujo-cab h3{{font-size:1.15rem;margin:0 0 .15rem;color:{PALETA["texto"]};}}
.ql-flujo-cab p{{margin:0 0 .9rem;color:{PALETA["tenue"]};font-size:.92rem;}}
.ql-flujo ol.ql-pasos{{list-style:none;margin:0;padding:0;display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);gap:30px;align-items:stretch;}}
.ql-paso{{position:relative;background:{PALETA["panel"]};border:1.5px solid var(--tono);border-radius:12px;padding:.75rem .8rem .8rem;
  box-shadow:0 0 0 1px rgba(0,0,0,.2), 0 0 18px -8px var(--tono);display:flex;flex-direction:column;}}
.ql-paso:not(:last-child)::after{{content:"";position:absolute;top:50%;right:-27px;width:18px;height:2px;background:{PALETA["tenue"]};}}
.ql-paso:not(:last-child)::before{{content:"";position:absolute;top:calc(50% - 5px);right:-29px;border:6px solid transparent;
  border-left:8px solid {PALETA["tenue"]};border-right:0;}}
.ql-paso-cab{{display:flex;align-items:center;gap:.5rem;margin-bottom:.35rem;}}
.ql-paso-num{{flex:0 0 auto;width:1.7rem;height:1.7rem;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
  background:var(--tono);color:{PALETA["fondo"]};font-weight:700;font-size:.9rem;}}
.ql-decision .ql-paso-num{{border-radius:4px;transform:rotate(45deg);width:1.45rem;height:1.45rem;}}
.ql-decision .ql-paso-num span{{transform:rotate(-45deg);}}
.ql-paso-tit{{font-weight:700;color:{PALETA["texto"]};font-size:.98rem;line-height:1.2;}}
.ql-paso-et{{display:block;font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--tono);margin-bottom:.1rem;}}
.ql-paso ul{{margin:.1rem 0 0;padding-left:1rem;color:{PALETA["texto"]};font-size:.84rem;line-height:1.38;}}
.ql-paso li{{margin:.12rem 0;}}
.ql-rama{{margin-top:auto;padding-top:.55rem;}}
.ql-rama div{{border:1.5px dashed {PALETA["rojo"]};border-radius:8px;padding:.35rem .5rem;font-size:.78rem;color:{PALETA["texto"]};}}
.ql-rama b{{color:{PALETA["rojo"]};margin-right:.25rem;}}
.ql-recordar{{margin-top:1rem;}}
.ql-recordar h4{{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:{PALETA["tenue"]};margin:0 0 .45rem;padding:0 !important;}}
.ql-recordar ol{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;}}
.ql-recordar li{{background:{PALETA["panel"]};border:1px solid {PALETA["borde"]};border-radius:10px;padding:.55rem .7rem;display:flex;gap:.55rem;}}
.ql-recordar .ql-paso-num{{background:{PALETA["cian"]};width:1.4rem;height:1.4rem;font-size:.78rem;}}
.ql-recordar b{{display:block;color:{PALETA["texto"]};font-size:.88rem;}}
.ql-recordar span.t{{color:{PALETA["tenue"]};font-size:.8rem;line-height:1.35;}}
@media (max-width:1100px){{
  .ql-flujo ol.ql-pasos{{grid-auto-flow:row;grid-auto-columns:auto;gap:26px;}}
  .ql-paso:not(:last-child)::after{{top:auto;bottom:-22px;right:auto;left:50%;width:2px;height:16px;}}
  .ql-paso:not(:last-child)::before{{top:auto;bottom:-25px;right:auto;left:calc(50% - 5px);border:6px solid transparent;
    border-top:8px solid {PALETA["tenue"]};border-bottom:0;}}
}}
</style>
"""


def _paso_html(i: int, p: Paso) -> str:
    clase = "ql-paso ql-decision" if p.rama else "ql-paso"
    etiqueta = f'<span class="ql-paso-et">{_e(p.etiqueta)}</span>' if p.etiqueta else ""
    puntos = "".join(f"<li>{_e(t)}</li>" for t in p.puntos)
    rama = f'<div class="ql-rama"><div><b>Si no:</b>{_e(p.rama)}</div></div>' if p.rama else ""
    return (f'<li class="{clase}" style="--tono:{PALETA[p.tono]}">'
            f'<div class="ql-paso-cab"><span class="ql-paso-num" aria-hidden="true"><span>{i}</span></span>'
            f'<div>{etiqueta}<span class="ql-paso-tit"><span class="ql-sr">Paso {i}: </span>{_e(p.titulo)}</span></div></div>'
            f"<ul>{puntos}</ul>{rama}</li>")


def diagrama_html(d: Diagrama, con_titulo: bool = True) -> str:
    """HTML de un diagrama completo (sin saltos de línea, para que Markdown no lo trate como bloque de código)."""
    cab = (f'<div class="ql-flujo-cab"><h3>{_e(d.titulo)}</h3><p>{_e(d.subtitulo)}</p></div>' if con_titulo else "")
    pasos = "".join(_paso_html(i, p) for i, p in enumerate(d.pasos, start=1))
    recordar = ""
    if d.recordar:
        items = "".join(f'<li><span class="ql-paso-num" aria-hidden="true">{i}</span><div><b>{_e(t)}</b><span class="t">{_e(x)}</span></div></li>'
                        for i, (t, x) in enumerate(d.recordar, start=1))
        recordar = f'<div class="ql-recordar"><h4>Para recordar</h4><ol>{items}</ol></div>'
    return (f'<section class="ql-flujo" aria-label="Diagrama de flujo: {_e(d.titulo)}">{cab}'
            f'<ol class="ql-pasos">{pasos}</ol>{recordar}</section>')
