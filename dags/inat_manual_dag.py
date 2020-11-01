
import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

default_task_arguments = {
    'owner': 'airflow',
    'depends_on_past': True, # Prevents new task being triggered if the previous run of the task has not finished successfully. 
    'start_date': datetime.datetime(2020, 10, 1),
    'email': ['mikkohei13+airflow@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': datetime.timedelta(minutes = 1)
}

dag = DAG(
    'inat_manual',
    catchup = False,
    default_args = default_task_arguments,
    description = 'DAG to manually copy iNaturalist observations.',
    max_active_runs = 1,
    schedule_interval = None # Only manual trigger
)

copyTask = BashOperator(
    task_id = 'inat_manual_copyTask',
    bash_command = 'python3 /opt/airflow/dags/inaturalist/inat.py production manual',
    dag = dag,
)

copyTask
