# This folder/file is intended to be a bunch of generic file downloaders.
# So if there's a PDF or other file that needs a specific setup/interaction
# to download, put the engine for that here

from ..util import webdriver
from ..util import article
from ..util import captcha

import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from time import sleep
import os
from pathlib import Path
import csv

class Downloader(webdriver.Webdriver):

    def __init__(self, url):
        super().__init__()
        self.url = url

    # Downloads pdfs with interactive pages
    def dl_pdf(self):
        return

    # Downloads automatically. Check for PDF/.docx/etc
    def dl_auto(self):
        return


    # TODO: what does this actually do?
    def most_recent_file(self):
        files = os.listdir(self.download_dir)
        if not files:
            return 0
        paths = [os.path.join(self.download_dir, basename) for basename in files]
        file = max(paths, key=os.path.getctime)
        return file
