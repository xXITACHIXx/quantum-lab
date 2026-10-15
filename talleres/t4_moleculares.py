"""
talleres/t4_moleculares.py — Taller 4: orbitales moleculares (CN⁻), combinación de dos orbitales 2p (O₂) y Hückel del alilo.
"""

from __future__ import annotations

import math

from talleres import _fisica as f
from talleres import _soluciones as _s
from talleres._modelo import NUM, OPC, Datos, Parte, Pregunta, Taller, tex

ESPECIES = {"CN⁻": "el ion cianuro (CN⁻)", "CO": "la molécula de monóxido de carbono (CO)", "NO⁺": "el catión nitrosonio (NO⁺)"}
ALILO = {2: ("catión alilo", "CH₂CHCH₂⁺"), 3: ("radical alilo", "CH₂CHCH₂·"), 4: ("anión alilo", "CH₂CHCH₂⁻")}


def _q1(d: Datos) -> Pregunta:
    esp = d.elegir("CN⁻", list(ESPECIES))
    enun = (f"Marco teórico del orbital molecular para {ESPECIES[esp]}:\n\n"
            "**a)** Genera su diagrama de orbitales moleculares: ¿cuál es el orden de energía de los orbitales de valencia?\n\n"
            "**b)** Escribe su configuración electrónica: ¿cuántos electrones de valencia hay y cuál es el orden de enlace?\n\n"
            "**c)** Escribe una función de onda aceptable considerando solamente los electrones del orbital $\\pi$.")
    orden = ("$\\sigma_{2s}<\\sigma^*_{2s}<\\pi_{2p}$ (dos, degenerados) $<\\sigma_{2p}<\\pi^*_{2p}$ (dos) $<\\sigma^*_{2p}$",
             "$\\sigma_{2s}<\\sigma^*_{2s}<\\sigma_{2p}<\\pi_{2p}$ (dos) $<\\pi^*_{2p}$ (dos) $<\\sigma^*_{2p}$",
             "$\\sigma_{2s}<\\sigma_{2p}<\\pi_{2p}<\\pi^*_{2p}<\\sigma^*_{2p}<\\sigma^*_{2s}$",
             "$\\pi_{2p}<\\sigma_{2s}<\\sigma^*_{2s}<\\sigma_{2p}<\\pi^*_{2p}<\\sigma^*_{2p}$")
    pi = ("Determinante de Slater 4×4 con $\\pi_x\\alpha$, $\\pi_x\\beta$, $\\pi_y\\alpha$ y $\\pi_y\\beta$",
          "Determinante de Slater 4×4 con $\\pi_x\\alpha$, $\\pi_x\\beta$, $\\pi^*_x\\alpha$ y $\\pi^*_x\\beta$",
          "Producto simple $\\pi_x(1)\\pi_x(2)\\pi_y(3)\\pi_y(4)$ con espines asignados",
          "Determinante de Slater 2×2 con $\\pi_x\\alpha$ y $\\pi_y\\alpha$")
    partes = (
        Parte("orden", "a) Orden de los orbitales de valencia", OPC, opciones=orden, correcta=0, peso=0.3,
              explicacion="En las especies con 10 electrones de valencia (como el N₂) los orbitales $2s$ y $2p$ se mezclan y el $\\sigma_{2p}$ queda por encima del $\\pi_{2p}$."),
        Parte("ev", "b) Número de electrones de valencia", NUM, 10.0, "", tol_rel=0.0, tol_abs=0.01, peso=0.15,
              explicacion="CN⁻: 4 + 5 + 1 (la carga). CO: 4 + 6. NO⁺: 5 + 6 − 1. En los tres casos suman 10."),
        Parte("oe", "b) Orden de enlace", NUM, 3.0, "", tol_rel=0.0, tol_abs=0.01, peso=0.25,
              confusiones=((2 / 3, "cuenta bien: $\\text{OE}=\\tfrac12(8-2)=3$ con 8 electrones enlazantes y 2 antienlazantes"),),
              explicacion="Configuración $(\\sigma_{2s})^2(\\sigma^*_{2s})^2(\\pi_{2p})^4(\\sigma_{2p})^2$: $\\text{OE}=\\tfrac12(8-2)=3$."),
        Parte("pi", "c) Función de onda de los electrones $\\pi$", OPC, opciones=pi, correcta=0, peso=0.3,
              explicacion="Cuatro electrones en $\\pi_x$ y $\\pi_y$ (dos orbitales con ambos espines): determinante 4×4 con los cuatro espín-orbitales."))
    sol = _s.moleculares_cn(esp)
    return Pregunta("q1", enun, 2.0, partes, sol, tema="orbitales_moleculares",
                    nota="Los apartados a) y c) son de opción múltiple porque un diagrama o un determinante no se califican como texto libre.")


