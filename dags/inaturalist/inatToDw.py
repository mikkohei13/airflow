
#from collections import defaultdict
import pprint
import json # for debug


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


def appendCollectionProjects(factsList, projects):
  for nro, project in enumerate(projects):
    factsList.append({"collectionProjectId": project['project_id']})
  return factsList


def appendTraditionalProjects(factsList, projects):
  for nro, project in enumerate(projects):
    factsList.append({"traditionalProjectId": project['project']['id']})
  return factsList


def appendTags(keywordsList, tags):
  for nro, tag in enumerate(tags):
    keywordsList.append(tag)
  return keywordsList


def summarizeQualityMetrics(quality_metrics):
  summary = {}

  for nro, vote in enumerate(quality_metrics):
    # Skip vote if spam or suspended user
    if vote["user"]["spam"]:
      continue
    if vote["user"]["suspended"]:
      continue 

    # Calculate vote
    if True == vote["agree"]:
      value = 1
    elif False == vote["agree"]:
      value = -1
    else:
      value = 0 

    # Init if not set
    if vote["metric"] not in summary:
      summary[vote["metric"]] = 0 

    summary[vote["metric"]] = summary[vote["metric"]] + value

  return summary


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

    # Debug
#    jsonData = json.dumps(inat)
#    print(jsonData)
#    pp = pprint.PrettyPrinter(indent=2)
#    pp.pprint(jsonData)
#    exit()

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


    # Description
    if "description" in inat: # TODO: This line not needed, even if desc would be missing??
      gathering['notes'] = inat["description"]


    # Wildness
    if 1 == inat["captive"]:
      unit['wild'] = False;


    # Projects
    # Non-traditional / Collection (automatic)
    if "non_traditional_projects" in inat:
      documentFacts = appendCollectionProjects(documentFacts, inat['non_traditional_projects'])
    
    # Traditional (manual)
    if "project_observations" in inat:
      documentFacts = appendTraditionalProjects(documentFacts, inat['project_observations'])


    # Dates
    publicDocument['createdDate'] = inat['created_at_details']['date']

    updatedDatePieces = inat['updated_at'].split("T")
    publicDocument['modifiedDate'] = updatedDatePieces[0]

    gathering['eventDate'] = {}
    gathering['eventDate']['begin'] = inat['observed_on_details']['date'] # TODO: test if date is missing
    gathering['eventDate']['end'] = gathering['eventDate']['begin'] # End alsways same as beginning

    documentFacts.append({"observedOrCreatedAt": inat['time_observed_at']}) # This is the exact datetime when observation was saved


    # Locality
    # Locality name used to be reversed, but not needed really?
    gathering['locality'] = inat['place_guess']
    gathering['country'] = "Finland"; # NOTE: This expects that only Finnish observations are fecthed


    # Tags
    if "tags" in inat:
      keywords = appendTags(keywords, inat["tags"])


    # Quality
    if inat['flags']:
      x=1
      # TODO: quality 


    # Quality metrics
    # TODO: There was byg in the PHP version: if quality was less than -1, not marked as unreliable. Must reprocess all.
    qualityMetricUnreliable = False
    if "quality_metrics" in inat:
      qualityMetricsSummary = summarizeQualityMetrics(inat["quality_metrics"])
      print(qualityMetricsSummary)

      for metric, value in qualityMetricsSummary.items():
        # Add to facts
        metricName = "quality_metrics_" + metric
        unitFacts.append({metricName: str(value)})

        # If at least one negative quality metric, mark as unreliable. Exception: non-wilds are handled elsewhere.
        if "wild" != metric:
          if value < 0:
            qualityMetricUnreliable = True

    


    # Observation fields
    for nro, val in enumerate(inat['ofvs']):
      unitFacts.append({val['name_ci']: val['value_ci']}) # This preserves zero values, which can be important in observation fields
    
    # Misc facts
    unitFacts = appendFact(unitFacts, inat, "out_of_range")
    unitFacts = appendFact(unitFacts, inat, "taxon_geoprivacy")
    unitFacts = appendFact(unitFacts, inat, "geoprivacy")
    unitFacts = appendFact(unitFacts, inat, "context_geoprivacy")
    unitFacts = appendFact(unitFacts, inat, "context_user_geoprivacy")
    unitFacts = appendFact(unitFacts, inat, "context_taxon_geoprivacy")
    unitFacts = appendFact(unitFacts, inat, "comments_count")
    unitFacts = appendFact(unitFacts, inat, "num_identification_agreements")
    unitFacts = appendFact(unitFacts, inat, "num_identification_disagreements")
    unitFacts = appendFact(unitFacts, inat, "owners_identification_from_vision")
    unitFacts = appendFact(unitFacts, inat, "oauth_application_id")


    # -------------------------------------
    # Build the multidimensional dictionary

    publicDocument['facts'] = documentFacts
    gathering['facts'] = gatheringFacts
    unit['facts'] = unitFacts
    publicDocument['keywords'] = keywords


    gathering["units"] = []
    gathering["units"].append(unit)

    publicDocument['gatherings'] = []
    publicDocument['gatherings'].append(gathering)

    dw['publicDocument'] = publicDocument

    dwObservations.append(dw)
    print("Converted obs " + str(inat["id"]))

  # End for each observations

  return dwObservations