

import requests
import json

class postDw():

  def __init__(self):
    self._sharedVar = 1


  def postSingleMock(self, dwObservationJson):
    targetUrl = "https://14935.mocklab.io/inat"

    # sending post request and saving the response as response object 
    targetRequest = requests.post(url = targetUrl, data = dwObservationJson) 
    print(targetRequest)
