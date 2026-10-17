"""
solucionador/_problemas.py — Resolutores de los problemas típicos del curso.

Cada función recibe las magnitudes en unidades cómodas (nm, eV, kg…), valida, y devuelve una `Solucion`. Los cálculos usan las constantes
CODATA de `scipy.constants`, y las pruebas comparan cada resultado con las funciones de los simuladores.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import constants as const

from biblioteca._modelo import Paso as P
from solucionador._modelo import Solucion, con_unidad as cu, num

H, HBAR, C, E, M_E = const.h, const.hbar, const.c, const.e, const.m_e

U_P = r"kg\,m/s"      # unidad del momento lineal

MASAS = {
    "electron": ("Electrón", const.m_e),
    "proton": ("Protón", const.m_p),
    "neutron": ("Neutrón", const.m_n),
    "personalizada": ("Otra masa (kg)", None),
}


def _positivo(valor: float, nombre: str) -> float:
    v = float(valor)
    if not math.isfinite(v) or v <= 0:
        raise ValueError(f"{nombre} debe ser un número positivo.")
    return v


def _entero(valor, nombre: str, minimo: int = 1, maximo: int = 1000) -> int:
    v = float(valor)
    if not math.isfinite(v) or v != int(v) or not (minimo <= v <= maximo):
        raise ValueError(f"{nombre} debe ser un entero entre {minimo} y {maximo}.")
    return int(v)


# ---------------------------------------------------------------------------------------------------------------- fotoeléctrico
def fotoelectrico(lambda_nm: float, phi_ev: float) -> Solucion:
    lam = _positivo(lambda_nm, "La longitud de onda")
    phi = _positivo(phi_ev, "La función de trabajo")
    nu = C / (lam * 1e-9)
    e_j = H * nu
    e_ev = e_j / E
    nu0 = phi * E / H
    lam0 = H * C / (phi * E) * 1e9
    hay = e_ev > phi
    k = max(e_ev - phi, 0.0)
    v = math.sqrt(2 * k * E / M_E)
    pasos = [
        P("Frecuencia de la luz a partir de su longitud de onda.", rf"\nu=\frac{{c}}{{\lambda}}=\frac{{{num(C)}\ \mathrm{{m/s}}}}{{{num(lam * 1e-9)}\ \mathrm{{m}}}}={cu(nu, 'Hz')}"),
        P("Energía de cada fotón, primero en julios y luego en electronvoltios (1 eV = 1.602×10⁻¹⁹ J).",
          rf"E_\gamma=h\nu=({num(H)}\ \mathrm{{J\,s}})({num(nu)}\ \mathrm{{Hz}})={cu(e_j, 'J')}={cu(e_ev, 'eV')}"),
        P("Umbral del metal: frecuencia y longitud de onda mínimas para que haya emisión.",
          rf"\nu_0=\frac{{\Phi}}{{h}}=\frac{{{num(phi)}\ \mathrm{{eV}}\cdot{num(E)}\ \mathrm{{J/eV}}}}{{{num(H)}\ \mathrm{{J\,s}}}}={cu(nu0, 'Hz')},\qquad "
          rf"\lambda_0=\frac{{hc}}{{\Phi}}={cu(lam0, 'nm')}"),
        P("Comparación: hay emisión si E_γ > Φ (equivale a ν > ν₀ y λ < λ₀).", rf"{num(e_ev)}\ \mathrm{{eV}}\ {'>' if hay else r'\le'}\ {num(phi)}\ \mathrm{{eV}}"),
    ]
    if hay:
        pasos += [
            P("Energía cinética máxima de los fotoelectrones.", rf"K_{{\max}}=h\nu-\Phi={num(e_ev)}\ \mathrm{{eV}}-{num(phi)}\ \mathrm{{eV}}={cu(k, 'eV')}"),
            P("Potencial de frenado: la diferencia de potencial que detiene al electrón más rápido (eV₀ = K_máx).",
              rf"V_0=\frac{{K_{{\max}}}}{{e}}={cu(k, 'V')}"),
            P("Rapidez máxima (no relativista, pues K_máx ≪ mₑc² ≈ 511 keV).",
              rf"v_{{\max}}=\sqrt{{\frac{{2K_{{\max}}}}{{m_e}}}}=\sqrt{{\frac{{2({num(k * E)}\ \mathrm{{J}})}}{{{num(M_E)}\ \mathrm{{kg}}}}}}={cu(v, 'm/s')}"),
        ]
        res = (("Energía del fotón", cu(e_ev, "eV")), ("Energía cinética máxima", cu(k, "eV")), ("Potencial de frenado", cu(k, "V")),
               ("Rapidez máxima", cu(v, "m/s")))
        interp = (f"Cada fotón entrega {num(e_ev)} eV; {num(phi)} eV se gastan en extraer el electrón y el resto queda como energía cinética. "
                  "Si se duplica la intensidad con la misma longitud de onda, llega el doble de fotones por segundo y la corriente se duplica, "
                  f"pero K_máx sigue siendo {num(k)} eV, porque cada electrón absorbe un solo fotón.")
        avis = ()
    else:
        res = (("Energía del fotón", cu(e_ev, "eV")), ("Longitud de onda umbral", cu(lam0, "nm")), ("Emisión", r"\text{no hay}"))
        interp = (f"Cada fotón tiene {num(e_ev)} eV, menos que los {num(phi)} eV que exige el metal; ningún electrón sale, por intensa que sea la luz, "
                  f"porque cada electrón absorbe un solo fotón. Hay que usar λ < {num(lam0)} nm.")
        avis = ("La energía del fotón no alcanza la función de trabajo: K_máx = 0 y no hay potencial de frenado que calcular.",)
    return Solucion("Efecto fotoeléctrico",
                    (("Energía del fotón", r"E_\gamma=h\nu=\frac{hc}{\lambda}"), ("Ecuación de Einstein", r"K_{\max}=h\nu-\Phi"),
                     ("Umbral", r"\nu_0=\Phi/h"), ("Potencial de frenado", r"eV_0=K_{\max}")),
                    (rf"\lambda={cu(lam, 'nm')}", rf"\Phi={cu(phi, 'eV')}", rf"h={num(H)}\ \mathrm{{J\,s}},\ c={num(C)}\ \mathrm{{m/s}},\ e={num(E)}\ \mathrm{{C}}"),
                    tuple(pasos), res, interp, avis,
                    {"nu": nu, "E_ev": e_ev, "nu0": nu0, "lambda0_nm": lam0, "K_ev": k, "V0": k, "v_max": v if hay else 0.0, "emision": hay})


# ---------------------------------------------------------------------------------------------------------------------- caja
def caja(n, a_nm: float, masa_kg: float) -> Solucion:
    n = _entero(n, "El número cuántico n", 1, 200)
    a = _positivo(a_nm, "La longitud de la caja") * 1e-9
    m = _positivo(masa_kg, "La masa")
    en = n ** 2 * math.pi ** 2 * HBAR ** 2 / (2 * m * a ** 2)
    p = n * math.pi * HBAR / a
    lam = 2 * a / n
    en1 = (n + 1) ** 2 * math.pi ** 2 * HBAR ** 2 / (2 * m * a ** 2)
    de = en1 - en
    lam_f = H * C / de
    pasos = [
        P("Energía del nivel n (de imponer ψ(0) = ψ(a) = 0).",
          rf"E_n=\frac{{n^2\pi^2\hbar^2}}{{2ma^2}}=\frac{{{n}^2\pi^2({num(HBAR)}\ \mathrm{{J\,s}})^2}}{{2({num(m)}\ \mathrm{{kg}})({num(a)}\ \mathrm{{m}})^2}}={cu(en, 'J')}={cu(en / E, 'eV')}"),
        P("Módulo del momento de cada onda viajera componente y longitud de onda de De Broglie.",
          rf"|p_n|=\frac{{n\pi\hbar}}{{a}}={cu(p, U_P)},\qquad \lambda_n=\frac{{2a}}{{n}}={cu(lam * 1e9, 'nm')}"),
        P("Nodos interiores: ψₙ se anula en x = ka/n, con k = 1, …, n − 1 (hay n − 1).", rf"\text{{número de nodos interiores}}=n-1={n - 1}"),
        P("Diferencia de energía hasta el nivel siguiente, y longitud de onda del fotón que la absorbería.",
          rf"\Delta E=E_{{{n + 1}}}-E_{{{n}}}=(2n+1)E_1={cu(de / E, 'eV')},\qquad \lambda_\gamma=\frac{{hc}}{{\Delta E}}={cu(lam_f * 1e9, 'nm')}"),
    ]
    return Solucion("Partícula en una caja unidimensional",
                    (("Energía", r"E_n=\frac{n^2\pi^2\hbar^2}{2ma^2}"), ("Momento", r"|p_n|=\frac{n\pi\hbar}{a}"),
                     ("De Broglie", r"\lambda_n=\frac{h}{|p_n|}=\frac{2a}{n}"), ("Transición", r"\Delta E=h\nu=\frac{hc}{\lambda}")),
                    (rf"n={n}", rf"a={cu(a * 1e9, 'nm')}", rf"m={cu(m, 'kg')}", rf"\hbar={num(HBAR)}\ \mathrm{{J\,s}}"),
                    tuple(pasos),
                    (("Energía del nivel", cu(en / E, "eV")), ("Longitud de onda de De Broglie", cu(lam * 1e9, "nm")),
                     ("Nodos interiores", str(n - 1)), (f"Fotón n → n+1", cu(lam_f * 1e9, "nm"))),
                    "La energía crece como n² y como 1/a²: la mitad de caja cuadruplica cada nivel. La caja contiene n semilongitudes de onda, es decir "
                    "una onda estacionaria; ψ es una amplitud y la partícula no recorre una trayectoria definida.",
                    () if a * 1e9 <= 1000 else ("Una caja de más de 1 µm hace que los niveles queden casi juntos: el efecto cuántico es ya muy pequeño.",),
                    {"E_J": en, "E_eV": en / E, "p": p, "lambda": lam, "dE_J": de, "lambda_foton": lam_f, "nodos": n - 1})


# ------------------------------------------------------------------------------------------------------------------ oscilador
def oscilador(n, masa_kg: float, omega: float | None = None, k_resorte: float | None = None) -> Solucion:
    n = _entero(n, "El número cuántico n", 0, 200)
    m = _positivo(masa_kg, "La masa")
    if (omega is None) == (k_resorte is None):
        raise ValueError("Indique ω o la constante de fuerza k, pero no ambas.")
    pasos = []
    if k_resorte is not None:
        k = _positivo(k_resorte, "La constante de fuerza k")
        w = math.sqrt(k / m)
        pasos.append(P("Frecuencia angular a partir de la constante de fuerza.", rf"\omega=\sqrt{{\frac{{k}}{{m}}}}=\sqrt{{\frac{{{num(k)}\ \mathrm{{N/m}}}}{{{num(m)}\ \mathrm{{kg}}}}}}={cu(w, 'rad/s')}"))
        dato = rf"k={cu(k, 'N/m')}"
    else:
        w = _positivo(omega, "La frecuencia angular ω")
        dato = rf"\omega={cu(w, 'rad/s')}"
    x0 = math.sqrt(HBAR / (m * w))
    en = HBAR * w * (n + 0.5)
    e0 = 0.5 * HBAR * w
    xr = math.sqrt(2 * n + 1) * x0
    de = HBAR * w
    nu = w / (2 * math.pi)
    lam_f = 2 * math.pi * C / w
    pasos += [
        P("Longitud característica del oscilador.", rf"x_0=\sqrt{{\frac{{\hbar}}{{m\omega}}}}=\sqrt{{\frac{{{num(HBAR)}}}{{({num(m)})({num(w)})}}}}\ \mathrm{{m}}={cu(x0 * 1e9, 'nm')}"),
        P("Energía del nivel y energía de punto cero.",
          rf"E_{{{n}}}=\hbar\omega\left({n}+\tfrac12\right)={cu(en, 'J')}={cu(en / E, 'eV')},\qquad E_0=\tfrac12\hbar\omega={cu(e0 / E, 'eV')}"),
        P("Punto de retorno clásico (donde V = E).", rf"x_{{\text{{ret}}}}=\sqrt{{2n+1}}\,x_0=\sqrt{{{2 * n + 1}}}\,({num(x0 * 1e9)}\ \mathrm{{nm}})={cu(xr * 1e9, 'nm')}"),
        P("Separación entre niveles consecutivos y el fotón que la absorbe (regla de selección Δn = ±1).",
          rf"\Delta E=\hbar\omega={cu(de / E, 'eV')},\qquad \nu=\frac{{\omega}}{{2\pi}}={cu(nu, 'Hz')},\qquad \lambda_\gamma=\frac{{2\pi c}}{{\omega}}={cu(lam_f * 1e9, 'nm')}"),
    ]
    return Solucion("Oscilador armónico cuántico",
                    (("Frecuencia", r"\omega=\sqrt{k/m}"), ("Longitud característica", r"x_0=\sqrt{\hbar/(m\omega)}"),
                     ("Energía", r"E_n=\hbar\omega\left(n+\tfrac12\right)"), ("Retorno", r"x_{\text{ret}}=\sqrt{2n+1}\,x_0")),
                    (rf"n={n}", rf"m={cu(m, 'kg')}", dato), tuple(pasos),
                    (("Energía del nivel", cu(en / E, "eV")), ("Energía de punto cero", cu(e0 / E, "eV")),
                     ("Punto de retorno", cu(xr * 1e9, "nm")), ("Separación entre niveles", cu(de / E, "eV"))),
                    "Los niveles son equiespaciados y el más bajo no tiene energía cero. La función de onda no termina en el punto de retorno: penetra "
                    "en la zona prohibida clásicamente, con probabilidad que decae.",
                    (), {"omega": w, "x0": x0, "E_J": en, "E0_J": e0, "x_ret": xr, "dE_J": de, "lambda_foton": lam_f})


# ---------------------------------------------------------------------------------------------------------------- Bohr / Rydberg
def rydberg(nucleo: str, n_i, n_f, masa_reducida: bool = True) -> Solucion:
    import modelo_bohr as mb
    if nucleo not in mb.NUCLEOS:
        raise ValueError("Núcleo no disponible.")
    n_i, n_f = _entero(n_i, "El nivel inicial", 1, 100), _entero(n_f, "El nivel final", 1, 100)
    if n_i == n_f:
        raise ValueError("Los niveles inicial y final deben ser distintos.")
    z = mb.NUCLEOS[nucleo][0]
    f = mb.factor_masa_reducida(nucleo) if masa_reducida else 1.0
    ry = mb.RY_EV
    ei, ef = -z ** 2 * ry * f / n_i ** 2, -z ** 2 * ry * f / n_f ** 2
    de = ef - ei                                  # >0 absorción
    emite = de < 0
    lam = H * C / (abs(de) * E) * 1e9
    nu = abs(de) * E / H
    serie = mb.identificar_serie(min(n_i, n_f), nucleo)
    factor_tex = r"\,\frac{\mu}{m_e}" if masa_reducida else ""
    pasos = [
        P("Energía de cada nivel (Bohr" + (", con la corrección de masa reducida)." if masa_reducida else ", núcleo de masa infinita)."),
          rf"E_n=-\frac{{Z^2\,\mathrm{{Ry}}}}{{n^2}}{factor_tex}:\quad E_{{{n_i}}}={cu(ei, 'eV')},\quad E_{{{n_f}}}={cu(ef, 'eV')}"),
        P("Variación de energía del átomo en la transición." , rf"\Delta E=E_{{{n_f}}}-E_{{{n_i}}}={cu(ef, 'eV')}-({cu(ei, 'eV')})={cu(de, 'eV')}"),
        P("El fotón lleva |ΔE|: se emite si ΔE < 0 y se absorbe si ΔE > 0.", rf"\lambda=\frac{{hc}}{{|\Delta E|}}={cu(lam, 'nm')},\qquad \nu=\frac{{|\Delta E|}}{{h}}={cu(nu, 'Hz')}"),
    ]
    return Solucion("Transición en un átomo hidrogenoide (Bohr)",
                    (("Niveles", r"E_n=-\frac{Z^2\,\mathrm{Ry}}{n^2}"), ("Fotón", r"|\Delta E|=h\nu=\frac{hc}{\lambda}"),
                     ("Rydberg", r"\frac1\lambda=R_MZ^2\left|\frac1{n_f^2}-\frac1{n_i^2}\right|")),
                    (rf"Z={z}", rf"n_i={n_i},\ n_f={n_f}", rf"\mathrm{{Ry}}={num(ry)}\ \mathrm{{eV}}", rf"\mu/m_e={num(f, 8)}" if masa_reducida else r"\mu/m_e\to1"),
                    tuple(pasos),
                    (("Proceso", r"\text{emisión}" if emite else r"\text{absorción}"), ("Energía del fotón", cu(abs(de), "eV")),
                     ("Longitud de onda", cu(lam, "nm")), ("Serie", rf"\text{{{serie[0]} ({serie[1]})}}")),
                    "Los saltos hacia n = 1 dan fotones más energéticos que los que terminan en n mayor: por eso Lyman está en el ultravioleta y Balmer, en parte, "
                    "en el visible. El modelo da bien los niveles del hidrógeno, pero no describe órbitas reales del electrón.",
                    () if nucleo == "H" else ("Para iones, la serie es análoga a la del hidrógeno pero con las energías multiplicadas por Z².",),
                    {"E_i": ei, "E_f": ef, "dE_eV": de, "lambda_nm": lam, "nu": nu, "emite": emite})


# ----------------------------------------------------------------------------------------------------------------------- De Broglie
def de_broglie(masa_kg: float, modo: str, valor: float) -> Solucion:
    m = _positivo(masa_kg, "La masa")
    if modo not in ("velocidad", "energia"):
        raise ValueError("El modo debe ser «velocidad» o «energia».")
    x = _positivo(valor, "El valor")
    if modo == "velocidad":
        v = x
        if v >= C:
            raise ValueError("La rapidez debe ser menor que la de la luz.")
        p = m * v
        k = 0.5 * m * v ** 2
        paso_p = P("Momento lineal (no relativista).", rf"p=mv=({num(m)}\ \mathrm{{kg}})({num(v)}\ \mathrm{{m/s}})={cu(p, U_P)}")
        dato = rf"v={cu(v, 'm/s')}"
    else:
        k = x * E
        p = math.sqrt(2 * m * k)
        v = p / m
        paso_p = P("Momento a partir de la energía cinética K = p²/2m.", rf"p=\sqrt{{2mK}}=\sqrt{{2({num(m)}\ \mathrm{{kg}})({num(k)}\ \mathrm{{J}})}}={cu(p, U_P)}")
        dato = rf"K={cu(x, 'eV')}"
    lam = H / p
    beta = v / C
    avis = ("La rapidez supera el 10 % de c: la fórmula no relativista pierde exactitud (en ese caso usar p = γmv).",) if beta > 0.1 else ()
    pasos = [paso_p, P("Rapidez como fracción de la de la luz: comprueba si la expresión no relativista es válida (β ≪ 1).",
                       rf"\beta=\frac{{v}}{{c}}=\frac{{{num(v)}\ \mathrm{{m/s}}}}{{{num(C)}\ \mathrm{{m/s}}}}={num(beta)}"),
             P("Longitud de onda de De Broglie.", rf"\lambda=\frac{{h}}{{p}}=\frac{{{num(H)}\ \mathrm{{J\,s}}}}{{{num(p)}\ \mathrm{{kg\,m/s}}}}={cu(lam, 'm')}={cu(lam * 1e9, 'nm')}")]
    macro = lam < 1e-12
    return Solucion("Longitud de onda de De Broglie",
                    (("Relación de De Broglie", r"\lambda=\frac{h}{p}"), ("Momento", r"p=mv=\sqrt{2mK}")),
                    (rf"m={cu(m, 'kg')}", dato, rf"h={num(H)}\ \mathrm{{J\,s}}"), tuple(pasos),
                    (("Momento", cu(p, U_P)), ("Longitud de onda", cu(lam * 1e9, "nm")), ("Rapidez", cu(v, "m/s"))),
                    ("Esta longitud de onda es mucho menor que cualquier objeto o rendija accesible: los efectos ondulatorios son inobservables y el objeto "
                     "se comporta de forma clásica." if macro else
                     "La longitud de onda es comparable con distancias atómicas o moleculares (≈ 0.1 nm); por eso aparecen difracción e interferencia con cristales o rendijas "
                     "de ese tamaño."),
                    avis, {"p": p, "lambda": lam, "v": v, "K_J": k})


# ---------------------------------------------------------------------------------------------------------------------- incertidumbre
def incertidumbre(dx_nm: float, masa_kg: float) -> Solucion:
    dx = _positivo(dx_nm, "La incertidumbre en la posición") * 1e-9
    m = _positivo(masa_kg, "La masa")
    dp = HBAR / (2 * dx)
    dv = dp / m
    ek = dp ** 2 / (2 * m)
    pasos = [
        P("Cota inferior de la incertidumbre en el momento (relación de Heisenberg).", rf"\Delta p\ge\frac{{\hbar}}{{2\,\Delta x}}=\frac{{{num(HBAR)}\ \mathrm{{J\,s}}}}{{2({num(dx)}\ \mathrm{{m}})}}={cu(dp, U_P)}"),
        P("Incertidumbre mínima en la rapidez.", rf"\Delta v\ge\frac{{\Delta p}}{{m}}=\frac{{{num(dp)}}}{{{num(m)}}}\ \mathrm{{m/s}}={cu(dv, 'm/s')}"),
        P("Orden de magnitud de la energía cinética asociada (zona de confinamiento).", rf"K\sim\frac{{(\Delta p)^2}}{{2m}}={cu(ek / E, 'eV')}"),
    ]
    return Solucion("Principio de incertidumbre",
                    (("Heisenberg", r"\Delta x\,\Delta p\ge\frac\hbar2"), ("Rapidez", r"\Delta v=\Delta p/m")),
                    (rf"\Delta x={cu(dx * 1e9, 'nm')}", rf"m={cu(m, 'kg')}", rf"\hbar={num(HBAR)}\ \mathrm{{J\,s}}"), tuple(pasos),
                    (("Δp mínima", cu(dp, U_P)), ("Δv mínima", cu(dv, "m/s")), ("Energía cinética asociada", cu(ek / E, "eV"))),
                    "Localizar la partícula en una región más estrecha obliga a una mayor dispersión de momentos. No es una limitación del instrumento: "
                    "es una propiedad del estado. Es el mismo argumento que explica la energía de punto cero.",
                    (), {"dp": dp, "dv": dv, "K_J": ek})


PROBLEMAS = {
    "fotoelectrico": "Efecto fotoeléctrico",
    "caja": "Partícula en una caja",
    "oscilador": "Oscilador armónico",
    "rydberg": "Transición de Bohr / Rydberg",
    "de_broglie": "Longitud de onda de De Broglie",
    "incertidumbre": "Principio de incertidumbre",
}
