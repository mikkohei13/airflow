

import requests
import json

class postDw():

  def __init__(self):
    self._sharedVar = 1


  def postSingleMock(self, dwObs):
    dwObservationJson = json.dumps(dwObs)
    targetUrl = "https://14935.mocklab.io/inat"

    # sending post request and saving the response as response object 
    targetRequest = requests.post(url = targetUrl, data = dwObservationJson) 
    print(targetRequest)


  def postMultiMock(self, dwObservations):
    lastUpdateKey = dwObservations[-1]["id"]

    dwObservationsJson = json.dumps(dwObservations)
    targetUrl = "https://14935.mocklab.io/inat"

    # sending post request and saving the response as response object 
    targetRequest = requests.post(url = targetUrl, data = dwObservationsJson) 

    if 200 == targetRequest.status_code:
      print("Mock API responded " + str(targetRequest.status_code))
      return lastUpdateKey
    else:
      errorCode = str(targetRequest.status_code)
      raise Exception(f"Mock API responded with error {errorCode}")

