"""
teoria/oscilador.py — Teoría: Oscilador armónico cuántico.

Contenido movido desde la pestaña «Ecuaciones» del simulador (oscilador_armonico.py). Se muestra en el Centro de teoría.
"""

import streamlit as st

import quantum_lab_comun as qc


def mostrar() -> None:
    qc.seccion("Modelo")
    st.latex(r"V(x)=\tfrac12 m\omega^2x^2\qquad x_0=\sqrt{\frac{\hbar}{m\omega}}\qquad E_n=\hbar\omega\left(n+\tfrac12\right)")
    st.latex(r"\left[-\frac{\hbar^2}{2m}\frac{d^2}{dx^2}+\tfrac12 m\omega^2x^2\right]\psi_n=E_n\psi_n")
    st.latex(r"\psi_n(x)=\frac{1}{\sqrt{2^n n!}}\frac{1}{\pi^{1/4}\sqrt{x_0}}H_n\!\left(\frac{x}{x_0}\right)e^{-x^2/2x_0^2}")
    qc.seccion("Densidades de energía")
    st.latex(r"u_V(x)=V(x)\,|\psi_n(x)|^2\qquad u_T(x)=\frac{\hbar^2}{2m}\left|\frac{d\psi_n}{dx}\right|^2\qquad E_n=\int(u_T+u_V)\,dx")
    st.latex(r"\langle T\rangle=\langle V\rangle=\frac{E_n}{2}\qquad \langle x\rangle=0\qquad \langle x^2\rangle=\left(n+\tfrac12\right)x_0^2")
    st.latex(r"\psi_n'(x)=\frac{1}{x_0}\left[\sqrt{\tfrac n2}\,\psi_{n-1}-\sqrt{\tfrac{n+1}{2}}\,\psi_{n+1}\right]")
    qc.seccion("Dinámica")
    st.latex(r"x_n^{\rm retorno}=\pm\sqrt{2n+1}\,x_0\qquad \Psi(x,t)=\sum_n c_n\psi_n(x)e^{-i(n+1/2)\omega t}")
    qc.seccion("Límite clásico")
    st.latex(r"A=\sqrt{2n+1}\,x_0,\qquad P_{\rm cl}(x)=\frac{1}{\pi\sqrt{A^2-x^2}},\qquad F_{\rm cl}(x)=\frac12+\frac{1}{\pi}\arcsin\frac{x}{A}")
    st.latex(r"D=\max_x\left|F_{\rm cuántica}(x)-F_{\rm cl}(x)\right|\ \xrightarrow[n\to\infty]{}\ 0,\qquad \langle x^2\rangle_{\rm cl}=\frac{A^2}{2}=\left(n+\tfrac12\right)x_0^2")
    st.markdown("**V(x)** (energía por unidad de probabilidad, en energía) no debe confundirse con **u_V(x)** "
                "(densidad de energía potencial, en energía/longitud).")
