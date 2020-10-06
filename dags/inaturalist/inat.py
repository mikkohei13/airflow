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


# GET

inat = getInat.getInat()

i = 0 # debug

for multiObservationDict in inat.getUpdatedGenerator(airflowVariable_inat_latest_obs_id, airflowVariable_inat_latest_update):
  print("")
  print("i: " + str(i)) # debug
#  print(multiObservationDict)

  # CONVERT
  for nro, inatObs in enumerate(multiObservationDict['results']): 
    dwObs = inatToDw.convertObservation(inatObs)
    print("---" + str(nro) + "--------------------------------------------------")
    print(dwObs)

  

  # POST

  # If all successful:
  # lastUpdateKey = # get from result
  lastObservationDict = multiObservationDict['results'][-1]
  lastUpdateKey = lastObservationDict["id"]
  print("lastUpdateKey: " + str(lastUpdateKey))

  # set lastUpdateKey as variable
# UNCOMMENT THIS TO USE VARS
#  Variable.set("inat_latest_obs_id", lastUpdateKey)

#  print(multiObservationDict)


# If whole for was successful
# UNCOMMENT THIS TO USE VARS
Variable.set("inat_latest_update", thisUpdateTime)


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

#dw = postDw.postDw()

#dataJson = json.dumps(data)
#print(dataJson)

#dw.postSingleMock(dwObservationJson)

# extracting data in json format 
#data = req.json() 
#print(data)

print("Script ended")
