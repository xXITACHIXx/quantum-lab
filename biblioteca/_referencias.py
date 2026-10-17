"""biblioteca/_referencias.py — Referencias bibliográficas, históricas y de herramientas (solo fuentes verificables)."""

from __future__ import annotations

from biblioteca._modelo import Referencia as R

REFERENCIAS = (
    R("atkins", "Libro de texto", "P. Atkins, J. de Paula, J. Keeler. Physical Chemistry. Oxford University Press (varias ediciones).",
      "Cubre el curso completo con enfoque de química física: caja, oscilador, rotor, hidrógeno, espectroscopía."),
    R("mcquarrie", "Libro de texto", "D. A. McQuarrie. Quantum Chemistry. University Science Books (varias ediciones).",
      "Desarrollo matemático detallado de los modelos solubles y de los postulados."),
    R("levine", "Libro de texto", "I. N. Levine. Quantum Chemistry. Pearson (varias ediciones).",
      "Operadores, conmutadores, métodos aproximados y estructura atómica."),
    R("griffiths", "Libro de texto", "D. J. Griffiths, D. F. Schroeter. Introduction to Quantum Mechanics. Cambridge University Press (varias ediciones).",
      "Buena fuente para la interpretación de la función de onda, el túnel y la incertidumbre."),
    R("einstein1905", "Artículo original", "A. Einstein. «Über einen die Erzeugung und Verwandlung des Lichtes betreffenden heuristischen Gesichtspunkt». Annalen der Physik 17, 132 (1905).",
      "Propone el cuanto de luz y explica el efecto fotoeléctrico."),
    R("millikan1916", "Artículo original", "R. A. Millikan. «A Direct Photoelectric Determination of Planck's h». Physical Review 7, 355 (1916).",
      "Verificación experimental de la ecuación de Einstein y medida de h."),
    R("bohr1913", "Artículo original", "N. Bohr. «On the Constitution of Atoms and Molecules». Philosophical Magazine 26, 1 (1913).",
      "Modelo del átomo de hidrógeno con momento angular cuantizado."),
    R("debroglie1925", "Tesis original", "L. de Broglie. «Recherches sur la théorie des quanta». Annales de Physique 3, 22 (1925).",
      "Hipótesis de ondas de materia."),
    R("schrodinger1926", "Artículo original", "E. Schrödinger. «Quantisierung als Eigenwertproblem». Annalen der Physik 79, 361 (1926).",
      "Primera formulación de la ecuación de ondas como problema de autovalores."),
    R("heisenberg1927", "Artículo original", "W. Heisenberg. «Über den anschaulichen Inhalt der quantentheoretischen Kinematik und Mechanik». Zeitschrift für Physik 43, 172 (1927).",
      "Relación de incertidumbre."),
    R("codata", "Datos", "CODATA, valores recomendados de las constantes físicas fundamentales (NIST).",
      "Origen de las constantes (ħ, h, mₑ, e, a₀) que usa el laboratorio a través de scipy.constants.", "https://physics.nist.gov/cuu/Constants/"),
    R("phet_bound", "Simulación de referencia", "PhET Interactive Simulations, Universidad de Colorado Boulder: Quantum Bound States.",
      "Muestra pozos de distinta forma, partes real e imaginaria y densidad de probabilidad. Se adoptó la idea de ver varias representaciones de un mismo estado.",
      "https://phet.colorado.edu/en/simulations/quantum-bound-states"),
    R("phet_tunel", "Simulación de referencia", "PhET Interactive Simulations: Quantum Tunneling and Wave Packets.",
      "Contrasta onda plana y paquete, y reflexión frente a transmisión. Sirvió de modelo para los objetivos de aprendizaje explícitos.",
      "https://phet.colorado.edu/en/simulations/quantum-tunneling"),
    R("phet_foto", "Simulación de referencia", "PhET Interactive Simulations: Photoelectric Effect.",
      "Permite variar intensidad y longitud de onda y observar la corriente. Es el contexto típico de la confusión entre intensidad y energía del fotón.",
      "https://phet.colorado.edu/en/simulations/photoelectric"),
    R("quantum_composer", "Artículo", "S. Ahmed et al. «Quantum Composer: A programmable quantum visualization and simulation tool for education and research». arXiv:2006.07263 (2020).",
      "Enlaza conceptos, operaciones y visualizaciones. Inspiró el mapa de conexiones entre conceptos.", "https://arxiv.org/abs/2006.07263"),
    R("streamlit", "Documentación", "Documentación de Streamlit: widgets, estado de sesión (st.session_state) y pruebas automatizadas (AppTest).",
      "Marco de la aplicación; las nuevas herramientas usan el mismo estado de sesión y se prueban con AppTest.", "https://docs.streamlit.io"),
)

POR_ID = {r.id: r for r in REFERENCIAS}
