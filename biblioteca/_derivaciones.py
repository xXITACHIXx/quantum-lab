"""biblioteca/_derivaciones.py — Derivaciones paso a paso, cada una con una comprobación numérica contra el código del laboratorio."""

from __future__ import annotations

import numpy as np

import quantum_lab_comun as qc
from biblioteca._modelo import Derivacion as D, Paso as P


# ---------------------------------------------------------------- comprobaciones (referencia calculada por otra vía) ---
def _chk_caja_energia():
    import particula_caja as pc
    a = 1e-9
    calc = pc.energia_nivel(1, a, qc.M_E) / qc.E_CARGA
    ref = qc.H_PLANCK ** 2 / (8 * qc.M_E * a ** 2) / qc.E_CARGA      # h²/(8ma²), forma equivalente
    return "E₁ de un electrón en una caja de 1 nm (código del laboratorio frente a h²/8ma²)", calc, ref, r"\text{eV}"


def _chk_caja_norm():
    import particula_caja as pc
    a = 2.5e-9
    x = np.linspace(0, a, 20001)
    calc = pc.normalizacion_numerica(x, pc.funcion_onda(x, 3, a))
    return "∫|ψ₃|² dx calculada numéricamente con A = √(2/a)", calc, 1.0, ""


def _chk_broglie():
    import particula_caja as pc
    a, n = 1e-9, 4
    calc = pc.longitud_onda_de_broglie(n, a)
    ref = qc.H_PLANCK / pc.momento_estado(n, a)
    return "λ₄ = 2a/n frente a h/p (a = 1 nm)", calc * 1e9, ref * 1e9, r"\text{nm}"


def _chk_osc_cero():
    import oscilador_armonico as oa
    m, w = qc.M_E, 1.0e15
    calc = oa.energia_teorica(0, w)
    return "E₀ del oscilador (ω = 10¹⁵ rad/s) frente a ħω/2", calc / qc.E_CARGA, 0.5 * qc.HBAR * w / qc.E_CARGA, r"\text{eV}"


def _chk_retorno():
    import oscilador_armonico as oa
    m, w, n = qc.M_E, 1.0e15, 3
    calc = oa.punto_retorno(n, m, w)
    ref = np.sqrt(2 * oa.energia_teorica(n, w) / (m * w ** 2))      # V(x) = E
    return "x_ret del estado n = 3 frente a √(2E/mω²)", calc * 1e9, ref * 1e9, r"\text{nm}"


def _chk_foto():
    import efecto_fotoelectrico as ef
    lam, phi = 300.0, 2.28
    nu = qc.C_LUZ / (lam * 1e-9) if hasattr(qc, "C_LUZ") else ef.C / (lam * 1e-9)
    calc = float(ef.energia_cinetica_maxima(nu, phi))
    ref = 1239.841984 / lam - phi                                    # hc = 1239.84 eV·nm
    return "K_máx para λ = 300 nm sobre sodio (Φ = 2.28 eV) frente a 1239.84/λ − Φ", calc, ref, r"\text{eV}"


def _chk_bohr():
    import modelo_bohr as mb
    calc = float(mb.energia_nivel(1))
    ref = -qc.E_HARTREE / 2 / qc.E_CARGA                             # −Eh/2
    return "E₁ del hidrógeno frente a −Eₕ/2", calc, ref, r"\text{eV}"


def _chk_rydberg():
    import modelo_bohr as mb
    calc = mb.longitud_rydberg(3, 2) * 1e9
    return "Línea Hα (3→2) con masa reducida frente al valor medido en vacío (656.47 nm)", calc, 656.47, r"\text{nm}"


def _chk_incert():
    sigma = 1.0
    x = np.linspace(-12, 12, 48001)
    psi = np.exp(-x ** 2 / (4 * sigma ** 2))
    psi = psi / np.sqrt(np.trapezoid(psi ** 2, x) if hasattr(np, "trapezoid") else np.trapz(psi ** 2, x))
    tr = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    dx = np.sqrt(tr(x ** 2 * psi ** 2, x))
    dp = np.sqrt(tr(np.gradient(psi, x) ** 2, x))                     # en unidades de ħ (⟨p⟩ = 0)
    return "Δx·Δp para un gaussiano (en unidades de ħ) frente a 1/2", dx * dp, 0.5, r"\hbar"


