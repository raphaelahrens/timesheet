#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

import timesheet


def parse_args(args):
    parser = argparse.ArgumentParser(description='Timesheet')
    parser.add_argument('command', type=str, help='timesheet commando')
    parser.add_argument('file', type=argparse.FileType('r'), nargs='?', default='-',
                        help='The timesheet file')
    return parser.parse_args(args)


def pprint(tree):
    for node in tree:
        print(node.pprint())
    return 0


commands = {'check': timesheet.check,
            'balance': timesheet.balance,
            'sum': timesheet.time_sum,
            'print': pprint,
            'fill': timesheet.fill,
            'logout': timesheet.logout,
            'calc': timesheet.calc}

no_input_cmds = {'login': timesheet.login}


def run_cmd(cmd, args):
    ts_parser = timesheet.parser.TimeSheetParser(semantics=timesheet.ast.TimeSheetSemantics())
    tree = ts_parser.parse(args.file.read())

    return pprint(cmd(tree))


def run_no_input_cmd(cmd, args):
    return pprint(cmd())


def main():
    args = parse_args(sys.argv[1:])
    cmd_str = args.command
    if cmd_str in commands:
        return run_cmd(commands[cmd_str], args)
    elif cmd_str in no_input_cmds:
        return run_no_input_cmd(no_input_cmds[cmd_str], args)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
