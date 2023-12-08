

Started 29.9.2020, put into production 1.11.2020.

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
   * `&` for no filtering
   * `&captive=true`
   * `&quality_grade=casual`
   * `&user_id=username`
   * `&project_id=105081`
   * `&photo_licensed=true`
   * `&taxon_name=Parus%20major` # only this taxon, not children, use %20 for spaces
   * `&taxon_id=211194` # Tracheophyta; this taxon and children
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

# Preparing private data

* Download private data from https://inaturalist.laji.fi/sites/20
* Unzip the data
* Run script `tools/simplify.py` for the `inaturalist-suomi-20-observations.csv` file
* Place the resulting `latest.tsv` file to `dags/inaturalist/privatedata/latest.tsv` (remove or archive the old datafile(s) in that directory)
* Place `inaturalist-suomi-20-users.csv`
* Double-check that Git doesn't see the files, by running `git status`
* Test by running inat_manual on Airflow, with `&user_id=mikkohei13&geoprivacy=obscured%2Cobscured_private%2Cprivate`
* Update all data by running inat_manual on Airflow, with filters:
   * `inat_MANUAL_production_latest_obsId = 0`
   * `inat_MANUAL_production_latest_update = 2000-01-01T00%3A25%3A15%2B00%3A00`
   * `inat_MANUAL_urlSuffix = &geoprivacy=obscured%2Cobscured_private%2Cprivate`
* Note that this doesn't update all observations with email addresses. Doing that would require updating all observations.

# Todo

### Issues:

- Deletions
- If location of an observation is first set to Finland, then copied to DW, then location is changed on iNaturalist to some other country, changes won't come to DW, since he system only fetches Finnish observations.
    - Solution options: Twice per year, check all occurrences against Finnish data dump. If observation is not found, it's deleted or moved outside Finland -> Delete from DW: Check: data dump should contain all Finnish observations, regardless of user affiliation.
- Does to docker-compose bug, does not gracefully stop, if `restart: always` is set
- https://github.com/docker/compose/pull/9019
- Spaces in date variables will cause fatal error with iNat API -> should strip the string

### For server setup:

- Send email on failure
- Setup proper env values, password-protect webserver ui https://airflow.apache.org/docs/stable/security.html
- Limit DAG refresh time (now ~3 secs)

### Should/Nice to have:

- Fix date created timezone
- iNat: Setup (unit) testing
- Monitor if iNat API changes (test observation)
- Set processor_poll_interval to e.g. 15 secs
- Conversion: annotation key 17 (inatHelpers)
- Conversion: Remove spaces, special chars etc. from fact names, esp. when handling observation fields
- Conversion: See todo's from conversion script


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
- Taxonomy issues. ETL process and annotations can change e.g. taxon, so that the observation cannot be found with the original name
- If observation has first been private or captive, and then changed to public or non-captive, it may not be copied by the regular copy process
