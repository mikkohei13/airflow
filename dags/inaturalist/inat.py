import json
import requests

from airflow.models import Variable

import getInat
import inatToDw
import postDw


# Temp helper
def printObject(object):
  print(object.__dict__)


print("Start") 


### GET

airflowVariable_inat_latest_obs_id = Variable.get("inat_latest_obs_id")
airflowVariable_inat_latest_update = Variable.get("inat_latest_update")

print("MY_VAR:" + airflowVariable_inat_latest_obs_id)

# 60063865

inat = getInat.getInat()

# TODO: This will be used for debugging -> not needed in DAG, only on CLI
singleObservationDict = inat.getSingle(airflowVariable_inat_latest_obs_id)


### CONVERT

#print(singleObservationDict)

dwObservationDict = inatToDw.convertObservation(singleObservationDict)
print(dwObservationDict)

dwObservationJson = json.dumps(dwObservationDict)

#pprint(inatResponse)


### POST

dw = postDw.postDw()

#dataJson = json.dumps(data)
#print(dataJson)

dw.postSingleMock(dwObservationJson)

# extracting data in json format 
#data = req.json() 
#print(data)

print("Script ended")
