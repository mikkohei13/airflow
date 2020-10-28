

import json
from collections import OrderedDict
import inatToDw

sourceFiles = []
targetFiles = []

# Files containing single or multiple observations as inat json
sourceFiles.append("testdata/60201865-source.json")
targetFiles.append("testdata/60201865-target.json")

sourceFiles.append("testdata/48148712-source.json")
targetFiles.append("testdata/48148712-target.json")

sourceFiles.append("testdata/60934016-source.json")
targetFiles.append("testdata/60934016-target.json")

print("")
print("__TESTS_STARTING______________________________")


for fileNro, sourceFilePath in enumerate(sourceFiles):

  with open(sourceFilePath) as file:
    inatJson = file.read()
    file.close()

  #print(inatJson)
  inatOrdereddict = json.loads(inatJson, object_pairs_hook=OrderedDict)

  #print(inatOrdereddict)

  dwOrdereddict, lastUpdateKey = inatToDw.convertObservations(inatOrdereddict['results'])

  #print(dwOrdereddict)

  with open(targetFiles[fileNro]) as file:
    testJson = file.read()
    file.close()

  testDwOrdereddict = json.loads(testJson, object_pairs_hook=OrderedDict)

  if testDwOrdereddict == dwOrdereddict:
    print("SUCCESS: " + str(lastUpdateKey))
  else:
    print("**********")
    print("Failure: " + str(lastUpdateKey))
    print("**********")

