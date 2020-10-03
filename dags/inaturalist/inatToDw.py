
def convertObservation(inat): 
  dw = {}
  dw["collectionId"] = "http://tun.fi/HR.3211"; # Prod: HR.3211 Test: HR.11146

  documentId = dw["collectionId"] + "/" + str(inat["id"])
  dw["documentId"] = documentId

  return dw
