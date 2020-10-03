

import requests
import json
import pprint


class getInat():

  def __init__(self):
    self._sharedVar = 1


  def getSingle(self, observationId):
    url = "https://api.inaturalist.org/v1/observations?id=" + str(observationId) + "&order=desc&order_by=created_at&include_new_projects=true";

    print("Getting " + url)

    try:
      inatResponse = requests.get(url)
    #printObject(inatResponse)
    except:
      raise Exception("Error getting data from iNaturalist API")

    if 200 == inatResponse.status_code:
      print("iNaturalist API responded " + str(inatResponse.status_code))
    else:
      errorCode = str(inatResponse.status_code)
      raise Exception(f"iNaturalist API responded with error {errorCode}")

    inatResponseDict = json.loads(inatResponse.text)

    if 0 == inatResponseDict["total_results"]:
      raise Exception(f"Zero results from iNaturalist API")

    return inatResponseDict["results"][0]

