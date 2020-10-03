from airflow.models import Variable

import getInat

inat = getInat.getInat()

i = 0 # Debug

# TODO: From Variable
lastUpdateKey = 0
lastUpdateTime = "2020-10-03T21:00:00+00:00"

for multiObservationDict in inat.getUpdatedGenerator(lastUpdateKey, lastUpdateTime):
  print(str(i))
  i = i + 1
#  print(multiObservationDict)

