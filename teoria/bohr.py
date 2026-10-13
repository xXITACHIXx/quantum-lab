"""
teoria/bohr.py — Teoría: Modelo de Bohr y átomo de hidrógeno.

Contenido movido desde la pestaña «Teoría» del simulador (modelo_bohr.py). Se muestra en el Centro de teoría.
"""

import streamlit as st

import quantum_lab_comun as qc


def mostrar() -> None:
    sub = st.tabs(["Antecedentes", "Postulados y deducción", "Espectro y series", "Éxitos y límites",
                   "De Bohr a Schrödinger", "Resumen de ecuaciones"])
    with sub[0]:
        qc.seccion("El problema: un átomo que no debería existir")
        st.markdown(
            "En 1911 Rutherford demostró, dispersando partículas alfa en láminas de oro, que el átomo tiene un "
            "**núcleo** diminuto y positivo con los electrones alrededor. El modelo natural era un «sistema solar» "
            "en miniatura, pero chocaba con el electromagnetismo clásico: una carga que gira está **acelerada** y "
            "toda carga acelerada radia energía (fórmula de Larmor).")
        st.latex(r"P=\frac{e^2a^2}{6\pi\varepsilon_0c^3}\qquad\Rightarrow\qquad t_{\rm colapso}\approx\frac{a_0^3}{4r_e^2c}\approx1.6\times10^{-11}\ \mathrm{s}")
        st.markdown(
            "Según la física clásica el electrón perdería energía, caería en espiral hacia el núcleo en unas "
            "decenas de picosegundos y, mientras tanto, emitiría luz de **todas** las frecuencias (un espectro "
            "continuo). La realidad es la opuesta: los átomos son **estables** y el hidrógeno emite solo unas "
            "pocas **líneas** de colores muy precisos.")
        qc.seccion("Las pistas experimentales")
        qc.tabla_libre([
            {"Año": "1853–1862", "Quién": "Ångström", "Hallazgo": "Mide con precisión las cuatro líneas visibles del hidrógeno."},
            {"Año": "1885", "Quién": "J. J. Balmer", "Hallazgo": "Encuentra la fórmula empírica λ = B·n²/(n² − 4), con B = 364.56 nm."},
            {"Año": "1888", "Quién": "J. Rydberg", "Hallazgo": "La generaliza: 1/λ = R(1/n₁² − 1/n₂²) para todas las series."},
            {"Año": "1900", "Quién": "M. Planck", "Hallazgo": "La energía de la radiación se intercambia en cuantos E = hν."},
            {"Año": "1905", "Quién": "A. Einstein", "Hallazgo": "La luz misma está formada por cuantos (efecto fotoeléctrico)."},
            {"Año": "1906–1908", "Quién": "Lyman, Paschen", "Hallazgo": "Descubren las series ultravioleta e infrarroja que predice la fórmula."},
            {"Año": "1911", "Quién": "E. Rutherford", "Hallazgo": "Modelo nuclear del átomo."},
            {"Año": "1913", "Quién": "N. Bohr", "Hallazgo": "Combina el átomo nuclear con la cuantización y deduce la constante de Rydberg."},
        ])
        st.markdown("La fórmula de Rydberg funcionaba de maravilla, pero nadie sabía **por qué**. El mérito de Bohr fue "
                    "deducirla, incluido el valor numérico de R, a partir de constantes fundamentales (mₑ, e, h, c).")
    with sub[1]:
        qc.seccion("Los tres postulados de Bohr (1913)")
        st.markdown(
            "1. **Estados estacionarios.** El electrón gira en órbitas circulares bajo la atracción de Coulomb y, "
            "en ciertas órbitas permitidas, **no radia**, en contra de la electrodinámica clásica.\n"
            "2. **Cuantización del momento angular.** Las órbitas permitidas son aquellas en que el momento angular "
            "es un múltiplo entero de ħ = h/2π:")
        st.latex(r"L=m_e\,v\,r=n\hbar,\qquad n=1,2,3,\dots")
        st.markdown(
            "3. **Saltos cuánticos.** El átomo emite o absorbe radiación solo cuando el electrón salta de una órbita "
            "a otra, con un único fotón cuya energía es la diferencia entre los niveles:")
        st.latex(r"h\nu=|E_i-E_f|")
        qc.seccion("Deducción de radios, velocidades y energías")
        st.markdown("La fuerza eléctrica proporciona la aceleración centrípeta (núcleo de carga Ze):")
        st.latex(r"\frac{Ze^2}{4\pi\varepsilon_0r^2}=\frac{m_ev^2}{r}")
        st.markdown("Combinando con mₑvr = nħ y despejando:")
        st.latex(r"r_n=\frac{n^2}{Z}\,a_0,\qquad a_0=\frac{4\pi\varepsilon_0\hbar^2}{m_ee^2}=0.0529\ \mathrm{nm}")
        st.latex(r"v_n=\frac{Z\alpha c}{n},\qquad \alpha=\frac{e^2}{4\pi\varepsilon_0\hbar c}\approx\frac{1}{137}")
        st.markdown("La energía total es la cinética más la potencial. Para una órbita circular la cinética es la "
                    "mitad del valor absoluto de la potencial (teorema del virial), así que:")
        st.latex(r"E_n=K+U=-K=-\frac{1}{2}m_ev_n^2=-\frac{Z^2}{n^2}\,\frac{m_ee^4}{2(4\pi\varepsilon_0)^2\hbar^2}=-\frac{Z^2}{n^2}\,13.6057\ \mathrm{eV}")
        st.markdown(
            "- El signo negativo indica un estado **ligado**: hace falta aportar energía para separar el electrón.\n"
            "- n = 1 es el **estado fundamental** (−13.6 eV, r = a₀, v ≈ c/137 ≈ 2 190 km/s).\n"
            "- Los niveles se acumulan hacia E = 0 al crecer n; por encima está el **continuo** de ionización.\n"
            "- Los radios crecen como n²: el nivel n = 10 ya mide 100 a₀ ≈ 5 nm.")
        qc.seccion("Interpretación de De Broglie (1924)")
        st.markdown("Once años después, De Broglie dio sentido a la regla de Bohr: si el electrón tiene longitud de "
                    "onda λ = h/p, las órbitas permitidas son aquellas en las que cabe un número entero de longitudes "
                    "de onda (una **onda estacionaria** que se cierra sobre sí misma):")
        st.latex(r"2\pi r=n\lambda=n\,\frac{h}{m_ev}\quad\Longleftrightarrow\quad m_evr=n\hbar")
    with sub[2]:
        qc.seccion("De los niveles a las líneas")
        st.markdown("La energía del fotón es la diferencia entre dos niveles, y la longitud de onda se obtiene de "
                    "E = hc/λ. El resultado es exactamente la fórmula de Rydberg:")
        st.latex(r"\frac{1}{\lambda}=R\,Z^2\left(\frac{1}{n_{\rm bajo}^2}-\frac{1}{n_{\rm alto}^2}\right),\qquad R_\infty=\frac{m_ee^4}{8\varepsilon_0^2h^3c}=1.0973731\times10^{7}\ \mathrm{m^{-1}}")
        st.markdown("Las líneas se agrupan en **series** según el nivel más bajo de la transición (el final en "
                    "emisión, el inicial en absorción):")
        qc.tabla_libre([
            {"Serie": "Lyman", "Nivel bajo": "1", "Primera línea": "121.6 nm", "Límite": "91.2 nm", "Región": "ultravioleta", "Descubierta": "1906"},
            {"Serie": "Balmer", "Nivel bajo": "2", "Primera línea": "656.5 nm", "Límite": "364.7 nm", "Región": "visible y UV cercano", "Descubierta": "1885"},
            {"Serie": "Paschen", "Nivel bajo": "3", "Primera línea": "1875.6 nm", "Límite": "820.6 nm", "Región": "infrarrojo cercano", "Descubierta": "1908"},
            {"Serie": "Brackett", "Nivel bajo": "4", "Primera línea": "4052 nm", "Límite": "1459 nm", "Región": "infrarrojo", "Descubierta": "1922"},
            {"Serie": "Pfund", "Nivel bajo": "5", "Primera línea": "7460 nm", "Límite": "2279 nm", "Región": "infrarrojo", "Descubierta": "1924"},
            {"Serie": "Humphreys", "Nivel bajo": "6", "Primera línea": "12 372 nm", "Límite": "3282 nm", "Región": "infrarrojo lejano", "Descubierta": "1953"},
        ], numericas=("Nivel bajo",))
        st.caption("Longitudes de onda en el vacío para el hidrógeno, con corrección de masa reducida.")
        qc.seccion("Emisión y absorción")
        st.markdown(
            "- Un gas **caliente** (o excitado por una descarga eléctrica) emite las líneas al caer los electrones a "
            "niveles inferiores: **espectro de emisión** (líneas brillantes sobre fondo oscuro).\n"
            "- Un gas **frío** iluminado con luz blanca absorbe exactamente las mismas longitudes de onda: "
            "**espectro de absorción** (líneas oscuras). Así se identifica el hidrógeno en las estrellas.\n"
            "- A temperatura ambiente casi todos los átomos están en n = 1, por eso en absorción se observa sobre "
            "todo la serie de Lyman.")
        qc.seccion("Masa reducida")
        st.markdown("Bohr supuso el núcleo inmóvil. En realidad electrón y núcleo giran alrededor del centro de masas, "
                    "lo que equivale a sustituir mₑ por la **masa reducida** μ:")
        st.latex(r"\mu=\frac{m_eM}{m_e+M},\qquad R_M=R_\infty\,\frac{\mu}{m_e}=\frac{R_\infty}{1+m_e/M}")
        st.markdown("La corrección es pequeña (0.054 % en el hidrógeno) pero medible. Urey la usó en 1931 para "
                    "descubrir el **deuterio**: sus líneas de Balmer aparecen desplazadas unos 0.18 nm respecto a las "
                    "del hidrógeno común.")
    with sub[3]:
        qc.seccion("Éxitos del modelo")
        st.markdown(
            "- **Deduce la constante de Rydberg** a partir de mₑ, e, h y c, con un acuerdo del orden de 0.05 % "
            "(exacto al incluir la masa reducida).\n"
            "- **Explica la estabilidad** del átomo (por postulado) y el carácter **discreto** del espectro.\n"
            "- **Predice el tamaño** del átomo, a₀ ≈ 0.053 nm, y la **energía de ionización**, 13.6 eV.\n"
            "- **Iones hidrogenoides.** La «serie de Pickering» observada en estrellas, que se atribuía al "
            "hidrógeno, resultó ser del He⁺ (Z = 2), como predijo Bohr.\n"
            "- **Franck y Hertz (1914)** comprobaron con electrones que chocan con vapor de mercurio que los átomos "
            "solo absorben energía en paquetes discretos (4.9 eV), confirmando los niveles de energía.\n"
            "- **Moseley (1913–1914)** usó la dependencia Z² para ordenar los elementos por su número atómico con "
            "rayos X.")
        qc.seccion("Limitaciones")
        st.markdown(
            "- **Átomos de varios electrones.** Falla ya con el helio neutro: no puede tratar la repulsión entre "
            "electrones.\n"
            "- **Estructura fina.** Con espectroscopios de alta resolución cada línea se desdobla en varias muy "
            "próximas (efectos relativistas y del espín). Sommerfeld (1916) añadió órbitas elípticas y relatividad, "
            "pero sin una base coherente.\n"
            "- **Intensidades.** No predice por qué unas líneas son más brillantes que otras, ni las reglas de "
            "selección.\n"
            "- **Efecto Zeeman anómalo** y el comportamiento en campos magnéticos.\n"
            "- **Momento angular del estado fundamental.** Bohr da L = ħ; en realidad el estado 1s tiene L = 0.\n"
            "- **Contradice el principio de incertidumbre.** Una órbita definida implica conocer a la vez la "
            "posición y la velocidad del electrón con exactitud, algo imposible (Heisenberg, 1927).\n"
            "- **Mezcla de física clásica y cuántica** sin justificación: ¿por qué el electrón no radia en una "
            "órbita permitida? El modelo lo postula, no lo explica.")
    with sub[4]:
        qc.seccion("La ecuación de Schrödinger (1926)")
        st.markdown("La mecánica cuántica sustituye las órbitas por **funciones de onda** ψ, soluciones de la "
                    "ecuación de Schrödinger con el potencial de Coulomb:")
        st.latex(r"-\frac{\hbar^2}{2\mu}\nabla^2\psi-\frac{Ze^2}{4\pi\varepsilon_0r}\,\psi=E\,\psi,\qquad \psi_{nlm}(r,\theta,\varphi)=R_{nl}(r)\,Y_l^m(\theta,\varphi)")
        st.markdown(
            "- Las energías salen **iguales** a las de Bohr: Eₙ = −Z²·13.6 eV/n². Por eso el espectro que predice "
            "Bohr es correcto (sin estructura fina).\n"
            "- Cada nivel n contiene **n² estados** distintos (l = 0…n − 1 y m = −l…l) con la misma energía "
            "(degeneración; 2n² contando el espín).\n"
            "- El momento angular es |L| = √(l(l+1)) ħ, no nħ; y puede ser cero (orbitales s).\n"
            "- |ψ|² es una **densidad de probabilidad**: dice dónde es probable encontrar al electrón al medir su "
            "posición, no por dónde pasa. Es lo que muestra la nube de la pestaña «Átomo en 3D».")
        qc.seccion("Qué queda de las órbitas de Bohr")
        st.latex(r"\langle r\rangle_{nl}=\frac{a_0}{2Z}\left[3n^2-l(l+1)\right],\qquad r_{\rm más\ probable}=\frac{n^2a_0}{Z}\ \ \text{si}\ l=n-1")
        st.markdown(
            "El radio de Bohr reaparece como la **distancia más probable** en los orbitales sin nodos radiales "
            "(1s, 2p, 3d, 4f…), los más parecidos a una «órbita circular». En el estado fundamental la distancia más "
            "probable es a₀ y la media 1.5 a₀. Para n grande la nube se concentra cerca de la órbita clásica: es el "
            "**principio de correspondencia** de Bohr, que pide recuperar la física clásica en ese límite.")
        qc.seccion("El principio de incertidumbre fija el tamaño del átomo")
        st.markdown("Si el electrón se confina en una región de tamaño r, su momento es al menos del orden de ħ/r. "
                    "La energía total es aproximadamente:")
        st.latex(r"E(r)\approx\frac{\hbar^2}{2m_er^2}-\frac{e^2}{4\pi\varepsilon_0r}\quad\xrightarrow{\ dE/dr=0\ }\quad r=a_0,\qquad E=-13.6\ \mathrm{eV}")
        st.markdown("Acercar el electrón al núcleo cuesta más energía cinética de la que se gana en energía "
                    "potencial: por eso el átomo **no colapsa**, sin necesidad de postular órbitas estables. Para el "
                    "estado 1s el producto de incertidumbres vale Δx·Δpₓ = ħ/√3 ≈ 0.577 ħ, por encima del mínimo ħ/2.")
    with sub[5]:
        qc.seccion("Postulados y resultados de Bohr")
        st.latex(r"L=m_e v r=n\hbar\qquad r_n=\frac{n^2a_0}{Z}\qquad v_n=\frac{Z\alpha c}{n}\qquad E_n=-\frac{Z^2\,R_y}{n^2},\ \ R_y=13.6057\ \mathrm{eV}")
        qc.seccion("Transiciones")
        st.latex(r"E_{\rm fotón}=|E_f-E_i|=h\nu=\frac{hc}{\lambda}\qquad \frac{1}{\lambda}=R_M\,Z^2\left|\frac{1}{n_f^2}-\frac{1}{n_i^2}\right|")
        qc.seccion("Masa reducida")
        st.latex(r"\mu=\frac{m_eM}{m_e+M},\qquad R_M=R_\infty\frac{\mu}{m_e}=\frac{R_\infty}{1+m_e/M},\qquad R_\infty=1.0973731\times10^{7}\ \mathrm{m^{-1}}")
        qc.seccion("Átomo de hidrógeno cuántico")
        st.latex(r"P(r)=r^2|R_{nl}(r)|^2,\qquad \langle r\rangle=\frac{a_0}{2Z}\left[3n^2-l(l+1)\right],\qquad \langle r^2\rangle=\frac{a_0^2n^2}{2Z^2}\left[5n^2+1-3l(l+1)\right]")
        st.latex(r"\langle p^2\rangle=\left(\frac{Z\hbar}{na_0}\right)^2,\qquad \Delta x\,\Delta p_x\big|_{l=0}=\frac{\sqrt{\langle r^2\rangle\langle p^2\rangle}}{3}\ \ge\ \frac{\hbar}{2}")
        st.latex(r"\text{nodos radiales}=n-l-1,\qquad \text{nodos angulares}=l,\qquad |L|=\sqrt{l(l+1)}\,\hbar,\qquad L_z=m\hbar")
