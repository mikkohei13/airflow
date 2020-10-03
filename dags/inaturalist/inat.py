import json
import requests

import getInat
import inatToDw
import postDw


# Temp helper
def printObject(object):
  print(object.__dict__)


print("Start") 


### GET

inat = getInat.getInat()

singleObservationDict = inat.getSingle(60063865)


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
