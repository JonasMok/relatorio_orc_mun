# relatorio_orc_mun
# Relatório Orçamentário Municipal (2020-23)

Este projeto é uma aplicação desenvolvida em Python utilizando a biblioteca [Streamlit](https://streamlit.io/) para visualização e análise de dados orçamentários municipais do Brasil no período de 2020 a 2023. A aplicação permite aos usuários selecionar um município específico e visualizar gráficos de receitas e despesas, bem como uma tabela detalhada dos indicadores de capacidade de pagamento (CAPAG) e suas respectivas notas.

## Funcionalidades

- Seleção de Estado e Município para visualização de dados.
- Gráficos interativos de:
  - Receita Total e Composição das Receitas (Receitas Correntes, de Capital e Intraorçamentárias).
  - Despesa Total e Composição das Despesas (Despesas Correntes, de Capital e Intraorçamentárias).
- Tabela com dados dos indicadores CAPAG, explicações sobre o cálculo e critérios para cada nota.

## Indicadores CAPAG

Os indicadores CAPAG (Capacidade de Pagamento) são usados para avaliar a saúde fiscal dos municípios. Eles são compostos por:

1. **Endividamento**: Mede o nível de endividamento em relação à Receita Corrente Líquida.
2. **Poupança Corrente**: Avalia a capacidade do município de gerar superávit em suas operações correntes.
3. **Liquidez**: Verifica a capacidade do município de pagar suas obrigações de curto prazo.

As notas CAPAG variam de **A** (excelente condição fiscal) a **C** (alta fragilidade fiscal), dependendo do desempenho do município em cada um dos indicadores.

## Tecnologias Utilizadas

- **Python 3.x**
- **Pandas**: Para manipulação de dados.
- **Altair**: Para visualização de gráficos.
- **Streamlit**: Para a construção da interface web interativa.
- **Openpyxl**: Para leitura de arquivos Excel.

## Como Executar

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado em sua máquina. Você também precisará instalar as dependências listadas no arquivo `requirements.txt`.

### Instalação

1. Clone o repositório para sua máquina local:

    ```bash
    git clone https://github.com/seu-usuario/nome-do-repositorio.git
    cd nome-do-repositorio
    ```

2. Crie um ambiente virtual e ative-o:

    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No Linux/Mac
    source venv/bin/activate
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

### Executando a Aplicação

1. Para iniciar a aplicação Streamlit, execute:

    ```bash
    streamlit run nome_do_arquivo.py
    ```

   Substitua `nome_do_arquivo.py` pelo nome do arquivo Python onde o código da aplicação está localizado.

2. Acesse o endereço local fornecido pelo Streamlit (normalmente `http://localhost:8501`) em seu navegador web.

## Estrutura do Projeto

- **data/**: Diretório contendo os arquivos de dados em formato Excel:
  - `rec_desp_full.xlsx`: Contém os dados de receitas e despesas municipais.
  - `capag_full.xlsx`: Contém os dados dos indicadores CAPAG para avaliação fiscal dos municípios.

- **app/**: Diretório contendo o código principal da aplicação:
  - `main.py`: Script Python que implementa a aplicação Streamlit para visualização dos dados orçamentários e fiscais.

- **requirements.txt**: Arquivo de texto listando todas as dependências Python que precisam ser instaladas para executar a aplicação.

- **README.md**: Este arquivo, que fornece uma visão geral do projeto, instruções de instalação, uso e contribuição.

- **LICENSE**: Arquivo de licença especificando os termos sob os quais o código do projeto pode ser utilizado, modificado e distribuído.


## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## Licença

Este projeto está sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

Para mais informações, entre em contato com [jonas.ok@gmail.com](mailto:jonas.ok@gmail.com).
