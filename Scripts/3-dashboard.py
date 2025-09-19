import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard – Vendas (nomes exatos)", layout="wide")
st.title("📈 Dashboard simples – vendas_preenchido (PT‑BR)")

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
col1, col2, col3, col4 = st.columns(4)
col1.metric("Linhas (vendas)", f"{len(df_f):,}")
col2.metric("Receita (R$)", f"{df_f['Receita'].sum():,.2f}")
col3.metric("Quantidade total", f"{df_f['Quantidade'].sum():,}")
col4.metric("Lucro (R$)", f"{df_f['Lucro'].sum():,.2f}")

st.divider()

# 6) Gráficos em grid 2x2 (nativos)
A, B = st.columns(2)
C, D = st.columns(2)

with A:
    st.markdown("### Receita por dia")
    if df_f["Dia"].notna().any():
        ts = df_f.groupby("Dia", dropna=True)["Receita"].sum().reset_index()
        st.line_chart(ts, x="Dia", y="Receita", use_container_width=True)
    else:
        st.info("Sem datas válidas em 'Dia'.")

with B:
    st.markdown("### Top 10 Tipos por Receita")
    top_tipo = (
        df_f.groupby("Tipo")["Receita"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    st.bar_chart(top_tipo, x="Tipo", y="Receita", use_container_width=True)

with C:
    st.markdown("### Receita por Loja")
    por_loja = df_f.groupby("Loja")["Receita"].sum().reset_index()
    st.bar_chart(por_loja, x="Loja", y="Receita", use_container_width=True)

with D:
    st.markdown("### Dispersão – Valor de venda × Quantidade")
    st.scatter_chart(
        df_f.dropna(subset=["Valor de venda", "Quantidade"]),
        x="Valor de venda",
        y="Quantidade",
        use_container_width=True,
    )

st.divider()

# 7) Amostra da tabela filtrada
st.markdown("### Amostra de linhas filtradas")
st.dataframe(df_f.head(200), use_container_width=True)

st.caption(
    "Dashboard minimalista: filtros simples, 4 KPIs e 4 gráficos nativos do Streamlit."
)
