<?php

// Converts one iNat observation to DW format


function observationInat2Dw($inat) {


  /*

  Ask iNat:
  - How to have FinBIF here: This observation is featured on 1 site

  */



  // ----------------------------------------------------------------------------------------


  log2("NOTICE", "Converted obs\t" . $inat['id'] . " of " . $inat['taxon']['name'] . " observed " . $inat['observed_on_details']['date'] . " updated " . $inat['updated_at'], "log/inat-obs-log.log");
//  echo "handled ".$inat['id']."\n"; // debug


  return $dw;
}
