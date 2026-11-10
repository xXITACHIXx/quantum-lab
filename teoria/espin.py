"""
teoria/espin.py — Teoría: Espín, estados de dos electrones y determinantes de Slater
"""

import streamlit as st
import sympy as sp

import espin_electrones as ee
import quantum_lab_comun as qc


def mostrar() -> None:
    sub = st.tabs(["El espín del electrón", "Dos electrones: S y S_z", "Singlete y triplete", "Antisimetría y Slater", "Calculadora", "Resumen"])
    with sub[0]:
        qc.seccion("Un momento angular intrínseco")
        st.markdown("Además de su momento angular orbital, el electrón tiene un **momento angular de espín** s = ½ que no depende de ninguna "
                    "coordenada espacial. Tiene dos estados, que se llaman **α** (m_s = +½) y **β** (m_s = −½), ortonormales.")
        st.latex(r"\hat s^2\,\alpha=\tfrac34\hbar^2\,\alpha,\qquad \hat s_z\,\alpha=+\tfrac12\hbar\,\alpha,\qquad \hat s^2\,\beta=\tfrac34\hbar^2\,\beta,\qquad \hat s_z\,\beta=-\tfrac12\hbar\,\beta")
        st.markdown("El estado de un electrón en un átomo queda definido por un **espín-orbital**: un orbital φ_nlm (parte espacial) por una función de "
                    "espín, φ_nlm α o φ_nlm β. Los cuatro números cuánticos son n, l, mₗ y m_s.")
        st.markdown("El operador de espín **no actúa sobre la parte espacial**.")
    with sub[1]:
        qc.seccion("Espín total de dos electrones")
        st.latex(r"\hat{\mathbf S}=\hat{\mathbf s}_1+\hat{\mathbf s}_2,\qquad \hat S_z=\hat s_{1z}+\hat s_{2z}")
        st.latex(r"\hat S^2=\hat s_1^2+\hat s_2^2+2\,\hat{\mathbf s}_1\!\cdot\hat{\mathbf s}_2=\tfrac32\hbar^2+2\hat s_{1z}\hat s_{2z}+\hat s_{1+}\hat s_{2-}+\hat s_{1-}\hat s_{2+}")
        st.markdown("Los autovalores son S² = s(s+1)ħ² y S_z = M_Sħ, con s = 0 o 1 y M_S = −s, …, s. **Acción sobre los productos de espín**:")
        qc.tabla_libre([
            {"Producto": "αα", "S_z": "+ħ", "S²·(función)": "2ħ² αα"},
            {"Producto": "ββ", "S_z": "−ħ", "S²·(función)": "2ħ² ββ"},
            {"Producto": "αβ", "S_z": "0", "S²·(función)": "ħ² (αβ + βα)"},
            {"Producto": "βα", "S_z": "0", "S²·(función)": "ħ² (βα + αβ)"},
        ])
        st.caption("αα y ββ son autofunciones; αβ y βα solo lo son sus combinaciones: el término ŝ₁₊ŝ₂₋ + ŝ₁₋ŝ₂₊ intercambia los espines.")
    with sub[2]:
        qc.seccion("Cuatro estados de espín: un singlete y un triplete")
        qc.tabla_libre([
            {"Estado": "triplete", "Función": "αα", "s": "1", "M_S": "+1", "S²": "2ħ²"},
            {"Estado": "triplete", "Función": "(αβ + βα)/√2", "s": "1", "M_S": "0", "S²": "2ħ²"},
            {"Estado": "triplete", "Función": "ββ", "s": "1", "M_S": "−1", "S²": "2ħ²"},
            {"Estado": "singlete", "Función": "(αβ − βα)/√2", "s": "0", "M_S": "0", "S²": "0"},
        ])
        st.markdown("Si Ψ no es autofunción de Ŝ², se descompone Ψ = Ψ_singlete + Ψ_triplete con los proyectores")
        st.latex(r"\hat P_{\text{triplete}}=\tfrac12\hat S^2/\hbar^2,\qquad \hat P_{\text{singlete}}=1-\tfrac12\hat S^2/\hbar^2")
        st.markdown("y medir S² da 0 o 2ħ² con probabilidades ‖P_singlete Ψ‖² y ‖P_triplete Ψ‖² (para Ψ normalizada). Por ejemplo, el producto "
                    "|1sα;2sβ⟩ es 50 % singlete y 50 % triplete M = 0.")
    with sub[3]:
        qc.seccion("Principio de Pauli y determinantes de Slater")
        st.markdown("Los electrones son indistinguibles y la función de onda total debe ser **antisimétrica** frente al intercambio de dos electrones "
                    "(postulado de antisimetría): Ψ(1,2) = −Ψ(2,1). Se logra con un **determinante de Slater**:")
        st.latex(r"\Psi(1,2)=\frac{1}{\sqrt2}\begin{vmatrix}\phi_a(1)&\phi_b(1)\\ \phi_a(2)&\phi_b(2)\end{vmatrix}=\frac{1}{\sqrt2}\left[\phi_a(1)\phi_b(2)-\phi_b(1)\phi_a(2)\right]")
        st.markdown("Con dos espín-orbitales iguales las dos filas coinciden y el determinante vale cero: **dos electrones no pueden tener los cuatro "
                    "números cuánticos iguales**. Ejemplos:")
        st.markdown("- **Helio, 1s²:** Slater(1sα, 1sβ) = 1s(1)1s(2)·(αβ − βα)/√2: antisimétrico, **singlete** (S = 0).\n"
                    "- **1s¹2s¹:** hay cuatro configuraciones de espín: un singlete (parte espacial simétrica) y un triplete (parte espacial antisimétrica). "
                    "Slater(1sα, 2sβ) por sí solo mezcla singlete y triplete M = 0 a partes iguales.")
    with sub[4]:
        qc.seccion("Calculadora")
        st.markdown("Resultado del simulador para una función de dos electrones (se calcula igual que en la página del simulador):")
        texto = st.text_input("Ψ", "Slater(1sα, 2sβ)", key="th_esp_psi")
        try:
            r = ee.analizar(texto)
            qc.metricas([("Ŝ_z", f"{ee.texto_num(r['sz'])} ħ" if r["sz"] is not None else "no autofunción"),
                         ("Ŝ²", f"{ee.texto_num(r['s2'])} ħ²" if r["s2"] is not None else "no autofunción"),
                         ("Intercambio", r["simetria"])], columnas=3)
            if r["p_s2"] is not None and r["s2"] is None:
                st.caption(f"P(singlete) = {ee.texto_num(r['p_s2'][0])}, P(triplete) = {ee.texto_num(r['p_s2'][1])}")
        except (ValueError, SyntaxError, TypeError) as error:
            qc.error(error)
        st.button("Abrir el simulador", key="th_esp_sim", icon=":material/arrow_forward:",
                  on_click=lambda: st.session_state.update(ql_pagina="espin", esp_psi=texto))
    with sub[5]:
        qc.seccion("Resumen de ecuaciones")
        qc.tabla_libre([
            {"Concepto": "Un electrón", "Ecuación": "s = ½;  ŝ²α = ¾ħ²α;  ŝ_zα = +½ħα;  ŝ_zβ = −½ħβ"},
            {"Concepto": "Dos electrones", "Ecuación": "Ŝ = ŝ₁ + ŝ₂;  Ŝ_z = ŝ₁z + ŝ₂z"},
            {"Concepto": "Autovalores", "Ecuación": "Ŝ² = s(s+1)ħ², s = 0, 1;  Ŝ_z = M_Sħ"},
            {"Concepto": "Singlete / triplete", "Ecuación": "(αβ−βα)/√2 con s = 0;  αα, (αβ+βα)/√2, ββ con s = 1"},
            {"Concepto": "Proyectores", "Ecuación": "P_triplete = Ŝ²/2ħ²;  P_singlete = 1 − Ŝ²/2ħ²"},
            {"Concepto": "Pauli", "Ecuación": "Ψ(1,2) = −Ψ(2,1);  determinante de Slater"},
        ])


