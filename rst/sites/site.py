from ..util import webdriver
from ..util import article
from ..util import captcha

# generic parser. Will attempt to grep out values. TODO.
def parse(self, soup):
    return None

# if we can't just cram the site into BS with wget, create a webdriver,
# let it load the js/captcha (and handle it if necessary), then get BS
# if there's further stuff (e.g. cookie-based logins) we can handle that
# on the individual site level
class site(webdriver):
    def __init__(self, url):
        webdriver.__init__()
        self.driver.get(url)
        self.soup = captcha.handleCaptcha(self.driver, self.sleep)

    def getSoup(self):
        return self.soup