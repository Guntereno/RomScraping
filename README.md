# RomScraping
## Overview
After using Steven Selphs fantastic scraping tool
(https://github.com/sselph/scraper) I found that it missed a lot of my roms and
that some manual intervention was required. This repository contains scripts
used to manipulate and scrape metadata afterwards.

## Requirements
- Python 3
- Pillow

## scrape_missing.py
The scrape_missing.py tool is designed to automate the process of scraping data
for roms which aren't in the gamelist.xml while querying for user input when
required.

For each rom in your rompath (which isn't already in the gamelist) the user is
shown a list of search results based on the roms filename. These can be selected
by typing the displayed index. If the results don't contain the correct game
then the id can be entered manually by entering 'i'. If you don't want to
take an action for the current rom you can enter 's' to skip it.

### Usage
scrape-missing.py -i &lt;inputfile&gt; -o &lt;outputfile&gt; -r &lt;rompath&gt; -m &lt;imagepath&gt; -p &lt;platform&gt;
- inputfile: The input gamelist xml file.
- outputfile: The resulting gamelist xml to be created. (Can be the same as inputfile.)
- rompath: The path to the roms to scrape data for.
- imagepath: The path containing the cover art images.
- platform: The platform as used in thegamesdb.net database.
