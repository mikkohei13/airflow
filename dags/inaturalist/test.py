from airflow.models import Variable

import getInat

inat = getInat.getInat()

i = 0 # Debug

# TODO: From Variable
lastUpdateKey = 0
lastUpdateTime = "2020-10-03T21:00:00+00:00"

for multiObservationDict in inat.getUpdatedGenerator(lastUpdateKey, lastUpdateTime):
  # Untested!
  if isinstance(multiObservationDict, Exception):
    raise Exception;
    break;
  else:
    print(str(i))
    # lastUpdateKey = # get from result
    # set lastUpdateKey as variable
    i = i + 1
#  print(multiObservationDict)

