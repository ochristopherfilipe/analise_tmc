# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Análise de Ministérios IDPB Filadélfia", layout="wide")

st.title("Análise de Ministérios IDPB Filadélfia")

# Leitura dos dados
@st.cache_data
def carregar_dados():
    # Substitua 'dados.csv' pelo nome do arquivo que contém seus dados
    df = pd.read_csv('dados.csv', delimiter=',', quotechar='"', encoding='utf-8')
    
    # Remover colunas indesejadas, se existirem
    colunas_para_remover = ['Carimbo de data/hora', 'id', 'index']
    df = df.drop(columns=colunas_para_remover, errors='ignore')
    
    # Remover espaços em branco das colunas e das células
    df.columns = df.columns.str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Conversão de porcentagens para valores numéricos
    porcentagem_cols = [
        'Dízimos praticados em 2024:',
        'Ofertas praticadas em 2024:',
        'Ofertas destinadas a Missões praticadas em 2024:',
        'Dificuldades financeiras, onde “0” é estar sem dívidas e “100” é estar muito endividado:',
        'Está satisfeito financeiramente, onde “0” é estar insatisfeito e “100” é estar satisfeito:',
        'Considera correta sua assiduidade nas Celebrações, onde “0” é estar incorreto e “100” é estar correto:',
        'Considera correta sua assiduidade na sua Célula, onde “0” é estar incorreto e “100” é estar correto:',
        'Considera correta sua assiduidade em seu Ministério, onde “0” é estar incorreto e “100” é estar correto:'
    ]
    
    for col in porcentagem_cols:
        df[col] = df[col].astype(str).str.replace('%', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Padronizar valores de porcentagem para 0, 25, 50, 75 ou 100
    def padronizar_porcentagem(valor):
        if valor <= 12.5:
            return 0
        elif valor <= 37.5:
            return 25
        elif valor <= 62.5:
            return 50
        elif valor <= 87.5:
            return 75
        else:
            return 100

    for col in porcentagem_cols:
        df[col] = df[col].apply(padronizar_porcentagem)
    
    # Renomear colunas para facilitar o acesso
    df = df.rename(columns={
        'Nome de usuário': 'Email',
        'Nome do Membro': 'Nome',
        'Ministérios que participa': 'Ministérios',
        'Dificuldades financeiras, onde “0” é estar sem dívidas e “100” é estar muito endividado:': 'Dificuldades Financeiras',
        'Está satisfeito financeiramente, onde “0” é estar insatisfeito e “100” é estar satisfeito:': 'Satisfação Financeira',
        'Selecione seu Estado Civil': 'Estado Civil',
        'Está em relacionamento romântico?': 'Em Relacionamento',
        'Como você considera seu engajamento e desempenho em seu Ministério?': 'Engajamento',
        'Escreva aqui o que deseja compartilhar como uma estratégia de melhoria em seu Ministério:': 'Estratégia de Melhoria'
    })
    
    # Remover espaços em branco nas células (novamente, após renomear colunas)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Separar ministérios em linhas diferentes
    df['Ministérios'] = df['Ministérios'].str.split(',')
    df = df.explode('Ministérios')
    df['Ministérios'] = df['Ministérios'].str.strip()
    
    # Resetar o índice para garantir que não haja índice personalizado
    df.reset_index(drop=True, inplace=True)
    
    # Reordenar as colunas para que "Nome" seja a primeira
    colunas_ordenadas = ['Nome'] + [col for col in df.columns if col != 'Nome']
    df = df[colunas_ordenadas]
    
    return df

df = carregar_dados()

# Listas de perguntas
sim_nao_cols = [
    'Está realizando seu discipulado de forma periódica?',
    'Está movimentando sua Ficha de Oikós?',
    'Ganhou vidas em 2024?',
    'Ganhou vidas em 2023?',
    'Está discipulando novos convertidos/membros de sua célula?',
    'Tem participado das Reuniões de Liderança com o Pr Joel?',
    'Tem participado dos Treinamentos do Trilho do Crescimento?',
    'Tem servido nos Encontros, Eventos de outros Ministérios e cursos da UDF?'
]

porcentagem_cols = [
    'Dízimos praticados em 2024:',
    'Ofertas praticadas em 2024:',
    'Ofertas destinadas a Missões praticadas em 2024:',
    'Dificuldades Financeiras',
    'Satisfação Financeira',
    'Considera correta sua assiduidade nas Celebrações, onde “0” é estar incorreto e “100” é estar correto:',
    'Considera correta sua assiduidade na sua Célula, onde “0” é estar incorreto e “100” é estar correto:',
    'Considera correta sua assiduidade em seu Ministério, onde “0” é estar incorreto e “100” é estar correto:'
]

# Criação das abas
aba_selecionada = st.sidebar.radio("Navegação", ["Geral", "Análise Individual", "Análise com Filtros"])

if aba_selecionada == "Geral":
    st.header("Dados Gerais")
    
    # Cálculos gerais para perguntas de Sim/Não
    st.subheader("Respostas para Perguntas de Sim/Não")
    for pergunta in sim_nao_cols:
        dados = df.groupby(pergunta).agg({
            'Nome': lambda x: list(x),
            pergunta: 'count'
        }).rename(columns={pergunta: 'Quantidade'}).reset_index()
        dados.columns = ['Resposta', 'Membros', 'Quantidade']
        dados['Porcentagem'] = (dados['Quantidade'] / dados['Quantidade'].sum()) * 100
        # Limitar a exibição dos nomes a um máximo de 10 para evitar excesso de informação
        dados['Membros'] = dados['Membros'].apply(lambda x: ', '.join(filter(None, x[:10])) + (' e mais...' if len(x) > 10 else ''))
        st.markdown(f"**{pergunta}**")
        st.write(dados[['Resposta', 'Quantidade', 'Porcentagem']])
        fig = px.pie(dados, values='Quantidade', names='Resposta', title=pergunta, hover_data=['Membros'])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
    
    # Cálculos gerais para perguntas de Porcentagem
    st.subheader("Médias para Perguntas de Porcentagem")
    for pergunta in porcentagem_cols:
        media = df[pergunta].mean()
        st.markdown(f"**{pergunta}:** Média = {media:.2f}")
        dados = df.groupby(pergunta).agg({
            'Nome': lambda x: list(x),
            pergunta: 'count'
        }).rename(columns={pergunta: 'Quantidade'}).reset_index()
        dados.columns = ['Valor', 'Membros', 'Quantidade']
        # Limitar a exibição dos nomes a um máximo de 10 para evitar excesso de informação
        dados['Membros'] = dados['Membros'].apply(lambda x: ', '.join(filter(None, x[:10])) + (' e mais...' if len(x) > 10 else ''))
        fig = px.bar(dados, x='Valor', y='Quantidade', text='Quantidade',
                     labels={'Valor': 'Valor', 'Quantidade': 'Quantidade'},
                     title=f'Distribuição das Respostas para: {pergunta}',
                     hover_data=['Membros'])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")

elif aba_selecionada == "Análise Individual":
    st.header("Análise Individual do Membro")
    nomes = df['Nome'].unique()
    nome_selecionado = st.selectbox("Selecione o Nome do Membro para Análise Individual", options=nomes)
    
    if nome_selecionado:
        dados_membro = df[df['Nome'] == nome_selecionado]
        st.subheader(f"Dados do Membro: {nome_selecionado}")
        
        # Transpor os dados para exibição vertical
        dados_membro_T = dados_membro.drop_duplicates(subset=['Nome']).set_index('Nome').transpose()
        dados_membro_T.columns = ['Resposta']
        
        st.table(dados_membro_T)
    else:
        st.write("Selecione um membro para ver a análise individual.")

elif aba_selecionada == "Análise com Filtros":
    st.header("Análise com Filtros")
    
    # Sidebar para filtros adicionais
    st.sidebar.subheader("Filtros")
    
    # Função para adicionar a opção "Todos" nos filtros
    def opcao_todos(lista_opcoes):
        lista_opcoes = list(lista_opcoes)
        lista_opcoes.insert(0, "Todos")
        return lista_opcoes
    
    # Filtrar por ministério
    ministerios = df['Ministérios'].unique()
    ministerios_opcoes = opcao_todos(ministerios)
    ministerio_selecionado = st.sidebar.multiselect("Selecione o Ministério", options=ministerios_opcoes, default="Todos", key="filtro_ministerio")
    
    # Filtrar por estado civil
    estado_civil_options = df['Estado Civil'].unique()
    estado_civil_opcoes = opcao_todos(estado_civil_options)
    estado_civil_selecionado = st.sidebar.multiselect("Selecione o Estado Civil", options=estado_civil_opcoes, default="Todos", key="filtro_estado_civil")
    
    # Filtrar por relacionamento romântico
    relacionamento_options = df['Em Relacionamento'].unique()
    relacionamento_opcoes = opcao_todos(relacionamento_options)
    relacionamento_selecionado = st.sidebar.multiselect("Em Relacionamento Romântico?", options=relacionamento_opcoes, default="Todos", key="filtro_relacionamento")
    
    # Filtros para perguntas de Sim/Não
    st.sidebar.subheader("Filtros para Perguntas de Sim/Não")
    respostas_sim_nao = {}
    for pergunta in sim_nao_cols:
        opcoes = ['Todos', 'Sim', 'Não']
        resposta = st.sidebar.selectbox(f"{pergunta}", options=opcoes, index=0, key=f"sim_nao_{pergunta}")
        respostas_sim_nao[pergunta] = resposta
    
    # Filtros para perguntas de Porcentagem
    st.sidebar.subheader("Filtros para Perguntas de Porcentagem")
    respostas_porcentagem = {}
    opcoes_porcentagem = [0, 25, 50, 75, 100]
    for pergunta in porcentagem_cols:
        valores = st.sidebar.multiselect(f"{pergunta}", options=opcoes_porcentagem, default=opcoes_porcentagem, key=f"porcentagem_{pergunta}")
        respostas_porcentagem[pergunta] = valores
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if "Todos" not in ministerio_selecionado and ministerio_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Ministérios'].isin(ministerio_selecionado)]
    
    if "Todos" not in estado_civil_selecionado and estado_civil_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Estado Civil'].isin(estado_civil_selecionado)]
    
    if "Todos" not in relacionamento_selecionado and relacionamento_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Em Relacionamento'].isin(relacionamento_selecionado)]
    
    # Aplicar filtros de Sim/Não
    for pergunta, resposta in respostas_sim_nao.items():
        if resposta != "Todos":
            df_filtrado = df_filtrado[df_filtrado[pergunta] == resposta]
    
    # Aplicar filtros de Porcentagem
    for pergunta, valores in respostas_porcentagem.items():
        if valores and valores != opcoes_porcentagem:
            df_filtrado = df_filtrado[df_filtrado[pergunta].isin(valores)]
    
    # Exibir dados filtrados
    st.subheader("Dados Filtrados")
    st.dataframe(df_filtrado)
    
    # Mostrar gráficos para cada pergunta de Sim/Não e Porcentagem
    st.subheader("Gráficos das Respostas")
    pergunta_selecionada = st.selectbox("Selecione a Pergunta", options=sim_nao_cols + porcentagem_cols, key="pergunta_grafico")
    if pergunta_selecionada:
        df_temp = df_filtrado
        if pergunta_selecionada in sim_nao_cols:
            dados = df_temp.groupby(pergunta_selecionada).agg({
                'Nome': lambda x: list(x),
                pergunta_selecionada: 'count'
            }).rename(columns={pergunta_selecionada: 'Quantidade'}).reset_index()
            dados.columns = ['Resposta', 'Membros', 'Quantidade']
            # Limitar a exibição dos nomes a um máximo de 10 para evitar excesso de informação
            dados['Membros'] = dados['Membros'].apply(lambda x: ', '.join(filter(None, x[:10])) + (' e mais...' if len(x) > 10 else ''))
            fig = px.bar(dados, x='Resposta', y='Quantidade', color='Resposta', text='Quantidade',
                         labels={'Resposta': 'Resposta', 'Quantidade': 'Quantidade'},
                         title=f'Respostas para: {pergunta_selecionada}',
                         hover_data=['Membros'])
            st.plotly_chart(fig, use_container_width=True)
        elif pergunta_selecionada in porcentagem_cols:
            dados = df_temp.groupby(pergunta_selecionada).agg({
                'Nome': lambda x: list(x),
                pergunta_selecionada: 'count'
            }).rename(columns={pergunta_selecionada: 'Quantidade'}).reset_index()
            dados.columns = ['Valor', 'Membros', 'Quantidade']
            # Limitar a exibição dos nomes a um máximo de 10 para evitar excesso de informação
            dados['Membros'] = dados['Membros'].apply(lambda x: ', '.join(filter(None, x[:10])) + (' e mais...' if len(x) > 10 else ''))
            fig = px.bar(dados, x='Valor', y='Quantidade', text='Quantidade',
                         labels={'Valor': 'Valor', 'Quantidade': 'Quantidade'},
                         title=f'Distribuição das Respostas para: {pergunta_selecionada}',
                         hover_data=['Membros'])
            st.plotly_chart(fig, use_container_width=True)

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido para auxiliar na verificação da qualidade de vida espiritual e financeira dos membros, bem como identificar melhorias necessárias para os ministérios.")
