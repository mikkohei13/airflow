
#from collections import defaultdict
import pprint
import json # for debug

import inatHelpers

"""
BUGFIXES COMPARED TO PHP VERSION 9/2020:
- If quality was less than -1, not marked as unreliable. Must reprocess all.
- If obs had multiple ARR images, multiple image_arr keywords were set.
- Obscured obs coordinate box was calculated incorrectly
- Obscured obs accuracy was set to 0
- Annotations were saved incorrectly, so that also negative and tied votes resulted in positive annotation and fact.

NOTES/CHANGES COMPARED TO PHP VERSION 9/2020:
- Script expects that all observations are from Finland, so it fills in hardcoded country name. Must change this if also foreign observations ar handled.
- DW removes/hides humans, so handling them here is not needed. (Used to make them private, remove images and description.)
- What to do if observation contains 1...n copyright infringement flagged media files? E.g. https://www.inaturalist.org/observations/46356508
- Earlier removed FI, Finland & Suomi from the location name, but not anymore
- Possibly TODO: Filter out unwanter users (e.g. test users: testaaja, outo)
- Previously used copyright string, now just user name for photo attribution, since license in separate field.
- Unit fact taxonByUser changed name to species_guess, which is the term used by iNat. Logic of this field is unclear.
- observerActivityCount should not be used, since it increases over time -> is affected by *when* the observation was fetched from iNat.
- Note that at least annotations and quality metrics appear on the api after a delay (c. 15 mins cache?)

DW data features:
- There can be multiple facts with the same name
- Facts are strings
- Fields can be left blank
- Enum values are ALL-CAPS
- Can there be multiple similar keywords?

"""


def skipObservation(inat):
  # Note: This is only for skipping observations that don't YET have enough infor to be worthwhile to be included to DW. Don't skip e.g. spam here, because then spammy observations would stay in DW forever. Instead mark them as having issues.

  if not inat["taxon"]:
    print("Skipping observation " + str(inat["id"]) + " without taxon.")
    return True
  elif not inat["observed_on_details"]:
    print("Skipping observation " + str(inat["id"]) + " without date.")
    return True
  else:
    return False


def appendKeyword(keywordList, inat, keywordName):
  # Handles only keys directly under root of inat

  if keywordName in inat: # Checks if key exists
    if inat[keywordName]: # Checks if value is truthy
      keywordList.append(keywordName)

  return keywordList


def appendCollectionProjects(factsList, projects):
  for nro, project in enumerate(projects):
    factsList.append({ "fact": "collectionProjectId", "name": project['project_id'] })
  return factsList


def appendTraditionalProjects(factsList, projects):
  for nro, project in enumerate(projects):
    factsList.append({ "fact": "traditionalProjectId", "value": project['project']['id'] })
  return factsList


def appendTags(keywordsList, tags):
  for nro, tag in enumerate(tags):
    keywordsList.append(tag)
  return keywordsList


def summarizeQualityMetrics(quality_metrics):
  summary = {}

  for nro, vote in enumerate(quality_metrics):
    # Skip vote if spam or suspended user, NOT TESTED
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

  if not licenseCode:
    return "http://tun.fi/MZ.intellectualRightsARR"
  else:
    if licenseCode in licenses:
      return licenses[licenseCode]
    else:
      print("Unknown license code " + str(licenseCode))
      return "http://tun.fi/MZ.intellectualRightsARR"


