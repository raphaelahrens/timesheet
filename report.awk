#!/usr/bin/awk -f

function absolute_time(time){
    if (substr(time, 1, 1) == "-") {
        return substr(time, 2)
    }
    return time
}

function get_sign(time) {
    if (substr(time, 1, 1) == "-") {
        return "-"
    }
    return "+"
}

function close_month(balance, text) {
    time=absolute_time(balance)
    sign=get_sign(balance)
    print "\\closemonth{" sign "}{" time "}{" text "}"
}

function start_week(){
    print "\\startweek"
}
function close_week(){
    print "\\closeweek"
}

function headline(){
    print "\\headline"
}

function previous_balance(prev_balance){
    close_month(prev_balance, "")
    headline()
    start_week()
}
function new_balance(n_balance){
    close_week()
    close_month(n_balance, "Übertrag in den Folgemonat")
}

BEGIN {
    balance = 0
    print "\\documentclass[paper=a4,fontsize=10pt]{scrartcl}"
    print "\\usepackage{tsreport}"
    print "\\newdate{monthdate}{1}{4}{2017}"
    print "\\begin{document}"
    print "\\begin{report}"
    print "\\begin{timesheet}"
    
}

/^$/{
    close_week()
    start_week()
}

/^[MTWDFS].. [0-9.]{10} +\"[^"]*\" +\|$/ {
    print $1 "&" $2 "&\\multicolumn{3}{c}{\\textbf{" substr($3,2,length($3)-2) "}}&&\\\\"
}

/^[MTWDS].. [0-9.]{10} +[0-9:]{5} -- [0-9:]{5} +\|.*$/{
    dayly_balance = $9
    time = absolute_time(dayly_balance)
    sign = get_sign(dayly_balance)
    print $1 "&" $2 "& 7,8 Std &" $3 "&" $5 "&" sign "&" time "\\\\"
}

/^ *-> Balance/  {
    if (balance == 0) {
        previous_balance($4)
    } else {
        new_balance($4)
    }
    balance = !balance
}
END{
    print "\\end{timesheet}"
    print "\\end{report}"
    print "\\end{document}"
}

