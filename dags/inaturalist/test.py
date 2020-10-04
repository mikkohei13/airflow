from airflow.models import Variable

import getInat

inat = getInat.getInat()

i = 0 # Debug

airflowVariable_inat_latest_obs_id = Variable.get("inat_latest_obs_id")
airflowVariable_inat_latest_update = Variable.get("inat_latest_update")

# TODO: From Variable
#lastUpdateKey = 60063865
#lastUpdateTime = "2020-10-03T21:00:00+00:00"

for multiObservationDict in inat.getUpdatedGenerator(airflowVariable_inat_latest_obs_id, airflowVariable_inat_latest_update):
  print(str(i))
  # Convert and sent observations 

  # If all successful:
  # lastUpdateKey = # get from result
  # set lastUpdateKey as variable
  i = i + 1
#  print(multiObservationDict)


# If whole for was successful
# TODO: set the started datetime value
Variable.set("inat_latest_update", "2020-10-03T21:00:00+00:00")
