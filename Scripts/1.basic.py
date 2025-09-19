import streamlit as st
import pandas as pd

path = "data/vendas_preenchido.csv"
df = pd.read_csv(path, sep=";")


st.set_page_config(page_title="Streamlit – Componentes", layout="wide")
st.title("🧩 Componentes básicos do Streamlit")
st.write("Esta página demonstra textos, inputs e interações.")


with st.expander("📥 Carregar dados (opcional)"):
    try:
        st.success(f"Dados carregados de: {path}")
        st.dataframe(df.head(10), use_container_width=True)
    except Exception as e:
        st.info("Você pode rodar este script sem dados ou colocar o CSV depois.")
        st.exception(e)


st.header("Texto & mídia")
st.markdown("**Markdown** com _itálico_, **negrito**, e código `inline`.")
st.code("print('Olá, turma!')", language="python")
st.info("Caixa de informação")
st.warning("Aviso")
st.error("Erro (exemplo)")
st.success("Sucesso")


st.header("Inputs comuns")
col1, col2, col3 = st.columns(3)
with col1:
    nome = st.text_input("Seu nome", value="João")
    ok = st.button("Dizer oi")
if ok:
    st.write(f"Olá, {nome} 👋")
with col2:
    idade = st.number_input("Idade", min_value=0, max_value=120, value=25, step=1)
st.write(f"Idade registrada: {idade}")
with col3:
    nota = st.slider("Avalie a aula", min_value=0, max_value=10, value=8)
    st.write(f"Nota: {nota}")


opcao = st.selectbox("Escolha um tema", ["Pandas", "Streamlit", "SQL", "ML"])
checks = st.multiselect(
    "Quais assuntos você domina?", ["Pandas", "Numpy", "Plot"], default=["Pandas"]
)
aceito = st.checkbox("Li e aceito as regras da turma")


st.write({"opcao": opcao, "checks": checks, "aceito": aceito})


st.header("Upload (extra)")
up = st.file_uploader("Faça upload de um CSV", type=["csv"])
if up is not None:
    df_up = pd.read_csv(up)
    st.dataframe(df_up.head())


st.caption("Pronto! Esses são os widgets que mais usamos em aulas.")
