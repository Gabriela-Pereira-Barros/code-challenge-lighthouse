from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

with DAG(
    dag_id='csv_to_csv',
    schedule_interval="* * * * 1-5",
    start_date=datetime(2023, 4, 1),
    catchup=False,
) as dag:

    run_meltano_task = BashOperator(
        task_id='run_meltano_task',
        bash_command='meltano run tap-csv target-csv',
    )