"""
Dashboard de la empresa Indurec - Taller Metalmecánico INDUREC
Ejecutar localmente:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

DATA_FILE = "Base_Dashboard_INDUREC_GAA.xlsx"
ORDEN_ESCENARIO = ["As-Is", "Estándar", "To-Be"]

st.set_page_config(
    page_title="Dashboard INDUREC",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Estilos
# --------------------------------------------------------------------------
st.markdown("""
<style>
    .stMetric {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px 10px;
    }
    div[data-testid="stMetricLabel"] { color: #94a3b8; }
    h1, h2, h3 { color: #f1f5f9; }
</style>
""", unsafe_allow_html=True)

COLOR_ESCENARIO = {"As-Is": "#e23213", "Estándar": "#94a3b8", "To-Be": "#8bf06d"}


@st.cache_data
def load_data():
    ind = pd.read_excel(DATA_FILE, sheet_name="Base_Indicadores")
    fin = pd.read_excel(DATA_FILE, sheet_name="Base_Financiera")
    return ind, fin


ind, fin = load_data()

# --------------------------------------------------------------------------
# Sidebar - filtros
# --------------------------------------------------------------------------
st.sidebar.markdown("## ⚙️ INDUREC")
st.sidebar.caption("Taller Metalmecánico INDUREC S.A.C · Dashboard propuesto por el grupo 4")
st.sidebar.divider()

objetivos_all = sorted(ind["Objetivo"].unique())
herramientas_all = sorted(ind["Herramienta"].unique())

objetivos_sel = st.sidebar.multiselect("Objetivo", objetivos_all, default=objetivos_all)
herramientas_sel = st.sidebar.multiselect("Herramienta Lean", herramientas_all, default=herramientas_all)

ind_f = ind[ind["Objetivo"].isin(objetivos_sel) & ind["Herramienta"].isin(herramientas_sel)]
fin_f = fin[fin["Objetivo"].isin(objetivos_sel) & fin["Herramienta"].isin(herramientas_sel)]

st.sidebar.divider()
st.sidebar.caption("Datos cargados desde Base_Dashboard_INDUREC_GAA.xlsx")

# --------------------------------------------------------------------------
# Encabezado
# --------------------------------------------------------------------------
st.title("Dashboard Resumen")

st.markdown(
    "Comparativo **As-Is / Estándar / To-Be** de los indicadores operativos y "
    "análisis financiero de las herramientas Lean implementadas en el taller."
)

if fin_f.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# --------------------------------------------------------------------------
# KPIs financieros
# --------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Inversión total", f"S/. {fin_f['Inversión (S/.)'].sum():,.2f}")
c2.metric("📈 Ahorro anual total", f"S/. {fin_f['Ahorro anual (S/.)'].sum():,.2f}")
c3.metric("🗓️ Ahorro mensual total", f"S/. {fin_f['Ahorro mensual (S/.)'].sum():,.2f}")
c4.metric("⏱️ Recuperación promedio", f"{fin_f['Recuperación (meses)'].mean():.1f} meses")

st.divider()

# --------------------------------------------------------------------------
# Gráficos financieros
# --------------------------------------------------------------------------
st.subheader("Análisis Financiero por Herramienta")
fc1, fc2 = st.columns(2)

with fc1:
    costo_melt = fin_f.melt(
        id_vars="Herramienta",
        value_vars=["Costo anual As-Is (S/.)", "Costo anual To-Be (S/.)"],
        var_name="Tipo", value_name="Costo (S/.)",
    )
    costo_melt["Tipo"] = costo_melt["Tipo"].str.replace(" (S/.)", "", regex=False)
    fig_costo = px.bar(
        costo_melt, x="Herramienta", y="Costo (S/.)", color="Tipo", barmode="group",
        title="Costo Anual: Antes vs Después",
        color_discrete_map={"Costo anual As-Is": "#ef4444", "Costo anual To-Be": "#10b981"},
    )
    fig_costo.update_layout(template="plotly_dark", plot_bgcolor="#0f172a", paper_bgcolor="#0f172a")
    st.plotly_chart(fig_costo, use_container_width=True)

with fc2:
    fig_recup = px.bar(
        fin_f, x="Herramienta", y="Recuperación (meses)", color="Herramienta",
        title="Tiempo de Recuperación de la Inversión (meses)",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_recup.update_layout(template="plotly_dark", plot_bgcolor="#0f172a", paper_bgcolor="#0f172a", showlegend=False)
    st.plotly_chart(fig_recup, use_container_width=True)

fig_ahorro = px.bar(
    fin_f, x="Herramienta", y="Ahorro anual (S/.)", color="Herramienta", text_auto=".2s",
    title="Ahorro Anual Generado por Herramienta",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_ahorro.update_layout(template="plotly_dark", plot_bgcolor="#0f172a", paper_bgcolor="#0f172a", showlegend=False)
st.plotly_chart(fig_ahorro, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
# Indicadores operativos por herramienta
# --------------------------------------------------------------------------
st.subheader("Indicadores Operativos por Herramienta")

for herramienta in sorted(ind_f["Herramienta"].unique(), key=lambda h: herramientas_all.index(h)):
    sub = ind_f[ind_f["Herramienta"] == herramienta]
    st.markdown(f"#### {herramienta}")
    indicadores = sub["Indicador"].unique()
    cols = st.columns(len(indicadores))
    for col, indicador in zip(cols, indicadores):
        d = sub[sub["Indicador"] == indicador].copy()
        d["Escenario"] = pd.Categorical(d["Escenario"], categories=ORDEN_ESCENARIO, ordered=True)
        d = d.sort_values("Escenario")
        fig = px.bar(
            d, x="Escenario", y="Valor", color="Escenario", title=indicador,
            color_discrete_map=COLOR_ESCENARIO,
        )
        fig.update_layout(
            template="plotly_dark", plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
            showlegend=False, height=280, margin=dict(t=40, b=10, l=10, r=10),
        )
        col.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
# Datos completos
# --------------------------------------------------------------------------
with st.expander("📋 Ver datos completos"):
    tab1, tab2 = st.tabs(["Indicadores", "Financiero"])
    with tab1:
        st.dataframe(ind_f, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(fin_f, use_container_width=True, hide_index=True)

st.caption("Dashboard generado para INDUREC · Taller Metalmecánico")
