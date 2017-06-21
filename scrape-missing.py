#!/usr/bin/python3
import sys
import os
import urllib.request,urllib.parse,urllib.error
import xml.etree.ElementTree
import xml.etree.ElementTree as ET
import time
import getopt

from PIL import Image


base_api_url = "http://thegamesdb.net/api/"
user_agent = "scrape-missing.py"

input_file = None
output_file = None
rom_path = None
image_path = None
platform = None


def main(argv):
    parse_args(argv)

    # Build dictionary of path to game node
    element_tree = ET.parse(input_file)
    game_dict = {}

    for game_node in element_tree.findall("game"):
        game_dict[game_node.find("path").text] = game_node

    # Build list of new meta XML nodes
    new_metas = []

    for rom in os.listdir(rom_path):
        ext = os.path.splitext(rom)
        if(ext[1] != ".zip"):
            continue
        
        rom = os.path.join(rom_path, rom)

        if(not rom in game_dict):
            game_meta = select_action(rom)
            if(game_meta):
                new_metas.append(game_meta)

    if(len(new_metas) is 0):
        print ("No changes made")
        sys.exit(1)

    print("Downloading images")
    for game_meta in new_metas:
        try:
            game_meta.download_image()
            game_meta.to_meta_xml(element_tree.getroot())
        except Exception as e:
            print("Didn't add due to error: {0}".format(str(e.args[0])).encode("utf-8"))

    print("Writing gamelist")
    indent(element_tree.getroot())
    element_tree.write(output_file)

def parse_args(argv):
    global input_file
    global output_file
    global rom_path
    global image_path
    global platform

    try:
        opts, args = getopt.getopt(
            argv, "hi:o:r:m:p:",
            [
                "infile=",
                "outfile=",
                "rompath=",
                "imgpath=",
                "platform=",
            ]
        )
    except getopt.GetoptError:
        print(help_string())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help_string())
            sys.exit()
        elif opt in ("-i", "--infile"):
            input_file = arg
        elif opt in ("-o", "--outfile"):
            output_file = arg
        elif opt in ("-r", "--rompath"):
            rom_path = arg
        elif opt in ("-m", "--imgpath"):
            image_path = arg
        elif opt in ("-p", "--platform"):
            platform = arg

    if(
        input_file is None
        or output_file is None
        or rom_path is None
        or image_path is None
        or platform is None
    ):
       print(help_string())
       sys.exit(2)

def help_string():
    return "scrape-missing.py -i <inputfile> -o <outputfie> -r <rompath> -m <imagepath> -p <platform>"

def select_action(rom):
    error_occured = False
    try:
        game_meta = select_action_internal(rom)
    except urllib.error.URLError as error:
        print(str(error.reason))
        error_occured = True
    except Exception as e:
        print("An error occured! {0}".format(str(e)))
        error_occured = True
    finally:
        if(error_occured):
            should_retry = query_yn("Try again?")
            if should_retry:
                return select_action(rom);
            else:
                return None

    if(game_meta):
        # Show confirm prompt
        print("Found '" + game_meta.name + "'.")
        confirmation = query_yn("Is this right?")
        if(confirmation):
            return game_meta
        else:
            return select_action(rom)


def select_action_internal(rom):
    print(rom)
    search_term = os.path.splitext(os.path.basename(rom))
    options = search_games(search_term, platform)

    # Show the menu
    for i,option in enumerate(options):
        print(
            str(i) + ": " +
            str(option["title"]) + "|" + 
            str(option["release"]) + "|" +
            str(option["platform"])
        )
    print("s: Skip")
    print("i: Enter ID")

    # Handle user selection
    while (True):
        selection = input("option>>")
        if(selection is "s"):
            return None
        elif(selection is "i"):
            return input_id(rom)
        else:
            try:
                index = int(selection)
                if((index < 0) or (index >= len(options))):
                    print ("Selection '" + selection + "' is out of range!")
                else:
                    return get_game(options[index]["id"], rom)
            except ValueError:
                print("Invalid value '" + selection + "'. Make another selection.")


def input_id(rom):
    # Get user to enter ID, then get the game with that ID
    print("Enter ID from http://thegamesdb.net")
    while (True):
        id = input("id>>")
        try:
            int_id = int(id)
            game_meta = get_game(id, rom)
            return game_meta
        except ValueError:
            print("Invalid ID '" + selection + "'!")


