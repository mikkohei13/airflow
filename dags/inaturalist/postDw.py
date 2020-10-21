

import requests
import json

from airflow.models import Variable


def postSingle(dwObs, target):
#  dwObsJson = json.dumps(dwObs)
#  print(dwObsJson)
#  exit()

  if "staging" == target:
    print("Pushing to staging API")
    targetUrl = "https://apitest.laji.fi/v0/warehouse/push?access_token=" + Variable.get("inat_staging_token")

  elif "production" == target:
    print("Pushing to production API")
    targetUrl = "https://api.laji.fi/v0/warehouse/push?access_token=" + Variable.get("inat_production_token")


  # Sending post request and saving the response as response object 
  print("Pushing to " + targetUrl)
  targetResponse = requests.post(url = targetUrl, json = dwObs) 

  if 200 == targetResponse.status_code:
    print("API responded " + str(targetResponse.status_code))
    return True

  else:
    errorCode = str(targetResponse.status_code)
    print(targetResponse.text)
    raise Exception(f"API responded with error {errorCode}")


def postMulti(dwObs, target):
#  dwObsJson = json.dumps(dwObs)

  if "staging" == target:
    print("Pushing to staging API.")
    targetUrl = "https://apitest.laji.fi/v0/warehouse/push?access_token=" + Variable.get("inat_staging_token")

  elif "production" == target:
    print("Pushing to production API")
    targetUrl = "https://api.laji.fi/v0/warehouse/push?access_token=" + Variable.get("inat_production_token")

  # sending post request and saving the response as response object 
  print("Pushing to " + targetUrl)
  targetResponse = requests.post(url = targetUrl, json = dwObs) 

  if 200 == targetResponse.status_code:
    print("API responded " + str(targetResponse.status_code))
    return True

  else:
    errorCode = str(targetResponse.status_code)
    raise Exception(f"API responded with error {errorCode}")


def postSingleMock(dwObs, mock):
  print("Pushing to mock API.")
  airflowVariable_token = Variable.get("inat_mock_token")

  targetUrl = "https://14935.mocklab.io/inat"

  # Sending post request and saving the response as response object 
  targetResponse = requests.post(url = targetUrl, json = dwObs) 
#  print(targetResponse)

  if 200 == targetResponse.status_code:
    print("Mock API responded " + str(targetResponse.status_code))
    return True

  else:
    errorCode = str(targetResponse.status_code)
    raise Exception(f"Mock API responded with error {errorCode}")


def postMultiMock(dwObs, lastUpdateKey):
  print("Pushing to mock API.")
  airflowVariable_token = Variable.get("inat_mock_token")

  targetUrl = "https://14935.mocklab.io/inat"

  # sending post request and saving the response as response object 
  targetResponse = requests.post(url = targetUrl, json = dwObs) 

  if 200 == targetResponse.status_code:
    print("Mock API responded " + str(targetResponse.status_code))
    return True

  else:
    errorCode = str(targetResponse.status_code)
    raise Exception(f"Mock API responded with error {errorCode}")

