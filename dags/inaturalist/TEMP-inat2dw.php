<?php

// Converts one iNat observation to DW format


function observationInat2Dw($inat) {


  /*

  Ask iNat:
  - How to have FinBIF here: This observation is featured on 1 site

  */

  
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
