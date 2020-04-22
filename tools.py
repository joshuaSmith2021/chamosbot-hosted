import re
import calendar
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
