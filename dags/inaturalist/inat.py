import json
import requests
import datetime
import sys
import time

from airflow.models import Variable

import getInat
import inatToDw
import postDw

import pandas

#import pathlib
#import os


# Temp helper
def printObject(object):
  print(object.__dict__)

# TODO: This is not used yet. Use or remove?
def getAirflowVariable(variableName):
  """Gets an Airflow variable and removes leading & trailing whitespace, so that it user has included these in error, they won't affect the scripts.

  Args:
    variableName (string): Name of the Airflow variable to get.

  Returns:
    Variable with leading and trailing whitespace removed.
  """
  variable = Variable.get(variableName)
  return variable.strip()


def setAirflowVariable(variable, value):
  """Sets an Airflow variable. If setting fails, waits and tries again. If fails, exits with exception.

  Args:
    variable (string): Name of the variable to be set.
    value (string): Value to be set.

  Raises:
    Exception: Setting fails after multiple tries.

  Returns:
    Nothing.
  """

  maxRetries = 3
  sleepSeconds = 3

  for _ in range(maxRetries):
    try:
      Variable.set(variable, value)
    except:
      print("Setting " + variable + " failed, sleeping " + sleepSeconds + " seconds")
      time.sleep(sleepSeconds)
      continue
    else: # On success
      break
  else:
    raise Exception("Setting " + variable + " failed after " + maxRetries + " retries")


### SETUP

#print(pathlib.Path(__file__).parent.resolve()) # /opt/airflow/dags/inaturalist
#exit("DONE")

#cwd = os.getcwd()
#print(cwd) # /tmp/airflowtmpa_qykltg
#exit("CWD DONE")


target = sys.argv[1] # staging | production
mode = sys.argv[2] # auto | manual

# Load private data
# TODO: can we avoid root paths, to be able to run this from command line also?
privateObservationData = pandas.read_csv("/opt/airflow/dags/inaturalist/privatedata/latest.tsv", sep='\t') 

"""
TODO:
- Select variables based on auto vs. manual
- When manual, get url suffix from variables, and set it on props

"""

print("------------------------------------------------") 
print("Starting inat.py, target " + target) 

# This will be the new updatedLast time in Variables. Generating update time here, since observations are coming from the API sorted by id, not by datemodified -> cannot use time of last record
now = datetime.datetime.now()
thisUpdateTime = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
thisUpdateTime = thisUpdateTime.replace(":", "%3A")
thisUpdateTime = thisUpdateTime.replace("+", "%2B")

# Get latest update data from Airflow variables
if "auto" == mode:
  urlSuffix = ""
  if "staging" == target:
    variableName_latest_obsId = "inat_auto_staging_latest_obsId"
    variableName_latest_update = "inat_auto_staging_latest_update"
  elif "production" == target:
    variableName_latest_obsId = "inat_auto_production_latest_obsId"
    variableName_latest_update = "inat_auto_production_latest_update"
if "manual" == mode:
  urlSuffix = Variable.get("inat_MANUAL_urlSuffix")
  if "staging" == target:
    variableName_latest_obsId = "inat_MANUAL_staging_latest_obsId"
    variableName_latest_update = "inat_MANUAL_staging_latest_update"
  elif "production" == target:
    variableName_latest_obsId = "inat_MANUAL_production_latest_obsId"
    variableName_latest_update = "inat_MANUAL_production_latest_update"


AirflowLatestObsId = Variable.get(variableName_latest_obsId)
AirflowLatestUpdate = Variable.get(variableName_latest_update)


# GET

page = 1

props = { "sleepSeconds": 10, "perPage": 100, "pageLimit": 10000, "urlSuffix": urlSuffix } # Prod
#props = { "sleepSeconds": 2, "perPage": 10, "pageLimit": 100, "urlSuffix": urlSuffix } # Debug


# For each pageful of data
for multiObservationDict in getInat.getUpdatedGenerator(AirflowLatestObsId, AirflowLatestUpdate, **props):

  # If no more observations on page, finish the process by saving update time and resetting observation id to zero.
  if False == multiObservationDict:
    print("Finishing, setting latest update to " + thisUpdateTime)
    setAirflowVariable(variableName_latest_update, thisUpdateTime)
    setAirflowVariable(variableName_latest_obsId, 0)
    break

  # CONVERT
  dwObservations, latestObsId = inatToDw.convertObservations(multiObservationDict['results'], privateObservationData)

  # POST
  # TODO: set production vs staging
  postSuccess = postDw.postMulti(dwObservations, target)

  # If this pageful contained data, and was saved successfully to DW, set latestObsId as variable
  if postSuccess:
    setAirflowVariable(variableName_latest_obsId, latestObsId)

  if page < props["pageLimit"]:
    page = page + 1
  else:
    # Exception because this should not happen in production (happens only if pageLimit is too low compared to frequency of this script being run)
    raise Exception("Page limit " + str(props["pageLimit"]) + " reached, this means that either page limit is set for debugging, or value is too low for production.")


print("End") 
print("------------------------------------------------") 

