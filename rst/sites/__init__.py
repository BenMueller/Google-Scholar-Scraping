from .sdirect import Scraper as sdirect
from .bmj import Scraper as bmj

sites = {
    ('sciencedirect.com') : sdirect,
    ('jeck.bmj.com', 'bmj.com') : bmj
}