"""
teoria/incertidumbre.py — Teoría: Principio de incertidumbre de Heisenberg.

Contenido movido desde la pestaña «Teoría» del simulador (principio_incertidumbre.py). Se muestra en el Centro de teoría.
"""

import streamlit as st

import quantum_lab_comun as qc


def mostrar() -> None:
    sub = st.tabs(["El principio", "Por qué ocurre", "Consecuencias", "Malentendidos", "Resumen de ecuaciones"])
    with sub[0]:
        qc.seccion("Heisenberg, 1927")
        st.markdown(
            "En 1927 Werner Heisenberg publicó que en la mecánica cuántica la posición y el momento de una partícula "
            "no pueden tener a la vez valores precisos. Lo ilustró con un «microscopio de rayos gamma»: para ver dónde "
            "está un electrón con precisión Δx hay que iluminarlo con luz de longitud de onda corta, λ ≲ Δx; pero un "
            "fotón así tiene un momento grande, h/λ, y al rebotar en el electrón le da un empujón imprevisible del "
            "orden de h/Δx.")
        st.markdown("Ese mismo año Earle Kennard demostró la forma precisa, con Δ las desviaciones típicas de las "
                    "distribuciones de probabilidad:")
        st.latex(r"\Delta x\,\Delta p\ \ge\ \frac{\hbar}{2},\qquad \Delta x=\sqrt{\langle x^2\rangle-\langle x\rangle^2},\quad \Delta p=\sqrt{\langle p^2\rangle-\langle p\rangle^2}")
        st.markdown("En 1929 Howard Robertson la generalizó a cualquier par de magnitudes A y B cuyos operadores no "
                    "conmutan:")
        st.latex(r"\Delta A\,\Delta B\ \ge\ \frac{1}{2}\left|\langle[\hat A,\hat B]\rangle\right|,\qquad [\hat x,\hat p]=i\hbar\ \Rightarrow\ \Delta x\,\Delta p\ge\frac{\hbar}{2}")
        st.markdown("Las componentes de distintas direcciones sí conmutan: se pueden conocer a la vez x y p_y, por "
                    "ejemplo. La restricción es para cada par conjugado (x con pₓ, y con p_y, z con p_z).")
    with sub[1]:
        qc.seccion("Es una propiedad de las ondas")
        st.markdown(
            "Una partícula cuántica se describe por una onda. Con longitud de onda bien definida (un único momento, "
            "p = h/λ) la onda se extiende por todo el espacio: no está localizada. Para fabricar un pulso localizado hay "
            "que superponer muchas ondas de longitudes distintas que interfieran constructivamente en una región y se "
            "anulen fuera. Cuanto más corto el pulso, más variedad de longitudes de onda (de momentos) hace falta.")
        st.latex(r"\psi(x)=\frac{1}{\sqrt{2\pi\hbar}}\int\varphi(p)\,e^{ipx/\hbar}\,dp\qquad\Longleftrightarrow\qquad\varphi(p)=\frac{1}{\sqrt{2\pi\hbar}}\int\psi(x)\,e^{-ipx/\hbar}\,dx")
        st.markdown(
            "Lo mismo ocurre con el sonido: una nota muy corta no tiene un tono definido (Δt·Δf ≳ 1/4π). La "
            "aportación de la física cuántica es identificar el momento con la frecuencia espacial, p = ħk; la "
            "desigualdad matemática Δx·Δk ≥ ½ se convierte así en una ley física.")
        qc.seccion("El paquete de mínima incertidumbre")
        st.markdown("La igualdad Δx·Δp = ħ/2 solo se alcanza con un gaussiano sin chirp. Cualquier otra forma, o un "
                    "gaussiano con fase cuadrática, tiene un producto mayor:")
        qc.tabla_libre([
            {"Paquete": "Gaussiano", "ψ(x)": "e^{−x²/4σ²}", "Δx·Δp": "ħ/2 = 0.5 ħ"},
            {"Paquete": "Secante hiperbólica", "ψ(x)": "sech(x/a)", "Δx·Δp": "πħ/6 ≈ 0.524 ħ"},
            {"Paquete": "Triangular", "ψ(x)": "1 − |x|/a", "Δx·Δp": "√(3/10) ħ ≈ 0.548 ħ"},
            {"Paquete": "Gaussiano con chirp", "ψ(x)": "e^{−(1−iβ)x²/4σ²}", "Δx·Δp": "½√(1+β²) ħ"},
            {"Paquete": "Rectangular", "ψ(x)": "1 si |x| < a", "Δx·Δp": "infinito (los bordes abruptos necesitan momentos arbitrariamente grandes)"},
        ])
    with sub[2]:
        qc.seccion("El tamaño y la estabilidad de los átomos")
        st.markdown("Confinar un electrón en una región de tamaño r le da un momento de al menos ~ħ/r, y una energía "
                    "cinética ~ħ²/2mr². Minimizando la energía total frente a la atracción del núcleo resulta el radio "
                    "de Bohr y la energía del hidrógeno (ver el simulador 05):")
        st.latex(r"E(r)\approx\frac{\hbar^2}{2m_er^2}-\frac{e^2}{4\pi\varepsilon_0r}\ \Rightarrow\ r_{\min}=a_0=0.053\ \mathrm{nm},\quad E_{\min}=-13.6\ \mathrm{eV}")
        qc.seccion("Energía de punto cero")
        st.markdown("Una partícula ligada nunca puede estar en reposo en el fondo del pozo: eso supondría Δx y Δp nulos. "
                    "Por eso el estado fundamental del oscilador armónico tiene energía ħω/2 (simulador 02) y la partícula "
                    "en una caja, π²ħ²/2ma² (simulador 01). El helio sigue líquido a presión atmosférica incluso cerca del "
                    "cero absoluto por esta energía.")
        qc.seccion("Escalas nucleares")
        st.markdown("Un protón confinado en un núcleo (Δx ≈ 1 fm) tiene energías cinéticas de varios MeV, un millón de "
                    "veces las energías químicas: de ahí la enorme energía de las reacciones nucleares.")
        qc.seccion("Energía y tiempo")
        st.latex(r"\Delta E\,\Delta t\ \gtrsim\ \frac{\hbar}{2}")
        st.markdown("No es exactamente igual que la de posición y momento (el tiempo no es un operador), pero tiene un "
                    "sentido preciso: un estado que dura un tiempo τ tiene una energía indefinida en ~ħ/τ. Por eso las "
                    "líneas espectrales de los átomos tienen una anchura natural, y las partículas muy inestables, una "
                    "masa «borrosa».")
        qc.seccion("Ensanchamiento de los paquetes")
        st.markdown("Una partícula libre con Δp tiene una dispersión de velocidades Δv = Δp/m; con el tiempo su posición "
                    "se vuelve cada vez más incierta. Para objetos macroscópicos el tiempo necesario es astronómico.")
    with sub[3]:
        qc.seccion("Lo que el principio NO dice")
        st.markdown(
            "- **No es un problema de los instrumentos.** Ningún aparato, por perfecto que sea, puede preparar un estado "
            "con Δx·Δp < ħ/2: esos estados no existen.\n"
            "- **No dice que la partícula tenga una posición y un momento exactos que desconocemos.** Antes de medir, "
            "esas magnitudes no tienen valores definidos simultáneos (los experimentos sobre desigualdades de Bell "
            "descartan las teorías «locales» de valores ocultos).\n"
            "- **No impide medir con precisión una sola magnitud.** Se puede medir x con toda la precisión que se "
            "quiera; lo que ocurre es que entonces p queda muy indeterminado.\n"
            "- **No se limita al «empujón» de la medida.** El microscopio de Heisenberg es una buena ilustración, pero "
            "la desigualdad de Kennard trata del estado en sí, haya o no medida.\n"
            "- **No es algo exclusivo del mundo microscópico.** Se aplica a todo; simplemente, para masas grandes, ħ "
            "es tan pequeña que el efecto no se puede detectar.")
    with sub[4]:
        qc.seccion("Relaciones de incertidumbre")
        st.latex(r"\Delta x\,\Delta p_x\ge\frac{\hbar}{2}\qquad\Delta A\,\Delta B\ge\frac12\left|\langle[\hat A,\hat B]\rangle\right|\qquad\Delta E\,\Delta t\gtrsim\frac{\hbar}{2}")
        qc.seccion("Paquetes de ondas")
        st.latex(r"\psi(x)\propto e^{-(1-i\beta)x^2/4\sigma^2}\,e^{ik_0x}\quad\Rightarrow\quad\Delta x=\sigma,\quad\Delta p=\frac{\hbar\sqrt{1+\beta^2}}{2\sigma},\quad\langle p\rangle=\hbar k_0")
        qc.seccion("Evolución libre")
        st.latex(r"\varphi(p,t)=\varphi(p,0)\,e^{-ip^2t/2m\hbar}\qquad\sigma(t)=\sigma_0\sqrt{1+2\beta s+(1+\beta^2)s^2},\quad s=\frac{t}{\tau},\quad\tau=\frac{2m\sigma_0^2}{\hbar}")
        qc.seccion("Rendija")
        st.latex(r"\frac{I(\theta)}{I_0}=\left[\frac{\sin(\pi a\sin\theta/\lambda)}{\pi a\sin\theta/\lambda}\right]^2,\qquad \sin\theta_1=\frac{\lambda}{a},\qquad \Delta y\,\Delta p_y\approx a\cdot\frac{h}{a}=h")
        qc.seccion("Ondas de materia")
        st.latex(r"\lambda=\frac{h}{p}=\frac{h}{\sqrt{2mE}}\qquad(\text{electrón: }\lambda\,[\mathrm{nm}]\approx\frac{1.226}{\sqrt{E\,[\mathrm{eV}]}})")