def _q2(d: Datos) -> Pregunta:
    S = d.elegir(0.15, [0.10, 0.15, 0.20, 0.25])
    H11 = d.elegir(-13.6, [-13.6, -15.8, -17.4])
    K = 1.75
    r = f.energias_lcao_homonuclear(H11, S, K)
    enun = ("Se combinan dos orbitales atómicos $2p_z$ (uno de cada átomo de O) para formar los dos orbitales moleculares del O₂ de este enlace $\\sigma$. "
            f"Se conocen el solapamiento $S_{{12}}={S}$, las energías de los orbitales atómicos $H_{{11}}=H_{{22}}={H11}$ eV y "
            f"$H_{{12}}=-{K}\\,S_{{12}}\\,(H_{{11}}H_{{22}})^{{1/2}}$.\n\n"
            "Evalúa la energía de los dos orbitales moleculares que se generan y sus coeficientes (en la forma $\\psi=c_1\\phi_1+c_2\\phi_2$, normalizada).")
    partes = (
        Parte("H12", "Paso previo: $H_{12}$ (en eV)", NUM, r["H12"], "eV", tol_rel=0.01, peso=0.2,
              confusiones=((-1.0, "$H_{12}$ es negativo: $-1.75\\,S_{12}\\sqrt{H_{11}H_{22}}$ y la raíz es positiva"),
                           ),
              explicacion=f"$H_{{12}}=-{K}\\cdot{S}\\cdot|{H11}|={r['H12']:.3f}$ eV."),
        Parte("Eb", "Energía del orbital enlazante $E_+$ (en eV)", NUM, r["E_enlazante"], "eV", tol_rel=0.01, peso=0.25,
              confusiones=((r["E_antienlazante"] / r["E_enlazante"], "ese es el orbital antienlazante, $E_-=(H_{11}-H_{12})/(1-S)$"),
                           ((H11 + r["H12"]) / r["E_enlazante"], "no olvides dividir entre $(1+S)$ (el solapamiento no es cero)")),
              explicacion="$E_+=\\dfrac{H_{11}+H_{12}}{1+S_{12}}$."),
        Parte("Ea", "Energía del orbital antienlazante $E_-$ (en eV)", NUM, r["E_antienlazante"], "eV", tol_rel=0.01, peso=0.25,
              confusiones=((r["E_enlazante"] / r["E_antienlazante"], "ese es el orbital enlazante, $E_+=(H_{11}+H_{12})/(1+S)$"),
                           ((H11 - r["H12"]) / r["E_antienlazante"], "no olvides dividir entre $(1-S)$")),
              explicacion="$E_-=\\dfrac{H_{11}-H_{12}}{1-S_{12}}$."),
        Parte("cb", "Coeficiente $c_1=c_2$ del enlazante", NUM, r["c_enlazante"], "", tol_rel=0.01, peso=0.15,
              confusiones=((math.sqrt(2) * r["c_enlazante"], "te falta el solapamiento en la normalización: $c=1/\\sqrt{2(1+S)}$, no $1/\\sqrt2$"),),
              explicacion="Normalización con solapamiento: $c_1^2+c_2^2+2c_1c_2S=1\\Rightarrow c=1/\\sqrt{2(1+S)}$."),
        Parte("ca", "Coeficiente $|c_1|=|c_2|$ del antienlazante", NUM, r["c_antienlazante"], "", tol_rel=0.01, peso=0.15,
              explicacion="Con $c_2=-c_1$: $c=1/\\sqrt{2(1-S)}$."))
    sol = _s.lcao(S, H11, K, r)
    return Pregunta("q2", enun, 1.5, partes, sol, tema="orbitales_moleculares")


