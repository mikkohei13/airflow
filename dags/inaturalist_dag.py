
from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1), # Todo: now, and once per hour thereafter
    'email': ['outo+airflow@biomi.org'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

dag = DAG(
    'inaturalist',
    default_args=default_args,
    description='DAG to copy iNaturalist observations',
    schedule_interval=timedelta(days=1),
)

def print_context(ds, **kwargs):
#    pprint(kwargs)
#    print(ds)
    return 'Hoi iNat!'

copyTask = BashOperator(
    task_id='inaturalist_copy',
#    provide_context=True,
#    depends_on_past=False,
#    bash_command=templated_command,
#    python_callable=print_context, # python operator
    bash_command='python3 /opt/airflow/dags/inaturalist/inat.py', # On Docker, you need to refer with absolute path
    params={'my_param': 'Parameter I passed in'},
    dag=dag,
)

copyTask
