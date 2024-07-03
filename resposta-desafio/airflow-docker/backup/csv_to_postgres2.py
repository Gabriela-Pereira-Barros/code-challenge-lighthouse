from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.utils.dates import days_ago
from datetime import datetime
import pandas as pd
import os
import io

def load_csv_to_postgres():
    # Obter a data atual no formato 'YYYY-MM-DD'
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Caminho para o arquivo CSV com a data atual
    csv_file_path = f'/meltano/public-categories-{current_date}.csv'
    
    # Conectar ao banco de dados PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_destino')  # Substitua pelo seu postgres_conn_id

     # Executar comando para limpar a tabela
    truncate_table_sql = "TRUNCATE TABLE categories"
    pg_hook.run(truncate_table_sql)

    # Carregar dados do CSV para um DataFrame pandas, ignorando a primeira linha
    df = pd.read_csv(csv_file_path)

    # Converta o DataFrame para um CSV em memória
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, header=False)
    csv_buffer.seek(0)

    # Use o método copy_expert para inserir os dados no PostgreSQL
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    table_name = 'categories'  # Nome da tabela onde você quer inserir os dados
    cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV", csv_buffer)
    conn.commit()

with DAG('csv_to_postgres2', 
         schedule_interval=None,  # Define a frequência de execução da DAG
         start_date=days_ago(1),  # Data de início da execução da DAG
         catchup=False) as dag:

    # Tarefa para carregar dados do CSV para o PostgreSQL
    load_csv_task = PythonOperator(
        task_id='load_csv_to_postgres',
        python_callable=load_csv_to_postgres
    )
