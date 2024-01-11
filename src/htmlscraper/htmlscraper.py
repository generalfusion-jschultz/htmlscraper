#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Jason Schultz
# Created Date: 2024-01-10
# version ='1.0'
# ---------------------------------------------------------------------------
"""
Tools to assist with webscraping

Originally written by Matthew Davidson
"""
# ---------------------------------------------------------------------------
import requests
from bs4 import BeautifulSoup
import re
import logging
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)


class ScrapedData:
    def __init__(self, filepath:str):
        self.time_list = []
        self.data_list = []
        self.id_dict = {}
        
        with open(filepath, "r") as file:
            data = yaml.safe_load(file)
        for category, names in data.items():
            for name in names:
                self.id_dict.update({name: category})
    
    def get_id_keys_as_list(self):
        return list(self.id_dict.keys())
    
    def add_data_set(self, scraped_data:dict):
        self.data_list.append(scraped_data)
        self.time_list.append(datetime.now())

    def clear_data(self):
        self.time_list.clear()
        self.data_list.clear()


class GetRequestUnsuccessful(Exception):
    pass


def fetch_html_content(url):
    # Construct the URL with the given IP address and optional path
    try:
        # Make a GET request to the URL
        response = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        logger.warning("HTML GET request was unsuccessful", extra=dict(details=e))
        raise GetRequestUnsuccessful

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Return the HTML content if successful
        return response.text
    else:
        # Print an error message if the request fails and return None
        logger.warning(f"Failed to retrieve HTML. Status code: {response.status_code}")
        raise GetRequestUnsuccessful


def parse_html_content(html):
    # Parse the HTML content using BeautifulSoup
    return BeautifulSoup(html, "html.parser")


def extract_timestamp_from_strings(strings):
    # Define a regular expression pattern for the timestamp format
    timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    # Iterate through the strings to find a matching timestamp
    for string in strings:
        match = timestamp_pattern.search(string)
        if match:
            return match.group()

    # Return None if no timestamp is found
    return None


def scrape_timestamp_from_soup(soup):
    # Extract all strings within the soup
    all_strings = soup.stripped_strings

    # Attempt to extract timestamp from the strings
    timestamp = extract_timestamp_from_strings(all_strings)

    if timestamp:
        return timestamp
    else:
        # Print a message if the timestamp is not found
        logger.warning("Timestamp not found.")


def remove_null_values_from_dict(result_dict, null=("nan", "", None)):
    assert isinstance(result_dict, dict)
    assert isinstance(null, (str, tuple, list))
    # if null is singular, then make it into a tuple
    if not isinstance(null, (list, tuple)):
        null = null
    result_dict_copy = result_dict.copy()
    for k, v in result_dict.items():
        if v in null:
            result_dict_copy.pop(k)
    return result_dict_copy


def extract_elements_by_ids(html, id_list):
    result_dict = {}

    if isinstance(html, str):
        soup = BeautifulSoup(html, "html.parser")
    else:
        soup = html

    # Ensure id_list is a list, even if it contains a single ID
    if not isinstance(id_list, list):
        id_list = [id_list]

    for element_id in id_list:
        element = soup.find(id=element_id)

        if element:
            result_dict[element_id] = element.text

    result_dict = remove_null_values_from_dict(result_dict)
    
    return result_dict


def display_data(scraped_data):
    if scraped_data:
        # Print or use the extracted data as needed
        for key, value in scraped_data.items():
            logger.info(f"{key}: {value}")
    else:
        # Print a message if there is no data to display
        logger.warning("No data to display.")


def scrape_data(webpage_url:str, measurements_filepath):
    try:
        # Fetch HTML content from the specified address and path
        html = fetch_html_content(webpage_url)
    except GetRequestUnsuccessful:  # CHECK EXCEPTION TYPE WHEN NOT CONNECTED
        # If unsuccessful, then restart loop and try again
        print('Fetch unsuccessful')
    # Parse the HTML content using BeautifulSoup
    soup = parse_html_content(html)
    # Scrape data from the parsed HTML

    id_dict = {}
    with open(measurements_filepath, "r") as file:
        data = yaml.safe_load(file)
    for category, names in data.items():
        for name in names:
            id_dict.update({name: category})
    
    scraped_values = extract_elements_by_ids(soup, list(id_dict.keys()))
    scraped_time = datetime.now()

    return scraped_values, scraped_time