import streamlit as st  
import pandas as pd
import altair as alt
import openpyxl

def main():
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
        '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="www.linkedin.com/in/jonas-manabu-okawara">Jonas Okawara</a></h6>',
    unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()




