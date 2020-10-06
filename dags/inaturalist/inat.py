import json
import requests
import datetime

from airflow.models import Variable

import getInat
import inatToDw
import postDw


# Temp helper
def printObject(object):
  print(object.__dict__)



### SETUP

print("Start") 

# This will be the new updatedLast time in Variables. Generating update time here, since observations are coming from the API sorted by id, not by datemodified -> cannot use time of last record
now = datetime.datetime.now()
thisUpdateTime = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")

# Puolukkapiiloyökkönen 60063865
airflowVariable_inat_latest_obs_id = Variable.get("inat_latest_obs_id")
airflowVariable_inat_latest_update = Variable.get("inat_latest_update")

airflowVariable_inat_latest_obs_id = 60063865 # debug

# GET

inat = getInat.getInat()
postDw = postDw.postDw()

i = 0 # debug

lastUpdateKey = 0 # Just in case, should be returned with conversion function

# For each pageful of data
for multiObservationDict in inat.getUpdatedGenerator(airflowVariable_inat_latest_obs_id, airflowVariable_inat_latest_update):
  print("")
  print("i: " + str(i)) # debug
#  print(multiObservationDict)

  # If no observations on page, don't convert & post
  if False == multiObservationDict:
    break;

  # CONVERT
  dwObservations = inatToDw.convertObservations(multiObservationDict['results'])

  print(dwObservations)

  # POST
  # ABBA: single obs -> multi obs
#  postDw.postSingleMock(dwObs)

  # TODO: return last successfully posted id, when dw api returns 200


  # If this pageful contained data, and was saved successfully to DW, set lastUpdateKey as variable
  if lastUpdateKey > 0:
    print("lastUpdateKey: " + str(lastUpdateKey))
#   Variable.set("inat_latest_obs_id", lastUpdateKey) # UNCOMMENT THIS TO USE VARS



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
