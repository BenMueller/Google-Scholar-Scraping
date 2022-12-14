from ..util.webdriver import Webdriver
from ..util import article
from ..util import captcha
from ..util import db

from ..sites import * #hmmmm

import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from time import sleep
import os
from pathlib import Path
import csv

class Engine(Webdriver):

    def __init__(self, search, pagelimit=5):
        super().__init__()
        self.search = search
        self.pagelimit = pagelimit
        self.soup = None
        self.articles = []
        self.db = db.connector()

    def scrape(self):
        self.soup = captcha.handleCaptcha(self.driver, self.sleep)
        return self.soup

    # If we have a dedicated parser for the URL in question, let's parse it using that!
    # some of those might need webdrivers, some might just wget the page and parse. TBD.
    def parse(self, url):
        for site in sites:
            if site in url:
                return sites[site].parse(url)
            else:
                return None

        # TODO: if url is in sites, then parse, else return null.
        # then gs.py or cnki.py checks for null, do inbuilt parser

    def run(self):
        articles_dl = []
        pass

    def toText(self):
        return self.db.toText()

    def save(self):
        if len(articles) == 0:
            return
        for article in articles:
            # TODO: append to global struct. Maybe db some day.
            self.articles.append(article)

    #TODO: rewrite this, it currently doesn't work. Honestly we need a more
    # fancy format than CSV, maybe json or something similar?
    def save_metadata(self, info):
        exists = os.path.isfile(self.download_dir + self.slash + 'metadata.csv')
        with open(self.download_dir + self.slash + 'metadata.csv', 'a', newline='', encoding="utf-8") as output:
            dictwriter = csv.DictWriter(self.articles, fieldnames=info.keys(), delimiter=";")
            if not exists:
                dictwriter.writeheader()
            dictwriter.writerow(info)
            output.close()
