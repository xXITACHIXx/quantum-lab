"""
espin_electrones.py — QUANTUM LAB · Simulador 08: espín total de dos electrones
===============================================================================

Dada una función de onda de dos electrones escrita en notación de Dirac con espín-orbitales hidrogenoides,

    Ψ = Σ cₖ |φₐ σₐ ; φᵦ σᵦ⟩         (electrón 1 ; electrón 2;  σ = α, β)

calcula los autovalores de Ŝ² (momento angular de espín total, s(s+1)ħ² con s = 0 o 1) y de Ŝ_z. Si Ψ no es autofunción,
muestra la función resultante (Ŝ²Ψ, Ŝ_zΨ), su descomposición en singlete y triplete y las probabilidades de cada resultado de medida.
También indica si Ψ es simétrica o antisimétrica frente al intercambio de los electrones (principio de Pauli).

Se trabaja en unidades de ħ. El operador de espín no actúa sobre la parte espacial. Los espín-orbitales distintos son ortonormales.
Los resultados coinciden con los del cuaderno de Colab «Espin_dos_electrones».

Estructura: 1. Lectura de la entrada · 2. Física del espín · 3. Figuras · 4. Pruebas · 5. Interfaz Streamlit
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import streamlit as st
import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, parse_expr, standard_transformations

import quantum_lab_comun as qc
from quantum_lab_comun import COLORES

# =====================================================================
# 1. LECTURA DE LA ENTRADA
# =====================================================================
# =====================================================================================
#  Estado de dos electrones:  Ψ = Σ cₖ |φₐ σₐ ; φᵦ σᵦ⟩   (electrón 1 ; electrón 2)
#  Se guarda como diccionario {(orbital1, espín1, orbital2, espín2): coeficiente}.
# =====================================================================================
TRANSFORMACIONES = standard_transformations + (implicit_multiplication_application, convert_xor)
_KET_RE = re.compile(r"\|([^|<>]+)>")
_SPIN_RE = re.compile(r"(?i)^(.*?)(alpha|beta|up|down|[αβ])$")
_SLATER_RE = re.compile(r"(?i)slater\s*\(\s*([^,;()|<>]+?)\s*,\s*([^,;()|<>]+?)\s*\)")
LETRAS_L = "spdfghik"
_REALES = {1: {"x", "y", "z"}, 2: {"z2", "xz", "yz", "xy", "x2-y2"}}


@dataclass(frozen=True)
class Ket:
    """Ket de dos electrones, cada uno como (orbital, espín)."""
    orbital_1: str
    spin_1: str
    orbital_2: str
    spin_2: str

    @property
    def base(self):
        return (self.orbital_1, self.spin_1, self.orbital_2, self.spin_2)


def normalizar_orbital(texto):
    """
    Valida un orbital hidrogenoide y lo devuelve en forma canónica.
    Admite 1s, 2p, 2p0, 2p+1, 2p-1, 3d-2, 2pz (≡ 2p0), 2px, 2py, 3dxy, ...
    Reglas: n ≥ 1, 0 ≤ l ≤ n−1, |mₗ| ≤ l.
    """
    t = texto.strip().replace("−", "-").replace(" ", "")
    m = re.fullmatch(r"(?i)(\d+)([spdfghik])(.*)", t)
    if not m:
        raise ValueError(f"Orbital no reconocido: «{texto}». Use el formato n + letra + mₗ opcional, p. ej. 1s, 2p0, 3d+1.")
    n, l, resto = int(m.group(1)), LETRAS_L.index(m.group(2).lower()), m.group(3).lower()
    if n < 1:
        raise ValueError(f"Orbital «{texto}»: n debe ser ≥ 1.")
    if l >= n:
        raise ValueError(f"Orbital «{texto}» no existe: con n = {n} solo se permite l ≤ {n - 1}.")
    letra = LETRAS_L[l]
    if resto == "":
        return f"{n}{letra}"
    if re.fullmatch(r"[+-]?\d+", resto):
        ml = int(resto)
        if abs(ml) > l:
            raise ValueError(f"Orbital «{texto}» no existe: para l = {l} debe cumplirse |mₗ| ≤ {l}.")
        return f"{n}{letra}{ml:+d}" if ml != 0 else f"{n}{letra}0"
    if l in _REALES and resto in _REALES[l]:
        return f"{n}{letra}0" if (l == 1 and resto == "z") else f"{n}{letra}{resto}"
    raise ValueError(f"Orbital «{texto}»: la parte «{resto}» no es un mₗ válido para l = {l}.")


def normalizar_espin(valor):
    v = valor.strip().lower()
    if v in {"alpha", "up", "α"}:
        return "alpha"
    if v in {"beta", "down", "β"}:
        return "beta"
    raise ValueError(f"Espín no reconocido: «{valor}». Use α/β o alpha/beta.")


def _leer_electron(texto):
    texto = texto.strip()
    partes = [p for p in re.split(r"[,:\s]+", texto) if p]
    if len(partes) == 2:
        return normalizar_orbital(partes[0]), normalizar_espin(partes[1])
    m = _SPIN_RE.match(texto)
    if m and m.group(1).strip():
        return normalizar_orbital(m.group(1)), normalizar_espin(m.group(2))
    raise ValueError(f"No se pudo interpretar el electrón «{texto}». Use, por ejemplo, «1s,α» o «1sα».")


def leer_ket(contenido):
    """Convierte «orbital,espín;orbital,espín» en un Ket."""
    electrones = [p.strip() for p in contenido.split(";")]
    if len(electrones) != 2:
        electrones = [p.strip() for p in contenido.split(",")]
    if len(electrones) != 2:
        raise ValueError(f"El ket «{contenido}» debe tener exactamente dos electrones, separados por «;».")
    return Ket(*_leer_electron(electrones[0]), *_leer_electron(electrones[1]))


def preparar_texto(texto):
    """Limpia la entrada: «Ψ = », ⟩, √, Slater(...)."""
    t = texto.strip()
    if "=" in t:
        t = t.split("=", 1)[1]
    t = t.replace("⟩", ">").replace("〉", ">").replace("¦", "|").replace("−", "-")
    t = re.sub(r"√\s*(\d+(?:\.\d+)?)", r"sqrt(\1)", t)
    t = re.sub(r"√\s*\(", "sqrt(", t)
    return _SLATER_RE.sub(lambda m: f"(1/sqrt(2))*(|{m.group(1)};{m.group(2)}> - |{m.group(2)};{m.group(1)}>)", t)


def _coeficiente(texto, nombres):
    local = {"sqrt": sp.sqrt, "I": sp.I, "i": sp.I}
    local.update({nombre: sp.Symbol(nombre) for nombre in nombres})
    return parse_expr(texto, local_dict=local, transformations=TRANSFORMACIONES, evaluate=True)


def leer_estado(texto):
    """Combinación lineal de kets -> {base: coeficiente}. Cada ket se sustituye por un símbolo KET_k rodeado de espacios."""
    texto = preparar_texto(texto)
    coincidencias = list(_KET_RE.finditer(texto))
    if not coincidencias:
        raise ValueError("No se encontró ningún ket |...> en el estado.")
    kets = [leer_ket(m.group(1)) for m in coincidencias]
    simbolos = [f"KET_{k}" for k in range(len(kets))]
    reescrito = texto
    for m, s in reversed(list(zip(coincidencias, simbolos))):
        reescrito = reescrito[:m.start()] + f" {s} " + reescrito[m.end():]
    try:
        expr = sp.expand(sp.nsimplify(_coeficiente(reescrito, simbolos), rational=True))
    except Exception as error:
        raise ValueError(f"No se pudo interpretar la expresión de los coeficientes ({error}).") from None
    estado, reconstruido = {}, sp.Integer(0)
    for s, ket in zip(simbolos, kets):
        c = sp.simplify(expr.coeff(sp.Symbol(s)))
        reconstruido += c * sp.Symbol(s)
        if c != 0:
            estado[ket.base] = sp.simplify(estado.get(ket.base, 0) + c)
    if sp.simplify(expr - reconstruido) != 0:
        raise ValueError("La expresión debe ser lineal en los kets: no se permiten productos de kets ni términos sueltos.")
    return {b: c for b, c in estado.items() if c != 0}


# =====================================================================
# 2. FÍSICA DEL ESPÍN
# =====================================================================
# =====================================================================================
#  Un electrón: s = 1/2;  ŝ² α = ŝ² β = (3/4)ħ²;  ŝ_z α = +ħ/2 α,  ŝ_z β = −ħ/2 β.
#  Dos electrones:  Ŝ = ŝ₁ + ŝ₂ ,   Ŝ_z = ŝ₁z + ŝ₂z ,
#       Ŝ² = ŝ₁² + ŝ₂² + 2 ŝ₁·ŝ₂ = 3/2 + 2 ŝ₁zŝ₂z + ŝ₁₊ŝ₂₋ + ŝ₁₋ŝ₂₊      (en unidades de ħ²)
#  Sobre la base:  αα y ββ → 2 (triplete);  αβ → 1·αβ + βα  (el término ŝ₁₊ŝ₂₋ + ŝ₁₋ŝ₂₊ intercambia los espines).
#  Autovalores de Ŝ²: s(s+1)ħ² con s = 0 (singlete, 0) o s = 1 (triplete, 2ħ²).
#  Proyectores:  P_triplete = Ŝ²/2 ,  P_singlete = 1 − Ŝ²/2.
#  El operador de espín no actúa sobre la parte espacial.
# =====================================================================================


def _sumar(destino, base, c):
    destino[base] = sp.simplify(destino.get(base, 0) + c)
    if destino[base] == 0:
        del destino[base]


def combinar(a, b, ca=1, cb=1):
    """ca·a + cb·b para estados (diccionarios)."""
    out = {}
    for base, c in a.items():
        _sumar(out, base, ca * c)
    for base, c in b.items():
        _sumar(out, base, cb * c)
    return out


def escalar(a, k):
    return {base: sp.simplify(k * c) for base, c in a.items() if sp.simplify(k * c) != 0}


def aplicar_sz(estado):
    """Ŝ_z Ψ (en unidades de ħ)."""
    out = {}
    for base, c in estado.items():
        _, s1, _, s2 = base
        m = sp.Rational(1, 2) * ((1 if s1 == "alpha" else -1) + (1 if s2 == "alpha" else -1))
        _sumar(out, base, c * m)
    return out


def aplicar_s2(estado):
    """Ŝ² Ψ (en unidades de ħ²)."""
    out = {}
    for base, c in estado.items():
        o1, s1, o2, s2 = base
        _sumar(out, base, c * (2 if s1 == s2 else 1))
        if s1 != s2:                                   # ŝ₁₊ŝ₂₋ + ŝ₁₋ŝ₂₊ intercambia los espines
            _sumar(out, (o1, s2, o2, s1), c)
    return out


def intercambiar_electrones(estado):
    """Operador de intercambio P₁₂: el electrón 1 pasa a ser el 2 (orbital y espín)."""
    return {(o2, s2, o1, s1): c for (o1, s1, o2, s2), c in estado.items()}


def norma2(estado):
    """⟨Ψ|Ψ⟩ con la base ortonormal (kets distintos son ortogonales)."""
    return sp.simplify(sum(sp.Abs(c) ** 2 for c in estado.values()))


def autovalor(estado, resultado):
    """λ si resultado = λ·estado; None si no son proporcionales."""
    if not estado:
        raise ValueError("El estado no puede ser nulo.")
    if not resultado:
        return sp.Integer(0)
    if set(estado) != set(resultado):
        return None
    lam = None
    for base, c in estado.items():
        cand = sp.simplify(resultado[base] / c)
        if lam is None:
            lam = cand
        elif sp.simplify(cand - lam) != 0:
            return None
    return sp.simplify(lam)


def probabilidades(estado, partes):
    """Probabilidad de cada componente: ‖parte‖² / ‖Ψ‖². Devuelve None si hay coeficientes simbólicos."""
    if any(c.free_symbols for c in estado.values()):
        return None
    total = norma2(estado)
    return [sp.nsimplify(sp.simplify(norma2(p) / total)) for p in partes]


def prob_ms(estado):
    """Probabilidad de medir M_S = +1, 0, −1 (None si hay símbolos)."""
    if any(c.free_symbols for c in estado.values()):
        return None
    total = norma2(estado)
    p = {1: 0, 0: 0, -1: 0}
    for (_, s1, _, s2), c in estado.items():
        m = ((1 if s1 == "alpha" else -1) + (1 if s2 == "alpha" else -1)) // 2
        p[m] += sp.Abs(c) ** 2
    return {m: sp.nsimplify(sp.simplify(v / total)) for m, v in p.items()}


def simetria_intercambio(estado):
    """'antisimétrica', 'simétrica' o 'ninguna' frente al intercambio de los dos electrones."""
    inter = intercambiar_electrones(estado)
    if not combinar(estado, inter, 1, 1):
        return "antisimétrica"
    if not combinar(estado, inter, 1, -1):
        return "simétrica"
    return "ninguna"


# ------------------------- Formato -------------------------
_SIMB = {"alpha": "α", "beta": "β"}


def texto_coef(c):
    """Coeficiente legible: 1/√2, √3/2, −i, ..."""
    c = sp.simplify(c)
    if c.is_real and c != 0 and not c.free_symbols:
        c2 = sp.nsimplify(c ** 2)
        if c2.is_Rational and not c.is_Rational:
            signo = "-" if c < 0 else ""
            p, q = c2.p, c2.q
            raiz = lambda k: "1" if k == 1 else (f"√{k}" if k < 10 ** 6 else f"√({k})")
            if p == 1:
                return f"{signo}1/{raiz(q)}"
            return f"{signo}{raiz(p)}/{raiz(q)}" if q != 1 else f"{signo}{raiz(p)}"
    s = sp.sstr(c).replace("**", "^").replace("sqrt", "√").replace("I", "i").replace("*", "·")
    return s


def texto_ket(base):
    o1, s1, o2, s2 = base
    return f"|{o1},{_SIMB[s1]};{o2},{_SIMB[s2]}⟩"


def texto_estado(estado):
    """Combinación lineal legible, con orden determinista."""
    if not estado:
        return "0"
    out = ""
    for k, (base, c) in enumerate(sorted(estado.items(), key=lambda kv: kv[0])):
        c = sp.simplify(c)
        neg = c.could_extract_minus_sign()
        mag = sp.simplify(-c if neg else c)
        signo = ("-" if neg else "") if k == 0 else (" - " if neg else " + ")
        if mag == 1:
            cuerpo = texto_ket(base)
        else:
            tc = texto_coef(mag)
            cuerpo = f"({tc}){texto_ket(base)}" if re.search(r"[/√+\-·^]", tc) or "i" in tc else f"{tc}{texto_ket(base)}"
        out += signo + cuerpo
    return out.replace("-", "−")


def texto_num(x):
    return str(sp.nsimplify(x)).replace("**", "^")


def analizar(texto):
    """Calcula todo lo pedido y lo devuelve en un diccionario (el informe solo lo imprime)."""
    psi = leer_estado(texto)
    r = {"psi": psi, "norma2": norma2(psi)}
    r["sz_psi"], r["s2_psi"] = aplicar_sz(psi), aplicar_s2(psi)
    r["sz"], r["s2"] = autovalor(psi, r["sz_psi"]), autovalor(psi, r["s2_psi"])
    r["triplete"] = escalar(r["s2_psi"], sp.Rational(1, 2))
    r["singlete"] = combinar(psi, r["triplete"], 1, -1)
    r["p_s2"] = probabilidades(psi, [r["singlete"], r["triplete"]])
    r["p_ms"] = prob_ms(psi)
    r["simetria"] = simetria_intercambio(psi)
    if r["s2"] is not None:
        for s in (0, 1):
            if sp.simplify(r["s2"] - s * (s + 1)) == 0:
                r["s"] = s
    return r


# =====================================================================
# 3. FIGURAS
# =====================================================================
def figura_probabilidades(r: dict):
    """Probabilidades de los resultados de medir Ŝ² (singlete/triplete) y Ŝ_z (M_S = −1, 0, +1)."""
    fig, (a1, a2) = qc.rejilla(1, 2, (11, 4.2), (7, 7.5), constrained_layout=True)
    p = [float(x) for x in r["p_s2"]]
    barras = a1.bar(["S² = 0\n(singlete)", "S² = 2ħ²\n(triplete)"], p, color=[COLORES["onda"], COLORES["energia"]], width=0.55)
    a1.set_ylim(0, 1.12)
    a1.set_ylabel("probabilidad")
    a1.set_title("Medida de Ŝ²")
    pm = r["p_ms"]
    ms = [-1, 0, 1]
    a2.bar([f"M_S = {m:+d}" if m else "M_S = 0" for m in ms], [float(pm[m]) for m in ms], color=COLORES["densidad"], width=0.55)
    a2.set_ylim(0, 1.12)
    a2.set_title("Medida de Ŝ_z")
    for ax, vals in ((a1, p), (a2, [float(pm[m]) for m in ms])):
        for i, v in enumerate(vals):
            ax.text(i, v + 0.025, f"{v:.3f}", ha="center", fontsize=10)
        ax.grid(alpha=0.25, axis="y")
        ax.set_axisbelow(True)
    return fig


# =====================================================================
# 4. PRUEBAS
# =====================================================================
def ejecutar_pruebas() -> qc.RegistroPruebas:
    r = qc.RegistroPruebas("Espín de dos electrones")
    an = analizar
    S = sp.Rational
    # A) Verificación independiente: matrices de Pauli en el espacio de espín 4×4
    sx, sy, sz_ = (np.array(m, dtype=complex) / 2 for m in ([[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]))
    I2 = np.eye(2)
    S2_mat = sum(np.kron(s, I2) @ np.kron(s, I2) + np.kron(I2, s) @ np.kron(I2, s) + 2 * np.kron(s, I2) @ np.kron(I2, s) for s in (sx, sy, sz_))
    Sz_mat = np.kron(sz_, I2) + np.kron(I2, sz_)
    r.comprobar("Matriz S² (Pauli): autovalores {0, 2, 2, 2}", np.allclose(sorted(np.linalg.eigvalsh(S2_mat)), [0, 2, 2, 2]))
    orden = [("alpha", "alpha"), ("alpha", "beta"), ("beta", "alpha"), ("beta", "beta")]
    rng = np.random.default_rng(7)
    ok_s2 = ok_sz = True
    for _ in range(25):
        v = rng.normal(size=4) + 1j * rng.normal(size=4)
        est = {("1s", a, "2s", b): sp.Float(v[k].real) + sp.I * sp.Float(v[k].imag) for k, (a, b) in enumerate(orden)}
        for oper, mat in ((aplicar_s2, S2_mat), (aplicar_sz, Sz_mat)):
            res = oper(est)
            w = np.array([complex(res.get(("1s", a, "2s", b), 0)) for a, b in orden])
            if not np.allclose(w, mat @ v, atol=1e-9):
                ok_s2 = ok_s2 and oper is not aplicar_s2
                ok_sz = ok_sz and oper is not aplicar_sz
    r.comprobar("Ŝ² = matriz de Pauli (25 estados aleatorios)", ok_s2)
    r.comprobar("Ŝ_z = matriz de Pauli (25 estados aleatorios)", ok_sz)
    # B) Casos conocidos
    x = an("(|1s,α;2s,β> - |1s,β;2s,α>)/√2")
    r.comprobar("Singlete de espín: S² = 0, S_z = 0", x["s2"] == 0 and x["sz"] == 0 and x["s"] == 0)
    for nombre, ket, m in (("triplete M = +1", "|1sα;2sα>", 1), ("triplete M = −1", "|1sβ;2sβ>", -1)):
        x = an(ket)
        r.comprobar(f"{nombre}: S² = 2, S_z = {m}", x["s2"] == 2 and x["sz"] == m and x["s"] == 1)
    x = an("(|1sα;2sβ> + |1sβ;2sα>)/sqrt(2)")
    r.comprobar("Triplete M = 0: S² = 2, S_z = 0", x["s2"] == 2 and x["sz"] == 0)
    x = an("|1sα;2sβ>")
    r.comprobar("|1sα;2sβ>: S_z = 0 y NO es autofunción de S²", x["sz"] == 0 and x["s2"] is None)
    r.comprobar("   …50 % singlete y 50 % triplete", x["p_s2"] == [S(1, 2), S(1, 2)], str(x["p_s2"]))
    r.comprobar("   …con S²Ψ = Ψ + |1sβ;2sα>", x["s2_psi"] == {("1s", "alpha", "2s", "beta"): 1, ("1s", "beta", "2s", "alpha"): 1})
    x = an("|1sα;2sα> + |1sβ;2sβ>")
    r.comprobar("αα + ββ: S² = 2, no es autofunción de S_z", x["s2"] == 2 and x["sz"] is None)
    r.comprobar("   …M_S = ±1 con probabilidad 1/2", x["p_ms"] == {1: S(1, 2), 0: 0, -1: S(1, 2)}, str(x["p_ms"]))
    x = an("Slater(1sα, 2sβ)")
    r.comprobar("Slater(1sα,2sβ): antisimétrica, S_z = 0, no autofunción de S²",
                x["simetria"] == "antisimétrica" and x["sz"] == 0 and x["s2"] is None)
    r.comprobar("   …50 % singlete y 50 % triplete", x["p_s2"] == [S(1, 2), S(1, 2)])
    x = an("Slater(1sα, 1sβ)")
    r.comprobar("He 1s² = Slater(1sα,1sβ): S² = 0, S_z = 0, antisimétrica", x["s2"] == 0 and x["sz"] == 0 and x["simetria"] == "antisimétrica")
    x = an("(|1sα;2sα> - |2sα;1sα>)/√2")
    r.comprobar("Triplete con parte espacial antisimétrica: S² = 2, S_z = 1, antisimétrica",
                x["s2"] == 2 and x["sz"] == 1 and x["simetria"] == "antisimétrica")
    x = an("(|1sα;2sβ> - |1sβ;2sα> + |2sα;1sβ> - |2sβ;1sα>)/2")
    r.comprobar("Singlete 1s2s totalmente antisimétrico: S² = 0", x["s2"] == 0 and x["simetria"] == "antisimétrica")
    r.comprobar("Dos electrones en 1sα: simétrica (viola Pauli)", an("|1sα;1sα>")["simetria"] == "simétrica")
    # C) Lectura de la entrada
    ref = an("(|1sα;2sβ> - |1sβ;2sα>)/sqrt(2)")["psi"]
    for variante in ("1/√2 (|1s,alpha;2s,beta> - |1s,beta;2s,alpha>)", "Ψ = (|1sα;2sβ⟩ - |1sβ;2sα⟩)*2^(-1/2)",
                     "(|1s up;2s down> - |1s down;2s up>)/2^(1/2)", "0.5*sqrt(2)*(|1sα;2sβ> - |1sβ;2sα>)"):
        r.comprobar(f"Variante de escritura: {variante[:42]}", an(variante)["psi"] == ref)
    r.comprobar("Coeficientes simbólicos c, d", len(an("c|1sα;2sβ> + d|1sβ;2sα>")["psi"]) == 2)
    x = an("i|1sα;2sα>")
    r.comprobar("Coeficiente imaginario: autovalores sin cambio", x["s2"] == 2 and x["sz"] == 1)
    r.comprobar("2pz ≡ 2p0 y 2p−1 se acepta", normalizar_orbital("2pz") == "2p0" and normalizar_orbital("2p−1") == "2p-1")
    for malo in ("1p", "2p+2", "3f", "0s", "2q"):
        r.comprobar_error(f"Rechaza el orbital {malo}", normalizar_orbital, malo)
    for malo in ("|1sα>", "1sα;2sβ", "|1sγ;2sβ>", "|1sα;2sβ>*|1sα;2sα>"):
        r.comprobar_error(f"Rechaza la entrada {malo}", analizar, malo, tipo=(ValueError, SyntaxError, TypeError))
    return r


# =====================================================================
# 5. INTERFAZ STREAMLIT
# =====================================================================
VALORES_INICIALES = {"esp_psi": "(|1s,α;2s,β⟩ - |1s,β;2s,α⟩)/√2"}
DEMOS = {
    "Singlete de espín (1s2s)": {"esp_psi": "(|1s,α;2s,β⟩ - |1s,β;2s,α⟩)/√2"},
    "Triplete M = +1": {"esp_psi": "|1sα;2sα⟩"},
    "Triplete M = 0": {"esp_psi": "(|1sα;2sβ⟩ + |1sβ;2sα⟩)/√2"},
    "Producto |1sα;2sβ⟩ (mezcla)": {"esp_psi": "|1sα;2sβ⟩"},
    "Helio fundamental 1s² (Slater)": {"esp_psi": "Slater(1sα, 1sβ)"},
    "Determinante de Slater 1s2s": {"esp_psi": "Slater(1sα, 2sβ)"},
    "αα + ββ": {"esp_psi": "|1sα;2sα⟩ + |1sβ;2sβ⟩"},
    "Con orbitales 2p0 y 3d+1": {"esp_psi": "(|2p0,α;3d+1,β⟩ - |2p0,β;3d+1,α⟩)/√2"},
}

GUIA = [
    {"titulo": "Singlete y triplete",
     "objetivo": "Comprobar que S² solo toma los valores 0 y 2ħ² para dos electrones.",
     "pasos": ["Cargar el singlete y leer S².", "Cargar el triplete M = 0 y leer S².", "Probar |1sα;2sα⟩ y |1sβ;2sβ⟩."],
     "pregunta": "¿Qué valores de S_z y S² tiene cada triplete?",
     "resultado": "Singlete: S² = 0 (s = 0). Tripletes: S² = 2ħ² = s(s+1)ħ² con s = 1, y M_S = +1, 0, −1 según los espines (αα, αβ+βα, ββ).",
     "pestana": "Resultados", "config": {"esp_psi": "(|1sα;2sβ⟩ + |1sβ;2sα⟩)/√2"}},
    {"titulo": "Un producto no es autofunción de S²",
     "objetivo": "Ver que |1sα;2sβ⟩ es autofunción de S_z pero no de S², y cómo se reparte entre singlete y triplete.",
     "pasos": ["Cargar el producto |1sα;2sβ⟩.", "Leer la función resultante S²Ψ.", "Ver la descomposición y las probabilidades."],
     "pregunta": "¿Con qué probabilidad se mide S² = 0 en |1sα;2sβ⟩?",
     "resultado": "S²Ψ = Ψ + |1sβ;2sα⟩, que no es proporcional a Ψ. Ψ = (singlete + triplete M = 0)/√2: 50 % de probabilidad de medir S² = 0 y 50 % de medir 2ħ².",
     "pestana": "Resultados", "config": {"esp_psi": "|1sα;2sβ⟩"}},
    {"titulo": "El determinante de Slater",
     "objetivo": "Comparar una función antisimétrica con una que no lo es.",
     "pasos": ["Cargar Slater(1sα, 1sβ) (helio fundamental).", "Cargar Slater(1sα, 2sβ).", "Mirar el aviso de simetría de cada una."],
     "pregunta": "¿Por qué Slater(1sα, 2sβ) no es autofunción de S² si es antisimétrica?",
     "resultado": "El principio de Pauli solo exige antisimetría global. Slater(1sα,2sβ) mezcla en partes iguales el singlete espacial-simétrico y el triplete espacial-antisimétrico; "
                  "el helio 1s² es un singlete puro porque ambos electrones comparten el orbital espacial.",
     "pestana": "Resultados", "config": {"esp_psi": "Slater(1sα, 2sβ)"}},
    {"titulo": "αα + ββ: S² definido, S_z no",
     "objetivo": "Encontrar una función con S² bien definido pero M_S indefinido.",
     "pasos": ["Cargar la configuración.", "Leer S² y S_z.", "Ver la probabilidad de cada M_S."],
     "pregunta": "¿Por qué S² = 2ħ² aunque S_z no tenga un valor definido?",
     "resultado": "Es combinación de dos miembros del triplete (M = +1 y −1): todos tienen S² = 2ħ². S_z da +ħ o −ħ con probabilidad 1/2.",
     "pestana": "Resultados", "config": {"esp_psi": "|1sα;2sα⟩ + |1sβ;2sβ⟩"}},
]

PREGUNTAS = [
    {"enunciado": "Para dos electrones, los posibles valores de S² son…",
     "opciones": ["0 y ħ²", "0 y 2ħ²", "ħ² y 2ħ²", "(3/4)ħ² y (15/4)ħ²"], "correcta": 1,
     "explicacion": "s = 0 (singlete) o s = 1 (triplete): s(s+1)ħ² = 0 o 2ħ²."},
    {"enunciado": "¿Cuántos estados tiene el triplete?",
     "opciones": ["1", "2", "3", "4"], "correcta": 2, "explicacion": "2s + 1 = 3, con M_S = +1, 0, −1."},
    {"enunciado": "Ŝ_z |1sα;2sα⟩ es igual a…",
     "opciones": ["0", "ħ/2 |1sα;2sα⟩", "ħ |1sα;2sα⟩", "−ħ |1sα;2sα⟩"], "correcta": 2,
     "explicacion": "Cada electrón con espín α aporta +ħ/2: M_S = 1."},
    {"enunciado": "El producto |1sα;2sβ⟩ es autofunción de…",
     "opciones": ["Ŝ_z y Ŝ²", "Ŝ_z pero no Ŝ²", "Ŝ² pero no Ŝ_z", "ninguno de los dos"], "correcta": 1,
     "explicacion": "M_S = 0 está definido, pero Ŝ² mezcla αβ con βα: la función es mitad singlete, mitad triplete M = 0."},
    {"enunciado": "El singlete de espín (αβ − βα)/√2 es…",
     "opciones": ["simétrico en el espín", "antisimétrico en el espín", "autofunción con S² = 2ħ²", "autofunción con M_S = 1"], "correcta": 1,
     "explicacion": "Cambia de signo al intercambiar los espines; S² = 0 y M_S = 0. Su parte espacial debe ser simétrica para que Ψ completa sea antisimétrica."},
    {"enunciado": "El principio de Pauli exige que la función completa de dos electrones sea…",
     "opciones": ["simétrica", "antisimétrica", "real", "autofunción de Ŝ²"], "correcta": 1,
     "explicacion": "Postulado de antisimetría: Ψ cambia de signo al intercambiar las coordenadas (espaciales y de espín) de dos electrones."},
    {"enunciado": "El helio en su estado fundamental 1s² es…",
     "opciones": ["un triplete", "un singlete", "una mezcla 50/50", "no tiene espín"], "correcta": 1,
     "explicacion": "Ambos electrones están en 1s con espines opuestos: Slater(1sα, 1sβ), antisimétrico con S = 0."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("esp_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


def _pestana_resultados(texto: str):
    try:
        r = analizar(texto)
    except (ValueError, SyntaxError, TypeError) as error:
        qc.error(error)
        return
    psi = r["psi"]
    simb = any(c.free_symbols for c in psi.values())
    qc.seccion("Estado de entrada")
    st.code("Ψ = " + texto_estado(psi), language=None)
    s2, sz = r["s2"], r["sz"]
    s = r.get("s")
    qc.metricas([
        ("⟨Ψ|Ψ⟩", texto_num(r["norma2"]), "Norma al cuadrado; los autovalores no dependen de ella"),
        ("Ŝ_z", f"{texto_num(sz)} ħ" if sz is not None else "no es autofunción", "Autovalor M_S ħ"),
        ("Ŝ²", f"{texto_num(s2)} ħ²" if s2 is not None else "no es autofunción", "s(s+1) ħ²"),
        ("Espín total s", str(s) if s is not None else "—", "0 = singlete, 1 = triplete"),
        ("|S| = √(s(s+1)) ħ", ("0" if s == 0 else "√2 ħ ≈ 1.4142 ħ") if s is not None else "—"),
        ("Multiplicidad 2s+1", str(2 * s + 1) if s is not None else "—"),
        ("Intercambio de electrones", r["simetria"], "Principio de Pauli: debe ser antisimétrica"),
    ], columnas=4)
    if r["simetria"] == "antisimétrica":
        qc.nota("Ψ es antisimétrica frente al intercambio de los dos electrones: cumple el principio de Pauli.")
    elif r["simetria"] == "simétrica":
        qc.aviso("Ψ es simétrica frente al intercambio de los electrones: NO cumple el postulado de antisimetría; no describe un estado físico de dos electrones.")
    else:
        qc.aviso("Ψ no es ni simétrica ni antisimétrica frente al intercambio: no cumple Pauli tal como está escrita. Para antisimetrizarla use "
                 "un determinante de Slater, p. ej. Slater(1sα, 2sβ). El valor de S² se calcula igualmente.")
    if not simb and sp.simplify(r["norma2"] - 1) != 0:
        qc.nota(f"Ψ no está normalizada (⟨Ψ|Ψ⟩ = {texto_num(r['norma2'])}): las probabilidades se calculan ya normalizadas.")
    if simb:
        qc.nota("Hay coeficientes simbólicos: los autovalores se calculan igualmente, pero no las probabilidades.")
    qc.seccion("Componente z")
    if sz is not None:
        st.success(f"Ψ es autofunción de Ŝ_z con autovalor M_S ħ = {texto_num(sz)} ħ.")
    else:
        st.warning("Ψ no es autofunción de Ŝ_z. Función resultante:")
        st.code("Ŝ_z Ψ = " + texto_estado(r["sz_psi"]) + "      (unidades de ħ)", language=None)
    qc.seccion("Espín total")
    if s2 is not None:
        st.success(f"Ψ es autofunción de Ŝ² con autovalor {texto_num(s2)} ħ²"
                   + (f" (s = {s}, {'singlete' if s == 0 else 'triplete'})." if s is not None else "."))
    else:
        st.warning("Ψ no es autofunción de Ŝ². Función resultante y descomposición en singlete (S² = 0) y triplete (S² = 2ħ²):")
        st.code("Ŝ² Ψ = " + texto_estado(r["s2_psi"]) + "      (unidades de ħ²)\n"
                "singlete = " + texto_estado(r["singlete"]) + "\ntriplete = " + texto_estado(r["triplete"]), language=None)
    if r["p_s2"] is not None:
        qc.seccion("Probabilidades de medida")
        qc.tabla_libre([{"Resultado": "S² = 0 (singlete)", "Probabilidad": texto_num(r["p_s2"][0])},
                        {"Resultado": "S² = 2ħ² (triplete)", "Probabilidad": texto_num(r["p_s2"][1])}] +
                       [{"Resultado": ("M_S = 0" if m == 0 else f"M_S = {m:+d}"), "Probabilidad": texto_num(p)}
                        for m, p in r["p_ms"].items() if p != 0], numericas=("Probabilidad",))
        qc.mostrar_pyplot(figura_probabilidades(r), archivo="espin_probabilidades.png")
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- Ŝ² = ŝ₁² + ŝ₂² + 2 ŝ₁·ŝ₂ solo toma los valores 0 y 2ħ²: singlete (s = 0) y triplete (s = 1).\n"
            "- Un producto |φₐ α; φᵦ β⟩ fija M_S, pero no S²: mezcla singlete y triplete M = 0.\n"
            "- Ŝ_z y Ŝ² conmutan, así que puede haber estados con ambos valores definidos; el espín no actúa sobre la parte espacial.\n"
            "- Si Ψ no es autofunción, medir S² da 0 o 2ħ² con las probabilidades indicadas y tras la medida el sistema queda en esa componente.")


def interfaz() -> None:
    """Página completa del simulador 8 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 08", "Espín total de dos electrones",
                         "Autovalores de Ŝ² y Ŝ_z de una función de dos electrones escrita en notación de Dirac con espín-orbitales hidrogenoides.")
    qc.enlace_teoria("espin")
    qc.ficha_simulador(
        "Calcular S² y S_z de una función de onda de dos electrones y, si no es autofunción, dar la función resultante.",
        r"\begin{gathered}\hat S^2\,\Psi=s(s+1)\hbar^2\,\Psi,\quad s=0,1\\[4pt]\hat S_z\,\Psi=M_S\hbar\,\Psi\end{gathered}",
        [("Ψ", "función de dos electrones"), ("α, β", "espín arriba y abajo"), ("s", "número cuántico de espín total"),
         ("M_S", "proyección sobre z")],
        "Dos electrones con espín-orbitales hidrogenoides ortonormales; unidades de ħ; el espín no actúa sobre la parte espacial.")
    with st.container(border=True):
        qc.seccion("Función de onda Ψ (notación de Dirac)")
        st.text_input("Ψ", key="esp_psi", help="Cada ket es |orbital,espín ; orbital,espín⟩ (electrón 1 ; electrón 2). Admite 1/√2, 2^(-1/2), i, "
                      "coeficientes simbólicos y Slater(1sα, 2sβ).")
        st.caption("Orbitales: 1s, 2s, 2p0, 2p+1, 2p−1, 3d+2… (n, l y mₗ). Espín: α, β (o alpha, beta).")
        qc.pie_de_parametros(DEMOS, "esp_demo", _aplicar_demo, VALORES_INICIALES, "esp_reset")
    tabs = st.tabs(["Resultados", "Guía de práctica", "Autoevaluación", "Pruebas numéricas"])
    with tabs[0]:
        _pestana_resultados(st.session_state["esp_psi"])
    with tabs[1]:
        qc.guia_practica(GUIA, "esp")
    with tabs[2]:
        qc.autoevaluacion(PREGUNTAS, "esp")
    with tabs[3]:
        qc.boton_pruebas(ejecutar_pruebas, "esp_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Espín de dos electrones", ":material/science:", "espin_electrones.py")
