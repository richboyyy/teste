import streamlit as st
import pandas as pd

# --- Simulação de Dados (substitua pela sua fonte de dados) ---
# Em um projeto real, você leria estes dados de um CSV, banco de dados ou API.
data = {
    'Tipo': ['Recebido', 'Recebido', 'Gerado', 'Recebido', 'Gerado', 'Recebido', 'Recebido', 'Gerado'],
    'Processo': [
        '25351.916770/2021-50',
        '25351.811781/2024-87',
        '25351.917738/2025-15',
        '25351.910813/2025-17',
        '25351.919126/2025-67',
        '25351.931265/2022-16',
        '25351.912479/2025-36',
        '25351.927023/2025-71'
    ],
    'Responsavel': [
        'andre.magela',
        'ricardo.nascimento',
        'lidyanne.beresnitzky',
        'sara.dsilva',
        'maria.hcastro',
        'andre.magela',
        'cleo.leao',
        'andre.magela'
    ],
    # Mapeamento de ícones para emojis para facilitar a visualização
    'Icones': [
        ['📝'],
        ['❗️', '🔥', '✒️'],
        ['📄', '📝'],
        ['📄', '✅'],
        ['📄', '🌍'],
        ['🔵', '🟡'],
        ['📄', '📝'],
        [] # Processo sem ícones
    ]
}
df = pd.DataFrame(data)

# --- Configuração da Página do Streamlit ---
st.set_page_config(layout="wide", page_title="Dashboard de Processos SEI")
st.title("🔎 Painel de Consulta de Processos SEI")
st.markdown("Uma interface mais intuitiva para navegar e filtrar processos do SEI.")

# --- Barra Lateral de Filtros (`st.sidebar`) ---
st.sidebar.header("Painel de Filtros")

# Filtro por texto no número do processo
search_term = st.sidebar.text_input("Buscar por Número do Processo", placeholder="Digite parte do número...")

# Filtro por responsável
all_users = sorted(df['Responsavel'].unique())
selected_users = st.sidebar.multiselect("Responsável", options=all_users, default=all_users)

# Filtro por tipo de processo
process_type = st.sidebar.radio("Tipo de Processo", ["Todos", "Recebidos", "Gerados"], index=0)

# --- Lógica de Filtragem dos Dados ---
# Começa com o dataframe completo e aplica os filtros em sequência
df_filtered = df

if search_term:
    df_filtered = df_filtered[df_filtered['Processo'].str.contains(search_term, case=False)]

if selected_users:
    df_filtered = df_filtered[df_filtered['Responsavel'].isin(selected_users)]

if process_type != "Todos":
    df_filtered = df_filtered[df_filtered['Tipo'] == process_type

# --- Área Principal do Dashboard ---

# Métricas de Resumo no topo
st.header("Resumo Geral")
col1, col2, col3 = st.columns(3)

# Métrica 1: Total de processos na vista atual
col1.metric(
    label="Processos na Vista",
    value=f"{len(df_filtered)}",
    delta=f"de {len(df)} no total",
    delta_color="off"
)

# Métrica 2: Conta quantos processos são do tipo "Recebido"
recebidos_count = len(df_filtered[df_filtered['Tipo'] == 'Recebido'])
col2.metric(label="Processos Recebidos", value=recebidos_count)

# Métrica 3: Conta processos "urgentes" (que contêm o ícone ❗️)
# A função apply com lambda verifica se o ícone está na lista de ícones de cada linha
urgentes_count = df_filtered['Icones'].apply(lambda icons: '❗️' in icons).sum()
col3.metric(label="Processos Urgentes", value=urgentes_count)

st.markdown("---")

# Visualização dos processos filtrados em formato de cards
st.header("Lista de Processos")

if df_filtered.empty:
    st.warning("Nenhum processo encontrado com os filtros selecionados.")
else:
    # Itera sobre cada linha do DataFrame filtrado para criar um "card"
    for index, row in df_filtered.iterrows():
        st.write("") # Adiciona um espaço vertical
        with st.container(border=True):
            col1, col2 = st.columns([4, 1]) # Coluna da esquerda 4x maior que a da direita
            
            with col1:
                st.subheader(f"{row['Processo']}")
                st.caption(f"Tipo: {row['Tipo']} | Responsável: {row['Responsavel']}")

            with col2:
                # Exibe os ícones (emojis) com um bom espaçamento
                st.markdown(f"<p style='text-align: right; font-size: 1.5em;'>{' '.join(row['Icones'])}</p>", unsafe_allow_html=True)
                
                # Botão para abrir o processo (URL de exemplo)
                process_url = f"https://sei.sistem.gov.br/sei/controlador.php?acao=processo_visualizar&id_procedimento={row['Processo']}"
                st.link_button("Abrir no SEI", process_url, use_container_width=True)