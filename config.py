# Headers and data are for making a request and getting proper result
headers = {
    "Host": "www.avcodes.co.uk",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.avcodes.co.uk",
    "Referer": "https://www.avcodes.co.uk/airlcodesearch.asp",
    "Upgrade-Insecure-Requests": "1",
}

data = {
    'iataairl': '',
    'icaoairl': '',
    'account': '',
    'prefix': '',
    'airlname': '',
    'country': 'country_name',
    'callsign': '',
    'B1': '',
}
# First url is for getting the list of current countries
countries_url = "https://www.avcodes.co.uk/airlcodesearch.asp"
# This link is where we get all airline information
url = "https://www.avcodes.co.uk/airlcoderes.asp"

# A file name where to write the info
target_file_name = "airline_iata_icao_codes.json"
