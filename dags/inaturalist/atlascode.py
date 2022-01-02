
testString = "oli kiva lintu lorem ipsum ÅÄÖåäö¤&#35#432$£@$atl:820fsdvds"

numbers = ["0","1","2","3","4","5","6","7","8","9"]

# to lowercase
testString = testString.lower()
print("Test string: " + testString)

try:
    index = testString.index("atl:")
except ValueError:
    print("Not found alt:")
else:
#    print("Found: " + str(index))
    start = index + 4
    end = start + 2
    atlasCode = testString[start:end]

    # If code length is 2, and if trailing char is not a number, remove it 
    if len(atlasCode) == 2:
        trailingChar = atlasCode[1:2]
        if not trailingChar in numbers:
            print("trail nan: " + trailingChar)
            atlasCode = atlasCode[0:1]

    # If  char after atlascode is number, it's probably an error
    charAfterAtlasCode = testString[end:(end + 1)]
    if charAfterAtlasCode in numbers:
        print("Char after atlascode is number: " + charAfterAtlasCode)

# Remove trailing zero
atlasCode = atlasCode.strip("0")

allowedAtlasCodes = ["1","2","3","4","5","6","7","8","61","62","63","64","65","66","71","72","73","74","75","81","82"]


if atlasCode in allowedAtlasCodes:
    print("Found allowed code: " + str(atlasCode))
else:
    print("Not found allowed code")

