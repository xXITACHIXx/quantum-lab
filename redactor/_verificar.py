"""
redactor/_verificar.py — Revisión de un desarrollo matemático paso a paso
========================================================================

Cada línea es una expresión o una ecuación («x = A = B = C»: el primer «=» es la ecuación y A = B = C una cadena
de igualdades). Se comprueba que:
  1. en una cadena, cada expresión sea realmente igual a la siguiente;
  2. cada línea se deduzca de la anterior (misma ecuación reordenada o multiplicada por una constante, despeje de una
     variable, sustitución de datos numéricos, o una expresión igual a la última parte de la línea anterior).

La comparación NO es una prueba formal: se evalúan las dos expresiones en varios puntos aleatorios (semilla fija, reproducible)
y, si no coinciden, se intenta despejar con SymPy. Cuando no se puede decidir se dice «no verificable»; nunca se
declara correcto algo que no se comprobó. Si un paso falla, la ayuda sale del propio cálculo (lo que se obtiene al despejar,
o el factor constante que lo separa de lo escrito), no de una respuesta guardada.

Unidades (opcionales, entre corchetes: «3.97e-19 [J]») se revisan con `_unidades`; las leyes de `_leyes` permiten dar por válido
un paso que usa una relación estándar. No comprueba el significado físico.
"""

from __future__ import annotations

import concurrent.futures
import math
import random
from dataclasses import dataclass

import sympy as sp

from redactor import _leyes, _unidades
from redactor._expr import ErrorExpresion, a_latex, leer_expresion, partes_de_igualdad
from redactor._unidades import ErrorUnidades
from talleres._calificar import leer_numero

OK, ERROR, NO_VERIFICABLE, SINTAXIS, INICIO = "ok", "error", "no_verificable", "sintaxis", "inicio"
MAX_OPERACIONES = 250
PUNTOS = 9
ESCALAS = (1.0, 1e-19, 1e15)                # una identidad vale a cualquier escala; un número mal copiado solo se nota en la suya
TIEMPO_DESPEJE_S = 4.0
_VENTANA = (0.6, 2.4)                       # valores aleatorios positivos para las variables


@dataclass(frozen=True)
class Paso:
    texto: str
    estado: str                              # OK | ERROR | NO_VERIFICABLE | SINTAXIS | INICIO
    mensaje: str = ""
    esperado_latex: str = ""                 # expresión que sale del cálculo (despeje) cuando el paso es erróneo
    prueba: str = ""                         # "simbolica" (simplificación exacta) | "numerica" (puntos aleatorios) | ""
    unidades: str = ""                       # resultado de la revisión dimensional ("" si no había nada que revisar)


# ---------------------------------------------------------------------
# Comparación numérica de expresiones
# ---------------------------------------------------------------------
def _valores(simbolos, semilla: int):
    rng = random.Random(semilla)
    orden = sorted(simbolos, key=lambda x: x.name)
    return [{s: sp.Float(rng.uniform(*_VENTANA) * ESCALAS[i % len(ESCALAS)]) for s in orden} for i in range(PUNTOS)]


def _evaluar(expr, valores):
    """Valor numérico con 30 cifras (número de SymPy, posiblemente complejo), o None si no está definido."""
    try:
        v = sp.N(expr.subs(valores), 30)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        return None
    if not v.is_number or v.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        return None
    return v


def _pares(a, b, datos=None):
    """Valores (a, b) en varios puntos; con `datos`, los símbolos conocidos toman su valor y solo se sortean los demás."""
    datos = datos or {}
    libres = (a.free_symbols | b.free_symbols) - set(datos)
    salida = []
    for punto in _valores(libres, 12345):
        punto = {**punto, **datos}
        va, vb = _evaluar(a, punto), _evaluar(b, punto)
        if va is not None and vb is not None:
            salida.append((va, vb))
    return salida


def _cerca(va, vb, tol: float) -> bool:
    """|va − vb| ≤ tol·máx(|va|, |vb|): comparación RELATIVA (sirve igual con 1e-19 que con 1e+19). Dos ceros son iguales."""
    escala = max(abs(va), abs(vb))
    if escala == 0:
        return True
    return bool(abs(va - vb) <= tol * escala)


