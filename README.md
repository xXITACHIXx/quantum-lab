# QUANTUM LAB — Laboratorio interactivo de mecánica cuántica

Seis simuladores con una identidad visual común (tema oscuro, tipografía científica sin emojis), todo en español.
Cada simulador incluye resultados numéricos, visualización, interpretación, ecuaciones o **teoría**, **guía de
práctica**, **autoevaluación** y **pruebas numéricas**. El cálculo se hace con NumPy y SciPy, sin APIs externas ni claves.

| Archivo | Contenido |
|---|---|
| `quantum_lab.py` | Menú principal (portada, introducción, acceso a los seis simuladores, pruebas globales) |
| `particula_caja.py` | 01 · Partícula en una caja 1D: ψₙ, Eₙ, De Broglie, nodos, **superposición e interferencia** |
| `oscilador_armonico.py` | 02 · Oscilador armónico: Hermite, densidades de energía, virial, **límite clásico**, dinámica |
| `particula_esfera.py` | 03 · Armónicos esféricos Yₗᵐ en 3D, nodos, simetrías, complejos vs reales, partícula confinada |
| `efecto_fotoelectrico.py` | 04 · Efecto fotoeléctrico: Einstein, umbral, corriente, comparación de metales, **determinación de h**, teoría e historia |
| `modelo_bohr.py` | 05 · Átomo de hidrógeno: modelo de Bohr (transiciones, series, Rydberg, masa reducida) y **átomo cuántico en 3D** (nubes de probabilidad, orbitales, animación del salto), teoría |
| `principio_incertidumbre.py` | 06 · Principio de incertidumbre: paquetes de ondas en x y p, límite ħ/2, evolución libre, difracción por una rendija, teoría |
| `quantum_lab_comun.py` | Código compartido (constantes, unidades, estilo, componentes de interfaz, enlaces, descargas, guías, autoevaluación, pruebas). No contiene física de los simuladores |
| `test_quantum_lab.py` | Pruebas con `pytest` |
| `requirements.txt` | Dependencias |
| `.streamlit/config.toml` | Tema visual (colores y tipografías Source Serif / Sans / Code incluidas en Streamlit) |

Los simuladores 04 y 05 proceden de los cuadernos «Efecto_Fotoelectrico_Simulacion.ipynb» y
«Modelo_Bohr_Simulacion.ipynb», adaptados a la interfaz interactiva y ampliados.

---

## 1. Requisitos

* **Python 3.10 a 3.13** (recomendado **3.12**). Las versiones más nuevas (3.14, 3.15) todavía no tienen
  versiones compiladas de algunas dependencias de Streamlit y la instalación falla («Failed to build pyarrow»).
  Descárgalo de <https://www.python.org/downloads/windows/> y marca **«Add python.exe to PATH»**.
* Un navegador moderno (Chrome, Edge, Firefox).

## 2. Instalación en Windows (PowerShell o CMD) / VS Code

1. Descomprime la carpeta `quantum_lab`.
2. **VS Code:** `Archivo → Abrir carpeta…` y elige `quantum_lab`. Abre la terminal con `Ctrl + ñ`.
3. Crea y activa un entorno virtual con Python 3.12:

   ```powershell
   py -3.12 -m venv .venv312
   .\.venv312\Scripts\Activate.ps1
   python --version          # debe decir Python 3.12.x
   ```

   *Si PowerShell rechaza el script*, ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
4. Instala las dependencias:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install --only-binary=:all: -r requirements.txt
   ```

5. En VS Code: `Ctrl+Shift+P → Python: Select Interpreter → .venv312`.

**Linux / macOS:** `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## 3. Ejecución

```powershell
python -m streamlit run quantum_lab.py
```

Se abre el navegador en <http://localhost:8501>. Para cerrarlo: `Ctrl + C` en la terminal.
Cada simulador también se puede lanzar por separado, p. ej. `python -m streamlit run modelo_bohr.py`.

