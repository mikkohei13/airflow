
import sys
import pprint

import getInat
import inatToDw
import postDw

import json # for debug

### SETUP

"""
Test observations
puolukkapiiloyökkönen 60063865 - tags, obs fields, desc with html
(joku)hopeatäplä 53608382 - coll and trad projects, obs fields (also negative)
ohdakeperhonen 39330050 - locality names
"""

print("Start") 
pp = pprint.PrettyPrinter(indent=2)

# Get arguments
id = sys.argv[1] # id of the iNat observation
mode = sys.argv[2] # dry | prod

singleObservationDict = getInat.getSingle(id)

if "dry" == mode:
  print("INAT:")
  pp.pprint(singleObservationDict['results'])

dwObservation = inatToDw.convertObservations(singleObservationDict['results'])

print("--------------------------------------------------------------")
print("DW:")
pp.pprint(dwObservation)
json = json.dumps(dwObservation)
print(json)