def getImageData(photo, observer):
  squareUrl = photo['photo']['url']

  thumbnailUrl = squareUrl.replace("square", "small")
  thumbnailUrl = thumbnailUrl.replace("https://static.inaturalist.org/photos/", "https://proxy.laji.fi/inaturalist/photos/") # TODO: refactor into helper

  fullUrl = squareUrl.replace("square", "original")
  fullUrl = fullUrl.replace("https://static.inaturalist.org/photos/", "https://proxy.laji.fi/inaturalist/photos/") # TODO: refactor

  photoDict = {}
  photoDict['thumbnailURL'] = thumbnailUrl
  photoDict['fullURL'] = fullUrl
  photoDict['copyrightOwner'] = observer
  photoDict['author'] = observer
  photoDict['licenseId'] = getLicenseUrl(photo['photo']['license_code'])
  photoDict['mediaType'] = "IMAGE"
  return photoDict


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
  lastUpdateKey = 0

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
    
    # Init empty values
    gathering['notes'] = ""
    unit['sourceTags'] = []
    unit["quality"] = {}
    unit["quality"]["issue"] = {}

    # -------------------------------------
    # Conversions

    # Data shared by all observations
    # TODO: select production/dev coll ... how?
    collectionId = "http://tun.fi/HR.3211" # production: HR.3211 Test: HR.11146
    dw["collectionId"] = collectionId
    publicDocument['collectionId'] = collectionId

    dw['sourceId'] = "http://tun.fi/KE.901"
    dw['schema'] = "laji-etl"
    publicDocument['secureLevel'] = "NONE"
    publicDocument['concealment'] = "PUBLIC"


    # Identifiers
    documentId = dw["collectionId"] + "/" + str(inat["id"])
    dw["documentId"] = documentId
    publicDocument['documentId'] = documentId
    gathering['gatheringId'] = documentId + "-G"
    unit['unitId'] = documentId + "-U"

    documentFacts.append({ "fact": "catalogueNumber", "value": inat['id']})
    documentFacts.append({ "fact": "referenceURI", "value": inat['uri']})
    keywords.append(str(inat['id'])) # id has to be string


    # Taxon
    # Scientific name iNat interprets this to be, special cases converted to match FinBIF taxonomy
    unit['taxonVerbatim'] = inatHelpers.convertTaxon(inat['taxon']['name'])

    # Name observer or identifiers(?) have given, can be any language
    unitFacts.append({ "fact": "species_guess", "value": inat['species_guess']})

    # Scientific name iNat interprets this to be
    unitFacts.append({ "fact": "taxonInterpretationByiNaturalist", "value": inat['taxon']['name']})


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
      documentFacts.append({ "fact": "observerOrcid", "value": inat['user']['orcid']}) 


    # Description
    if inat["description"]:
      gathering['notes'] = gathering['notes'] + inat["description"]


    # Wildness
    if 1 == inat["captive"]:
      unit['wild'] = False


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

    documentFacts.append({ "fact": "observedOrCreatedAt", "value": inat['time_observed_at']}) # This is the exact datetime when observation was saved


    # Locality
    # Locality name used to be reversed, but not needed really?
    gathering['locality'] = inat['place_guess']
    gathering['country'] = "Finland" # NOTE: This expects that only Finnish observations are fecthed


    # Tags
    if "tags" in inat:
      keywords = appendTags(keywords, inat["tags"])

    
    # Photos
    photoCount = len(inat['observation_photos'])
    if photoCount >= 1:
      unit['media'] = []
      keywords.append("has_photos") # Needed for combined photo & image search
      unitFacts.append({ "fact": "imageCount", "value": photoCount})
      arrImagesIncluded = False

      if photoCount > 4:
        keywords.append("over_4_photos")

      for nro, photo in enumerate(inat['observation_photos']):
        # Facts
        photoId = str(photo['photo']['id'])
        unitFacts.append({ "fact": "imageId", "value": photoId})
        unitFacts.append({ "fact": "imageUrl", "value": "https://www.inaturalist.org/photos/" + photoId})

        # Photo
        if photo['photo']['license_code']:
          unit['media'].append(getImageData(photo, observer))
        else:
          arrImagesIncluded = True 

      if arrImagesIncluded:
        keywords.append("image_arr") # Set if at least one photo is missing license   


    # Sounds
    soundCount = len(inat['sounds'])
    # Note: if audio is later linked via proxy, need to check that cc-license is given 
    if soundCount >= 1:
      keywords.append("has_sounds") # Needed for combined photo & image search
      unitFacts.append({ "fact": "soundCount", "value": soundCount})

      if soundCount > 1:
        keywords.append("over_1_sounds")

      for nro, sound in enumerate(inat['sounds']):
        unitFacts.append({ "fact": "audioId", "value": sound['id']})
        unitFacts.append({ "fact": "audioUrl", "value": sound['file_url']})


    # Any media
    if 0 == soundCount and 0 == photoCount:
      keywords.append("no_media")


    # Observation fields
    hasSpecimen = False
    for nro, val in enumerate(inat['ofvs']):
      unitFacts.append({ "fact": val['name_ci'], "value": val['value_ci']}) # This preserves zero values, which can be important in observation fields
      if "Specimen" == val['name_ci']:
        hasSpecimen = True


    # Record basis
    # TODO: Refactor into function
    if hasSpecimen:
      unit['recordBasis'] = "PRESERVED_SPECIMEN"
    elif photoCount >= 1:
      unit['recordBasis'] = "HUMAN_OBSERVATION_PHOTO"
    elif soundCount >= 1:
      unit['recordBasis'] = "HUMAN_OBSERVATION_RECORDED_AUDIO"
    else:
      unit['recordBasis'] = "HUMAN_OBSERVATION_UNSPECIFIED"


    # License URL's/URI's
    publicDocument['licenseId'] = getLicenseUrl(inat['license_code'])


    # Annotations
    if inat['annotations']:
      keywords.append("has_annotations")

      for nro, annotation in enumerate(inat['annotations']):
        key, value = inatHelpers.summarizeAnnotation(annotation)

        # Annotations voted against or tie, saved only as keyword
        if "keyword" == key:
          keywords.append(value)
        # Annotation voted for, added as unit fact
        else:
          factName = "annotation_" + str(key)
          unitFacts.append({ "fact": factName, "value": str(value)})

        # Annotations with native values in DW:
        # TODO: test
        if "lifeStage" == key:
          unit['lifeStage'] = value
        elif "sex" == key:
          unit['sex'] = value



    # Quality metrics
    qualityMetricUnreliable = False
    if "quality_metrics" in inat:
      qualityMetricsSummary = summarizeQualityMetrics(inat["quality_metrics"])

      for metric, value in qualityMetricsSummary.items():
        # Add to facts
        metricName = "quality_metrics_" + metric
        unitFacts.append({ "fact": metricName, "value": str(value)})

        # If at least one negative quality metric, mark as unreliable. Exception: non-wilds are handled elsewhere.
        if "wild" != metric:
          if value < 0:
            qualityMetricUnreliable = True


    # Quality on DW

    # TODO: Refactor and test
    # Negative quality metrics (thumbs down) 
    # TODO: Check: does this make issue, or mark as unreliable, or both on Laji.fi?
    if qualityMetricUnreliable:
      unit['sourceTags'].append("EXPERT_TAG_UNCERTAIN")
      keywords.append("quality-metric-unreliable")


    # Flags
    # TODO: Has not been tested!
    if inat["flags"]:
      unit['sourceTags'].append("EXPERT_TAG_UNCERTAIN")
      keywords.append("flagged")
      gathering['notes'] = gathering['notes'] + "\n\[Observation flagged on iNaturalist as problematic or duplicate.]"

    # TODO: Has not been tested!
    if inat["spam"]:
      unit['sourceTags'].append("ADMIN_MARKED_SPAM")
      keywords.append("spam-observation")

    # TODO: Has not been tested!
    if inat["user"]["spam"]:
      unit['sourceTags'].append("ADMIN_MARKED_SPAM")
      keywords.append("spam-user")

    # TODO: Maybe hide obs from suspended users?
