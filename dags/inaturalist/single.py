
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

Flagged observations to test with:
https://www.inaturalist.org/flags?commit=Suodata&flaggable_type=Observation&flagger_name=&flagger_type=any&flagger_user_id=&flags%5B%5D=other&page=3&reason_query=&resolved=no&resolver_name=&resolver_user_id=&user_id=&user_name=&utf8=%E2%9C%93

"""

# Input
id = sys.argv[1] # id of the iNat observation
mode = sys.argv[2] # dry | prod


# Get and transform data
singleObservationDict = getInat.getSingle(id)

dwObservation = inatToDw.convertObservations(singleObservationDict['results'])


# Output
pp = pprint.PrettyPrinter(indent=2)

if "prod" == mode:
  print("Pushing to DW")
  # TODO: push to DW

else:
  if "dry-verbose" == mode:
    print("INAT:")
    print(singleObservationDict['results'])

  print("--------------------------------------------------------------")
  print("DW:")
  pp.pprint(dwObservation)
  print("--------------------------------------------------------------")
  print(json.dumps(dwObservation))

