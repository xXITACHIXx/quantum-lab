# QUANTUM LAB — Laboratorio interactivo de mecánica cuántica

Tres simuladores independientes con una identidad visual común (tema oscuro y tipografía científica), todo en español y
**100 % local** (sin APIs externas, sin claves, sin Internet en ejecución).

| Archivo | Contenido |
|---|---|
| `quantum_lab.py` | Menú principal (portada, introducción, acceso a los tres simuladores, pruebas globales) |
| `particula_caja.py` | Partícula en una caja 1D: ψₙ, Eₙ, ρₙ, De Broglie, nodos, **superposición e interferencia dependientes del tiempo** |
| `oscilador_armonico.py` | Oscilador armónico 1D: Hermite, 6 paneles sincronizados (ψ, ρ, V+E, u_V, u_T, energía total), virial, dinámica |
| `particula_esfera.py` | Armónicos esféricos Yₗᵐ en 3D rotable, nodos, simetrías, complejos vs reales, modelo opcional de partícula confinada |
| `quantum_lab_comun.py` | Código compartido (constantes, unidades, estilo visual, componentes de interfaz, registro de pruebas). No contiene física de los simuladores |
| `test_quantum_lab.py` | Pruebas con `pytest` |
| `requirements.txt` | Dependencias |
| `.streamlit/config.toml` | Tema visual (colores, tipografías Source Serif / Sans / Code incluidas en Streamlit) |

---

## 1. Requisitos

* **Python 3.10 o superior** (probado con 3.13). Descárgalo de <https://www.python.org/downloads/>.
  En el instalador de Windows marca **«Add python.exe to PATH»**.
* Un navegador moderno (Chrome, Edge, Firefox).

## 2. Instalación en Windows (PowerShell o CMD) / VS Code

1. Descomprime la carpeta `quantum_lab` (por ejemplo en `C:\Users\TU_USUARIO\quantum_lab`).
2. **VS Code:** `Archivo → Abrir carpeta…` y elige `quantum_lab`. Abre la terminal integrada con
   `Ctrl + ñ` (o menú `Terminal → Nueva terminal`). Si prefieres no usar VS Code, abre PowerShell y
   ejecuta `cd C:\Users\TU_USUARIO\quantum_lab`.
3. Crea y activa un entorno virtual:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   *Si PowerShell rechaza el script* («la ejecución de scripts está deshabilitada»), ejecuta una vez
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` o usa CMD con `.venv\Scripts\activate.bat`.
   *(En VS Code, cuando te pregunte si quieres usar el nuevo entorno, di que sí; o elige el intérprete con
   `Ctrl+Shift+P → Python: Select Interpreter → .venv`.)*

4. Instala las dependencias:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

**Linux / macOS:** `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## 3. Ejecución

```powershell
streamlit run quantum_lab.py
```

Se abre el navegador en <http://localhost:8501>. Para cerrarlo: `Ctrl + C` en la terminal.

Cada simulador también se puede lanzar por separado:

```powershell
streamlit run particula_caja.py
streamlit run oscilador_armonico.py
streamlit run particula_esfera.py
```

> Si `streamlit` no se reconoce como comando, usa `python -m streamlit run quantum_lab.py`.

## 4. Pruebas

```powershell
python -m pytest -q          # 3 grupos de pruebas (caja, oscilador, esfera)
python quantum_lab.py        # lista todas las comprobaciones y su resultado
python particula_caja.py     # pruebas de un solo simulador (también: oscilador_armonico.py, particula_esfera.py)
```

También hay un botón de pruebas en la pestaña **«Pruebas numéricas»** de cada simulador y en la página
**«Pruebas globales»** del menú.

## 5. Uso rápido

* Los **parámetros** están arriba de cada simulador; los resultados se recalculan al instante.
* «Configuración de ejemplo» carga casos típicos; «Restaurar valores iniciales» vuelve al principio.
* La barra lateral agrupa las páginas en secciones desplegables (Simuladores; Teoría y verificación) y se puede
  ocultar con el botón « de su esquina superior.
* **Las animaciones** (superposición en la caja y dinámica del oscilador) se reproducen en el navegador con
  los botones «Reproducir» / «Pausa» y un deslizador de tiempo: **no bloquean** la interfaz.
