import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Vendas – Vários Gráficos", layout="wide")


@st.cache
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Arquivo não encontrado: {path}")
        st.stop()
    return pd.read_csv(path, sep=";")


def get_column_mapping(df):
    cols = df.columns.tolist()

    def _suggest(name_options):
        for n in name_options:
            if n in cols:
                return n
        return None

    st.sidebar.header("Mapeamento de colunas")
    mapping = {
        "data": st.sidebar.selectbox(
            "Coluna de data (opcional)",
            ["(nenhuma)"] + cols,
            index=(["(nenhuma)"] + cols).index(
                _suggest(["data", "Data", "data_venda", "data_pedido"]) or "(nenhuma)"
            ),
        ),
        "produto": st.sidebar.selectbox(
            "Coluna de produto (opcional)",
            ["(nenhuma)"] + cols,
            index=(["(nenhuma)"] + cols).index(
                _suggest(["produto", "Produto", "product"]) or "(nenhuma)"
            ),
        ),
        "categoria": st.sidebar.selectbox(
            "Coluna de categoria (opcional)",
            ["(nenhuma)"] + cols,
            index=(["(nenhuma)"] + cols).index(
                _suggest(["categoria", "Categoria", "category"]) or "(nenhuma)"
            ),
        ),
        "valor": st.sidebar.selectbox(
            "Coluna de valor_total (se já existir)",
            ["(nenhuma)"] + cols,
            index=(["(nenhuma)"] + cols).index(
                _suggest(["valor_total", "Valor_Total", "valor", "total"])
                or "(nenhuma)"
            ),
        ),
        "preco": st.sidebar.selectbox(
            "Coluna de preço",
            ["(nenhuma)"] + cols,
            index=(["(nenhuma)"] + cols).index(
                _suggest(["preco", "Preço", "price"]) or "(nenhuma)"
            ),
        ),
        "qtd": st.sidebar.selectbox(
            "Coluna de quantidade",
            ["(nenhuma)"] + cols,
            index=(["(nenhuma)"] + cols).index(
                _suggest(["quantidade", "Quantidade", "qtd", "qty"]) or "(nenhuma)"
            ),
        ),
    }
    return mapping


def prepare_data(df, mapping):
    df_prep = df.copy()
    if mapping["data"] != "(nenhuma)":
        df_prep[mapping["data"]] = pd.to_datetime(
            df_prep[mapping["data"]], errors="coerce"
        )

    valor_series = None
    if mapping["valor"] != "(nenhuma)" and mapping["valor"] in df_prep.columns:
        valor_series = pd.to_numeric(df_prep[mapping["valor"]], errors="coerce")
    elif (
        mapping["preco"] != "(nenhuma)"
        and mapping["qtd"] != "(nenhuma)"
        and mapping["preco"] in df_prep.columns
        and mapping["qtd"] in df_prep.columns
    ):
        valor_series = pd.to_numeric(
            df_prep[mapping["preco"]], errors="coerce"
        ).fillna(0) * pd.to_numeric(df_prep[mapping["qtd"]], errors="coerce").fillna(
            0
        )
    return df_prep, valor_series


def filter_data(df, valor_series, mapping):
    df_f = df.copy()
    if mapping["data"] != "(nenhuma)" and df_f[mapping["data"]].notna().any():
        dmin, dmax = df_f[mapping["data"]].min().date(), df_f[mapping["data"]].max().date()
        d1, d2 = st.sidebar.date_input("Período", (dmin, dmax))
        if isinstance(d1, tuple):
            d1, d2 = d1
        mask = (df_f[mapping["data"]] >= pd.to_datetime(d1)) & (
            df_f[mapping["data"]] <= pd.to_datetime(d2)
        )
        df_f = df_f[mask]

    if mapping["categoria"] != "(nenhuma)":
        cats = ["(todas)"] + sorted(
            [c for c in df_f[mapping["categoria"]].dropna().unique()]
        )
        sel = st.sidebar.selectbox("Categoria", cats)
        if sel != "(todas)":
            df_f = df_f[df_f[mapping["categoria"]] == sel]

    valor_f = valor_series.loc[df_f.index] if valor_series is not None else None
    return df_f, valor_f


def plot_charts(df, valor, mapping):
    tab1, tab2, tab3 = st.tabs(
        ["Séries Temporais", "Análise de Produtos e Categorias", "Distribuição e Dispersão"]
    )

    with tab1:
        if mapping["data"] != "(nenhuma)" and valor is not None:
            st.subheader("Faturamento ao longo do tempo")
            ts = (
                pd.DataFrame({"data": df[mapping["data"]], "valor": valor})
                .dropna(subset=["data", "valor"])
                .groupby("data")["valor"]
                .sum()
                .reset_index()
            )
            fig = px.line(ts, x="data", y="valor", title="Faturamento por Dia")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Selecione uma coluna de data e uma de valor para ver o gráfico de séries temporais.")

    with tab2:
        if mapping["produto"] != "(nenhuma)" and valor is not None:
            st.subheader("Top 5 produtos por faturamento")
            top_prod = (
                pd.DataFrame({"produto": df[mapping["produto"]], "valor": valor})
                .dropna(subset=["produto", "valor"])
                .groupby("produto")["valor"]
                .sum()
                .nlargest(5)
                .reset_index()
            )
            fig = px.bar(top_prod, x="produto", y="valor", title="Top 5 Produtos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Selecione uma coluna de produto e uma de valor para ver o top produtos.")

        if mapping["categoria"] != "(nenhuma)" and valor is not None:
            st.subheader("Participação de faturamento por categoria")
            cat = (
                pd.DataFrame({"categoria": df[mapping["categoria"]], "valor": valor})
                .dropna(subset=["categoria", "valor"])
                .groupby("categoria")["valor"]
                .sum()
                .reset_index()
            )
            fig = px.pie(cat, names="categoria", values="valor", title="Faturamento por Categoria")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Selecione uma coluna de categoria e uma de valor para ver o gráfico de pizza.")

    with tab3:
        if valor is not None:
            st.subheader("Distribuição do valor de cada venda")
            fig = px.histogram(valor.dropna(), title="Distribuição de Valores")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Selecione uma coluna de valor para ver o histograma.")

        if (
            mapping["preco"] != "(nenhuma)"
            and mapping["qtd"] != "(nenhuma)"
            and mapping["preco"] in df.columns
            and mapping["qtd"] in df.columns
        ):
            st.subheader("Dispersão preço × quantidade")
            fig = px.scatter(
                df,
                x=mapping["preco"],
                y=mapping["qtd"],
                title="Dispersão Preço vs. Quantidade",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Selecione colunas de preço e quantidade para ver o gráfico de dispersão.")


def main():
    st.title("📊 Exemplos de gráficos com dados de vendas (colunas originais)")
    CSV_PATH = "data/vendas_preenchido.csv"

    df = load_data(CSV_PATH)
    st.caption(
        f"Arquivo carregado: {CSV_PATH} — {len(df):,} linhas | {len(df.columns)} colunas"
    )
    with st.expander("Visualizar dados brutos"):
        st.dataframe(df.head(10), use_container_width=True)

    mapping = get_column_mapping(df)
    df_prepared, valor_series = prepare_data(df, mapping)
    df_filtered, valor_filtered = filter_data(df_prepared, valor_series, mapping)
    plot_charts(df_filtered, valor_filtered, mapping)

    st.caption(
        "Os nomes das colunas são mantidos como no CSV. Use o mapeamento na sidebar."
    )


if __name__ == "__main__":
    main()
