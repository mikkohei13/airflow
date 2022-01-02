
test = {
    "ATL:1": 1,
    "atl:65": 65,
    "atL:20    ": 2,
    " atl:75": 75,
    "foo bar atl:65": 65,
    "ATL:5foo": 5,
    "oli kiva lintu lorem ipsum lorem ipsum lorem ipsum lorem ipsum ÅÄÖåäö¤&#35#432$£@$atl:82fsdvds": 82,
    "atl:1atl:2": 1,
    "   atl:4, oli kiva lintu": 4,
    "atl:1.2": 1,
    "atl:7,2": 7,
    "atl:6e2": 6,
    "atl:650": 65, # Should this be allowed or not?
    "ATL:x atl:2": None,
    "atl;5": None,
    "atl:x3": None,
    "atl:83": None,
    "XXX:2": None,
    "atl: 1": None,
    "atl:-5": None,
     "": None,
}

def extractAtlasCode(text):
    numbers = ["0","1","2","3","4","5","6","7","8","9"]

    # to lowercase
    text = text.lower()
#    print("Test string: " + text)

    try:
        index = text.index("atl:")
    except ValueError:
#        print("Not found alt:")
        return None
    else:
    #    print("Found: " + str(index))
        start = index + 4
        end = start + 2
        atlasCode = text[start:end]

        # If code length is 2, and if trailing char is not a number, remove it 
        if len(atlasCode) == 2:
            trailingChar = atlasCode[1:2]
            if not trailingChar in numbers:
#                print("trail nan: " + trailingChar)
                atlasCode = atlasCode[0:1]

        # If  char after atlascode is number, it's probably an error
#        charAfterAtlasCode = text[end:(end + 1)]
#        if charAfterAtlasCode in numbers:
#            print("Char after atlascode is number: " + charAfterAtlasCode)

    # Remove trailing zero
    atlasCode = atlasCode.strip("0")

    allowedAtlasCodes = ["1","2","3","4","5","6","7","8","61","62","63","64","65","66","71","72","73","74","75","81","82"]

    if atlasCode in allowedAtlasCodes:
#        print("Found allowed code: " + atlasCode)
        return int(atlasCode)
    else:
#        print("Not found allowed code")
        return None


for k, v in test.items():
    atlasCode = extractAtlasCode(k)
    if atlasCode == v:
        print("PASS: " + k + ", expected " + str(v) + " got " + str(atlasCode))
    else:
        print("-------> fail: " + k + ", expected " + str(v) + " got " + str(atlasCode))