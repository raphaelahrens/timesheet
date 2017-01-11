import datetime
import calendar
import collections
import timesheet.tsparser

DAYLY_SOLL_TIME = datetime.timedelta(hours=7, minutes=48)
LAUNCH_PAUSE = datetime.timedelta(minutes=45)
PADDING = 36 * ' '
BASE = '{0} {1:%d.%m.%Y} '


def print_diff(delta):
    if delta is None:
        return ''
    sign = ' '
    if delta < datetime.timedelta():
        sign = '-'
        delta = abs(delta)
    hours = (delta.days * 24) + (delta.seconds // 3600)
    minutes = delta.seconds // 60 % 60
    return '{0}{1:d}:{2:02d}'.format(sign, hours, minutes)


def calc_total(work):
    start = datetime.datetime.combine(work.date, work.start)
    end = datetime.datetime.combine(work.date, work.end)
    return end - start


class V(object):
    def __init__(self, default=None):
        self.default = default


class NodeMeta(type):

    @classmethod
    def __prepare__(mcs, _name, _bases):
        return collections.OrderedDict()

    def __new__(mcs, clsname, bases, dct):
        attr = {}
        value_set = set()
        arg_list = []
        for name, val in dct.items():
            if isinstance(val, V):
                value_set.add(name)
                attr[name] = val.default
                arg_list.append(name)
            else:
                attr[name] = val
        attr["_value_set"] = value_set
        attr["_arg_list"] = arg_list
        return type.__new__(mcs, clsname, bases, attr)


class Node(object, metaclass=NodeMeta):
    def __init__(self, *args, **kwargs):
        for k, v in zip(range(len(args)), args):
            setattr(self, self._arg_list[k], v)
        for k, v in kwargs.items():
            setattr(self, k, v)


class Special(Node):
    date = V()
    comment = V()
    weekday = V()

    def check(self):
        return True

    def calc(self):
        return self

    def pprint(self):
        fmt_str = BASE + '{2:^20} |'
        return fmt_str.format(calendar.day_abbr[self.weekday],
                              self.date,
                              self.comment)


class Work(Node):
    date = V()
    start = V()
    end = V()
    weekday = V()
    total = V()
    saldo = V()
    done = V(default=True)

    def check(self):
        return (calc_total(self) == self.total and
                self.weekday == self.date.weekday())

    def calc(self):
        new_total = calc_total(self)
        new_saldo = new_total - DAYLY_SOLL_TIME - LAUNCH_PAUSE
        return Work(self.date, self.start, self.end, self.date.weekday(), new_total, new_saldo, self.done)

    def pprint(self):
        if self.total is None:
            fmt_str = (BASE + '   {2:%H:%M} -- {3:%H:%M}')
        else:
            fmt_str = (BASE + '   {2:%H:%M} -- {3:%H:%M}    | {4:>6} => {5}')
        return fmt_str.format(calendar.day_abbr[self.weekday],
                              self.date,
                              self.start,
                              self.end,
                              print_diff(self.total),
                              print_diff(self.saldo))


class Unfinished(Work):
    @staticmethod
    def now():
        dt_now = datetime.datetime.now()
        return Unfinished(date=dt_now.date(),
                          start=dt_now.time(),
                          weekday=dt_now.weekday())

    def pprint(self):
        fmt_str = (BASE + '   {2:%H:%M} --')
        return fmt_str.format(calendar.day_abbr[self.weekday],
                              self.date,
                              self.start)

    def check(self):
        return False

    def calc(self):
        self.end = datetime.datetime.now().time()
        return super().calc()


class Balance(Node):
    balance = V()

    @classmethod
    def zero(cls):
        return Balance(datetime.timedelta(0))

    def check(self):
        return True

    def calc(self):
        return self

    def pprint(self):
        fmt_str = PADDING + '-> Balance = {0}'
        return (fmt_str.format(print_diff(self.balance)))

    def __add__(self, obj):
        if type(obj) is Work:
            return Balance(self.balance + obj.saldo)
        return self


class Month(Node):
    total = V()
    soll = V()
    breaks = V()
    work = V()
    diff = V()

    @classmethod
    def zero(cls):
        total = datetime.timedelta(0)
        soll = datetime.timedelta(0)
        breaks = datetime.timedelta(0)
        return Month(total, soll, breaks)

    def check(self):
        return True

    def calc(self):
        work = self.total - self.breaks
        diff = work - self.soll
        return Month(self.total, self.soll, self.breaks, work, diff)

    def pprint(self):
        return (PADDING + '=>{work:^9}-{pause:^7}-{soll:^7}= ({total:^7},{diff:^7})'.format(
                work=print_diff(self.total),
                pause=print_diff(self.breaks),
                total=print_diff(self.work),
                soll=print_diff(self.soll),
                diff=print_diff(self.diff)))

    def __add__(self, obj):
        if type(obj) is Work:
            total = self.total + obj.total
            soll = self.soll + DAYLY_SOLL_TIME
            breaks = self.breaks + LAUNCH_PAUSE
            return Month(total, soll, breaks).calc()
        return self


WEEKDAYS = {day: n for day, n in zip(calendar.day_abbr, range(7))}


class TimeSheetSemantics(timesheet.tsparser.TimeSheetSemantics):
    def start(self, ast):
        return ast

    def line(self, ast):
        return ast

    def special_line(self, ast):
        return Special(**ast)

    def work_line(self, ast):
        return Work(**ast)

    def unfinished(self, ast):
        return Unfinished(**ast)

    def sum_line(self, ast):
        return Month(**ast)

    def balance_line(self, ast):
        return Balance(ast)

    def date(self, ast):
        return datetime.date(day=ast['day'], month=ast['month'], year=ast['year'])

    def time(self, ast):
        return datetime.time(hour=ast['hour'], minute=ast['minute'])

    def diff(self, ast):
        delta = datetime.timedelta(hours=ast['hours'], minutes=ast['minutes'])
        if ast['sign']:
            return delta
        else:
            return -delta

    def DD(self, ast):
        return int(ast, 10)

    def YEAR(self, ast):
        return int(ast, 10)

    def ND(self, ast):
        return int(ast, 10)

    def SIGN(self, ast):
        return ast != '-'

    def weekday(self, ast):
        return WEEKDAYS[ast]

    def string(self, ast):
        return ast
