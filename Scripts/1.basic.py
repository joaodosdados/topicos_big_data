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
st.caption(
    "Use texto e elementos de mídia para exibir informações, títulos e mensagens."
)
st.markdown("**Markdown** com _itálico_, **negrito**, e código `inline`.")
st.code("print('Olá, turma!')", language="python")
st.info("Caixa de informação")
st.warning("Aviso")
st.error("Erro (exemplo)")
st.success("Sucesso")


st.header("Inputs comuns")
st.caption(
    "Colete informações do usuário com os componentes de input mais utilizados."
)
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

st.header("Inputs de Data, Hora e Cor")
st.caption(
    "Utilize inputs especializados para coletar dados como datas, horas e cores."
)

col1, col2, col3 = st.columns(3)
with col1:
    data = st.date_input("Data de nascimento")
    st.write(f"Data selecionada: {data}")
with col2:
    hora = st.time_input("Horário de entrada")
    st.write(f"Horário selecionado: {hora}")
with col3:
    cor = st.color_picker("Escolha uma cor", "#00f900")
    st.write(f"Cor selecionada: {cor}")

st.header("Interatividade Combinada")
st.caption(
    "Combine o estado de múltiplos widgets para criar uma lógica mais complexa e saídas personalizadas."
)
if st.button("Gerar mensagem personalizada"):
    st.markdown(
        f'<div style="color: {cor};">Olá, {nome}! Sua data de nascimento é {data.strftime("%d/%m/%Y")}.</div>',
        unsafe_allow_html=True,
    )


st.header("Upload (extra)")
st.caption(
    "Permita que os usuários enviem seus próprios arquivos para análise no aplicativo."
)
up = st.file_uploader("Faça upload de um CSV", type=["csv"])
if up is not None:
    df_up = pd.read_csv(up)
    st.dataframe(df_up.head())


st.caption("Pronto! Esses são os widgets que mais usamos em aulas.")