def _iguales(a, b, tol: float = 1e-9, datos=None) -> bool | None:
    """True/False si se pudo decidir con al menos 4 puntos válidos; None si no se pudo."""
    if sp.count_ops(a) + sp.count_ops(b) > MAX_OPERACIONES:
        return None
    pares = _pares(a, b, datos)
    if len(pares) < 4:
        return None
    return all(_cerca(va, vb, tol) for va, vb in pares)


def _razon_constante(f, g, datos=None):
    """k tal que f = k·g en todos los puntos (g ≠ 0), o None si no hay constante. Devuelve complex."""
    pares = [(vf, vg) for vf, vg in _pares(f, g, datos) if abs(vg) > sp.Float("1e-25")]
    if len(pares) < 4:
        return None
    k = pares[0][0] / pares[0][1]
    if all(_cerca(vf, k * vg, 1e-9) for vf, vg in pares):
        return complex(k)
    return None


# ---------------------------------------------------------------------
# Despeje con límite de tiempo y de tamaño
# ---------------------------------------------------------------------
def _despejar(ecuacion, simbolo) -> list | None:
    if sp.count_ops(ecuacion) > 80 or ecuacion.has(sp.sin, sp.cos, sp.tan, sp.exp, sp.log, sp.Abs):
        return None
    return _con_limite(sp.solve, ecuacion, simbolo, conversion=list)


def _con_limite(funcion, *args, conversion=None):
    """Ejecuta `funcion` con límite de tiempo. Si se pasa, devuelve None sin esperar a que termine el cálculo."""
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    futuro = ex.submit(funcion, *args)
    try:
        r = futuro.result(timeout=TIEMPO_DESPEJE_S)
        return conversion(r) if conversion else r
    except (concurrent.futures.TimeoutError, NotImplementedError, ValueError, TypeError, RecursionError):
        return None
    finally:
        ex.shutdown(wait=False, cancel_futures=True)


def _exactas(a, b) -> bool:
    """True si SymPy demuestra a − b = 0 por simplificación exacta (no por puntos). Falso si no pudo o tardó demasiado."""
    if sp.count_ops(a) + sp.count_ops(b) > 60:
        return False
    r = _con_limite(lambda: sp.simplify(sp.expand(a - b)) == 0)
    return bool(r)


def _describir_factor(k: complex) -> str:
    if abs(k.imag) > 1e-9:
        return ""
    k = k.real
    for valor, texto in ((-1.0, "tiene el signo contrario"), (2.0, "es el doble de lo esperado"),
                         (0.5, "es la mitad de lo esperado"), (4.0, "es cuatro veces lo esperado"),
                         (0.25, "es la cuarta parte de lo esperado"), (-2.0, "es el doble con signo contrario"),
                         (-0.5, "es la mitad con signo contrario")):
        if math.isclose(k, valor, rel_tol=1e-6):
            return f"Lo que escribiste {texto}."
    return f"Lo que escribiste difiere de lo esperado por un factor constante de {k:.6g}."


# ---------------------------------------------------------------------
# Lectura de líneas
# ---------------------------------------------------------------------
def leer_datos(datos: dict | None) -> dict:
    """{'m': '9.109e-31 [kg]', ...} → {Symbol('m'): Float en SI}. Lanza ErrorExpresion si algo no se entiende."""
    return _leer_datos_con_unidades(datos)[0]


