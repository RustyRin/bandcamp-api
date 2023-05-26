import requests


class Artist:
    def __init__(self, artist_id: int):
        self.artist_title = ""
        self.artist_id = 0
        self.artist_url = ""
        self.bio = ""
        self.profile_picture_url = ""
        self.location = ""
        self.concerts = []
        self.links = []
        self.album_ids = []

        # getting information from api
        response = requests.get(
            url="https://bandcamp.com/api/mobile/25/band_details?band_id=" + str(artist_id),
        )
        result = response.json()
        self.artist_title = result['name']
        self.artist_id = result['id']
        self.artist_url = result['bandcamp_url']
        self.bio = result['bio']
        self.profile_picture_url = "https://f4.bcbits.com/img/" + str(result["bio_image_id"]).zfill(10) + "_0.jpg"
        self.location = result['location']

        for show in result["shows"]:
            current_show = {
                "location": show["loc"],
                "venue": show["venue"],
                "date": show["date"],
                "url": show["uri"],
                "unix_time": show["utc_date"]
            }

            self.concerts.append(current_show)

        for link in result["sites"]:
            self.links.append(link["url"])

        for album in result["discography"]:
            self.album_ids.append(album["item_id"])
