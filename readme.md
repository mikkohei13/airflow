

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

Set up api token, latest observation id and update time to Airflow varibales in the Airflow UI (Admin > Variables).

Tokens:

* inat_production_token (for api.laji.fi)
* inat_staging_token (for api)

To test the DAG in Airflow, enable and trigger it manually. 

To run scripts manually, start with:

    docker exec -ti airflow_webserver bash
    cd dags/inaturalist/

Debug single observation:

    python3 single.py 60063865 dry 

Get updated observations and post to DW. Replace `staging` with `production` in order to push into production. This depends on variables in Airflow:

* inat_auto_staging_latest_obsId (e.g. `0`)
* inat_auto_staging_latest_update (e.g. `2020-10-31T19%3A16%3A43%2B00%3A00`)

    python3 inat.py staging auto

Get updated observations and post to DW. This also depends on variables on Airflow, including urlSuffix, which can be used to filter observations from iNat API:

* inat_MANUAL_production_latest_obsId
* inat_MANUAL_production_latest_update
* inat_MANUAL_urlSuffix (e.g. `&captive=true` or `&` for no filtering)

    python3 inat.py staging manual



# Todo

- MUST:
  - Docker-compose with image version numbers?
  - Setup & test email notifications
- Setup proper env values, password-protect webserver ui
- SHOULD:
  - iNat: Setup delete command
  - iNat: Setup (unit) testing
  - Monitor if iNat API changes (test observation)
- NICE:
  - Set processor_poll_interval to e.g. 15 secs
  - Conversion: annotation key 17 (inatHelpers)
  - Conversion: Remove spaces, special chars etc. from fact names, esp. when handling observation fields
  - Conversion: See todo's from conversion script
  - Store original observations from inat, where?
- ASK: Why dev.laji.fi does not seem to update all observations? (Slack with Esko)

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

