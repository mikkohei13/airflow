

import requests
import json
from collections import OrderedDict
import time

def getPageFromAPI(url):
  """Get a single pageful of observations from iNat.

  Args:
    url (string): API URL to get data from.

  Raises:
    Exception: API responds with code other than 200, or does not repond at all.

  Returns:
    orderedDictionary: Observatons and associated API metadata (paging etc.)
  """
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

  # TODO: create ordered dict. ALREADY DONE?
  inatResponseDict = json.loads(inatResponse.text, object_pairs_hook=OrderedDict)
#  print(inatResponse.text)
#  exit()

  return inatResponseDict


def getUpdatedGenerator(latestObsId, latestUpdateTime, pageLimit, perPage, sleepSeconds):
  """Generator that gets and yields new and updated iNat observations, by handling pagination and calling getPageFromAPI().

  Args:
    latestObsId (int): Highest observation id that should not be fetched.
    latestUpdateTime (string): Time after which updated observations should be fecthed.

  Raises:
    Exception: If getPageFromAPI() fails to fetch data.

  Returns:
    orderedDictionary: Yields observations and associated API metadata (paging etc.)
    boolean: Returns False when no more results.
  """

  # TODO: Check if time(zone) is correct in Docker.

  # TODO: stop after all is fecthed

  page = 0

  while True:
    print("Getting page " + str(page) + " below " + str(pageLimit) + " latestObsId " + str(latestObsId) + " latestUpdateTime " + latestUpdateTime)

    # TODO: Option to get only nonwilds

    url = "https://api.inaturalist.org/v1/observations?place_id=7020%2C10282&page=1&per_page=" + str(perPage) + "&order=asc&order_by=id&updated_since=" + latestUpdateTime + "&id_above=" + str(latestObsId) + "&include_new_projects=true"

    # TODO: Remove this debugging part
    # Debugging case where API does not respond correctly after n:th page
#    debug = True
#    if debug:
#      if page > 0:
        # User broken URI
#        url = "https://api.inaturalist.org/v1/observations?place_id=7020%2C10282&page=1&per_page=" + str(perPage) + "&order=asc&order_by=id&updated_since=" + latestUpdateTime + "&id_above=" + str(latestObsId) + "00&include_new_projects=true"
    # Debug end

#    print("Getting URL " + url)
    inatResponseDict = getPageFromAPI(url)

    resultObservationCount = inatResponseDict["total_results"]
    print("Search matched " + str(resultObservationCount) + " observations.")

    # If no observations on page, just return False
    if 0 == resultObservationCount:
      print("No more observations.")
      return False
    
    else:
      latestObsId = inatResponseDict["results"][-1]["id"]

      page = page + 1
  
      time.sleep(sleepSeconds) # TODO: Can this be after yield?

      # return whole dict
      yield inatResponseDict



def getSingle(observationId):
  """Gets and returns a single iNat observation, by calling getPageFromAPI().

  Args:
    observationId (int): iNat observation id.

  Raises:
    Exception: If getPageFromAPI() fails to fetch data, or if zero result is found.

  Returns:
    orderedDictionary: Single observation and associated API metadata (paging etc.)
  """

  url = "https://api.inaturalist.org/v1/observations?id=" + str(observationId) + "&order=desc&order_by=created_at&include_new_projects=true";

  inatResponseDict = getPageFromAPI(url)

  # When getting a single observation, zero results is an error
  if 0 == inatResponseDict["total_results"]:
    raise Exception(f"Zero results from iNaturalist API")

  return inatResponseDict
  

