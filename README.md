# Research Scraping Tool (RST)

![PyPI - Status](https://img.shields.io/pypi/status/research-scraping-tool) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/Madwonk/Research-Scraping-Tool) ![PyPI - License](https://img.shields.io/pypi/l/research-scraping-tool) ![Read the Docs](https://img.shields.io/readthedocs/research-scraping-tool)

This is a fork of [Eloise Zag's](https://github.com/El-Zag) wonderful Google Scholar Scraping tool, with some extra features and bugfixes. Ideally, I'd like to generalize it to work with many academic databases (Scholar, Researchgate, CNKI, etc.) and get it packaged for general availability. Contributions are more than welcome!

# Installation
## Linux
* Install Chromium and/or Chrome through your package manager
* Run `pip install research-scraping-tool`

## Windows
* Install Google Chrome and the Chrome Selenium [Webdriver](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/).
* TODO: Test on Windows to see what the install process is

# Usage Guide
There are 2 ways to use this script : 
* Manually, through Jupyter Notebook or a similar Python3 script.
* Through the [CLI](https://research-scraping-tool.readthedocs.io/en/latest/).

## Configuration Options
* download_dir : Directory where the files will be downloaded with the metadata csv
* language : 'fr', 'en'.. Language of Google, which switches reasearch results a little
* captcha : change to True if you get recognized as a bot and start to get the error "NoneType Element has no attribute findChildren". It will switch to a selenium webdriver to scrape html, and let you manually fill in the Captcha before you can keep going.
* sleeptime : time in seconds to wait for the pages to charge when downloading embedded pdfs or html pages. You may need to make it longer if you have a slow connexion to not get errors

## Future Extensions 
* Does the code currently support non-english charactersets (Cyrillic, Korean Hangul, Chinese Hanzi, etc.?) **THIS IS ESSENTIAL**
* It would be nice if we could link into google translate API or similar to automatically translate titles/names/abstracts
* Choose to export metadata in json or csv
* Add HTML sources other than sciencedirect
* Find a way to better treat the captchas issue
* Transform .pdf to good .html
* Treat .html file to ensure they are indeed related to the subject
* Add CNKI as a supported academic database (any others? E.g. Researchgate?)
* Allow scraping author profiles
* Optionally use Firefox as webdriver
* Would be nice if we could scrape author associations from iopscience.iop.org articles
* DOI. **IMPORTANT**
* Grepping through the PDFs/html for author emails/contact info would be nice. Regex?
* Add a CLI interface for Linux. Would be pretty easy, I've done it before. (Package it?)
* Automated Testing. While this is at the bottom of the list, it definitely isn't the lowest priority!
* Proper logging. Right now there's alot of random prints, not sure where they go necessarily.