def _leer_datos_con_unidades(datos: dict | None, unidades: dict | None = None) -> tuple[dict, dict]:
    """(valores en SI, dimensiones). `unidades` {'E': 'J'} declara la unidad de variables sin valor."""
    valores, dims = {}, {}
    for nombre, valor in (datos or {}).items():
        nombre = str(nombre).strip()
        if not nombre:
            continue
        simbolo = leer_expresion(nombre)
        if not isinstance(simbolo, sp.Symbol):
            raise ErrorExpresion(f"«{nombre}» no es un nombre de variable válido para un dato.")
        try:
            numero, unidad = _unidades.separar_unidad(str(valor))
            factor, dim = unidad if unidad else (1.0, None)
            valores[simbolo] = sp.Float(leer_numero(numero)) * sp.Float(factor)
            if dim is not None:
                dims[simbolo] = dim
        except ErrorUnidades as error:
            raise ErrorExpresion(f"La unidad de {nombre}: {error}") from None
        except ValueError as error:
            raise ErrorExpresion(f"El valor de {nombre}: {error}") from None
    for nombre, texto in (unidades or {}).items():
        simbolo = leer_expresion(str(nombre).strip())
        if not isinstance(simbolo, sp.Symbol):
            raise ErrorExpresion(f"«{nombre}» no es un nombre de variable válido para declarar su unidad.")
        try:
            dims[simbolo] = _unidades.leer_unidad(texto)[1]
        except ErrorUnidades as error:
            raise ErrorExpresion(f"La unidad de {nombre}: {error}") from None
    return valores, dims


def _leer_linea(texto: str):
    """Lista de expresiones de una línea («a = b = c» → [a, b, c]). Lanza ErrorExpresion."""
    return _leer_linea_con_unidades(texto)[0]


def _leer_linea_con_unidades(texto: str):
    """
    (expresiones en SI, unidades declaradas por parte, texto sin corchetes). «500 [nm]» se lee como 5e-7 con dimensión m.
    Lanza ErrorExpresion (también por una unidad mal escrita).
    """
    partes = partes_de_igualdad(texto)
    if not partes or any(not p for p in partes):
        raise ErrorExpresion("Falta una expresión a un lado del signo «=».")
    expresiones, declaradas, limpias = [], [], []
    for p in partes:
        try:
            sin_unidad, unidad = _unidades.separar_unidad(p)
        except ErrorUnidades as error:
            raise ErrorExpresion(f"Unidad: {error}") from None
        e = leer_expresion(sin_unidad)
        if unidad and unidad[0] != 1.0:
            e = e * sp.Float(unidad[0])
        expresiones.append(e)
        declaradas.append(unidad[1] if unidad else None)
        limpias.append(sin_unidad)
    return expresiones, declaradas, " = ".join(limpias)


def _revisar_unidades(partes, declaradas, tabla, texto_limpio) -> tuple[bool, str]:
    """(hay_error, mensaje). Mensaje vacío si no se pudo revisar nada. Compara la dimensión de todas las partes de la línea."""
    dims = []
    for expr, decl in zip(partes, declaradas, strict=True):
        try:
            d = _unidades.dimension(expr, tabla)
        except ErrorUnidades as error:
            return True, f"Unidades: {error}"
        if decl is not None:
            if d is not None and d != _unidades.CERO and d != decl:
                return True, f"Unidades: la expresión resulta {_unidades.escribir(d)} y la marcaste como {_unidades.escribir(decl)}."
            d = decl
        dims.append(d)
    conocidas = [(i, d) for i, d in enumerate(dims) if d is not None]
    if len(conocidas) < 2:
        return False, ""
    nombres = [p.strip() for p in texto_limpio.split("=")]
    for i, d in conocidas[1:]:
        if d != conocidas[0][1]:
            return True, (f"Unidades: «{nombres[conocidas[0][0]]}» es {_unidades.escribir(conocidas[0][1])} pero "
                          f"«{nombres[i]}» es {_unidades.escribir(d)}; no pueden ser iguales.")
    return False, f"Las unidades coinciden ({_unidades.escribir(conocidas[0][1])})."


# ---------------------------------------------------------------------
# Verificación
# ---------------------------------------------------------------------
def _cadena_consistente(partes, tol, datos) -> tuple[bool | None, int]:
    """Comprueba que las expresiones consecutivas de la cadena sean iguales. Devuelve (resultado, índice de la 1.ª pareja que falla)."""
    incierto = False
    for i in range(len(partes) - 1):
        r = _iguales(partes[i], partes[i + 1], datos=None)
        if r is False and datos and (partes[i].free_symbols | partes[i + 1].free_symbols) <= set(datos):
            r = _iguales(partes[i], partes[i + 1], tol=tol, datos=datos)       # sustitución numérica con tolerancia
        if r is False:
            return False, i
        incierto = incierto or r is None
    return (None if incierto else True), -1


