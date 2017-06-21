#!/usr/bin/python3
import xml.etree.ElementTree as ET
import sys
import os
import copy

gamelist_from_path = sys.argv[1]
gamelist_to_path = sys.argv[2]
gamelist_result_path = sys.argv[3]

from_root = ET.parse(gamelist_from_path)
to_root = ET.parse(gamelist_to_path)

for game in from_root.findall('game'):
    path = game.find('path').text

    found = False
    for to_game in to_root.findall('game'):
        path_elem = to_game.find('path')
        if(path_elem == None):
            print(to) 
        to_path = to_game.find('path').text
        if(path == to_path):
            found = True
            print(path + " already exists, skipping.")
            break
    
    if(not found):
        print("Adding " + path)
        new_element = copy.deepcopy(game)
        to_root.getroot().append(new_element);

to_root.write(gamelist_result_path)
