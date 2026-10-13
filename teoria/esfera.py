"""
teoria/esfera.py — Teoría: Momento angular y partícula en una esfera.

Contenido movido desde la pestaña «Ecuaciones» del simulador (particula_esfera.py). Se muestra en el Centro de teoría.
"""

import streamlit as st

import quantum_lab_comun as qc


def mostrar() -> None:
    qc.seccion("Armónicos esféricos")
    st.latex(r"Y_l^m(\theta,\varphi)=(-1)^m\sqrt{\frac{2l+1}{4\pi}\frac{(l-m)!}{(l+m)!}}\;P_l^m(\cos\theta)\,e^{im\varphi},\quad m\ge 0")
    st.latex(r"Y_l^{-m}=(-1)^m\,\overline{Y_l^m}\qquad \hat L^2Y_l^m=\hbar^2l(l+1)Y_l^m\qquad \hat L_zY_l^m=\hbar mY_l^m")
    st.latex(r"\int_0^{2\pi}\!\!\int_0^{\pi}\overline{Y_l^m}\,Y_{l'}^{m'}\sin\theta\,d\theta\,d\varphi=\delta_{ll'}\delta_{mm'}")
    st.latex(r"x=r\sin\theta\cos\varphi,\quad y=r\sin\theta\sin\varphi,\quad z=r\cos\theta")
    qc.seccion("Combinaciones reales")
    st.latex(r"R^{c}_{lm}=\sqrt2\,(-1)^m\,\mathrm{Re}\,Y_l^{m}\propto\cos m\varphi,\qquad R^{s}_{lm}=\sqrt2\,(-1)^m\,\mathrm{Im}\,Y_l^{m}\propto\sin m\varphi")
    st.markdown("Nodos latitudinales: raíces de $P_l^{|m|}(\\cos\\theta)$, hay $l-|m|$. Combinación real: además $|m|$ planos "
                "verticales; en total $l$ superficies nodales.")
    qc.seccion("Partícula en una esfera impenetrable")
    st.latex(r"\psi_{nlm}=R_{nl}(r)\,Y_l^m,\qquad R_{nl}(r)=\sqrt{\frac{2}{R^3}}\,\frac{j_l(\alpha_{nl}r/R)}{|j_{l+1}(\alpha_{nl})|}")
    st.latex(r"j_l(\alpha_{nl})=0,\qquad E_{nl}=\frac{\hbar^2\alpha_{nl}^2}{2mR^2},\qquad \int_0^R R_{nl}^2r^2dr=1")
    qc.seccion("Limitaciones del modelo")
    st.markdown("- La parte angular es la misma para cualquier potencial central; **el átomo de hidrógeno** requeriría otra "
                "parte radial (Laguerre), que no se implementa aquí.\n"
                "- El espín no se considera.\n"
                "- Las superficies deformadas o de lóbulos son representaciones geométricas, no objetos físicos.")
