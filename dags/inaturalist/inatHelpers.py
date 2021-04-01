
import math

"""
def appendFact(factsList, factLabel, factValue = False):
  if factValue: # Checks if value is truthy
    factsList.append({ "fact": factLabel, "value": factValue })

  return factsList
"""

def appendRootFact(factsList, inat, factName):
  # Handles only keys directly under root of inat

  if factName in inat: # Checks if key exists
    if inat[factName]: # Checks if value is truthy
      factsList.append({ "fact": factName, "value": inat[factName]} )

  return factsList


def decimalFloor(n, decimals=1):
  multiplier = 10 ** decimals
  return str(math.floor(n * multiplier) / multiplier)


def getCoordinates(inat):

  coord = {}
  coord['type'] = "WGS84";

  # TODO: observation without coordinates

  # Obscured observation
  if inat['obscured']: # Alternative: ("obscured" == geoprivacy || "obscured" = taxon_geoprivacy)
    
    # Creates a 0.2*0.2 degree box around the observation, so that corner first decimal digit is even-numbered.

    lonRaw = inat['geojson']['coordinates'][0]
    lonFirstDigit = int(str(lonRaw).split('.')[1][0])
    if lonFirstDigit % 2 == 0: # even
      coord['lonMin'] = decimalFloor(lonRaw)
      coord['lonMax'] = decimalFloor((lonRaw + 0.2))
    else:
      coord['lonMin'] = decimalFloor((lonRaw - 0.1))
      coord['lonMax'] = decimalFloor((lonRaw + 0.1))

    latRaw = inat['geojson']['coordinates'][1]
    latFirstDigit = int(str(latRaw).split('.')[1][0])
    if latFirstDigit % 2 == 0: # even
      coord['latMin'] = decimalFloor(latRaw)
      coord['latMax'] = decimalFloor((latRaw + 0.2))
    else:
      coord['latMin'] = decimalFloor((latRaw - 0.1))
      coord['latMax'] = decimalFloor((latRaw + 0.1))

#    coord['accuracyInMeters'] = "" # Accuracy not set for obscured obs, since DW calculates it by itself from bounding box

  # Non-obscured observation
  else:
    lon = round(inat['geojson']['coordinates'][0], 5)
    lat = round(inat['geojson']['coordinates'][1], 5)

    if not inat['positional_accuracy']:
      accuracy = 100; # Default for missing values. Mobile app often leaves the value empty, even if the coordinates are accurate.
    elif inat['positional_accuracy'] < 10:
      accuracy = 10 # Minimum value
    else:
      accuracy = round(inat['positional_accuracy'], 0) # Round to one meter

    coord['accuracyInMeters'] = accuracy

    coord['lonMin'] = lon;
    coord['lonMax'] = lon;
    coord['latMin'] = lat;
    coord['latMax'] = lat;  

  return coord


def convertTaxon(taxon):
  convert = {}

  convert['Life'] = "Biota"
  convert['unknown'] = "Biota"
  convert['Elämä'] = "Biota" # Is this needed?
  convert['tuntematon'] = "Biota" # Is this needed?

  convert['Taraxacum officinale'] = "Taraxacum"
  convert['Alchemilla vulgaris'] = "Alchemilla"
  convert['Pteridium aquilinum'] = "Pteridium pinetorum"
  convert['Ranunculus auricomus'] = "Ranunculus auricomus -ryhmä s. lat."
  convert['Bombus lucorum-complex'] = "Bombus lucorum coll."
  convert['Chrysoperla carnea-group'] = "Chrysoperla"
  convert['Potentilla argentea'] = "Potentilla argentea -ryhmä"
  convert['Chenopodium album'] = "Chenopodium album -ryhmä"
  convert['Imparidentia'] = "Heterodonta" # hieta- ja liejusimpukan alin yhteinen taksoni
  convert['Canis familiaris'] = "Canis lupus familiaris" # koira

  if not taxon: # Empty, False, Null/None
    return ""  
  elif taxon in convert:
    return convert[taxon]
  else:
    return taxon


def summarizeAnnotation(annotation):
  """
  Annotations describe three attributes (see them below.)

  The logic is complicated, and there's no official documentation about it.
  - Someone creates an observation.
  - Someone creates an annotation for an attribute.
  - Someone adds a value to that attribute.
  - Anyone can vote for or agains that value, but cannot create a competing value.

  In the API, vote_score shows the outcome of the voting. positive=agree, 0=tie, negative=disagree

  Attributes (= keys):
  1=Life Stage, 9=Sex, 12=Plant Phenology, 17=Live or dead

  Values:
  Life Stage: 2=Adult, 3=Teneral, 4=Pupa, 5=Nymph, 6=Larva, 7=Egg, 8=Juvenile, 16=Subimago
  Sex: 10=Female, 11=Male
  Plant Phenology: 13=Flowering, 14=Fruiting, 15=Budding
  Live or dead: 18=Live, 19=Dead, 20=Cannot be identified

  See in main conversion script how the result is submitted to DW.

  See more at https://forum.inaturalist.org/t/how-to-use-inaturalists-search-urls-wiki/63
  """

  key = annotation["controlled_attribute_id"]
  value = annotation["controlled_value_id"]
  vote_score = annotation["vote_score"]

  if 2 == value:
    key = "lifeStage"
    value = "ADULT"
  elif 4 == value:
    key = "lifeStage"
    value = "PUPA"
  elif 5 == value:
    key = "lifeStage"
    value = "NYMPH"
  elif 6 == value:
    key = "lifeStage"
    value = "LARVA"
  elif 7 == value:
    key = "lifeStage"
    value = "EGG"
  elif 8 == value:
    key = "lifeStage"
    value = "JUVENILE"
  elif 16 == value:
    key = "lifeStage"
    value = "SUBIMAGO"
  elif 13 == value:
    key = "lifeStage"
    value = "FLOWER"
  elif 10 == value:
    key = "sex"
    value = "FEMALE"
  elif 11 == value:
    key = "sex"
    value = "MALE"
  else:
    pass


  if vote_score >= 1:
    return key, value

  elif vote_score <= -1:
#    print("Annotation " + str(key) + " = " + str(value) + " was voted against by " + str(vote_score))
    return "keyword", "annotation_against"

  elif 0 == vote_score:
#    print("Annotation " + str(key) + " = " + str(value) + " vote tied")
    return "keyword", "annotation_tie"


def getProxyUrl(squareUrl, imageSize):
  url = squareUrl.replace("square", imageSize)

  # TODO: User full URL when CC-images moved to free bucket 
  return url

  '''
  # Rudimentatry test that URL is expected.
  # TODO: Test for changes in the URL's
  if not url.startswith("https://inaturalist-open-data.s3.amazonaws.com/photos/"):
    print("Skipping image with unexpected url ", url)
    return ""

  splitUrl = url.split("/photos/")
  proxyUrl = "https://proxy.laji.fi/inaturalist/photos/" + splitUrl[1]
#  print(proxyUrl)

#  url = url.replace("https://static.inaturalist.org/photos/", "https://proxy.laji.fi/inaturalist/photos/")

  return proxyUrl
  '''


