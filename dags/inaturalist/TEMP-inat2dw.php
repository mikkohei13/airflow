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
