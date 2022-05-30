import os
import os.path
from os.path import exists
import requests
from urllib.error import HTTPError, URLError
import sys
import sqlite3
home=os.path.expanduser('~')
webbanner='https://lutris.net/games/banner/'
database=home + '/.local/share/lutris/pga.db'
webcacheloc=home + '/.cache/lutris/webcache.txt'
webcache={}
if not exists(database):
    print('Database does not exist!')
    sys.exit(1)
if not exists(webcacheloc):
	f = open(webcacheloc, 'x')
	f.close()
connection=sqlite3.connect(database)
cursor=connection.cursor()
rows=None
try:
	rows=cursor.execute("SELECT slug from games").fetchall()
except sqlite3.OperationalError:
	print('Invalid db format')
	sys.exit(1)
with open(webcacheloc, 'r') as f:
    for line in f.readlines():
        webcache[line]=1
count=0
for row in rows:
    file=row[0]
    url=webbanner + file + '.jpg'
    localloc=home + '/.cache/lutris/banners/' + file + '.jpg'
    if not exists(localloc) and webcache.get(url + '\n') == None:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            with open(localloc, 'wb') as f:
                f.write(r.content)
            print(url)
            count+=1
        except requests.exceptions.HTTPError as e:
            print(e)
            with open(webcacheloc, 'a') as f:
                f.write(url + '\n')
        except requests.exceptions.URLError as e:
            print(e)
            with open(webcacheloc, 'a') as f:
                f.write(url + '\n')
        except requests.exceptions.Timeout as e:
            print(e)
    else:
        if webcache.get(url + '\n') != None:
            print('Exists in cache!  Continuing import')
        if exists(localloc):
            print('File already exists!  Continuing import')

print('Completed!  Number of new files downloads: ' + str(count))

