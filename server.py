import json
import requests

import tools

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def greeting():
    return 'Hello, world!'

@app.route('/bedwars')
@app.route('/bedwars/')
def bedwars():
    # get a list of the usernames, make sure they are lowercase
    usernames = list(map(lambda x: x.lower(), request.args.get('igns').split('.')))
    stat_file = requests.get('https://raw.githubusercontent.com/joshuaSmith2021/chamosbot-data/master/data.json').json()

    # list of timestamps that have data for the specified usernames
    times = []
    # list of times to be displayed on tables
    display_times = []

    # See which times have an entry for any of the users
    for time, data in sorted(stat_file.items(), key=lambda x: x[0]):
        if not set(usernames).isdisjoint(data.keys()):
            times.append(time)

    display_times = [tools.pretty_time(time) for time in times]

    # Now build a dict containing all of the data for charts.js
    datasets = {'kills': [], 'finals': [], 'kdrs': [], 'fkdrs': [], 'wins': [], 'winRate': []}

    for field in datasets.keys():
        for username in usernames:
            datasets[field].append({'label': username, 'data': [], 'fill': False})


    for time in times[::-1]:
        dataset = stat_file[time]
        for username in usernames:
            # if user does not have an entry for the given time, just repeat the previous time
            if username not in dataset.keys():
                for field, lst in datasets.items():
                    datasets[field][usernames.index(username)]['data'].append(datasets[field][user_index]['data'][-1])
                
        for user, stats in filter(lambda x: x[0] in usernames, dataset.items()):
            user_index = usernames.index(user)
            bedwars = stats['Bedwars']
            datasets['kills'][user_index]['data'].append(bedwars['kills_bedwars'])
            datasets['finals'][user_index]['data'].append(bedwars['final_kills_bedwars'])
            datasets['kdrs'][user_index]['data'].append(round(bedwars['kills_bedwars'] / bedwars['deaths_bedwars'] * 1000) / 1000) 
            datasets['fkdrs'][user_index]['data'].append(round(bedwars['final_kills_bedwars'] / bedwars['final_kills_bedwars'] * 1000) / 1000)
            datasets['wins'][user_index]['data'].append(bedwars['wins_bedwars'])
            datasets['winRate'][user_index]['data'].append(round(bedwars['wins_bedwars'] / bedwars['games_played_bedwars'] * 1000) / 1000)

    for field, lst in datasets.items():
        datasets[field] = json.dumps(lst[::-1])

    print('Rendering template...')
    return render_template('bedwars.html', display_times=json.dumps(display_times), datasets=datasets)
