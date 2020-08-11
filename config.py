# Headers and data are for making a request and getting proper result
headers = {
"Host": "www.avcodes.co.uk",
"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
"Content-Type": "application/x-www-form-urlencoded",
"Content-Length": "86",
"Origin": "http://www.avcodes.co.uk",
"Referer": "http://www.avcodes.co.uk/airlcodesearch.asp",
"Upgrade-Insecure-Requests": "1",
}

data = {
"status": "Y",
"iataairl": "",
"icaoairl": "",
"account": "",
"prefix": "",
"airlname": "",
"country": "country_name",
"callsign": "",
"B1": "",
}

# First url is for getting the list of current countries
countries_url = "http://www.avcodes.co.uk/airlcodesearch.asp"
# This link is where we get all airline information
url = "http://www.avcodes.co.uk/airlcoderes.asp"

# These detectors are to identifies the rows in the html code where
# iata, icao or full name of the airline is written
# you can update this list to parse more information such as website or iata
# itentifiers
detectors = {
        "iata": "IATA Code:\xa0",
        "icao": "ICAO Code:\xa0",
        "full_name": "Full Name:",
        }
# A file name where to write the info
target_file_name = "airline_iata_icao_codes.json"

# Set write_to_mongo to True to write to mongodb
write_to_mongo = False
# Mongodb connection uri
mongo_connection_uri = "your_connection_url"
# The DB and collection names in MongoDB
mongo_db_name = "db name"
mongo_collection_name = "colleciton name"