#    if inat["user"]["suspended"]:



    # Quality grade
    unitFacts.append({ "fact": "quality_grade", "value": inat['quality_grade'] + "_grade"})
    keywords.append(inat['quality_grade'] + "_grade")


    # Quality tags
    if "research" == inat['quality_grade']:
      unit['sourceTags'].append("COMMUNITY_TAG_VERIFIED")


    # Misc facts
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "out_of_range")
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "taxon_geoprivacy")
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "geoprivacy")
#    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "context_geoprivacy") # not used anymore?
#    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "context_user_geoprivacy") # not used anymore?
#    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "context_taxon_geoprivacy") # not used anymore?
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "comments_count")
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "num_identification_agreements")
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "num_identification_disagreements")
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "owners_identification_from_vision")
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "oauth_application_id")
    unitFacts = inatHelpers.appendRootFact(unitFacts, inat, "identifications_count")


    # Misc keywords
    keywords = appendKeyword(keywords, inat, "out_of_range")
    keywords = appendKeyword(keywords, inat, "identifications_most_agree")
    keywords = appendKeyword(keywords, inat, "identifications_most_disagree")
    keywords = appendKeyword(keywords, inat, "owners_identification_from_vision")


    # Faves
    if inat["faves_count"] >= 1:
      keywords.append("faved")

    if inat["faves_count"] >= 5:
      keywords.append("many_faved")
    elif inat["faves_count"] >= 3:
      keywords.append("few_faved")


    # Application used to save the obs
    if not inat["oauth_application_id"]:
      inat["oauth_application_id"] = 999 # Fake value for web client

    keywords.append("oauth_" + str(inat["oauth_application_id"]))


    # Coordinates
    # TODO: test with obs without coord
    if inat['mappable']:
      gathering['coordinates'] = inatHelpers.getCoordinates(inat)


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

    # Store last converted observation
    lastUpdateKey = inat["id"]

    print("Converted obs " + str(inat["id"]))


  # End for each observations

  # Root elements for DW
  dwRoot = {}
  dwRoot["schema"] = "laji-etl"
  dwRoot["roots"] = dwObservations

  return dwRoot, lastUpdateKey