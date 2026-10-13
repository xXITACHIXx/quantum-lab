"""
teoria/caja.py — Teoría: Partícula en una caja unidimensional.

Contenido movido desde la pestaña «Ecuaciones» del simulador (particula_caja.py). Se muestra en el Centro de teoría.
"""

import streamlit as st

import quantum_lab_comun as qc


def mostrar() -> None:
    qc.seccion("Modelo")
    st.latex(r"V(x)=0\ (0<x<a),\qquad V(x)=\infty\ \text{fuera}")
    st.latex(r"\psi_n(x)=\sqrt{\frac{2}{a}}\,\sin\!\left(\frac{n\pi x}{a}\right),\qquad n=1,2,3,\dots")
    st.latex(r"E_n=\frac{n^2\pi^2\hbar^2}{2ma^2}\qquad \rho_n(x)=|\psi_n(x)|^2")
    st.latex(r"\lambda_n=\frac{h}{|p_n|}=\frac{2a}{n},\qquad |p_n|=\frac{n\pi\hbar}{a}")
    qc.seccion("Superposición")
    st.latex(r"\Psi(x,t)=\sum_n c_n\,\psi_n(x)\,e^{-iE_nt/\hbar},\qquad \rho(x,t)=|\Psi(x,t)|^2")
    st.latex(r"|\Psi|^2=\sum_n|c_n|^2|\psi_n|^2+2\sum_{n<m}\mathrm{Re}\!\left[c_n^*c_m\,\psi_n\psi_m\,e^{-i(E_m-E_n)t/\hbar}\right]")
    st.latex(r"\tau=\frac{E_1t}{\hbar}\ \Rightarrow\ e^{-iE_nt/\hbar}=e^{-in^2\tau},\qquad \text{reaparición en }\tau=2\pi")
    st.markdown("Los dos últimos bloques muestran por qué **no** se pueden sumar las densidades: el segundo "
                "sumando (interferencia) solo aparece al elevar al cuadrado la función de onda total.")
