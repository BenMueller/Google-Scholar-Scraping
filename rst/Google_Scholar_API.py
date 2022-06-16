import requests
from requests.exceptions import Timeout, ConnectionError
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
from sys import platform
import os
import codecs
from pathlib import Path
import re
from fake_useragent import UserAgent
import csv


class Scraper:
    def __init__(self, download_dir, language, captcha, sleeptime, blacklist=True, allow_broken_ssl=False):
        # Parameters that can be altered during the session
        self.download_dir = download_dir
        self.language = language
        self.captcha = captcha
        self.sleep = sleeptime

        # Global parameters
        self.regex = re.compile('[^a-zA-Z0-9]')
        self.ua = UserAgent()
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': self.ua.chrome,
        }

        self.timeout = 10

        self.driver = None
        # On ouvre une session et on rempli à la main le captcha
        if self.captcha:
            options = webdriver.ChromeOptions()
            options.add_argument(f'user-agent={self.ua.chrome}')
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://scholar.google.com/")


        if platform == "win32":
            self.slash = '\\'
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.slash = '/'

        # TODO: this code probably breaks on Windows, test it there. Intended to be a blacklist of
        # "bad" URLs that appear to not work, but we should let the user ignore this if they want
        # (ideally we would log the broken download link after making an attempt)
        # Note 2: this code ALREADY breaks if you're using pip/packagetools. todo: fix this in setup.cfg
        # Hotfix currently in place: don't read from the file
        if blacklist:
            self.blacklist = ['icm.edu.pl', 'proquest.com', 'kut.edu.kp', 'ist.psu.edu', 'koreascience.or.kr', 'www.koreascience.or.kr', 'img.hisupplier.com',
                              'xuebao.neu.edu.cn', 'journal.hep.com.cn', 'worldscientific.com', 'academia.edu', 'nanoscience.or.kr']
