
#from collections import defaultdict
import pprint
import json # for debug

"""
NOTES/POSSIBLY TODO:
- There was bug in the PHP version: if quality was less than -1, not marked as unreliable. Must reprocess all.
- DW removes/hides humans, so handling them here is not needed. (Used to make private, remove images and description.)
- What to do if observation contains 1...n copyright infringement flaged media files, e.g. https://www.inaturalist.org/observations/46356508
- Earlier removed FI, Finland & Suomi from the location name, but not anymore
- Filter out unwanter users (e.g. test users: testaaja, outo)

Misc facts left out:
"identifications_most_agree"
"identifications_most_disagree"
"observerActivityCount" // This is problematic because it increases over time -> is affected by *when* the observation was fetched from iNat

iNat API features:
- This conversion expects that all observations are from Finland, and are filtered by the API call. If changed, need to remove hard-coded country name here.
- Quality metrics appear on the api after a delay (15 mins?)
- 

DW data features:
- There can be multiple facts with the same name
- Facts are strings
- Fields can be left blank
- Enum values are ALL-CAPS

"""


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


def getLicenseUrl(licenseCode):
  licenses = {}
  licenses["cc0"] = "http://tun.fi/MZ.intellectualRightsCC0-4.0"
  licenses["cc-by"] = "http://tun.fi/MZ.intellectualRightsCC-BY-4.0"
  licenses["cc-by-nc"] = "http://tun.fi/MZ.intellectualRightsCC-BY-NC-4.0"
  licenses["cc-by-nd"] = "http://tun.fi/MZ.intellectualRightsCC-BY-ND-4.0"
  licenses["cc-by-sa"] = "http://tun.fi/MZ.intellectualRightsCC-BY-SA-4.0"
  licenses["cc-by-nc-nd"] = "http://tun.fi/MZ.intellectualRightsCC-BY-NC-ND-4.0"
  licenses["cc-by-nc-sa"] = "http://tun.fi/MZ.intellectualRightsCC-BY-NC-SA-4.0"

  if False == licenseCode:
    return "http://tun.fi/MZ.intellectualRightsARR"
  else:
    if licenseCode in licenses:
      return licenses[licenseCode]
    else:
      print("Unknown license code " + licenseCode)
      return "http://tun.fi/MZ.intellectualRightsARR"


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


    # Observation fields
    for nro, val in enumerate(inat['ofvs']):
      unitFacts.append({val['name_ci']: val['value_ci']}) # This preserves zero values, which can be important in observation fields


    # License URL's/URI's
    publicDocument['licenseId'] = getLicenseUrl(inat['license_code'])


    # Observer
    # Observer name, prefer full name over loginname
    if inat['user']['name']:
      observer = inat['user']['name']
    else:
      observer = inat['user']['login']

    gathering['team'] = []
    gathering['team'].append(observer)


    # Editor & observer id
    userId = "inaturalist:"  + str(inat['user']['id'])
    publicDocument['editorUserIds'] = []
    publicDocument['editorUserIds'].append(userId)
    gathering['observerUserIds'] = []
    gathering['observerUserIds'].append(userId)


    # Orcid
    if inat['user']['orcid']:
      documentFacts.append({"observerOrcid": inat['user']['orcid']}) 


    # Quality metrics
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


    # Quality on DW
    # Init
    unit["quality"] = {}
    unit["quality"]["issue"] = {}

    # Negative quality metrics (thumbs down) 
    # TODO: Check: does this make issue, or mark as unreliable, or both on Laji.fi?
    if qualityMetricUnreliable:
      unit["quality"]["issue"]["issue"] = "REPORTED_UNRELIABLE"
      unit["quality"]["issue"]["source"] = "ORIGINAL_DOCUMENT"
      keywords.append("quality-metric-unreliable")

    # Flags
    # TODO: Has not been tested!
    if inat["flags"]:
      publicDocument['concealment'] = "PRIVATE" # Mark private, because might be flagged due to copyright or privacy reasons.
      unit["quality"]["issue"]["issue"] = "REPORTED_UNRELIABLE"
      unit["quality"]["issue"]["source"] = "ORIGINAL_DOCUMENT"
      keywords.append("flagged")


    # Quality grade
    unitFacts.append({"quality_grade": inat['quality_grade'] + "_grade"})
    keywords.append(inat['quality_grade'] + "_grade")

    # Quality tags
    if "research" == inat['quality_grade']:
      unit['sourceTags'] = []
      unit['sourceTags'].append("COMMUNITY_TAG_VERIFIED")


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