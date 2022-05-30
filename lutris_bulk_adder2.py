#!/usr/bin/env python3

import re
import os
import sys
import argparse
import sqlite3
from datetime import datetime

DEFAULT_ROM_FILE_EXTS = ['bin', 'iso', 'zip', 'rar', '7z', 'sfc', 'gba', 'gbc', 'gb', 'md', 'n64',
                         'nes', '32x', 'gg', 'sms', 'bin', 'smc', 'a78', 'a52', 'lnx', 'jag',
                         'col', 'D64', 'T64', 'd64', 't64', 'nds', 'dsi', 'chd', 'vec', 'vb', 
                         'xci', 'nsp']
EXT_MAP = {'Steam': '.exe .pkg .Appimage',
            '3DO': '.bin .cue',
			'Atari 2600': '.a26 .bin',
			'Atari 5200': '.a52 .bin',
			'Atari 7800': '.a78',
			'Apple Mac OSX': '.pkg',
			'Commodore 128': '.7z .gz .rar .zip',
			'Coleco ColecoVision': '.col',
			'Commodore 64': '.D64 .d64 .T64 .t64',
			'Commodore VIC-20': '.20 .40 .60 .70 .a0 .b0 .v20',
			'Nintendo Game Boy/Game Boy Color': '.gb .gbc',
			'Nintendo Game Boy Advance': '.gb .gbc .gba',
			'Hartung Game Master': '.bin',
			'Mattel Intellivision': '.bin .int .itv',
			'Atari Jaguar': '.jag',
			'Atari Lynx': '.lnx',
			'Linux': '.Appimage',
			'MS-DOS': '.exe',
			'Microsoft MSX/MSXII': '.mx2 .rom',
			'Magnavox Odyssey2': '.bin',
			'SNK Neo Geo': '.7z .gz .rar .zip',
			'Nintendo 3DS': '.3ds',
			'Nintendo DS': '.dsi .nds',
			'Nintendo 64': '.n64 .ndd .z64',
			'Nintendo NES': '.nes',
			'Nintendo GameCube': '.iso',
			'Nintendo Switch': '.nsp .xci',
			'Nintendo Wii': '.iso',
			'Nintendo Wii U': '.rpx',
			'PC Engine Supergrafx': '.pce',
			'PC Engine TurboGrafx 16': '.pce',
			'Philips CDi': '.chd',
			'Scummvm': '',
			'Sony PSP': '.iso',
			'Sony Playstation': '.bin .cue',
			'Sony Playstation 2': '.bin .cue .iso',
			'Sony Playstation 3': '.BIN',
			'Sega 32x': '.32x',
			'Sega Dreamcast': '.bin .cue',
			'Sega Saturn': '.bin .cue',
			'Sega Game Gear': '.gg',
			'Sega Master System/Pico': '.md',
			'Sega Genesis': '.sms',
			'Sega CD': '.bin .cue',
			'Nintendo SNES': '.sfc .smc',
			'Namco Triforce': '.iso',
			'GCE Vectrex': '.vecx',
			'Nintendo Virtual Boy': '.vb',
			'Microsoft Windows': '.exe'
			}
