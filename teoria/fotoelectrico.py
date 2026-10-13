"""
teoria/fotoelectrico.py — Teoría: Efecto fotoeléctrico.

Contenido movido desde la pestaña «Teoría» del simulador (efecto_fotoelectrico.py). Se muestra en el Centro de teoría.
"""

import streamlit as st

import quantum_lab_comun as qc


def mostrar() -> None:
    sub = st.tabs(["Historia", "Clásico frente a experimento", "La explicación de Einstein",
                   "Millikan y la constante h", "Dualidad y aplicaciones", "Resumen de ecuaciones"])
    with sub[0]:
        qc.seccion("Un efecto descubierto por casualidad")
        st.markdown(
            "En 1887 Heinrich Hertz, mientras confirmaba la existencia de las ondas electromagnéticas, notó que la "
            "chispa de su receptor saltaba con más facilidad cuando le llegaba la luz ultravioleta de la chispa "
            "emisora. Sin saberlo, había observado electrones arrancados de un metal por la luz. Las décadas "
            "siguientes convirtieron esa curiosidad en uno de los experimentos que dieron origen a la física cuántica.")
        qc.tabla_libre([
            {"Año": "1887", "Quién": "H. Hertz", "Hallazgo": "La luz ultravioleta facilita las descargas eléctricas entre electrodos."},
            {"Año": "1888", "Quién": "W. Hallwachs", "Hallazgo": "Una placa de zinc con carga negativa se descarga al iluminarla con UV; con carga positiva, no."},
            {"Año": "1899", "Quién": "J. J. Thomson", "Hallazgo": "Mide la relación carga/masa de las partículas emitidas: son electrones."},
            {"Año": "1902", "Quién": "P. Lenard", "Hallazgo": "La energía máxima de los electrones no depende de la intensidad de la luz, sino de su frecuencia."},
            {"Año": "1905", "Quién": "A. Einstein", "Hallazgo": "Propone que la luz está formada por cuantos de energía hν: K_max = hν − Φ."},
            {"Año": "1916", "Quién": "R. A. Millikan", "Hallazgo": "Confirma la ecuación de Einstein con gran precisión y mide h."},
            {"Año": "1921", "Quién": "Premio Nobel", "Hallazgo": "Einstein lo recibe «especialmente por su descubrimiento de la ley del efecto fotoeléctrico»."},
            {"Año": "1923", "Quién": "A. H. Compton / Premio Nobel", "Hallazgo": "Compton demuestra que los cuantos de luz también tienen momento (p = h/λ); Millikan recibe el Nobel."},
            {"Año": "1926", "Quién": "G. N. Lewis", "Hallazgo": "Propone el nombre «fotón» para el cuanto de luz."},
        ])
        st.markdown("Es notable que el Nobel de Einstein no fuera por la relatividad, y que Millikan, que diseñó sus "
                    "experimentos convencido de que la idea de los cuantos de luz era errónea, terminara siendo quien "
                    "mejor la confirmó.")
    with sub[1]:
        qc.seccion("Lo que predice la teoría ondulatoria de la luz")
        st.markdown(
            "Para la física clásica la luz es una onda electromagnética cuya energía se reparte de forma continua "
            "por todo el frente de onda y es proporcional a su **intensidad** (al cuadrado de la amplitud del campo "
            "eléctrico). Un electrón del metal absorbería esa energía poco a poco, como un corcho que oscila con "
            "las olas, hasta acumular la suficiente para escapar.")
        qc.tabla_libre([
            {"Aspecto": "Energía de los electrones emitidos", "Predicción clásica": "Crece con la intensidad de la luz",
             "Lo que se observa": "No depende de la intensidad; crece linealmente con la frecuencia"},
            {"Aspecto": "Frecuencia mínima", "Predicción clásica": "No existe: con luz intensa cualquier frecuencia arranca electrones",
             "Lo que se observa": "Por debajo de la frecuencia umbral ν₀ no se emite ningún electrón, por intensa que sea la luz"},
            {"Aspecto": "Tiempo de respuesta", "Predicción clásica": "Con luz débil, segundos o incluso meses para acumular la energía",
             "Lo que se observa": "La emisión es instantánea (retardo medido menor que 10⁻⁹ s)"},
            {"Aspecto": "Número de electrones por segundo", "Predicción clásica": "Crece con la intensidad",
             "Lo que se observa": "Crece con la intensidad (la única predicción que acierta)"},
        ])
        qc.seccion("Una estimación del retardo clásico")
        st.markdown("Supongamos luz muy débil, de 10⁻⁶ W/m², y que cada átomo de la superficie (radio ≈ 0.1 nm) "
                    "absorbe la energía que cae sobre su sección:")
        st.latex(r"P_{\rm átomo}=I\,\pi r^2\approx10^{-6}\cdot3\times10^{-20}=3\times10^{-26}\ \mathrm{W}\qquad t=\frac{2\ \mathrm{eV}}{P_{\rm átomo}}\approx\frac{3.2\times10^{-19}\ \mathrm{J}}{3\times10^{-26}\ \mathrm{W}}\approx10^{7}\ \mathrm{s}")
        st.markdown("Unos cuatro meses. En el experimento, en cambio, los primeros electrones salen en cuanto llega "
                    "la luz (con luz débil salen **pocos**, pero salen enseguida). El modelo de una energía "
                    "repartida de forma continua no puede explicarlo.")
    with sub[2]:
        qc.seccion("La hipótesis de los cuantos de luz (1905)")
        st.markdown(
            "Einstein extendió la idea de Planck: no solo la materia intercambia energía en paquetes, sino que la luz "
            "misma **está formada** por cuantos localizados, cada uno con energía proporcional a la frecuencia:")
        st.latex(r"E_{\rm fotón}=h\nu=\frac{hc}{\lambda},\qquad h=6.62607015\times10^{-34}\ \mathrm{J\,s}")
        st.markdown(
            "Cada fotón entrega **toda** su energía a **un solo** electrón. Parte de ella, la **función de trabajo** Φ, "
            "se gasta en sacarlo del metal; el resto queda como energía cinética. Los electrones más energéticos "
            "(los que salen de la superficie sin perder energía en choques) tienen:")
        st.latex(r"K_{\max}=h\nu-\Phi\quad(h\nu\ge\Phi),\qquad\text{sin emisión si }h\nu<\Phi")
        qc.seccion("Cómo explica cada observación")
        st.markdown(
            "- **Frecuencia umbral.** Si hν < Φ, un fotón no tiene energía suficiente y no se suman fotones (es "
            "prácticamente imposible que un electrón absorba dos a la vez con luz ordinaria). El umbral es ν₀ = Φ/h, "
            "o λ₀ = hc/Φ.\n"
            "- **La intensidad no cambia K_max.** Más intensidad significa **más fotones** por segundo, no fotones más "
            "energéticos: aumenta la corriente, no la energía de cada electrón.\n"
            "- **Emisión instantánea.** La energía llega concentrada en el fotón; no hay que esperar a acumularla.\n"
            "- **Dependencia lineal.** K_max crece con ν con pendiente h, la misma para todos los metales.")
        qc.seccion("Conceptos clave")
        qc.tabla_libre([
            {"Concepto": "Función de trabajo Φ", "Significado": "Energía mínima para arrancar un electrón de la superficie. Depende del metal y del estado de la superficie (2–6 eV típicamente)."},
            {"Concepto": "Frecuencia umbral ν₀ = Φ/h", "Significado": "Frecuencia mínima de la luz que produce emisión."},
            {"Concepto": "Potencial de frenado V₀", "Significado": "Tensión inversa que detiene incluso a los electrones más rápidos: eV₀ = K_max."},
            {"Concepto": "Corriente de saturación", "Significado": "Corriente cuando todos los electrones emitidos llegan al colector; proporcional al número de fotones por segundo."},
            {"Concepto": "Eficiencia cuántica η", "Significado": "Fracción de fotones que arrancan un electrón. En metales limpios suele ser inferior al 0.1 %; en fotocátodos especiales llega al 20–30 %."},
        ])
    with sub[3]:
        qc.seccion("El experimento de Millikan (1914–1916)")
        st.markdown(
            "Millikan iluminó superficies de metales alcalinos (sodio, potasio, litio) con las líneas del mercurio. "
            "Para evitar que la oxidación cambiara la función de trabajo, raspaba los metales **dentro del vacío** con "
            "una cuchilla movida desde fuera. Para cada frecuencia midió el potencial de frenado V₀. Como "
            "eV₀ = hν − Φ, al representar V₀ frente a ν se obtiene una recta:")
        st.latex(r"V_0=\frac{h}{e}\,\nu-\frac{\Phi}{e}\qquad\Rightarrow\qquad\text{pendiente}=\frac{h}{e},\qquad\text{corte con el eje }\nu:\ \nu_0=\frac{\Phi}{h}")
        st.markdown(
            "- La **pendiente** es la misma para todos los metales: solo depende de constantes universales.\n"
            "- Con e conocida (Millikan la había medido con su experimento de la gota de aceite), la pendiente da h. "
            "Obtuvo h ≈ 6.57×10⁻³⁴ J·s, a menos del 1 % del valor actual, en acuerdo con el valor deducido por "
            "Planck de la radiación del cuerpo negro.\n"
            "- El **corte** con el eje de frecuencias da la frecuencia umbral y, con ella, la función de trabajo.\n"
            "- Las diferencias de potencial de contacto entre los electrodos desplazan la recta, pero **no cambian "
            "la pendiente**: por eso el método es tan robusto.\n\n"
            "La pestaña «Determinación de h» reproduce este análisis con datos simulados y ruido de medida.")
    with sub[4]:
        qc.seccion("Dualidad onda–partícula")
        st.markdown(
            "La luz produce interferencia y difracción, fenómenos típicamente **ondulatorios**, pero en el efecto "
            "fotoeléctrico se comporta como un chorro de **partículas** de energía hν. Ninguna de las dos imágenes es "
            "completa por sí sola: la luz se propaga como una onda (que da la probabilidad de detectar un fotón en "
            "cada lugar) y se absorbe en cuantos. En 1924 De Broglie propuso la simetría inversa: las partículas "
            "materiales, como el electrón, también tienen una longitud de onda λ = h/p.")
        st.latex(r"E=h\nu\qquad p=\frac{h}{\lambda}\qquad\text{(fotón: }E=pc\text{, masa nula)}")
        qc.seccion("Aplicaciones")
        st.markdown(
            "- **Fotomultiplicadores.** Un fotón arranca un electrón de un fotocátodo y una cascada de electrodos lo "
            "multiplica millones de veces: detectan fotones individuales (física de partículas, medicina nuclear, "
            "detectores de neutrinos).\n"
            "- **Cámaras digitales (CCD y CMOS).** Usan el efecto fotoeléctrico **interno**: el fotón lleva un "
            "electrón del semiconductor a la banda de conducción, sin que salga del material, y se cuentan las cargas "
            "de cada píxel.\n"
            "- **Celdas solares.** El efecto fotovoltaico se basa en el mismo principio: fotones con energía mayor que "
            "la banda prohibida del semiconductor (≈ 1.1 eV en el silicio) generan pares electrón–hueco.\n"
            "- **Espectroscopía de fotoelectrones (XPS, ARPES).** Midiendo la energía de los electrones arrancados con "
            "rayos X o ultravioleta se identifican los elementos de una superficie y su estructura electrónica.\n"
            "- **Visores nocturnos** e intensificadores de imagen, sensores de presencia y fotocélulas.\n"
            "- **Naves espaciales y polvo lunar.** La luz solar ultravioleta arranca electrones de sus superficies, "
            "que quedan cargadas positivamente.")
        qc.seccion("Limitaciones del modelo del simulador")
        st.markdown(
            "- K_max corresponde solo a los electrones más energéticos; los demás salen con menos energía, así que la "
            "curva corriente–voltaje real se curva de forma suave cerca de −V₀.\n"
            "- La función de trabajo depende de la cara del cristal, de la limpieza y de la temperatura: los valores de "
            "la tabla son aproximados.\n"
            "- La eficiencia cuántica real depende de la longitud de onda; aquí se toma constante.")
    with sub[5]:
        qc.seccion("Ecuación de Einstein")
        st.latex(r"E_{\rm fotón}=h\nu=\frac{hc}{\lambda}\qquad K_{\max}=h\nu-\Phi\quad(h\nu\ge\Phi)\qquad K_{\max}=0\quad(h\nu<\Phi)")
        st.latex(r"\nu_0=\frac{\Phi}{h}\qquad \lambda_0=\frac{hc}{\Phi}\qquad K_{\max}=\tfrac12 m_e v_{\max}^2\ \Rightarrow\ v_{\max}=\sqrt{\frac{2K_{\max}}{m_e}}")
        qc.seccion("Potencial de frenado y corriente")
        st.latex(r"eV_0=K_{\max}=h\nu-\Phi\ \Rightarrow\ V_0=\frac{h}{e}\,\nu-\frac{\Phi}{e}")
        st.latex(r"N=\frac{P}{h\nu}\ \text{fotones/s},\qquad I_{\rm sat}=\eta\,e\,N\qquad I(V)=I_{\rm sat}\left(1-\frac{e|V|}{K_{\max}}\right)\ (-V_0<V<0)")
        st.markdown("La última expresión es un modelo didáctico simplificado; la forma real de la curva depende de la "
                    "geometría de la fotocélula y de la distribución de energías de los electrones.")
        qc.seccion("Constantes útiles")
        st.latex(r"hc=1239.84\ \mathrm{eV\,nm}\qquad \frac{h}{e}=4.1357\times10^{-15}\ \mathrm{V\,s}\qquad 1\ \mathrm{eV}=1.602177\times10^{-19}\ \mathrm{J}")
