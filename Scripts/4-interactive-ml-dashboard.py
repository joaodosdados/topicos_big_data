import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import plotly.figure_factory as ff

st.set_page_config(page_title="Dashboard de ML Interativo", layout="wide")


@st.cache_data
def load_data(file):
    return pd.read_csv(file)


def main():
    st.title("🚀 Dashboard Interativo de Machine Learning")
    st.write(
        "Faça upload de um CSV, selecione as colunas, treine um modelo e veja os resultados!"
    )

    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.success("Dados carregados com sucesso!")

        with st.expander("Visualizar dados"):
            st.dataframe(df.head())

        st.sidebar.header("Configurações do Modelo")
        target_column = st.sidebar.selectbox(
            "Selecione a coluna alvo (target)", df.columns
        )
        feature_columns = st.sidebar.multiselect(
            "Selecione as colunas de features",
            [col for col in df.columns if col != target_column],
        )

        model_choice = st.sidebar.selectbox(
            "Escolha o modelo", ["Regressão Logística", "Random Forest"]
        )

        if st.sidebar.button("Treinar Modelo"):
            if not feature_columns:
                st.warning("Por favor, selecione pelo menos uma feature.")
                st.stop()

            # Lidar com dados ausentes e categóricos de forma simples
            df_processed = df.copy()
            for col in feature_columns:
                if df_processed[col].dtype == "object":
                    df_processed = pd.get_dummies(
                        df_processed, columns=[col], drop_first=True
                    )
                elif df_processed[col].isnull().any():
                    df_processed[col].fillna(df_processed[col].median(), inplace=True)

            feature_columns_processed = [
                c for c in df_processed.columns if c in feature_columns or any(c.startswith(f + '_') for f in feature_columns)
            ]


            X = df_processed[feature_columns_processed]
            y = df_processed[target_column]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )

            if model_choice == "Regressão Logística":
                model = LogisticRegression()
            else:
                model = RandomForestClassifier()

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            cm = confusion_matrix(y_test, y_pred)

            st.subheader("Resultados do Modelo")
            st.metric("Acurácia", f"{accuracy:.4f}")

            st.subheader("Matriz de Confusão")
            fig = ff.create_annotated_heatmap(
                z=cm,
                x=["Previsto Negativo", "Previsto Positivo"],
                y=["Real Negativo", "Real Positivo"],
                colorscale="Viridis",
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
