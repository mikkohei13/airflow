

Started 29.9.2020

Based on https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

# Setup

  git clone https://github.com/mikkohei13/airflow.git
  chmod -R 777 logs/
  chmod -R 777 dags/
  chmod -R 777 scripts/

Set environment variables to .env.
Note that AIRFLOW__CORE__FERNET_KEY and FERNET_KEY have to be must be 32 url-safe base64-encoded bytes. These can be generated with ´openssl rand -base64 32´ 

  docker-compose up; docker-compose down;


# Todo

- Rewrite minimal conversion with python
- Push to staging dw, with token hidden from Git
- Setup Python IDE
- Setup (unit) testing
- Setup email notifications
- Rewrite all conversions with python (add: no accuracy when coarse location)
- Setup proper env values, password-protect webserver ui
- Show to colleagues, get feedback


# Testing

Basic test

  docker exec -ti airflow_webserver bash
  python3 dags/dummy_dag.py

Print the list of active DAGs

  airflow list_dags

Prints the list of tasks the "tutorial" dag_id

  airflow list_tasks tutorial

Prints the hierarchy of tasks in the tutorial DAG

  airflow list_tasks tutorial --tree

???

  airflow test inaturalist inaturalist_copy 2020-10-02

