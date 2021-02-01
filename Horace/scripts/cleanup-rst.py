#!/usr/bin/env python3
"""
Code to convert from pandoc output to readable rst based on SPHINX standard
"""

import sys
import re
import argparse
import os.path


_parser = argparse.ArgumentParser(description='Convert source rst from pandoc to SPHINX standard', add_help=True)
_parser.add_argument('--input', '-i', help="Input file")
_parser.add_argument('--output', '-o', help="Output directory")
_parser.add_argument('--debug', action="store_true")

argList = _parser.parse_args()
if not argList.input:
    _parser.print_help()
    sys.exit()
if not os.path.isfile(argList.input):
    raise IOError(f"File {argList.input} not found")
if not os.path.isdir(argList.output):
    raise IOError(f"Directory {argList.output} not found")

DEBUG = argList.debug

# Lazy date RE for catching datestamp - Supports up to 2010-2039 date stamps in YYYY/MM/DD+rest
DATE_RE = r"20[0-3][0-9][01][0-9][0-3][0-9]+"

# New page determined by title datestamp
NEWPAGE_RE = re.compile(r"(?P<title>\w+)\s+"+DATE_RE)
TITLE_RE = re.compile(r"^\s*===(?P<subtitle>[^=]+?)===")
SUBTITLE_RE = re.compile(r"^\s*==(?P<subsubtitle>[^=]+)==")
MINORTITLE_RE = re.compile(r"^\s*=(?P<minortitle>[^=]+)=")
LIST_RE = re.compile(r"^([\\\*]*\*[\\\*]*\s*)")
LITERAL_BLOCK_RE = re.compile(r"\s*::")
PAPER_LIST_RE = re.compile(r"\\\*\*\\")
TABLE_START_RE = re.compile(r"{\\?\|")
TABLE_END_RE = re.compile(r"\|}")
IMAGE_RE = re.compile(r"\\ `(?P<size>[0-9]+px)\s*(\s|\|)\s*(?P<label>[^<]+)<image:(?P<path>[^>]+)>`__")
NL_RE = re.compile(r"\n")
ANY_MATCH_RE = re.compile("|".join(map(lambda r: r.pattern, (
    NEWPAGE_RE,
    TITLE_RE,
    SUBTITLE_RE,
    MINORTITLE_RE,
    LIST_RE,
    LITERAL_BLOCK_RE,
    TABLE_START_RE,
    IMAGE_RE,
    NL_RE,))))


RST_EXT = ".rst"
HTML_EXT = ".html"
MAKE_COMMAND = "rst2html.py"

MAKE_FILE = open(argList.output+"/"+"make.sh", 'w')
print(r"#!/bin/bash", file=MAKE_FILE)


def new_file(fp, filename):
    """ Open a new file """
    fp = open(argList.output+"/"+filename+RST_EXT, 'w')
    nameLen = len(filename)
    print(f"{MAKE_COMMAND} {filename+RST_EXT} > {filename+HTML_EXT}", file=MAKE_FILE)
    print("#"*nameLen, file=fp)
    print(filename, file=fp)
    print("#"*nameLen, file=fp)
    print(file=fp)
    print(f"STATUS: Parsing {filename}")
    return fp


def output(*args):
    """ Print to file (no unicode) """
    print(*map(lambda x: x.encode('latin-1').decode('latin-1'), args), file=OUTFILE)


def standard_replace(string: str, newline=True):
    """ Do standard replaces on a read string """
    indent = re.match(r"^\s*", string)
    if newline:
        string = string.replace(r"\n", "\n"+" "*(indent.end() - indent.start()))
    string = string.replace(u"\u2212", "-")
    string = string.replace(u"\u2013", "--")
    string = string.replace(u"\u2014", "---")
    string = string.replace(u"\u2026", "...")
    string = string.replace(u"\u201c", "\"")
    string = string.replace(u"\u201d", "\"")
    string = string.replace(u"\u2018", "'")
    string = string.replace(u"\u2019", "'")
    string = string.replace(u"\u2009", " ")

    string = string.replace(u"\u0127", "h-bar")
    string = string.replace(u"\u03b1", "alpha")
    string = string.replace(u"\u03bc", "mu")
    return string


def print_table(table):
    """ Print a table in rst format """
    maxCols = max([len(row) for row in table])
    if maxCols == 1:
        table = [row + [" "] for row in table]
        maxCols = 2
    maxWidth = [0]*maxCols
    for row in table:
        for i, elem in enumerate(row):
            maxWidth[i] = max(maxWidth[i], len(elem))

    currCol = 0
    # blockStart = "+"
    # blockSep = "+"
    # lineStart = "|"
    # sep = "|"
    blockStart = ""
    blockSep = " "
    lineStart = ""
    sep = " "
    headChar = "="

    tailLine = blockStart
    headLine = blockStart
    currLine = lineStart
    sepLen = len(sep)
    for col in maxWidth:
        headLine += headChar*col + blockSep
    output(headLine)

    for row in table:
        for elem in row:
            if isinstance(elem, tuple):
                blockSize = sum(maxWidth[currCol:currCol+elem[1]])+(elem[1]*sepLen) - len(elem[0]) - sepLen
                currLine += elem[0] + " "*blockSize + sep
                tailLine += "-"*(sum(maxWidth[currCol:currCol+elem[1]])+elem[1]-1)+blockSep
                currCol += elem[1]
            else:
                blockSize = maxWidth[currCol] - len(elem) + 1 - sepLen
                currLine += elem + " "*blockSize + sep
                currCol += 1

        output(currLine)
        if tailLine:
            tailLine = tailLine.strip()
            tailLine += "-" * (len(headLine)-len(tailLine)-1)
            output(tailLine)
            tailLine = ""
        currCol = 0
        currLine = lineStart
    output(headLine)
    output()


