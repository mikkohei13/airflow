
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


def appendFact(factsList, inat, factName):
  # Handles only keys directly under root of inat

  if factName in inat: # Checks if key exists
    if inat[factName]: # Checks if value is truthy
      factsList.append({factName: inat[factName]})

  return factsList


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

    desc = {}

    keywords = []
    documentFacts = []
    gatheringFacts = []
    unitFacts = []

    # -------------------------------------
    # Conversions

    # Data shared by all observations
    # TODO: select prod/dev coll ... how?
    collectionId = "http://tun.fi/HR.3211"; # Prod: HR.3211 Test: HR.11146
    dw["collectionId"] = collectionId
    publicDocument['collectionId'] = collectionId

    dw['sourceId'] = "http://tun.fi/KE.901"
    dw['schema'] = "laji-etl";
    publicDocument['secureLevel'] = "NONE";
    publicDocument['concealment'] = "PUBLIC";

    # identifiers
    documentId = dw["collectionId"] + "/" + str(inat["id"])
    dw["documentId"] = documentId
    publicDocument['documentId'] = documentId
    gathering['gatheringId'] = documentId + "-G"
    unit['unitId'] = documentId + "-U"

    documentFacts.append({"catalogueNumber": inat['id']})
    documentFacts.append({"referenceURI": inat['uri']})
    keywords.append(str(inat['id'])) # id has to be string

    dw["id"] = inat["id"] # The original id is needed for returning lastUpdateKey, so do not remove it here! TODO maybe: this function returns the id, then inat.py uses it only if posting was successful


    # Wildness
    if 1 == inat["captive"]:
      unit['wild'] = False;

    # Quality
    if inat['flags']:
      x=1
      # TODO: quality 


    # Observations fields
    for nro, val in enumerate(inat['ofvs']):
      unitFacts.append({val['name_ci']: val['value_ci']}) # This preserves zero values, which can be important in observation fields
    
    # Misc facts
    appendFact(unitFacts, inat, "out_of_range")
    appendFact(unitFacts, inat, "taxon_geoprivacy")
    appendFact(unitFacts, inat, "geoprivacy")
    appendFact(unitFacts, inat, "context_geoprivacy")
    appendFact(unitFacts, inat, "context_user_geoprivacy")
    appendFact(unitFacts, inat, "context_taxon_geoprivacy")
    appendFact(unitFacts, inat, "comments_count")
    appendFact(unitFacts, inat, "num_identification_agreements")
    appendFact(unitFacts, inat, "num_identification_disagreements")
    appendFact(unitFacts, inat, "owners_identification_from_vision")
    appendFact(unitFacts, inat, "oauth_application_id")


    # -------------------------------------
    # Build the multidimensional dictionary

    publicDocument['facts'] = documentFacts
    gathering['facts'] = gatheringFacts
    unit['facts'] = unitFacts


    gathering["units"] = []
    gathering["units"].append(unit)

    publicDocument['gatherings'] = []
    publicDocument['gatherings'].append(gathering)

    dw['publicDocument'] = publicDocument

    dwObservations.append(dw)
    print("Converted obs " + str(inat["id"]))

  # End for each observations

  return dwObservations