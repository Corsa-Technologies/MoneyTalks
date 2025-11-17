from airflow import DAG
from airflow.decorators import task
from data_engineering.extract_cripto import Extract_data
from pandas import DataFrame
from datetime import datetime, timedelta

# ------------------------------------------------------------------------------
# DAG: etl_currency
# Executa mensalmente um fluxo ETL para buscar criptomoedas no Supabase,
# consultar seus preços atuais via API e armazenar um histórico de cotações.
# ------------------------------------------------------------------------------

with DAG(
    dag_id='etl_currency',
    start_date=datetime(2025, 11, 9),
    schedule='@monthly',  # Executa uma vez por mês
    catchup=False,
    tags=["crypto", "etl"]
) as dag:
    
    # Instância da classe responsável por buscar e inserir dados
    extractor = Extract_data()

    @task
    def get_cripto():
        """
        Task 1: Recupera do Supabase a lista de criptomoedas cadastradas.

        Returns:
            dict: Dicionário no formato {id_cripto: "BTC-USDT"}
        """
        criptos = extractor.get_criptos()
        return criptos
    
    @task
    def extrair_dados(criptos):
        """
        Task 2: Realiza a extração dos preços das criptomoedas
        usando a API da OKX e insere os valores no Supabase.

        Args:
            criptos (dict): Dados retornados pela task get_cripto().

        Returns:
            bool: Indica finalização do processo.
        """
        data = extractor.extract_cripto(criptos)
        return data

    # Encadeamento das tarefas
    criptos = get_cripto()
    extrair_dados(criptos)
