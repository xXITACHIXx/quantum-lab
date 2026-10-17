"""biblioteca/_conexiones.py — Mapa de conexiones entre conceptos del glosario (aristas dirigidas con etiqueta)."""

from __future__ import annotations

from biblioteca._modelo import Relacion as Rel

RELACIONES = (
    Rel("funcion_onda", "amplitud", "su valor es una amplitud"),
    Rel("amplitud", "densidad_prob", "su módulo al cuadrado da"),
    Rel("densidad_prob", "normalizacion", "debe integrar a 1 (normalización)"),
    Rel("hamiltoniano", "schrodinger_est", "forma la ecuación"),
    Rel("schrodinger_est", "cuantizacion", "con condiciones de frontera da"),
    Rel("schrodinger_est", "estado_estacionario", "sus soluciones son"),
    Rel("estado_estacionario", "superposicion", "se combinan en"),
    Rel("superposicion", "interferencia", "produce"),
    Rel("fase", "interferencia", "la fase relativa controla"),
    Rel("operador", "autovalor", "tiene"),
    Rel("autovalor", "medida", "son los resultados posibles de"),
    Rel("operador", "conmutador", "dos operadores definen un"),
    Rel("conmutador", "incertidumbre", "si no es cero implica"),
    Rel("incertidumbre", "energia_cero", "explica la"),
    Rel("pozo_infinito", "cuantizacion", "ejemplo de"),
    Rel("pozo_infinito", "nodo", "tiene n − 1"),
    Rel("pozo_infinito", "de_broglie", "ondas estacionarias de"),
    Rel("oscilador", "hermite", "sus autofunciones usan"),
    Rel("oscilador", "punto_retorno", "tiene"),
    Rel("punto_retorno", "tunel", "más allá aparece"),
    Rel("oscilador", "virial", "cumple"),
    Rel("de_broglie", "dualidad", "expresa la"),
    Rel("foton", "dualidad", "cara corpuscular de la"),
    Rel("foton", "funcion_trabajo", "debe superar la"),
    Rel("funcion_trabajo", "frecuencia_umbral", "fija la"),
    Rel("funcion_trabajo", "potencial_frenado", "determina, con hν, el"),
    Rel("intensidad", "corriente_fotoelectrica", "controla la"),
    Rel("intensidad", "foton", "cuenta el número de"),
    Rel("momento_angular", "armonicos", "tiene como autofunciones los"),
    Rel("armonicos", "orbital", "forman la parte angular del"),
    Rel("orbital", "densidad_radial", "su parte radial da la"),
    Rel("numero_cuantico", "orbital", "identifican el"),
    Rel("modelo_bohr", "radio_bohr", "define el"),
    Rel("modelo_bohr", "serie_espectral", "explica las"),
    Rel("masa_reducida", "serie_espectral", "corrige las"),
    Rel("espin", "numero_cuantico", "añade mₛ a los"),
    Rel("degeneracion", "orbital", "cuenta los orbitales de igual energía"),
)


def vecinos(termino_id: str) -> tuple[list, list]:
    """(salientes, entrantes) del concepto: listas de (otro_id, etiqueta)."""
    sal = [(r.destino, r.etiqueta) for r in RELACIONES if r.origen == termino_id]
    ent = [(r.origen, r.etiqueta) for r in RELACIONES if r.destino == termino_id]
    return sal, ent


def dot(ids=None) -> str:
    """Grafo en formato DOT (para st.graphviz_chart). Si se dan ids, solo las aristas entre ellos."""
    from biblioteca._glosario import POR_ID
    sel = set(ids) if ids else None
    lineas = ['digraph G {', 'rankdir=LR;', 'node [shape=box, style="rounded", fontname="Source Sans"];', 'edge [fontname="Source Sans", fontsize=10];']
    usados = set()
    for r in RELACIONES:
        if sel is None or (r.origen in sel and r.destino in sel):
            usados |= {r.origen, r.destino}
            lineas.append(f'{r.origen} -> {r.destino} [label="{r.etiqueta}"];')
    for i in sorted(usados):
        lineas.append(f'{i} [label="{POR_ID[i].nombre}"];')
    lineas.append("}")
    return "\n".join(lineas)
