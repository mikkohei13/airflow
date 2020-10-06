def convertObservations(inatObservations):
  """Convert a single observation from iNat to FinBIF DW format.

  Args:
  inat (orderedDictionary): single observation in iNat format.

  Raises:
  Exception: 

  Returns:
  orderedDictionary: multiple observations in FinBIF DW format
  """

  dwObservations = []

  # For each observation
  for nro, inat in enumerate(inatObservations):
  #    if False == inatObs:
  #      return dwObservations

    dw = {}
    dw["collectionId"] = "http://tun.fi/HR.3211"; # Prod: HR.3211 Test: HR.11146

    documentId = dw["collectionId"] + "/" + str(inat["id"])
    dw["documentId"] = documentId

    dwObservations.append(dw)
    print("Converted obs " + str(inat["id"]))

  # End for each observations

  return dwObservations