def _q3(d: Datos) -> Pregunta:
    ne = d.elegir(4, [2, 3, 4])
    nombre, formula = ALILO[ne]
    x, C = f.huckel_alilo()
    enun = (f"El {nombre} ({formula}) es un sistema $\\pi$ conjugado de tres carbonos con **{ne} electrones $\\pi$**.\n\n"
            "**a)** Calcula la energía de los electrones $\\pi$ con la aproximación de Hückel, escrita como $E_\\pi=n_\\alpha\\,\\alpha+n_\\beta\\,\\beta$ "
            "(recuerda que $\\beta<0$).\n\n"
            "**b)** Indica la expresión del orbital molecular $\\pi$ de menor energía con los coeficientes calculados.")
    partes = (
        Parte("e1", "Energía del orbital más bajo: coeficiente de $\\beta$ en $E_1=\\alpha+x\\beta$ ($x$ =)", NUM, float(x[0]), "", tol_rel=0.01, peso=0.2,
              explicacion="La ecuación secular $\\begin{vmatrix}-x&1&0\\\\1&-x&1\\\\0&1&-x\\end{vmatrix}=0$ da $x=\\sqrt2,0,-\\sqrt2$."),
        Parte("na", f"$E_\\pi$: número $n_\\alpha$ (cantidad de $\\alpha$)", NUM, float(ne), "", tol_rel=0.0, tol_abs=0.01, peso=0.2,
              explicacion=f"Cada electrón aporta un $\\alpha$: $n_\\alpha={ne}$."),
        Parte("nb", "$E_\\pi$: coeficiente $n_\\beta$ de $\\beta$", NUM, 2 * float(x[0]), "", tol_rel=0.01, peso=0.25,
              confusiones=((0.5, "los dos electrones del orbital más bajo aportan $2\\sqrt2$; el electrón del no enlazante aporta $0\\cdot\\beta$"),),
              explicacion="Dos electrones en $\\alpha+\\sqrt2\\beta$ aportan $2\\sqrt2\\beta$; el tercero (no enlazante, $x=0$) y el cuarto (si lo hay) no aportan $\\beta$."),
        Parte("c2", "Coeficiente del carbono central en el orbital más bajo", NUM, float(C[1, 0]), "", tol_rel=0.01, peso=0.2,
              confusiones=((0.5 / C[1, 0], "ese es el coeficiente de los carbonos de los extremos ($\\tfrac12$)"),),
              explicacion="$c_2=1/\\sqrt2$."),
        Parte("c1", "Coeficiente de cada carbono extremo en el orbital más bajo", NUM, float(C[0, 0]), "", tol_rel=0.01, peso=0.15,
              confusiones=((C[1, 0] / C[0, 0], "ese es el coeficiente del carbono central ($1/\\sqrt2$); los extremos valen $\\tfrac12$"),),
              explicacion="$c_1=c_3=\\tfrac12$; normalización: $\\tfrac14+\\tfrac12+\\tfrac14=1$."))
    sol = _s.alilo(ne, nombre, formula, x, C)
    return Pregunta("q3", enun, 1.5, partes, sol, tema="orbitales_moleculares",
                    nota="La especie del enunciado original es el anión alilo, CH₂CHCH₂⁻, con 4 electrones $\\pi$ (2 del doble enlace y 2 del carbanión). "
                         "Con «datos nuevos» también aparecen el catión (2 electrones) y el radical (3): solo cambia $n_\\alpha$.")


def construir(d: Datos) -> list[Pregunta]:
    return [_q1(d), _q2(d), _q3(d)]


TALLER = Taller(
    "moleculares", "Orbitales moleculares y método de Hückel",
    "Diagrama de OM y configuración del CN⁻, combinación de dos orbitales 2p con solapamiento (O₂) y orbitales π del alilo por el método de Hückel.",
    ("Orbitales moleculares", "LCAO con solapamiento", "Método de Hückel"), construir,
    n_preguntas=3, puntos=5.0)
