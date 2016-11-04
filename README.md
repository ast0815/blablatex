# blablatex
Check your latex document for bullshit with the BlaBlaMeter

See [blablameter.com](http://www.blablameter.com) for details about the index.

Blablatex looks for text blocks that do *not* start with an '%' or an '\',
or start with either '\par' or '\label'. Other blocks will not be annotated.
A BS index of -1 suggests that the paragraph is too short to calculate a proper value.
The calculation needs at least three sentences to succeed.

You also need to 'annotate' the tex-file that contains your `\documentclass`
and `\begin{document}` lines.
