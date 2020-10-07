
#from collections import defaultdict

def skipObservation(inat):
  if not inat["taxon"]:
    print("Skipping observation " + str(inat["id"]) + " without taxon.")
    return True
  elif not inat["observed_on_details"]:
    print("Skipping observation " + str(inat["id"]) + " without date.")
    return True
  else:
    return False


def convertObservations(inatObservations):
  """Convert a single observation from iNat to FinBIF DW format.

  Args:
  inat (orderedDictionary): single observation in iNat format.

  Raises:
  Exception: 

  Returns:
  orderedDictionary: multiple observations in FinBIF DW format
  False: if observation should not be posted to DW

  Test:
  - obs without observed_on_details
  """

  dwObservations = []

  # For each observation
  for nro, inat in enumerate(inatObservations):

    # Skip incomplete observations
    if skipObservation(inat):
      continue

#    dw = defaultdict(dict)

    # Prepare elements of the observation
    dw = {}
    publicDocument = {}
    gathering = {}
    unit = {}

    # -------------------------------------
    # Conversions

    # Identifiers
    dw["collectionId"] = "http://tun.fi/HR.3211"; # Prod: HR.3211 Test: HR.11146

    documentId = dw["collectionId"] + "/" + str(inat["id"])
    dw["documentId"] = documentId
    dw["id"] = inat["id"] # The original id is needed for returning lastUpdateKey, so do not remove it here! TODO maybe: this function returns the id, then inat.py uses it only if posting was successful


    # Wildness
    inat["captive"] = 1 # debug
    if 1 == inat["captive"]:
      unit['wild'] = False;


    # -------------------------------------
    # Build the multidimensional dictionary
    gathering["units"] = {}
    gathering["units"][0] = unit

    publicDocument['gatherings'] = {}
    publicDocument['gatherings'][0] = gathering

    dw['publicDocument'] = publicDocument

    dwObservations.append(dw)
    print("Converted obs " + str(inat["id"]))

  # End for each observations

  return dwObservations