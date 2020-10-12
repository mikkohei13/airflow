import json
import requests
import datetime
import sys

from airflow.models import Variable

import getInat
import inatToDw
import postDw


# Temp helper
def printObject(object):
  print(object.__dict__)



### SETUP

print("Start") 


#TODO: Args for production vs staging
target = "staging" # production | staging

# This will be the new updatedLast time in Variables. Generating update time here, since observations are coming from the API sorted by id, not by datemodified -> cannot use time of last record
now = datetime.datetime.now()
thisUpdateTime = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")

# Get latest update data from Airflow variables
if "staging" == target:
  airflowVariable_inat_latest_obs_id = Variable.get("inat_staging_latest_obs_id")
elif "production" == target:
  airflowVariable_inat_latest_update = Variable.get("inat_production_latest_update")

#airflowVariable_inat_latest_obs_id = 60063865 # debug


# GET

i = 0 # debug

# TODO: refactor name to "latestObsId"
lastUpdateKey = 0 # Just in case, should be returned with conversion function. TODO: remove this loc

# For each pageful of data
for multiObservationDict in getInat.getUpdatedGenerator(airflowVariable_inat_latest_obs_id, airflowVariable_inat_latest_update):
  print("")
  print("i: " + str(i)) # debug
#  print(multiObservationDict)

  # If no observations on page, don't convert & post
  if False == multiObservationDict:
    break;

  # CONVERT
  dwObservation, lastUpdateKey = inatToDw.convertObservations(multiObservationDict['results'])

  print(dwObservations)


  # POST
  # TODO: set production vs staging
  postSuccess = postDw.postMultiMock(dwObservations, target)

  # If this pageful contained data, and was saved successfully to DW, set lastUpdateKey as variable
  if postSuccess:
    if "staging" == target:
      Variable.set("inat_staging_latest_obs_id", lastUpdateKey)
      Variable.set("inat_staging_latest_update", thisUpdateTime)
    elif "production" == target:
      Variable.set("inat_production_latest_obs_id", lastUpdateKey)
      Variable.set("inat_staging_latest_update", thisUpdateTime)
      


# If whole process was successful
#Variable.set("inat_latest_update", thisUpdateTime) # UNCOMMENT THIS TO USE VARS


# TODO: This will be used for debugging -> not needed in DAG, only on CLI
#singleObservationDict = inat.getSingle(airflowVariable_inat_latest_obs_id)


# -----------------------------------------------------------
# OLDs
# -----------------------------------------------------------

### CONVERT

#print(singleObservationDict)

#dwObservationDict = inatToDw.convertObservation(singleObservationDict)
#print(dwObservationDict)

#dwObservationJson = json.dumps(dwObservationDict)

#pprint(inatResponse)


### POST



#dataJson = json.dumps(data)
#print(dataJson)

#dw.postSingleMock(dwObservationJson)

# extracting data in json format 
#data = req.json() 
#print(data)

print("Script ended")
