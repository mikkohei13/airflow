
def convertObservation(inat):
  """Convert a single observation from iNat to FinBIF DW format.

  Args:
    inat (dictionary): single observation in iNat format.

  Raises:
    Exception: 

  Returns:
    dictionary: single observation in FinBIF DW format
  """

  dw = {}
  dw["collectionId"] = "http://tun.fi/HR.3211"; # Prod: HR.3211 Test: HR.11146

  documentId = dw["collectionId"] + "/" + str(inat["id"])
  dw["documentId"] = documentId

  return dw
