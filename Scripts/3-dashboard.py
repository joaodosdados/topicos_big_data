import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard – Vendas (nomes exatos)", layout="wide")
st.title("📈 Dashboard de Vendas")

CSV_PATH = "data/vendas_preenchido.csv"

# 1) Carrega CSV com separador ';' e usa nomes EXATOS
try:
    df = pd.read_csv(CSV_PATH, sep=";")
except FileNotFoundError:
    st.error("Coloque o arquivo 'vendas_preenchido.csv' dentro da pasta data/.")
    st.stop()

st.caption(f"Arquivo: {CSV_PATH} — {len(df):,} linhas | {len(df.columns)} colunas")

# 2) Validação mínima
required = [
    "Dia",
    "Loja",
    "Quantidade",
    "Tipo",
    "Marca",
    "Custo de compra",
    "Valor de venda",
]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Faltam colunas no CSV: {', '.join(missing)}")
    st.stop()

# 3) Tipos e colunas derivadas (sem renomear nada)
df["Dia"] = pd.to_datetime(df["Dia"], errors="coerce")
df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce")
df["Valor de venda"] = pd.to_numeric(df["Valor de venda"], errors="coerce")
df["Custo de compra"] = pd.to_numeric(df["Custo de compra"], errors="coerce")

if "Receita" not in df.columns:
    df["Receita"] = df["Valor de venda"] * df["Quantidade"]
if "Custo Total" not in df.columns:
    df["Custo Total"] = df["Custo de compra"] * df["Quantidade"]
if "Lucro" not in df.columns:
    df["Lucro"] = df["Receita"] - df["Custo Total"]

# 4) Filtros mínimos (simples)
st.sidebar.header("Filtros")
df_f = df.copy()
if df_f["Dia"].notna().any():
    dmin, dmax = df_f["Dia"].min().date(), df_f["Dia"].max().date()
    d1, d2 = st.sidebar.date_input("Período", (dmin, dmax))
    if isinstance(d1, tuple):  # compatibilidade
        d1, d2 = d1
    mask = (df_f["Dia"] >= pd.to_datetime(d1)) & (df_f["Dia"] <= pd.to_datetime(d2))
    df_f = df_f[mask]

# Filtros opcionais
if "Loja" in df_f.columns:
    lojas = sorted(df["Loja"].dropna().unique().tolist())
    sel_lojas = st.sidebar.multiselect("Lojas", lojas, default=[])
    if sel_lojas:
        df_f = df_f[df_f["Loja"].isin(sel_lojas)]

if "Tipo" in df_f.columns:
    tipos = sorted(df["Tipo"].dropna().unique().tolist())
    sel_tipos = st.sidebar.multiselect("Tipos", tipos, default=[])
    if sel_tipos:
        df_f = df_f[df_f["Tipo"].isin(sel_tipos)]

# 5) KPIs
st.subheader("KPIs")
kpi1, kpi2, kpi3 = st.columns(3)
kpi4, kpi5, kpi6 = st.columns(3)

receita_total = df_f["Receita"].sum()
lucro_total = df_f["Lucro"].sum()
qtd_total = df_f["Quantidade"].sum()
num_vendas = len(df_f)

kpi1.metric("Vendas realizadas", f"{num_vendas:,}")
kpi2.metric("Receita Total (R$)", f"{receita_total:,.2f}")
kpi3.metric(
    "Ticket Médio (R$)",
    f"{receita_total / num_vendas:,.2f}" if num_vendas > 0 else "N/A",
)
kpi4.metric("Itens Vendidos", f"{qtd_total:,}")
kpi5.metric("Lucro Total (R$)", f"{lucro_total:,.2f}")
kpi6.metric(
    "Margem de Lucro (%)",
    f"{(lucro_total / receita_total) * 100:,.2f}%" if receita_total > 0 else "N/A",
)


st.divider()

# 6) Gráficos
st.subheader("Análises Gráficas")
A, B = st.columns(2)
C, D = st.columns(2)

with A:
    st.markdown("### Receita por Dia")
    if df_f["Dia"].notna().any():
        ts = df_f.groupby("Dia")["Receita"].sum().reset_index()
        fig = px.line(ts, x="Dia", y="Receita", title="Receita Diária")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem datas válidas em 'Dia'.")

with B:
    st.markdown("### Receita por Tipo de Produto")
    por_tipo = df_f.groupby("Tipo")["Receita"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(por_tipo, x="Tipo", y="Receita", title="Receita por Tipo")
    st.plotly_chart(fig, use_container_width=True)

with C:
    st.markdown("### Receita por Loja")
    por_loja = df_f.groupby("Loja")["Receita"].sum().reset_index()
    fig = px.pie(por_loja, names="Loja", values="Receita", title="Participação da Receita por Loja")
    st.plotly_chart(fig, use_container_width=True)

with D:
    st.markdown("### Receita por Tipo de Produto em cada Loja")
    receita_loja_tipo = (
        df_f.groupby(["Loja", "Tipo"])["Receita"].sum().reset_index()
    )
    fig = px.bar(
        receita_loja_tipo,
        x="Loja",
        y="Receita",
        color="Tipo",
        title="Receita por Tipo de Produto em cada Loja",
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# 7) Amostra da tabela filtrada
st.markdown("### Amostra de linhas filtradas")
st.dataframe(df_f.head(200), use_container_width=True)

st.caption(
    "Dashboard minimalista: filtros simples, 4 KPIs e 4 gráficos nativos do Streamlit."
)