# ------------------------------------------------------------------------------------------------------ derivaciones ---
DERIVACIONES = (
    D("caja_energias", "Niveles de energía de la partícula en una caja", "caja", "caja",
      (P("Dentro de la caja V = 0; la ecuación de Schrödinger estacionaria queda así.", r"-\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2}=E\,\psi"),
       P("Se propone una solución oscilante con número de onda k.", r"\psi(x)=A\sin(kx)+B\cos(kx),\qquad k=\frac{\sqrt{2mE}}{\hbar}"),
       P("En la pared x = 0 la función debe anularse (V = ∞ fuera), lo que elimina el coseno.", r"\psi(0)=0\ \Rightarrow\ B=0"),
       P("En x = a también debe anularse; el seno solo lo hace para ciertos k.", r"\psi(a)=0\ \Rightarrow\ \sin(ka)=0\ \Rightarrow\ k_n=\frac{n\pi}{a},\ \ n=1,2,3,\dots"),
       P("Se despeja la energía con la relación entre k y E. n = 0 se descarta porque da ψ ≡ 0.", r"E_n=\frac{\hbar^2k_n^2}{2m}=\frac{n^2\pi^2\hbar^2}{2ma^2}=\frac{n^2h^2}{8ma^2}")),
      "La energía está cuantizada y crece como n². El estado fundamental (n = 1) no tiene energía cero. Reducir la caja a la mitad cuadruplica cada nivel.",
      _chk_caja_energia, "caja"),
    D("caja_normalizacion", "Normalización de las autofunciones de la caja", "caja", "caja",
      (P("La función tiene la forma ψₙ = A sin(nπx/a) dentro de la caja y cero fuera.", r"\psi_n(x)=A\sin\!\left(\frac{n\pi x}{a}\right)"),
       P("La probabilidad total debe valer 1.", r"\int_0^a |\psi_n|^2\,dx=A^2\int_0^a\sin^2\!\left(\frac{n\pi x}{a}\right)dx=1"),
       P("La integral del seno al cuadrado sobre un número entero de semiperiodos vale a/2.", r"\int_0^a\sin^2\!\left(\frac{n\pi x}{a}\right)dx=\frac a2"),
       P("Se despeja la constante (se toma real y positiva; una fase global no importa).", r"A^2\,\frac a2=1\ \Rightarrow\ A=\sqrt{\frac2a}")),
      "ψₙ(x) = √(2/a) sin(nπx/a). La constante no depende de n, y tiene unidades de 1/√longitud para que |ψ|² sea una densidad por unidad de longitud.",
      _chk_caja_norm, "caja"),
    D("caja_broglie", "Longitud de onda de De Broglie en la caja", "de_broglie", "caja",
      (P("La energía en la caja es solo cinética, por lo que el módulo del momento sale de E = p²/2m.", r"E_n=\frac{p_n^2}{2m}\ \Rightarrow\ |p_n|=\sqrt{2mE_n}"),
       P("Con la energía cuantizada de la caja.", r"|p_n|=\frac{n\pi\hbar}{a}=\frac{nh}{2a}"),
       P("Se aplica la relación de De Broglie.", r"\lambda_n=\frac{h}{|p_n|}=\frac{2a}{n}"),
       P("Equivale a exigir que quepan n semilongitudes de onda en la caja.", r"n\,\frac{\lambda_n}{2}=a")),
      "La condición de cuantización equivale a una onda estacionaria. ψₙ es la suma de dos ondas viajeras con momentos +pₙ y −pₙ, no la descripción de una trayectoria.",
      _chk_broglie, "caja"),
    D("osc_cero", "Energía del estado fundamental del oscilador", "oscilador", "oscilador",
      (P("Con ξ = x/x₀ y x₀ = √(ħ/mω), el hamiltoniano se escribe en forma adimensional.", r"\hat H=\frac{\hbar\omega}{2}\left(-\frac{d^2}{d\xi^2}+\xi^2\right)"),
       P("Se prueba la gaussiana ψ₀ = e^{−ξ²/2}. Sus derivadas son:", r"\psi_0'=-\xi\,\psi_0,\qquad \psi_0''=(\xi^2-1)\,\psi_0"),
       P("Se sustituye en el hamiltoniano.", r"\hat H\psi_0=\frac{\hbar\omega}{2}\left[-(\xi^2-1)+\xi^2\right]\psi_0=\frac{\hbar\omega}{2}\,\psi_0"),
       P("Es una autofunción; su autovalor es la energía del estado fundamental.", r"E_0=\frac{\hbar\omega}{2}"),
       P("Los demás niveles (resultado de la solución completa, con polinomios de Hermite) están separados ħω.", r"E_n=\hbar\omega\left(n+\tfrac12\right)")),
      "El oscilador nunca está en reposo: E₀ = ħω/2. Es la misma idea que en la caja: confinar la partícula obliga a un momento no nulo.",
      _chk_osc_cero, "oscilador"),
    D("osc_retorno", "Punto de retorno clásico del oscilador", "oscilador", "oscilador",
      (P("En el punto de retorno la energía cinética clásica es cero, así que E = V.", r"E_n=\tfrac12m\omega^2x_{\text{ret}}^2"),
       P("Se despeja x y se sustituye En = ħω(n + ½).", r"x_{\text{ret}}=\sqrt{\frac{2E_n}{m\omega^2}}=\sqrt{\frac{2\hbar(n+\tfrac12)}{m\omega}}"),
       P("En términos de la longitud característica x₀.", r"x_{\text{ret}}=\sqrt{2n+1}\;x_0")),
      "Clásicamente la partícula no va más allá de ±x_ret. La función de onda sí se extiende un poco más allá (penetración en la zona prohibida), cada vez menos conforme x crece.",
      _chk_retorno, "oscilador"),
    D("foto_einstein", "Ecuación de Einstein del efecto fotoeléctrico", "fotoelectrico", "fotoelectrico",
      (P("Cada electrón absorbe un fotón completo; su energía es hν.", r"E_\gamma=h\nu"),
       P("Parte de esa energía se gasta en vencer la atracción del metal (función de trabajo Φ). El resto es energía cinética.", r"h\nu=\Phi+K"),
       P("La máxima energía cinética corresponde a los electrones que no pierden energía adicional en el interior.", r"K_{\max}=h\nu-\Phi"),
       P("La emisión exige K_máx ≥ 0, lo que fija la frecuencia umbral.", r"\nu_0=\frac{\Phi}{h}"),
       P("El potencial de frenado detiene al electrón más rápido: eV₀ = K_máx.", r"V_0=\frac{h\nu-\Phi}{e}")),
      "K_máx depende de la frecuencia pero no de la intensidad; la intensidad cambia el número de fotoelectrones por segundo. Una pendiente h/e en V₀(ν) permite medir la constante de Planck.",
      _chk_foto, "fotoelectrico"),
    D("bohr_niveles", "Niveles de energía del hidrógeno (Bohr)", "bohr", "bohr",
      (P("Fuerza de Coulomb igual a masa por aceleración centrípeta, para una órbita circular de radio r.", r"\frac{e^2}{4\pi\varepsilon_0r^2}=\frac{m_ev^2}{r}"),
       P("Postulado de Bohr: el momento angular está cuantizado.", r"m_evr=n\hbar"),
       P("Se elimina v y se obtiene el radio permitido.", r"r_n=\frac{4\pi\varepsilon_0\hbar^2}{m_ee^2}\,n^2=a_0\,n^2"),
       P("Energía total = cinética + potencial. Por el virial, K = −V/2, de modo que E = V/2.", r"E=\frac12m_ev^2-\frac{e^2}{4\pi\varepsilon_0r}=-\frac{e^2}{8\pi\varepsilon_0r}"),
       P("Se sustituye el radio de la órbita n.", r"E_n=-\frac{m_ee^4}{8\varepsilon_0^2h^2}\frac1{n^2}=-\frac{E_h}{2n^2}\approx-\frac{13.6\ \text{eV}}{n^2}")),
      "Los niveles reproducen los del hidrógeno, pero la imagen de órbitas circulares no es correcta: la teoría cuántica los obtiene con orbitales, sin trayectorias.",
      _chk_bohr, "bohr"),
    D("bohr_rydberg", "Fórmula de Rydberg para las líneas espectrales", "bohr", "bohr",
      (P("Al pasar de nᵢ a n_f se emite un fotón con la diferencia de energías.", r"h\nu=E_{n_i}-E_{n_f}"),
       P("Con los niveles de Bohr de un ion hidrogenoide de carga nuclear Z.", r"h\nu=\frac{Z^2E_h}{2}\left(\frac1{n_f^2}-\frac1{n_i^2}\right)"),
       P("Se pasa a número de onda 1/λ = ν/c.", r"\frac1\lambda=R\,Z^2\left(\frac1{n_f^2}-\frac1{n_i^2}\right),\qquad R=\frac{E_h}{2hc}"),
       P("Con masa reducida, R se corrige por μ/mₑ; en el hidrógeno el cambio relativo es de unos 5×10⁻⁴.", r"R_M=R_\infty\,\frac{\mu}{m_e},\quad \mu=\frac{m_eM}{m_e+M}")),
      "Las series (Lyman, Balmer, Paschen…) son los grupos de transiciones con el mismo n_f. Con la masa reducida el resultado concuerda con los espectros medidos.",
      _chk_rydberg, "bohr"),
    D("incert_gauss", "Incertidumbre mínima: el paquete gaussiano", "incertidumbre", "incertidumbre",
      (P("Se toma un gaussiano real centrado en el origen, con ancho σ.", r"\psi(x)=\left(2\pi\sigma^2\right)^{-1/4}e^{-x^2/4\sigma^2}"),
       P("Su dispersión en posición es σ (⟨x⟩ = 0).", r"\Delta x=\sigma"),
       P("Con p̂ = −iħ d/dx, ⟨p⟩ = 0 y ⟨p²⟩ = ħ²∫|ψ′|²dx.", r"\psi'=-\frac{x}{2\sigma^2}\psi\ \Rightarrow\ \langle p^2\rangle=\frac{\hbar^2}{4\sigma^2}"),
       P("Por tanto:", r"\Delta p=\frac{\hbar}{2\sigma}\ \Rightarrow\ \Delta x\,\Delta p=\frac\hbar2")),
      "El gaussiano alcanza la cota mínima de Heisenberg. Estrechar el paquete en x lo ensancha en p, y recíprocamente.",
      _chk_incert, "incertidumbre"),
)

POR_ID = {d.id: d for d in DERIVACIONES}
