#!/usr/bin/python3
import xml.etree.ElementTree as ET
import sys
import os
import copy

gamelist_path = sys.argv[1]

root = ET.parse(gamelist_path)

for game in root.findall('game'):
    path = game.find('path').text
    title_elem = game.find('name')
    title = title_elem.text
    try:
        index = title.index("(")
        title = str.strip(title[:index])
        title_elem.text = title
        print("Updated: '" + title + "'")
    except:
        print("No change: " + title)

root.write(gamelist_path)
