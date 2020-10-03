

import requests
import json
import datetime


class getInat():

  def __init__(self):
    self._sharedVar = 1


  def getPageFromAPI(self, url):
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

    return inatResponseDict


  def getUpdated(self):
    # TODO: Check if time(zone) is correct in Docker.

    # This will be the new updatedLast time in Variables. Generating update time here, since observations are coming from the API sorted by id, not by datemodified -> cannot use time of last record
    now = datetime.datetime.now()
    thisUpdateTime = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    # TODO: From Variable
    lastUpdateKey = 0
    lastUpdateTime = "2020-10-03T21:00:00+00:00"


    perPage = 3 # Production value: 100
    maxPages = 3 # Production value: 1000
    page = 0

    while page < maxPages:
      print("Getting page " + str(page) + " below " + str(maxPages) + " thisUpdateTime " + thisUpdateTime + " lastUpdateKey " + str(lastUpdateKey) + " lastUpdateTime " + lastUpdateTime)
      page = page + 1

      # TODO: Option to get only nonwilds

      url = "https://api.inaturalist.org/v1/observations?place_id=7020%2C10282&page=1&per_page=" + str(perPage) + "&order=asc&order_by=id&updated_since=" + lastUpdateTime + "&id_above=" + str(lastUpdateKey) + "&include_new_projects=true"

      # TODO: If fails, return latest successful id. Then push this to variables.
      # Option, yield exception with value, then use isinstance to check if it's exception or not. If exception, push t variables and stop.
      # Check: throwing vs. raising errors
      inatResponseDict = self.getPageFromAPI(url)

      yield inatResponseDict["results"]





  def getSingle(self, observationId):
    url = "https://api.inaturalist.org/v1/observations?id=" + str(observationId) + "&order=desc&order_by=created_at&include_new_projects=true";

    inatResponseDict = self.getPageFromAPI(url)

    # When getting a single observation, zero results is an error
    if 0 == inatResponseDict["total_results"]:
      raise Exception(f"Zero results from iNaturalist API")

    return inatResponseDict["results"][0]
    

