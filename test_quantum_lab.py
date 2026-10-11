"""Pruebas con pytest:  pytest -q   (ejecuta las comprobaciones numéricas de los tres simuladores)."""
import pytest

import oscilador_armonico
import particula_caja
import particula_esfera

MODULOS = [particula_caja, oscilador_armonico, particula_esfera]


@pytest.mark.parametrize("modulo", MODULOS, ids=lambda m: m.__name__)
def test_pruebas_numericas(modulo):
    registro = modulo.ejecutar_pruebas()
    fallos = [r["Prueba"] + "  " + r["Detalle"] for r in registro.resultados if not r["ok"]]
    assert not fallos, "Pruebas fallidas:\n" + "\n".join(fallos)
    assert len(registro.resultados) >= 25
