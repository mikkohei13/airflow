<?php

// Converts one iNat observation to DW format


function observationInat2Dw($inat) {


  /*

  Ask iNat:
  - How to have FinBIF here: This observation is featured on 1 site

  */


  // Coordinates
  if ($inat['mappable']) {
    $dw['publicDocument']['gatherings'][0]['coordinates']['type'] = "WGS84";


    // TODO: observation without coordinates

    // Obscured observation
    if (TRUE === $inat['obscured']) { // Alternative: ("obscured" == geoprivacy || "obscured" = taxon_geoprivacy)
      // Bounding box coordinates
      $lon = substr(removeNullFalse($inat['geojson']['coordinates'][0]), 0, 4);
      $lat = substr(removeNullFalse($inat['geojson']['coordinates'][1]), 0, 4);
//      echo "LON:" . $lon;

      // Conservative bounding box calculation: this is less accurate than the box shown on the iNat website, but the true location is definitely inside this box.
      // Todo: Find out how the bounding box on iNat observation page is calculated - how do they know which 0.2x0.2 square to draw? It's not on the API.
      $dw['publicDocument']['gatherings'][0]['coordinates']['lonMin'] = $lon - 0.1;
      $dw['publicDocument']['gatherings'][0]['coordinates']['lonMax'] = $lon + 0.2;
      $dw['publicDocument']['gatherings'][0]['coordinates']['latMin'] = $lat - 0.1;
      $dw['publicDocument']['gatherings'][0]['coordinates']['latMax'] = $lat + 0.2;  

      $dw['publicDocument']['gatherings'][0]['coordinates']['accuracyInMeters'] = 0;
    }

    // Non-obscured observation
    else {
      if (empty($inat['positional_accuracy'])) {
        $accuracy = 100; // Default for missing values. Mobile app often misses the value, even if the coordinates are accurate.
      }
      elseif ($inat['positional_accuracy'] < 10) {
        $accuracy = 5; // Minimum value
      }
      else {
        $accuracy = round($inat['positional_accuracy'], 0); // Round to one meter
      }
      $dw['publicDocument']['gatherings'][0]['coordinates']['accuracyInMeters'] = $accuracy;

      // Point coordinates
      // Rounding, see https://gis.stackexchange.com/questions/8650/measuring-accuracy-of-latitude-and-longitude/8674#8674
      $lon = round(removeNullFalse($inat['geojson']['coordinates'][0]), 6);
      $lat = round(removeNullFalse($inat['geojson']['coordinates'][1]), 6);

      $dw['publicDocument']['gatherings'][0]['coordinates']['lonMin'] = $lon;
      $dw['publicDocument']['gatherings'][0]['coordinates']['lonMax'] = $lon;
      $dw['publicDocument']['gatherings'][0]['coordinates']['latMin'] = $lat;
      $dw['publicDocument']['gatherings'][0]['coordinates']['latMax'] = $lat;  
    }

  }


  // Photos
  $photoCount = count($inat['observation_photos']);
  if ($photoCount >= 1) {
    array_push($keywordsArr, "has_images"); // not needed if we use media object
    foreach ($inat['observation_photos'] as $photoNro => $photo) {
      
      // Facts
      $factsArr = factsArrayPush($factsArr, "U", "imageId", $photo['photo']['id']); // Photo id
      $factsArr = factsArrayPush($factsArr, "U", "imageUrl", "https://www.inaturalist.org/photos/" . $photo['photo']['id']); // Photo link

      // CC-licensed photos via proxy
      if (!empty($photo['photo']['license_code'])) {
        $squareUrl = $photo['photo']['url'];

        $thumbnailUrl = str_replace("square", "small", $squareUrl);
        $thumbnailUrl = str_replace("https://static.inaturalist.org/photos/", "https://proxy.laji.fi/inaturalist/photos/", $thumbnailUrl); // TODO: refactor into helper

        $fullUrl = str_replace("square", "original", $squareUrl);
        $fullUrl = str_replace("https://static.inaturalist.org/photos/", "https://proxy.laji.fi/inaturalist/photos/", $fullUrl); // TODO: refactor

        $media = Array();

        $media['thumbnailURL'] = $thumbnailUrl;
        $media['copyrightOwner'] = $photo['photo']['attribution'];
        $media['author'] = $photo['photo']['attribution']; // TODO: or simply observer name
        $media['fullURL'] = $fullUrl;
        $media['licenseId'] = getLicenseUrl($photo['photo']['license_code']);
        $media['mediaType'] = "IMAGE";

        $dw['publicDocument']['gatherings'][0]['units'][0]['media'][] = $media;
      }
      else {
        array_push($keywordsArr, "image_arr"); // keyword for all rights reserved -images. Will be given if at least one photo is missing license.
      }

    }
    $factsArr = factsArrayPush($factsArr, "U", "imageCount", $photoCount);
  }

  // Sounds
  // Note: if audio is linked via proxy, need to check that cc-license is given 
  $soundCount = count($inat['sounds']);
  if ($soundCount >= 1) {
    array_push($keywordsArr, "has_audio"); // not needed if we use media object
    foreach ($inat['sounds'] as $soundNro => $sound) {
      $factsArr = factsArrayPush($factsArr, "U", "audioId", $sound['id']); // Sound id
      $factsArr = factsArrayPush($factsArr, "U", "audioUrl", $sound['file_url']); // Sound link
    }
    $factsArr = factsArrayPush($factsArr, "U", "audioCount", $soundCount);
  }

  if (FALSE == $soundCount && FALSE == $photoCount) {
    array_push($keywordsArr, "no_media"); // To search for obs which cannot be verified
  }


  // Record basis
  if (hasSpecimen($inat['ofvs'])) {
    $dw['publicDocument']['gatherings'][0]['units'][0]['recordBasis'] = "PRESERVED_SPECIMEN";
  }
  elseif ($photoCount >= 1) {
    $dw['publicDocument']['gatherings'][0]['units'][0]['recordBasis'] = "HUMAN_OBSERVATION_PHOTO";
  }
  elseif ($soundCount >= 1) {
    $dw['publicDocument']['gatherings'][0]['units'][0]['recordBasis'] = "HUMAN_OBSERVATION_RECORDED_AUDIO";
  }
  else {
    $dw['publicDocument']['gatherings'][0]['units'][0]['recordBasis'] = "HUMAN_OBSERVATION_UNSPECIFIED";
  }



  // Annotations
  if (!empty($inat['annotations'])) {
    foreach ($inat['annotations'] as $annotationNro => $annotation) {
      $anno = handleAnnotation($annotation);
      $factsArr = factsArrayPush($factsArr, "U", $anno['attribute'], $anno['value']);
      
      if (isset($anno['dwLifeStage'])) {
        $dw['publicDocument']['gatherings'][0]['units'][0]['lifeStage'] = $anno['dwLifeStage'];
      }
      if (isset($anno['dwSex'])) {
        $dw['publicDocument']['gatherings'][0]['units'][0]['sex'] = $anno['dwSex'];
      }
    }
  }


  // Taxon
  // scientific name iNat interprets this to be, special cases converted by this script to match FinBIF taxonomy
  $dw['publicDocument']['gatherings'][0]['units'][0]['taxonVerbatim'] = handleTaxon($inat['taxon']['name']);

  // name observer or identifiers(?) have given, can be any language
  $factsArr = factsArrayPush($factsArr, "U", "taxonByUser", handleTaxon($inat['species_guess']));

  // scientific name iNat interprets this to be
  $factsArr = factsArrayPush($factsArr, "U", "taxonInterpretationByiNaturalist", $inat['taxon']['name']);


  // ----------------------------------------------------------------------------------------


  log2("NOTICE", "Converted obs\t" . $inat['id'] . " of " . $inat['taxon']['name'] . " observed " . $inat['observed_on_details']['date'] . " updated " . $inat['updated_at'], "log/inat-obs-log.log");
//  echo "handled ".$inat['id']."\n"; // debug


  return $dw;
}
