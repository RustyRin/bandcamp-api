import requests
from bs4 import BeautifulSoup, FeatureNotFound
import logging
import json
from .bandcampjson import BandcampJSON
from datetime import datetime
import time

def string_clean(input_string):
    return ' '.join(input_string.split())

class Daily():
    def __init__(Bandcamp):
       """Bandcamp Daily"""

    def search_latest(self, num_to_get: int):
        """Gets the latests stories form the Bandcamp Daily
        :param num_to_get: The number of BCDaily posts to return. Will allways return an array of article links."""
        page = 1
        url = "https://daily.bandcamp.com/latest?page="
        posts_obtained = []
        header = {'User-Agent': 'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}
        while True:
            try:
                response = requests.get(url=url + str(page), headers=header)
            except requests.exceptions.MissingSchema as Err:
                return Err
            
            try:
                soup = BeautifulSoup(response.text, "lxml")
            except FeatureNotFound:
                soup = BeautifulSoup(response.text, "html.parser")

            articles = soup.find("articles-list")
            try:
                articles = articles.find_all('div', {"class": "title-wrapper"})
                #list = []

                for article in articles:
                    if len(posts_obtained) < num_to_get:
                        posts_obtained.append("https://daily.bandcamp.com" + article.find('a').get('href'))
                    else:
                        return posts_obtained
            except:
                return posts_obtained

            page += 1

    def search_best_of(self, section_slug: str, num_to_get: int):
        """Seach for BCDaily posts in the Best Of section.
        :param section_slug: The URL slug of the section you want. Example for Best of 2016: 'best-of-2016'
        :param num_to_get: The number of BCDaily posts to return. Will allways return an array of article links."""
        header = {'User-Agent': 'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}
        url = "https://daily.bandcamp.com/"
        page = 1
        posts_obtained = []

        while True:
            try:
                response = requests.get(url=url + section_slug  + '?page=' + str(page), headers=header)
            except requests.exceptions.MissingSchema:
                return ""
            
            try:
                soup = BeautifulSoup(response.text, "lxml")
            except FeatureNotFound:
                soup = BeautifulSoup(response.text, "html.parser")

            articles = soup.find("articles-list")
            try:
                articles = articles.find_all('div', {"class": "title-wrapper"})

                for article in articles:
                    if len(posts_obtained) < num_to_get:
                        posts_obtained.append("https://daily.bandcamp.com" + article.find('a').get('href'))
                    else:
                        return posts_obtained
            except:
                return posts_obtained

            page += 1
            print("Going to page " + str(page))
                



    def search_franchises(self, section_slug: str, num_to_get: int):
        """Seach the BCDaily in the Franchises section.
        :param section_slug: The URL slug of the section you want. Example for Album Of The Day: album-of-the-day
        :param num_to_get: The number of BCDaily posts to return. Will allways return an array of article links."""
        header = {'User-Agent': 'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}
        url = "https://daily.bandcamp.com/"
        page = 1
        posts_obtained = []

        while True:
            try:
                response = requests.get(url=url + section_slug  + '?page=' + str(page), headers=header)
            except requests.exceptions.MissingSchema:
                return ""
            
            try:
                soup = BeautifulSoup(response.text, "lxml")
            except FeatureNotFound:
                soup = BeautifulSoup(response.text, "html.parser")

            articles = soup.find("articles-list")
            try:
                articles = articles.find_all('div', {"class": "title-wrapper"})

                for article in articles:
                    if len(posts_obtained) < num_to_get:
                        posts_obtained.append("https://daily.bandcamp.com" + article.find('a').get('href'))
                    else:
                        return posts_obtained
            except:
                return posts_obtained

            page += 1

    def search_genre(self, genre_slug: str, num_to_get: int):
        """Search the BCDail in the Genre section.
        :param genre_slug: The URL slug of the genre you want. Example for R&B/Soul: r-b-soul
        :param num_to_get: The number of BCDaily posts to return. Will allways return an array of article links."""
        header = {'User-Agent': 'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}
        url = "https://daily.bandcamp.com/genres/"
        page = 1
        posts_obtained = []

        while True:
            try:
                response = requests.get(url=url + genre_slug  + '?page=' + str(page), headers=header)
            except requests.exceptions.MissingSchema:
                return ""
            
            try:
                soup = BeautifulSoup(response.text, "lxml")
            except FeatureNotFound:
                soup = BeautifulSoup(response.text, "html.parser")

            try:
                articles = soup.find("articles-list")
                articles = articles.find_all('div', {"class": "title-wrapper"})
                list = []

                for article in articles:
                    if len(posts_obtained) < num_to_get:
                        posts_obtained.append("https://daily.bandcamp.com/genres" + article.find('a').get('href'))
                    else:
                        return posts_obtained
            except:
                return posts_obtained

            page += 1        

def get_json(url, debugging: bool = False):

    header = {'User-Agent': f'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

    try:
        response = requests.get(url, headers=header)
    except requests.exceptions.MissingSchema:
        return ""
    
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

class Story():
    def __init__(self, story_url: str):
        self.title = ""
        self.author = ""
        self.description = ""
        self.headline = ""
        self.main_image_url = ""
        self.story_type = ""
        self.linked_in_text = []
        self.linked_media = []
        self.text = ""
        self.date_published = 0
        self.date_last_modified = 0
        self.images = []        # look for story with multiple images
        self.tags = []

        response = requests.get(story_url)

        try:
            page_json = get_json(url = story_url)
        except Exception as err:
            print(err)
            raise AttributeError("Either the Artist URL gicen is either private, deleted or the link is malformed")
        
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except FeatureNotFound:
            soup = BeautifulSoup(response.text, "html.parser")
        
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except FeatureNotFound:
            soup = BeautifulSoup(response.text, "html5lib")

        self.title = string_clean(soup.find('article-title').text)

        self.author = soup.find('article-credits')
        self.author = string_clean(self.author.find('a').text)

        self.story_type = string_clean(soup.find('article-type').text.lower())
        body = soup.find('article')
        body = body.find_all('p')

        for section in body:
            for link in section.find_all('a'):
                #self.linked_in_text.append(link.absolute_links.pop())
                self.linked_in_text.append(link.get('href'))
            if string_clean(section.text):
                self.text = self.text + string_clean(section.text) + '\n\n'                

        players = soup.find_all("div", {"class": "player-wrapper"})


        '''
        I wanted to make a thing
        to get songs that were featured
        in a BCD story, but a large amount
        of the information is rendered
        in JS, I tried to get it with
        requests-html and its render
        funtion but could not get it
        to work propery. Sorry.
        '''

        try:
            self.date_published = datetime.strptime(page_json['datePublished'], '%Y-%m-%dT%H:%M:%SZ')
            self.date_published = int(time.mktime(self.date_published.timetuple()))
        except:
            self.published = 0

        try:
            self.date_last_modified = datetime.strptime(page_json['dateModified'], '%Y-%m-%dT%H:%M:%SZ')
            self.date_last_modified = int(time.mktime(self.advanced['last_edited'].timetuple()))
        except:
            self.date_last_modified = self.date_published

        self.description = page_json['description']

        self.headline = page_json['headline']

        self.main_image_url = page_json['image']

        '''
        bandcamp does not seem to have a standard way
        to deal with images
        sometimes its in a gallery class
        sometimes its in an inline class
        sometimes its just laying there

        so i am loading the entire article body
        then deleting all music, artist and merch
        that is all on the side
        '''
        body = soup.find('article')

        artists = body.find_all("mplayer-artist")       # artists
        for artist in artists:
            artist.decompose()
        players = body.find_all('mplayer')              # players
        for player in players:
            player.decompose()
        all_merch = body.find_all('mplayer-sidebar')    # merch
        for merch in all_merch:
            merch.decompose()

        for photo in body.find_all('img'):
            if photo.get('src') is not None:
                self.images.append(photo.get('src'))

        self.tags = page_json['keywords'].split(', ')
