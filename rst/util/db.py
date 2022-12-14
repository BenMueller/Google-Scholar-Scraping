# not actually a DB at this point in time
# Right now this is just a global storage block
# Note that I have NOT made this thread safe at the moment. TODO.
# Ideally this will evolve into some kind of actual db connector
# Yes, I know, this is *bad* practice being a singleton.

from . import article
import pprint

class connector:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(connector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        connector._articles_list = []

    @staticmethod
    def append(toAppend):
        connector._articles_list.append(toAppend)

    def toText(self):
        pp = pprint.PrettyPrinter(indent=2)
        return pp.pprint(connector._articles_list)