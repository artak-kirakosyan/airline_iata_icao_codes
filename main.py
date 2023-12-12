import datetime
import json
import logging
import re

import requests
from bs4 import BeautifulSoup

import config as config


def get_country_list():
    try:
        resp = requests.get(config.countries_url)
    except Exception as e:
        raise ValueError(f"Failed to make the request: {e}")
    if not resp.ok:
        raise ValueError(f"Response has error code:{resp.status_code}")

    try:
        soup = BeautifulSoup(resp.text, 'lxml')
    except Exception as e:
        raise ValueError(f"Something wrong in the response text: {e}")

    country_options = soup.find("select", attrs={"name": "country"})
    countries = []
    if country_options is None:
        logging.warning("No countries were identified.")
        return countries
    # Parse country names from the option tags
    for country in country_options.find_all("option"):
        country_name = country.text.strip("\n\r\t ")
        if country_name != "":
            countries.append(country_name)

    return countries


def parse_all_countries(countries):
    for country in countries:
        logging.info(f"Trying to parse {country}")
        try:
            country_info = parse_country(country)
            logging.info(f"{country} has been parsed.")
        except ValueError as e:
            logging.exception(f"Failed to parse {country}: {e}")
            country_info = None
        yield country, country_info


def parse_country(country):
    """
        Take country name and parse the airlines of the current country.
        Args:
            country: country name
        Returns:
            airlines: list of airlines for current country
        
        If any error occurred while making the request or parsing html code,
        a ValueError is being risen.
    """
    soup = get_country_soup(country)

    airlines = []
    for index, main_tag in enumerate(soup.findAll("main"), 1):
        airline_info = {}
        text = main_tag.text
        airline_name_match = re.search(r'Full Name:\s*(.*?)\n', text)
        if not airline_name_match:
            logging.warning("No name found in position %s for %s", index, country)
            continue
        name = airline_name_match.group(1).strip()
        if name == "":
            logging.warning("Name is empty in position %s for %s", index, country)
            continue
        airline_info['name'] = name
        iata_match = re.search(r'IATA Code:\s*(\w*?)\n', text)
        iata = None
        if iata_match:
            iata = iata_match.group(1).strip()
            if iata == "":
                iata = None
        airline_info['IATA'] = iata
        icao = None
        icao_match = re.search(r'ICAO Code:\s*(\w*?)\n', text)
        if icao_match:
            icao = icao_match.group(1).strip()
            if icao == "":
                icao = None
        airline_info['ICAO'] = icao
        website = None
        website_match = re.search(r"Website URL(.*?)\n", text)
        if website_match:
            website = website_match.group(1).strip()
            if website == "":
                website = None
        airline_info["website"] = website
        notes = None
        remarks_match = re.search(r'Remarks / Notes:\s*(.*?)\n', text)
        if remarks_match:
            notes = remarks_match.group(1).strip()
            if notes == "":
                notes = None
        airline_info['notes'] = notes
        data_status_match = re.search(r'This is Current Data', text)
        airline_info['is_up_to_date'] = data_status_match is not None

        airline_info['parsed'] = str(datetime.datetime.now())
        airlines.append(airline_info)

    return airlines


def get_country_soup(country):
    data = config.data.copy()
    data["country"] = country
    try:
        resp = requests.post(
            config.url,
            data=data,
            headers=config.headers,
        )
    except Exception as e:
        raise ValueError(f"Failed to make the request: {e}")
    if not resp.ok:
        raise ValueError(f"Response has error code:{resp.status_code}")
    try:
        soup = BeautifulSoup(resp.text, 'lxml')
    except Exception as e:
        raise ValueError(f"Something wrong in the response text: {e}")
    return soup


def main():
    countries = get_country_list()
    results = {}
    for country, country_data in parse_all_countries(countries):
        results[country] = country_data
        if country_data is None:
            logging.warning(f"No data found for {country}")
            continue
        country_name = country.replace(" ", "_")
        country_name = country_name.replace("/", "_")
        try:
            with open(f"{config.base_directory}/{country_name}.json", "w") as f:
                json.dump(country_data, f, indent=2)
        except Exception as e:
            logging.exception(f"Failed to write {country} data: {e}")
            continue
    with open(config.target_file_name, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
