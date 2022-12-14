from .engine import Engine
import os
import regex as re
from ..util import captcha
from ..util import db
from ..util import dlpdf

from bs4 import BeautifulSoup

class Scraper(Engine):
    def __init__(self, query):
        super().__init__(query)

        # Parameters that can be altered during the session
        self.languages = self.config.get('Languages')

        # Global parameters
        self.regex = re.compile('[^a-zA-Z0-9]')

        self.timeout = 10

        self.driver.get("https://scholar.google.com/")

        # TODO: this code probably breaks on Windows, test it there. Intended to be a blacklist of
        # "bad" URLs that appear to not work, but we should let the user ignore this if they want
        # (ideally we would log the broken download link after making an attempt)
        # Note 2: this code ALREADY breaks if you're using pip/packagetools. todo: fix this in setup.cfg
        # Hotfix currently in place: don't read from the file
        if self.config.get('Blacklist'):
            self.blacklist = ['icm.edu.pl', 'proquest.com', 'kut.edu.kp', 'ist.psu.edu', 'koreascience.or.kr', 'www.koreascience.or.kr', 'img.hisupplier.com',
                              'xuebao.neu.edu.cn', 'journal.hep.com.cn', 'worldscientific.com', 'academia.edu', 'nanoscience.or.kr']
#            with open("../res/blacklist.txt") as fh:
#                self.blacklist.append(fh.readline())

    def parse(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        body = soup.find("div", class_="gs_r")
        if body is None:
            return None
        else:
            if "did not match any articles." in body.get_text(strip=True):
                print("Zero results found")
                pass
            else:
                # All the gs article results
                results = soup.find("div", id="gs_res_ccl_mid")
                articles_soup = results.findChildren("div", class_="gs_r gs_or gs_scl")


                # First we're going to download the article PDF, if possible.
                # Then we hand off the URL to the super() handler, if it doesn't
                # know what to do with it we use the generic parser here
                # At the end, we append to the global db
                for article_soup in articles_soup:
                    info = dict()

                    general_infos = article_soup.findChild("div", class_="gs_ri")
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


                    # TODO: add a checker for bad URLs/bad certs somewhere. Config setting?

                    dlpdf.genericHandler(article_soup, info['Title'], self.download_dir)

                    recognized = super().parse(info['Link'])

                    if not recognized:
                        self.db.append(info)



# TODO: this is a remainder of old code, move to specific sites to handle their PDFs
#                    else:
#                        name = self.regex.sub('_', info['Title'].lower()) + '.html'
#                        if not os.path.exists(self.download_dir + self.slash + name):

                            # sciencedirect.com
#                            if info['DL Source'] == "sciencedirect.com":
#                                info['Filename'] = name
#                                self.sciencedirect(info['Download'], name)

#                                self.save_metadata(info)
#                                print("\x1B[3m'" + info['Title'] + "'\x1B[23m")
#                articles_dl.append(info)
#            elif include_all:
#                articles_dl.append(self.article_info(article, False))

#        return articles_dl


            # parse the gs stuff here
            # pass the URL to super to see if it's recognized
            # if not, we get a null and just parse generically here

    def run(self):
        super().run()
        for i in range(1, self.pagelimit):
            url = self.generate_url(self.search, page=i)
            self.driver.get(url)
            captcha.handleCaptcha(self.driver, self.sleep)
            if self.parse() is None:
                break
            if BeautifulSoup(self.driver.page_source, 'lxml').find(
                "span", class_="gs_ico gs_ico_nav_last") is None:
                break #TODO: Test this section
        return

    def toText(self):
        return super().toText()


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

    def most_recent_file(self):
        files = os.listdir(self.download_dir)
        if not files:
            return 0
        paths = [os.path.join(self.download_dir, basename) for basename in files]
        file = max(paths, key=os.path.getctime)
        return file

    # search should be a String, just as you would have typed it in Google Scholar
    # Generate the google scholar url based on the words in the searchbar, at the indicated page
    def generate_url(self, search, authors="", page=1):
        search = self.generate_hexstring(search)
        page = (page - 1) * 10 #hmmm. Not sure this is right. Should it actually concat to 00 or 10 etc etc? i.e. concat a 0?
        for name in authors:
            search += '+author%3A"' + self.generate_hexstring(name) + '"'
        return "https://scholar.google.com/scholar?start=" + str(page) + "&q=" + search + "&hl=" + self.languages + "&as_sdt=0,5"

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