def _definiciones(contexto) -> list[tuple[sp.Symbol, sp.Expr]]:
    """Igualdades «símbolo = expresión» de las líneas anteriores (el símbolo no aparece en la expresión)."""
    salida = []
    for partes in contexto:
        if len(partes) < 2:
            continue
        for s_, e_ in ((partes[0], partes[-1]), (partes[-1], partes[0])):
            if isinstance(s_, sp.Symbol) and s_ not in e_.free_symbols and not e_.is_number:
                salida.append((s_, e_))
                break
    return salida


def _es_monomio(expr) -> bool:
    """Producto de potencias de símbolos y números (sin sumas): un factor por el que se multiplicó ambos lados."""
    return not expr.has(sp.Add) and expr != 0


def _misma_relacion(d_actual, d_previo, datos) -> str:
    """Texto que explica por qué las dos ecuaciones (como «lado − lado») son la misma, o '' si no lo son."""
    k = _razon_constante(d_actual, d_previo, datos)
    if k is not None and abs(k) > 1e-12:
        return "Es la misma ecuación de la línea anterior (reordenada o multiplicada por una constante)."
    if sp.count_ops(d_actual) + sp.count_ops(d_previo) <= MAX_OPERACIONES:
        try:
            factor = sp.cancel(sp.together(d_actual / d_previo))
        except (ZeroDivisionError, TypeError, ValueError, sp.PolynomialError):
            return ""
        if factor.is_number is False and _es_monomio(factor) and factor.free_symbols:
            return f"Se multiplicaron o dividieron ambos lados de la línea anterior por {sp.latex(sp.simplify(factor))}."
    return ""


def _deduce(contexto, actual, tol, datos) -> tuple[str, str, str]:
    """Estado, mensaje y ayuda de la relación entre la línea anterior (la última de `contexto`) y la actual."""
    anterior = contexto[-1]
    definiciones = _definiciones(contexto)
    ult_prev = anterior[-1]

    if len(actual) == 1:                                                  # solo una expresión: continúa la anterior
        candidatos = [ult_prev] + [ult_prev.subs(s_, e_) for s_, e_ in definiciones if s_ in ult_prev.free_symbols]
        for c in candidatos:
            r = _iguales(c, actual[0])
            if r is False and datos and (c.free_symbols | actual[0].free_symbols) <= set(datos):
                r = _iguales(c, actual[0], tol=tol, datos=datos)
            if r is True:
                return OK, "Igual a la última expresión de la línea anterior" + (" (con una sustitución)." if c is not ult_prev else "."), ""
        simbolos_ok = set().union(*[p.free_symbols for linea in contexto for p in linea]) if contexto else set()
        if not actual[0].free_symbols <= simbolos_ok:
            return NO_VERIFICABLE, "Aparecen símbolos que no estaban antes: no puedo comprobar este paso.", ""
        k = _razon_constante(actual[0], ult_prev, datos)
        return ERROR, "No es igual a la última expresión de la línea anterior. " + (_describir_factor(k) if k is not None else ""), \
            a_latex(ult_prev)

    izq1, der1 = anterior[0], anterior[-1]
    izq2, der2 = actual[0], actual[-1]
    d1, d2 = izq1 - der1, izq2 - der2
    # (a) misma ecuación: reordenada, multiplicada por una constante o por un monomio
    explicacion = _misma_relacion(d2, d1, None)
    if explicacion:
        return OK, explicacion, ""
    # (b) sustitución de definiciones de líneas anteriores (p. ej. «p = nπħ/a» en «E = p²/2m», que es la línea 1, no la anterior)
    for k_linea in range(len(contexto) - 1, -1, -1):
        base = contexto[k_linea][0] - contexto[k_linea][-1]
        if k_linea < len(contexto) - 1 and _misma_relacion(d2, base, None):
            return OK, f"Se obtiene de la línea {k_linea + 1} (reordenada o multiplicada por un factor).", ""
        for s_, e_ in definiciones:
            if s_ in base.free_symbols and _misma_relacion(d2, base.subs(s_, e_), None):
                return OK, f"Se obtiene sustituyendo {s_} = {e_} en la línea {k_linea + 1}.", ""
        if len(definiciones) >= 2:                                        # varias sustituciones a la vez
            base_s = base
            for _ in range(3):
                for s_, e_ in definiciones:
                    base_s = base_s.subs(s_, e_)
            if base_s != base and _misma_relacion(d2, base_s, None):
                return OK, f"Se obtiene sustituyendo las definiciones anteriores en la línea {k_linea + 1}.", ""
    # (c) despeje de una variable
    candidatos = [s for s in (izq2, der2) if isinstance(s, sp.Symbol) and s in d1.free_symbols]
    for s in candidatos:
        otro = der2 if s is izq2 else izq2
        if s in otro.free_symbols:
            continue
        sols = _despejar(sp.Eq(izq1, der1), s)
        if not sols:
            continue
        for sol in sols:
            if _iguales(sol, otro) is True:
                return OK, f"Es el despeje de {s} en la línea anterior.", ""
        for sol in sols:                                                  # sustitución numérica con los datos
            if datos and (sol.free_symbols | otro.free_symbols) <= set(datos) and _iguales(sol, otro, tol=tol, datos=datos) is True:
                return OK, f"Coincide con {s} calculado con los datos (tolerancia {tol * 100:.2g} %).", ""
        conocidos = set().union(*[p.free_symbols for linea in contexto for p in linea]) | set(datos or {})
        if not (izq2.free_symbols | der2.free_symbols) <= conocidos:
            return NO_VERIFICABLE, "Aparecen símbolos que no estaban antes: no puedo comprobar este paso como un despeje.", ""
        esperado = sols[0] if len(sols) == 1 else min(sols, key=sp.count_ops)
        k = _razon_constante(otro, esperado, datos)
        ayuda = _describir_factor(k) if k is not None else ""
        return ERROR, (f"No se obtiene de la línea anterior al despejar {s}. " + ayuda).strip(), f"{a_latex(s)} = {a_latex(esperado)}"
    # (d) datos numéricos sustituidos en una ecuación sin variables libres
    if datos and (d1.free_symbols | d2.free_symbols) <= set(datos):
        r = _razon_constante(d2, d1, datos)
        if r is not None:
            return OK, "Es la ecuación anterior con los datos sustituidos.", ""
    return NO_VERIFICABLE, ("No pude relacionar esta línea con la anterior: puede ser un paso válido que no sé comprobar "
                            "(por ejemplo, una ley nueva, un cambio de variable o una simplificación con unidades)."), ""


