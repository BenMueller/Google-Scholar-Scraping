from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from .config import Config

import os, requests
from requests import Timeout, ConnectionError
from pathlib import Path

pdf_markers = ["gs_ggs gs_fl", "gs_or_ggsm"]

#TODO: We should gracefully handle search timeout, do we currently?

# Generic PDF download script. Takes the URL, checks for already existing PDF, and downloads if new.
# TODO: give options for where to download to.
def genericHandler(soup, name, download_dir, default_class=pdf_markers):
    slash = Config.get_config().get('Slash')
    timeout = Config.get_config().get('TimeOut')

    for marker in pdf_markers:
        link_info = soup.findChild("div", class_=marker)
        if link_info is not None:
            soup = link_info
    if link_info is not None:
        url = link_info.a['href']
        # Check if the paper has already been downloaded
        if not os.path.exists(download_dir + slash + name):

            # If the link is already a pdf file, download it directly
            if os.path.splitext(name)[1] == ".pdf":
                filename = Path(download_dir + slash + name)
                try:
                    response = requests.get(url, timeout=timeout)
                    filename.write_bytes(response.content)
                except (Timeout, ConnectionError) as err:
                    print("Downloading file at " + url + " timed out\n")


#    # TODO: If not a usable URL, use webdriver to download the links
#    else:
#        embeddedHandler(url, name)
#    print("\x1B[3m'" + name + "'\x1B[23m")

def embeddedHandler(link, name):
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

    # For pdfs from wiley it doesn't download it right away
    frame = tmp_driver.find_elements_by_id('pdf-iframe')
    if len(frame) == 1:
        tmp_driver.switch_to.frame(frame[0])
        tmp_driver.find_element_by_tag_name('a').click()

    # TODO: this section seems to not work on Linux. Files simply end up in the user/Downloads
    # folder and don't appear to get copied to the intended destination (more testing needed)
    file = self.most_recent_file()
    while not file or file.endswith('.crdownload'):
        sleep(1)
        file = self.most_recent_file()
    print("saving to: " + self.download_dir + self.slash + name)
    os.rename(file, self.download_dir + self.slash + name)
    print("should be done")
    tmp_driver.close()


# TODO: what does this actually do?
def most_recent_file(self):
    files = os.listdir(self.download_dir)
    if not files:
        return 0
    paths = [os.path.join(self.download_dir, basename) for basename in files]
    file = max(paths, key=os.path.getctime)
    return file