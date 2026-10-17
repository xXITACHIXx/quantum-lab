"""
tutor/_errores.py — Catálogo de confusiones conceptuales frecuentes y detector basado en reglas.

El detector NO entiende el lenguaje: busca patrones frecuentes en oraciones y descarta las oraciones con negación, salvo que el error
se exprese con «no». Por eso solo detecta formulaciones típicas; el tutor lo dice abiertamente. Cada confusión lleva frases de ejemplo
(que deben detectarse) y frases correctas parecidas (que no deben detectarse), que las pruebas comprueban.
"""

from __future__ import annotations

import re
import unicodedata

from tutor._modelo import Concepcion as C

_GRIEGAS = {"ψ": "psi", "Ψ": "psi", "ρ": "rho", "ħ": "hbar", "ν": "nu", "λ": "lambda", "Φ": "phi", "φ": "phi", "²": "2", "₁": "1", "₂": "2"}
_NEGACION = re.compile(r"\b(no|nunca|tampoco|jamas|ni|sin)\b")
_NO_NEGATIVO = re.compile(r"\bno (sabemos|se sabe|sabe|conocemos|se conoce|conoce)\b")   # «no sabemos cuál» no niega la oración


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, griegas transcritas y espacios simples."""
    for k, v in _GRIEGAS.items():
        texto = texto.replace(k, v)
    texto = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    texto = texto.replace("|", " ")
    return re.sub(r"\s+", " ", texto).strip()


def _oraciones(texto: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.;!?\n]+", normalizar(texto)) if s.strip()]


CONCEPCIONES = (
    C("amplitud_prob", "Amplitud y probabilidad",
      "La función de onda (o su amplitud) es la probabilidad.",
      "Si ψ puede ser negativa o compleja, ¿puede ser una probabilidad? ¿Qué cantidad sí es siempre positiva?",
      "La función de onda es una amplitud de probabilidad, con signo o fase. La probabilidad sale de su módulo al cuadrado: |ψ|² es la densidad de "
      "probabilidad, y la probabilidad de un intervalo es la integral de |ψ|² sobre él. En una superposición, el peso de cada estado es |cₙ|², no cₙ.",
      r"P=|c|^2,\qquad P(a\le x\le b)=\int_a^b|\psi|^2dx",
      ("amplitud", "funcion_onda", "densidad_prob"), "postulados", "caja",
      reglas=((r"\b(amplitud|psi|funcion de onda)( de onda)? (es|equivale a|representa|significa|es igual a|=) (la |el )?probabilidad",),
              (r"\bprobabilidad (es|=|es igual a|se calcula como) (la |el )?(amplitud|psi|funcion de onda)\b(?! ?(al cuadrado|\^?2|cuadrado|modulo))",)),
      frases_error=("La función de onda es la probabilidad de encontrar la partícula.", "La amplitud es igual a la probabilidad.", "La probabilidad es psi."),
      frases_correctas=("La función de onda es una amplitud de probabilidad.", "La probabilidad es psi al cuadrado.", "La amplitud no es la probabilidad.")),
    C("psi_negativa", "Signo de la función de onda",
      "Si ψ es negativa en un punto, la probabilidad allí es negativa.",
      "¿Qué operación se hace con ψ antes de hablar de probabilidad? ¿Qué pasa con el signo?",
      "La probabilidad nunca es negativa. El signo de ψ (o su fase) no cambia |ψ|²; solo importa cuando se suman amplitudes, porque ahí decide si "
      "la interferencia es constructiva o destructiva.",
      r"\psi(x_0)=-0.8/\sqrt a\ \Rightarrow\ |\psi|^2=0.64/a>0",
      ("amplitud", "fase", "interferencia"), "ondas", "caja",
      reglas=((r"probabilidad.{0,25}negativ",), (r"negativ.{0,25}probabilidad",)),
      frases_error=("Si psi es negativa la probabilidad es negativa.", "Una probabilidad negativa significa que falta partícula en ese punto."),
      frases_correctas=("La probabilidad no puede ser negativa.", "La función de onda puede ser negativa, pero la probabilidad no.")),
    C("densidad_valor_punto", "Densidad de probabilidad y probabilidad",
      "El valor de |ψ|² en un punto es la probabilidad de hallar la partícula en ese punto.",
      "¿Qué unidades tiene |ψ|² en una dimensión? ¿Cuál es la probabilidad de hallarla exactamente en un único punto?",
      "|ψ|² es una densidad (probabilidad por unidad de longitud, con unidades 1/m). Solo la integral sobre un intervalo da una probabilidad. "
      "Para un punto exacto el intervalo mide cero y la probabilidad es cero; lo que se compara entre puntos es cuán probable es cada región.",
      r"P(x_0\le x\le x_0+dx)\approx|\psi(x_0)|^2\,dx",
      ("densidad_prob", "normalizacion"), "postulados", "caja",
      reglas=((r"(psi ?2|psi al cuadrado|densidad de probabilidad).{0,40}probabilidad (en|de (hallarla|encontrarla|hallar|encontrar) en) (un |el |ese )?(punto|valor de x)",),),
      frases_error=("La densidad de probabilidad es la probabilidad en un punto.", "Psi al cuadrado es la probabilidad en ese punto."),
      frases_correctas=("La densidad de probabilidad integrada da la probabilidad en un intervalo.",)),
    C("intensidad_energia_foton", "Intensidad y energía del fotón",
      "Más intensidad de luz significa fotones (o fotoelectrones) más energéticos.",
      "¿De qué depende la energía de un solo fotón? ¿Qué cambia cuando se hace la luz más intensa sin cambiar el color?",
      "La energía de cada fotón es hν y depende solo de la frecuencia. La intensidad, a frecuencia fija, mide cuántos fotones llegan por segundo. "
      "Más intensidad da más fotoelectrones por segundo (más corriente), pero cada uno sale con la misma energía cinética máxima.",
      r"E_\gamma=h\nu,\qquad I\propto \dot N_\gamma\,h\nu,\qquad K_{\max}=h\nu-\Phi",
      ("foton", "intensidad", "corriente_fotoelectrica"), "fotoelectrico", "fotoelectrico",
      reglas=((r"(intensidad|brillo).{0,15}(determina|define|aumenta|incrementa|cambia|es proporcional a|es igual a).{0,20}energia (de cada|del|de los) (foton|fotones)",),
              (r"(mas|mayor) intensidad.{0,40}(electrones|fotoelectrones).{0,25}(mas|mayor) (energia|velocidad|rapidez)",),
              (r"(aumento|aumenta|aumentas|aumentar|incremento|incrementa|subo|sube|subir) (la )?intensidad.{0,40}(electrones|fotoelectrones).{0,25}(mas|mayor) (energia|velocidad|rapidez)",),
              (r"(aumentar|aumenta|aumentas|incrementar|duplicar|duplica|duplicas) (la )?intensidad.{0,40}(aumenta|incrementa|crece|se duplica).{0,25}energia (cinetica|de los (fotones|electrones))",)),
      frases_error=("Al aumentar la intensidad aumenta la energía de cada fotón.", "Con más intensidad los electrones salen con más energía.",
                    "Si duplicas la intensidad se duplica la energía cinética máxima.", "Si aumento la intensidad, los electrones salen con más energía."),
      frases_correctas=("La intensidad no cambia la energía de cada fotón.", "Más intensidad significa más fotones por segundo.",
                        "La energía del fotón depende de la frecuencia.", "Si aumento la intensidad salen más electrones con la misma energía.")),
    C("corriente_independiente_intensidad", "Intensidad y corriente fotoeléctrica",
      "La intensidad de la luz no afecta la corriente fotoeléctrica.",
      "Si llegan más fotones por segundo y cada uno libera como mucho un electrón, ¿qué pasa con el número de electrones por segundo?",
      "Con frecuencia sobre el umbral, la corriente de saturación es proporcional a la intensidad: más fotones por segundo liberan más electrones por segundo. "
      "Lo que no depende de la intensidad es la energía cinética máxima (y el potencial de frenado).",
      r"I_e\propto I_{\text{luz}}\quad(\nu>\nu_0)",
      ("corriente_fotoelectrica", "intensidad"), "fotoelectrico", "fotoelectrico",
      reglas=((r"intensidad.{0,30}(no afecta|no cambia|no influye|no modifica|no tiene efecto).{0,25}(corriente|numero de electrones|fotoelectrones)",),),
      con_negacion=True,
      frases_error=("La intensidad no afecta la corriente fotoeléctrica.", "La intensidad no cambia el número de electrones emitidos."),
      frases_correctas=("La intensidad no afecta la energía cinética máxima.", "La corriente es proporcional a la intensidad.")),
    C("umbral_intensidad", "Frecuencia umbral",
      "Con luz de baja frecuencia pero suficiente intensidad, el metal emite electrones.",
      "¿Cuánta energía entrega un fotón al electrón? ¿Pueden sumarse varios fotones para un solo electrón en este efecto?",
      "Cada electrón absorbe un fotón completo. Si hν < Φ, ningún fotón individual puede extraerlo y la intensidad no lo compensa (solo aumenta la cantidad de "
      "fotones, todos insuficientes). El efecto exige ν ≥ ν₀ = Φ/h.",
      r"h\nu<\Phi\ \Rightarrow\ \text{sin emisión, sea cual sea } I",
      ("frecuencia_umbral", "funcion_trabajo", "foton"), "fotoelectrico", "fotoelectrico",
      reglas=((r"(baja frecuencia|bajo (el )?umbral|debajo del umbral|menor (que )?(la )?frecuencia umbral|luz roja|longitud de onda (mayor|larga)).{0,80}intensidad.{0,60}(emit|salen|arranc|liber|acumul)",),
              (r"(mucha|suficiente|alta|bastante) intensidad.{0,60}(compens|suple|basta|alcanza|acumul).{0,60}(frecuencia|umbral)",)),
      frases_error=("Con luz roja de baja frecuencia pero mucha intensidad igual se emiten electrones.", "Con suficiente intensidad se compensa la frecuencia baja."),
      frases_correctas=("A mayor intensidad se emiten más electrones.", "Por debajo del umbral la intensidad no sirve de nada.")),
    C("potencial_frenado_intensidad", "Potencial de frenado",
      "El potencial de frenado crece con la intensidad de la luz.",
      "El potencial de frenado mide la energía de los electrones más rápidos. ¿Esa energía depende de cuántos fotones llegan?",
      "El potencial de frenado cumple eV₀ = K_máx = hν − Φ, que depende de la frecuencia y del metal, no de la intensidad. La intensidad solo "
      "cambia la altura de la curva corriente–voltaje.",
      r"V_0=\frac{h\nu-\Phi}{e}",
      ("potencial_frenado", "intensidad"), "fotoelectrico", "fotoelectrico",
      reglas=((r"potencial de frenado.{0,40}(aumenta|crece|depende|sube|mayor).{0,25}intensidad",),
              (r"intensidad.{0,40}(aumenta|incrementa|cambia|determina|define).{0,25}potencial de frenado",)),
      frases_error=("El potencial de frenado aumenta con la intensidad.", "Más intensidad aumenta el potencial de frenado."),
      frases_correctas=("El potencial de frenado depende de la frecuencia.", "La intensidad no cambia el potencial de frenado.")),
    C("nodo_barrera", "Nodos de la función de onda",
      "La partícula no puede atravesar un nodo: es una barrera.",
      "¿Un nodo es un obstáculo físico o un punto donde se anula la función de onda? ¿Habla la función de onda de trayectorias?",
      "Un nodo es un punto donde ψ = 0 y, por tanto, la densidad es cero: no hay densidad de probabilidad allí. No es una pared, y la función de onda no describe "
      "una trayectoria que deba cruzar ese punto. La distribución a ambos lados está conectada en el mismo estado.",
      r"\psi(x_0)=0\ \Rightarrow\ \rho(x_0)=0",
      ("nodo", "densidad_prob", "funcion_onda"), "caja", "caja",
      reglas=((r"(no puede|no pasa|nunca pasa|imposible).{0,25}nodo",), (r"nodo.{0,40}(barrera|pared|no puede pasar|no puede cruzar)",)),
      con_negacion=True,
      frases_error=("La partícula no puede pasar por un nodo.", "El nodo es una barrera para la partícula."),
      frases_correctas=("En un nodo la densidad de probabilidad es cero.",)),
    C("estacionario_reposo", "Estado estacionario",
      "Estado estacionario significa que la partícula está quieta.",
      "¿Qué magnitud permanece constante en el tiempo en un estado estacionario: la posición de la partícula o su densidad de probabilidad?",
      "«Estacionario» se refiere a que la densidad de probabilidad no cambia con el tiempo (es un estado de energía definida; solo cambia su fase global). "
      "La partícula no está en reposo: en la caja, por ejemplo, su momento es ±nπħ/a, distinto de cero.",
      r"|\Psi_n(x,t)|^2=|\psi_n(x)|^2\ \text{(independiente de } t)",
      ("estado_estacionario", "densidad_prob", "fase"), "schrodinger", "caja",
      reglas=((r"estacionari[oa].{0,45}(reposo|quiet[oa]|no se mueve|detenid[oa]|inmovil)",), (r"(reposo|quiet[oa]|no se mueve).{0,45}estacionari",)),
      con_negacion=True,
      frases_error=("Un estado estacionario es cuando la partícula está en reposo.", "Estacionario significa que no se mueve."),
      frases_correctas=("En un estado estacionario la densidad de probabilidad no cambia con el tiempo.",)),
    C("energia_cero", "Energía de punto cero",
      "El estado fundamental tiene energía cero (la partícula puede estar en reposo).",
      "Si la partícula está confinada en una región pequeña, ¿qué dice la incertidumbre sobre su momento? ¿Puede ese momento ser cero?",
      "Confinar la partícula obliga a una dispersión de momentos y, con ella, a una energía cinética mínima no nula. En la caja E₁ = π²ħ²/(2ma²) > 0 y en el "
      "oscilador E₀ = ħω/2 > 0. Que el estado fundamental no tenga energía cero es consecuencia directa de la incertidumbre.",
      r"E_1^{\text{caja}}=\frac{\pi^2\hbar^2}{2ma^2},\qquad E_0^{\text{osc}}=\frac{\hbar\omega}{2}",
      ("energia_cero", "incertidumbre", "cuantizacion"), "caja", "oscilador",
      reglas=((r"fundamental.{0,30}(energia (es )?(cero|0|nula)|sin energia|no tiene energia)",),
              (r"puede (estar|quedarse) (en reposo|quiet[oa]).{0,25}(caja|pozo|oscilador)",)),
      con_negacion=True,
      frases_error=("El estado fundamental tiene energía cero.", "La partícula puede estar en reposo en la caja."),
      frases_correctas=("El estado fundamental tiene energía distinta de cero.",)),
    C("superposicion_mezcla", "Superposición",
      "En una superposición la partícula está en un estado u otro, pero no sabemos cuál.",
      "Si fuera solo ignorancia, ¿habría interferencia entre los estados? ¿Qué se suma en una superposición: probabilidades o amplitudes?",
      "En Ψ = c₁ψ₁ + c₂ψ₂ el sistema no está en ψ₁ o ψ₂ sin que lo sepamos: está en el estado combinado, y la densidad contiene un término de interferencia que una mezcla "
      "estadística no tiene. Solo al medir la energía se obtiene E₁ o E₂, con probabilidades |c₁|² y |c₂|².",
      r"\rho=|c_1\psi_1|^2+|c_2\psi_2|^2+\text{(interferencia)}",
      ("superposicion", "interferencia", "medida"), "postulados", "caja",
      reglas=((r"superposicion.{0,40}(a veces|unas veces|o bien|uno u otro|mezcla|estadistica|no sabemos|ignoramos)",),
              (r"(esta en|esta en uno de).{0,25}(o en|u otro|o bien).{0,25}(no sabemos|desconocemos|ignoramos)",),
              (r"(superposicion|combinacion).{0,25}(es )?(solo )?(ignorancia|desconocimiento)",)),
      frases_error=("En una superposición la partícula está en un estado u otro, pero no sabemos cuál.", "La superposición es una mezcla estadística."),
      frases_correctas=("En una superposición las amplitudes interfieren.",)),
    C("suma_probabilidades", "Interferencia",
      "En una superposición se suman las probabilidades de cada estado (no hay interferencia).",
      "Para sumar dos ondas, ¿se suman sus intensidades o sus amplitudes? ¿Qué aparece al elevar al cuadrado una suma?",
      "Se suman amplitudes: |c₁ψ₁ + c₂ψ₂|² = |c₁ψ₁|² + |c₂ψ₂|² + 2 Re(c₁*c₂ψ₁*ψ₂). El último término (interferencia) es lo que distingue una superposición "
      "coherente de una mezcla, y oscila en el tiempo con la frecuencia (E₂ − E₁)/ħ.",
      r"\rho=\tfrac12\psi_1^2+\tfrac12\psi_2^2+\psi_1\psi_2\cos\!\left(\tfrac{(E_2-E_1)t}{\hbar}\right)",
      ("interferencia", "amplitud", "superposicion"), "postulados", "caja",
      reglas=((r"(se suman|sumar).{0,20}(las )?(probabilidades|densidades).{0,40}(superposicion|estados)",),
              (r"superposicion.{0,40}(se suman|sumar|suman) (las )?(probabilidades|densidades)",),
              (r"superposicion.{0,30}(no hay|sin|no existe) interferencia",),
              (r"superposicion.{0,40}(suma|sumar|promedio) de (las )?(probabilidades|densidades)",),
              (r"(no hay|sin|no existe).{0,15}interferencia.{0,30}superposicion",)),
      con_negacion=True,
      frases_error=("En una superposición se suman las probabilidades de cada estado.", "En la superposición no hay interferencia."),
      frases_correctas=("En una superposición se suman las amplitudes.",)),
    C("valor_esperado_medido", "Valor esperado",
      "El valor esperado es lo que se obtiene al medir una vez.",
      "¿Es 2.5 eV uno de los niveles permitidos entre 1 eV y 4 eV? ¿Qué resultados individuales son posibles?",
      "Una medida individual da siempre un autovalor del operador. El valor esperado es el promedio de muchas medidas sobre copias idénticas del sistema y "
      "puede no coincidir con ninguno de los valores posibles. Con E₁ = 1 eV y E₂ = 4 eV a partes iguales, ⟨E⟩ = 2.5 eV, que nunca se mide.",
      r"\langle E\rangle=\sum_n|c_n|^2E_n",
      ("valor_esperado", "medida", "autovalor"), "postulados", "caja",
      reglas=((r"valor esperado.{0,15}\b(es|sera)\b.{0,12}(el )?(resultado|valor) (de|que se obtiene al|al) (una )?(medir|medida|medicion)",),
              (r"(al medir|medimos|se mide).{0,25}(se obtiene|obtenemos|da|resulta).{0,25}(el )?(valor esperado)",)),
      frases_error=("El valor esperado es el resultado de una medida.", "Al medir se obtiene el valor esperado."),
      frases_correctas=("El valor esperado es el promedio de muchas medidas.",)),
    C("fase_ignorada", "Fase relativa",
      "La fase (o el signo) entre los términos de una superposición no importa.",
      "Compara (ψ₁ + ψ₂) y (ψ₁ − ψ₂): ¿tienen igual |c|² para cada estado? ¿Cambia su densidad en algún punto?",
      "La fase global de todo el estado no cambia ninguna probabilidad, pero la fase relativa entre los términos sí cambia la interferencia. "
      "(ψ₁ + ψ₂)/√2 y (ψ₁ − ψ₂)/√2 dan las mismas probabilidades de energía, pero densidades distintas: el término 2ψ₁ψ₂ tiene signo opuesto.",
      r"|\psi_1\pm\psi_2|^2=\psi_1^2+\psi_2^2\pm2\psi_1\psi_2",
      ("fase", "interferencia", "superposicion"), "ondas", "caja",
      reglas=((r"^(?!.*global).*\b(fase|signo)\b.{0,25}(no importa|no afecta|no influye|da igual|es irrelevante)",),),
      con_negacion=True, excluye=r"global",
      frases_error=("La fase relativa no importa.", "El signo entre los dos estados da igual."),
      frases_correctas=("La fase global no importa.", "La fase relativa cambia la interferencia.")),
    C("fase_global_cambia", "Fase global",
      "Multiplicar toda la función de onda por e^{iφ} cambia las probabilidades.",
      "¿Cuánto vale el módulo de e^{iφ}? ¿Qué le pasa a |e^{iφ}ψ|²?",
      "Si el estado completo se multiplica por e^{iφ}, |e^{iφ}ψ|² = |ψ|² porque |e^{iφ}| = 1. Una fase global no es observable. "
      "Es distinta de la fase relativa entre términos de una superposición, que sí lo es.",
      r"|e^{i\varphi}\psi|^2=|\psi|^2",
      ("fase", "amplitud"), "ondas", "caja",
      reglas=((r"fase global.{0,40}(cambia|modifica|altera|afecta).{0,25}(probabilidad|densidad|resultado)",),
              (r"multiplicar.{0,25}e ?\^? ?i.{0,40}(cambia|modifica|altera).{0,20}probabilidad",)),
      frases_error=("La fase global cambia las probabilidades.", "Multiplicar por e^i phi modifica la probabilidad."),
      frases_correctas=("La fase global no cambia las probabilidades.",)),
    C("incertidumbre_instrumento", "Principio de incertidumbre",
      "La incertidumbre es un error de los instrumentos o una perturbación al medir.",
      "Si se usaran instrumentos perfectos, ¿desaparecería la cota ΔxΔp ≥ ħ/2? ¿De qué propiedad de los operadores x y p sale?",
      "La relación de incertidumbre es una propiedad del estado cuántico: x̂ y p̂ no conmutan ([x̂, p̂] = iħ), así que no existe ningún estado con ambas dispersiones "
      "arbitrariamente pequeñas. Se cumple aun con medidas ideales.",
      r"[\hat x,\hat p]=i\hbar\ \Rightarrow\ \Delta x\,\Delta p\ge\frac\hbar2",
      ("incertidumbre", "conmutador"), "incertidumbre", "incertidumbre",
      reglas=((r"incertidumbre.{0,50}(se debe|es debida?|causada por|culpa|por).{0,20}(instrumento|aparato|medicion imperfecta|error de medi|perturb)",),
              (r"(instrumento|aparato)s?.{0,30}(imprecis|imperfect|perturb).{0,30}(incertidumbre|heisenberg)",)),
      frases_error=("La incertidumbre se debe a que los instrumentos son imprecisos.", "La incertidumbre es causada por la perturbación del aparato de medida."),
      frases_correctas=("La incertidumbre no se debe al instrumento.", "La incertidumbre viene de que x y p no conmutan.")),
    C("orbital_orbita", "Orbital y órbita",
      "Un orbital es la trayectoria que recorre el electrón alrededor del núcleo.",
      "¿Qué representa |ψ|² en un orbital: un camino o una distribución de probabilidad? ¿Tiene sentido hablar de trayectoria?",
      "Un orbital es una función de onda de un electrón (ψₙₗₘ). Su módulo al cuadrado da la densidad de probabilidad de hallar al electrón; no hay trayectoria definida. "
      "Las órbitas circulares son del modelo de Bohr, que acierta con los niveles de energía pero no con la imagen del electrón.",
      r"\psi_{nlm}(r,\theta,\varphi)=R_{nl}(r)\,Y_l^m(\theta,\varphi)",
      ("orbital", "densidad_radial", "modelo_bohr"), "hidrogeno", "bohr",
      reglas=((r"orbital.{0,25}(es )?(la )?(trayectoria|orbita|camino|ruta)",), (r"electron.{0,25}(gira|orbita|recorre).{0,25}(alrededor|orbita|trayectoria|nucleo)",)),
      excluye=r"bohr|modelo|semiclasic|clasic",
      frases_error=("Un orbital es la trayectoria del electrón.", "El electrón gira alrededor del núcleo en un orbital."),
      frases_correctas=("En el modelo de Bohr el electrón gira alrededor del núcleo.", "Un orbital es una función de onda.")),
    C("bohr_realidad", "Modelo de Bohr",
      "Las órbitas circulares de Bohr son reales: el electrón realmente las recorre.",
      "El modelo de Bohr acierta con las energías del hidrógeno. ¿Eso prueba que la imagen de órbitas sea correcta?",
      "El modelo de Bohr reproduce los niveles de energía del hidrógeno, pero su imagen de órbitas con radio definido contradice la incertidumbre y falla con átomos de varios "
      "electrones. La descripción actual usa orbitales con densidad de probabilidad.",
      r"E_n=-\frac{13.6\ \text{eV}}{n^2}\quad(\text{correcto}),\quad \text{órbitas}\ (\text{no})",
      ("modelo_bohr", "orbital"), "bohr", "bohr",
      reglas=((r"bohr.{0,40}(describe|muestra|demuestra|prueba).{0,40}(orbitas|trayectoria).{0,25}(reales|existen|correct)",),
              (r"(orbitas|orbita) (de bohr )?(son|es) (reales|correctas|observad)",),
              (r"el electron (realmente|en realidad|efectivamente) (gira|orbita|recorre)",)),
      frases_error=("Las órbitas de Bohr son reales.", "El electrón realmente gira en órbitas."),
      frases_correctas=("Las órbitas de Bohr son una aproximación.",)),
    C("debroglie_macroscopico", "Ondas de materia",
      "Los objetos grandes no tienen onda asociada, o su efecto ondulatorio debería verse.",
      "Calcula h/p para una pelota. ¿Cómo se compara el resultado con el tamaño de cualquier rendija?",
      "Todo objeto con momento p tiene λ = h/p. Para una pelota de 0.145 kg a 40 m/s, λ ≈ 1.1×10⁻³⁴ m, inmensamente menor que cualquier estructura posible: "
      "la difracción es inobservable. Los efectos ondulatorios aparecen cuando λ es comparable con el tamaño de las estructuras (átomos, rendijas atómicas).",
      r"\lambda=\frac hp=\frac{6.626\times10^{-34}}{0.145\cdot40}\approx1.1\times10^{-34}\ \mathrm{m}",
      ("de_broglie", "dualidad"), "de_broglie", "",
      reglas=((r"(pelota|objeto|macroscopic|cuerpo|persona).{0,40}(no tiene|no posee|carece de).{0,20}(longitud de onda|onda)",),),
      con_negacion=True,
      frases_error=("Una pelota no tiene longitud de onda.", "Los objetos macroscópicos no poseen onda asociada."),
      frases_correctas=("Una pelota tiene longitud de onda, pero es muy pequeña.",)),
    C("n_cero", "Números cuánticos de la caja",
      "En la caja de potencial n puede valer 0 (partícula en reposo).",
      "¿Qué función de onda resulta de n = 0 en ψ = A sin(nπx/a)? ¿Describe una partícula en la caja?",
      "Con n = 0, sin(0) = 0 y ψ ≡ 0: no hay partícula. Por eso n = 1, 2, 3, … y el nivel más bajo es E₁ > 0. (En el oscilador sí puede ser n = 0, pues allí E₀ = ħω/2.)",
      r"n=0\ \Rightarrow\ \psi\equiv0\ \text{(no normalizable)}",
      ("pozo_infinito", "cuantizacion", "energia_cero"), "caja", "caja",
      reglas=((r"\bn ?(= ?|puede ser |vale )0\b.{0,40}(caja|pozo|reposo|permitido|posible)",), (r"(caja|pozo).{0,40}\bn ?(= ?|puede ser |vale )0\b",)),
      excluye=r"oscilador|armonic|hermite",
      frases_error=("En la caja n puede ser 0.", "Con n = 0 la partícula está en reposo en el pozo."),
      frases_correctas=("En el oscilador n = 0 es el estado fundamental.",)),
    C("niveles_equiespaciados", "Niveles de energía de la caja",
      "Los niveles de energía de la caja están igualmente espaciados.",
      "Si E_n = n²E₁, ¿cuánto valen E₂ y E₃ en unidades de E₁? ¿Qué sistema sí tiene niveles equiespaciados?",
      "En la caja E_n = n²E₁: 1, 4, 9, 16… La separación crece con n (E_{n+1} − E_n = (2n+1)E₁). Niveles equiespaciados es característica del oscilador armónico, E_n = ħω(n + ½).",
      r"E_n=n^2E_1\quad(1,\,4,\,9,\,16,\dots)",
      ("pozo_infinito", "oscilador", "cuantizacion"), "caja", "caja",
      reglas=((r"(caja|pozo).{0,50}(niveles|energias).{0,30}(equiespaciad|igualmente espaciad|misma separacion|separacion constante)",),
              (r"niveles.{0,10}(de la caja).{0,30}equiespaciad",)),
      frases_error=("Los niveles de la caja están equiespaciados.", "En el pozo los niveles de energía tienen la misma separación."),
      frases_correctas=("Los niveles del oscilador son equiespaciados.", "Los niveles de la caja no son equiespaciados.")),
    C("coeficientes_suma", "Normalización de una superposición",
      "Una superposición está normalizada si los coeficientes suman 1.",
      "¿Qué se suma para obtener la probabilidad total: cₙ o |cₙ|²? Prueba con c₁ = 0.6 y c₂ = 0.8.",
      "La normalización exige Σ|cₙ|² = 1. Con c₁ = 0.6 y c₂ = 0.8, la suma de coeficientes es 1.4, pero 0.36 + 0.64 = 1, así que el estado sí está normalizado. "
      "Si los coeficientes son complejos, también se usa el módulo.",
      r"\sum_n|c_n|^2=1",
      ("normalizacion", "amplitud", "superposicion"), "postulados", "caja",
      reglas=((r"(coeficientes|c ?1 ?\+ ?c ?2).{0,30}(suman|suma|sumar).{0,10}(1|uno)\b",), (r"(suma de los coeficientes).{0,20}(1|uno|igual a 1)",)),
      excluye=r"cuadrad|modulo|probabilidades|c ?\d? ?2\b",
      frases_error=("Los coeficientes deben sumar 1.", "La suma de los coeficientes es igual a 1."),
      frases_correctas=("Los cuadrados de los coeficientes suman 1.", "La suma de las probabilidades es 1.")),
)

POR_ID = {c.id: c for c in CONCEPCIONES}


def detectar(texto: str) -> list:
    """Confusiones detectadas en el texto (lista de `Concepcion`, sin repetir y en el orden del catálogo)."""
    encontradas = []
    for oracion in _oraciones(texto):
        negada = bool(_NEGACION.search(_NO_NEGATIVO.sub("", oracion)))
        for c in CONCEPCIONES:
            if c in encontradas or (negada and not c.con_negacion):
                continue
            if c.excluye and re.search(c.excluye, oracion):
                continue
            if any(all(re.search(patron, oracion) for patron in regla) for regla in c.reglas):
                encontradas.append(c)
    return sorted(encontradas, key=CONCEPCIONES.index)
