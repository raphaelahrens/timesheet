#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

import timesheet

TS_PARSER = timesheet.parser.TimeSheetParser(semantics=timesheet.ast.TimeSheetSemantics())


def pprint(tree):
    for node in tree:
        print(node.pprint())
    return 0


class Cmd(object):
    all = {}

    def __init__(self, name, fn, rule_name='start'):
        self.fn = fn
        self.rule_name = rule_name

        Cmd.all[name] = self

    def execute(self, args):
        tree = TS_PARSER.parse(args.file.read(), rule_name=self.rule_name)
        return self.fn(tree)

    @classmethod
    def get(cls, name):
        return cls.all[name]

    @classmethod
    def run(cls, args):
        name = args.command
        cmd = cls.get(name)
        return pprint(cmd.execute(args))


class NoInputCmd(Cmd):
    def execute(self, args):
        return self.fn()


Cmd('check', timesheet.check)
Cmd('balance', timesheet.balance)
Cmd('sum', timesheet.time_sum)
Cmd('print', lambda x: x)
Cmd('fill', timesheet.fill)
Cmd('logout', timesheet.logout, rule_name='sp_unfinished')
Cmd('calc', timesheet.calc)
Cmd('report', timesheet.report)

NoInputCmd('login', timesheet.login)

LIST_CMDS = ' '.join(Cmd.all.keys())


def parse_args(args):
    parser = argparse.ArgumentParser(description='Timesheet')
    parser.add_argument('command', type=str, help='timesheet commando [{}]'.format(LIST_CMDS))
    parser.add_argument('file', type=argparse.FileType('r'), nargs='?', default='-',
                        help='The timesheet file')
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    return Cmd.run(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