#            with open("../res/blacklist.txt") as fh:
#                self.blacklist.append(fh.readline())

        if allow_broken_ssl:
            # TODO: some pages due to various... reasons... (hmmm, I wonder why Kim-Chaek university
            # in North Korea doesn't load properly lol) have broken SSL.
            # We should give the option to users to ignore browser warnings and download/scrape anyways.
            # For now, I'm adding kim-chaek to the blacklist, but it should be removed once we fix this.
            print("This feature is not yet implemented!")


    def close(self):
        self.driver.close()

    def set_language(self, language):
        self.language = language

    def set_download_dir(self, download_dir):
        self.download_dir = download_dir

    def set_captcha(self, captcha):
        if not (self.captcha == captcha):
            if self.captcha:
                self.driver.close()
                self.driver = None
            else:
                self.driver = webdriver.Chrome()
                self.driver.get("https://scholar.google.com/")

    def set_sleep(self, sleeptime):
        self.sleep = sleeptime

    # searchbar should be a String, just as you would have typed it in Google Scholar
    # downloaded the documents related to the searchbar String, for the pages indicated
    # returns a list of dics with the metadata
    def scrape_all(self, search, authors=[], first_page=1, last_page=5, include_all = False):

        articles_dl = []

        if isinstance(authors, str):
            authors = [authors]

        for i in range(first_page, last_page + 1):

            print("\nExploration of Page " + str(i))

            url = self.generate_url(search, authors, page=i)

            if not self.captcha:
                req = requests.get(url, self.headers)
                soup = BeautifulSoup(req.content, 'lxml')

            # SWITCH TO THIS if captcha block
            else:
                self.driver.get(url)
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                if soup.find("div", id="gs_captcha_ccl") is not None:
                    try:
                        WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.ID, 'gs_captcha_ccl')))
                        WebDriverWait(self.driver, 120).until(EC.invisibility_of_element_located((By.ID, 'gs_captcha_ccl')))
                    except TimeoutException:
                        print("Search timed out! Try increasing the timeout variable.") #TODO: this is currently embedded above. Unify timeout vars.
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')

            body = soup.find("div", class_="gs_r")
            if body is not None:
                if "did not match any articles." in body.get_text(strip=True):
                    print("Zero results found")
                    break

            page_articles = self.scrape_page(soup, include_all)

            articles_dl = articles_dl + page_articles

            #TODO: this check for next page appears to not work, debug
            if soup.find("span", class_="gs_ico gs_ico_nav_last") is not None:
                print("Results ended on Page " + str(i))
                break

        print("\n" + str(len(articles_dl)) + " documents ont été téléchargés")
        return articles_dl

    # Inputs a BeautifulSoup page, and scrapes all info (TODO: include_all is misleading)
    def scrape_page(self, soup, include_all=False):

        # All the results of the page
        results = soup.find("div", id="gs_res_ccl_mid")

        # List of all the articles
        articles = results.findChildren("div", class_="gs_r gs_or gs_scl")

        articles_dl = []
        # TODO: I want to eventually rewrite this section/inputs so that instead of include_all, we have a flag download=Y/N, and another one to ignore ones missing the doc (ignore_missing?)
        for article in articles:
            # Cas d'un lien pdf directement
            if article.find("div", class_="gs_ggs gs_fl") is not None:
                info = self.article_info(article, True)
                print(info['Download'])

                if not any(site in info['DL Source'] for site in self.blacklist):
                    if info['Type'] == 'PDF':

                        # Name of the file we're going to download
                        name = self.regex.sub('_', info['Title'].lower()) + '.pdf'

                        # Check if the paper has already been downloaded
                        if not os.path.exists(self.download_dir + self.slash + name):
                            info['Filename'] = name

                            # If the link is already a pdf file, download it directly
                            if os.path.splitext(info['Download'])[1] == ".pdf":
                                filename = Path(self.download_dir + self.slash + name)
                                try:
                                    response = requests.get(info['Download'], timeout=self.timeout)
                                    filename.write_bytes(response.content)
                                except (Timeout, NewConnectionError) as err:
                                    print("Downloading file at " + info['Download'] + " timed out\n")

                            # If not, use webdriver to download the links
                            else:
                                self.dl_embedded_pdf(info['Download'], name)
                            print("\x1B[3m'" + info['Title'] + "'\x1B[23m")

                            self.save_metadata(info)
                    else:
                        name = self.regex.sub('_', info['Title'].lower()) + '.html'
                        if not os.path.exists(self.download_dir + self.slash + name):

                            # sciencedirect.com
                            if info['DL Source'] == "sciencedirect.com":
                                info['Filename'] = name
                                self.sciencedirect(info['Download'], name)

                                self.save_metadata(info)
                                print("\x1B[3m'" + info['Title'] + "'\x1B[23m")
                articles_dl.append(info)
            elif include_all:
                articles_dl.append(self.article_info(article, False))

        return articles_dl

    # Take as input a div class = "gs_r gs_or gs_scl" (an article in google scholar's html)
    # With a downloadable link (assert)
    # Output is a dictionary with those infos :
    # { Title : String, title of the paper,
    # Link : String, url to the article,
    # Authors : String, list of Authors
    # Journal : String, partial name of Journal
    # Year : int, Year of publication
    # Source : String, Source of publication
    # Summary : String, Google scholar summary
    # Cited : Int, Number of times cited
    # Download : String, url to download the text
    # Type : String, 'PDF', 'HTML'..
    # DL Source : String, website the download is from}
    def article_info(self, soup_article, has_document=True):
        # assert (soup_article.find("div", class_="gs_ggs gs_fl") is not None, "Il n'y a pas de lien pour télécharger cet article")
        info = dict()

        # Informations sur l'article
        general_infos = soup_article.findChild("div", class_="gs_ri")
        info['Title'] = general_infos.h3.a.text
        info['Link'] = general_infos.h3.a['href']

        publication_infos = general_infos.findChild("div", class_="gs_a").text
        publication_infos = publication_infos.replace(u'\xa0', u' ')
        publication_infos = publication_infos.split(" - ")
        length = len(publication_infos[1])
        info['Authors'] = publication_infos[0]
        if(len(publication_infos) > 2):
            info['Journal'] = publication_infos[1][0:length - 6]
            info['Year'] = int(publication_infos[1][length - 4:length])
            info['Source'] = publication_infos[2]
        else:
            info['Source'] = publication_infos[1]

        summary = general_infos.findChild("div", class_="gs_rs").text
        summary = summary.replace(u'\xa0', u' ')
        info['Summary'] = summary

        bottom_text = general_infos.findChild("div", class_="gs_fl")
        cited = bottom_text.findChildren("a")[2].text
        cited = cited.replace(u'\xa0', u' ')
        info['Cited'] = cited[5:len(cited) - 5]

        # Informations sur le téléchargement
        if has_document:
            dl_infos = soup_article.findChild("div", class_="gs_or_ggsm")
            info['Download'] = dl_infos.a['href']
            if dl_infos.text == "Full View":
                info['Type'] = 'HTML'
                info['DL Source'] = 'unknown'
            else:
                dl_type = dl_infos.span.text
                info['Type'] = dl_type[1:len(dl_type) - 1]
                info['DL Source'] = dl_infos.a.text.split(']')[1].split()[0]
        return info

    # Downloads pdfs that are embedded in a link and not .pdf
    # Uses additional selenium and time for Wiley documents
    def dl_embedded_pdf(self, link, name):
        options = webdriver.ChromeOptions()

        options.add_experimental_option('prefs', {
            "download.default_directory": self.download_dir,  # Change default directory for downloads
            "download.prompt_for_download": False,  # To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
        })
        options.add_argument(f'user-agent={self.ua.random}')

        tmp_driver = webdriver.Chrome(options=options)
        tmp_driver.get(link)

        sleep(int(self.sleep))

        # For pdfs from wiley it doesn't download it right away
        frame = tmp_driver.find_elements_by_id('pdf-iframe')
        if len(frame) == 1:
            tmp_driver.switch_to.frame(frame[0])
            tmp_driver.find_element_by_tag_name('a').click()
            sleep(int(self.sleep))

        # TODO: this section seems to not work on Linux. Files simply end up in the user/Downloads
        # folder and don't appear to get copied to the intended destination (more testing needed)
        file = self.most_recent_file()
        while not file or file.endswith('.crdownload'):
            sleep(1)
            file = self.most_recent_file()
        os.rename(file, self.download_dir + self.slash + name)
        tmp_driver.close()

    def most_recent_file(self):
        files = os.listdir(self.download_dir)
        if not files:
            return 0
        paths = [os.path.join(self.download_dir, basename) for basename in files]
        file = max(paths, key=os.path.getctime)
        return file

    # search should be a String, just as you would have typed it in Google Scholar
    # Generate the google scholar url based on the words in the searchbar, at the indicated page
    def generate_url(self, search, authors, page=1):
        search = self.generate_hexstring(search)
        page = (page - 1) * 10
        for name in authors:
            search += '+author%3A"' + self.generate_hexstring(name) + '"'

        return "https://scholar.google.com/scholar?start=" + str(page) + "&q=" + search + "&hl=" + self.language + "&as_sdt=0,5"

    def generate_hexstring(self, instr):
        q = instr.split()
        for i in range(len(q)):
            word = q[i]
            for j in range(len(word)):
                if not word[j].isalpha():  # For characters that aren't letters, they are encoded in hex by google
                    if word[j] == "\\":
                        word[j] = "%5C"
                    else:
                        hvalue = '%' + codecs.decode(codecs.encode(bytes(word[j], 'utf-8'), 'hex'), 'utf-8').upper()
                        q[i] = word.replace(word[j], hvalue)
        q = '+'.join(q)
        return q

    def save_metadata(self, info):
        exists = os.path.isfile(self.download_dir + self.slash + 'metadonnees.csv')
        with open(self.download_dir + self.slash + 'metadonnees.csv', 'a', newline='', encoding="utf-8") as output:
            dictwriter = csv.DictWriter(output, fieldnames=info.keys(), delimiter=";")
            if not exists:
                dictwriter.writeheader()
            dictwriter.writerow(info)
            output.close()



    # Saves a html with abstract, text, and bibliography from a full url
    def sciencedirect(self, soup_url, name):
        if not self.captcha:
            req = requests.get(soup_url, self.headers)
            soup = BeautifulSoup(req.content, 'lxml')

        # SWITCH TO THIS if captcha block
        else:
            self.driver.get(soup_url)
            sleep(int(self.sleep))
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

        html = open(self.download_dir + "\\" + name, "w", encoding='utf-8')

        abstract = soup.findChild('div', id="abstracts")
        html.write(str(abstract))

        body = soup.findChild('div', id="body")
        html.write(str(body))

        tail = soup.find("div", class_="Tail")
        biblio = tail.next_element
        html.write(str(biblio))

        html.close()

# Example of scraper :
# scraper = Scraper(os.getcwd() + '\\Download', 'fr', True, 5)



