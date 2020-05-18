import requests
import re
import calendar
import json

from bs4 import BeautifulSoup
import yaml

def pretty_time(timestamp):
    # If date follows YYYYMMDD-HH0000 format:
    if re.match('^[0-9]{8}-[0-2][0-9]0{4}$', timestamp):
        month = calendar.month_name[int(timestamp[4:6])]
        day = timestamp[6:8] if timestamp[6] != '0' else timestamp[7]
        hourint = int(timestamp[9:11])
        hour = None
        if hourint == 0:
            hour = '12:00am'
        elif 0 < hourint < 12:
            hour = '{0}:00am'.format(hourint)
        elif hourint == 12:
            hour = '12:00pm'
        elif 12 < hourint < 24:
            hour = '{0}:00pm'.format(hourint - 12)

        return '{0} {1} {2}'.format(month, day, hour)

    elif re.match('^[0-9]{8}$', timestamp):
        month = calendar.month_name[int(timestamp[4:6])]
        day = timestamp[6:8] if timestamp[6] != '0' else timestamp[7]
        return '{0} {1}'.format(month, day)


def key_index(lst, key, val):
    for i, item in enumerate(lst):
        if item[key] == val:
            return i
    raise ValueError("Dictionary with dict['{0}']: {1} is not in list".format(key, val))


current_html = ''
def generate_html(elements):
    global current_html
    for element in elements:
        tag = element['type'].split('.')[0]
        classes = element['type'].split('.')[1:]
        content = element['content']
        current_html += '<{0} class="{1}">'.format(tag, ' '.join(classes))
        if type(content) == ''.__class__:
            # content is a string, just append the string to the result
            current_html += content
        elif type(content) == [].__class__:
            generate_html(content)
        else:
            raise SyntaxError('Invalid yaml input')
        current_html += '</{0}>'.format(tag)
    return current_html


def parse_yaml(path):
    result = None
    with open(path) as stream:
        try:
            result = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)
            result = None
    return result


def get_command(name):
    yaml_file_name = '{0}.yaml'.format(name)
    yaml_file_path = 'data/commands/{0}'.format(yaml_file_name)
    command = None
    with open(yaml_file_path) as stream:
        try:
            command = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)
            return None

        for i, section in enumerate(command['sections']):
            global current_html
            current_html = ''
            inner_html = generate_html(section['innerHTML'])
            section['innerHTML'] = inner_html
            command[i] = section

    return command


def get_player_pages(igns):
    # Get the Plancke page for each player
    if type(igns) == ''.__class__:
        igns = [igns]

    urls = [f'https://plancke.io/hypixel/player/stats/{ign}' for ign in igns]
    reqs = [requests.get(url) for url in urls]
    return [x.text for x in reqs]


def get_bw_data(page):
    # Get Bedwars data from their Plancke page
    soup = BeautifulSoup(page, features='html5lib')
    bw_div = soup.find('div', {'id': 'stat_panel_BedWars'})

    if bw_div is None:
        return 'Invalid username'

    bw_table = bw_div.findChild('table')

    table = []
    for row in [x for x in bw_table.descendants if x.name == 'tr'][1:]:
        # for cell in row.children:
        #     print(cell)
        cells = [x for x in row.strings if x != '\n']
        if cells == []:
            continue

        table.append(cells)

    stats = {}
    keys = table[0]
    gamemodes = [x[0] for x in table][1:]
    for row in table[1:]:
        zipped = list(zip(keys, row))
        gamemode = zipped[0][1]
        current = {}
        for key, stat in zipped[1:]:
            if key not in current.keys():
                current[key] = stat
            else:
                current['Final {0}'.format(key)] = stat

        stats[gamemode] = current

    return json.dumps(stats)

