#@title Oscilador armónico 1D: animación de la superposición de estados vibracionales { display-mode: "form" }
# =====================================================================================
#  Ψ(x,t) = Σₙ cₙ ψₙ(x) e^{−iEₙt/ħ},     Eₙ = ħω(n + ½),     V(x) = ½ m ω² x²
#
#  Se trabaja con ξ = x/x₀ (x₀ = √(ħ/mω)) y τ = ωt:   Ψ(ξ,τ) = Σ cₙ φₙ(ξ) e^{−i(n+½)τ}
#  y al final se dibuja en unidades reales (nm, fs) con la masa y la frecuencia indicadas.
#  Esta celda es independiente: solo necesita NumPy y Matplotlib (ya instalados en Colab).
# =====================================================================================
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import Normalize
from IPython.display import HTML, display

# ------------------------------- 1) DATOS DEL USUARIO --------------------------------
estados    = [0, 1, 2]       # cuántos y cuáles estados se superponen (números cuánticos n = 0, 1, 2, …)
amplitudes = [1.0, 1.0, 1.0]  # amplitud Aₙ de cada estado (cₙ = Aₙ·e^{iφₙ}); puede ser cualquier valor ≥ 0
fases      = [0.0, 0.0, 0.0]  # fase φₙ de cada estado, en radianes
normalizar = True             # True: divide entre √Σ|cₙ|² para que la probabilidad total sea 1

masa_me = 1.0                 # masa en unidades de la masa del electrón (protón ≈ 1836.15)
omega   = 1.0e15              # frecuencia angular ω [rad/s]
periodos   = 1                # τ = ωt recorre de 0 a 2π·periodos
n_cuadros  = 120              # cuadros de la animación
guardar_gif = False           # True: además guarda 'oscilador_superposicion.gif'

# --------------------------------- 2) FÍSICA -----------------------------------------
HBAR, M_E = 1.054571817e-34, 9.1093837015e-31     # J·s, kg
x0 = math.sqrt(HBAR / (masa_me * M_E * omega))    # longitud característica [m]


def fi(n_max, xi):
    """φ₀ … φ_{n_max}(ξ), ortonormales respecto de ξ (recurrencia estable, sin polinomios de Hermite explícitos)."""
    phi = np.zeros((n_max + 1, xi.size))
    phi[0] = np.pi ** -0.25 * np.exp(-xi ** 2 / 2)
    if n_max >= 1:
        phi[1] = math.sqrt(2.0) * xi * phi[0]
    for k in range(1, n_max):
        phi[k + 1] = math.sqrt(2.0 / (k + 1)) * xi * phi[k] - math.sqrt(k / (k + 1)) * phi[k - 1]
    return phi


def validar(estados, amplitudes, fases):
    if not (len(estados) == len(amplitudes) == len(fases) and len(estados) >= 1):
        raise ValueError("«estados», «amplitudes» y «fases» deben tener la misma longitud (al menos 1).")
    if any(int(n) != n or n < 0 for n in estados):
        raise ValueError("Los números cuánticos n deben ser enteros ≥ 0.")
    if len(set(estados)) != len(estados):
        raise ValueError("Hay un estado repetido: cada n debe aparecer una sola vez (suma sus coeficientes).")
    if any(a < 0 for a in amplitudes):
        raise ValueError("Las amplitudes deben ser ≥ 0 (usa la fase π para un signo negativo).")
    if not np.any(np.asarray(amplitudes) > 0):
        raise ValueError("Al menos una amplitud debe ser distinta de cero.")
    if masa_me <= 0 or omega <= 0:
        raise ValueError("La masa y ω deben ser positivas.")


validar(estados, amplitudes, fases)
n_arr = np.array(estados, dtype=int)
c = np.array(amplitudes, dtype=float) * np.exp(1j * np.array(fases, dtype=float))
if normalizar:
    c = c / np.sqrt(np.sum(np.abs(c) ** 2))
n_max = int(n_arr.max())

# Malla en ξ: hasta el punto de retorno del estado más alto (√(2n+1)) más una cola de 5 unidades
xi_max = math.sqrt(2 * n_max + 1) + 5.0
xi = np.linspace(-xi_max, xi_max, 1201)
dxi = xi[1] - xi[0]
phi = fi(n_max, xi)[n_arr]                                   # (nº de estados, nº de puntos)
tau = np.linspace(0.0, 2 * np.pi * periodos, n_cuadros, endpoint=False)
fase_t = np.exp(-1j * np.outer(tau, n_arr + 0.5))             # (cuadros, estados)
psi = (fase_t * c) @ phi                                       # Ψ(ξ, τ) = Σ cₙ φₙ(ξ) e^{−i(n+½)τ}   [en unidades de x₀^{-1/2}]
rho = np.abs(psi) ** 2
xi_medio = (rho * xi).sum(axis=1) * dxi / (rho.sum(axis=1) * dxi)

# Comprobaciones numéricas
norma = rho.sum(axis=1) * dxi
E_medio = float(np.sum(np.abs(c) ** 2 * (n_arr + 0.5)))      # ⟨E⟩/ħω
dE = float(np.sqrt(np.sum(np.abs(c) ** 2 * (n_arr + 0.5) ** 2) - E_medio ** 2))
print(f"Σ|cₙ|² = {np.sum(np.abs(c) ** 2):.6f}     ∫|Ψ|²dx (mín, máx sobre τ) = {norma.min():.6f}, {norma.max():.6f}")
print(f"⟨E⟩ = {E_medio:.4f} ħω = {E_medio * HBAR * omega / 1.602176634e-19:.4f} eV      ΔE = {dE:.4f} ħω")
dif = np.diff(np.sort(n_arr))
if len(n_arr) > 1:
    print(f"Periodo de la densidad: T = 2π/ω = {2 * np.pi / omega * 1e15:.4g} fs "
          "(todas las diferencias de energía son múltiplos enteros de ħω).")
