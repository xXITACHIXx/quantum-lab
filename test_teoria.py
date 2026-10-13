"""
Pruebas numéricas de los módulos del Centro de teoría: cada función de cálculo se contrasta con un valor conocido
o con un cálculo independiente (integración numérica, constantes tabuladas).
"""
import math

import numpy as np
import pytest
from scipy.integrate import trapezoid

from teoria import (caja, conmutadores, criterios, cuerpo_negro, de_broglie, esfera, libre_pared, ondas, operadores,
                    oscilador, postulados, schrodinger)
from teoria._util import C, EV, H, KB, SIGMA


def test_wien_y_stefan_boltzmann():
    T = 5772.0
    lam = np.linspace(50e-9, 5e-6, 800001)
    pico = lam[np.argmax(cuerpo_negro.planck(lam, T))]
    assert pico == pytest.approx(cuerpo_negro.lambda_max(T), rel=1e-4)
    assert cuerpo_negro.B_WIEN == pytest.approx(2.897771955e-3, rel=1e-8)
    lf = np.linspace(20e-9, 200e-6, 1000001)
    total = trapezoid(cuerpo_negro.planck(lf, T), lf)
    assert total == pytest.approx(4 * SIGMA / C * T ** 4, rel=1e-6)


def test_planck_tiende_a_rayleigh_jeans_a_longitudes_largas():
    T = 3000.0
    lam = 1e-2
    assert cuerpo_negro.planck(lam, T) == pytest.approx(cuerpo_negro.rayleigh_jeans(lam, T), rel=1e-3)


def test_energia_media_limites_clasico_y_cuantico():
    T = 300.0
    assert cuerpo_negro.energia_media_planck(1e9, T) == pytest.approx(KB * T, rel=1e-3)
    assert cuerpo_negro.energia_media_planck(1e15, T) < 1e-30 * KB * T


def test_de_broglie_valores_conocidos():
    assert de_broglie.lambda_desde_energia(9.1093837e-31, 54 * EV) == pytest.approx(0.1669e-9, rel=2e-3)
    assert de_broglie.energia_para_lambda(9.1093837e-31, 0.30e-9) == pytest.approx(2.68e-18, rel=5e-3)
    assert 1.226e-9 / math.sqrt(100) == pytest.approx(de_broglie.lambda_desde_energia(9.1093837e-31, 100 * EV), rel=1e-3)
    assert de_broglie.longitud_de_onda(0.145, 40.0) < 1e-30


def test_boltzmann():
    assert criterios.razon_de_poblaciones(10 * criterios.kT_ev(298), 298) == pytest.approx(math.exp(-10), rel=1e-12)
    assert criterios.razon_de_poblaciones(0.1, 298, 3, 1) == pytest.approx(3 * math.exp(-0.1 / criterios.kT_ev(298)))
    assert criterios.kT_ev(298) == pytest.approx(0.02568, rel=2e-3)
    assert criterios.espaciado_traslacional_ev(4.65e-26, 1e-2) < 1e-18


def test_ecuacion_de_onda_se_cumple():
    assert ondas.residuo_ecuacion_de_onda() < 1e-5
    x = np.linspace(0, 3, 50)
    est = ondas.onda_estacionaria(x, 0.37, 1.0, 2.0, 5.0)
    assert np.allclose(est, 2 * np.sin(2.0 * x) * np.cos(5.0 * 0.37))


@pytest.mark.parametrize("sistema,n", [("caja", 400), ("oscilador", 800)])
def test_schrodinger_numerico(sistema, n):
    _, E, psi, exactas = schrodinger.energias_numericas(sistema, n)
    assert np.all(np.abs(E - exactas) / exactas < 1e-3)
    dx = _[1] - _[0]
    assert np.allclose(np.sum(psi ** 2, axis=0) * dx, 1.0, atol=1e-9)


def test_autofunciones_y_operadores():
    assert operadores.probar_autofuncion("e^(i·2x)", "d/dx") == (True, pytest.approx(2j))
    ok, lam = operadores.probar_autofuncion("sin(2x)", "d²/dx²")
    assert ok and lam == pytest.approx(-4)
    assert not operadores.probar_autofuncion("sin(2x)", "d/dx")[0]
    ok, lam = operadores.probar_autofuncion("e^(i·2x)", "p̂ = −i d/dx  (ħ = 1)")
    assert ok and lam == pytest.approx(2)


def test_ortonormalidad_y_completitud():
    S = operadores.matriz_de_solapamiento(6)
    assert np.allclose(S, np.eye(6), atol=1e-7)
    x, psi, b, aprox = operadores.desarrollar("Parábola x(L − x)", 40)
    assert np.sum(b[:40] ** 2) == pytest.approx(1.0, abs=1e-6)
    assert trapezoid((psi - aprox) ** 2, x) < 1e-6


