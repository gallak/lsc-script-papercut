// DEST
//supannCMSId;x-desfire-xlsb 	00000EtDVb0hAPeB
//supannCMSIdEtiquette 	{DESFIRE:XLSB}00000EtDVb0hAPeB
//supannCMSAffectation 	[type=personnel][format=DESFIRE:XLSB][id=00000EtDVb0hAPeB][valide=vrai]


function extractTag(cardTag){
  var prefixPapercut = {
    "MIFARE"  : "r007f0120",
    "DESFIRE" : "r007f0138"
  };

  prefix = cardTag.substring(0,9)

  switch(prefix){
    case prefixPapercut.MIFARE : 
        tag = "MIFARE:00000000" + cardTag.slice(-2) +cardTag.slice(-4,-2)+ cardTag.slice(-6,-4) + cardTag.slice(-8,-6);
      break;
    case prefixPapercut.DESFIRE :
        tag = "DESFIRE:000"+cardTag.substring(10,24);
      break;
  }

return(tag);
}



//function extractType(cardTag){
//        return(extractTag(cardTag).split(":")[0]);
//}


function setSupannCMSId(cardTag,type){
	tagArray=extractTag(cardTag).split(":");
        if (type == tagArray[0]){
		return(tagArray[1]);
	}else{
		return;
	}
}

function setSupannCMSIdEtiquette(cardTag){
        tagArray=extractTag(cardTag).split(":");
	return("{"+tagArray[0]+":XLSB}"+tagArray[1]);
}


function setSupannCMSAffectation(cardTag){
        tagArray=extractTag(cardTag).split(":");
        return("[type=personnel][format="+tagArray[0]+":XLSB][id="+tagArray[1]+"][valide=vrai]");
}







// Functyion use to tranforms some RFID Tag stored inside LDAP Supannized Tree
// Antoine Gallavardin (antoine.gallavardin@free.fr)

function transformId2PCId(cardTag,cardFormat,cardValidity){
  // prefix table is empirique keys should correspond to label inside LDAP tree : label of SupannCMSFormats
  var prefixPapercut = {
    "MIFARE"  : "r007f0120",
    "DESFIRE" : "r007f0138"
  };
  var tagLength = 16;

  if ( cardValidity == "vrai" ) {
    if (cardTag.length == tagLength){
      cardType     = cardFormat.split(":")[0];
      cardEncoding = cardFormat.split(":")[1];  // not used yet
      lowerTag = cardTag.slice(-14); 	        // last 14 digits : Magic Number that is what I observered

      if (cardType == "UNKNOWN") {  // try to detect Tag type
        if (lowerTag.slice(0,6) == "000000") {
          cardType="MIFARE";
        }else{
          cardType="DESFIRE";
        }
      }

      switch(cardType) {
        case "MIFARE" : 
          PCTag=prefixPapercut.MIFARE +lowerTag.slice(-2) + lowerTag.slice(-4,-2) + lowerTag.slice(-6,-4) + lowerTag.slice(-8,-6);
          break;
        case "DESFIRE" : 
          PCTag=prefixPapercut.DESFIRE + lowerTag;
          break;
      }
      return PCTag.toLowerCase();
    }
    return "BAD_TAG_LENGTH :" + cardTag.length
  }
  return ""
}


// [type=etudiant][format=MIFARE:XLSB][id=00000000DFDE3445][valide=vrai]
// see : https://services.renater.fr/documentation/supann/supann2020/recommandations2020/attributs/supanncmsaffectation
// coulb used if There is only one Card : check if https://services.renater.fr/documentation/supann/supann2020/recommandations2020/attributs/supannCMSAppAffectation isn't a better option
function extractPCId(supannCMSAffectation) {
  var compositeSeparator = new RegExp("\\[|\\]");

  if ( supannCMSAffectation ){
    CMSArray 	= supannCMSAffectation.split(compositeSeparator) ;
    isValidId	= CMSArray[7].split("=")[1]; //vrai
    idValue     = CMSArray[5].split("=")[1]; //0000000DFDE3445
    idFormat	= CMSArray[3].split("=")[1]; //MIFARE:XLSB
    return transformId2PCId(idValue,idFormat,isValidId)
  }else{
    return ""
  }

}

// if Tag is extract from supannCMSAppAffectation
// example [type=etudiant][source=izly@universite.fr][domaine=PAPERCUT][id=00000000D43E735A][valide=vrai]
function extractPCIdPerApp(supannCMSAppAffectations,domainId) {
  var compositeSeparator = new RegExp("\\[|\\]");
  var tagLength = 16;
  if (supannCMSAppAffectations) {
    for (i = 0; i < supannCMSAppAffectations.length; i++) {
      domain = supannCMSAppAffectations[i].split(compositeSeparator)[5].split("=")[1];
      if (domain = domainId) {
        isValidId   = supannCMSAppAffectations[i].split(compositeSeparator)[9].split("=")[1]; //vrai
        idValue     = supannCMSAppAffectations[i].split(compositeSeparator)[7].split("=")[1]; //0000000D43E3445
        idFormat    = "UNKNOWN:UNKNOWN";
        return transformId2PCId(idValue,idFormat,isValidId)
      }
    }
  }
  return ""
}