def _prueba(contexto, partes, datos) -> str:
    """«simbolica» si la igualdad se demuestra por simplificación exacta; «numerica» si solo se comprobó en puntos; «» si no aplica."""
    if datos:
        return "numerica"
    if len(partes) >= 3:
        return "simbolica" if all(_exactas(partes[k], partes[k + 1]) for k in range(1, len(partes) - 1)) else "numerica"
    if len(partes) == 1 and contexto:
        return "simbolica" if _exactas(contexto[-1][-1], partes[0]) else "numerica"
    return "numerica"


def _con_leyes(contexto, partes, tol, datos):
    """
    Si el paso se deduce de la línea anterior usando una ley estándar, (OK, mensaje); si no, None. Se prueba (1) la ley como una
    línea más del contexto y (2) despejar cada símbolo de la ley y sustituirlo en la línea anterior (p. ej. ν = c/λ en E = hν).
    """
    simbolos = set().union(*[p.free_symbols for p in partes])
    anterior = contexto[-1]
    previos = set().union(*[p.free_symbols for p in anterior])
    aviso = "Usa la ley «{}» (si tus símbolos tienen su significado habitual)."
    for nombre, texto in _leyes.LEYES:
        ley = [leer_expresion(x) for x in partes_de_igualdad(texto)]
        simbolos_ley = set().union(*[p.free_symbols for p in ley])
        if not simbolos_ley & (simbolos | previos):
            continue
        estado, mensaje, _ = _deduce([*contexto[:-1], ley, anterior], partes, tol, datos)
        if estado == OK:
            return OK, f"{mensaje} {aviso.format(nombre)}"
        for s in sorted(simbolos_ley & previos, key=lambda x: x.name):
            sols = _despejar(sp.Eq(ley[0], ley[-1]), s)
            if not sols or len(sols) != 1:
                continue
            sustituida = [x.subs(s, sols[0]) for x in anterior]
            estado, mensaje, _ = _deduce([*contexto[:-1], sustituida], partes, tol, datos)
            if estado == OK:
                return OK, f"Sustituyendo {s} = {sols[0]} en la línea anterior se obtiene este paso. {aviso.format(nombre)}"
    return None


