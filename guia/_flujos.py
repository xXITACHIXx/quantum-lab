"""
Contenido de los diagramas de flujo de la guía de usuario.

Cada diagrama es una secuencia de pasos numerados (con una posible rama de error en el paso de validación) y una fila
«Para recordar». Cada paso puede citar las funciones que lo implementan en la web (`web`) y en el cuaderno de Colab
(`colab`); `guia.ejecutar_pruebas` comprueba que esas funciones existan, para que los diagramas no se desactualicen.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TONOS = ("cian", "violeta", "verde", "amarillo", "rojo")


@dataclass(frozen=True)
class Paso:
    titulo: str
    puntos: tuple[str, ...]
    tono: str = "cian"
    etiqueta: str = ""                 # texto corto sobre el título (por ejemplo, «Celda 2»)
    rama: str = ""                     # camino alternativo (decisión): qué pasa si la condición falla
    web: tuple[str, ...] = ()          # funciones del módulo web que hacen este paso
    colab: tuple[str, ...] = ()        # funciones del cuaderno de Colab que hacen este paso


@dataclass(frozen=True)
class Diagrama:
    id: str
    titulo: str
    subtitulo: str
    pasos: tuple[Paso, ...]
    recordar: tuple[tuple[str, str], ...] = ()
    modulo_web: str = ""               # módulo de la web (para comprobar `Paso.web`)
    cuaderno: str = ""                 # cuaderno de Colab (para comprobar `Paso.colab`)
    simulador: str = ""                # clave de la página del simulador (botón «Abrir»)
    notas: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------
# 1. Cómo se usa cualquier simulador de la web
# ---------------------------------------------------------------------
USAR_SIMULADOR = Diagrama(
    "usar", "Ruta de un cálculo en la web", "De la portada a la gráfica: así se usa cualquier simulador",
    (
        Paso("Portada", ("Elegir un capítulo", "Entrar al simulador"), "cian"),
        Paso("Parámetros", ("Estado: n, o l y mₗ", "Tamaño, masa y unidades", "O una configuración de ejemplo"), "violeta"),
        Paso("Validación", ("Revisa rangos y unidades",), "amarillo", etiqueta="Decisión",
             rama="Dato inválido: aparece un mensaje con la causa y no se grafica"),
        Paso("Cálculo", ("Ecuaciones exactas del modelo", "Resultados en caché: los cambios son rápidos"), "verde"),
        Paso("Pestañas", ("Gráficas interactivas", "Métricas y tablas", "Guía de práctica y autoevaluación"), "cian"),
        Paso("Exportar", ("CSV, PNG o HTML", "Compartir configuración (enlace)"), "violeta"),
    ),
    (("Restaurar valores iniciales", "Vuelve al punto de partida del simulador."),
     ("Pruebas numéricas", "La última pestaña de cada simulador comprueba sus cálculos."),
     ("Enlace compartido", "Guarda los parámetros: quien lo abre ve la misma gráfica.")),
)

# ---------------------------------------------------------------------
# 2. Cuadernos de Colab: estructura de celdas y qué pasa al cambiar un dato
# ---------------------------------------------------------------------
CELDAS_COLAB = Diagrama(
    "celdas", "Estructura de un cuaderno de Colab", "Seis celdas que se ejecutan en orden; la última es el simulador",
    (
        Paso("Utilidades", ("Formato de resultados", "Lectura de datos y diagnóstico"), "cian", etiqueta="Celda 1"),
        Paso("Física", ("Ecuaciones del modelo", "Revisión de los datos"), "violeta", etiqueta="Celda 2"),
        Paso("Gráficas", ("Figuras 2D y 3D",), "verde", etiqueta="Celda 3"),
        Paso("Resultados en texto", ("Parámetros, resultados e interpretación",), "amarillo", etiqueta="Celda 4"),
        Paso("Pruebas numéricas", ("Normalización, ortogonalidad y fórmulas exactas",), "cian", etiqueta="Celda 5"),
        Paso("Simulador interactivo", ("Casillas arriba, resultados en pestañas",), "violeta", etiqueta="Celda 6"),
    ),
    (("Ejecutar todo", "Menú Entorno de ejecución → Ejecutar todo."),
     ("Sin instalar nada", "Todo lo necesario ya viene en Colab."),
     ("Pruebas", "Botón «Ejecutar las pruebas numéricas» en la última pestaña.")),
)

CALCULO_COLAB = Diagrama(
    "calculo_colab", "Qué pasa al cambiar un dato en Colab", "Cada vez que se escribe un valor y se pulsa Enter",
    (
        Paso("Entrada", ("Casillas y deslizadores", "Acepta 2,5 · 1e-30 · 2*pi"), "cian"),
        Paso("Diagnóstico", ("ERROR: no se puede calcular", "AVISO y NOTA: se calcula y se explica"), "amarillo",
             etiqueta="Decisión", rama="ERROR: se explica la causa y se detiene el cálculo"),
        Paso("Física", ("Ecuaciones del modelo",), "violeta"),
        Paso("Informe", ("Parámetros, resultados, niveles e interpretación",), "verde"),
        Paso("Gráficas", ("Se dibujan debajo del informe",), "cian"),
    ),
    (("Se recalcula solo", "No hay botón Calcular: basta cambiar el dato."),
     ("Validez física", "El apartado «Validez física de los datos» explica cada aviso."),
     ("Mismos resultados", "La web y Colab usan las mismas ecuaciones.")),
)

# ---------------------------------------------------------------------
# 3. Un diagrama por simulador (mismos pasos en la web y en Colab)
# ---------------------------------------------------------------------
CAJA = Diagrama(
    "caja", "Partícula en una caja", "Pozo infinito de longitud a: del estado n a sus gráficas",
    (
        Paso("Entradas", ("Estado n (1, 2, 3…)", "Longitud a y masa m", "Superposición: cuántos estados, cuáles y sus coeficientes"),
             "cian"),
        Paso("Validación", ("n entero positivo", "a y m positivos"), "amarillo", etiqueta="Decisión",
             rama="Dato inválido: mensaje con la causa", web=("validar_parametros_caja",), colab=("revisar_n", "revisar_caja")),
        Paso("Física", ("Eₙ = n²π²ħ²/(2ma²)", "ψₙ(x) = √(2/a)·sen(nπx/a)", "Ψ(x,t) = Σ cₙ ψₙ(x) e^(−iEₙt/ħ)"), "violeta",
             web=("energia_nivel", "funcion_onda", "onda_total"), colab=("energia_nivel", "funcion_onda", "onda_total")),
        Paso("Resultados", ("Energía, λ = 2a/n y n − 1 nodos", "Δx, ⟨x⟩ y probabilidad en una región"), "verde",
             web=("calcular_estado_individual", "calcular_superposicion"), colab=("informe_estado", "informe_superposicion")),
        Paso("Gráficas", ("Función de onda y densidad de probabilidad", "Energía frente a la posición",
                          "Superposición: Re Ψ, Im Ψ, |Ψ|² y animación"), "cian",
             web=("figura_estado_individual", "figura_superposicion"), colab=("figura_estado", "figura_superposicion")),
        Paso("Pruebas", ("Normalización y ortogonalidad", "Energías contra la fórmula exacta"), "violeta",
             web=("ejecutar_pruebas",), colab=("ejecutar_pruebas",)),
    ),
    (("Coeficientes", "Se normalizan solos: Σ|cₙ|² = 1."),
     ("Tiempo", "τ = E₁t/ħ; la densidad se repite cada T = 2πħ/E₁."),
     ("Estado estacionario", "Su densidad de probabilidad no cambia con el tiempo.")),
    modulo_web="particula_caja", cuaderno="QUANTUM_LAB_particula_caja_colab.ipynb", simulador="caja",
)

OSCILADOR = Diagrama(
    "oscilador", "Oscilador armónico", "Potencial parabólico V = ½mω²x²: del estado n a sus densidades de energía",
    (
        Paso("Entradas", ("Estado n (0, 1, 2…)", "Masa m y frecuencia ω", "Superposición: estados, coeficientes e instante"), "cian"),
        Paso("Validación", ("n entero, n ≥ 0", "m y ω positivos"), "amarillo", etiqueta="Decisión",
             rama="Dato inválido: mensaje con la causa", web=("validar_parametros_oscilador",), colab=("revisar_n_osc", "revisar_oscilador")),
        Paso("Física", ("x₀ = √(ħ/mω)", "ψₙ con polinomios de Hermite", "Eₙ = ħω(n + ½)"), "violeta",
             web=("longitud_caracteristica", "psi_oscilador", "energia_teorica"), colab=("longitud_caracteristica", "funciones_hermite", "estado")),
        Paso("Resultados", ("Punto de retorno A = √(2n+1)·x₀", "Probabilidad en la zona prohibida", "Virial: ⟨T⟩ = ⟨V⟩ = E/2"), "verde",
             web=("calcular_estado", "punto_retorno", "probabilidad_fuera_retorno"), colab=("informe_estado", "informe_superposicion")),
        Paso("Gráficas", ("Función de onda y densidad de probabilidad", "Densidades de energía cinética y potencial",
                          "Energía frente a la posición"), "cian",
             web=("figura_estado_individual", "figura_dinamica"), colab=("figura_estado", "figura_superposicion")),
        Paso("Pruebas", ("Normalización y ortogonalidad", "Energía numérica = ħω(n + ½)"), "violeta",
             web=("ejecutar_pruebas",), colab=("ejecutar_pruebas",)),
    ),
    (("Punto cero", "n = 0 tiene energía ħω/2: nunca está en reposo."),
     ("Zona prohibida", "En n = 0, el 15.73 % de la probabilidad está fuera de los puntos de retorno."),
     ("Límite clásico", "Con n grande, la densidad se parece a la clásica.")),
    modulo_web="oscilador_armonico", cuaderno="QUANTUM_LAB_oscilador_armonico_colab.ipynb", simulador="oscilador",
)

ESFERA = Diagrama(
    "esfera", "Partícula en una esfera", "Armónicos esféricos: de l y mₗ a la densidad de probabilidad en x, y, z",
    (
        Paso("Entradas", ("l y mₗ, con |mₗ| ≤ l", "Radio R; orbital complejo o real", "Punto (x, y, z)"), "cian"),
        Paso("Validación", ("|mₗ| ≤ l y R > 0", "El punto no puede ser el origen"), "amarillo", etiqueta="Decisión",
             rama="Dato inválido: mensaje con la causa", web=("validar_parametros_esfera",), colab=("revisar_lm", "revisar_rotor")),
        Paso("Física", ("Yₗᵐ(θ, φ) con Legendre normalizado", "(x, y, z) → (r, θ, φ): cos θ = z/r", "P = |Yₗᵐ|²/R²"), "violeta",
             web=("armonico_esferico", "cartesianas_a_esfericas", "densidad_probabilidad"),
             colab=("armonico", "a_esfericas", "densidad_probabilidad")),
        Paso("Resultados", ("L² = ħ²l(l+1) y L_z = mₗħ", "l − |mₗ| conos nodales", "Densidad en el punto elegido"), "verde",
             web=("densidad_en_punto", "nodos_latitud"), colab=("informe_densidad", "informe_armonico")),
        Paso("Gráficas", ("Esfera coloreada por P y superficie |Y|²", "Cortes en los planos xz, yz y xy", "Densidad angular frente a z"),
             "cian", web=("figura_densidad_3d", "figura_densidad_cartesiana", "figura_superficie_3d"),
             colab=("figura_densidad_3d", "figura_densidad_cartesiana", "figura_3d")),
        Paso("Pruebas", ("∫|Y|² dΩ = 1 y ortogonalidad", "Formas cerradas de Y₀⁰ a Y₂ᵐ"), "violeta",
             web=("ejecutar_pruebas",), colab=("ejecutar_pruebas",)),
    ),
    (("Probabilidad", "P·dA es la probabilidad en el área dA = R² sen θ dθ dφ."),
     ("Orbital complejo", "Su densidad solo depende de z: simetría alrededor del eje z."),
     ("Degeneración", "Cada l tiene 2l + 1 valores de mₗ con la misma energía.")),
    modulo_web="particula_esfera", cuaderno="QUANTUM_LAB_particula_esfera_colab.ipynb", simulador="esfera",
)

SIMULADORES = (CAJA, OSCILADOR, ESFERA)
TODOS = (USAR_SIMULADOR, CELDAS_COLAB, CALCULO_COLAB) + SIMULADORES


def mermaid(d: Diagrama) -> str:
    """El mismo diagrama en sintaxis Mermaid, para pegarlo en draw.io, el editor de Mermaid, Notion o GitHub."""
    lineas = ["flowchart LR"]
    for i, p in enumerate(d.pasos, start=1):
        texto = p.titulo.replace('"', "'")
        forma = ('{"' + texto + '"}') if p.rama else ('["' + f"{i}. {texto}" + '"]')
        lineas.append(f"    P{i}{forma}")
    for i in range(1, len(d.pasos)):
        etiqueta = "|Sí|" if d.pasos[i - 1].rama else ""
        lineas.append(f"    P{i} -->{etiqueta} P{i + 1}")
    for i, p in enumerate(d.pasos, start=1):
        if p.rama:
            lineas.append(f'    P{i} -->|No| E{i}["{p.rama.replace(chr(34), chr(39))}"]')
    return "\n".join(lineas)
