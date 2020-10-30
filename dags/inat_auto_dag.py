
import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
#from airflow.utils.dates import days_ago

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_task_arguments = {
    'owner': 'airflow',
    'depends_on_past': True, # Prevents new task being triggered if the previous schedule for the 
    'start_date': datetime.datetime(2020, 10, 1),
    'email': ['mikkohei13+airflow@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': datetime.timedelta(minutes = 2),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': datetime.timedelta(hours=2),
    # 'execution_timeout': datetime.timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

# TODO: WARNING - schedule_interval is used for <Task(BashOperator): inaturalist_copy>, though it has been deprecated as a task parameter, you need to specify it as a DAG parameter instead



dag = DAG(
    'inat_auto',
    catchup = False, # Since the script handles its own catchup
    default_args = default_task_arguments,
    description = 'DAG to iNaturalist observations automatically in sync.',
    max_active_runs = 1, # Prevent overlapping runs, which would use same variables. TEST
    schedule_interval = datetime.timedelta(minutes = 10)
)

#def print_context(ds, **kwargs):
#    pprint(kwargs)
#    print(ds)
#    return 'Hoi iNat!'

copyTask = BashOperator(
    task_id = 'inat_auto_copyTask',
#    provide_context=True,
#    depends_on_past = True,
#    bash_command=templated_command,
#    python_callable=print_context, # python operator
    bash_command = 'python3 /opt/airflow/dags/inaturalist/inat.py staging auto', # On Docker, you need to refer with absolute path
#    params={'my_param': 'Parameter I passed in'},
    dag = dag,
)

copyTask
