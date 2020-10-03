from airflow.models import Variable

import getInat

inat = getInat.getInat()

i = 0 # Debug

# Todo: make function stateless, i.e. pass starting values here
# This is generator that yields data
for multiObservationDict in inat.getUpdated():
  print(str(i))
  i = i + 1
  print(multiObservationDict)

