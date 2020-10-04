

import requests
import json
from collections import OrderedDict


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

    # TODO: Find out why slightly too large idAbove returns 200 with zero results, but with much too large returns 400 
    if 200 == inatResponse.status_code:
      print("iNaturalist API responded " + str(inatResponse.status_code))
    else:
      errorCode = str(inatResponse.status_code)
      raise Exception(f"iNaturalist API responded with error {errorCode}")

    # TODO: create ordered dict
    inatResponseDict = json.loads(inatResponse.text, object_pairs_hook=OrderedDict)

    return inatResponseDict


  def getUpdatedGenerator(self, lastUpdateKey, lastUpdateTime):
    # TODO: Check if time(zone) is correct in Docker.

    perPage = 3 # Production value: 100
    maxPages = 3 # Production value: 1000
    page = 0

    while page < maxPages:
      log = "Getting page " + str(page) + " below " + str(maxPages) + " lastUpdateKey " + str(lastUpdateKey) + " lastUpdateTime " + lastUpdateTime
      print(log)

      # TODO: Option to get only nonwilds

      url = "https://api.inaturalist.org/v1/observations?place_id=7020%2C10282&page=1&per_page=" + str(perPage) + "&order=asc&order_by=id&updated_since=" + lastUpdateTime + "&id_above=" + str(lastUpdateKey) + "&include_new_projects=true"

      debug = True
      if debug:
        if page > 0:
          # User broken URI
          url = "https://api.inaturalist.org/v1/observations?place_id=7020%2C10282&page=1&per_page=" + str(perPage) + "&order=asc&order_by=id&updated_since=" + lastUpdateTime + "&id_above=" + str(lastUpdateKey) + "00&include_new_projects=true"

        inatResponseDict = self.getPageFromAPI(url)
        print("Got: " + log + "\n")
        page = page + 1

      # return whole dict
      yield inatResponseDict



  def getSingle(self, observationId):
    url = "https://api.inaturalist.org/v1/observations?id=" + str(observationId) + "&order=desc&order_by=created_at&include_new_projects=true";

    inatResponseDict = self.getPageFromAPI(url)

    # When getting a single observation, zero results is an error
    if 0 == inatResponseDict["total_results"]:
      raise Exception(f"Zero results from iNaturalist API")

    # TODO: Check should this return the whole dict?
    return inatResponseDict["results"][0]
    

