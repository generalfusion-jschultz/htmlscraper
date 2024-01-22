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

logger = logging.getLogger(__name__)


class Scraper:
    '''
    Scrapes specified ids from a URL
    '''

    def __init__(self, webpage_url:str):
        
        self.url = webpage_url


    def fetch_html_content(self, url):
       
        # Construct the URL with the given IP address and optional path
        try:
            # Make a GET request to the URL
            response = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            logger.warning("HTML GET request was unsuccessful", extra=dict(details=e))
            # raise GetRequestUnsuccessful

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the HTML content if successful
            return response.text
        else:
            # Print an error message if the request fails and return None
            logger.warning(f"Failed to retrieve HTML. Status code: {response.status_code}")
            # raise GetRequestUnsuccessful


    def parse_html_content(self, html):
        
        # Parse the HTML content using BeautifulSoup
        return BeautifulSoup(html, "html.parser")


    def extract_timestamp_from_strings(self, strings):
        
        # Define a regular expression pattern for the timestamp format
        timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

        # Iterate through the strings to find a matching timestamp
        for string in strings:
            match = timestamp_pattern.search(string)
            if match:
                return match.group()

        # Return None if no timestamp is found
        return None


    def scrape_timestamp_from_soup(self, soup):
        
        # Extract all strings within the soup
        all_strings = soup.stripped_strings

        # Attempt to extract timestamp from the strings
        timestamp = self.extract_timestamp_from_strings(all_strings)

        if timestamp:
            return timestamp
        else:
            # Print a message if the timestamp is not found
            logger.warning("Timestamp not found.")


    def remove_null_values_from_dict(self, result_dict, null=("nan", "", None)):
        
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


    def extract_elements_by_ids(self, html, id_list):
        
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

        result_dict = self.remove_null_values_from_dict(result_dict)
    
        return result_dict


    def scrape_data(self, id_list:list):
        
        try:
            # Fetch HTML content from the specified address and path
            html = self.fetch_html_content(self.url)
        except Exception:
            # GetRequestUnsuccessful:  # CHECK EXCEPTION TYPE WHEN NOT CONNECTED
            # If unsuccessful, then restart loop and try again
            logger.warning('Fetch unsuccessful')
        # Parse the HTML content using BeautifulSoup
        soup = self.parse_html_content(html)
        
        # Scrape data from the parsed HTML
        scraped_values = self.extract_elements_by_ids(soup, id_list)

        return scraped_values
    
    def scrape_data2(self, id_list:list, time_id_list:list):

        try:
            # Fetch HTML content from the specified address and path
            html = self.fetch_html_content(self.url)
        except Exception:
            # GetRequestUnsuccessful:  # CHECK EXCEPTION TYPE WHEN NOT CONNECTED
            # If unsuccessful, then restart loop and try again
            logger.warning('Fetch unsuccessful')
        # Parse the HTML content using BeautifulSoup
        soup = self.parse_html_content(html)
        
        # Scrape data from the parsed HTML
        scraped_values = self.extract_elements_by_ids(soup, id_list)
        scraped_time = self.extract_elements_by_ids(soup, time_id_list)

        return scraped_values, scraped_time
    

class ScraperTextFile:
    '''
    Scrapes specified ids from an HTML text file
    '''

    def __init__(self, filepath:str):
        
        with open(filepath) as html:
            index = html.read()
            self.soup = BeautifulSoup(index, "html.parser")


    def remove_null_values_from_dict(self, result_dict, null=("nan", "", None)):
        
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


    def extract_elements_by_ids(self, id_list):
        
        result_dict = {}

        # Ensure id_list is a list, even if it contains a single ID
        if not isinstance(id_list, list):
            id_list = [id_list]

        for element_id in id_list:
            element = self.soup.find(id=element_id)

            if element:
                result_dict[element_id] = element.text

        result_dict = self.remove_null_values_from_dict(result_dict)
    
        return result_dict


    def scrape_data(self, id_list:list):
        
        # Scrape data from the parsed HTML
        scraped_values = self.extract_elements_by_ids(id_list)
            
        return scraped_values
    

    def scrape_data2(self, id_list:list, time_id_list:list):
        
        # Scrape data from the parsed HTML
        scraped_values = self.extract_elements_by_ids(id_list)
        scraped_time = self.extract_elements_by_ids(time_id_list)
            
        return scraped_values, scraped_time