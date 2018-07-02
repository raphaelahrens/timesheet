import itertools
import traceback
import datetime

import timesheet

HEAD = r'''
\documentclass[paper=a4,fontsize=10pt]{scrartcl}
\usepackage{tsreport}'''
DATE = r'\newdate{{monthdate}}{{ {0:%Y} }}{{ {0:%m} }}{{ {0:%d} }}'
BEGIN = r'''
\begin{document}
\begin{report}
\begin{timesheet}'''

CLOSE = r'''
\end{timesheet}
\end{report}
\end{document}'''

START_WEEK = r'\startweek'
CLOSE_WEEK = r'\closeweek'
HEAD_LINE = r'\headline'

CLOSE_MONTH = r'\closemonth{{ {sign} }}{{ {balance} }}{{ {text} }}'

SPECIAL_DAY = r'{weekday} & {date:%d.%m.%Y} &\multicolumn{{4}}{{c}}{{\textbf{{ {comment} }}}}&&\\'
WORK_DAY = r'{weekday} & {date:%d.%m.%Y} & 7,8 Std & {start:%H:%M} & {end:%H:%M}& {work_time} & {sign} & {saldo} \\'


class Report(object):
    def __init__(self, string):
        self.string = string

    def pprint(self):
        return self.string


def process_special_day(node):
    return SPECIAL_DAY.format(weekday=timesheet.weekday_str(node.weekday),
                              date=node.date,
                              comment=node.comment)


def process_work_day(node):
    sign, saldo = timesheet.diff_split(node.saldo, '+')
    _, work_time = timesheet.diff_split(node.total - node.pause)
    return WORK_DAY.format(weekday=timesheet.weekday_str(node.weekday),
                           date=node.date,
                           start=node.start,
                           end=node.end,
                           work_time=work_time,
                           saldo=saldo,
                           sign=sign)


def process_balance_node(node, text):
    sign, balance = timesheet.diff_split(node.balance, '+')
    return CLOSE_MONTH.format(sign=sign,
                              balance=balance,
                              text=text)


def process_balance_start(node):
    balance_line = process_balance_node(node, '')
    global process_balance
    process_balance = process_balance_end
    return '\n'.join((balance_line, HEAD_LINE, START_WEEK))


def process_balance_end(node):
    balance_line = process_balance_node(node, 'Übertrag in den Folgemonat')
    global process_balance
    process_balance = process_balance_start
    return '\n'.join((CLOSE_WEEK, balance_line))


process_balance = process_balance_start


def process_to_str(node):
    node_type = type(node)
    if node_type is timesheet.ast.Special:
        return process_special_day(node)
    elif node_type is timesheet.ast.Work:
        return process_work_day(node)
    elif node_type is timesheet.ast.Balance:
        return process_balance(node)
    return ''


def process(node):
    try:
        return Report(process_to_str(node))
    except:
        return Report('|'.join(traceback.format_exc().splitlines()))


def report(tree):
    date = DATE.format(datetime.datetime.now().date())
    start = (Report(x) for x in (HEAD, date, BEGIN))
    days = (timesheet.latex.process(node) for node in tree)
    end = (Report(CLOSE),)
    return itertools.chain(start, days, end)
