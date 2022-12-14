import requests
import os
from bs4 import BeautifulSoup

# Saves a html with abstract, text, and bibliography from a full url
# TODO: What this SHOULD do is check for PDF access, else pull metadata
def sciencedirect(self, soup_url, name):
    if not self.captcha:
        req = requests.get(soup_url, self.headers)
        soup = BeautifulSoup(req.content, 'lxml')
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

# TODO
class Scraper():
    def parse(url):
        return None