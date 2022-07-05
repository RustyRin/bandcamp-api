from .bandcampjson import BandcampJSON
from bs4 import BeautifulSoup, FeatureNotFound
import requests
import logging
import json

def get_json(url, debugging: bool = False):

        headers = {'User-Agent': f'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.MissingSchema:
            return None

        try:
            soup = BeautifulSoup(response.text, "lxml")
        except FeatureNotFound:
            soup = BeautifulSoup(response.text, "html.parser")

        logging.debug(" Generating BandcampJSON..")
        bandcamp_json = BandcampJSON(soup, debugging).generate()
        page_json = {}
        for entry in bandcamp_json:
            page_json = {**page_json, **json.loads(entry)}
        logging.debug(" BandcampJSON generated..")

        return page_json

def get_main_genres():
    try:
        page_json = get_json(url="https://intlanthem.bandcamp.com/album/in-these-times")
    except Exception as err:
        print("Error getting the sample album for the genres")
        print(err)
        raise AttributeError

    genres = []
    for genre_dict in page_json['signup_params']['genres']:
        genres.append(genre_dict['value'])

    return genres

def get_subgenres(main_genre: str):

    if main_genre == "" or main_genre == None:
        raise Exception('Main genre slug was not provided')
    
    try:
        page_json = get_json(url="https://intlanthem.bandcamp.com/album/in-these-times")
    except Exception as err:
        print("Error getting the sample album for the genres")
        print(err)
        raise AttributeError

    subgenres = []

    for subgenre in  page_json['signup_params']['subgenres'][main_genre]:
        subgenres.append(subgenre['value'])

    return subgenres