### Publicación en la web (Streamlit Community Cloud)

Sube **todos** los archivos de la tabla (incluida la carpeta `.streamlit`) a un repositorio de GitHub y despliega
`quantum_lab.py` desde <https://share.streamlit.io> eligiendo **Python 3.12** en «Advanced settings». Para
actualizar la web basta con subir los archivos modificados: la aplicación se redespliega sola.

## 4. Pruebas

```powershell
python -m pytest -q          # 6 grupos de pruebas (uno por simulador)
python quantum_lab.py        # lista todas las comprobaciones y su resultado
python modelo_bohr.py        # pruebas de un solo simulador
```

También hay un botón de pruebas en la pestaña **«Pruebas numéricas»** de cada simulador y en la página
**«Pruebas numéricas»** del menú.

## 5. Uso

* Los **parámetros** están arriba de cada simulador; los resultados se recalculan al instante.
* «Configuración de ejemplo» carga casos típicos; «Restaurar valores iniciales» vuelve al principio.
* **Compartir configuración:** la dirección de la página guarda el simulador y los parámetros que difieren de los
  valores iniciales (p. ej. `?sim=bohr&bohr_ni=4`). El botón «Compartir configuración» muestra el enlace listo para
  copiar; al abrirlo se reproduce exactamente la misma configuración. Los parámetros no válidos se ignoran.
* **Descargas:** debajo de cada gráfica y tabla hay un botón para descargarla: PNG (gráficas estáticas), HTML
  interactivo (gráficas 3D y animaciones) o CSV (tablas; se abre en Excel con tildes y símbolos correctos).
* **Vista para celular:** se activa sola al abrir la página desde un teléfono (también hay un interruptor en la
  barra lateral). Muestra 2 indicadores por fila y apila los paneles de las gráficas en una columna.
* **Guía de práctica:** experimentos con objetivo, procedimiento, una pregunta para predecir, un botón que carga la
  configuración y el resultado esperado oculto. El cuadro de texto sirve para anotar predicciones y medidas.
* **Autoevaluación:** preguntas de opción múltiple con corrección, puntuación y explicación de cada respuesta.
* **Animaciones** (caja, oscilador, átomo de hidrógeno, incertidumbre): botones «Reproducir» / «Pausa» y deslizador;
  se ejecutan en el navegador.
* Los gráficos 3D se **rotan con el ratón**, se amplían con la rueda y se restablecen con doble clic.
* Si introduces un valor no válido aparece un mensaje en rojo que explica el problema; la aplicación no se cae.

## 6. Qué se calcula y cómo se comprueba

* **Caja:** ψₙ = √(2/a) sin(nπx/a), Eₙ = n²π²ħ²/2ma², λ = 2a/n. Superposición Ψ = Σ cₙψₙe^{−iEₙt/ħ} con
  ρ = |Ψ|² **desde la onda total**. 35 pruebas.
* **Oscilador:** ψₙ con polinomios de Hermite; energía ∫(u_T+u_V)dx contra ħω(n+½), virial, nodos, zona prohibida,
  orden de convergencia. **Límite clásico:** P_cl(x) = 1/(π√(A²−x²)) con A = √(2n+1)x₀; se comparan las
  probabilidades acumuladas (distancia D, que disminuye con n) y ⟨x²⟩ (idéntico). 34 pruebas.
* **Esfera:** Yₗᵐ calibrados contra fórmulas cerradas (Condon–Shortley), normalización de Gauss–Legendre,
  simetrías, nodos, ceros de Bessel. 65 pruebas.
* **Efecto fotoeléctrico:** K_max = hν − Φ, umbral ν₀ = Φ/h, v_max, potencial de frenado; corriente ∝ potencia
  (la intensidad no cambia K_max); característica I–V simplificada; ajuste de Millikan de V₀ frente a ν con las
  líneas del mercurio (recupera h y Φ; con ruido, la incertidumbre del ajuste es coherente). 29 pruebas.