def test_normalizacion_analitica():
    for nombre in ("x(a − x) en [0, a]", "sin(πx/a) en [0, a]", "e^(−x/a) en [0, ∞)"):
        num, ana, _ = operadores.constante_de_normalizacion(nombre, 3.7)
        assert num == pytest.approx(ana, rel=1e-8)


@pytest.mark.parametrize("coef", [[1, 0.8, 0, 0.4], [1, 0, 0, 0], [0.3, 0.3, 0.3, 0.3], [0, 0, 0, 1]])
def test_valor_esperado_de_la_energia(coef):
    assert postulados.energia_esperada(coef) == pytest.approx(postulados.energia_esperada_por_integral(coef), rel=1e-6)
    p = postulados.probabilidades(coef)
    assert p.sum() == pytest.approx(1.0)


def test_medidas_solo_dan_autovalores_y_convergen():
    medidas = postulados.simular_medidas([1, 0.8, 0, 0.4], 200000, 3)
    assert set(np.unique(medidas)) <= {1, 4, 9, 16}
    assert medidas.mean() == pytest.approx(postulados.energia_esperada([1, 0.8, 0, 0.4]), rel=2e-2)
    with pytest.raises(ValueError):
        postulados.probabilidades([0, 0, 0, 0])


def test_conmutadores_conocidos():
    x = np.linspace(-2, 2, 9)
    for A, B in [("x̂", "p̂"), ("p̂", "x̂"), ("x̂", "p̂²"), ("x̂²", "p̂"), ("p̂", "T̂ = p̂²/2"), ("x̂", "x̂²")]:
        assert np.allclose(conmutadores.conmutador_numerico(A, B, x), conmutadores.conmutador_esperado(A, B, x), atol=1e-4)


@pytest.mark.parametrize("n", [1, 2, 5, 20])
def test_incertidumbre_en_la_caja(n):
    dx, dp, prod = conmutadores.incertidumbres_caja(n)
    dxn, dpn, prodn = conmutadores.incertidumbres_caja_numericas(n)
    assert prod == pytest.approx(prodn, rel=1e-6)
    assert prod > 0.5


def test_estado_fundamental_de_la_caja():
    assert conmutadores.incertidumbres_caja(1)[2] == pytest.approx(math.sqrt((math.pi ** 2 - 6) / 12), rel=1e-12)
    assert conmutadores.incertidumbres_caja(1)[2] == pytest.approx(0.568, abs=1e-3)


# ---------------------------------------------------------------- semana 5: partícula libre y pared
def test_pared_continuidad_y_reflexion_total():
    k = libre_pared.numero_de_onda(9.1093837e-31, 1 * EV)
    kap = libre_pared.kappa(9.1093837e-31, 3 * EV, 1 * EV)
    _, R, T = libre_pared.funcion_de_onda_pared(np.array([0.0]), k, kap)
    assert abs(R) == pytest.approx(1.0, abs=1e-12)
    assert abs(T) ** 2 == pytest.approx(4 * 1 / 3, rel=1e-12)                 # |T|² = 4E/V
    h = 1e-15
    f = lambda x: libre_pared.funcion_de_onda_pared(np.array([x]), k, kap)[0][0]
    assert f(-h) == pytest.approx(f(h), rel=1e-4)                              # ψ continua en x = 0
    assert (f(-h) - f(-2 * h)) / h == pytest.approx((f(2 * h) - f(h)) / h, rel=1e-4)   # ψ' continua


def test_profundidad_de_penetracion():
    me = 9.1093837e-31
    assert libre_pared.profundidad_de_penetracion(me, 2 * EV, 1 * EV) == pytest.approx(0.1952e-9, rel=1e-3)
    assert libre_pared.profundidad_de_penetracion(me, 5 * EV, 1 * EV) == pytest.approx(0.0976e-9, rel=1e-3)
    with pytest.raises(ValueError):
        libre_pared.kappa(me, 1 * EV, 2 * EV)


# ---------------------------------------------------------------- semana 6: caja
def test_caja_probabilidades_y_energias():
    assert caja.probabilidad_en_intervalo(1, 1 / 3, 2 / 3) == pytest.approx(1 / 3 + math.sqrt(3) / (2 * math.pi), rel=1e-12)
    for n in (1, 3, 8):
        assert caja.probabilidad_en_intervalo(n, 0.2, 0.9) == pytest.approx(caja.probabilidad_numerica(n, 0.2, 0.9), rel=1e-9)
        assert caja.probabilidad_en_intervalo(n, 0, 1) == pytest.approx(1.0)
    assert caja.energia_caja(2, 9.1093837e-31, 1e-9) == pytest.approx(4 * caja.energia_caja(1, 9.1093837e-31, 1e-9))
    assert caja.energia_caja(1, 9.1093837e-31, 1e-9) / EV == pytest.approx(0.3760, rel=1e-3)
    assert caja.separacion_relativa(1000) == pytest.approx(2001 / 1e6)


