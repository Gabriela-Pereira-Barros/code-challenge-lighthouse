from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import Variable
from airflow.utils.dates import days_ago
from datetime import datetime
from airflow.exceptions import AirflowException
import pandas as pd
import os
import io

def load_csvs_to_postgres():
    # Obter a data de execução a partir da variável do Airflow, se não estiver definida, usar a data atual
    execution_date = Variable.get("execution_date", default_var=datetime.now().strftime('%Y-%m-%d'))
    
    # Lista de arquivos CSV e tabelas correspondentes no banco de dados
    files_and_tables = [
        (f'/meltano/csv/order_details-{execution_date}.csv', 'order_details'),
        (f'/meltano/postgres/public-employee_territories-{execution_date}.csv', 'employee_territories'),
        (f'/meltano/postgres/public-orders-{execution_date}.csv', 'orders'),
        (f'/meltano/postgres/public-customers-{execution_date}.csv', 'customers'),
        (f'/meltano/postgres/public-products-{execution_date}.csv', 'products'),
        (f'/meltano/postgres/public-shippers-{execution_date}.csv', 'shippers'),
        (f'/meltano/postgres/public-suppliers-{execution_date}.csv', 'suppliers'),
        (f'/meltano/postgres/public-territories-{execution_date}.csv', 'territories'),
        (f'/meltano/postgres/public-us_states-{execution_date}.csv', 'us_states'),
        (f'/meltano/postgres/public-categories-{execution_date}.csv', 'categories'),
        (f'/meltano/postgres/public-region-{execution_date}.csv', 'region'),
        (f'/meltano/postgres/public-employees-{execution_date}.csv', 'employees')                
    ]
    
    # Conectar ao banco de dados PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_destino')

    for csv_file_path, table_name in files_and_tables:
        if not os.path.exists(csv_file_path):
            # Mensagem de aviso para caso o step 1 não tenha sido bem sucedido
            raise AirflowException("Arquivos para o dia de execução selecionado não encontrados, verificar logs de execução Airflow no Meltano. Obs.: verificar também se existe alguma variável execution_date criada aqui no Airflow.")
        else:
            # Executar comando para limpar a tabela
            truncate_table_sql = f"TRUNCATE TABLE {table_name}"
            pg_hook.run(truncate_table_sql)

            # Carregar dados do CSV para um DataFrame pandas
            df = pd.read_csv(csv_file_path)

            # Converter o DataFrame para um CSV em memória
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, header=False)
            csv_buffer.seek(0)

            # Usar o método copy_expert para inserir os dados no PostgreSQL
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV", csv_buffer)
            conn.commit()

with DAG('csv_to_postgres', 
         schedule_interval = "* * * * 1-5",
         start_date = days_ago(1),
         catchup = False) as dag:

    load_csvs_task = PythonOperator(
        task_id='load_csvs_to_postgres',
        python_callable=load_csvs_to_postgres
    )