class GameMeta:
    id = None
    path = None
    name = None
    desc = None
    image_url = None
    image_filename = None
    rating = None
    releasedate = None
    developer = None
    publisher = None
    genre = None
    players = None

    def to_meta_xml(self, parent):
        game_node = ET.SubElement(parent, "game", {"id": self.id, "source":"theGamesDB.net"})

        if (self.path):
            path_node = ET.SubElement(game_node, "path")
            path_node.text = self.path

        if (self.name):
            name_node = ET.SubElement(game_node, "name")
            name_node.text = self.name

        if(self.desc):
            desc_node = ET.SubElement(game_node, "desc")
            desc_node.text = self.desc;

        if(self.image_filename):
            image_node = ET.SubElement(game_node, "image")
            image_node.text = self.image_filename

        if(self.rating):
            rating = float(self.rating) / 5.0
            rating_node = ET.SubElement(game_node, "rating")
            rating_node.text = str(rating)

        if(self.releasedate):
            release_date_st = None
            try:
                release_date_st = time.strptime(self.releasedate, "%m/%d/%Y")
            except ValueError:
                print("Game '" + self.id + "' has invalid date format '" + self.releasedate)
                try:
                    release_date_st = time.strptime(self.releasedate, "%Y")
                except:
                    release_date_st = None

            if(release_date_st):
                release_date = "%04d%02d%02dT000000" % (release_date_st[0], release_date_st[1], release_date_st[2])
                release_date_node = ET.SubElement(game_node, "releasedate")
                release_date_node.text = release_date

        if(self.developer):
            developer_node = ET.SubElement(game_node, "developer")
            developer_node.text = self.developer

        if(self.publisher):
            publisher_node = ET.SubElement(game_node, "publisher")
            publisher_node.text = self.publisher

        if(self.genre):
            genre_node = ET.SubElement(game_node, "genre")
            genre_node.text = self.genre

        if(self.players):
            players_node = ET.SubElement(game_node, "players")
            players_node.text = self.players

    def download_image(self):
        if((self.image_filename == None) or (self.image_url == None)):
            return
        
        error_occured = False
        try:
            req = urllib.request.Request(self.image_url, headers={'User-Agent' : __file__}) 
            f = urllib.request.urlopen(req)
            data = f.read()

            # Download the image to a temp file
            ext = os.path.splitext(self.image_filename)[1]
            temp_file = "temp" + ext
            with open(temp_file, "wb") as code:
                code.write(data)
            
            # Resize the image to 400px width with Pillow
            image = Image.open(temp_file)
            size = image.size
            scale = 400 / size[0]
            new_size = (400, int(size[1] * scale))
            image = image.resize(new_size, Image.ANTIALIAS)
            print("Saving " + self.image_filename)
            image.save(self.image_filename)

        except urllib.error.URLError as error:
            print(str(error.reason))
            error_occured = True
        except Exception as e:
            print("An error occured!: {0}".format(str(e)))
            error_occured = True
        finally:
            os.remove(temp_file)
            if(error_occured):
                should_retry = query_yn("Try again?")
                if should_retry:
                    self.download_image()
                else:
                    raise Exception

    def from_gamesdb_xml(self, game_node, base_image_url, rom):
        if(game_node != None):
            self.id = game_node.find("id").text
            self.path = rom
            self.name = try_get_text(game_node, ["GameTitle"])
            self.desc = try_get_text(game_node, ["Overview"])
            self.rating = try_get_text(game_node, ["Rating"])
            self.releasedate = try_get_text(game_node, ["ReleaseDate"])
            self.developer = try_get_text(game_node, ["Developer"])
            self.publisher = try_get_text(game_node, ["Publisher"])
            self.genre = try_get_text(game_node, ["Genres", "genre"])
            self.players = try_get_text(game_node, ["Players"])
            
            images_node = game_node.find("Images")
            if(images_node):
                for boxart_node in images_node.findall("boxart"):
                    if(boxart_node.attrib["side"] == "front"):
                        self.image_url = base_image_url + boxart_node.text
                        ext = os.path.splitext(self.image_url)[1]
                        image_filename = os.path.splitext(os.path.basename(rom))[0] + "-image" + ext
                        self.image_filename = os.path.abspath(os.path.join(image_path, image_filename))
                        break


def try_get_subnode(root, path):
    current = root
    for val in path:
        current = current.find(val)
        if(current == None):
            return None
    return current


def try_get_text(root, path):
    node = try_get_subnode(root, path)
    if(node != None):
        return node.text


def try_get_attrib(root, path, attrib):
    node = try_get_subnode(root, path)
    if(node != None):
        return node.attrib(attrib)


def query_yn(message):
    print(message + " (y/n)");
    selection = input("select>>")
    if(selection is "y" or selection is "yes"):
        return True
    else:
        return False;


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def get_game(id, rom):
    url = base_api_url + "GetGame.php?id=" + id
    req = urllib.request.Request(url, headers={'User-Agent' : user_agent}) 
    response = urllib.request.urlopen(req)
    xml = response.read()

    xml_root = ET.fromstring(xml)

    base_image_url = xml_root.find("baseImgUrl").text;
    game_node = xml_root.find("Game")
    result = GameMeta()
    result.from_gamesdb_xml(game_node, base_image_url, rom)

    return result


def search_games(search_term, platform):
    data = urllib.parse.urlencode({'name': search_term, 'platform': platform})
    data = data.encode('utf-8')
    url = base_api_url + "GetGamesList.php";
    req = urllib.request.Request(url, headers={'User-Agent' : user_agent}) 
    response = urllib.request.urlopen(req, data)
    xml = response.read()

    result = []
    xml_root = ET.fromstring(xml)
    for game_node in xml_root.findall("Game"):
        entry = {
            "id": game_node.find("id").text,
            "title": try_get_text(game_node, ["GameTitle"]),
            "release": try_get_text(game_node, ["ReleaseDate"]), 
            "platform": try_get_text(game_node, ["Platform"])
            }
        result.append(entry)
    return result


if __name__ == "__main__":
   main(sys.argv[1:])