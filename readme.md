

Started 29.9.2020

Based on https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

# Setup

To set up:

  git clone https://github.com/mikkohei13/airflow.git
  chmod -R 777 logs/
  chmod -R 777 dags/
  chmod -R 777 scripts/

Set environment variables to .env.
Note that AIRFLOW__CORE__FERNET_KEY and FERNET_KEY have to be must be 32 url-safe base64-encoded bytes. These can be generated with ´openssl rand -base64 32´ 

Then:

  docker-compose up; docker-compose down;

Set up api token, latest observation id and update time to Varibales. TODO: instructions.

To test the DAG in Airflow, enable and trigger it manually. 

To run scripts manually, start with:

  docker exec -ti airflow_webserver bash
  cd dags/inaturalist/

Debug single observations:

  python3 single.py 60063865 dry 

Get updated observations and post to DW:

  python3 inat.py


# Todo

iNat
- Monitor if iNat API changes (test observation)
- CONVERSIONS:
  - test if date begin is missing
  - select production/dev coll ... how?
  - LATER: annotation key 17 (inatHelpers)
  - ASK: Remove spaces, special chars etc. from fact names, esp. when handling observation fields
  - See TODO's from conversion script
- ASK: Why dev.laji.fi does not seem to update all observations? (Slack with Esko)
- Setup delete command
- Setup (unit) testing
- Docker-compose with image version numbers?
- Setup email notifications
- Store original observations from inat, where?
- Setup proper env values, password-protect webserver ui
- Show to colleagues, get feedback

- Setup Python IDE


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

