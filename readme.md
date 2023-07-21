

Started 29.9.2020, put into production 1.11.2020.

Based on https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96

# Setup

To set up:

    git clone https://github.com/mikkohei13/airflow.git
    cd airflow
    mkdir logs
    chmod -R 777 logs/
    chmod -R 777 dags/
    chmod -R 777 scripts/
    mkdir dags/inaturalist/privatedata

Set environment variables to `.env` or use default ones.

Note that `AIRFLOW__CORE__FERNET_KEY` and `FERNET_KEY` have to be must be 32 url-safe base64-encoded bytes. These can be generated with `openssl rand -base64 32`

Then:

    docker-compose up; docker-compose down;

Set up api token, latest observation id and update time to Airflow varibales in the Airflow UI (Admin > Variables).

Tokens:

* inat_production_token (for api.laji.fi)
* inat_staging_token (for api)

Set up variables (Admin > Variables):

* inat_auto_production_latest_obsId = 0
* inat_auto_production_latest_update = 2023-02-01T00%3A00%3A00%2B00%3A00 (NOTE: no space allowed at the end of string)
* inat_MANUAL_production_latest_obsId = 0
* inat_MANUAL_production_latest_update = 2023-02-01T00%3A00%3A00%2B00%3A00 
* inat_MANUAL_urlSuffix = &captive=true 

Upload latest.tsv to dags/inaturalist/privatedata, see instructions below.

## Test the setup

To test the DAG in Airflow, enable and trigger it manually. 

To run scripts manually, start with:

    docker exec -ti airflow_webserver bash
    cd dags/inaturalist/

Debug single observation:

    python3 single.py 54911120 dry 

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
   * `&taxon_name=Parus%20major` # only this taxon, not children, use %20 for spaces
   * `&taxon_id=211194` # Tracheophyta; this taxon and children
   * `&quality_grade=casual`
   * `&` for no filtering
   * `&user_id=mikkohei13&geoprivacy=obscured%2Cobscured_private%2Cprivate` # test with obscured  observations
   * `&place_id=165234` # Finland EEZ
   * `&term_id=17&term_value_id=19` # with attribute dead (not necessarily upvoted?)
   * `&field:Host` # Observation field regardless of value
   * `&field:Host%20plant`
   * `&field:Isäntälaji`

Use iNaturalist API documentation to see what kind of parameters you can give: https://api.inaturalist.org/v1/docs/#!/Observations/get_observations

    python3 inat.py staging manual

# How it works

* Airflow has DAG's for automatic and manual updates (http://localhost:8082/admin/)
* inat_auto
   * Airflow runs this every 30 minutes and handles retries of something goes wrong
       * If the DAG ends up in an erroneous state, it will have to be cleared (set as successful manually) before the automatic update can continue
   * Calls `python3 /opt/airflow/dags/inaturalist/inat.py production auto`
   * inat.py
       * Get startup variables from Airflow
       * Loads private data to Pandas dataframe
       * Gets data from iNat and goes through it page-by-page. Uses custom pagination, since iNat pagination does not work past 333 (?) pages.
    * inatToDW.py
       * Converts all observations to DW format
       * Adds private data if it's available, to a privateDocument
    * postDW.py
       * Posts all observations to FinBIF DW as a batch
    * inat.py
       * If success, sets vatiables to Airflow

* inat_manual
    * This can be triggered manually via Airflow, to update e.g. captive records
    * Set preferences under Airflow Admin > Variables
       * url suffix
       * first id (set to 0)
       * start time (change this!)

# Preparing private data (latest.tsv)

Last time done: 12/2022

* Download private data from https://inaturalist.laji.fi/sites/20
* Import data to Excel, from file inaturalist-suomi-20-observations.csv
   * Set File Origin charset as UTF-8
   * Select Transform, and set observed_on field Data type = text
   * Close and load
* Filter so that you have
   * coordinates_obscrued=TRUE
   * place_country_name = Finnish or Åland data
   * private_latitude or private_longitude is not blank
* Remove all columns except
    * id
    * observed_on
    * positional_accuracy
    * private_place_guess
    * private_latitude
    * private_longitude
* Copy-paste the visible observation to another sheet
* Check that there are no semicolons (;) in the data. If there are (in place names), replace them with something else.
* Save that sheet as Unicode text (it will be UTF-16)
* Edit the file with VS Code
   * Check that there are no extra semicolons at the end of the rows. There often are on the *last row* (Pandas wants that all rows have exactly 6 columns)
   * Remove empty rows at the bottom
   * Replace semicolons with tabs
* Save the file as UTF-8
* Change file extension to .tsv
* Place file to dags/inaturalist/privatedata/latest.tsv (remove or archive the old datafile(s) in that directory)
* Double-check that Git does not see the file, by running git status
* Test by running inat_manual on Airflow, without filters and with very recent data
* Update all data by running inat_manual on Airflow, with filters:
   * inat_MANUAL_production_latest_obsId = 0
   * inat_MANUAL_production_latest_update = 2000-01-01T00%3A25%3A15%2B00%3A00
   * inat_MANUAL_urlSuffix = &geoprivacy=obscured%2Cobscured_private%2Cprivate


# Todo

- Issue: If location of an observation is first set to Finlanf, then copied to DW, then location is changed on iNaturalist to some other country, changes won't come to DW, since he system only fetches Finnish observations.
    - Solution options:
        - 1-2 timer per year, check all occurrences against Finnish data dump. If observation is not found, it's deleted or moved outside Finland.
        - Manually fix observations with annotations


- TRY OUT:
  - restart: unless-stopped

- KNOWN ISSUES:
  - Does to docker-compose bug, does not gracefully stop, if `restart: always` is set
    - https://github.com/docker/compose/pull/9019
- Spaces in date variables will cause fatal error with iNat API -> should strip the string

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


# FAQ: Why observation on iNat is not visible on Laji.fi?

- Laji.fi hides non-wild observations by default
- Laji.fi hides observations that have issues, or have been annotated as erroneous
- Laji.fi obscures certain sensitive species, which then cannot be found using all filters
- ETL process and annotations can change e.g. taxon, so that the observation cannot be found with the original name
- If observation has first been private or captive, and then changed to public or non-captive, it may not be copied by the regular copy process


# Reading

https://www.astronomer.io/blog/7-common-errors-to-check-when-debugging-airflow-dag/