else:
    print("Un solo estado: la densidad |Ψ|² no cambia con el tiempo (estado estacionario).")

# Unidades de dibujo: x en nm, t en fs, |Ψ|² en nm⁻¹
X = xi * x0 * 1e9
T = tau / omega * 1e15
RHO = rho / (x0 * 1e9)
RE, IM = psi.real / math.sqrt(x0 * 1e9), psi.imag / math.sqrt(x0 * 1e9)
XM = xi_medio * x0 * 1e9
A_ret = math.sqrt(2 * n_max + 1) * x0 * 1e9                  # punto de retorno clásico del estado más alto

plt.rcParams.update({"font.size": 11, "axes.titleweight": "bold"})

# ------------------- 3) SUPERFICIE 3D: |Ψ(x,t)|² (como la figura del proyecto) --------
fig3d = plt.figure(figsize=(10.5, 6.6))
ax3 = fig3d.add_subplot(111, projection="3d")
XX, TT = np.meshgrid(X, T)
sup = ax3.plot_surface(XX, TT, RHO, cmap="plasma", linewidth=0, antialiased=True, rstride=2, cstride=4)
ax3.set_xlabel("Posición x [nm]")
ax3.set_ylabel("Tiempo t [fs]")
ax3.set_zlabel("Densidad de probabilidad |Ψ(x,t)|² [nm⁻¹]", labelpad=8)
ax3.set_title("Superposición de estados n = " + ", ".join(map(str, estados)))
fig3d.colorbar(sup, ax=ax3, shrink=0.6, pad=0.12, label="Probabilidad")
ax3.view_init(elev=35, azim=-125)
plt.show()

# ------------------------------- 4) ANIMACIÓN ----------------------------------------
fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(9.5, 9), gridspec_kw={"height_ratios": [1.5, 1.2, 0.9]})
lim = float(X.max())
ymax = float(RHO.max()) * 1.12
a1.set_xlim(-lim, lim); a1.set_ylim(0, ymax)
a1.axvline(-A_ret, color="gray", ls=":", lw=1); a1.axvline(A_ret, color="gray", ls=":", lw=1, label="puntos de retorno (n máx)")
rho_linea, = a1.plot([], [], color="#1f77b4", lw=2.2, label=r"$|\Psi(x,t)|^2$")
relleno = [a1.fill_between(X, 0, 0)]
marca, = a1.plot([], [], "o", color="crimson", ms=8, label=r"$\langle x\rangle$")
a1.set_xlabel("x [nm]"); a1.set_ylabel(r"$|\Psi|^2$ [nm$^{-1}$]")
a1.set_title("Densidad de probabilidad"); a1.legend(loc="upper right", fontsize=9); a1.grid(alpha=0.3)

cmax = float(max(np.abs(RE).max(), np.abs(IM).max())) * 1.1
a2.set_xlim(-lim, lim); a2.set_ylim(-cmax, cmax)
re_linea, = a2.plot([], [], color="#2ca02c", lw=1.8, label=r"Re $\Psi$")
im_linea, = a2.plot([], [], color="#ff7f0e", lw=1.8, label=r"Im $\Psi$")
a2.axhline(0, color="gray", lw=0.8)
a2.set_xlabel("x [nm]"); a2.set_ylabel(r"$\Psi$ [nm$^{-1/2}$]")
a2.set_title("Función de onda compleja"); a2.legend(loc="upper right", fontsize=9); a2.grid(alpha=0.3)

a3.set_xlim(T.min(), T.max() if len(T) > 1 else T.min() + 1); a3.set_ylim(-1.1 * max(abs(XM).max(), 1e-12), 1.1 * max(abs(XM).max(), 1e-12))
a3.plot(T, XM, color="crimson", lw=1.2, alpha=0.35)
cursor, = a3.plot([], [], "o", color="crimson", ms=7)
a3.axhline(0, color="gray", lw=0.8)
a3.set_xlabel("t [fs]"); a3.set_ylabel(r"$\langle x\rangle$ [nm]")
a3.set_title("Posición media"); a3.grid(alpha=0.3)
titulo = fig.suptitle("", fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.96))


def cuadro(i):
    rho_linea.set_data(X, RHO[i])
    relleno[0].remove()
    relleno[0] = a1.fill_between(X, RHO[i], color="#1f77b4", alpha=0.18)
    marca.set_data([XM[i]], [0])
    re_linea.set_data(X, RE[i]); im_linea.set_data(X, IM[i])
    cursor.set_data([T[i]], [XM[i]])
    titulo.set_text(f"t = {T[i]:.3f} fs     (τ = ωt = {tau[i]:.2f} rad)")
    return rho_linea, marca, re_linea, im_linea, cursor, titulo


anim = animation.FuncAnimation(fig, cuadro, frames=len(T), interval=60, blit=False)
plt.close(fig)
plt.rcParams["animation.embed_limit"] = 80          # MB que puede pesar la animación incrustada
display(HTML(anim.to_jshtml()))
if guardar_gif:
    anim.save("oscilador_superposicion.gif", writer="pillow", fps=20)
    print("GIF guardado: oscilador_superposicion.gif (panel de archivos de Colab, a la izquierda).")
