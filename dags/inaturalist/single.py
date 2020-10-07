
import sys
import pprint

import getInat
import inatToDw
import postDw

### SETUP

print("Start") 

# Get arguments
id = sys.argv[1] # id of the iNat observation, puolukkapiiloyökkönen 60063865
mode = sys.argv[2] # dry | prod

singleObservationDict = getInat.getSingle(id)

dwObservation = inatToDw.convertObservations(singleObservationDict['results'])

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(dwObservation)
