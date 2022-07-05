from bs4 import BeautifulSoup, FeatureNotFound
import requests
import logging
import json

from .bandcampjson import BandcampJSON

def get_soup(url, debugging: bool = False):
    header = {'User-Agent': f'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

    try:
        response = requests.get(url, headers=header)
    except requests.exceptions.MissingSchema:
        return None
    
    try:
        soup = BeautifulSoup(response.text, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(response.text, "html.parser")

    return soup


def get_json(url, debugging: bool = False):

    header = {'User-Agent': f'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

    try:
        response = requests.get(url, headers=header)
    except requests.exceptions.MissingSchema:
        return None
    
    try:
        soup = BeautifulSoup(response.text, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(response.text, "html.parser")

    logging.debug(" Generating JSON...")

    bandcamp_json = BandcampJSON(soup, debugging).generate()
    page_json = {}
    for entry in bandcamp_json:
        page_json = {**page_json, **json.loads(entry)}

    logging.debug(' Bandcamp JSON generated...')

    return page_json

class Artist:

    def __init__(self, artist_url, debugging: bool = False):
        self.artist_title = ""
        self.artist_url = ""
        self.bio = ""
        self.profile_picture_url = ""
        self.location = ""
        self.concerts = []
        '''
        {
            "address": "",
            "venue": "",
            "date": "",
            "url": ""
        }
        '''
        self.links = []
        self.album_urls = []

        try:
            page_json = get_json(url = artist_url)

        except Exception as err:
            print(err)
            raise AttributeError("Either the Artist URL given is either private, deleted or the link is malformed")

        self.artist_title = str(page_json['artist']) # if their name is just numbers
        #self.url = page_json['byArtist']["@id"] # bc you may give a link that contains /album/.. or /track/...
        if 'track' in artist_url:
            self.artist_url = artist_url.rpartition('/track/')[0]
        elif '/album/' in artist_url:
            self.artist_url = artist_url.rpartition('/album/')[0]
        else:
            self.artist_url = artist_url

        self.artist_url = self.artist_url + '/music'

        try:
            self.bio = page_json['publisher']['description']
        except:
            self.bio = ""

        try:
            self.profile_picture_url = page_json['publisher']['image'].split('_')[0] + '_0.jpg'
        except:
            self.profile_picture_url = ""

        try:
            self.location = str(page_json['publisher']['foundingLocation']['name'])
        except:
            self.location = ""

        try:
            for concert in page_json['shows_list']:
                current_concert = {}

                try:
                    current_concert['address'] = concert['loc']
                except:
                    current_concert['address'] = ""

                try:
                    current_concert['venue'] = concert['venue']
                except:
                    current_concert['venue'] = ""

                try:
                    current_concert['date'] = int(concert['utc_date'])
                except:
                    current_concert['date'] = 0


                try:
                    current_concert['url'] = concert['uri']
                except:
                    current_concert['url'] = ""

                self.concerts.append(current_concert)
        except:
            pass


        try:
            for link in page_json['publisher']['mainEntityOfPage']:
                self.links.append(link['url'])
        except:
            pass

        soup = get_soup(self.artist_url)

        soup = soup.find('ol', {'id': "music-grid"})
        album_links = soup.find_all('a')

        if 'track' in artist_url:
            base_link = artist_url.rpartition('/track/')[0]
        elif '/album/' in artist_url:
            base_link = artist_url.rpartition('/album/')[0]
        else:
            base_link = artist_url

        for link in album_links:
            self.album_urls.append(base_link + link.get('href'))