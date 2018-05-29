#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 18:43:10 2018

@author: chrisstrods
"""

from scraper import get_matches as get
from scraper import get_extra_data as get_extra
from scraper import scrape
from scraper import process

print("GETTING DATAFILES")
get.main(1897,2018,4961,9602)
print("SUCCESSFULLY LOADED DATAFILES")
print("SCRAPING AFLTABLES DATA")
scrape.main(1897,2018)
print("SUCCESSFULLY SCRAPED AFLTABLES DATA")
print("SCRAPING FOOTYWIRE DATA")
get_extra.main(4961,9602)
print("SUCCESSFULLY SCRAPED FOOTYWIRE DATA")
print("POST-PROCESSING SCRAPED DATA")
process.main()
print("SUCCESSFULLY POST-PROCESSED SCRAPED DATA")

print("DATA IS NOW READY FOR ANALYSIS!")
