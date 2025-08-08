import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Leitura da Planilha ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("planilha_processos.csv", sep=";", encoding="utf-8")
    # Criar data fictícia se não existir
    if "Data" not in df.columns:
        np.random.seed(42)
        datas_falsas = [datetime.today() - timedelta(days=np.random.randint(0, 200)) for _ in range(len(df))]
        df["Data"] = datas_falsas
    else:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    return df

df = carregar_dados()

# --- Função para ícones e cores ---
def get_marker_icon_color(marcador):
    mapping = {
        "Administrativo - Gestão": ("📊", "#2E86C1"),
        "Aguardando Resposta da Área Responsável": ("⏳", "#E67E22"),
        "Comunicação": ("🗣️", "#27AE60"),
        "Reclamação, Sugestão, Solicitação - Manifestação": ("📬", "#C0392B")
    }
    return mapping.get(marcador, ("📁", "#7F8C8D"))

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Dashboard de Processos SEI")
st.title("🔎 Painel de Consulta de Processos SEI")

# --- Barra Lateral de Filtros ---
st.sidebar.header("Painel de Filtros")
search_term = st.sidebar.text_input("Buscar", placeholder="Número, descrição ou assunto...")
all_users = sorted(df['Responsável'].dropna().unique())
selected_users = st.sidebar.multiselect("Responsável", options=all_users, default=all_users)
all_marcadores = sorted(df['Marcador'].dropna().unique())
selected_marcadores = st.sidebar.multiselect("Marcador", options=all_marcadores, default=all_marcadores)

# Filtro por período
min_date, max_date = df["Data"].min(), df["Data"].max()
date_range = st.sidebar.date_input("Período", [min_date, max_date])

# --- Filtragem ---
df_filtered = df.copy()

if search_term:
    df_filtered = df_filtered[
        df_filtered['Número'].str.contains(search_term, case=False, na=False) |
        df_filtered['Descrição'].str.contains(search_term, case=False, na=False) |
        df_filtered['Assunto'].str.contains(search_term, case=False, na=False)
    ]

if selected_users:
    df_filtered = df_filtered[df_filtered['Responsável'].isin(selected_users)]

if selected_marcadores:
    df_filtered = df_filtered[df_filtered['Marcador'].isin(selected_marcadores)]

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[(df_filtered["Data"] >= pd.to_datetime(start_date)) &
                               (df_filtered["Data"] <= pd.to_datetime(end_date))]

# --- Resumo Geral ---
SLA_MAX = 120  # Dias para vencimento do SLA

st.header("Resumo Geral")
col1, col2, col3, col4 = st.columns(4)

# Processos na vista
col1.metric(
    "Processos na Vista",
    f"{len(df_filtered)}",
    delta=f"de {len(df)} no total",
    delta_color="off"
)

# Aguardando resposta
col2.metric(
    "Aguardando Resposta",
    len(df_filtered[df_filtered['Marcador'] == "Aguardando Resposta da Área Responsável"])
)

# Vencidos no SLA
vencidos_count = sum((datetime.today() - row["Data"]).days > SLA_MAX for _, row in df_filtered.iterrows())
col3.metric(
    "🔴 Vencidos SLA",
    vencidos_count
)

# Quase vencendo no SLA
quase_count = sum(SLA_MAX * 0.8 <= (datetime.today() - row["Data"]).days <= SLA_MAX for _, row in df_filtered.iterrows())
col4.metric(
    "🟠 Quase Vencendo",
    quase_count
)

# --- Botão para exportar CSV filtrado ---
csv_download = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Baixar CSV filtrado", csv_download, "processos_filtrados.csv", "text/csv")

st.markdown("---")

# --- Lista de Processos ---
st.header("📋 Lista de Processos")

if df_filtered.empty:
    st.warning("Nenhum processo encontrado com os filtros selecionados.")
else:
    for _, row in df_filtered.iterrows():
        icon, color = get_marker_icon_color(row['Marcador'])
        
        dias_passados = (datetime.today() - row["Data"]).days
        progresso = min(100, int((dias_passados / SLA_MAX) * 100))
        
        # Determinar status de prazo
        if dias_passados > SLA_MAX:
            prazo_status = f"🔴 Prazo Vencido ({dias_passados} dias)"
            barra_cor = "red"
        elif dias_passados >= SLA_MAX * 0.8:
            prazo_status = f"🟠 Quase Vencendo ({dias_passados} dias)"
            barra_cor = "orange"
        else:
            prazo_status = f"🟢 Dentro do Prazo ({dias_passados} dias)"
            barra_cor = "green"
        
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {icon} <span style='color:{color}'>{row['Número']}</span>", unsafe_allow_html=True)
                st.caption(f"Responsável: {row['Responsável']} | Marcador: {row['Marcador']} | Data: {row['Data'].date()}")
                
                st.markdown(f"<div style='background-color:{barra_cor};height:15px;width:{progresso}%;border-radius:5px'></div>", unsafe_allow_html=True)
                st.write(f"**SLA:** {prazo_status}")
                
                if pd.notna(row['Descrição']):
                    st.write(row['Descrição'])
                if pd.notna(row['Assunto']):
                    st.write(f"**Assunto:** {row['Assunto']}")
            with col2:
                if st.button("Ver detalhes", key=row['Número']):
                    st.session_state["detalhes"] = row.to_dict()
                process_url = f"https://sei.sistem.gov.br/sei/controlador.php?acao=processo_visualizar&id_procedimento={row['Número']}"
                st.link_button("Abrir no SEI", process_url, use_container_width=True)

# --- Página de detalhes ---
if "detalhes" in st.session_state:
    st.sidebar.markdown("### 📄 Detalhes do Processo Selecionado")
    for k, v in st.session_state["detalhes"].items():
        st.sidebar.write(f"**{k}:** {v}")
