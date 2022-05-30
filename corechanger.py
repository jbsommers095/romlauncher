import os
import os.path
from os.path import exists
import re
import sys
import sqlite3

if len(sys.argv) != 3:
    print(str(len(sys.argv)))
    print('Invalid args.  Usage: python corechanger.py <corename> <platform>')
    quit()
core=sys.argv[1]
platform=sys.argv[2]
home=os.path.expanduser('~')
database=home + '/.local/share/lutris/pga.db'
if not exists(database):
    print('Database not found!')
    quit()
connection=sqlite3.connect(database)
cursor=connection.cursor()
platforms=cursor.execute("SELECT DISTINCT(platform) FROM games where runner='libretro' AND platform != 'None'").fetchall()
found=False
count=0
for i in range(0, len(platforms)):
    if platform == platforms[i][0]:
        found=True
        break
if not found:
    print('Invalid Platform!!  Runner must be set to libretro')
    quit()
print('VALID PLATFORM!!')
configpath=home+'/.config/lutris/games/'
rows=cursor.execute("SELECT configpath FROM games WHERE platform= '" + platform + "' AND runner = 'libretro'").fetchall()
for row in rows:
    file = configpath + row[0] + '.yml'
    print(file)
    filecontents=[]
    with open(file, 'r') as f:
        filecontents=f.readlines()
    if '  core' in filecontents[1]:
        filecontents[1] = '  core: ' + core + '\n'
    else:
        filecontents.insert(1, '  core: ' + core + '\n')
    open(file, 'w').close()
    with open(file, 'a') as f:
        for line in filecontents:
            f.write(line)
print('Changes complete!!')
