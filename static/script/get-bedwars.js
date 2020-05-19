function populateTable(tableData) {
    for (i = 0; i < tableData[0].length; i++) {
        document.querySelector('#allTimeHead').innerHTML += `<th>${tableData[0][i]}</th>`;
    }
    
    var specialTable = document.querySelector('#allTimeBody');

    for (i = 1; i < tableData.length; i++) {
        var row = tableData[i];
        var cells = '';
        for (j = 0; j < row.length; j++) {
            cells += `<td>${row[j]}</td>`;
        }
        specialTable.innerHTML += `<tr>${cells}</tr>`;
    }

    const wholeTable = document.querySelector('#hiddenTable');
    const loadingBar = document.querySelector('#loadingBar');

    wholeTable.style.visibility = 'visible';
    wholeTable.style.margin = 'auto';
    loadingBar.style.visibility = 'hidden';
}

function evaluateExpression(expression) {
    let evaluated = Math.round(eval(expression) * 100) / 100;
    let str = evaluated.toString().split('.');

    if (str[0].length > 3) {
        str[0] = str[0].replace(/(\d)(?=(\d{3})+$)/g, '$1,');
    }

    return str.join('.');
}

function getStat(dataset, key) {
    keys = key.split('.');
    let data = dataset;
    for (let k = 0; k < keys.length; k++) {
        let currentKey = keys[k];
        data = data[keys[k]];
    }

    return data.replace(',', '');
}

function getBedwarsData(datasets) {
    let result = [];
    let keyPattern = /\^[^^$]+\.[^^$]+\$/gi;

    let rows = ['^Solo.Wins$ #Solo Wins', '^Doubles.Wins$ #Doubles Wins', '^3v3v3v3.Wins$ #3v3v3v3 Wins',
                '^4v4v4v4.Wins$ #4v4v4v4 Wins', '^4v4.Wins$ #4v4 Wins', '^Overall.Wins$ #Total Wins', 
                '^Overall.Wins$ / (^Overall.Wins$ + ^Overall.Losses$) #Win Rate', '^Overall.Kills$ #Kills', 
                '^Overall.K/D$ #K/D', '^Overall.Final Kills$ #Final Kills', '^Overall.Final K/D$ #Final K/D', 
                '^Overall.Kills$ + ^Overall.Final Kills$ #Total Kills'];

    let igns = Object.keys(datasets);

    result.push([''].concat(igns));

    for (let j = 0; j < rows.length; j++) {
        let current = [];

        let row = rows[j];
        let params = row.split('#');
        let key = params[0];
        let displayName = params[1];

        current.push(displayName);

        for (let i = 0; i < igns.length; i++) {
            let ign = igns[i];
            let dataset = JSON.parse(datasets[ign]);
            let plugged = key.split('#')[0].replace(keyPattern, function (x) {
                let subString = x.substring(1, x.length - 1);
                let replacement = getStat(dataset, subString);
                return replacement;
            });

            let evaluation = evaluateExpression(plugged);

            current.push(evaluation);
        }

        result.push(current);
    }

    populateTable(result);
}

function getPlayerPages(igns) {
    let result = {};
    let desiredLength = igns.length;

    for (let i = 0; i < igns.length; i++) {
        let ign = igns[i];
        let url = `/plancke/${ign}`;
        let req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {
                result[ign] = req.responseText;
            } else if (this.readyState == 4 && this.status === 400) {
                desiredLength -= 1;
            }

            if (desiredLength === 0) {
                document.querySelector('#allTimeButton').style.display = 'none';
                document.querySelector('#scroll-tab-10').style.visibility = 'hidden';
            } else if (Object.keys(result).length === desiredLength) {
                // All users have data, move on to the next function
                getBedwarsData(result);
            }
        };

        req.open('GET', url);
        req.send();
    }
}

getPlayerPages(usernames);
