from .cnki import Scraper as cnki
from .gs import Scraper as gs

# If there's any optional scrapers/require specific deps, handle that here

engines = [cnki, gs]