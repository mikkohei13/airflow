
import math


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
      print("lon odd")
      coord['lonMin'] = decimalFloor((lonRaw - 0.1))
      coord['lonMax'] = decimalFloor((lonRaw + 0.1))
      print("lonMin: " + str(coord['lonMin']))

    latRaw = inat['geojson']['coordinates'][1]
    latFirstDigit = int(str(latRaw).split('.')[1][0])
    if latFirstDigit % 2 == 0: # even
      coord['latMin'] = decimalFloor(latRaw)
      coord['latMax'] = decimalFloor((latRaw + 0.2))
    else:
      coord['latMin'] = decimalFloor((latRaw - 0.1))
      coord['latMax'] = decimalFloor((latRaw + 0.1))

    coord['accuracyInMeters'] = "" # This changed compared to PHP version

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
  return taxon
