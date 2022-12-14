from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

captchas = ["gs_captcha_ccl"]

#TODO: We should gracefully handle search timeout, do we currently?

# driver : Selenium webdriver
# sleep : time to sleep while waiting for page/captcha to load
# Returns: soup of page after captcha has been handled.
def handleCaptcha(driver, sleep):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    for captcha in captchas:
        if soup.find("div", id=captcha) is not None:
            try:
                WebDriverWait(driver, sleep).until(EC.presence_of_element_located((By.ID, captcha)))
                WebDriverWait(driver, sleep).until(EC.invisibility_of_element_located((By.ID, captcha)))
            except TimeoutException:
                print("Captcha timed out! Try increasing the timeout variable.")
            return 1
        else:
            return 0