def verificar_pasos(lineas: list[str], datos: dict | None = None, tol_rel: float = 0.01, unidades: dict | None = None) -> list[Paso]:
    """
    Revisa un desarrollo. `datos`: valores de las variables (texto; con unidad opcional «6.626e-34 [J s]»); `tol_rel`: tolerancia al
    sustituir números; `unidades`: unidad de variables sin valor ({'E': 'J'}).
    """
    try:
        valores, tabla_dims = _leer_datos_con_unidades(datos, unidades)
    except ErrorExpresion as error:
        return [Paso(t, SINTAXIS, f"Datos conocidos: {error}") for t in lineas] or []
    resultados: list[Paso] = []
    contexto: list = []
    saltadas = 0                              # líneas erróneas desde la última válida: no se usan como referencia
    for texto in lineas:
        if not str(texto).strip():
            continue
        try:
            partes, declaradas, limpio = _leer_linea_con_unidades(texto)
        except ErrorExpresion as error:
            resultados.append(Paso(texto, SINTAXIS, str(error)))
            saltadas += 1
            continue
        error_u, msg_u = _revisar_unidades(partes, declaradas, tabla_dims, limpio)
        if error_u:
            resultados.append(Paso(texto, ERROR, msg_u, "", "", msg_u))
            saltadas += 1
            continue
        # «x = A = B = C»: el primer «=» es la ecuación; las expresiones A, B, C son una cadena de igualdades que debe cumplirse
        cadena, falla = _cadena_consistente(partes[1:], tol_rel, valores)
        if cadena is False:
            resultados.append(Paso(texto, ERROR, f"Las expresiones «{_leer_texto(limpio, falla + 1)}» y «{_leer_texto(limpio, falla + 2)}» "
                                                 "no son iguales.", ""))
            saltadas += 1
        elif not contexto:
            msg = "Primera línea: no se compara con nada." if cadena is not None else \
                  "Primera línea; no pude comprobar la igualdad interna."
            prueba = _prueba(contexto, partes, valores) if cadena and len(partes) >= 3 else ""
            resultados.append(Paso(texto, INICIO if cadena is not None else NO_VERIFICABLE, msg, "", prueba, msg_u))
        else:
            estado, mensaje, ayuda = _deduce(contexto, partes, tol_rel, valores)
            if estado == NO_VERIFICABLE:
                con_ley = _con_leyes(contexto, partes, tol_rel, valores)
                if con_ley:
                    estado, mensaje = con_ley
            if saltadas and estado == ERROR:
                mensaje += " (Se compara con la última línea correcta, no con las que tienen error.)"
            if estado == ERROR:
                resultados.append(Paso(texto, estado, mensaje, ayuda))
                saltadas += 1
                continue
            saltadas = 0
            if cadena is None and estado == OK:
                estado, mensaje = NO_VERIFICABLE, "Se deduce de la anterior, pero no pude comprobar la igualdad interna de la línea."
            prueba = _prueba(contexto, partes, valores) if estado == OK else ""
            resultados.append(Paso(texto, estado, mensaje, ayuda, prueba, msg_u))
        saltadas = 0
        contexto.append(partes)
    return resultados


def _leer_texto(texto: str, indice: int) -> str:
    partes = partes_de_igualdad(texto)
    return partes[indice].strip() if 0 <= indice < len(partes) else ""


def resumen(pasos: list[Paso]) -> dict:
    """Conteo por estado, para mostrar «3 pasos correctos, 1 con error, 1 no verificable»."""
    cuentas = {OK: 0, ERROR: 0, NO_VERIFICABLE: 0, SINTAXIS: 0, INICIO: 0}
    for p in pasos:
        cuentas[p.estado] += 1
    return cuentas

