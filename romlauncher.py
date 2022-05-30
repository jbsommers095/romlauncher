import os
import os.path
from os.path import exists
import re
import sys
import sqlite3

home=os.path.expanduser('~')

defaultsteamcmd="steam steam://rungameid/"
defaultwincmd="wine "
defaultscummvmcmd="scummvm "
defaultmsdoscmd="dosbox "
defaultwin31cmd="bash ~/runwin31game.bash "
defaulttriforcecmd=home + "/triforce/triforce -U " + home + "/triforce" + " -e "
defaultgccmd=home + "/dolphin/build/Binaries/dolphin-emu -e "
default3dscmd=home + "/citra/build/bin/Release/citra-qt "
defaultswitchcmd=home + "/yuzu/yuzu "
defaultps2cmd=home + "PCSX2 --fullboot "
defaultps3cmd=home + "/rpcs3/"
defaultretroarchcmd=home + "/.local/share/lutris/runners/retroarch/retroarch"

if len(sys.argv) != 2:
    print('Invalid args.  Usage: python3 romlauncher.py Gamename')
    print('Alternate Usage: python3 romlauncher.py Gamename* to search for filenames containing the given Gamename')
    sys.exit(1)
ymlfile=re.sub(r"\s+", " ", sys.argv[1]).strip(" ")
ymlfile=ymlfile.lower().replace(" ", "-")
print(ymlfile)
#home=os.path.expanduser('~')
database=home + '/.local/share/lutris/pga.db'
if not exists(database):
    print('Database not found!')
    sys.exit(1)
connection=sqlite3.connect(database)
cursor=connection.cursor()
#names=cursor.execute("SELECT distinct slug FROM games").fetchall()
try:
    cursor.execute("SELECT distinct slug FROM games")
except sqlite3.OperationalError:
    print("Database doesn't contain the appropriate columns.  Reinstall Lutris or check this.")
    sys.exit(1)
names = cursor.fetchall()
found=False
if "*" in ymlfile:
    words=ymlfile.split("*")
    ymlfile=ymlfile.replace("*", "")
    print("Files containing this word " + ymlfile + " found: ")
    for word in words:
        if len(word) != 0:
            for name in names:
                if word in name[0]:
                    found=True
                    print(name[0])
    if not found:
        print("No files found!")
    sys.exit(0)
for name in names:
    if name[0] == ymlfile:
        found=True
        break
if not found:
    print("Game title not found in database!  Use * character in input to print all game titles containing the given input.")
    sys.exit(1)
else:
    print('Game title found!')
installplatformrunners=''
gametitle=''
runnersall=''#cursor.execute("SELECT DISTINCT runner FROM games").fetchall()
steamid=''
try:
    runnersall=cursor.execute("SELECT DISTINCT runner FROM games").fetchall()
    installplatformrunners=cursor.execute("SELECT extension, platform, runner, retroarch_core, game_directory FROM games WHERE slug = '" + ymlfile + "'").fetchall()
    gametitle=cursor.execute("SELECT DISTINCT name FROM games WHERE slug = '" + ymlfile + "'").fetchone()
    steamid=cursor.execute("SELECT steam_id FROM games WHERE slug = '" + ymlfile + "' AND platform = 'Steam'").fetchone()
except sqlite3.OperationalError:
    print("Database doesn't contain proper columns.  Reinstall Lutris or look into this before proceeding.")
    sys.exit(1)
#runnersall=cursor.fetchall()
choice=0
for i in range(0, len(installplatformrunners)):
    print(str(i) + ": " +  installplatformrunners[i][1])
print('q: quit')
num=input('Pick your choice based on platform.\n')
choice=-1
if num == "q":
    print('Exiting application')
    sys.exit(0)
# check if input is either a float or non-numberic, should only take integer input
if '.' not in num and num.isnumeric():
    choice=int(num)
while not num.isnumeric() or '.' in num or choice < 0 or choice >= len(installplatformrunners):
    num=input('Invalid Choice!  Try another!\n')
    if num == "q":
        print("Exiting application")
        sys.exit(0)
    if num.isnumeric():
        choice=int(num)
extension=installplatformrunners[choice][0]
platform=installplatformrunners[choice][1]
runner=installplatformrunners[choice][2]
retroarchcore=installplatformrunners[choice][3]
gamefile=installplatformrunners[choice][4]

found=False
for i in range(0, len(runnersall)):
    if runner == runnersall[i][0]:
        found = True
        break
if not found or platform == '' or runner == '':
    if platform == '':
        print('Platform not set!')
    if runner == '':
        print('Runner not set!')
    else:
        print('Invalid Platform!  Install valid platform before trying again!')
    sys.exit(1)
found=False
connection.close()
#retroarchcore=installplatformrunners[choice][3]
scummvmid=''
tempdir=home + '/.cache/lutris/tmp/'
if runner == 'steam' or runner == 'wine':
    found=True