* Los gráficos 3D se **rotan con el ratón**, se amplían con la rueda y se restablecen con doble clic.
* Unidades: todo se calcula en SI. Puedes introducir y leer en SI (nm, eV, rad/s) o en unidades atómicas
  (a₀, Eₕ, ħ/Eₕ). Al cambiar de sistema, ω del oscilador se convierte automáticamente.
* Si introduces un valor no válido (masa ≤ 0, m > l, resolución insuficiente…) aparece un mensaje en rojo
  que explica el problema; la aplicación no se cae.

## 6. Qué se calcula y cómo se comprueba

* **Caja:** ψₙ = √(2/a) sin(nπx/a), Eₙ = n²π²ħ²/2ma², λ = 2a/n, n−1 nodos interiores. Superposición
  Ψ = Σ cₙψₙe^{−iEₙt/ħ}; ρ = |Ψ|² **siempre desde la onda total** (el término de interferencia es la diferencia
  con Σ|cₙ|²|ψₙ|²). Pruebas: ψ(0)=ψ(a)=0, normalización, E∝n², E∝1/a², normalización de coeficientes, reaparición.
* **Oscilador:** ψₙ con `scipy.special.eval_hermite` y prefactor logarítmico (sin desbordamiento hasta n = 100).
  Energía total ∫(u_T+u_V)dx contra ħω(n+½); error de la derivada numérica documentado con un estudio de
  convergencia (orden observado ≈ 2); virial ⟨T⟩=⟨V⟩; nodos = raíces de Hₙ; probabilidad en la zona prohibida.
* **Esfera:** Yₗᵐ con `scipy.special.sph_harm_y` (SciPy ≥ 1.15) o la firma antigua `sph_harm` con ángulos
  **invertidos** si la versión es anterior; el programa **calibra** la función al arrancar contra las fórmulas
  cerradas (incluida la fase de Condon–Shortley) y, si falla, usa una implementación propia con `lpmv`. Pruebas:
  l y m permitidos, normalización con Gauss–Legendre, ortonormalidad, simetrías, paridad, nodos, transformación a
  cartesianas, ceros de Bessel, energías del modelo confinado.

## 7. Limitaciones científicas

* Es una herramienta **educativa** con modelos de una sola partícula, sin espín ni interacciones. No describe
  átomos reales (el hidrógeno necesitaría la parte radial de Laguerre, que no se implementa).
* Las integrales y derivadas son **numéricas** (trapecio; diferencias centrales de orden 2). Los errores se
  muestran en pantalla (p. ej. ~10⁻⁵ relativo en la energía del oscilador con la resolución por defecto).
* Oscilador: n ≤ 100; caja: n ≤ 200; esfera: l ≤ 20 (confinada: n ≤ 6, l ≤ 8). Con resolución insuficiente el
  programa **rechaza** el cálculo en lugar de dibujar algo incorrecto.
* La animación del oscilador/caja muestra Re Ψ, Im Ψ y |Ψ|². Un estado estacionario único **no se mueve**
  (|Ψ|² constante): solo gira su fase global; el movimiento aparece al superponer estados.
* En la esfera, «deformación suave» y «lóbulos» son representaciones geométricas, no formas físicas. La parte
  angular no depende del radio R.
* Las figuras Matplotlib son estáticas (cada cambio de parámetro las redibuja); son interactivas los controles,
  las figuras Plotly (3D de la esfera, comparación de orbitales, animaciones) y las tablas.

## 8. Solución de problemas

| Problema | Solución |
|---|---|
| `streamlit` no se reconoce | `python -m streamlit run quantum_lab.py` |
| `ModuleNotFoundError: numpy` | Activa el entorno virtual (`.venv\Scripts\Activate.ps1`) e instala `requirements.txt` |
| El puerto 8501 está ocupado | `streamlit run quantum_lab.py --server.port 8502` |
| Gráficos lentos | Reduce la resolución angular (esfera) o los puntos (caja/oscilador) |
| La página no se actualiza | Pulsa `R` en el navegador o «Rerun» |
| Se ve el diseño antiguo o un aviso sobre `theme` | Actualiza Streamlit: `python -m pip install -U -r requirements.txt` (se necesita 1.50 o superior) y reinicia |
