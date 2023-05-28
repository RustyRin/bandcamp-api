# bandcamp-api
A simple way to get info from Bandcamp

This was based on and inspired by the work at [bandcamp-dl](https://github.com/iheanyi/bandcamp-dl)  
Thank you for making my work much easier!

#### Installation
`pip install bandcamp-api`

#### Basic Use
```python
from bandcamp_api import Bandcamp

bc = Bandcamp()

album = bc.get_album(album_url="https://c418.bandcamp.com/album/minecraft-volume-alpha")

print("Album title:", album.album_title)
```

For more information on the functions available see the [functions wiki](https://github.com/RustyRin/bandcamp-api/wiki/Functions) or the [object wiki](https://github.com/RustyRin/bandcamp-api/wiki/Bandcamp-api-Objects)
