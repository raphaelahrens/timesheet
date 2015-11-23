import datetime


def h_and_mins(delta):
    sign = ' '
    if delta < datetime.timedelta():
        sign = '-'
        delta = abs(delta)
    hours = (delta.days * 24) + (delta.seconds // 3600)
    minutes = delta.seconds // 60 % 60
    return '{0}{1:d}:{2:02d}'.format(sign, hours, minutes)
