import os
import datetime, dateparser

# TODO: Getters and setters for the classes below
# Required values:
# Title : String, title of the paper,
# Link : String, primary url to the article. First come first serve.
# Summary : String, short summary.
# engine : the db engine used to generate.

# Optional values:
# Authors : String, list of Authors
# primary_authors : list of PRIMARY authors
# author_contacts : dict of authors and their contact info
# journals : if we find multiple entries we can append these.
class Article:
    def __init__(self, title, link, summary, engine, abstract = None, authors=[],
                 primary_authors=[], author_contacts={},
                 journals=[]):
        self.title = title
        self.link = link
        self.summary = summary
        self.engine = engine

        self.abstract = abstract
        self.authors = authors
        self.primary_authors = primary_authors
        self.author_contacts = author_contacts
        self.journals = journals

    def __str__(self):
        return None #TODO: placeholder

    def add_journal(self, journal):
        # TODO: Check for duplicates, somehow
        self.journals.append(journal)

    # TODO: Let's say we have multiple articles. Add them to the source list.
    # on second thought maybe we just want to check for duplicates, add the journal entry?
    def merge(self, article1, article2):
        self.merged = True

# name : Name of Journal. V is list of: date, cited, publisher/etc
# Link : String, primary url to the article. First come first serve.
# site : the site parser used (if any)
# date : the date published
# dlurl : String, url to download the text
# dltype : String, 'PDF', 'HTML'... not sure if I want to keep this option
class Journal:
    def __init__(self, name, link, site, date=None, cited=None,
                 dlurl=None, dltype=None):
        self.name = name
        self.link = link
        self.site = site
        self.accessed = datetime.today()
        self.date = dateparser.parse(date)
        self.cited = cited
        self.dlurl = dlurl
        self.dltype = dltype

# This will take in a list of articles and assemble them into a json
# format for saving to a file or otherwise sharing.
def articles_to_json(articles):
    return None #TODO