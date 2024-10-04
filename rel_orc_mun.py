import streamlit as st
import pandas as pd
import altair as alt
import glob
import unicodedata
import re

def normalizar_texto(texto):
    if pd.isnull(texto):
        return ''
    # Remover acentuação
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Remover caracteres especiais
    texto = re.sub(r'[^\w\s]', '', texto)
    # Converter para maiúsculas e remover espaços extras
    texto = texto.upper().strip()
    return texto

def main():
    # Definir o caminho onde estão seus arquivos CSV
    caminho_desp = './Despesas/'  # Coloque './Despesas/' se a pasta Despesas estiver na mesma pasta que o script
    caminho_rec = './Receitas/'

    # Usar glob para encontrar todos os arquivos CSV no caminho
    arquivos_desp = glob.glob(caminho_desp + "*.csv")
    arquivos_rec = glob.glob(caminho_rec + "*.csv")

    # Carregar e concatenar todos os arquivos CSV
    df_desp = pd.concat(
        [pd.read_csv(arquivos, encoding='ISO-8859-1', sep=';', on_bad_lines='skip') for arquivos in arquivos_desp],
        ignore_index=True)

    df_rec = pd.concat(
        [pd.read_csv(arquivos, encoding='ISO-8859-1', sep=';', on_bad_lines='skip') for arquivos in arquivos_rec],
        ignore_index=True)

    # Converter a coluna 'Ano' para string
    df_rec['Ano'] = df_rec['Ano'].astype(str)
    df_desp['Ano'] = df_desp['Ano'].astype(str)

    # Limpar e converter os valores da coluna 'Valor' para numérico
    df_rec['Valor'] = df_rec['Valor'].replace({r'\.': '', r',': '.', r'[^\d\.]': ''}, regex=True)
    df_rec['Valor'] = pd.to_numeric(df_rec['Valor'], errors='coerce')

    df_desp['Valor'] = df_desp['Valor'].replace({r'\.': '', r',': '.', r'[^\d\.]': ''}, regex=True)
    df_desp['Valor'] = pd.to_numeric(df_desp['Valor'], errors='coerce')


    # Normalizar os nomes das contas
    df_rec['Conta_Normalizada'] = df_rec['Conta'].apply(normalizar_texto)
    df_desp['Conta_Normalizada'] = df_desp['Conta'].apply(normalizar_texto)

    # Normalizar outras colunas se necessário
    df_rec['UF'] = df_rec['UF'].str.strip().str.upper()
    df_rec['Instituição'] = df_rec['Instituição'].str.strip().str.upper()

    df_desp['UF'] = df_desp['UF'].str.strip().str.upper()
    df_desp['Instituição'] = df_desp['Instituição'].str.strip().str.upper()


    # Atualizar o nome da conta de referência
    conta_receita_corrente_normalizada = normalizar_texto('RECEITA CORRENTE LÍQUIDA (III) = (I - II)')
    conta_despesa_corrente_normalizada = normalizar_texto('DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)')
    
    # Criar uma barra lateral para a navegação entre as páginas
    page = st.sidebar.selectbox('Escolha a Página', ['Relatório Orçamentário', 'Evolução da Receita','Evolução da Despesa'])

    if page == 'Relatório Orçamentário':
            # Carregar os dados
        df = pd.read_excel('rec_desp_full.xlsx')
        df_2 = pd.read_excel('capag_full.xlsx')

        # Convertendo colunas para string
        df['id_municipio'] = df['id_municipio'].astype(str)
        df['ano'] = df['ano'].astype(str)
        df_2['cod'] = df_2['cod'].astype(str)
        df_2['ano'] = df_2['ano'].astype(str)

        # Título da aplicação
        st.title("Relatório Orçamentário Municipal (2020-23)")

        # Ordenar a lista de estados em ordem alfabética
        estados = sorted(df['uf'].unique())

        # Selectbox para selecionar o estado na barra lateral
        estado_selecionado = st.sidebar.selectbox('Selecione o Estado', estados)

        # Filtrar e ordenar os municípios com base no estado selecionado
        municipios = sorted(df[df['uf'] == estado_selecionado]['municipio'].unique())

        # Selectbox para selecionar o município na barra lateral
        municipio_selecionado = st.sidebar.selectbox('Selecione o Município', municipios)

        # Verificar se um município foi selecionado
        if municipio_selecionado:
            # Filtrar o DataFrame para o município selecionado
            df_filtrado = df[df['municipio'] == municipio_selecionado]
            df_despesas = df[df['municipio'] == municipio_selecionado]

            # Filtrar o DataFrame df_2 para obter a Nota Capag do município selecionado
            df_capag = df_2[df_2['Nome_Município'] == municipio_selecionado]

            # Remover as duas primeiras colunas e ordenar cronologicamente
            df_capag_exibicao = df_capag.drop(columns=['cod']).sort_values(by='ano').reset_index(drop=True)
            
            # Exibir os gráficos somente se houver dados para o município selecionado
            if not df_filtrado.empty and not df_despesas.empty:
                st.sidebar.write(f"Você selecionou o estado {estado_selecionado} e o município {municipio_selecionado}.")
                
                # Gráfico de Receita
                st.write(f'Evolução da composição da Receita Total do município {municipio_selecionado} ({estado_selecionado})')
                
                # Gráfico de barras empilhadas para as receitas correntes, de capital e intraorçamentárias
                barras_receita = alt.Chart(df_filtrado).transform_fold(
                    ['Receita_Corrente', 'Receita_Capital', 'Receita_Intra_Orcamentaria'],
                    as_=['Tipo_Receita', 'Valor']
                ).mark_bar().encode(
                    x=alt.X('ano:O', title='Ano'),
                    y=alt.Y('Valor:Q', title='Valores das Receitas'),
                    color=alt.Color('Tipo_Receita:N', legend=alt.Legend(orient='bottom')),
                    tooltip=[
                        alt.Tooltip('ano:O', title='Ano'), 
                        alt.Tooltip('Tipo_Receita:N', title='Tipo de Receita'), 
                        alt.Tooltip('Valor:Q', title='Valor', format=",.2f", formatType='number')  # Formatação de moeda
                    ]
                )

                # Gráfico de linha para Receita Total
                linha_receita = alt.Chart(df_filtrado).mark_line(color='black', size=2).encode(
                    x=alt.X('ano:O', title='Ano'),
                    y=alt.Y('Receita_Total:Q', title='Receita Total'),
                    tooltip=[
                        alt.Tooltip('ano:O', title='Ano'), 
                        alt.Tooltip('Receita_Total:Q', title='Receita Total', format=",.2f", formatType='number')  # Formatação de moeda
                    ]
                )

                # Combinar ambos os gráficos de receita e definir o uso da largura total
                chart_receita = (barras_receita + linha_receita).properties(
                    width='container',  # Ajusta a largura ao tamanho do container
                    height=400,
                    title="Evolução da Receita Total e Composição das Receitas"
                )

                # Exibir o gráfico de receita
                st.altair_chart(chart_receita, use_container_width=True)
                
                # Fonte de dados
                st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
                st.markdown("---") 

                # Gráfico de Despesa
                st.write(f'Evolução da composição das Despesas do município {municipio_selecionado}')
                
                # Gráfico de barras empilhadas para as despesas correntes, de capital e intraorçamentárias com cores personalizadas
                barras_despesa = alt.Chart(df_despesas).transform_fold(
                    ['Despesa_Corrente', 'Despesa_Capital', 'Despesa_Intra_Orcamentaria'],
                    as_=['Tipo_Despesa', 'Valor']
                ).mark_bar().encode(
                    x=alt.X('ano:O', title='Ano'),
                    y=alt.Y('Valor:Q', title='Valores das Despesas'),
                    color=alt.Color('Tipo_Despesa:N', scale=alt.Scale(range=['#FF6666', '#FFB266', '#FFCC66']), legend=alt.Legend(orient='bottom')),  # Cores personalizadas
                    tooltip=[
                        alt.Tooltip('ano:O', title='Ano'), 
                        alt.Tooltip('Tipo_Despesa:N', title='Tipo de Despesa'), 
                        alt.Tooltip('Valor:Q', title='Valor', format=",.2f", formatType='number')  # Formatação de moeda
                    ]
                )

                # Gráfico de linha para Despesa Total
                linha_despesa = alt.Chart(df_despesas).mark_line(color='red', size=2).encode(
                    x=alt.X('ano:O', title='Ano'),
                    y=alt.Y('Despesa_Total:Q', title='Despesa Total'),
                    tooltip=[
                        alt.Tooltip('ano:O', title='Ano'), 
                        alt.Tooltip('Despesa_Total:Q', title='Despesa Total', format=",.2f", formatType='number')  # Formatação de moeda
                    ]
                )

                # Combinar ambos os gráficos de despesa e definir o uso da largura total
                chart_despesa = (barras_despesa + linha_despesa).properties(
                    width='container',  # Ajusta a largura ao tamanho do container
                    height=400,
                    title="Evolução da Despesa Total e Composição das Despesas"
                )

                # Exibir o gráfico de despesa
                st.altair_chart(chart_despesa, use_container_width=True)

                # Fonte de dados
                st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
                st.markdown("---") 

                # Exibir a tabela da Nota Capag sem as duas primeiras colunas e ordenada
                st.write(f"Tabela com dados da Nota Capag para o município {municipio_selecionado} ({estado_selecionado})")
                st.dataframe(df_capag_exibicao, use_container_width=True)  # Mostrar o DataFrame filtrado e ajustado na tabela

                # Texto explicativo sobre os indicadores e notas CAPAG
                st.write("""
                ### Explicação dos Indicadores e Notas CAPAG
                - **Indicador 1 - Endividamento**: Mede o grau de endividamento do município em relação à sua Receita Corrente Líquida (RCL). Quanto menor o percentual, melhor a condição fiscal do município.
                - **Fórmula**: (Dívida Consolidada Líquida / Receita Corrente Líquida) * 100
                - **Nota A**: Dívida ≤ 60% da RCL
                - **Nota B**: Dívida entre 60% e 120% da RCL
                - **Nota C**: Dívida > 120% da RCL
                
                - **Indicador 2 - Poupança Corrente**: Avalia a capacidade do município de gerar superávit em suas operações correntes. Indica se o município está conseguindo cobrir suas despesas correntes com suas receitas correntes.
                - **Fórmula**: (Receita Corrente Líquida - Despesa Corrente) / Receita Corrente Líquida * 100
                - **Nota A**: Superávit Corrente ≥ 5%
                - **Nota B**: Superávit Corrente entre 0% e 5%
                - **Nota C**: Déficit Corrente
                
                - **Indicador 3 - Liquidez**: Verifica a capacidade do município de pagar suas obrigações de curto prazo.
                - **Nota A**: Liquidez > 100%
                - **Nota B**: Liquidez entre 50% e 100%
                - **Nota C**: Liquidez < 50%
                
                - **Fórmula**: (Disponibilidade de Caixa Bruta / Restos a Pagar Processados) * 100.
                - **Nota A**: Todos os indicadores com Nota A.
                - **Nota B**: Condição mista com indicadores entre A e C.
                - **Nota C**: Qualquer indicador com Nota C.
                
                - **CAPAG (Capacidade de Pagamento)**: Nota consolidada baseada nos três indicadores acima. Avalia a capacidade geral do município de honrar seus compromissos financeiros.
                
                """)

                # Fonte de dados
                st.markdown('<h6>Fonte: <a href="https://www.tesourotransparente.gov.br/temas/estados-e-municipios/capacidade-de-pagamento-capag">Capacidade de Pagamento (CAPAG)</a></h6>',unsafe_allow_html=True)
                st.markdown("---") 

            else:
                st.write("Não há dados disponíveis para o município selecionado.")
        else:
            st.write("Selecione um município para visualizar os gráficos.")

        st.sidebar.markdown("---")
        st.sidebar.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.linkedin.com/in/jonas-manabu-okawara">Jonas Okawara</a></h6>',
        unsafe_allow_html=True,
        )
    
    elif page == 'Evolução da Receita':
        # Página Evolução da Receita
        st.title("Evolução da Receita por Instituição")

        # Seleção de UF, Instituição e Conta
        ufs = sorted(df_rec['UF'].unique())
        uf_selecionada = st.sidebar.selectbox('Selecione a UF', ufs)

        instituicoes = sorted(df_rec[df_rec['UF'] == uf_selecionada]['Instituição'].unique())
        instituicao_selecionada = st.sidebar.selectbox('Selecione a Instituição', instituicoes)

        # Normalizar o nome da instituição selecionada
        instituicao_selecionada_normalizada = normalizar_texto(instituicao_selecionada)

        # Filtrar os dados com base nas seleções de UF e Instituição
        df_filtrado_instituicao = df_rec[
            (df_rec['UF'] == uf_selecionada) &
            (df_rec['Instituição'] == instituicao_selecionada)
        ]

        # Identificar o último ano da série
        ultimo_ano = df_filtrado_instituicao['Ano'].max()

        # Filtrar os dados para o último ano
        df_ultimo_ano = df_filtrado_instituicao[df_filtrado_instituicao['Ano'] == ultimo_ano]

        # Filtrar os dados da receita corrente líquida
        df_receita_corrente_ultimo_ano = df_ultimo_ano[df_ultimo_ano['Conta_Normalizada'] == conta_receita_corrente_normalizada]

        # **Novo**: Obter o valor da população para 2023 a partir da coluna 'População' (ajuste o nome da coluna conforme necessário)
        df_populacao_2023 = df_rec[
            (df_rec['UF'] == uf_selecionada) &
            (df_rec['Instituição'] == instituicao_selecionada) &
            (df_rec['Ano'] == '2023')
        ]

        if 'População' in df_populacao_2023.columns:
            populacao_2023 = df_populacao_2023['População'].values[0]
        else:
            populacao_2023 = None

        if not df_receita_corrente_ultimo_ano.empty:
            receita_corrente_valor = df_receita_corrente_ultimo_ano['Valor'].values[0]

            # Calcular a participação percentual de cada conta no último ano
            df_ultimo_ano['Percentual'] = df_ultimo_ano.apply(
                lambda row: (row['Valor'] / receita_corrente_valor) * 100 if pd.notna(row['Valor']) else None, axis=1)

            # Ordenar as contas por percentual em ordem decrescente
            df_ultimo_ano_ordenado = df_ultimo_ano.sort_values(by='Percentual', ascending=False)

            # Remover as 4 primeiras contas
            df_ultimo_ano_restante = df_ultimo_ano_ordenado.iloc[4:]

            # Exibir o resumo das contas restantes com percentual ordenado
            st.write(f"### Participação percentual na Receita Corrente Líquida ({ultimo_ano}) para {instituicao_selecionada}:")
            
            # Exibir a população de 2023, se disponível
            if populacao_2023:
                st.write(f"População da cidade em 2023: {int(populacao_2023):,} habitantes")

            # Definir quantas colunas por linha (ajuste conforme necessário)
            colunas_por_linha = 3

            # Dividir os dados em blocos de linhas com 3 colunas
            for inicio in range(0, len(df_ultimo_ano_restante), colunas_por_linha):
                cols = st.columns(colunas_por_linha)
                for idx, (i, row) in enumerate(df_ultimo_ano_restante.iloc[inicio:inicio + colunas_por_linha].iterrows()):
                    with cols[idx]:
                        st.metric(label=row['Conta'], value=f"{row['Percentual']:.2f}%")
        else:
            st.write(f"Nenhum dado disponível para 'Receita Corrente Líquida' no ano {ultimo_ano}.")

        # Seleção de Conta
        contas = sorted(df_filtrado_instituicao['Conta'].unique())
        conta_selecionada = st.selectbox('Selecione a Conta', contas)

        # Normalizar o nome da conta selecionada
        conta_selecionada_normalizada = normalizar_texto(conta_selecionada)

        # Filtrar os dados com base nas seleções de conta
        df_filtrado = df_rec[
            (df_rec['UF'] == uf_selecionada) &
            (df_rec['Instituição'] == instituicao_selecionada) &
            (df_rec['Ano'].between('2015', '2023'))
        ]

        # Verificar se os dados foram filtrados corretamente
        #st.write("Dados filtrados após as seleções:")
        #st.write(df_filtrado[['Ano', 'Conta', 'Valor']])

        def calcular_percentual(row, df_filtrado):
            receita_corrente_liquida = df_filtrado[
                (df_filtrado['Conta_Normalizada'] == conta_receita_corrente_normalizada) & 
                (df_filtrado['Ano'] == row['Ano'])
            ]
            if not receita_corrente_liquida.empty:
                valor_receita_corrente = receita_corrente_liquida['Valor'].values[0]
                valor_atual = row['Valor']
                if pd.notna(valor_receita_corrente) and pd.notna(valor_atual):
                    return (valor_atual / valor_receita_corrente) * 100
            return None

        # Aplicar a função para calcular o percentual
        df_filtrado['Percentual_Receita'] = df_filtrado.apply(
            lambda row: calcular_percentual(row, df_filtrado) if row['Conta_Normalizada'] == conta_selecionada_normalizada else None, axis=1
        )

        # Verificar se o percentual foi calculado corretamente
        #st.write("Dados com Percentual Receita calculado:")
        #st.write(df_filtrado[['Ano', 'Conta', 'Valor', 'Percentual_Receita']])

        # Filtrar os dados da conta escolhida ao longo do tempo
        df_evolucao_conta = df_rec[
            (df_rec['UF'] == uf_selecionada) &
            (df_rec['Instituição'] == instituicao_selecionada) &
            (df_rec['Conta_Normalizada'] == conta_selecionada_normalizada) &
            (df_rec['Ano'].between('2015', '2023'))
        ]

        # Gráfico de evolução da conta selecionada ao longo do tempo
        if not df_evolucao_conta.empty:
            st.write(f"Evolução da conta ({conta_selecionada}) ao longo do tempo (2015-2023)")
            chart_conta = alt.Chart(df_evolucao_conta).mark_line().encode(
                x=alt.X('Ano:O', title='Ano'),
                y=alt.Y('Valor:Q', title=f'Valor da {conta_selecionada}'),
                tooltip=[alt.Tooltip('Ano:O', title='Ano'),
                        alt.Tooltip('Valor:Q', title='Valor', format=",.2f")]
            ).properties(width='container', height=400)
            st.altair_chart(chart_conta, use_container_width=True)
        else:
            st.write(f"Não há dados disponíveis para a conta ({conta_selecionada}) entre 2015 e 2023.")
        
        st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
        st.markdown("---")



        # Gráfico de evolução da Receita (em barras)
        if df_filtrado['Percentual_Receita'].notnull().sum() > 0:
            st.write(f"Evolução da Receita ({conta_selecionada}) sobre a Receita Corrente Líquida (2015-2023)")
            chart_receita = alt.Chart(df_filtrado.dropna(subset=['Percentual_Receita'])).mark_bar().encode(
                x=alt.X('Ano:O', title='Ano'),
                y=alt.Y('Percentual_Receita:Q', title=f'Percentual da {conta_selecionada} sobre Receita Corrente Líquida'),
                tooltip=[alt.Tooltip('Ano:O', title='Ano'), 
                        alt.Tooltip('Percentual_Receita:Q', title='Percentual', format=",.2f")]
            ).properties(width='container', height=400)
            st.altair_chart(chart_receita, use_container_width=True)
        else:
            st.write("Nenhum dado disponível para calcular o percentual.")
        
        st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
        st.markdown("---")

        # Tabela com os valores da Conta Selecionada e Receita Corrente Líquida
        st.write("Tabela de valores da Conta Selecionada e Receita Corrente Líquida por Ano:")

        # Filtrar os dados da receita corrente líquida
        df_receita_corrente = df_filtrado[df_filtrado['Conta_Normalizada'] == conta_receita_corrente_normalizada][['Ano', 'Valor']]
        df_receita_corrente = df_receita_corrente.rename(columns={'Valor': 'Receita Corrente Líquida'})

        # Filtrar os dados da conta selecionada
        df_conta_selecionada = df_filtrado[df_filtrado['Conta_Normalizada'] == conta_selecionada_normalizada][['Ano', 'Valor']]
        df_conta_selecionada = df_conta_selecionada.rename(columns={'Valor': f'Valor da {conta_selecionada}'})

        # Mesclar os dados por ano
        df_tabela = pd.merge(df_conta_selecionada, df_receita_corrente, on='Ano', how='left')

        # Exibir a tabela
        st.write(df_tabela)
        
        st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
        st.markdown("---")


        st.sidebar.markdown("---")
        st.sidebar.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.linkedin.com/in/jonas-manabu-okawara">Jonas Okawara</a></h6>',
        unsafe_allow_html=True,
        )

    elif page == 'Evolução da Despesa':
        # Página Evolução da Despesa
        st.title("Evolução da Despesa por Instituição")

        # Seleção de UF, Instituição e Conta
        ufs = sorted(df_desp['UF'].unique())
        uf_selecionada = st.sidebar.selectbox('Selecione a UF', ufs)

        instituicoes = sorted(df_desp[df_desp['UF'] == uf_selecionada]['Instituição'].unique())
        instituicao_selecionada = st.sidebar.selectbox('Selecione a Instituição', instituicoes)

        # Normalizar o nome da instituição selecionada
        instituicao_selecionada_normalizada = normalizar_texto(instituicao_selecionada)

        # Filtrar os dados com base nas seleções de UF e Instituição
        df_filtrado_instituicao = df_desp[
            (df_desp['UF'] == uf_selecionada) &
            (df_desp['Instituição'] == instituicao_selecionada)
        ]

        # Identificar o último ano da série
        ultimo_ano = df_filtrado_instituicao['Ano'].max()

        # Filtrar os dados para o último ano
        df_ultimo_ano = df_filtrado_instituicao[df_filtrado_instituicao['Ano'] == ultimo_ano]

        # Filtrar os dados da despesa corrente líquida (usando o mesmo nome de coluna para a despesa)
        df_despesa_corrente_ultimo_ano = df_ultimo_ano[df_ultimo_ano['Conta_Normalizada'] == conta_despesa_corrente_normalizada]

        # Obter o valor da população para 2023 a partir da coluna 'População'
        df_populacao_2023 = df_desp[
            (df_desp['UF'] == uf_selecionada) &
            (df_desp['Instituição'] == instituicao_selecionada) &
            (df_desp['Ano'] == '2023')
        ]

        if 'População' in df_populacao_2023.columns:
            populacao_2023 = df_populacao_2023['População'].values[0]
        else:
            populacao_2023 = None

        if not df_despesa_corrente_ultimo_ano.empty:
            despesa_corrente_valor = df_despesa_corrente_ultimo_ano['Valor'].values[0]

            # Calcular a participação percentual de cada conta no último ano
            df_ultimo_ano['Percentual'] = df_ultimo_ano.apply(
                lambda row: (row['Valor'] / despesa_corrente_valor) * 100 if pd.notna(row['Valor']) else None, axis=1)

            # Ordenar as contas por percentual em ordem decrescente
            df_ultimo_ano_ordenado = df_ultimo_ano.sort_values(by='Percentual', ascending=False)

            # Remover as 4 primeiras contas
            df_ultimo_ano_restante = df_ultimo_ano_ordenado.iloc[1:]

            # Exibir o resumo das contas restantes com percentual ordenado
            st.write(f"### Participação percentual na Despesa (EXCETO INTRA-ORÇAMENTÁRIAS) ({ultimo_ano}) para {instituicao_selecionada}:")

            # Exibir a população de 2023, se disponível
            if populacao_2023:
                st.write(f"População da cidade em 2023: {int(populacao_2023):,} habitantes")

            # Definir quantas colunas por linha (ajuste conforme necessário)
            colunas_por_linha = 3

            # Dividir os dados em blocos de linhas com 3 colunas
            for inicio in range(0, len(df_ultimo_ano_restante), colunas_por_linha):
                cols = st.columns(colunas_por_linha)
                for idx, (i, row) in enumerate(df_ultimo_ano_restante.iloc[inicio:inicio + colunas_por_linha].iterrows()):
                    with cols[idx]:
                        st.metric(label=row['Conta'], value=f"{row['Percentual']:.2f}%")
        else:
            st.write(f"Nenhum dado disponível para 'Despesa' no ano {ultimo_ano}.")

        # Seleção de Conta
        contas = sorted(df_filtrado_instituicao['Conta'].unique())
        conta_selecionada = st.selectbox('Selecione a Conta', contas)

        # Normalizar o nome da conta selecionada
        conta_selecionada_normalizada = normalizar_texto(conta_selecionada)

        # Filtrar os dados com base nas seleções de conta
        df_filtrado = df_desp[
            (df_desp['UF'] == uf_selecionada) &
            (df_desp['Instituição'] == instituicao_selecionada) &
            (df_desp['Ano'].between('2015', '2023'))
        ]

        # Função para calcular percentual
        def calcular_percentual(row, df_filtrado):
            despesa_corrente_liquida = df_filtrado[
                (df_filtrado['Conta_Normalizada'] == conta_despesa_corrente_normalizada) & 
                (df_filtrado['Ano'] == row['Ano'])
            ]
            if not despesa_corrente_liquida.empty:
                valor_despesa_corrente = despesa_corrente_liquida['Valor'].values[0]
                valor_atual = row['Valor']
                if pd.notna(valor_despesa_corrente) and pd.notna(valor_atual):
                    return (valor_atual / valor_despesa_corrente) * 100
            return None

        # Aplicar a função para calcular o percentual
        df_filtrado['Percentual_Despesa'] = df_filtrado.apply(
            lambda row: calcular_percentual(row, df_filtrado) if row['Conta_Normalizada'] == conta_selecionada_normalizada else None, axis=1
        )

        # Gráfico de evolução da conta selecionada ao longo do tempo
        if not df_filtrado.empty:
            st.write(f"Evolução da conta ({conta_selecionada}) ao longo do tempo (2015-2023)")
            chart_conta = alt.Chart(df_filtrado).mark_line().encode(
                x=alt.X('Ano:O', title='Ano'),
                y=alt.Y('Valor:Q', title=f'Valor da {conta_selecionada}'),
                tooltip=[alt.Tooltip('Ano:O', title='Ano'),
                        alt.Tooltip('Valor:Q', title='Valor', format=",.2f")]
            ).properties(width='container', height=400)
            st.altair_chart(chart_conta, use_container_width=True)
        else:
            st.write(f"Não há dados disponíveis para a conta ({conta_selecionada}) entre 2015 e 2023.")
        
        st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
        st.markdown("---")

        # Gráfico de evolução da Despesa (em barras)
        if df_filtrado['Percentual_Despesa'].notnull().sum() > 0:
            st.write(f"Evolução da Despesa ({conta_selecionada}) sobre a Despesa Corrente Líquida (2015-2023)")
            chart_despesa = alt.Chart(df_filtrado.dropna(subset=['Percentual_Despesa'])).mark_bar().encode(
                x=alt.X('Ano:O', title='Ano'),
                y=alt.Y('Percentual_Despesa:Q', title=f'Percentual da {conta_selecionada} sobre Despesa Corrente Líquida'),
                tooltip=[alt.Tooltip('Ano:O', title='Ano'), 
                        alt.Tooltip('Percentual_Despesa:Q', title='Percentual', format=",.2f")]
            ).properties(width='container', height=400)
            st.altair_chart(chart_despesa, use_container_width=True)
        else:
            st.write("Nenhum dado disponível para calcular o percentual.")
        
        st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
        st.markdown("---")

        # Tabela com os valores da Conta Selecionada e Despesa Corrente Líquida
        st.write("Tabela de valores da Conta Selecionada e Despesa Total por Ano:")

        # Filtrar os dados da despesa corrente líquida
        df_despesa_corrente = df_filtrado[df_filtrado['Conta_Normalizada'] == conta_despesa_corrente_normalizada][['Ano', 'Valor']]
        df_despesa_corrente = df_despesa_corrente.rename(columns={'Valor': 'Despesa Exceto Intra-orçamentárias'})

        # Filtrar os dados da conta selecionada
        df_conta_selecionada = df_filtrado[df_filtrado['Conta_Normalizada'] == conta_selecionada_normalizada][['Ano', 'Valor']]
        df_conta_selecionada = df_conta_selecionada.rename(columns={'Valor': f'Valor da {conta_selecionada}'})

        # Mesclar os dados por ano
        df_tabela = pd.merge(df_conta_selecionada, df_despesa_corrente, on='Ano', how='left')

        # Exibir a tabela
        st.write(df_tabela)
        
        st.markdown('<h6>Fonte: <a href="https://siconfi.tesouro.gov.br/siconfi/index.jsf">Siconfi</a></h6>',unsafe_allow_html=True)
        st.markdown("---")


        st.sidebar.markdown("---")
        st.sidebar.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.linkedin.com/in/jonas-manabu-okawara">Jonas Okawara</a></h6>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()