PREGUNTAS = [
    {"enunciado": "El espín del electrón s vale…",
     "opciones": ["0", "½", "1", "3/2"], "correcta": 1, "explicacion": "s = ½: dos estados, α (m_s = +½) y β (m_s = −½)."},
    {"enunciado": "Los valores posibles de S² para dos electrones son…",
     "opciones": ["0 y ħ²", "0 y 2ħ²", "¾ħ² y 2ħ²", "solo 2ħ²"], "correcta": 1, "explicacion": "s = 0 (singlete) o 1 (triplete): s(s+1)ħ² = 0 o 2ħ²."},
    {"enunciado": "El triplete tiene…",
     "opciones": ["1 estado", "2 estados", "3 estados", "4 estados"], "correcta": 2, "explicacion": "2s + 1 = 3 estados: M_S = +1, 0, −1."},
    {"enunciado": "αβ es…",
     "opciones": ["autofunción de Ŝ_z y de Ŝ²", "autofunción de Ŝ_z pero no de Ŝ²", "autofunción de Ŝ² pero no de Ŝ_z", "de ninguno"], "correcta": 1,
     "explicacion": "M_S = 0, pero Ŝ²(αβ) = ħ²(αβ + βα) no es proporcional a αβ: es mitad singlete y mitad triplete."},
    {"enunciado": "El principio de Pauli exige que Ψ de dos electrones sea…",
     "opciones": ["simétrica", "antisimétrica", "real", "autofunción de Ŝ²"], "correcta": 1, "explicacion": "Ψ(1,2) = −Ψ(2,1): postulado de antisimetría."},
    {"enunciado": "Un determinante de Slater con dos espín-orbitales iguales…",
     "opciones": ["vale 1", "se anula", "es el triplete", "es simétrico"], "correcta": 1, "explicacion": "Dos filas iguales: el determinante es cero (principio de exclusión)."},
    {"enunciado": "El estado fundamental del helio (1s²) es…",
     "opciones": ["un triplete", "un singlete", "mezcla singlete-triplete", "sin espín definido"], "correcta": 1,
     "explicacion": "1s(1)1s(2)(αβ − βα)/√2: antisimétrico y con S = 0."},
]
