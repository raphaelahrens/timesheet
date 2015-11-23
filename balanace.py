#!/usr/bin/env python3
import datetime
import fileinput
import re
import deltaformat


def main():
    reg = re.compile(r'\s*=>.*\(.*, (?P<sign>[- ])(?P<hours>[0-9]+):(?P<minutes>[0-5][0-9])\s*\)')
    balance = datetime.timedelta()
    for line in fileinput.input():
        matched = reg.match(line)
        if matched is not None:
            hours = int(matched.group("hours"), base=10)
            minutes = int(matched.group("minutes"), base=10)
            sign = matched.group("sign")
            delta = datetime.timedelta(hours=hours, minutes=minutes)
            if sign == "-":
                balance -= delta
                print(' -{0:>7}'.format(deltaformat.h_and_mins(delta)))
            else:
                balance += delta
                print(' +{0:>7}'.format(deltaformat.h_and_mins(delta)))
    print('─' * 9)
    print('{0:>9}'.format(deltaformat.h_and_mins(balance)))


if __name__ == "__main__":
    main()
