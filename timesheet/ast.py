import datetime
import calendar
import collections
import timesheet.parser

DAYLY_SOLL_TIME = datetime.timedelta(hours=7, minutes=48)
PAUSE_THRESHOLD = datetime.timedelta(hours=5, minutes=0)
LAUNCH_PAUSE = datetime.timedelta(minutes=45)
PADDING = 36 * ' '
BASE = '{0} {1:%d.%m.%Y} '


def print_diff(delta, default_plus=' '):
    sign, time = timesheet.diff_split(delta, default_plus)
    return '{0}{1}'.format(sign, time)


def calc_total(work):
    def diff_time_span(time_span):
        start = datetime.datetime.combine(work.date, time_span.start)
        end = datetime.datetime.combine(work.date, time_span.end)
        return end - start

    def calc_pause(a, b):
        b_start = datetime.datetime.combine(work.date, b.start)
        a_end = datetime.datetime.combine(work.date, a.end)
        return b_start - a_end

    total_time = sum(map(diff_time_span, work.time_spans), timesheet.ZERO_DT)
    double_iterator = ((x, y) for x, y in zip(work.time_spans, work.time_spans[1:]))
    pause = sum((calc_pause(*x) for x in double_iterator), timesheet.ZERO_DT)

    if total_time > PAUSE_THRESHOLD and pause < LAUNCH_PAUSE:
        pause = LAUNCH_PAUSE

    return total_time, pause


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
        return fmt_str.format(timesheet.weekday_str(self.weekday),
                              self.date,
                              self.comment)


class TimeSpan(Node):
    start = V()
    end = V()
    pause = V(datetime.timedelta(0))

    def pprint(self):
        return '{:%H:%M} -- {:%H:%M}'.format(self.start, self.end)


class Work(Node):
    date = V()
    weekday = V()
    total = V()
    saldo = V()
    time_spans = V()
    pause = V(datetime.timedelta(0))

    def check(self):
        total, pause = calc_total(self)
        return (total == self.total and
                self.weekday == self.date.weekday())

    def calc(self):
        new_total, new_pause = calc_total(self)
        new_saldo = new_total - DAYLY_SOLL_TIME - LAUNCH_PAUSE
        return Work(self.date,
                    self.date.weekday(),
                    new_total,
                    new_saldo,
                    self.time_spans,
                    new_pause)

    @property
    def start(self):
        return min(self.time_spans, key=lambda x: x.start).start

    @property
    def end(self):
        return max(self.time_spans, key=lambda x: x.end).end

    def pprint(self):
        time_span_str = '\n                  '.join(map(TimeSpan.pprint, self.time_spans))
        if self.total is None:
            fmt_str = (BASE + '   {2}')
        else:
            fmt_str = (BASE + '   {2}    | ({3}) {4:>6} => {5}')
        return fmt_str.format(timesheet.weekday_str(self.weekday),
                              self.date,
                              time_span_str,
                              print_diff(self.pause, '-'),
                              print_diff(self.total),
                              print_diff(self.saldo))


class Unfinished(Work):
    start = V()

    @staticmethod
    def now():
        dt_now = datetime.datetime.now()
        return Unfinished(date=dt_now.date(),
                          start=dt_now.time(),
                          weekday=dt_now.weekday())

    def pprint(self):
        fmt_str = (BASE + '   {2:%H:%M} --')
        return fmt_str.format(timesheet.weekday_str(self.weekday),
                              self.date,
                              self.start)

    def check(self):
        return False

    def calc(self):
        self.end = datetime.datetime.now().time()
        return super().calc()


class SubUnfinished(Node):
    start = V()

    def pprint(self):
        fmt_str = ('                     {:%H:%M} --')
        return fmt_str.format(self.start)

    def check(self):
        return False

    def calc(self):
        self.end = datetime.datetime.now().time()
        return SubFinished(self.start, self.end)


class SubFinished(Node):
    start = V()
    end = V()

    def pprint(self):
        fmt_str = ('                     {:%H:%M} -- {:%H:%M}')
        return fmt_str.format(self.start, self.end)

    def check(self):
        return False

    def calc(self):
        self.end = datetime.datetime.now().time()
        return super().calc()


class Balance(Node):
    balance = V()

    @classmethod
    def zero(cls):
        return Balance(timesheet.timesheet.ZERO_DT)

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


class TimeSheetSemantics(timesheet.parser.TimeSheetSemantics):
    def start(self, ast):
        return ast

    def line(self, ast):
        return ast

    def special_line(self, ast):
        return Special(**ast)

    def time_span(self, ast):
        return TimeSpan(**ast)

    def work_line(self, ast):
        return Work(**ast)

    def unfinished(self, ast):
        return Unfinished(**ast)

    def sub_unfinished(self, ast):
        return SubUnfinished(**ast)

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
