# Airline IATA and ICAO codes

Python script that parses airline IATA and ICAO codes from a website and writes a JSON file.

I was working on a project and needed the list of all current airline's IATA and ICAO codes.
I failed to find one complete resource so I built one.

This script parses information from the following website: http://www.avcodes.co.uk/airlcodesearch.asp

It parses the list of all countries from the main page(button options) and then uses that list to request all airlines for each of the countries.

The webpage does not have specific URLs for each of the countries so the only way was to generate and submit POST requests to get info.

The HTML tags of the website does not have proper id's or classes, so I use detector texts to find out if I encountered useful info or not.
Currently I parse the name, full name, IATA and ICAO codes.
If you want some additional information, look at the HTML code and find out what detector would detect that info you need and add it to the config.py detector's list.
