"""Pruebas con pytest:  pytest -q   (comprobaciones numéricas de los simuladores y de la verificación)."""
import csv
import io

import numpy as np
import pytest

import efecto_fotoelectrico
import modelo_bohr
import oscilador_armonico
import particula_caja
import particula_esfera
import principio_incertidumbre
import quantum_lab_comun as qc
import teoria
import verificacion

MODULOS = [particula_caja, oscilador_armonico, particula_esfera, efecto_fotoelectrico, modelo_bohr,
           principio_incertidumbre, verificacion]


@pytest.mark.parametrize("modulo", MODULOS, ids=lambda m: m.__name__)
def test_pruebas_numericas(modulo):
    registro = modulo.ejecutar_pruebas()
    fallos = [r["Prueba"] + "  " + r["Detalle"] for r in registro.resultados if not r["ok"]]
    assert not fallos, "Pruebas fallidas:\n" + "\n".join(fallos)
    assert len(registro.resultados) >= 20


def test_verificacion_cubre_todos_los_sistemas():
    sistemas = {c["sistema"] for c in verificacion.casos_de_verificacion()}
    assert len(sistemas) == 6
    r = verificacion.resumen(verificacion.casos_de_verificacion())
    assert r["ok"] == r["total"] and r["error_max"] < 2e-3


def test_valores_por_defecto_compartidos_con_colab():
    """Los notebooks de Colab abren con los mismos valores: caja n = 1, oscilador n = 0, esfera l = 2, m = 1."""
    assert particula_caja.VALORES_INICIALES["caja_n"] == 1
    assert particula_caja.VALORES_INICIALES["caja_longitud"] == 1.0
    assert oscilador_armonico.VALORES_INICIALES["osc_n"] == 0
    assert oscilador_armonico.VALORES_INICIALES["osc_omega"] == "1e15"
    ve = particula_esfera.VALORES_INICIALES
    assert (ve["esf_l"], ve["esf_m"], ve["esf_modo"], ve["esf_forma"]) == (2, 1, "densidad", "lobulos")
    assert ve["esf_alfa"] == 0.4 and ve["esf_ntheta"] == 90


def test_csv_de_columnas():
    datos = qc.csv_de_columnas({"x": np.arange(3.0), "psi": np.array([1 + 2j, 3, 4j])}).decode("utf-8-sig")
    filas = list(csv.reader(io.StringIO(datos)))
    assert filas[0] == ["x", "Re psi", "Im psi"]
    assert filas[3] == ["2", "0", "4"]
    with pytest.raises(ValueError):
        qc.csv_de_columnas({"a": [1, 2], "b": [1, 2, 3]})


def test_lista_rapida_de_estados():
    numeros, c = particula_caja.leer_lista_estados("1:1; 2:0,5\n7:-0.3:1.0")
    assert numeros == [1, 2, 7] and abs(c[1] - 0.5) < 1e-15
    # amplitud negativa = amplitud positiva con la fase aumentada en π
    assert abs(abs(c[2]) - 0.3) < 1e-12 and abs(np.exp(1j * np.angle(c[2])) - np.exp(1j * (1.0 + np.pi))) < 1e-12
    for malo in ("2.5:1", "1:2:3:4", "a:1", " ; "):
        with pytest.raises(ValueError):
            particula_caja.leer_lista_estados(malo)


def test_centro_de_teoria_indice_consistente():
    registro = teoria.ejecutar_pruebas()
    fallos = [r["Prueba"] for r in registro.resultados if not r["ok"]]
    assert not fallos, fallos