def test_caja_3d_degeneraciones():
    cubo = {round(e, 6): g for e, g, _ in caja.niveles_caja_3d(1, 1, cuantos=8)}
    assert cubo[3.0] == 1 and cubo[6.0] == 3 and cubo[9.0] == 3 and cubo[12.0] == 1 and cubo[14.0] == 6
    assert all(g == 1 or g == 3 or g == 6 for g in cubo.values())
    asim = caja.niveles_caja_3d(1.37, 1.91, cuantos=6)
    assert all(g == 1 for _, g, _ in asim)                                    # sin simetría no hay degeneración


# ---------------------------------------------------------------- semana 9: oscilador
def test_oscilador_hermite_energias_y_virial():
    assert np.allclose(oscilador.nodos(4), [-1.6507, -0.5246, 0.5246, 1.6507], atol=1e-4)
    z = np.linspace(-14, 14, 40001)
    for n in (0, 1, 4, 9):
        assert trapezoid(oscilador.psi(n, z) ** 2, z) == pytest.approx(1.0, abs=1e-9)
    assert trapezoid(oscilador.psi(2, z) * oscilador.psi(5, z), z) == pytest.approx(0.0, abs=1e-12)
    for n in (0, 1, 2, 5):
        T, V = oscilador.energias_medias_adimensionales(n)
        assert T == pytest.approx(V, abs=1e-5)
        assert T + V == pytest.approx(n + 0.5, abs=1e-4)


def test_oscilador_moleculas_y_gaussiana():
    for nombre, (mu_u, w) in oscilador.MOLECULAS.items():
        mu = mu_u * oscilador.U_MASA
        k = oscilador.constante_de_fuerza(mu, w)
        assert oscilador.frecuencia(mu, k) / (C * 100) == pytest.approx(w, rel=1e-9)
    assert oscilador.constante_de_fuerza(oscilador.MOLECULAS["HCl (H³⁵Cl)"][0] * oscilador.U_MASA, 2990.95) == pytest.approx(516, rel=2e-3)
    mu = oscilador.MOLECULAS["CO"][0] * oscilador.U_MASA
    k = oscilador.constante_de_fuerza(mu, 2169.81)
    from teoria._util import HBAR
    assert math.sqrt(k * mu) / (2 * HBAR) == pytest.approx(oscilador.alfa(mu, k) ** 2 / 2, rel=1e-12)
    assert oscilador.energia(0, mu, k) == pytest.approx(0.5 * H * oscilador.frecuencia(mu, k))


# ---------------------------------------------------------------- semana 10: rotación
@pytest.mark.parametrize("l,m", [(0, 0), (1, 0), (1, 1), (2, -1), (5, 3), (8, -8)])
def test_armonicos_son_autofunciones_del_legendriano(l, m):
    assert esfera.autovalor_legendriano(l, m) == pytest.approx(l * (l + 1), abs=2e-3)


def test_anillo_y_esfera():
    I = esfera.momento_de_inercia(1.67e-27, 1e-10)
    assert esfera.energia_anillo(2, I) == pytest.approx(4 * esfera.energia_anillo(1, I))
    assert esfera.energia_esfera(1, I) == pytest.approx(2 * esfera.energia_anillo(1, I) )
    phi = np.linspace(0, 2 * np.pi, 20001)
    for m in (0, 1, -3):
        assert trapezoid(np.abs(esfera.phi_anillo(m, phi)) ** 2, phi) == pytest.approx(1.0, abs=1e-9)
    assert esfera.angulo_minimo(1000) == pytest.approx(1.8112, abs=1e-3)
    assert len(esfera.angulos_permitidos(1000)) == 2001


def test_constantes_rotacionales_conocidas():
    from teoria._util import HBAR
    esperadas = {"H₂": 60.85, "HCl (H³⁵Cl)": 10.59, "CO": 1.931, "N₂": 1.998, "O₂": 1.438}
    for nombre, (mu_u, r_pm) in esfera.MOLECULAS.items():
        I = esfera.momento_de_inercia(mu_u * esfera.U_MASA, r_pm * 1e-12)
        B = HBAR / (4 * math.pi * C * 100 * I)
        assert B == pytest.approx(esperadas[nombre], rel=6e-3)