PLATFORMS=EXT_MAP.keys()
'''PLATFORMS = [
    '3DO',
    'Amstrad CPC',
    'Arcade',
    'Atari 2600',
    'Atari 7800',
    'Atari 5200',
    'Atari 8bit computers',
    'Atari Jaguar',
    'Atari Lynx',
    'Atari ST/STE/TT/Falcon',
    'Bandai WonderSwan',
    'ChaiLove',
    'ColecoVision',
    'C128',
    'Commodore 16/Plus/4',
    'Commodore 64',
    'VIC-20',
    'VJME',
    'Intellivision',
    'Game Boy/Game Boy Color/Game Boy Advance',
    'Jaguar',
    'Lynx',
    'Magnavox Odyssey²',
    'MS-DOS',
    'MSX/MSX2/MSX2+',
    'MSX',
    'NEC PC Engine (SuperGrafx)',
    'NEC PC Engine (TurboGrafx-16)',
    'NEC PC Engine TurboGrafx-16',
    'NEC PC-98',
    'NEC PC-FX',
    'Neo Geo',
    'Nintendo 3DS',
    'Nintendo DS',
    'Nintendo Game Boy (Color)',
    'Nintendo Game Boy Advance',
    'Nintendo Game Boy Color',
    'Nintendo GameCube',
    'Nintendo 64',
    'Nintendo Entertainment System',
    'Nintendo Switch',
    'Nintendo Virtual Boy',
    'Nintendo Wii',
    'Nintendo GameCube',
    'PSP',
    'PC-8000 / PC-8800 series',
    'PC Engine SuperGrafx',
    'Sega Dreamcast',
    'Sega Game Gear',
    'Sega Genesis',
    'Sega Genesis/Mega Drive',
    'Sega Maste System/Gamegear',
    'Sega Master System',
    'Sega Saturn',
    'Saturn',
    'Sega 8/16-bit + 32X (Various)',
    'Sharp X68000',
    'Sinclair ZX Spectrum',
    'Sinclair ZX81',
    'SNK Neo Geo Pocket (Color)',
    'SNK Neo Geo Pocket',
    'Sony PlayStation 2',
    'Sony PlayStation 3',
    'Sony PlayStation Portable',
    'PlayStation',
    'Steam',
    'Super Nintendo Entertainment System',
    'Uzebox',
    'Vectrex',
    'Virtual Boy',
    'Z-Machine'
]'''

def option_list(options):
    """Option list type for argparse
    Args:
        options: String containing space-delimited key-value pairs in the form <name>=<value>

    Returns:
        dictionary containing parsed options
    Raises:
        argparse.ArgumentTypeError: Argument is formatted incorrectly
    """

    pairs_raw = re.split(r"\s+", options)
    pairs = {}
    for pair in pairs_raw:
        parsed = pair.split('=', maxsplit=1)
        if len(parsed) < 2:
            raise argparse.ArgumentTypeError("Option \"{}\" is not formatted correctly".format(pair))

        pairs.update({parsed[0]: parsed[1]})

    return(pairs)


def directory(path):
    """Directory type for argparse
    Args:
        path: directory path

    Returns:
        directory path
    Raises:
        argparse.ArgumentTypeError: Argument is not a directory
    """
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError("{} is not a directory".format(path))
    else:
        return path


def scan_for_filetypes(dir, types):
    """Scans a directory for all files matching a list of extension types.
    Args:
        dir: Directory location to scan.
        types: List of file extensions to include.
    Returns:
        A list of file paths.
    Raises:
        FileNotFoundError: Directory does not exist.
    """

    files = set()
    with os.scandir(dir) as it:
        for entity in it:
            if entity.is_file():
                fn_delimited = entity.name.split(os.extsep)
                try:
                    if(fn_delimited[len(fn_delimited) - 1].lower() in types):
                        files.add(os.path.join(dir, entity.name))
                except IndexError:
                    pass
    return files


