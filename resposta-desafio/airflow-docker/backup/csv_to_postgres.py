from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.utils.dates import days_ago
import pandas as pd
import os

def load_csv_to_postgres():
    # Caminho para o arquivo CSV
    csv_file_path = '/meltano/public-categories-2024-07-03.csv'

    # Conectar ao banco de dados PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_destino')  # Substitua pelo seu postgres_conn_id

    # Carregar dados do CSV para um DataFrame pandas
    df = pd.read_csv(csv_file_path, skiprows=1)

    # Inserir os dados no banco de dados PostgreSQL
    table_name = 'categories'  # Nome da tabela onde você quer inserir os dados
    pg_hook.insert_rows(table_name, df.to_dict('records'))

with DAG('csv_to_postgres', 
         schedule_interval=None,  # Define a frequência de execução da DAG
         start_date=days_ago(1),  # Data de início da execução da DAG
         catchup=False) as dag:

    # Tarefa para carregar dados do CSV para o PostgreSQL
    load_csv_task = PythonOperator(
        task_id='load_csv_to_postgres',
        python_callable=load_csv_to_postgres
    )