* **Bohr:** Eₙ = −Z²·13.6057 eV/n², rₙ = n²a₀/Z, vₙ = Zαc/n; transición, fotón, serie (la fija el nivel más bajo) y
  región espectral; comparación con Rydberg: sin masa reducida difieren en mₑ/M ≈ 5.4×10⁻⁴, con ella coinciden.
  Hα = 656.47 nm, Lyman α = 121.57 nm, límite de Balmer = 364.71 nm (en el vacío). **Átomo cuántico:** R_nl con
  polinomios de Laguerre (normalización, ecuación radial, nodos n − l − 1, ⟨r⟩ exacto, radio más probable = n²a₀ si
  l = n − 1); la nube son medidas simuladas por muestreo exacto de |ψ|² (media de Monte Carlo dentro de 4σ);
  Δx·Δpₓ = ħ/√3 en el 1s. 36 pruebas.
* **Incertidumbre:** Δx y Δp numéricos (FFT, comprobados también con la derivada) frente a las fórmulas cerradas:
  gaussiano ħ/2, chirp ½√(1+β²)ħ, triangular √0.3 ħ, sech πħ/6, dos gaussianas con solapamiento; Parseval;
  evolución libre exacta (σ(τ) = √2σ₀, enfoque del chirp negativo, Δp y norma constantes, velocidad de grupo);
  rendija: sinc² contra suma de ondas de Huygens y primer mínimo en sen θ = λ/a. 32 pruebas.

## 7. Limitaciones científicas

* Herramienta **educativa** con modelos de una partícula, sin espín ni interacciones. El modelo de Bohr reproduce
  el espectro del hidrógeno pero no es la descripción moderna (no hay órbitas definidas) y no sirve para átomos de
  varios electrones; tampoco incluye la estructura fina.
* Las integrales y derivadas son **numéricas**; los errores se muestran en pantalla.
* Las funciones de trabajo del efecto fotoeléctrico son valores aproximados (dependen de la superficie). La curva
  corriente–voltaje usa un modelo simplificado.
* Las longitudes de onda del modelo de Bohr son **en el vacío** (en aire Hα mide 656.28 nm).
* La nube de probabilidad 3D muestra posiciones simuladas; los colores indican el signo (orbitales reales) o la fase
  (complejos) de ψ. La animación de las órbitas de Bohr tiene los radios a escala, pero no las velocidades.
* En la difracción por una rendija, Δp_y ≈ h/a es una estimación con el ancho del máximo central (la desviación
  típica de una rendija de bordes netos no es finita).
* Los colores de las líneas espectrales son una aproximación visual, no una conversión colorimétrica exacta.
* En la esfera, «deformación suave» y «lóbulos» son representaciones geométricas, no formas físicas.

## 8. Solución de problemas

| Problema | Solución |
|---|---|
| `Failed to build 'pyarrow'` al instalar | Tu Python es demasiado nuevo: instala Python 3.12 y crea el entorno con `py -3.12 -m venv .venv312` |
| «No se encontró Python» | Python no está instalado o no está en PATH: reinstálalo marcando «Add python.exe to PATH» y reinicia VS Code |
| `streamlit` no se reconoce | `python -m streamlit run quantum_lab.py` |
| `ModuleNotFoundError: numpy` | Activa el entorno virtual e instala `requirements.txt` |
| El puerto 8501 está ocupado | `python -m streamlit run quantum_lab.py --server.port 8502` |
| Gráficos lentos | Reduce la resolución angular (esfera), los puntos (caja/oscilador) o el número de medidas (nube 3D) |
| Se ve el diseño antiguo o un aviso sobre `theme` | `python -m pip install -U -r requirements.txt` (Streamlit 1.50 o superior) y reinicia |
| Símbolos como ₙ o ⟨⟩ salen como recuadros | La app incrusta una fuente de símbolos; si persiste, recarga la página sin caché (`Ctrl + F5`) |
