#!/usr/bin/env python

try:
    import time
    import json
    
    from pymongo import MongoClient
    from pymongo import UpdateOne
    import requests
    from bs4 import BeautifulSoup

    
    import config as config
except ImportError as e:
    print(f'Error occured during import: {e}')
    print('Please install all necessary libraries and try again')
    exit(1)


def get_country_list():
    """
        This function uses the config file to parse the list of countries
        from the website and returns it

        Args:
            None
        Returns:
            countries: list of found countries

        If there is an error while making the request or parsing the soup,
            a ValueError is being rised with proper message.
        If no countries found, returning empty list.
    """
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
        print("No countries were identified.")
        return countries
    # Parse country names from the option tags
    for country in country_options.find_all("option"):
        country_name = country.text.strip("\n\r\t ")
        if country_name != "":
            countries.append(country_name)

    return countries


def scrape_all_countries(countries):
    """
        Take the list of all countries 
            and parse all airlines from all countries.
        Args:
            countries: list of countries
        Return:
            airlines_data: dictionary {country: [list of airlines]} format
        If an error occures while parsing any of the countries, we skip over.
    """


    airlines_data = {}
    data = config.data.copy()
    headers= config.headers
    url = config.url

    for country in countries:
        data["country"] = country
        print(f"Trying to parse {country}")
        try:
            country_info = parse_country(url, data, headers)
            airlines_data[country] = country_info
            print(f"{country} has been parsed.")
        except ValueError as e:
            print(f"Failed to parse {country}, skipping: {e}")
        
    return airlines_data


def parse_country(url, data, headers):
    """
        Take the url, the data and headers and parse the airlines of the current
        country.
        Args:
            url: string representation of the url
            data: dictionary with necessary info to make the request
            headers: headers of the request
        Returns:
            airlines: list of airlines for current country
        
        If any error occures while making the request or parsing html code,
        a ValueError is being rised.
    """
    try:
        resp = requests.post(
                url,
                data=data,
                headers=headers,
                )
    except Exception as e:
        raise ValueError(f"Failed to make the request: {e}")

    if not resp.ok:
        raise ValueError(f"Response has error code:{resp.status_code}")

    try:
        soup = BeautifulSoup(resp.text, 'lxml')
    except Exception as e:
        raise ValueError(f"Something wrong in the response text: {e}")

    airlines = []
    for item in soup.findAll("div"):
        current_airline = {}
        # check if the current div is a proper airline record
        if item.p is None:
            continue
        if item.p.text != "Current Record":
            continue
        # Find the name of the airline
        current_airline["name"] = item.td.text
        # Iterate over td tags and try to detect info
        for curr_row in item.table.findAll("td"):
            # For each td, iterate over detectors and try to match it
            for detector_name, detector in config.detectors.items():
                # If detector matches, scrap and strip the info and save
                if curr_row.text.startswith(detector):
                    current_airline[detector_name] = curr_row.text[len(detector):].strip("* ")
                    # If parsed info is empty, set it to None
                    if current_airline[detector_name] == "":
                        current_airline[detector_name] = None
        airlines.append(current_airline)

    return airlines


def write_to_a_file(data, file_path=None):
    """
        Take the data and file path and write json to that file
        Arguments:
            data: any JSON serializable data
            file_path: a file path where to write(optional)
        Returns:
            None
    """
    if file_path is None:
        try:
            file_name = config.target_file_name
        except KeyError as e:
            print("File name missing from config file")
            print("Using default file name format.")
            file_name = "results_" + str(int(time.time())) + ".json"
    else:
        file_name = file_path
    with open(file_name, "w") as f:
        json.dump(data, f, indent=2)


def organize_and_upsert(airlines, collection):
    """
        Take the airlines info, reorganize and insert into mongodb.
        
        Arguments:
            airlines: dictionary of airlines {country:[list of airlines]}
            colleciton: Mongodb colleciton object
        Returns:
            None
    """
    updates = []
    curr_doc_count = 0
    docs = []
    for country, country_airlines in airlines.items():
        for airline in country_airlines:
            airline["country"] = country
            # Id of the airline is the concatination of the contry and full_name
            airline["_id"] = airline["country"] + "_" + airline["full_name"]
            docs.append(airline)
            curr_update = UpdateOne(
                    {"_id": airline["_id"]},
                    {"$set": airline},
                    upsert=True,
                    )
            updates.append(curr_update)
            curr_doc_count += 1
        # If more than 1000 updates created, write to the db
        if curr_doc_count > 1000:
            write_resp = collection.bulk_write(updates)
            if write_resp.acknowledged:
                print(f"Upserted {write_resp.upserted_count} out of {len(updates)}.")
                updates = []
                curr_doc_count = 0
            else:
                print(f"Bulk write operation didnt acknowledge: {updates}")
    
    # If still updates remaining
    if updates:
        write_resp = collection.bulk_write(updates)
        if write_resp.acknowledged:
            print(f"Upserted {write_resp.upserted_count} out of {len(updates)}.")
            updates = []
            curr_doc_count = 0
        else:
            print(f"Bulk write operation didnt acknowledge: {updates}")
    if updates:
        print("Some updates didnt get written to the DB: {len(updates)}")


def setup_mongo():
    """
        Use info from config to create mongodb colleciton and return it
        Arguments:
            None
        Returns:
            collection: MongoDB collection object
    """
    mongo_client = MongoClient(config.mongo_connection_uri)
    db = mongo_client[config.mongo_db_name]
    collection = db[config.mongo_collection_name]
    return collection


def main():
    try:
        countries = get_country_list()
    except ValueError as e:
        print(f"Something went wrong: {e}")
        exit(1)
    try:
        airlines = scrape_all_countries(countries)
    except ValueError as e:
        print(f"Something went wrong: {e}")
        exit(1)
    
    write_to_a_file(airlines)

    # If you want to enable mongo writing, update the config file.
    if config.write_to_mongo:
        collection = setup_mongo()
        organize_and_upsert(airlines, collection)

if __name__ == "__main__":
    main()

