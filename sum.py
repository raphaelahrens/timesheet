#!/usr/bin/env python3
import datetime
import fileinput
import re
import deltaformat

SOLL_TIME = datetime.timedelta(hours=30, minutes=48)


def main():
    reg = re.compile(r'.+\|\s*(?P<hours>[0-9]+):(?P<minutes>[0-5][0-9]):(?P<seconds>[0-5][0-9])\s*')
    work_sum = datetime.timedelta()
    time_count = 0
    for line in fileinput.input():
        matched = reg.match(line)
        check = ''
        if matched is not None:
            hours = int(matched.group("hours"), base=10)
            minutes = int(matched.group("minutes"), base=10)
            seconds = int(matched.group("seconds"), base=10)
            work_sum += datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            time_count += 1
            check = ' ✓'

        print(line[:-1] + check)
    pause_sum = datetime.timedelta(minutes=45) * time_count
    padding = ' ' * 30
    total = work_sum - pause_sum
    print("{padding}=>{work:^7}-{pause:^7}-{soll:^7}= ({total:^7},{diff:^7})".format(
        padding=padding,
        work=deltaformat.h_and_mins(work_sum),
        pause=deltaformat.h_and_mins(pause_sum),
        total=deltaformat.h_and_mins(total),
        soll=deltaformat.h_and_mins(SOLL_TIME),
        diff=deltaformat.h_and_mins(total - SOLL_TIME)))
    return 0

if __name__ == "__main__":
    main()
