"""
redactor/_simuladores.py — Resultados de los simuladores para insertar en un informe
====================================================================================

Cada entrada describe los campos que se piden (con límites) y una función `construir(valores)` que llama a las MISMAS funciones
de validación y de cálculo del simulador y devuelve su `Informe` (parámetros, resultados y figura). Nada se recalcula aquí:
lo que aparece en el cuaderno es lo que muestra el simulador con esos parámetros. Los valores se guardan en el cuaderno
(no la imagen), así que el resultado es reproducible al abrirlo de nuevo.
"""

from __future__ import annotations

from dataclasses import dataclass

import efecto_fotoelectrico as foto
import modelo_bohr as bohr
import oscilador_armonico as osc
import particula_caja as caja
import particula_esfera as esf
import principio_incertidumbre as inc


@dataclass(frozen=True)
class Campo:
    clave: str
    etiqueta: str
    tipo: str                       # "int" | "float" | "opciones"
    defecto: object
    minimo: float | None = None
    maximo: float | None = None
    opciones: tuple = ()            # tipo "opciones": ((valor, etiqueta), …)
    ayuda: str = ""


@dataclass(frozen=True)
class Simulador:
    clave: str
    nombre: str
    campos: tuple
    construir: object               # valores (dict) -> Informe


def _caja(v):
    p = caja.validar_parametros_caja(v["n"], v["a"], v["m"], "SI", 1500)
    return caja.informe_estado(p, caja.calcular_estado_individual(p))


def _osc(v):
    p = osc.validar_parametros_oscilador(v["n"], v["m"], v["omega"], "SI", 9.0, 3001)
    return osc.informe_estado(p, osc.calcular_estado(p))


def _foto(v):
    p = foto.validar_parametros_foto(v["metal"], 2.0, "longitud", v["lam"], v["potencia"], v["eficiencia"])
    return foto.informe_experimento(p, foto.calcular_foto(p))


def _bohr(v):
    ni, nf, nucleo = bohr.validar_transicion(v["ni"], v["nf"], v["nucleo"])
    t = bohr.Transicion(ni, nf, nucleo, bool(v["masa_reducida"]))
    return bohr.informe_transicion(t, bohr.calcular_transicion(t))


def _esf(v):
    p = esf.validar_parametros_esfera(v["l"], v["m"], 1.0, "SI", 90, "densidad", "lobulos", 0.4, "Viridis")
    return esf.informe_estado_angular(p)


def _inc(v):
    p = inc.validar_paquete(v["tipo"], v["ancho"], v["k0"], 0.0 if v["tipo"] != "chirp" else v["beta"],
                            v["separacion"] if v["tipo"] == "dos" else 0.0)
    return inc.informe_paquete(p, inc.calcular_paquete(p))


SIMULADORES: dict[str, Simulador] = {s.clave: s for s in (
    Simulador("caja", "Partícula en una caja", (
        Campo("n", "Número cuántico n", "int", 1, 1, caja.N_MAX),
        Campo("a", "Longitud a [nm]", "float", 1.0, 1e-6, 1e3),
        Campo("m", "Masa [mₑ]", "float", 1.0, 1e-3, 1e5)), _caja),
    Simulador("oscilador", "Oscilador armónico", (
        Campo("n", "Número cuántico n", "int", 0, 0, osc.N_MAX // 2),
        Campo("m", "Masa [mₑ]", "float", 1.0, 1e-3, 1e5),
        Campo("omega", "Frecuencia angular ω [rad/s]", "float", 1.0e15, 1e10, 1e18)), _osc),
    Simulador("fotoelectrico", "Efecto fotoeléctrico", (
        Campo("metal", "Metal", "opciones", "Cesio", opciones=tuple((k, k) for k in foto.METALES)),
        Campo("lam", "Longitud de onda λ [nm]", "float", 400.0, 10.0, 5000.0),
        Campo("potencia", "Potencia [mW]", "float", 1.0, 1e-3, 1e3),
        Campo("eficiencia", "Eficiencia cuántica [%]", "float", 10.0, 0.01, 100.0)), _foto),
    Simulador("bohr", "Átomo de hidrógeno (Bohr)", (
        Campo("ni", "Nivel inicial", "int", 3, 1, bohr.N_MAX),
        Campo("nf", "Nivel final", "int", 2, 1, bohr.N_MAX),
        Campo("nucleo", "Átomo", "opciones", "H", opciones=tuple((k, v[2]) for k, v in bohr.NUCLEOS.items())),
        Campo("masa_reducida", "Corrección de masa reducida", "opciones", True, opciones=((True, "Sí"), (False, "No")))), _bohr),
    Simulador("esfera", "Armónicos esféricos", (
        Campo("l", "Número cuántico l", "int", 2, 0, esf.L_MAX),
        Campo("m", "Número cuántico m", "int", 1, -esf.L_MAX, esf.L_MAX, ayuda="Debe cumplir |m| ≤ l.")), _esf),
    Simulador("incertidumbre", "Principio de incertidumbre", (
        Campo("tipo", "Forma del paquete", "opciones", "gaussiano", opciones=tuple(inc.TIPOS.items())),
        Campo("ancho", "Ancho [nm]", "float", 1.0, inc.ANCHO_MIN, inc.ANCHO_MAX),
        Campo("k0", "Número de onda central k₀ [nm⁻¹]", "float", 5.0, -50.0, 50.0),
        Campo("beta", "Chirp β (solo «con chirp»)", "float", 2.0, -20.0, 20.0),
        Campo("separacion", "Separación d [nm] (solo «dos gaussianas»)", "float", 6.0, 0.0, 100.0)), _inc),
)}


def valores_por_defecto(clave: str) -> dict:
    return {c.clave: c.defecto for c in SIMULADORES[clave].campos}


def construir(clave: str, valores: dict):
    """Informe del simulador con los valores dados. Lanza ValueError con un mensaje comprensible si no son válidos."""
    if clave not in SIMULADORES:
        raise ValueError(f"Simulador desconocido: {clave!r}.")
    sim = SIMULADORES[clave]
    completos = {**valores_por_defecto(clave), **{k: v for k, v in (valores or {}).items() if k in valores_por_defecto(clave)}}
    return sim.construir(completos)
