"""
efecto_fotoelectrico.py — QUANTUM LAB · Simulador 04: efecto fotoeléctrico
===========================================================================

Adaptado del simulador de consola «Efecto_Fotoelectrico_Simulacion.ipynb» al formato de QUANTUM LAB
(misma física, interfaz interactiva, pruebas numéricas y ampliaciones).

Ecuación de Einstein (1905):

    E_fotón = hν = hc/λ
    K_max   = hν − Φ          si hν ≥ Φ          (si hν < Φ no hay emisión y K_max = 0)
    ν₀      = Φ/h,  λ₀ = hc/Φ                    (umbral)
    K_max   = ½ mₑ v_max²   ⇒   v_max = √(2K_max/mₑ)
    eV₀     = K_max                              (potencial de frenado)

Ampliaciones respecto al cuaderno original:
  * corriente fotoeléctrica en función de la potencia luminosa (la intensidad cambia el NÚMERO de
    electrones, no su energía máxima) y curva corriente–voltaje con el potencial de frenado;
  * comparación de metales (rectas paralelas de pendiente h);
  * «experimento de Millikan» simulado: medida de V₀ para las líneas de una lámpara de mercurio y ajuste
    lineal para DETERMINAR h y Φ, con ruido de medida opcional.

Estructura: 1. Física · 2. Figuras · 3. Pruebas · 4. Interfaz Streamlit
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import streamlit as st
from scipy import constants as const

import quantum_lab_comun as qc
from quantum_lab_comun import COLORES

# =====================================================================
# 1. FÍSICA
# =====================================================================
H = const.h                      # J·s
C = const.c                      # m/s
E = const.e                      # C   (1 eV = E julios)
M_E = const.m_e                  # kg
H_EV = H / E                     # eV·s

# Funciones de trabajo aproximadas (eV). Dependen de la cara cristalina y del estado de la superficie;
# los cinco primeros son los del cuaderno original.
METALES = {
    "Cesio": 2.14, "Potasio": 2.30, "Sodio": 2.28, "Zinc": 4.30, "Aluminio": 4.08,
    "Litio": 2.93, "Calcio": 2.87, "Plata": 4.26, "Cobre": 4.65, "Oro": 5.10, "Platino": 5.65,
}
PERSONALIZADO = "Personalizado"

# Líneas de una lámpara de mercurio (nm), las del experimento clásico de Millikan.
LINEAS_MERCURIO = [365.02, 404.66, 435.83, 546.07, 576.96]

LAMBDA_MIN, LAMBDA_MAX = 50.0, 5000.0     # nm admitidos
PHI_MAX = 10.0                            # eV


@dataclass(frozen=True)
class ParametrosFoto:
    metal: str
    phi: float                # eV
    frecuencia: float         # Hz
    potencia: float           # W (potencia luminosa que incide)
    eficiencia: float         # fracción 0–1 (electrones por fotón absorbido)

    @property
    def longitud(self) -> float:
        return C / self.frecuencia


def validar_parametros_foto(metal, phi_personal, modo, valor, potencia_mw=1.0, eficiencia_pct=10.0) -> ParametrosFoto:
    """`modo` = 'longitud' (valor en nm) o 'frecuencia' (valor en Hz)."""
    if metal == PERSONALIZADO:
        phi = qc.positivo_finito(phi_personal, "La función de trabajo Φ [eV]")
        if phi > PHI_MAX:
            raise ValueError(f"La función de trabajo debe ser como mucho {PHI_MAX} eV (recibido: {phi}).")
    elif metal in METALES:
        phi = METALES[metal]
    else:
        raise ValueError(f"Metal desconocido: {metal!r}.")
    if modo == "longitud":
        lam = qc.positivo_finito(valor, "La longitud de onda λ [nm]")
        if not LAMBDA_MIN <= lam <= LAMBDA_MAX:
            raise ValueError(f"La longitud de onda debe estar entre {LAMBDA_MIN:g} y {LAMBDA_MAX:g} nm (recibido: {lam:g}).")
        frecuencia = C / (lam * 1e-9)
    elif modo == "frecuencia":
        frecuencia = qc.positivo_finito(valor, "La frecuencia ν [Hz]")
        lam = C / frecuencia * 1e9
        if not LAMBDA_MIN <= lam <= LAMBDA_MAX:
            raise ValueError(f"La frecuencia debe corresponder a λ entre {LAMBDA_MIN:g} y {LAMBDA_MAX:g} nm "
                             f"(≈ {C / (LAMBDA_MAX * 1e-9):.3g} – {C / (LAMBDA_MIN * 1e-9):.3g} Hz).")
    else:
        raise ValueError("El modo de entrada debe ser 'longitud' o 'frecuencia'.")
    try:
        potencia = float(potencia_mw)
    except (TypeError, ValueError):
        raise ValueError(f"La potencia luminosa debe ser un número (recibido: {potencia_mw!r}).")
    if not np.isfinite(potencia) or potencia < 0:
        raise ValueError(f"La potencia luminosa debe ser ≥ 0 (recibido: {potencia_mw}).")
    try:
        eficiencia = float(eficiencia_pct)
    except (TypeError, ValueError):
        raise ValueError(f"La eficiencia cuántica debe ser un número (recibido: {eficiencia_pct!r}).")
    if not 0 <= eficiencia <= 100:
        raise ValueError(f"La eficiencia cuántica debe estar entre 0 y 100 % (recibido: {eficiencia_pct}).")
    return ParametrosFoto(metal, phi, frecuencia, potencia * 1e-3, eficiencia / 100.0)


def energia_foton_ev(frecuencia):
    """E = hν  [eV]."""
    return H_EV * np.asarray(frecuencia, dtype=float)


def frecuencia_umbral(phi_ev: float) -> float:
    """ν₀ = Φ/h  [Hz]."""
    return phi_ev / H_EV


def longitud_umbral_nm(phi_ev: float) -> float:
    """λ₀ = hc/Φ  [nm]."""
    return H * C / (phi_ev * E) * 1e9


def energia_cinetica_maxima(frecuencia, phi_ev: float):
    """K_max = máx(hν − Φ, 0)  [eV]."""
    return np.maximum(energia_foton_ev(frecuencia) - phi_ev, 0.0)


def velocidad_maxima(kmax_ev: float) -> float:
    """v_max = √(2K_max/mₑ)  [m/s] (no relativista: K_max ≪ mₑc² ≈ 511 keV)."""
    return float(np.sqrt(2.0 * max(float(kmax_ev), 0.0) * E / M_E))


def potencial_frenado(kmax_ev: float) -> float:
    """V₀ = K_max/e  [V]  (numéricamente igual a K_max en eV)."""
    return float(kmax_ev)


def flujo_fotones(potencia_w: float, frecuencia: float) -> float:
    """Fotones por segundo: N = P/(hν)."""
    return potencia_w / (H * frecuencia)


def corriente_saturacion(p: ParametrosFoto) -> float:
    """I_sat = η·e·N  si hν ≥ Φ; 0 si no hay emisión  [A]."""
    if energia_foton_ev(p.frecuencia) < p.phi:
        return 0.0
    return p.eficiencia * E * flujo_fotones(p.potencia, p.frecuencia)


def corriente_voltaje(voltajes, i_sat: float, kmax_ev: float):
    """
    Modelo simplificado de la característica I–V de una fotocélula: con V ≥ 0 se recogen todos los
    electrones (saturación); con V < 0 solo llegan los que tienen K > e|V|. Suponiendo energías repartidas
    uniformemente entre 0 y K_max:  I = I_sat (1 − e|V|/K_max), que se anula en V = −V₀.
    """
    v = np.asarray(voltajes, dtype=float)
    if kmax_ev <= 0 or i_sat <= 0:
        return np.zeros_like(v)
    return np.where(v >= 0, i_sat, i_sat * np.clip(1.0 + v / kmax_ev, 0.0, 1.0))


def calcular_foto(p: ParametrosFoto) -> dict:
    """Todos los resultados de la radiación seleccionada sobre el metal elegido."""
    e_foton = float(energia_foton_ev(p.frecuencia))
    kmax = float(energia_cinetica_maxima(p.frecuencia, p.phi))
    lam_nm = p.longitud * 1e9
    return {
        "frecuencia": p.frecuencia, "longitud_nm": lam_nm,
        "energia_foton_ev": e_foton, "energia_foton_j": e_foton * E,
        "nu0": frecuencia_umbral(p.phi), "lambda0_nm": longitud_umbral_nm(p.phi),
        "kmax_ev": kmax, "kmax_j": kmax * E, "vmax": velocidad_maxima(kmax), "v0": potencial_frenado(kmax),
        "emision": e_foton >= p.phi, "flujo": flujo_fotones(p.potencia, p.frecuencia),
        "i_sat": corriente_saturacion(p), "region": qc.region_espectral(lam_nm),
        "region_umbral": qc.region_espectral(longitud_umbral_nm(p.phi)),
    }


def experimento_millikan(phi_ev: float, longitudes_nm, ruido_mv: float = 0.0, semilla: int = 1) -> dict:
    """
    Simula la medida del potencial de frenado V₀ para varias longitudes de onda y ajusta la recta
    V₀ = (h/e)ν − Φ/e por mínimos cuadrados. Devuelve los datos, el ajuste y h, Φ estimados con su
    incertidumbre (a partir de la covarianza del ajuste). Las líneas por debajo del umbral se descartan.
    """
    lam = np.asarray(longitudes_nm, dtype=float)
    nu = C / (lam * 1e-9)
    v0 = energia_foton_ev(nu) - phi_ev                     # V₀ en voltios (K_max en eV)
    validos = v0 > 0
    nu, lam, v0 = nu[validos], lam[validos], v0[validos]
    rng = np.random.default_rng(int(semilla))
    medidos = v0 + rng.normal(0.0, ruido_mv * 1e-3, size=v0.size) if ruido_mv > 0 else v0.copy()
    res = {"nu": nu, "lam": lam, "v0_ideal": v0, "v0": medidos, "n": int(nu.size)}
    if nu.size < 2:
        res.update(ajuste=False)
        return res
    if ruido_mv > 0:
        # σ de cada medida es conocido: covarianza «no escalada» con pesos 1/σ (no se estima σ con 2–3 puntos)
        sigma = ruido_mv * 1e-3
        (pend, orden), cov = np.polyfit(nu, medidos, 1, w=np.full(nu.size, 1.0 / sigma), cov="unscaled")
    else:
        (pend, orden), cov = np.polyfit(nu, medidos, 1), np.zeros((2, 2))
    h_est = pend * E
    phi_est = -orden
    res.update(ajuste=True, pendiente=pend, ordenada=orden,
               h=h_est, h_err=float(np.sqrt(max(cov[0, 0], 0.0))) * E,
               phi=phi_est, phi_err=float(np.sqrt(max(cov[1, 1], 0.0))),
               error_h_rel=abs(h_est - H) / H, nu0=-orden / pend)
    return res


# =====================================================================
# 2. FIGURAS
# =====================================================================
ESCALA_NU = 1e14          # las frecuencias se muestran en unidades de 10¹⁴ Hz


def figura_experimento(p: ParametrosFoto, d: dict):
    """K_max frente a ν (con el umbral y la radiación elegida) y la característica corriente–voltaje."""
    fig, (ax, ax2) = qc.rejilla(1, 2, (16, 5.6), constrained_layout=True)
    nu0 = d["nu0"]
    nu_max = max(2.2 * nu0, 1.15 * p.frecuencia)
    nus = np.linspace(0.35 * nu0, nu_max, 800)
    kmax = energia_cinetica_maxima(nus, p.phi)
    x = nus / ESCALA_NU
    ax.axvspan(x[0], nu0 / ESCALA_NU, color=COLORES["energia"], alpha=0.10, label="sin emisión")
    ax.axvspan(nu0 / ESCALA_NU, x[-1], color=COLORES["cinetica"], alpha=0.07, label="con emisión")
    ax.plot(x, energia_foton_ev(nus) - p.phi, color=COLORES["gris"], ls="--", lw=1.3, label=r"recta $h\nu-\Phi$")
    ax.plot(x, kmax, color=COLORES["cinetica"], lw=2.6, label=r"$K_{\max}=\max(h\nu-\Phi,\,0)$")
    ax.axvline(nu0 / ESCALA_NU, color=COLORES["potencial"], ls=":", lw=2)
    ax.axhline(0, color="white", lw=0.8, alpha=0.5)
    ax.annotate(rf"$\nu_0$ = {nu0 / ESCALA_NU:.3f}×10¹⁴ Hz" + f"\nλ₀ = {d['lambda0_nm']:.1f} nm",
                xy=(nu0 / ESCALA_NU, 0), xytext=(nu0 / ESCALA_NU * 1.03, 0.55 * max(kmax.max(), 0.5)),
                color=COLORES["potencial"], fontsize=10, arrowprops=dict(arrowstyle="->", color=COLORES["potencial"]))
    color = qc.color_longitud_onda(d["longitud_nm"], fuera=COLORES["densidad"])
    ax.plot([p.frecuencia / ESCALA_NU], [d["kmax_ev"]], "o", ms=12, color=color, mec="white", mew=1.5, zorder=5,
            label=f"radiación elegida (λ = {d['longitud_nm']:.1f} nm)")
    ax.set_xlabel(r"frecuencia $\nu$ [10¹⁴ Hz]")
    ax.set_ylabel("Energía cinética máxima [eV]")
    ax.set_title(f"Energía cinética máxima · {p.metal}")
    ax.set_ylim(min(-0.4, (energia_foton_ev(nus[0]) - p.phi) * 0.5), max(kmax.max(), d["kmax_ev"], 0.5) * 1.15)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=8.5)
    sec = ax.secondary_xaxis("top", functions=(lambda v: C / (np.maximum(v, 1e-6) * ESCALA_NU) * 1e9,
                                               lambda l: C / (np.maximum(l, 1e-6) * 1e-9) / ESCALA_NU))
    # Marcas de λ «redondas» que caen dentro del rango visible del eje (el eje λ no es lineal: se eligen a mano)
    lam_min, lam_max = C / (x[-1] * ESCALA_NU) * 1e9, C / (x[0] * ESCALA_NU) * 1e9
    candidatas = [100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 5000]
    marcas = [l for l in candidatas if lam_min <= l <= lam_max]
    separadas = []
    for l in sorted(marcas):                     # que no queden a menos de ~6 % del ancho del eje
        if all(abs(C / (l * 1e-9) - C / (m * 1e-9)) / (x[-1] - x[0]) / ESCALA_NU > 0.06 for m in separadas):
            separadas.append(l)
    sec.set_xticks(separadas)
    sec.set_xlabel("longitud de onda λ [nm]", color=COLORES["gris"])
    sec.tick_params(colors=COLORES["gris"])

    # Característica I–V: radiación elegida, el doble de potencia y una frecuencia mayor
    kmax_sel = d["kmax_ev"]
    k_mayor = float(energia_cinetica_maxima(1.25 * p.frecuencia, p.phi))
    vlim = max(kmax_sel, k_mayor, 0.6) * 1.25
    v = np.linspace(-vlim, 0.5 * vlim, 600)
    i_sat = d["i_sat"] if d["i_sat"] > 0 else 0.0
    escala = 1e6
    curvas = [(i_sat, kmax_sel, COLORES["cinetica"], f"elegida: {p.potencia * 1e3:g} mW, λ = {d['longitud_nm']:.0f} nm")]
    if i_sat > 0:
        curvas.append((2 * i_sat, kmax_sel, COLORES["onda"], "doble de potencia (misma λ)"))
        nu2 = 1.25 * p.frecuencia
        p2 = ParametrosFoto(p.metal, p.phi, nu2, p.potencia, p.eficiencia)
        curvas.append((corriente_saturacion(p2), float(energia_cinetica_maxima(nu2, p.phi)), COLORES["energia"],
                       f"misma potencia, ν × 1.25 (λ = {C / nu2 * 1e9:.0f} nm)"))
    for isat, km, col, etq in curvas:
        ax2.plot(v, corriente_voltaje(v, isat, km) * escala, color=col, lw=2.2, label=etq)
        if km > 0 and isat > 0:
            ax2.plot([-km], [0], "o", color=col, ms=6)
    ax2.axvline(0, color="white", lw=0.7, alpha=0.4)
    ax2.axhline(0, color="white", lw=0.7, alpha=0.4)
    ax2.set_xlabel("voltaje aplicado V [V]")
    ax2.set_ylabel("Corriente [μA]")
    ax2.set_title("Corriente frente a voltaje")
    ax2.grid(alpha=0.3)
    if i_sat > 0:
        ax2.legend(loc="upper left", fontsize=8.5)
        ax2.annotate(f"−V₀ = −{kmax_sel:.3f} V", xy=(-kmax_sel, 0), xytext=(-kmax_sel, 0.35 * 2 * i_sat * escala),
                     color=COLORES["cinetica"], ha="center", arrowprops=dict(arrowstyle="->", color=COLORES["cinetica"]))
    else:
        ax2.text(0.5, 0.5, "Sin emisión: hν < Φ\nla corriente es nula para cualquier potencia",
                 transform=ax2.transAxes, ha="center", va="center", color=COLORES["energia"], fontsize=12)
    return fig


def figura_metales(metales: list[str], nu_sel: float | None = None):
    """K_max(ν) de varios metales: rectas paralelas (misma pendiente h) desplazadas por Φ."""
    fig, ax = qc.rejilla(1, 1, (13, 5.6), constrained_layout=True)
    phis = [METALES[m] for m in metales]
    nus = np.linspace(0.3 * min(phis) / H_EV, 1.6 * max(phis) / H_EV, 800)
    paleta = [COLORES["onda"], COLORES["densidad"], COLORES["cinetica"], COLORES["energia"], COLORES["potencial"],
              COLORES["interferencia"], "#F97316", "#E879F9", "#A3E635", "#FDE68A", "#93C5FD"]
    for i, m in enumerate(metales):
        col = paleta[i % len(paleta)]
        ax.plot(nus / ESCALA_NU, energia_cinetica_maxima(nus, METALES[m]), color=col, lw=2.2,
                label=f"{m}  (Φ = {METALES[m]:.2f} eV, λ₀ = {longitud_umbral_nm(METALES[m]):.0f} nm)")
        ax.plot([frecuencia_umbral(METALES[m]) / ESCALA_NU], [0], "o", color=col, ms=6)
    if nu_sel is not None:
        ax.axvline(nu_sel / ESCALA_NU, color="white", ls="--", lw=1.2, alpha=0.7)
        ax.text(nu_sel / ESCALA_NU, ax.get_ylim()[1] * 0.95, "  radiación elegida", color="white", va="top", fontsize=9)
    ax.set_xlabel(r"frecuencia $\nu$ [10¹⁴ Hz]")
    ax.set_ylabel("Energía cinética máxima [eV]")
    ax.set_title("Energía cinética máxima frente a frecuencia")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=8.5)
    return fig


def figura_millikan(res: dict, phi_real: float, metal: str):
    """Datos simulados de V₀ frente a ν y su ajuste lineal."""
    fig, ax = qc.rejilla(1, 1, (13, 5.6), constrained_layout=True)
    if res["n"] == 0:
        ax.text(0.5, 0.5, "Ninguna línea supera el umbral de este metal", transform=ax.transAxes, ha="center")
        return fig
    nus = np.linspace(0.0, 1.08 * res["nu"].max(), 200)
    for nu, lam, v in zip(res["nu"], res["lam"], res["v0"]):
        ax.plot([nu / ESCALA_NU], [v], "o", ms=11, color=qc.color_longitud_onda(lam, fuera=COLORES["onda"]),
                mec="white", mew=1.2, zorder=4)
        ax.annotate(f"{lam:.0f} nm", (nu / ESCALA_NU, v), textcoords="offset points", xytext=(8, -12), fontsize=9,
                    color=COLORES["gris"])
    ax.plot(nus / ESCALA_NU, (H_EV * nus) - phi_real, color=COLORES["gris"], ls=":", lw=1.4,
            label=f"recta teórica (h exacta, Φ = {phi_real:.2f} eV)")
    if res.get("ajuste"):
        ax.plot(nus / ESCALA_NU, res["pendiente"] * nus + res["ordenada"], color=COLORES["energia"], lw=2,
                label=f"ajuste: h = {res['h']:.4e} J·s, Φ = {res['phi']:.3f} eV")
        ax.plot([res["nu0"] / ESCALA_NU], [0], "s", color=COLORES["energia"], ms=8)
    ax.axhline(0, color="white", lw=0.7, alpha=0.5)
    ax.set_xlim(0, nus[-1] / ESCALA_NU)
    ax.set_ylim(min(-phi_real * 1.1, -0.5), max(res["v0"].max() * 1.25, 0.5))
    ax.set_xlabel(r"frecuencia $\nu$ [10¹⁴ Hz]")
    ax.set_ylabel("Potencial de frenado [V]")
    ax.set_title(f"Potencial de frenado · {metal}")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    return fig


# =====================================================================
# 3. PRUEBAS NUMÉRICAS
# =====================================================================
def ejecutar_pruebas() -> qc.RegistroPruebas:
    r = qc.RegistroPruebas("Efecto fotoeléctrico")
    phi = METALES["Cesio"]
    nu0 = frecuencia_umbral(phi)
    r.comprobar("Umbral: h·ν₀ = Φ", abs(energia_foton_ev(nu0) - phi) < 1e-12)
    r.comprobar("Cesio: λ₀ = hc/Φ ≈ 579.4 nm", abs(longitud_umbral_nm(phi) - 579.365) < 0.01,
                f"{longitud_umbral_nm(phi):.3f} nm")
    r.comprobar("c = λν (conversión λ ↔ ν)", abs(C / nu0 * 1e9 - longitud_umbral_nm(phi)) < 1e-9)
    r.comprobar("Por debajo del umbral K_max = 0", float(energia_cinetica_maxima(0.9 * nu0, phi)) == 0.0)
    nu = 1.5 * nu0
    r.comprobar("Por encima del umbral K_max = hν − Φ", abs(float(energia_cinetica_maxima(nu, phi)) - (H_EV * nu - phi)) < 1e-12)
    nus = np.linspace(1.1, 3.0, 20) * nu0
    pend = np.polyfit(nus, energia_cinetica_maxima(nus, phi), 1)[0]
    r.comprobar("Pendiente de K_max(ν) = h (en eV·s)", abs(pend / H_EV - 1) < 1e-10)
    pendientes = [np.polyfit(nus * frecuencia_umbral(METALES[m]) / nu0,
                             energia_cinetica_maxima(nus * frecuencia_umbral(METALES[m]) / nu0, METALES[m]), 1)[0]
                  for m in ("Sodio", "Zinc", "Platino")]
    r.comprobar("La pendiente h es la misma para todos los metales", np.allclose(pendientes, H_EV, rtol=1e-10))
    k = 1.0
    v = velocidad_maxima(k)
    r.comprobar("K_max = ½ mₑ v_max² (ida y vuelta)", abs(0.5 * M_E * v ** 2 / E - k) < 1e-12, f"v(1 eV) = {v:.4e} m/s")
    r.comprobar("v_max(1 eV) ≈ 5.93×10⁵ m/s", abs(v - 5.931e5) / 5.931e5 < 1e-3)
    r.comprobar("Potencial de frenado: V₀ [V] = K_max [eV]", potencial_frenado(1.234) == 1.234)

    p = validar_parametros_foto("Cesio", 0, "longitud", 400.0, 1.0, 10.0)
    p2 = validar_parametros_foto("Cesio", 0, "longitud", 400.0, 5.0, 10.0)
    d, d2 = calcular_foto(p), calcular_foto(p2)
    r.comprobar("La intensidad NO cambia K_max", d["kmax_ev"] == d2["kmax_ev"])
    r.comprobar("La corriente es proporcional a la potencia", abs(d2["i_sat"] / d["i_sat"] - 5.0) < 1e-12)
    r.comprobar("I_sat = η·e·P/(hν)", abs(d["i_sat"] - 0.1 * E * 1e-3 / (H * p.frecuencia)) < 1e-18)
    pr = validar_parametros_foto("Cesio", 0, "longitud", 700.0, 1000.0, 100.0)
    r.comprobar("Sin emisión no hay corriente aunque la potencia sea muy elevada", calcular_foto(pr)["i_sat"] == 0.0)
    vv = np.array([-d["kmax_ev"], -0.5 * d["kmax_ev"], 0.0, 2.0])
    iv = corriente_voltaje(vv, d["i_sat"], d["kmax_ev"])
    r.comprobar("Curva I–V: I(−V₀) = 0, I(−V₀/2) = I_sat/2, saturación para V ≥ 0",
                abs(iv[0]) < 1e-30 and abs(iv[1] - d["i_sat"] / 2) < 1e-20 and iv[2] == iv[3] == d["i_sat"])
    pf = validar_parametros_foto("Cesio", 0, "frecuencia", C / 400e-9, 1.0, 10.0)
    r.comprobar("Entrada por frecuencia = entrada por longitud de onda", abs(calcular_foto(pf)["kmax_ev"] - d["kmax_ev"]) < 1e-12)

    m = experimento_millikan(METALES["Sodio"], LINEAS_MERCURIO, ruido_mv=0.0)
    r.comprobar("Millikan sin ruido: h recuperada exactamente", m["ajuste"] and m["error_h_rel"] < 1e-10,
                f"h = {m['h']:.6e} J·s")
    r.comprobar("Millikan sin ruido: Φ recuperada", abs(m["phi"] - METALES["Sodio"]) < 1e-9)
    dentro = sum(abs(m_["h"] - H) < 3 * m_["h_err"]
                 for m_ in (experimento_millikan(METALES["Cesio"], LINEAS_MERCURIO, 20.0, s_) for s_ in range(1, 41)))
    r.comprobar("Millikan con ruido de 20 mV: la incertidumbre del ajuste es coherente (h exacta dentro de 3σ)",
                dentro >= 38, f"{dentro}/40 repeticiones")
    mz = experimento_millikan(METALES["Platino"], LINEAS_MERCURIO)
    r.comprobar("Platino: ninguna línea del mercurio supera el umbral (se descartan)", mz["n"] == 0 and not mz["ajuste"])

    r.comprobar("Región espectral: 400 nm visible, 250 nm UV, 1200 nm IR",
                qc.region_espectral(400).startswith("Visible") and qc.region_espectral(250) == "Ultravioleta"
                and qc.region_espectral(1200) == "Infrarrojo")
    v_ = validar_parametros_foto
    r.comprobar_error("Rechaza λ ≤ 0", v_, "Cesio", 0, "longitud", -5)
    r.comprobar_error(f"Rechaza λ fuera de [{LAMBDA_MIN:g}, {LAMBDA_MAX:g}] nm", v_, "Cesio", 0, "longitud", 20000)
    r.comprobar_error("Rechaza frecuencia no numérica", v_, "Cesio", 0, "frecuencia", "abc")
    r.comprobar_error("Rechaza Φ ≤ 0 (personalizado)", v_, PERSONALIZADO, 0.0, "longitud", 400)
    r.comprobar_error("Rechaza Φ > 10 eV", v_, PERSONALIZADO, 12.0, "longitud", 400)
    r.comprobar_error("Rechaza potencia negativa", v_, "Cesio", 0, "longitud", 400, -1.0)
    r.comprobar_error("Rechaza eficiencia > 100 %", v_, "Cesio", 0, "longitud", 400, 1.0, 150.0)
    r.comprobar_error("Rechaza metal desconocido", v_, "Kriptonita", 0, "longitud", 400)
    return r


# =====================================================================
# 4. INTERFAZ (Streamlit)
# =====================================================================
MODOS_ENTRADA = {"longitud": "Longitud de onda λ [nm]", "frecuencia": "Frecuencia ν [Hz]"}
VALORES_INICIALES = {
    "foto_metal": "Cesio", "foto_phi": 2.50, "foto_modo": "longitud", "foto_lambda": 400.0, "foto_nu": "7.5e14",
    "foto_potencia": 1.0, "foto_eficiencia": 10.0,
    "foto_comp": ["Cesio", "Sodio", "Aluminio", "Zinc", "Platino"],
    "foto_mk_metal": "Cesio", "foto_mk_ruido": 20.0, "foto_mk_semilla": 1,
}
DEMOS = {
    "Cesio con luz violeta (400 nm): hay emisión": {"foto_metal": "Cesio", "foto_modo": "longitud", "foto_lambda": 400.0},
    "Cesio con luz roja (700 nm): no hay emisión": {"foto_metal": "Cesio", "foto_modo": "longitud", "foto_lambda": 700.0},
    "Zinc con luz visible (450 nm): no hay emisión": {"foto_metal": "Zinc", "foto_modo": "longitud", "foto_lambda": 450.0},
    "Zinc con ultravioleta (200 nm)": {"foto_metal": "Zinc", "foto_modo": "longitud", "foto_lambda": 200.0},
    "Justo en el umbral del sodio (543.8 nm)": {"foto_metal": "Sodio", "foto_modo": "longitud", "foto_lambda": 543.8},
}

GUIA = [
    {"titulo": "Existe una frecuencia umbral",
     "objetivo": "Comprobar que por debajo de ν₀ no hay emisión, sea cual sea la intensidad.",
     "pasos": ["Cargar la configuración (cesio, luz roja de 700 nm).", "Registrar K_max y la corriente.",
               "Aumentar la potencia a 100 mW.", "Disminuir la longitud de onda a 550 nm y después a 450 nm."],
     "pregunta": "¿Puede una luz roja muy intensa arrancar electrones del cesio?",
     "resultado": "No: con 700 nm, hν ≈ 1.77 eV < Φ = 2.14 eV y la corriente es cero para cualquier potencia. "
                  "La emisión empieza por debajo de λ₀ ≈ 579 nm. Esto contradice la teoría ondulatoria clásica, "
                  "según la cual bastaría con más intensidad.",
     "pestana": "Experimento", "config": {"foto_metal": "Cesio", "foto_modo": "longitud", "foto_lambda": 700.0,
                                         "foto_potencia": 1.0}},
    {"titulo": "La intensidad cambia el número de electrones, no su energía",
     "objetivo": "Separar los efectos de la intensidad y de la frecuencia.",
     "pasos": ["Cargar la configuración (cesio, 400 nm, 1 mW).", "Registrar K_max, V₀ y la corriente de saturación.",
               "Multiplicar la potencia por 5.", "Volver a 1 mW y cambiar λ a 300 nm."],
     "pregunta": "¿Qué magnitudes cambian al aumentar la potencia? ¿Y al disminuir λ?",
     "resultado": "Con más potencia la corriente se multiplica por 5 pero K_max y V₀ no cambian (en la curva I–V "
                  "las dos curvas cortan el eje en el mismo −V₀). Al bajar λ aumenta K_max (de ≈ 0.96 a ≈ 1.99 eV) "
                  "y la corriente, a igual potencia, BAJA (× 0.75 = 300/400): cada fotón lleva más energía, así que llegan menos fotones por segundo.",
     "pestana": "Experimento", "config": {"foto_metal": "Cesio", "foto_modo": "longitud", "foto_lambda": 400.0,
                                         "foto_potencia": 1.0, "foto_eficiencia": 10.0}},
    {"titulo": "Pendiente universal h",
     "objetivo": "Comparar metales distintos.",
     "pasos": ["Cargar la configuración.", "Observar las rectas K_max(ν) de los metales seleccionados.",
               "Comparar su pendiente y su corte con el eje horizontal."],
     "pregunta": "¿Qué propiedad depende del metal y cuál es universal?",
     "resultado": "Todas las rectas son paralelas: la pendiente es h para cualquier metal. Lo que cambia es la "
                  "función de trabajo Φ, que desplaza la recta y fija la frecuencia umbral ν₀ = Φ/h.",
     "pestana": "Comparación de metales", "config": {"foto_comp": ["Cesio", "Sodio", "Aluminio", "Zinc", "Platino"]}},
    {"titulo": "Medir la constante de Planck",
     "objetivo": "Reproducir el método de Millikan: ajustar V₀ frente a ν.",
     "pasos": ["Cargar la configuración (cesio, ruido de 20 mV).", "Registrar h estimada y su error.",
               "Establecer el ruido a 0 mV y después a 100 mV. Cambiar la semilla para repetir la medida.",
               "Cambiar el metal a sodio: ¿cuántas líneas quedan por encima del umbral?"],
     "pregunta": "¿Qué parte de la recta da h y cuál da Φ? ¿Cómo influye el ruido?",
     "resultado": "La pendiente es h/e y la ordenada en el origen es −Φ/e. Sin ruido se recupera h exactamente; "
                  "con ruido el error crece y la incertidumbre del ajuste lo refleja. Con sodio (λ₀ ≈ 544 nm) solo "
                  "sirven 3 de las 5 líneas y el error aumenta: el intervalo de frecuencias es menor. Millikan (1916) obtuvo así "
                  "h con un 0.5 % de error, confirmando la ecuación de Einstein.",
     "pestana": "Determinación de h", "config": {"foto_mk_metal": "Cesio", "foto_mk_ruido": 20.0, "foto_mk_semilla": 1}},
]

PREGUNTAS = [
    {"enunciado": "Si se duplica la intensidad de la luz (misma frecuencia, por encima del umbral)…",
     "opciones": ["se duplica K_max", "se duplica el número de electrones emitidos por segundo",
                  "disminuye la frecuencia umbral", "no cambia nada"], "correcta": 1,
     "explicacion": "Más intensidad = más fotones por segundo = más electrones. Cada fotón sigue teniendo hν, así "
                    "que K_max = hν − Φ no cambia."},
    {"enunciado": "La función de trabajo del cesio es 2.14 eV. ¿Habrá emisión con luz de 700 nm (hν ≈ 1.77 eV)?",
     "opciones": ["Sí, siempre que la luz sea intensa", "Sí, pero con K_max negativa", "No, porque hν < Φ",
                  "Depende del voltaje aplicado"], "correcta": 2,
     "explicacion": "Un solo fotón debe aportar al menos Φ. Con hν < Φ no hay emisión, sea cual sea la intensidad."},
    {"enunciado": "En la gráfica de K_max frente a ν, la pendiente de la recta es…",
     "opciones": ["la función de trabajo Φ", "la constante de Planck h", "la carga del electrón e",
                  "distinta para cada metal"], "correcta": 1,
     "explicacion": "K_max = hν − Φ: pendiente h (universal) y ordenada −Φ (depende del metal)."},
    {"enunciado": "El potencial de frenado V₀ mide…",
     "opciones": ["el número de fotones", "la energía cinética máxima de los electrones: eV₀ = K_max",
                  "la función de trabajo", "la intensidad de la luz"], "correcta": 1,
     "explicacion": "Es el voltaje que detiene incluso a los electrones más rápidos: eV₀ = K_max."},
    {"enunciado": "¿Qué hecho experimental NO puede explicar la teoría ondulatoria clásica de la luz?",
     "opciones": ["que la luz se refleje", "la existencia de una frecuencia umbral independiente de la intensidad",
                  "que la corriente aumente con la intensidad", "que los metales conduzcan la electricidad"],
     "correcta": 1,
     "explicacion": "Clásicamente, una onda intensa de cualquier frecuencia acabaría arrancando electrones. El umbral "
                    "solo se explica si la luz llega en cuantos de energía hν (Einstein, 1905)."},
    {"enunciado": "Para un mismo metal, ¿cómo cambia K_max si la longitud de onda disminuye?",
     "opciones": ["Aumentar", "Disminuir", "No cambia", "Se hace negativa"], "correcta": 0,
     "explicacion": "λ menor ⇒ ν = c/λ mayor ⇒ hν mayor ⇒ K_max = hν − Φ mayor."},
]


def _aplicar_demo():
    eleccion = st.session_state.get("foto_demo")
    if eleccion in DEMOS:
        qc.fijar_estado(DEMOS[eleccion])


def _leer_parametros():
    with st.container(border=True):
        qc.seccion("Metal y radiación incidente")
        c1, c2, c3, c4 = st.columns(4)
        metal = c1.selectbox("Metal", list(METALES) + [PERSONALIZADO], key="foto_metal",
                             format_func=lambda m: m if m == PERSONALIZADO else f"{m} (Φ = {METALES[m]:.2f} eV)",
                             help="Funciones de trabajo aproximadas: dependen del estado de la superficie.")
        c2.number_input("Función de trabajo Φ [eV]", min_value=0.0, max_value=PHI_MAX, step=0.05, format="%.3f",
                        key="foto_phi", disabled=(metal != PERSONALIZADO),
                        help="Solo se usa con el metal «Personalizado».")
        modo = c3.radio("Dato de entrada", list(MODOS_ENTRADA), key="foto_modo", format_func=MODOS_ENTRADA.get,
                        horizontal=False)
        if modo == "longitud":
            valor = c4.number_input("Longitud de onda λ [nm]", min_value=0.0, step=5.0, format="%.2f", key="foto_lambda")
        else:
            valor = c4.text_input("Frecuencia ν [Hz]", key="foto_nu", help="Admite notación científica, p. ej. 7.5e14")
        qc.seccion("Fuente de luz y detector")
        d1, d2, _, _ = st.columns(4)
        d1.number_input("Potencia luminosa P [mW]", min_value=0.0, step=0.5, format="%.3g", key="foto_potencia",
                        help="Potencia que llega al metal. Determinar el número de fotones por segundo.")
        d2.slider("Eficiencia cuántica η [%]", 0.0, 100.0, step=1.0, key="foto_eficiencia",
                  help="Fracción de fotones absorbidos que arrancan un electrón.")
        qc.pie_de_parametros(DEMOS, "foto_demo", _aplicar_demo, VALORES_INICIALES, "foto_reset")
    try:
        return validar_parametros_foto(metal, st.session_state["foto_phi"], modo, valor,
                                       st.session_state["foto_potencia"], st.session_state["foto_eficiencia"])
    except ValueError as error:
        qc.error(error)
        return None


def _pestana_experimento(p: ParametrosFoto):
    d = calcular_foto(p)
    if d["emision"]:
        qc.nota(f"**Hay emisión fotoeléctrica**: hν = {d['energia_foton_ev']:.4f} eV ≥ Φ = {p.phi:.3f} eV. "
                f"La energía sobrante, {d['kmax_ev']:.4f} eV, es la energía cinética máxima del electrón.")
    else:
        qc.aviso(f"**No hay emisión**: hν = {d['energia_foton_ev']:.4f} eV < Φ = {p.phi:.3f} eV. Hace falta "
                 f"λ < λ₀ = {d['lambda0_nm']:.1f} nm, independientemente de la intensidad.")
    qc.seccion("Resultados")
    qc.metricas([
        ("Energía del fotón hν [eV]", f"{d['energia_foton_ev']:.4f}", f"{d['energia_foton_j']:.4e} J"),
        ("Función de trabajo Φ [eV]", f"{p.phi:.4f}"),
        (r"$K_{\max}$ [eV]", f"{d['kmax_ev']:.4f}", f"{d['kmax_j']:.4e} J"),
        (r"$v_{\max}$ [m/s]", qc.cientifico(d["vmax"], 4)),
        ("Frecuencia umbral ν₀ [Hz]", qc.cientifico(d["nu0"], 4)),
        ("Longitud de onda umbral λ₀ [nm]", f"{d['lambda0_nm']:.2f}", d["region_umbral"]),
        ("Potencial de frenado V₀ [V]", f"{d['v0']:.4f}", "eV₀ = K_max"),
        ("Corriente de saturación [μA]", f"{d['i_sat'] * 1e6:.4g}", f"{d['flujo']:.3e} fotones/s"),
    ])
    color = qc.color_longitud_onda(d["longitud_nm"], fuera=None)
    muestra = (f'<span style="display:inline-block;width:.9rem;height:.9rem;border-radius:2px;background:{color};'
               f'vertical-align:-2px;margin-right:.4rem"></span>') if color else ""
    st.markdown(f'<p class="ql-subtitulo">{muestra}Radiación: λ = {d["longitud_nm"]:.2f} nm, ν = '
                f'{d["frecuencia"]:.4e} Hz · {d["region"]}</p>', unsafe_allow_html=True)
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_experimento(p, d), archivo=f"fotoelectrico_{p.metal.lower()}_{d['longitud_nm']:.0f}nm.png")
    v_iv = np.linspace(-(d["kmax_ev"] + 1.0), 3.0, 401)
    qc.exportar_datos({"V [V]": v_iv, "I [A]": corriente_voltaje(v_iv, d["i_sat"], d["kmax_ev"])},
                      f"fotoelectrico_curva_IV_{p.metal.lower()}_{d['longitud_nm']:.0f}nm.csv",
                      "Descargar la curva corriente–voltaje (CSV)")
    with st.expander("Valores numéricos detallados", expanded=False):
        qc.tabla([
            ("Metal", p.metal, ""), ("Función de trabajo Φ", f"{p.phi:.6f}", "eV"),
            ("Frecuencia ν", f"{d['frecuencia']:.6e}", "Hz"), ("Longitud de onda λ", f"{d['longitud_nm']:.6f}", "nm"),
            ("Energía del fotón hν", f"{d['energia_foton_ev']:.6f}", "eV"),
            ("Energía del fotón hν", f"{d['energia_foton_j']:.6e}", "J"),
            ("Frecuencia umbral ν₀ = Φ/h", f"{d['nu0']:.6e}", "Hz"),
            ("Longitud de onda umbral λ₀ = hc/Φ", f"{d['lambda0_nm']:.4f}", "nm", d["region_umbral"]),
            ("Energía cinética máxima K_max", f"{d['kmax_ev']:.6f}", "eV"),
            ("Energía cinética máxima K_max", f"{d['kmax_j']:.6e}", "J"),
            ("Velocidad máxima v_max", f"{d['vmax']:.6e}", "m/s", f"{d['vmax'] / C:.2e} c (no relativista)"),
            ("Potencial de frenado V₀", f"{d['v0']:.6f}", "V"),
            ("Flujo de fotones P/(hν)", f"{d['flujo']:.6e}", "1/s"),
            ("Corriente de saturación η·e·P/(hν)", f"{d['i_sat'] * 1e6:.6g}", "μA"),
        ], archivo="fotoelectrico_valores.csv")
    with st.expander("Interpretación física", expanded=False):
        st.markdown(
            "- La luz llega en **fotones** de energía hν. Un electrón absorbe **un** fotón: si hν < Φ no puede escapar, "
            "por intensa que sea la luz.\n"
            "- Si hν ≥ Φ, la energía sobrante aparece como energía cinética: K_max = hν − Φ. Es un **máximo** porque "
            "los electrones más internos pierden energía adicional antes de salir.\n"
            "- La **intensidad** fija el número de fotones por segundo y, por tanto, la **corriente**; no cambia K_max ni V₀.\n"
            "- La curva corriente–voltaje usa un modelo simplificado (energías repartidas uniformemente entre 0 y K_max): "
            "lo importante es que la corriente se anula en −V₀, el mismo para cualquier intensidad.")


def _pestana_metales(p: ParametrosFoto):
    sel = st.multiselect("Metales a comparar", list(METALES), key="foto_comp")
    if not sel:
        qc.nota("Seleccionar al menos un metal.")
        return
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_metales(sel, p.frecuencia), archivo="fotoelectrico_metales.png")
    lam = p.longitud * 1e9
    qc.seccion("Tabla comparativa con la radiación elegida")
    st.caption(f"Radiación elegida: λ = {lam:.1f} nm.")
    filas = []
    for m in sel:
        phi = METALES[m]
        k = float(energia_cinetica_maxima(p.frecuencia, phi))
        filas.append({"Metal": m, "Φ [eV]": f"{phi:.2f}", "ν₀ [10¹⁴ Hz]": f"{frecuencia_umbral(phi) / 1e14:.3f}",
                      "λ₀ [nm]": f"{longitud_umbral_nm(phi):.1f}", "Región de λ₀": qc.region_espectral(longitud_umbral_nm(phi)),
                      "K_max [eV]": f"{k:.4f}", "¿Emite?": "sí" if k > 0 else "no"})
    qc.tabla_libre(filas, numericas=("Φ [eV]", "ν₀ [10¹⁴ Hz]", "λ₀ [nm]", "K_max [eV]"), archivo="fotoelectrico_metales.csv")
    st.caption("Los metales alcalinos (cesio, potasio, sodio) emiten con luz visible; el zinc, el cobre o el "
               "platino necesitan ultravioleta.")


def _pestana_millikan():
    with st.container(border=True):
        qc.seccion("Montaje simulado: lámpara de mercurio y fotocélula")
        c1, c2, c3, _ = st.columns(4)
        metal = c1.selectbox("Metal del cátodo", list(METALES), key="foto_mk_metal")
        ruido = c2.slider("Ruido de medida σ [mV]", 0.0, 200.0, step=5.0, key="foto_mk_ruido",
                          help="Desviación típica del error aleatorio en cada medida de V₀.")
        semilla = c3.number_input("Semilla (repetir la medida)", 0, 10_000, step=1, key="foto_mk_semilla")
    res = experimento_millikan(METALES[metal], LINEAS_MERCURIO, ruido, semilla)
    descartadas = len(LINEAS_MERCURIO) - res["n"]
    if descartadas:
        qc.aviso(f"{descartadas} línea(s) del mercurio no superan el umbral de este metal (λ₀ = "
                 f"{longitud_umbral_nm(METALES[metal]):.0f} nm) y no producen corriente: se descartan.")
    if not res.get("ajuste"):
        qc.error("Hacen falta al menos dos líneas por encima del umbral para ajustar una recta. Seleccionar otro metal.")
        if res["n"] == 0:
            return
    else:
        qc.seccion("Resultados del ajuste lineal")
        st.caption("Recta ajustada: V₀ = (h/e)·ν − Φ/e. La pendiente da h y la ordenada en el origen da Φ.")
        qc.metricas([
            ("h estimada [J·s]", f"{res['h']:.4e}", f"± {res['h_err']:.1e} J·s (1σ del ajuste)"),
            ("Error respecto a h exacta", f"{100 * res['error_h_rel']:.3f} %", f"h = {H:.8e} J·s (valor exacto del SI)"),
            ("Φ estimada [eV]", f"{res['phi']:.4f}", f"± {res['phi_err']:.3f} eV"),
            ("ν₀ estimada [10¹⁴ Hz]", f"{res['nu0'] / 1e14:.4f}"),
        ])
    qc.seccion("Visualización")
    qc.mostrar_pyplot(figura_millikan(res, METALES[metal], metal), archivo=f"millikan_{metal.lower()}.png")
    qc.seccion("Datos medidos")
    qc.tabla_libre([{"λ [nm]": f"{l:.2f}", "ν [10¹⁴ Hz]": f"{n / 1e14:.4f}", "V₀ ideal [V]": f"{vi:.4f}",
                     "V₀ medido [V]": f"{vm:.4f}"} for l, n, vi, vm in zip(res["lam"], res["nu"], res["v0_ideal"], res["v0"])],
                   numericas=("λ [nm]", "ν [10¹⁴ Hz]", "V₀ ideal [V]", "V₀ medido [V]"), archivo=f"millikan_{metal.lower()}.csv")


def interfaz() -> None:
    """Página completa del simulador 4 (se puede insertar dentro de quantum_lab.py)."""
    qc.iniciar_estado(VALORES_INICIALES)
    qc.mostrar_mensaje_pendiente()
    qc.encabezado_pagina("Simulador 04", "Efecto fotoeléctrico",
                         "Ecuación de Einstein, frecuencia umbral, energía de los electrones emitidos, corriente "
                         "fotoeléctrica y determinación experimental de la constante de Planck.")
    qc.enlace_teoria("fotoelectrico")
    qc.ficha_simulador(
        "Aplicar la ecuación de Einstein para hallar la frecuencia umbral, la energía de los electrones emitidos "
        "y la constante de Planck.",
        r"\begin{gathered}K_{\max}=h\nu-\phi\\[4pt]\nu_0=\phi/h,\qquad eV_0=K_{\max}\end{gathered}",
        [("ν", "frecuencia de la luz"), ("φ", "función de trabajo del metal"), ("ν₀", "frecuencia umbral"),
         ("V₀", "potencial de frenado")],
        "Modelo de Einstein: un fotón libera un electrón si hν ≥ φ. No incluye efectos de superficie ni de temperatura.")
    p = _leer_parametros()
    if p is None:
        return
    tabs = st.tabs(["Experimento", "Comparación de metales", "Determinación de h", "Guía de práctica", "Autoevaluación",
                    "Pruebas numéricas"])
    with tabs[0]:
        _pestana_experimento(p)
    with tabs[1]:
        _pestana_metales(p)
    with tabs[2]:
        _pestana_millikan()
    with tabs[3]:
        qc.guia_practica(GUIA, "foto")
    with tabs[4]:
        qc.autoevaluacion(PREGUNTAS, "foto")
    with tabs[5]:
        qc.boton_pruebas(ejecutar_pruebas, "foto_pruebas")
    qc.escribir_en_url(VALORES_INICIALES)


if __name__ == "__main__":
    qc.lanzar(ejecutar_pruebas, interfaz, "Quantum Lab · Efecto fotoeléctrico", ":material/science:",
              "efecto_fotoelectrico.py")
