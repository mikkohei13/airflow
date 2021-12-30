

Started 29.9.2020, put into production 1.11.2020.

Based on https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

# Setup

To set up:

    git clone https://github.com/mikkohei13/airflow.git
    chmod -R 777 logs/
    chmod -R 777 dags/
    chmod -R 777 scripts/

Set environment variables to `.env` or use default ones.

Note that `AIRFLOW__CORE__FERNET_KEY` and `FERNET_KEY` have to be must be 32 url-safe base64-encoded bytes. These can be generated with `openssl rand -base64 32`

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

    python3 single.py 71954693 dry 

Get updated observations and post to DW. Replace `staging` with `production` in order to push into production. This depends on variables in Airflow:

* inat_auto_staging_latest_obsId (e.g. `0`)
* inat_auto_staging_latest_update (e.g. `2020-10-31T19%3A16%3A43%2B00%3A00`)

    python3 inat.py staging auto

Get updated observations and post to DW. This also depends on variables on Airflow, including urlSuffix, which can be used to filter observations from iNat API:

* inat_MANUAL_production_latest_obsId
* inat_MANUAL_production_latest_update
* inat_MANUAL_urlSuffix
* Example suffixes:
   * `&captive=true`
   * `&quality_grade=casual`
   * `&user_id=username`
   * `&project_id=105081`
   * `&photo_licensed=true`
   * `&taxon_name=Monotropa` # only this taxon, not children
   * `&taxon_id=211194` # Tracheophyta; this taxon and children
   * `&quality_grade=casual`
   * `&` for no filtering

Use iNaturalist API documentation to see what kind of parameters you can give: https://api.inaturalist.org/v1/docs/#!/Observations/get_observations

    python3 inat.py staging manual



# Todo

- KNOWN ISSUES:
  - Does to docker-compose bug, does not gracefully stop, if `restart: always` is set
    - https://github.com/docker/compose/pull/9019

- MUST FOR PRODUCTION:
  - Test with own observation that API response stays the same 
  - Send email on failure
  - Setup proper env values, password-protect webserver ui https://airflow.apache.org/docs/stable/security.html
  - Limit DAG refresh time (now ~3 secs)
  - Log cleanup https://github.com/teamclairvoyant/airflow-maintenance-dags/tree/master/log-cleanup
  - Fix date created timezone

- SHOULD:
  - Log level setup https://github.com/apache/airflow/pull/2191
  - iNat: Setup delete command
  - iNat: Setup (unit) testing
  - Monitor if iNat API changes (test observation)
  - Setup & test email notifications

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


# Why observation on iNat is not visible on Laji.fi?

- Laji.fi hides non-wild observations by default
- Laji.fi hides observations that have issues, or have been annotated as erroneous
- Laji.fi obscures certain sensitive species, which then cannot be found using all filters
- ETL process and annotations can cange e.g. taxon, so that the observation cannot be found with the original name
- If observation has first been private, and then changed to public, it may not be copied by the regular copy process


# Reading

https://www.astronomer.io/blog/7-common-errors-to-check-when-debugging-airflow-dag/

