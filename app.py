import streamlit as st
import pandas as pd

# --- Leitura da Planilha ---
@st.cache_data
def carregar_dados():
    return pd.read_csv("planilha_processos.csv", sep=";", encoding="utf-8")

df = carregar_dados()

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Dashboard de Processos SEI")
st.title("🔎 Painel de Consulta de Processos SEI")
st.markdown("Uma interface para navegar e filtrar processos do SEI com base na planilha de dados.")

# --- Barra Lateral de Filtros ---
st.sidebar.header("Painel de Filtros")

# Filtro por texto no número do processo
search_term = st.sidebar.text_input("Buscar por Número do Processo", placeholder="Digite parte do número...")

# Filtro por responsável
all_users = sorted(df['Responsável'].dropna().unique())
selected_users = st.sidebar.multiselect("Responsável", options=all_users, default=all_users)

# Filtro por marcador
all_marcadores = sorted(df['Marcador'].dropna().unique())
selected_marcadores = st.sidebar.multiselect("Marcador", options=all_marcadores, default=all_marcadores)

# --- Lógica de Filtragem ---
df_filtered = df.copy()

if search_term:
    df_filtered = df_filtered[df_filtered['Número'].str.contains(search_term, case=False, na=False)]

if selected_users:
    df_filtered = df_filtered[df_filtered['Responsável'].isin(selected_users)]

if selected_marcadores:
    df_filtered = df_filtered[df_filtered['Marcador'].isin(selected_marcadores)]

# --- Métricas de Resumo ---
st.header("Resumo Geral")
col1, col2, col3 = st.columns(3)

col1.metric(
    label="Processos na Vista",
    value=f"{len(df_filtered)}",
    delta=f"de {len(df)} no total",
    delta_color="off"
)

# Total por marcador (exemplo: "Administrativo - Gestão")
col2.metric(
    label="Administrativo - Gestão",
    value=len(df_filtered[df_filtered['Marcador'] == "Administrativo - Gestão"])
)

# Total por marcador específico (exemplo: "Aguardando Resposta da Área Responsável")
col3.metric(
    label="Aguardando Resposta",
    value=len(df_filtered[df_filtered['Marcador'] == "Aguardando Resposta da Área Responsável"])
)

st.markdown("---")

# --- Lista de Processos (Cards) ---
st.header("Lista de Processos")

if df_filtered.empty:
    st.warning("Nenhum processo encontrado com os filtros selecionados.")
else:
    for _, row in df_filtered.iterrows():
        st.write("")  # Espaçamento
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(f"{row['Número']}")
                st.caption(f"Responsável: {row['Responsável']} | Marcador: {row['Marcador']}")
                if pd.notna(row['Descrição']):
                    st.write(row['Descrição'])
                if pd.notna(row['Assunto']):
                    st.write(f"**Assunto:** {row['Assunto']}")
            with col2:
                process_url = f"https://sei.sistem.gov.br/sei/controlador.php?acao=processo_visualizar&id_procedimento={row['Número']}"
                st.link_button("Abrir no SEI", process_url, use_container_width=True)
