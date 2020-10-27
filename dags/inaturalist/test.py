

import json
from collections import OrderedDict
import inatToDw

# Files containing single or multiple observations as inat json
filePath = "testdata/60201865.json"
testFilePath = "testdata/60201865dw.json"

filePath = "testdata/61079103.json"
testFilePath = "testdata/61079103dw.json"



with open(filePath) as file:
  inatJson = file.read()
  file.close()

#print(inatJson)
inatOrdereddict = json.loads(inatJson, object_pairs_hook=OrderedDict)

#print(inatOrdereddict)

dwOrdereddict, lastUpdateKey = inatToDw.convertObservations(inatOrdereddict['results'])

#print(dwOrdereddict)

with open(testFilePath) as file:
  testJson = file.read()
  file.close()

testDwOrdereddict = json.loads(testJson, object_pairs_hook=OrderedDict)

if testDwOrdereddict == dwOrdereddict:
  print("SUCCESS!")
else:
  print("Failure")
