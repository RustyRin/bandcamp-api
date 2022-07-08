import requests
from bs4 import BeautifulSoup, FeatureNotFound

class Label:

    def __init__(self, label_url: str, debugging: bool = False):

        self.label_title = ""
        self.location = ""
        self.bio = ""
        self.links = []
        self.bands = []
        '''
        {
            "name": "",
            "location": "",
            "picture": "",
            "url": ""
        }
        '''
        self.albums = []
        """
        {
            "artist": "",
            "title": "",
            "art_url": "",
            "url": ""
        }
        """
        self.merch_url = ""
        self.subscription_url = ""
        self.community_url = ""         # maybe in the future, scrape the page
        self.profile_picture_url = ""

        header = {'User-Agent': 'bandcamp-api/0 (https://github.com/RustyRin/bandcamp-api)'}

        #change the url to bands
        label_url = label_url.split('/')
        label_url = label_url[0] + '//' + label_url[2]  # [1] is empty
        artists_url = label_url + '/artists'
        albums_url = label_url + '/music'

        try:
            response = requests.get(url=artists_url, headers=header)
        except requests.exceptions.MissingSchema:
            return None
        
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except FeatureNotFound:
            soup = BeautifulSoup(response.text, "html.parser")

        name_location = soup.find('p', {"id": "band-name-location"})
        self.label_title = name_location.find('span', {"class": "title"}).get_text()

        self.location = name_location.find("span", {"class": "location secondaryText"}).get_text()

        self.bio = soup.find("p", {"id": "bio-text"}).get_text()

        try:
            links = soup.find("ol", {"id": "band-links"})
            links = links.find_all("a")
            for link in links:
                self.links.append(link.get('href'))
        except:
            pass

        artists = soup.find("div", {"class": "leftMiddleColumns"})
        artists = artists.find_all("li")

        for artist in artists:
            band = {}
            band['name'] = artist.text
            band['name'] = ' '.join(band['name'].split())

            band['location'] = artist.find("div", {"class": "artists-grid-location secondaryText"}).get_text()
            band['location'] = ' '.join(band['location'].split())
            try:
                band["picture"] = artist.find("img").get('data-original').split('_')[0] + '_0.jpg'
            except:
                try:
                    band["picture"] = artist.find("img").get('src').split('_')[0] + '_0.jpg'
                except:
                    band["picture"] = ""

            band["url"] = artist.find("a").get('href')

            self.bands.append(band)

        # changing url to the album url
        try:
            response = requests.get(url=albums_url, headers=header)
        except requests.exceptions.MissingSchema:
            return None
        
        try:
            soup = BeautifulSoup(response.text, "html5lib")
        except FeatureNotFound:
            soup = BeautifulSoup(response.text, "html.parser")

        albums = soup.find("ol", {"id": "music-grid"})
        albums = albums.find_all("li")

        for album in albums:

            current_album = {}

            try:
                current_album["artist"] = album.find('span', {"class": "artist-override"}).text
                current_album['artist'] = ' '.join(current_album['artist'].split())
            except:
                current_album['artist'] = ''


            current_album['title'] = album.find("p", {"class": "title"}).get_text().replace(current_album['artist'], "")
            current_album['title'] = ' '.join(current_album['title'].split())

            try:
                current_album['art_url'] = album.find("img").get('data-original').split('_')[0] + '_0.jpg'
            except:
                current_album['art_url'] = album.find("img").get('src').split('_')[0] + '_0.jpg'

            #current_album['art_url'] = album.find("img").get("src")

            if 'http' not in album.find('a').get('href'):
                current_album['url'] = label_url + album.find('a').get('href')
            else:
                current_album['url'] = album.find('a').get('href')

            self.albums.append(current_album)

        self.merch_url = label_url + '/merch'
        self.subscription_url = label_url + '/fan-club'
        self.community_url = label_url + '/community'

        self.profile_picture_url = soup.find('div', {'id': "rightColumn"})
        self.profile_picture_url = self.profile_picture_url.find('div', {"id": "bio-container"})