elif runner == 'scummvm':
    scummvmconfig=home + '/.config/scummvm/scummvm.ini'
    with open(scummvmconfig, 'r') as f:
        lines=f.readlines()
        for i in range(0, len(lines)):
            if 'description' in lines[i]:
                if gametitle[0] in lines[i]:
                    # search for gameid in file
                    while lines[i] != '\n':
                        #scummvmid=lines[j].replace('gameid=', '').replace("\n", "")
                        if 'gameid' in lines[i]:
                            scummvmid=lines[i].replace('gameid=', '').replace("\n", "")
                            print(str(i) + ", " + scummvmid)
                            found=True
                            break
                        i+=1
            if found:
                break
    print('Loading game ' + gametitle[0])
else:
    if not os.path.exists(gamefile):
        print('File does not exist.  If this is an archive, game filename should match the filename of the archive.  Exiting program.')
        sys.exit(1)
    extpos=len(gamefile)-gamefile.rfind('.')
    directfile=gamefile[gamefile.rfind('/') + 1:len(gamefile) - extpos]
    print(directfile)
    extensions=['.zip', '.7z', '.rar', '.gz']
    cmd=''
    found=False
    for ext in extensions:
        if ext in gamefile:
            print(ext + ' file found!  Compressing')
            found=True
            break
    if found and extension != '.7z .gz .rar .zip':
        cmd="7z x '" + gamefile + "' -o" + tempdir
        #print(cmd)
        os.system(cmd)
        for file in os.listdir(tempdir):
            # Assumes the extracted content has same name as compressed file
            # Let Emulator handle exceptions regarding this
            # First assure .cue file gets priority in checking as cds run .cue file
            # TODO recursively find file as it might be in subdirectory of tempdir, assumes no or only one subdir as placeholder
            if '.cue' in file:
                gamefile="'" + tempdir + file + "'"
                break
            exts=extension.split()
            for ext in exts:
                if ext in file:
                    gamefile="'" + tempdir + file + "'"
                    #print(gamefile)
            woquote=re.sub("'", '', gamefile)
            if os.path.isdir(woquote):
                for subfile in os.listdir(woquote):
                    if '.cue' in subfile:
                        gamefile="'" + tempdir + file + "/" + subfile + "'"
                        break
                    if ext in subfile:
                        gamefile="'" + tempdir + file + "/" + subfile + "'"
    else:
        gamefile = "'" + gamefile + "'"
    print('Loading game ' + gamefile)
retroarchpath = defaultretroarchcmd
retroarchcorepath = home + "/.local/share/lutris/runners/retroarch/cores/"
#retroarchpath = "retroarch"
#retroarchcorepath = home + "/.config/retroarch/cores/"
#TODO store runnerpaths in different file for global config

if platform == "Steam":
    cmd = defaultsteamcmd + str(steamid[0])
elif platform == "Microsoft Windows":
    cmd = defaultwincmd + "'" + gamefile + "'"
elif platform == "Linux":
    if runner == "scummvm":
        cmd = defaultscummvmcmd + scummvmid + "-win"
elif platform == "MS-DOS":
    print(gamefile)
    cmd = defaultmsdoscmd + gamefile
elif platform == "Windows 3.1":
    # decrement last by 1 to drop final quotation
    gamefile = gamefile[gamefile.rfind('/') + 1:len(gamefile) - 1]
    #gamefile = "'" + gamefile[gamefile.rfind('/') + 1:len(gamefile)]
    # TODO Windows 3.1 exes don't seem to always load from commandline and error out with file not found error sometimes, find out what causes this
    print(gamefile)
    cmd = defaultwin31cmd + gamefile
elif platform == 'Nintendo GameCube' or platform == 'Nintendo Wii' or platform == 'Triforce':
    if platform == 'Triforce':
        print("Triforce game loading")
        cmd = defaulttriforcecmd + gamefile
    else:
        cmd = defaultgccmd + gamefile
elif platform == 'Nintendo 3DS':
    cmd = default3dscmd + gamefile
elif platform == 'Nintendo Switch':
    cmd = defaultswitchcmd + gamefile
elif platform == 'Sony Playstation 2':
    cmd = defaultps2cmd + gamefile
elif platform == 'Sony Playstation 3':
    cmd = defaultps3cmd + gamefile
else:
    print('RETROARCH :D')
    retroarchcfg=home + '/.local/share/lutris/runners/retroarch/retroarch.cfg'
    #retroarchcfg=home + '/.config/retroarch/retroarch.cfg'
    cmd = retroarchpath + " --fullscreen --config=" + retroarchcfg + " --libretro=" + retroarchcorepath + retroarchcore + "_libretro.so " + gamefile
    #print(cmd)
print(cmd)
os.system(cmd)
print('Clearing cache.')
os.system("rm -rv " + tempdir + "*")
print('Program has sucessfully closed')
