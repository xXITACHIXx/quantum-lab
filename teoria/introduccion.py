"""
teoria/introduccion.py — Teoría: Introducción a la mecánica cuántica.

Contenido movido desde la antigua página «Introducción teórica».
"""

import streamlit as st

import quantum_lab_comun as qc


def mostrar() -> None:
    with st.expander("1. Función de onda y probabilidad", expanded=True):
        st.markdown("El estado de una partícula se describe con la **función de onda** ψ(x), en general compleja. "
                    "Lo medible es la **densidad de probabilidad** ρ = |ψ|²; la probabilidad de encontrarla en [x₁, x₂] "
                    "es ∫ρ dx y la total vale 1 (**normalización**).")
        st.latex(r"\int_{-\infty}^{\infty}|\psi(x)|^2\,dx = 1")
    with st.expander("2. Ecuación de Schrödinger y estados estacionarios", expanded=True):
        st.latex(r"i\hbar\,\partial_t\Psi=\hat H\Psi,\qquad \hat H\psi_n=E_n\psi_n\ \Rightarrow\ \Psi_n(x,t)=\psi_n(x)\,e^{-iE_nt/\hbar}")
        st.markdown("En un estado estacionario la fase gira pero **|Ψ|² no cambia**. La energía está **cuantizada** por las "
                    "condiciones de contorno (caja: ψ = 0 en las paredes; oscilador: ψ → 0 en el infinito).")
    with st.expander("3. Superposición e interferencia", expanded=False):
        st.latex(r"\Psi=\sum_n c_n\psi_n e^{-iE_nt/\hbar},\qquad |\Psi|^2=\sum_n|c_n|^2|\psi_n|^2+\text{(términos cruzados)}")
        st.markdown("Los términos cruzados dependen de las **fases relativas** y oscilan a las frecuencias (Eₙ − Eₘ)/ħ: "
                    "son la interferencia cuántica.")
    with st.expander("4. Momento angular y armónicos esféricos", expanded=False):
        st.markdown("En un potencial central la parte angular de ψ son los armónicos esféricos Yₗᵐ(θ, φ): autoestados de L² "
                    "(ħ²l(l+1)) y L_z (ħm), con l = 0, 1, 2… y −l ≤ m ≤ l.")
    with st.expander("5. Unidades", expanded=False):
        st.markdown("Internamente todo se calcula en **SI**. Puedes introducir y ver los resultados en SI (nm, eV, rad/s) o en "
                    "**unidades atómicas** (a₀, Eₕ, ħ/Eₕ), donde ħ = mₑ = e = 1.")
