import calendar
import datetime
import itertools

import timesheet.ast


def check(tree):
    node_list = list(itertools.filterfalse(lambda x: x.check(), tree))
    correct_list = [x.calc() for x in node_list]
    return list(itertools.chain(*zip(node_list, correct_list)))


def login():
    login_node = timesheet.ast.Unfinished.now()
    return [login_node]


def logout(tree):
    last_node = tree[-1]
    if isinstance(last_node, timesheet.ast.Unfinished):
        end_time = datetime.datetime.now().time()
        time_spans = last_node.time_spans + [timesheet.ast.TimeSpan(start=last_node.start, end=end_time)]
        finished_node = timesheet.ast.Work(date=last_node.date,
                                           time_spans=time_spans,
                                           weekday=last_node.weekday)
        return tree[:-1] + [finished_node]
    elif isinstance(last_node, timesheet.ast.SubUnfinished):
        end_time = datetime.datetime.now().time()
        finished_node = timesheet.ast.SubFinished(start=last_node.start, end=end_time)
                                           
        return tree[:-1] + [finished_node]
    else:
        return tree


def is_day(node):
    return isinstance(node, (timesheet.ast.Work, timesheet.ast.Special))


def is_balance(node):
    return type(node) is timesheet.ast.Balance


def fill(tree):
    def gen_days(tree):
        work_day_gen = (node.date for node in tree if is_day(node))
        next_record_date = next(work_day_gen)
        day = next_record_date.replace(day=1)
        for node in tree:
            if not is_day(node):
                yield node
            else:
                while day < next_record_date:
                    if day.weekday() != calendar.SUNDAY:
                        yield timesheet.ast.Special(date=day,
                                                    comment='"-"',
                                                    weekday=day.weekday())
                    day = day + datetime.timedelta(days=1)
                yield node
                day = day + datetime.timedelta(days=1)
                try:
                    next_record_date = next(work_day_gen)
                except StopIteration:
                    pass
    return gen_days(tree)


def takeuntil(predicate, iterable, not_found=None):
    # takeuntil(lambda x: x > 5, [1,4,6,4,1]) --> 1 4 6
    for x in iterable:
        if predicate(x):
            yield x
            return
        else:
            yield x
    else:
        yield not_found


def balance(tree):
    last_days = list(takeuntil(is_balance, reversed(tree),
                               timesheet.ast.Balance.zero()))
    balance_node = sum(last_days[:-1], last_days[-1])
    return tree + [balance_node]


def calc(tree):
    def calc_work(node):
        if type(node) is timesheet.ast.Work:
            return node.calc()
        return node

    return map(calc_work, tree)


def time_sum(tree):
    last_days = itertools.takewhile(is_day, reversed(tree))
    sum_node = sum(last_days, timesheet.ast.Month.zero())
    return tree + [sum_node]
