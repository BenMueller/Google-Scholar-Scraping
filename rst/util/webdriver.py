from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from sys import platform
import re
from fake_useragent import UserAgent

from .config import Config

class Webdriver:
    def __init__(self):
        self.config = Config().get_config()
        print(self.config.get('DownloadDir'))
        self.download_dir = self.config.get('DownloadDir')
        self.sleep = self.config.get('TimeOut')
        self.allow_broken_ssl = self.config.get('AllowBrokenSSL')

        # Global parameters
        self.regex = re.compile('[^a-zA-Z0-9]')
        self.ua = UserAgent()
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': self.ua.chrome
        }

        self.driver = None
        self.options = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'--no-sandbox')
        self.options.add_argument(f'--disable-dev-shm-usage')
        self.options.add_argument(f'user-agent={self.ua.chrome}')

        self.driver = webdriver.Chrome(options=self.options, service=ChromeService(ChromeDriverManager().install()))

        if platform == "win32":
            self.slash = '\\'
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.slash = '/'

        if self.allow_broken_ssl:
            self.options.add_argument('ignore-certificate-errors')

    def close(self):
        self.driver.close()