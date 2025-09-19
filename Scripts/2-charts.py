import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Vendas – Vários Gráficos", layout="wide")
st.title("📊 Exemplos de gráficos com dados de vendas (colunas originais)")

# --- 1) Carrega CSV sem alterar nomes de colunas ---
CSV_PATH = "data/vendas_preenchido.csv"
if not os.path.exists(CSV_PATH):
    st.error("Coloque o arquivo 'vendas_preenchido.csv' dentro da pasta data/.")
    st.stop()

df = pd.read_csv(CSV_PATH, sep=";")
st.caption(
    f"Arquivo carregado: {CSV_PATH} — {len(df):,} linhas | {len(df.columns)} colunas"
)
st.dataframe(df.head(10), use_container_width=True)

# --- 2) Mapear colunas manualmente (mantendo nomes originais) ---
cols = df.columns.tolist()


# Sugestões automáticas (se existirem)
def _suggest(name_options):
    for n in name_options:
        if n in cols:
            return n
    return None


st.sidebar.header("Mapeamento de colunas")
col_data = st.sidebar.selectbox(
    "Coluna de data (opcional)",
    ["(nenhuma)"] + cols,
    index=(["(nenhuma)"] + cols).index(
        _suggest(["data", "Data", "data_venda", "data_pedido"]) or "(nenhuma)"
    ),
)
col_produto = st.sidebar.selectbox(
    "Coluna de produto (opcional)",
    ["(nenhuma)"] + cols,
    index=(["(nenhuma)"] + cols).index(
        _suggest(["produto", "Produto", "product"]) or "(nenhuma)"
    ),
)
col_categoria = st.sidebar.selectbox(
    "Coluna de categoria (opcional)",
    ["(nenhuma)"] + cols,
    index=(["(nenhuma)"] + cols).index(
        _suggest(["categoria", "Categoria", "category"]) or "(nenhuma)"
    ),
)
col_cliente = st.sidebar.selectbox(
    "Coluna de cliente (opcional)",
    ["(nenhuma)"] + cols,
    index=(["(nenhuma)"] + cols).index(
        _suggest(["cliente", "Cliente", "customer"]) or "(nenhuma)"
    ),
)

col_valor = st.sidebar.selectbox(
    "Coluna de valor_total (se já existir)",
    ["(nenhuma)"] + cols,
    index=(["(nenhuma)"] + cols).index(
        _suggest(["valor_total", "Valor_Total", "valor", "total"]) or "(nenhuma)"
    ),
)

st.sidebar.markdown("**Ou** informe preço × quantidade para calcular o valor:")
col_preco = st.sidebar.selectbox(
    "Coluna de preço",
    ["(nenhuma)"] + cols,
    index=(["(nenhuma)"] + cols).index(
        _suggest(["preco", "Preço", "price"]) or "(nenhuma)"
    ),
)
col_qtd = st.sidebar.selectbox(
    "Coluna de quantidade",
    ["(nenhuma)"] + cols,
    index=(["(nenhuma)"] + cols).index(
        _suggest(["quantidade", "Quantidade", "qtd", "qty"]) or "(nenhuma)"
    ),
)

# --- 3) Preparos de tipos (sem renomear) ---
if col_data != "(nenhuma)":
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")

# Cria coluna virtual de valor (Series) para gráficos
valor_series = None
if col_valor != "(nenhuma)" and col_valor in df.columns:
    valor_series = pd.to_numeric(df[col_valor], errors="coerce")
elif (
    col_preco != "(nenhuma)"
    and col_qtd != "(nenhuma)"
    and col_preco in df.columns
    and col_qtd in df.columns
):
    valor_series = pd.to_numeric(df[col_preco], errors="coerce").fillna(
        0
    ) * pd.to_numeric(df[col_qtd], errors="coerce").fillna(0)

# --- 4) Filtros simples ---
df_f = df.copy()
if col_data != "(nenhuma)" and df_f[col_data].notna().any():
    dmin, dmax = df_f[col_data].min().date(), df_f[col_data].max().date()
    d1, d2 = st.sidebar.date_input("Período", (dmin, dmax))
    if isinstance(d1, tuple):  # compatibilidade
        d1, d2 = d1
    mask = (df_f[col_data] >= pd.to_datetime(d1)) & (
        df_f[col_data] <= pd.to_datetime(d2)
    )
    df_f = df_f[mask]

if col_categoria != "(nenhuma)":
    cats = ["(todas)"] + sorted([c for c in df_f[col_categoria].dropna().unique()])
    sel = st.sidebar.selectbox("Categoria", cats)
    if sel != "(todas)":
        df_f = df_f[df_f[col_categoria] == sel]

# Atualiza valor para o filtrado
if valor_series is not None:
    valor_f = valor_series.loc[df_f.index]
else:
    valor_f = None

st.write("Visualização de dados básicos de vendas.")

# --- 5) Gráficos ---
# 5.1 Linha: faturamento ao longo do tempo
if col_data != "(nenhuma)" and valor_f is not None:
    st.subheader("Faturamento ao longo do tempo")
    ts = (
        pd.DataFrame({"data": df_f[col_data], "valor": valor_f})
        .dropna(subset=["data", "valor"])
        .groupby("data")["valor"]
        .sum()
        .reset_index()
    )
    st.line_chart(ts, x="data", y="valor", use_container_width=True)

# 5.2 Barras: Top N produtos por faturamento
if col_produto != "(nenhuma)" and valor_f is not None:
    st.subheader("Top 5 produtos por faturamento")
    top_prod = (
        pd.DataFrame({"produto": df_f[col_produto], "valor": valor_f})
        .dropna(subset=["produto", "valor"])
        .groupby("produto")["valor"]
        .sum()
        .nlargest(5)
        .reset_index()
    )
    st.bar_chart(top_prod, x="produto", y="valor", use_container_width=True)

# 5.3 Pizza: participação por categoria (matplotlib)
if col_categoria != "(nenhuma)" and valor_f is not None:
    st.subheader("Participação de faturamento por categoria")
    cat = (
        pd.DataFrame({"categoria": df_f[col_categoria], "valor": valor_f})
        .dropna(subset=["categoria", "valor"])
        .groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
    )
    fig, ax = plt.subplots()
    ax.pie(cat.values, labels=cat.index, autopct="%1.1f%%")
    ax.axis("equal")
    st.pyplot(fig, use_container_width=True)

# 5.4 Histograma: distribuição de valor
if valor_f is not None:
    st.subheader("Distribuição do valor de cada venda")
    fig2, ax2 = plt.subplots()
    ax2.hist(valor_f.dropna().values, bins=20)
    ax2.set_title("Distribuição de valores")
    ax2.set_xlabel("valor")
    ax2.set_ylabel("freq")
    st.pyplot(fig2, use_container_width=True)

# 5.5 Dispersão: preço vs quantidade (se ambas existirem)
if (
    col_preco != "(nenhuma)"
    and col_qtd != "(nenhuma)"
    and col_preco in df_f.columns
    and col_qtd in df_f.columns
):
    st.subheader("Dispersão preço × quantidade")
    st.scatter_chart(
        df_f[[col_preco, col_qtd]].dropna(),
        x=col_preco,
        y=col_qtd,
        use_container_width=True,
    )

st.caption(
    "Os nomes das colunas são mantidos exatamente como estão no CSV. Use o mapeamento na sidebar quando necessário."
)