def main():
    parser = argparse.ArgumentParser(description='Scan a directory for ROMs to add to Lutris.')

    # Required arguments
    parser.add_argument('-d', '--directory', type=directory, required=True,
                        help='Directory to scan for games.')
    parser.add_argument('-r', '--runner', type=str.lower, required=True,
                        help='Name of Lutris runner to use.')
    parser.add_argument('-p', '--platform', type=str, required=True, choices=PLATFORMS,
                        help='Platform name.')

    # Lutris paths
    parser.add_argument('-ld', '--lutris-database', type=str,
                        default=os.path.join(os.path.expanduser('~'), '.local', 'share', 'lutris', 'pga.db'),
                        help='Path to the Lutris SQLite database.')
    parser.add_argument('-ly', '--lutris-yml-dir', type=directory,
                        default=os.path.join(os.path.expanduser('~'), '.config', 'lutris', 'games'),
                        help='Directory containing Lutris yml files.')
    parser.add_argument('-lg', '--lutris-game-dir', type=directory,
                        default=os.path.join(os.path.expanduser('~'), 'Games'),
                        help='Lutris games install dir.')

    # Other options
    parser.add_argument('-c', '--core', type=str,help='Set core if platform is set to retroarch.  This argument is also to be used with scummvm to take the launch argument.')
    parser.add_argument('-f', '--file-types', type=str, nargs='*', default=DEFAULT_ROM_FILE_EXTS,
                        help='Space-separated list of file types to scan for.')
    parser.add_argument('-o', '--game-options', type=option_list,
                        help='Additional options to write to the YAML file under the "game" key (e.g. platform number as required for Dolphin)')
    parser.add_argument('-s', '--strip-filename', nargs='*', default=[],
                        help='Space-separated list of strings to strip from filenames when generating game names.')
    parser.add_argument('-n', '--no-write', action='store_true',
                        help="""
Do not write YML files or alter Lutris database, only print data to be written out to stdout. (i.e. dry run)
    """)

    args = parser.parse_args()
    print(args.directory)
    if args.runner == 'retroarch' or args.runner == 'libretro' or args.runner == 'scummvm' or args.platform == 'Scummvm':
        if args.core == None or args.core == '':
            print('Core must be supplied as runner is set to retroarch or scummvm')
            sys.exit(1)

    # Lutris SQLite db
    if os.path.isfile(args.lutris_database):
        conn = sqlite3.connect(args.lutris_database)
        cur = conn.cursor()
    else:
        print("Error opening database {}".format(args.lutris_database))
        sys.exit(1)

    # Get max game ID to increment from
    try:
        cur.execute("select max(id) from games")
    except sqlite3.OperationalError:
        print("SQLite error, is {} a valid Lutris database?".format(args.lutris_database))
        sys.exit(1)
    fetchid=cur.fetchone()
    game_id = 1
    if len(fetchid) > 0:
        game_id = fetchid[0] + 1
    # Scan dir for ROMs
    files = scan_for_filetypes(args.directory, args.file_types)
    for file in files:
        ts = int(datetime.utcnow().timestamp())
        fil=os.path.basename(file)
        extpos=len(fil) - fil.rfind('.')
        # Generate game name and slug from filename
        game = fil[0:len(fil) - extpos]                     # Strip extension
        for token in args.strip_filename:
            game = game.replace(token, "")                  # Strip tokens
        game = re.sub("\(.*?\)","",game)                    # Remove all chars in ()
        game = re.sub("\[.*?\]","",game)                    # Remove all chars in []
        game = re.sub(r"\s+", " ", game).strip(" ")         # Remove excess whitespace

        slug = re.sub(r"[^0-9A-Za-z']", " ", game)          # Split on nonword characters
        slug = slug.replace("'", "")                        # Strip apostrophe
        slug = re.sub(r"\s+", "-", slug).strip("-").lower() # Replace whitespace with dashes

        # Data for YML file
        '''
        config_file = '{slug}-{ts}'.format(slug=slug, ts=ts)
        config_file_path = os.path.join(args.lutris_yml_dir, "{}.yml".format(config_file))
        config = {
            args.runner: {},
            "game": {
                "main_file": file
            },
            "system": {}
        }

        if args.game_options is not None:
            config['game'].update(args.game_options)
'''
        # Data for Lutris DB
        values = {
            "id": game_id,
            "name": game,
            "slug": slug,
            "extension": EXT_MAP[args.platform],
            "installer_slug": None,
            "parent_slug": None,
            "platform": args.platform,
            "runner": args.runner,
            "retroarch_core": None if args.core is None or args.core == '' else args.core,
            "steam_id": None,
            "executable": None,
            "directory": args.lutris_game_dir,
            "game_directory": file,
            "updated": None,
            "lastplayed": 0,
            "installed": 1,
            "installed_at": ts,
            "year": None,
            "configpath": slug + '-' + str(ts),
            "has_custom_banner": None,
            "has_custom_icon": None,
            "playtime": None,
            "hidden": 0,
            "service": None,
            "service_id": None
        }

        # Output to console
        if args.no_write:
            print("file: {}".format(file))
            print("SQLite:\n{}".format(values)),
            #print("YML at {ymlfile}:\n{config}\n".format(ymlfile=config_file_path,
             #                                            config=yaml.dump(config, default_flow_style=False)))

        # Write to DB/filesystem
        else:
           # with open(config_file_path, 'w') as f:
            #    yaml.dump(config, f, default_flow_style=False)

            query = "INSERT INTO games ({columns}) VALUES ({placeholders})".format(
                columns = ','.join(values.keys()),
                placeholders = ','.join('?' * len(values))
            )

            cur.execute(query, list(values.values()))
            conn.commit()

        game_id += 1


if __name__ == '__main__':
    main()
