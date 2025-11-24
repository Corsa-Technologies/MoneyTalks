from airflow import DAG
from airflow.decorators import task
from data_engineering.extract_forex import Process_forex
from pandas import DataFrame
from datetime import datetime, timedelta

# ------------------------------------------------------------------------------
# DAG: etl_forex
# Executa mensalmente um fluxo ETL para buscar forexes no Supabase,
# consultar seus preços atuais via API e armazenar um histórico de cotações.
# ------------------------------------------------------------------------------

with DAG(
    dag_id='etl_forex',
    start_date=datetime(2025, 11, 9),
    schedule='@daily',  # Executa uma vez por mês
    catchup=False,
    tags=["forex", "etl"]
) as dag:
    
    # Instância da classe responsável por buscar e inserir dados
    extractor = Process_forex()

    @task
    def get_forex():
        """
        Task 1: Recupera do Supabase a lista de forexes cadastradas.

        Returns:
            dict: Dicionário no formato {id_cripto: "BTC-USDT"}
        """
        forex = extractor.get_forex()
        return forex
    
    @task
    def extrair_dados(forex):
        """
        Task 2: Realiza a extração dos preços das forexes
        usando a API da OKX e insere os valores no Supabase.

        Args:
            forex (dict): Dados retornados pela task get_cripto().

        Returns:
            bool: Indica finalização do processo.
        """
        data = extractor.extract_forex(forex)
        return data

    # Encadeamento das tarefas
    forex = get_forex()
    extrair_dados(forex)
