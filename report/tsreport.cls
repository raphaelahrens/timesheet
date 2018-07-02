\NeedsTeXFormat{LaTeX2e}[1994/06/01]
\ProvidesClass{tsreport}[2013/04/29 v1.5.1 modern curriculum vitae and letter document class]
%-------------------------------------------------------------------------------
%                class options
%
% (need to be done before the external package loading, for example because
% we need \paperwidth, \paperheight and \@ptsize to be defined before loading
% geometry and fancyhdr)
%-------------------------------------------------------------------------------
% paper size option
\DeclareOption{a4paper}{%
  \setlength\paperheight{297mm}
  \setlength\paperwidth{210mm}}
\DeclareOption{a5paper}{%
  \setlength\paperheight{210mm}
  \setlength\paperwidth{148mm}}
\DeclareOption{b5paper}{%
  \setlength\paperheight{250mm}
  \setlength\paperwidth{176mm}}

% font size options
\newcommand\@ptsize{}
\DeclareOption{10pt}{\renewcommand\@ptsize{1}}
\DeclareOption{11pt}{\renewcommand\@ptsize{1}}
\DeclareOption{12pt}{\renewcommand\@ptsize{2}}
% font type options
\DeclareOption{sans}{\AtBeginDocument{\renewcommand{\familydefault}{\sfdefault}}}
\DeclareOption{roman}{\AtBeginDocument{\renewcommand{\familydefault}{\rmdefault}}}

% execute default options
\ExecuteOptions{a4paper,10pt}

% process given options
\ProcessOptions\relax
\input{size1\@ptsize.clo}

%-------------------------------------------------------------------------------
%                required packages
%-------------------------------------------------------------------------------
% \AtEndPreamble hook (loading etoolbox instead of defining the macro, as to avoid incompatibilities with etoolbox (and packages relying on it) defining the macro too)
\RequirePackage{graphicx}

\RequirePackage{datetime}% deutsch

\newdateformat{monthyeardate}{%
  \monthname[\THEMONTH], \THEYEAR}

\newdateformat{daymonthyeardate}{%
  \twodigit{\THEDAY}.\twodigit{\THEMONTH}.\THEYEAR}

\renewcommand*\rmdefault{iwona}

\newcommand*{\Signature}[2]{%
    \parbox{2.0in}{%
          \begin{tabular}{l}%
            #2\\%
            \hline%
            #1%
          \end{tabular}%
    }%
}%

\newcommand*{\headline}{%
  \textbf{Tag} & \textbf{Datum} & \textbf{nominelle} & \multicolumn{2}{c}{\textbf{Uhrzeit}} & \multicolumn{2}{c}{\textbf{Zeitsalden}}\\
                     &                & \textbf{Arbeitszeit} & \textbf{Arbeitsbeginn} & \textbf{Arbeitsende} &                    &\\
        \multicolumn{7}{l}{}                    \\ %
}

\newenvironment{report}{%
\parbox{6cm}{%
    {\huge \textbf Arbeitszeitkonto}\\
    {\large \monthyeardate\displaydate{monthdate}}
}
\hfill
\raisebox{-.5\height}{\includegraphics[width=0.33\textwidth]{fraunhofer.png}}
\vspace{1.5cm}
\Signature{Name, Vorname}{Ahrens, Raphael} \hspace{3cm} \Signature{Org. - Einheit}{310}
\vspace{1cm}
}{%
\vspace{2cm}
\Signature{Datum, Unterschift des Mitarbeiters}{\daymonthyeardate\today ,} \hspace{3cm} \Signature{Datum, Unterschift des Vorgesetzten}{}
}
\newenvironment{timesheet}{%
    \begin{tabular}{lllllcl}%
        \multicolumn{7}{l}{}                    \\ %
}{%
    \end{tabular}
}%

\newcommand*{\startweek}{\hline}
\newcommand*{\closeweek}{%
    \hline%
    \multicolumn{7}{l}{}                    \\ %
}
\newcommand*{\closemonth}[3]{%
    \multicolumn{5}{l}{#3}                    & #1 & #2\\ %
    \multicolumn{7}{l}{}                    \\ %
}

\setlength\parindent{0pt}

\newdate{monthdate}{1}{12}{2016}
