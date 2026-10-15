"""
python -m ejercicios — Informe de mantenimiento de los Ejercicios de práctica.

Revisa las reglas de calidad de cada ejercicio, las pruebas numéricas internas y resume qué hay por fuente, semana y tema.
Termina con código de salida 1 si algo falla (útil antes de publicar).
"""

import sys
from collections import Counter

import ejercicios
from ejercicios import _calidad, _figuras
from ejercicios._modelo import TEMAS


def main() -> int:
    problemas = {e.id: _calidad.revisar(e) for e in ejercicios.EJERCICIOS}
    problemas = {k: v for k, v in problemas.items() if v}
    reg = ejercicios.ejecutar_pruebas()
    fallos = [r for r in reg.resultados if not r["ok"]]

    print(f"Ejercicios: {len(ejercicios.EJERCICIOS)}  ·  con comprobación: {sum(e.comprobable for e in ejercicios.EJERCICIOS)}  "
          f"·  con gráfica: {len(_figuras.FIGURAS)}")
    print("Por fuente:", dict(Counter(e.fuente for e in ejercicios.EJERCICIOS)))
    print("Por semana:", dict(sorted(Counter(e.referencia.split(' ·')[0] for e in ejercicios.EJERCICIOS).items())))
    print("Por tema:", {TEMAS[k]: v for k, v in sorted(Counter(e.tema for e in ejercicios.EJERCICIOS).items())})
    print(f"Pruebas internas: {len(reg.resultados) - len(fallos)}/{len(reg.resultados)} correctas")
    for r in fallos:
        print("  FALLA:", r["Prueba"], r["Detalle"])
    for ej_id, lista in problemas.items():
        for m in lista:
            print(f"  CALIDAD [{ej_id}]: {m}")
    return 1 if (problemas or fallos) else 0


if __name__ == "__main__":
    sys.exit(main())
