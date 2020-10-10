
import sys
import pprint

import getInat
import inatToDw
import postDw

import json # for debug

### SETUP

"""
Test observations
puolukkapiiloyökkönen 60063865 - tags, obs fields, desc with html, annotations (also negative)
(joku)hopeatäplä 53608382 - coll and trad projects, annotations (also negative)
ohdakeperhonen 39330050 - locality names
parmaj 61948403 - kaupunkilinnut, 9 photos
cerfam 61079103 - kaupunkilinnt, 2 photos 1 sound
mittari 60201865 - karkeistettu
sieni lehdellä 60934016 - yksityinen
sammal 62132113 - ei koordinaattien tarkkuutta
tolppa 55900883 - quality metrics

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
