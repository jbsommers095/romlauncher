import os
import os.path
from os.path import exists
import re
import sys
import sqlite3

if len(sys.argv) != 3:
    print('Usage: addsteamgame <Game Name> <Gamefile.exe directory>')
    sys.exit(1)
home=os.path.expanduser('~')
dbfile=home + '/pga.db'

if not os.path.exists(dbfile):
    print('File not found!')
    sys.exit(1)
connection = sqlite3.connect(dbfile)
cur = connection.cursor()
cur.execute("SELECT max(id) from games")
game_id = 1
lis=cur.fetchone()
if len(lis) > 0:
    game_id=lis[0] + 1
game = sys.argv[1]
slug = game.replace("'", "").replace(' ', '-').lower()
#platform = 'Steam'
#runner = 'steam'
#steam_id = int(sys.argv[2])
platform = 'Microsoft Windows'
runner = 'wine'
steam_id = None
directory = sys.argv[2]
values = {"id": game_id,
            "name": game,
            "slug": slug,
            "extension": '.exe',
            "installer_slug": None,
            "parent_slug": None,
            "platform": platform,
            "runner": runner,
            "retroarch_core": None,
            "steam_id": steam_id,
            "executable": None,
            "directory": home,
            "game_directory": directory,
            "updated": None,
            "lastplayed": 0,
            "installed": 1,
            "installed_at": None,
            "year": None,
            "configpath": None,
            "has_custom_banner": None,
            "has_custom_icon": None,
            "playtime": 0.0,
            "hidden": 0,
            "service": None,
            "service_id": None
        }
query = "INSERT INTO games ({columns}) VALUES ({placeholders})".format(
    columns = ','.join(values.keys()),
    placeholders = ','.join('?' * len(values))
    )
cur.execute(query, list(values.values()))
connection.commit()
print(game + ' written to database!')
