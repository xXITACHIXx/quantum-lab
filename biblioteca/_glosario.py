"""biblioteca/_glosario.py — Glosario de mecánica cuántica del curso (definiciones breves, con sus relaciones)."""

from __future__ import annotations

from biblioteca._modelo import Termino as T

TERMINOS = (
    T("funcion_onda", "Función de onda",
      "Función ψ(x, t) (complejo en general) que contiene toda la información que la teoría permite conocer del estado de un sistema. "
      "No es observable por sí sola: lo medible sale de ella mediante operadores y de su módulo al cuadrado.",
      r"\Psi(x,t)", ("amplitud", "densidad_prob", "normalizacion", "superposicion"), "postulados", "caja",
      "ψ puede ser negativa o compleja; no es una probabilidad."),
    T("amplitud", "Amplitud de probabilidad",
      "Valor (complejo) de la función de onda en un punto o el coeficiente cₙ de un estado en una superposición. La probabilidad se obtiene "
      "tomando el módulo al cuadrado; las amplitudes, no las probabilidades, son las que se suman e interfieren.",
      r"P = |c|^2", ("funcion_onda", "densidad_prob", "interferencia", "fase"), "postulados", "",
      "Amplitud y probabilidad no son lo mismo: una amplitud puede ser negativa o compleja, una probabilidad nunca."),
    T("densidad_prob", "Densidad de probabilidad",
      "Magnitud |ψ(x)|² (probabilidad por unidad de longitud en 1D). La probabilidad de hallar la partícula en un intervalo es la integral "
      "de la densidad sobre ese intervalo.",
      r"P(a\le x\le b)=\int_a^b |\psi(x)|^2\,dx", ("funcion_onda", "normalizacion", "nodo"), "postulados", "caja",
      "Su valor en un punto no es una probabilidad (tiene unidades de 1/longitud); sí lo es su integral."),
    T("normalizacion", "Normalización",
      "Condición de que la probabilidad total valga 1. Una función de onda se multiplica por una constante para cumplirla; en una "
      "superposición equivale a Σ|cₙ|² = 1.",
      r"\int |\psi|^2\,dx = 1,\qquad \sum_n |c_n|^2 = 1", ("funcion_onda", "densidad_prob", "superposicion"), "operadores", "caja"),
    T("operador", "Operador",
      "Regla matemática que transforma una función en otra y que representa una magnitud física. Ejemplos: posición x̂ = x, momento "
      "p̂ = −iħ d/dx, energía Ĥ.",
      r"\hat p=-i\hbar\,\frac{d}{dx}", ("autovalor", "hamiltoniano", "conmutador", "valor_esperado"), "operadores"),
    T("autovalor", "Autofunción y autovalor",
      "Si al aplicar un operador a una función se obtiene la misma función multiplicada por una constante, la función es una autofunción "
      "y la constante, su autovalor. Los autovalores son los únicos resultados posibles de medir esa magnitud.",
      r"\hat A\,\psi_a = a\,\psi_a", ("operador", "hamiltoniano", "cuantizacion"), "operadores"),
    T("valor_esperado", "Valor esperado",
      "Promedio de los resultados de medir una magnitud sobre muchas copias idénticas del sistema. No es el resultado de una medida "
      "individual ni tiene por qué ser un valor posible.",
      r"\langle A\rangle=\int \psi^*\hat A\psi\,dx", ("operador", "funcion_onda", "superposicion"), "postulados"),
    T("hamiltoniano", "Hamiltoniano",
      "Operador de la energía total: energía cinética más energía potencial. Sus autovalores son las energías permitidas.",
      r"\hat H=-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}+V(x)", ("schrodinger_est", "operador", "estado_estacionario"), "schrodinger"),
    T("schrodinger_est", "Ecuación de Schrödinger independiente del tiempo",
      "Ecuación de autovalores del hamiltoniano. Sus soluciones aceptables (normalizables y que cumplen las condiciones de frontera) "
      "existen solo para ciertas energías: de ahí sale la cuantización.",
      r"\hat H\psi = E\psi", ("hamiltoniano", "cuantizacion", "estado_estacionario"), "schrodinger"),
    T("schrodinger_t", "Ecuación de Schrödinger dependiente del tiempo",
      "Ecuación que gobierna la evolución del estado. Para un estado de energía definida Eₙ, la dependencia temporal es solo una fase "
      "global e^{−iEₙt/ħ}.",
      r"i\hbar\frac{\partial\Psi}{\partial t}=\hat H\Psi", ("hamiltoniano", "estado_estacionario", "fase"), "schrodinger"),
    T("estado_estacionario", "Estado estacionario",
      "Estado de energía definida. Su densidad de probabilidad no cambia con el tiempo, aunque la función de onda compleja sí gira en fase.",
      r"\Psi_n(x,t)=\psi_n(x)\,e^{-iE_nt/\hbar}", ("schrodinger_est", "fase", "superposicion"), "schrodinger", "caja",
      "«Estacionario» no significa que la partícula esté quieta: su momento no es cero."),
    T("superposicion", "Superposición",
      "Combinación lineal de estados. Si el sistema está en Σ cₙψₙ, medir la energía da Eₙ con probabilidad |cₙ|², y la densidad total "
      "incluye términos de interferencia entre los estados.",
      r"\Psi=\sum_n c_n\,\psi_n\,e^{-iE_nt/\hbar}", ("interferencia", "amplitud", "fase", "normalizacion"), "postulados", "caja",
      "No es una mezcla estadística de «a veces en un estado, a veces en otro»: las amplitudes interfieren."),
    T("interferencia", "Interferencia",
      "Aparece al sumar amplitudes (no probabilidades). En una superposición de dos estados, la densidad contiene un término cruzado que "
      "oscila con la frecuencia (E₂ − E₁)/ħ.",
      r"\rho=|c_1\psi_1|^2+|c_2\psi_2|^2+2\,\mathrm{Re}(c_1^*c_2\,\psi_1\psi_2\,e^{-i\Delta E t/\hbar})", ("superposicion", "amplitud", "fase"),
      "postulados", "caja"),
    T("fase", "Fase (global y relativa)",
      "Ángulo φ del número complejo e^{iφ}. Una fase global (común a todo el estado) no cambia ninguna probabilidad; una fase relativa "
      "entre los términos de una superposición sí cambia la interferencia.",
      r"c_n=|c_n|\,e^{i\varphi_n}", ("amplitud", "interferencia", "estado_estacionario"), "ondas", "caja"),
    T("ortogonalidad", "Ortogonalidad",
      "Las autofunciones de un operador hermítico con autovalores distintos son ortogonales: su integral de solapamiento vale cero. "
      "Junto con la normalización forman un conjunto ortonormal.",
      r"\int\psi_m^*\psi_n\,dx=\delta_{mn}", ("autovalor", "normalizacion", "superposicion"), "operadores"),
    T("conmutador", "Conmutador",
      "Diferencia [Â, B̂] = ÂB̂ − B̂Â. Si es cero, ambas magnitudes pueden tener valores definidos a la vez; si no, existe una relación de "
      "incertidumbre entre ellas.",
      r"[\hat x,\hat p]=i\hbar", ("operador", "incertidumbre"), "conmutadores", "incertidumbre"),
    T("incertidumbre", "Principio de incertidumbre",
      "Límite inferior del producto de las dispersiones de dos magnitudes que no conmutan. Es una propiedad de los estados cuánticos, no una "
      "limitación del instrumento de medida.",
      r"\Delta x\,\Delta p\ge \frac{\hbar}{2}", ("conmutador", "paquete_ondas", "energia_cero"), "conmutadores", "incertidumbre",
      "No habla del error del aparato: aun con medidas ideales, Δx y Δp no pueden ser ambas arbitrariamente pequeñas."),
    T("paquete_ondas", "Paquete de ondas",
      "Superposición de ondas planas que localiza la partícula en una región. Cuanto más localizado en x, más ancho en p. El gaussiano "
      "alcanza el mínimo Δx·Δp = ħ/2.",
      r"\Delta x\,\Delta p=\frac{\hbar}{2}\ \text{(gaussiano)}", ("incertidumbre", "superposicion"), "conmutadores", "incertidumbre"),
    T("de_broglie", "Longitud de onda de De Broglie",
      "Longitud de onda asociada a una partícula de momento p. Solo es apreciable cuando es comparable con las dimensiones del sistema.",
      r"\lambda=\frac{h}{p}", ("dualidad", "cuantizacion"), "de_broglie", "caja"),
    T("dualidad", "Dualidad onda-partícula",
      "La luz y la materia muestran comportamiento ondulatorio (interferencia, difracción) y corpuscular (detección en puntos, "
      "intercambio de energía en cuantos). Lo que se observa depende del experimento.",
      "", ("de_broglie", "foton", "interferencia"), "de_broglie"),
    T("foton", "Fotón",
      "Cuanto de energía de la radiación electromagnética. Un fotón de frecuencia ν tiene energía hν; la intensidad de un haz depende del "
      "número de fotones por segundo, no de la energía de cada uno.",
      r"E_\gamma=h\nu=\frac{hc}{\lambda}", ("intensidad", "funcion_trabajo", "dualidad"), "fotoelectrico", "fotoelectrico",
      "Aumentar la intensidad no aumenta la energía de cada fotón; aumenta cuántos llegan."),
    T("intensidad", "Intensidad de la luz",
      "Potencia por unidad de área. Para luz monocromática es proporcional al número de fotones por segundo; para una frecuencia fija, "
      "más intensidad significa más fotones, no fotones más energéticos.",
      r"I\propto \dot N_\gamma\,h\nu", ("foton", "corriente_fotoelectrica"), "fotoelectrico", "fotoelectrico"),
    T("funcion_trabajo", "Función de trabajo",
      "Energía mínima que hay que entregar a un electrón para extraerlo de la superficie de un metal. Depende del material y de la superficie.",
      r"\Phi", ("frecuencia_umbral", "foton", "potencial_frenado"), "fotoelectrico", "fotoelectrico"),
    T("frecuencia_umbral", "Frecuencia umbral",
      "Frecuencia mínima de la luz para que haya emisión de electrones. Por debajo de ella no hay fotoelectrones, por intensa que sea la luz.",
      r"\nu_0=\frac{\Phi}{h}", ("funcion_trabajo", "foton"), "fotoelectrico", "fotoelectrico",
      "Con luz por debajo del umbral, subir la intensidad no produce emisión."),
    T("potencial_frenado", "Potencial de frenado",
      "Diferencia de potencial que detiene incluso a los fotoelectrones más rápidos. Mide su energía cinética máxima: eV₀ = K_máx.",
      r"eV_0=K_{\max}=h\nu-\Phi", ("funcion_trabajo", "corriente_fotoelectrica"), "fotoelectrico", "fotoelectrico"),
    T("corriente_fotoelectrica", "Corriente fotoeléctrica",
      "Carga por segundo de los electrones emitidos. Con frecuencia fija y sobre el umbral, es proporcional a la intensidad; la energía "
      "máxima de los electrones no depende de ella.",
      r"I_e\propto I_{\text{luz}}", ("intensidad", "potencial_frenado"), "fotoelectrico", "fotoelectrico"),
    T("cuantizacion", "Cuantización de la energía",
      "Solo ciertos valores de la energía son posibles en un sistema ligado. Surge de exigir que la función de onda sea normalizable y "
      "cumpla las condiciones de frontera, no de un postulado aparte.",
      r"E_n,\ n=1,2,\dots", ("schrodinger_est", "numero_cuantico", "energia_cero"), "schrodinger"),
    T("numero_cuantico", "Número cuántico",
      "Entero (o semientero) que identifica un estado permitido y determina el valor de una magnitud: n para la energía, l y mₗ para el "
      "momento angular, s y mₛ para el espín.",
      r"n,\ l,\ m_l,\ m_s", ("cuantizacion", "orbital"), "hidrogeno"),
    T("energia_cero", "Energía de punto cero",
      "Energía mínima de un sistema ligado, siempre mayor que el mínimo del potencial: confinar una partícula la obliga a tener momento "
      "no nulo (incertidumbre).",
      r"E_1^{\text{caja}}=\frac{\pi^2\hbar^2}{2ma^2},\qquad E_0^{\text{osc}}=\frac{\hbar\omega}{2}", ("incertidumbre", "cuantizacion"),
      "caja", "oscilador", "El estado fundamental no tiene energía cero."),
    T("nodo", "Nodo",
      "Punto donde la función de onda se anula y, por tanto, la densidad de probabilidad es cero. La partícula puede estar a ambos lados; no "
      "es una barrera.",
      r"\psi(x_0)=0", ("densidad_prob", "funcion_onda"), "caja", "caja",
      "Cero probabilidad en un punto no impide pasar de un lado al otro: la onda describe una distribución, no una trayectoria."),
    T("pozo_infinito", "Partícula en una caja",
      "Modelo de una partícula confinada entre paredes impenetrables (V = ∞ fuera). Las funciones de onda son senoidales y las energías "
      "crecen como n².",
      r"\psi_n=\sqrt{\tfrac2a}\sin\tfrac{n\pi x}{a},\quad E_n=\tfrac{n^2\pi^2\hbar^2}{2ma^2}", ("cuantizacion", "nodo", "energia_cero"),
      "caja", "caja"),
    T("oscilador", "Oscilador armónico",
      "Partícula bajo un potencial cuadrático V = ½mω²x². Sus niveles son equiespaciados y las funciones de onda, polinomios de Hermite por "
      "una gaussiana.",
      r"E_n=\hbar\omega\left(n+\tfrac12\right)", ("hermite", "energia_cero", "punto_retorno"), "oscilador", "oscilador"),
    T("hermite", "Polinomios de Hermite",
      "Familia de polinomios Hₙ(ξ) que, multiplicados por e^{−ξ²/2}, dan las autofunciones del oscilador armónico. Hₙ tiene n ceros, "
      "igual que el número de nodos de ψₙ.",
      r"\psi_n\propto H_n(\xi)\,e^{-\xi^2/2},\ \ \xi=\frac{x}{x_0}", ("oscilador", "nodo"), "oscilador", "oscilador"),
    T("punto_retorno", "Punto de retorno clásico y zona prohibida",
      "Posición donde la energía total iguala a la potencial (T = 0). Una partícula clásica no pasa de ahí; la función de onda cuántica "
      "decae dentro de la zona prohibida pero no se anula.",
      r"x_{\text{ret}}=\pm\sqrt{\frac{2E}{m\omega^2}}=\pm\sqrt{2n+1}\,x_0", ("oscilador", "tunel"), "oscilador", "oscilador"),
    T("tunel", "Efecto túnel",
      "Probabilidad no nula de hallar la partícula donde la energía potencial supera su energía total. Se debe a que la función de onda "
      "penetra en la barrera con un decaimiento exponencial.",
      r"\psi\sim e^{-\kappa x},\quad \kappa=\frac{\sqrt{2m(V-E)}}{\hbar}", ("punto_retorno", "funcion_onda"), "libre_pared", "oscilador"),
    T("virial", "Teorema del virial",
      "Para un potencial V ∝ xᵏ, los promedios de las energías cinética y potencial guardan una proporción fija. En el oscilador armónico "
      "(k = 2), ⟨T⟩ = ⟨V⟩ = E/2.",
      r"2\langle T\rangle=k\,\langle V\rangle", ("oscilador", "valor_esperado"), "oscilador", "oscilador"),
    T("momento_angular", "Momento angular",
      "Magnitud de la rotación. Sus valores están cuantizados: L² = ħ²l(l+1) y Lz = mₗħ con mₗ = −l,…,l. Lx, Ly y Lz no pueden tener valores "
      "definidos a la vez.",
      r"L^2=\hbar^2l(l+1),\quad L_z=m_l\hbar", ("armonicos", "numero_cuantico", "conmutador"), "esfera", "esfera"),
    T("armonicos", "Armónicos esféricos",
      "Funciones Yₗᵐ(θ, φ) que son autofunciones de L² y Lz. Describen la parte angular de los orbitales y tienen l nodos angulares.",
      r"\hat L^2Y_l^m=\hbar^2l(l+1)Y_l^m", ("momento_angular", "orbital"), "esfera", "esfera"),
    T("orbital", "Orbital",
      "Función de onda de un electrón en un átomo (ψₙₗₘ). Su módulo al cuadrado da la densidad de probabilidad; no es una trayectoria "
      "ni una órbita.",
      r"\psi_{nlm}=R_{nl}(r)\,Y_l^m(\theta,\varphi)", ("armonicos", "densidad_radial", "numero_cuantico"), "hidrogeno", "bohr",
      "Un orbital no es una órbita: el electrón no recorre una trayectoria definida."),
    T("densidad_radial", "Densidad de probabilidad radial",
      "Probabilidad por unidad de radio de hallar el electrón a una distancia r del núcleo: P(r) = r²R(r)². Su máximo no coincide con el "
      "máximo de |ψ|² en general.",
      r"P(r)=r^2\,[R_{nl}(r)]^2", ("orbital",), "hidrogeno", "bohr"),
    T("radio_bohr", "Radio de Bohr",
      "Radio de la primera órbita del modelo de Bohr para el hidrógeno; unidad atómica de longitud (a₀ ≈ 0.0529 nm). En la teoría cuántica "
      "es el radio más probable del 1s.",
      r"a_0=\frac{4\pi\varepsilon_0\hbar^2}{m_ee^2}", ("modelo_bohr", "unidades_atomicas"), "bohr", "bohr"),
    T("modelo_bohr", "Modelo de Bohr",
      "Modelo semiclásico del hidrógeno con órbitas circulares y momento angular cuantizado L = nħ. Reproduce los niveles de energía "
      "del hidrógeno, pero no describe átomos con varios electrones ni da una imagen correcta del electrón.",
      r"E_n=-\frac{13.6\ \text{eV}}{n^2}", ("radio_bohr", "serie_espectral", "orbital"), "bohr", "bohr",
      "Las órbitas de Bohr no existen como trayectorias; sí son útiles para los niveles de energía del H."),
    T("serie_espectral", "Serie espectral",
      "Conjunto de transiciones que terminan en el mismo nivel inferior: Lyman (n=1, ultravioleta), Balmer (n=2, visible), Paschen (n=3, "
      "infrarrojo). Se calcula con la fórmula de Rydberg.",
      r"\frac1\lambda=R_\infty Z^2\left(\frac1{n_f^2}-\frac1{n_i^2}\right)", ("modelo_bohr", "foton", "masa_reducida"), "bohr", "bohr"),
    T("masa_reducida", "Masa reducida",
      "Masa efectiva μ = m₁m₂/(m₁+m₂) de un sistema de dos cuerpos. Corrige la constante de Rydberg por el movimiento del núcleo; la "
      "diferencia relativa en el hidrógeno es de unos 5×10⁻⁴.",
      r"\mu=\frac{m_1m_2}{m_1+m_2}", ("serie_espectral", "modelo_bohr"), "bohr", "bohr"),
    T("espin", "Espín",
      "Momento angular intrínseco de las partículas, sin análogo clásico. El electrón tiene espín ½, con dos proyecciones mₛ = ±½. Los "
      "fermiones requieren funciones de onda antisimétricas.",
      r"s=\tfrac12,\quad m_s=\pm\tfrac12", ("momento_angular", "numero_cuantico"), "espin"),
    T("degeneracion", "Degeneración",
      "Número de estados distintos que comparten la misma energía. En el hidrógeno (sin estructura fina), la energía depende solo de n y "
      "hay n² orbitales por nivel (2n² contando el espín).",
      r"g_n=n^2", ("numero_cuantico", "orbital"), "hidrogeno", "bohr"),
    T("unidades_atomicas", "Unidades atómicas",
      "Sistema de unidades en el que ħ = mₑ = e = 4πε₀ = 1. La unidad de longitud es el radio de Bohr y la de energía, el hartree "
      "(≈ 27.211 eV).",
      r"E_h\approx 27.211\ \text{eV}", ("radio_bohr",), "bohr"),
    T("medida", "Medida y colapso",
      "Al medir una magnitud solo se obtiene uno de sus autovalores, con probabilidad |cₙ|². Después de la medida el estado queda en la "
      "autofunción correspondiente (según el postulado de proyección).",
      r"P(a_n)=|c_n|^2", ("autovalor", "amplitud", "valor_esperado"), "postulados"),
)

POR_ID = {t.id: t for t in TERMINOS}


def buscar(texto: str) -> list:
    """Términos cuyo nombre, definición o ecuación contienen el texto (sin distinguir mayúsculas ni tildes)."""
    import unicodedata

    def base(s: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")

    q = base((texto or "").strip())
    if not q:
        return list(TERMINOS)
    return [t for t in TERMINOS if q in base(f"{t.nombre} {t.definicion} {t.ecuacion} {t.cuidado}")]
