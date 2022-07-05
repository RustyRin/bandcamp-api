from setuptools import *

setup(
    name="bandcamp_api",
    version="0.1",
    description="Obtains information from bandcamp.com",
    author="RustyRin",
    packages=['bandcamp_api'],
    requires=["setuptools", 'json', 'requests', "bs4", "datetime", "time", "logging", "random", "demjson3"],
    zip_safe=False
    )