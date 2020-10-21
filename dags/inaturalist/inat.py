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
  af_latest_obsId = Variable.get("inat_staging_latest_obsId")
  af_latest_update = Variable.get("inat_staging_latest_update")
elif "production" == target:
  af_latest_obsId = Variable.get("inat_production_latest_obsId")
  af_latest_update = Variable.get("inat_production_latest_update")

#af_latest_obsId = 60063865 # debug


# GET

page = 1
pageLimit = 5

# For each pageful of data
for multiObservationDict in getInat.getUpdatedGenerator(af_latest_obsId, af_latest_update):
  print("Page: " + str(page)) # debug
#  print(multiObservationDict)

  # If no observations on page, don't convert & post
  if False == multiObservationDict:
    break;

  # CONVERT
  dwObservations, latestObsId = inatToDw.convertObservations(multiObservationDict['results'])

#  print(dwObservations)
#  exit()


  # POST
  # TODO: set production vs staging
  postSuccess = postDw.postMulti(dwObservations, target)

  # If this pageful contained data, and was saved successfully to DW, set latestObsId as variable
  if postSuccess:
    if "staging" == target:
      Variable.set("inat_staging_latest_obsId", latestObsId)
#      Variable.set("inat_staging_latest_update", thisUpdateTime)
    elif "production" == target:
      Variable.set("inat_production_latest_obsId", latestObsId)
#      Variable.set("inat_production_latest_update", thisUpdateTime)

  if page < pageLimit:
    page = page + 1
  else:
    print("Page limit " + str(pageLimit) + " reached")
    break



# If whole process was successful
if "staging" == target:
  Variable.set("inat_staging_latest_update", thisUpdateTime)
elif "production" == target:
  Variable.set("inat_production_latest_update", thisUpdateTime)


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
