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
thisUpdateTime = thisUpdateTime.replace(":", "%3A")
thisUpdateTime = thisUpdateTime.replace("+", "%2B")

# Get latest update data from Airflow variables
if "staging" == target:
  af_latest_obsId = Variable.get("inat_staging_latest_obsId")
  af_latest_update = Variable.get("inat_staging_latest_update")
elif "production" == target:
  af_latest_obsId = Variable.get("inat_production_latest_obsId")
  af_latest_update = Variable.get("inat_production_latest_update")

#af_latest_obsId = 60063865 # debug


# GET

page = 1

props = { "sleepSeconds": 5, "perPage": 100, "pageLimit": 1000 } # Prod
props = { "sleepSeconds": 2, "perPage": 100, "pageLimit": 10 } # Debug


# For each pageful of data
for multiObservationDict in getInat.getUpdatedGenerator(af_latest_obsId, af_latest_update, **props):
  print("Page: " + str(page)) # debug
#  print(multiObservationDict)

  # If no more observations on page, finish the process by saving update time and resetting observation id to zero.
  if False == multiObservationDict:
    print("Finishing, setting latest update to " + thisUpdateTime)
    if "staging" == target:
      Variable.set("inat_staging_latest_update", thisUpdateTime)
      Variable.set("inat_staging_latest_obsId", 0)
    elif "production" == target:
      Variable.set("inat_production_latest_update", thisUpdateTime)
      Variable.set("inat_production_latest_obsId", 0)
    break

  # CONVERT
  dwObservations, latestObsId = inatToDw.convertObservations(multiObservationDict['results'])

  # POST
  # TODO: set production vs staging
  postSuccess = postDw.postMulti(dwObservations, target)

  # If this pageful contained data, and was saved successfully to DW, set latestObsId as variable
  if postSuccess:
    if "staging" == target:
      Variable.set("inat_staging_latest_obsId", latestObsId)
    elif "production" == target:
      Variable.set("inat_production_latest_obsId", latestObsId)

  if page < props["pageLimit"]:
    page = page + 1
  else:
    # Exception because this should not happen in production (happens only if pageLimit is too low compared to frequency of this script being run)
    raise Exception("Page limit " + str(props["pageLimit"]) + " reached.")



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
