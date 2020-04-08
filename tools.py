import re
import calendar

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


def key_index(lst, key, val):
    for i, item in enumerate(lst):
        if item[key] == val:
            return i
    raise ValueError("Dictionary with dict['{0}']: {1} is not in list".format(key, val))
