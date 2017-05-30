
.PHONY: clean test all

all: timesheet/parser.py test

timesheet/parser.py: data/timesheet.ebnf
	python3 -m tatsu data/timesheet.ebnf -m TimeSheet -o timesheet/parser.py

clean:
	rm timesheet/parser.py
