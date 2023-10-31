from setuptools import *

setup(
    name="bandcamp_api",
    version="0.2.3",
    description="Obtains information from bandcamp.com",
    author="RustyRin",
    packages=['bandcamp_api'],
    url="https://github.com/RustyRin/bandcamp-api/",
    install_requires=["setuptools", "beautifulsoup4", "demjson3", 'html5lib', 'lxml', "requests"],
    keywords=["api", "bandcamp"],
    zip_safe=False
    )
