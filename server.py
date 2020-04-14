import json
import requests

import tools

from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

@app.route('/')
def home_page():
    return send_from_directory('templates', 'index.html')


@app.route('/bedwars')
@app.route('/bedwars/')
def bedwars():
    # get a list of the usernames, make sure they are lowercase
    usernames = list(map(lambda x: x.lower(), request.args.get('igns').split('.')))
    data_file = request.args.get('file')

    req = requests.get('https://raw.githubusercontent.com/joshuaSmith2021/chamosbot-data/master/{0}.json'.format(data_file))
    if req.status_code != 200:
        # File not found, revert to default file
        fallback_file = 'today'
        req = requests.get('https://raw.githubusercontent.com/joshuaSmith2021/chamosbot-data/master/{0}.json'.format(fallback_file))
    stat_file = req.json()

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
    datasets = {'kills': [], 'finals': [], 'kdrs': [], 'fkdrs': [],
                'wins': [], 'winRate': [], 'kpg': [], 'fkpg': [],
                'deaths': [], 'final_deaths': [], 'played': []}

    for field in datasets.keys():
        for username in usernames:
            datasets[field].append({'label': username, 'data': [], 'fill': False})


    for time in times[::-1]:
        dataset = stat_file[time]
        for username in usernames:
            # if user does not have an entry for the given time, just repeat the previous time
            if username not in dataset.keys():
                for field, lst in datasets.items():
                    datasets[field][usernames.index(username)]['data'].append(datasets[field][usernames.index(username)]['data'][-1])
                
        for user, stats in filter(lambda x: x[0] in usernames, dataset.items()):
            user_index = usernames.index(user)
            bedwars = stats['Bedwars']
            datasets['kills'][user_index]['data'].append(bedwars['kills_bedwars'])
            datasets['deaths'][user_index]['data'].append(bedwars['deaths_bedwars'])
            datasets['finals'][user_index]['data'].append(bedwars['final_kills_bedwars'])
            datasets['final_deaths'][user_index]['data'].append(bedwars['final_deaths_bedwars'])
            datasets['kdrs'][user_index]['data'].append(round(bedwars['kills_bedwars'] / bedwars['deaths_bedwars'] * 1000) / 1000) 
            datasets['fkdrs'][user_index]['data'].append(round(bedwars['final_kills_bedwars'] / bedwars['final_deaths_bedwars'] * 1000) / 1000)
            datasets['wins'][user_index]['data'].append(bedwars['wins_bedwars'])
            datasets['played'][user_index]['data'].append(bedwars['games_played_bedwars'])
            datasets['winRate'][user_index]['data'].append(round(bedwars['wins_bedwars'] / bedwars['games_played_bedwars'] * 1000) / 1000)
            datasets['kpg'][user_index]['data'].append(round(bedwars['kills_bedwars'] / bedwars['games_played_bedwars'] * 1000) / 1000)
            datasets['fkpg'][user_index]['data'].append(round(bedwars['final_kills_bedwars'] / bedwars['games_played_bedwars'] * 1000) / 1000)

    performances = []
    perfKeys = [
        ('kills', 'Kills'),
        ('finals', 'Final Kills'),
        ('!kdr', 'KDR'),
        ('!fkdr', 'FKDR'),
        ('wins', 'Wins'),
        ('!winRate', 'Win Rate')
        ]

    performances.append([''] + usernames)
    for i, pair in enumerate(perfKeys):
        dset, display = pair
        performances.append([display])
        for j, username in enumerate(usernames):
            result = None
            if dset[0] == '!':
                try:
                    if dset[1:] == 'kdr':
                        kill_data = datasets['kills'][j]['data']
                        death_data = datasets['deaths'][j]['data']
                        kills = kill_data[0] - kill_data[-1]
                        deaths = death_data[0] - death_data[-1]
                        print(deaths)
                        result = round(kills / deaths * 1000) / 1000
                    elif dset[1:] == 'fkdr':
                        kill_data = datasets['finals'][j]['data']
                        death_data = datasets['final_deaths'][j]['data']
                        kills = kill_data[0] - kill_data[-1]
                        deaths = death_data[0] - death_data[-1]
                        result = round(kills / deaths * 1000) / 1000
                    elif dset[1:] == 'winRate':
                        kill_data = datasets['wins'][j]['data']
                        death_data = datasets['played'][j]['data']
                        kills = kill_data[0] - kill_data[-1]
                        deaths = death_data[0] - death_data[-1]
                        result = round(kills / deaths * 1000) / 1000
                except ZeroDivisionError as err:
                    # A user has had no deaths, final deaths, or games played
                    #   in the specified time frame, so zerodivision happens.
                    #   Just return not available... for now...
                    result = 'Not Available'
                    #raise(err)
            else:
                dataset = datasets[dset][j]['data']
                result   = dataset[0] - dataset[-1]
            performances[-1].append(result)


    colores = ['#ff6384', '#ff9f40', '#ffcd56', '#4bc0c0', '#36c0eb', '#9966ff', '#c9cbcf']
    for field, lst in datasets.items():
        for i in range(len(lst)):
            lst[i]['borderColor'] = colores[i]
            lst[i]['data'].reverse()

        # put fields in json format for javascript to read later
        datasets[field] = json.dumps(lst)

    datasets['table'] = json.dumps(performances)
    print('Rendering template...')
    print(datasets)
    return render_template('bedwars.html', display_times=json.dumps(display_times), datasets=datasets, usernames=json.dumps(usernames))
