#!/bin/env python
"""blablatex

Annotate tex document paragraphs with their bullshit index.
See blablameter.com for the meaning of the index.

Usage:
    blablatex [-r | --remove] [--lang=<lang>] <texfile> ...
    blablatex (-h | --help)

Options:
    -h --help       Show help text.
    -r --remove     Remove blablatex blocks rather than adding them.
    --lang=<lang>   Set the text language. One of 'en', 'de', 'es'.
                    [default: en]

            ### WARNING! ###

The original files will be replaced!
The originals will be saved as `<texfile>.org`.

The removal with `-r` does not work very reliably!

"""

from docopt import docopt
from blablameter import check_bullshit
import re
import os, sys

def add_requirements(text):
    """Add required definitions at the appropraite positions."""

    packages=r"""
%blablatex
\\usepackage{framed}
\\usepackage{xcolor}
%/blablatex"""

    blabla_environment=r"""
%blablatex
\\newenvironment{blabla}[2]
{%
    \\def\\FrameCommand
    {%
        {\\color{#2}%
        \\parbox{2.5em}{BS:\\\\ $#1$}%
        \\vrule width 3pt}%
        \\hspace{3pt}
    }%
    \\MakeFramed{\\advance\\hsize-\\width}%
}
{\\endMakeFramed}
%/blablatex"""

    ret = ""
    for line in text.split('\n'):
        line = re.sub(r'^(\\documentclass.+)$', '\\1%s'%(packages,), line)
        line = re.sub(r'^(\\begin{document.+)$', '\\1%s'%(blabla_environment,), line)
        ret += line + '\n'

    return ret[:-1]

def annotate_paragraph(par, lang='en'):
    """Annotate the paragraph with blablatex blocks.

    If `remove` is `True`, remove the blocks rather than adding them.
    """

    BS = check_bullshit(par, lang=lang)
    if 0.0<=BS<0.2:
        color = 'green'
    elif 0.2<=BS<0.4:
        color = 'olive'
    elif 0.4<=BS<0.6:
        color = 'orange'
    elif 0.6<=BS:
        color = 'red'
    else:
        color = 'black'

    startblock = "%%blablatex\n\\begin{blabla}{%.2f}{%s}\n%%/blablatex\n"%(BS, color)
    endblock = "%blablatex\n\\end{blabla}\n%/blablatex\n"

    return startblock + par + endblock

def lines_without_blablatex_blocks(fileobject):
    """Remove blablatex blocks from text."""

    in_block = False

    for line in fileobject:
        if re.match(r'%blablatex', line):
            in_block = True
        if not in_block:
            yield line
        if re.match(r'%/blablatex', line):
            in_block = False

def yield_blocks(fileobject):
    """Yield text blocks from the file object."""

    block = ""

    for line in fileobject:
        if re.match(r'\s*$', line) or re.match(r'\s*\\par', line) or re.match(r'\s*\\begin', line):
            # Start a new block with the line
            if block != "":
                yield block
            block = line
        elif re.match(r'\s*\\(?:sub)*section', line) or re.match(r'\s*\\chapter', line):
            # Start a new block after a \(sub)(sub)section or \chapter
            block += line
            yield block
            block = ""
        else:
            # Add the line to the block
            block += line

    if block != "":
        # Yield last block if there is no trailing empty line
        yield block

class BackupError(Exception):
    pass

def annotate_file(filename, lang='en', remove=False):
    """Annotate the file `<filename>`.

    The orginal is saved as `<filename>.org`.
    """

    if os.path.lexists(filename+'.org'):
        raise BackupError("File already exists: %s"%(filename+'.org',))

    os.rename(filename, filename+'.org')

    if os.path.lexists(filename):
        raise BackupError("File already exists: %s"%(filename+'.org',))

    with open(filename+'.org', 'r') as inf:
        with open(filename, 'w') as outf:
            if remove:
                for line in lines_without_blablatex_blocks(inf):
                    outf.write(line)
            else:
                for block in yield_blocks(inf):
                    if (not re.match(r'\s*[%\\]', block)) or (re.match(r'\s*\\par', block) or re.match(r'\s*\\label', block)):
                        # Only consider blocks not starting with '%' or '\',
                        # or starting with '\par' or '\label'
                        if len(block) > 80:
                            # Probably a regular paragraph
                            block = annotate_paragraph(block, lang=lang)
                    else:
                        block = add_requirements(block)

                    outf.write(block)

if __name__ == '__main__':
    args = docopt(__doc__)

    lang = args['--lang']
    remove = args['--remove']
    texfiles = args['<texfile>']

    for tf in texfiles:
        try:
            annotate_file(tf, lang=lang, remove=remove)
        except BackupError:
            sys.stderr.write("Could not backup file: %s\n"%(tf,))
            sys.stderr.write("Skipping...\n")
