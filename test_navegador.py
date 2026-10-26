"""
test_navegador.py — Recorrido en un navegador real (Chromium + Playwright) de los seis simuladores
==================================================================================================

Arranca la aplicación con `streamlit run` y recorre las pestañas nuevas. Comprueba que se muestren los resultados y que no
aparezca ninguna excepción de Streamlit ni error de JavaScript. Se omite si Playwright o Chromium no están instalados.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

RAIZ = Path(__file__).parent
SIMULADORES = {            # página → (tiene laboratorio inverso, pestaña de instrumentos)
    "caja": (True, None),
    "oscilador": (True, "Instrumentos e informe"),
    "fotoelectrico": (True, "Instrumentos e informe"),
    "bohr": (True, "Instrumentos e informe"),
    "esfera": (True, "Instrumentos e informe"),
    "incertidumbre": (True, "Instrumentos e informe"),
}


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def servidor():
    puerto = _puerto_libre()
    proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "quantum_lab.py", "--server.headless", "true",
                             "--server.port", str(puerto), "--browser.gatherUsageStats", "false"], cwd=RAIZ,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{puerto}"
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(f"{url}/_stcore/health", timeout=2)
                break
            except OSError:
                time.sleep(1)
        else:
            pytest.skip("No se pudo arrancar el servidor de Streamlit.")
        yield url
    finally:
        proc.terminate()
        proc.wait(timeout=20)


@pytest.fixture(scope="module")
def pagina(servidor):
    with sync_api.sync_playwright() as p:
        try:
            navegador = p.chromium.launch()
        except sync_api.Error:
            pytest.skip("Chromium no está disponible para Playwright.")
        ctx = navegador.new_context(viewport={"width": 1400, "height": 1000})
        pg = ctx.new_page()
        pg.errores_js = []
        pg.on("pageerror", lambda e: pg.errores_js.append(str(e)))
        yield pg
        navegador.close()


def _abrir(pg, url: str, sim: str):
    pg.goto(f"{url}/?sim={sim}")
    pg.wait_for_selector("[data-testid=stTab]", timeout=90_000)
    pg.wait_for_timeout(2500)


def _sin_excepciones(pg):
    assert pg.locator("[data-testid=stException]").count() == 0, pg.inner_text("[data-testid=stException]")
    assert pg.errores_js == []


@pytest.mark.parametrize("sim", list(SIMULADORES))
def test_predice_y_experimenta_en_navegador(servidor, pagina, sim):
    _abrir(pagina, servidor, sim)
    pagina.get_by_role("tab", name="Predice y experimenta").click()
    pagina.get_by_role("button", name="Ejecutar experimento").first.click()
    pagina.get_by_text("Cociente modificado / referencia").first.wait_for(timeout=45_000)
    _sin_excepciones(pagina)


@pytest.mark.parametrize("sim", list(SIMULADORES))
def test_laboratorio_inverso_y_instrumentos_en_navegador(servidor, pagina, sim):
    _, instrumentos = SIMULADORES[sim]
    _abrir(pagina, servidor, sim)
    pagina.get_by_role("tab", name="Laboratorio inverso").click()
    pagina.get_by_role("button", name="Verificar").first.click()
    pagina.get_by_text("Verificación matemática").first.wait_for(timeout=45_000)
    _sin_excepciones(pagina)
    if instrumentos:
        pagina.get_by_role("tab", name=instrumentos).click()
        pagina.wait_for_timeout(1500)
        _sin_excepciones(pagina)


def test_reto_de_la_esfera_acepta_la_solucion_en_navegador(servidor, pagina):
    """l = 5, m = 3 (2 conos + 3 planos) debe aparecer como «Solución exacta»."""
    _abrir(pagina, servidor, "esfera")
    pagina.get_by_role("tab", name="Laboratorio inverso").click()
    campos = pagina.get_by_role("tabpanel").locator("input[type=number]")
    for i, valor in enumerate(("5", "3")):
        campos.nth(i).fill(valor)
        campos.nth(i).press("Enter")
        pagina.wait_for_timeout(1200)
    pagina.get_by_role("button", name="Verificar").first.click()
    pagina.get_by_text("Solución exacta").first.wait_for(timeout=45_000)
    _sin_excepciones(pagina)


@pytest.mark.parametrize("sim", list(SIMULADORES))
def test_vista_de_celular_sin_desbordamiento_horizontal(servidor, pagina, sim):
    """En 390 px de ancho las pestañas nuevas no deben provocar desplazamiento horizontal de la página."""
    pagina.set_viewport_size({"width": 390, "height": 844})
    try:
        _abrir(pagina, servidor, sim)
        for pestana in ("Predice y experimenta", "Laboratorio inverso"):
            pagina.get_by_role("tab", name=pestana).click()
            pagina.wait_for_timeout(1200)
            assert pagina.evaluate("document.documentElement.scrollWidth") <= 390, pestana
        _sin_excepciones(pagina)
    finally:
        pagina.set_viewport_size({"width": 1400, "height": 1000})