OUTFILE = None


def main(filename):
    """ Perform the main conversion """
    global OUTFILE

    def next_line(newline=True):
        for line in inFile:
            val = line.rstrip('\n')
            break
        else:
            return None
        return standard_replace(val, newline)

    with open(filename, 'r', encoding="utf8") as inFile:
        line = next_line()
        while inFile:
            # Reached a newline
            match = ANY_MATCH_RE.search(line)
            while match:
                if NEWPAGE_RE.search(line) and match.group() == NEWPAGE_RE.search(line).group():
                    if DEBUG:
                        print("newpage", match)
                    title = match.group('title').strip()
                    output(line[:match.start()])
                    if OUTFILE is not None:
                        OUTFILE.close()
                    OUTFILE = new_file(OUTFILE, title)
                    line = line[match.end():]
                elif TITLE_RE.search(line) and match.group() == TITLE_RE.search(line).group():
                    if DEBUG:
                        print("title", match)
                    title = match.group('subtitle').strip()
                    output(line[:match.start()])
                    output(title)
                    output("*"*len(title))
                    output()
                    line = line[match.end():]
                elif SUBTITLE_RE.search(line) and match.group() == SUBTITLE_RE.search(line).group():
                    if DEBUG:
                        print("subtitle", match)
                    title = match.group('subsubtitle').strip()
                    output(line[:match.start()])
                    output(title)
                    output("="*len(title))
                    output()
                    line = line[match.end():]

                elif MINORTITLE_RE.search(line) and match.group() == MINORTITLE_RE.search(line).group():
                    if DEBUG:
                        print("minortitle", match)
                    title = match.group('minortitle').strip()
                    output(line[:match.start()])
                    output(title)
                    output("-"*len(title))
                    output()
                    line = line[match.end():]

                elif LIST_RE.search(line) and match.group() == LIST_RE.search(line).group():
                    if DEBUG:
                        print("list", match)

                    matchGroup = match.group()
                    line = line.replace(matchGroup, "   "*(matchGroup.count('*')-1)+"- ", 1)

                elif LITERAL_BLOCK_RE.search(line) and match.group() == LITERAL_BLOCK_RE.search(line).group():
                    if DEBUG:
                        print("literal", match)
                    output(line[:match.start()])
                    output("::")
                    line = line[match.end():]

                elif TABLE_START_RE.search(line) and match.group() == TABLE_START_RE.search(line).group():
                    if DEBUG:
                        print("table", match)
                    output(line[:match.start()])
                    line = line[match.start():]
                    endmatch = TABLE_END_RE.search(line)
                    while not endmatch:
                        nextLine = next_line()
                        if nextLine is None:
                            raise IOError('Table never closed')
                        if line:
                            line += " " + nextLine
                        else:
                            line = nextLine
                        endmatch = TABLE_END_RE.search(line)

                    tableData = line[:endmatch.end()]
                    row = []
                    data = []
                    for tableLine in tableData.splitlines():
                        tableLine = tableLine.lstrip("{").rstrip("}").strip("\\").strip()
                        if re.match(r"\|-(?!-)", tableLine):
                            if row:
                                data.append(row)
                            row = []
                        elif "class=" in tableLine:
                            continue
                        elif "colspan=" in tableLine:
                            rowmatch = re.search(r"='([0-9]+)'[ \\\|]+", tableLine)
                            val = (tableLine[rowmatch.end():], int(rowmatch.group(1)))

                            row.append(val)
                        elif re.match(r"^(!|\|)", tableLine):
                            rowmatch = re.match(r"^(!|\|)", tableLine)
                            val = tableLine[rowmatch.end():].strip()
                            row.append(val)
                    # Catch final
                    data.append(row)
                    tableData = data
                    del data

                    for i, row in enumerate(tableData):
                        tableData[i] = [elem for elem in tableData[i] if elem]

                    tableData = [row for row in tableData if row]
                    if DEBUG:
                        for row in tableData:
                            print(row)

                    print_table(tableData)
                    line = line[endmatch.end():]
                elif IMAGE_RE.search(line) and match.group() == IMAGE_RE.search(line).group():
                    output(f"""
.. image:: images/{match.group("path")}
   :width: {match.group("size")}
   :alt: {match.group("label")}

""")

                    line = line[match.end():]

                elif NL_RE.search(line) and match.group() == NL_RE.search(line).group():
                    if DEBUG:
                        print("newline", match)
                    val = line[:match.start()]
                    # Remove end of line slashes
                    val = re.sub(r"(?<!\\)\\$", "", val)
                    # Count of non-escaped *s
                    if len(re.findall(r"(?<!\\)\*", val)) % 2:
                        ind = val.rfind("*")
                        val = val[:ind] + val[ind+1:]
                    output(val)
                    line = line[match.end():]

                match = ANY_MATCH_RE.search(line)
                # End main block
            nextLine = next_line()
            if nextLine is None:
                break
            else:
                if not nextLine:
                    line += "\n\n"
                else:
                    if line:
                        line += " " + nextLine
                    else:
                        line = nextLine

    # Dump remainder
    output(line)


if __name__ == "__main__":
    main(argList.input)
