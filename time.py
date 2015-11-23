#!/usr/bin/env python3
from datetime import datetime
import fileinput
import re


FMT = '%H:%M'


def main():
    reg = re.compile(r'(([01][0-9]|2[0-4]):([0-5][0-9]))')

    for line in fileinput.input():
        result = reg.findall(line)
        if len(result) == 2:
            start_time = result[0][0]
            end_time = result[1][0]
            tdelta = datetime.strptime(end_time, FMT) - datetime.strptime(start_time, FMT)
            print("{0} |{1:>10}".format(line[:-1], str(tdelta)))
        else:
            print(line[:-1])

    return 0

if __name__ == "__main__":
    main()
