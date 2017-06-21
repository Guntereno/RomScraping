#!/usr/bin/python2.7
import xml.etree.ElementTree
import sys
import os

gamelist_path = sys.argv[1]


root = xml.etree.ElementTree.parse(gamelist_path)

for game in root.findall('game'):
    id = game.get('id')
    # Items with the id were gained with scraper
    if id:
        image = game.find('image')
        image_path = image.text
        os.remove(image_path)