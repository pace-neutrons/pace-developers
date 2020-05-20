# Coding Style Guidelines

**Python**

For Python files, effort is made to comply with
[PEP8](https://www.python.org/dev/peps/pep-0008/), in particular line lengths
of 73 characters for flowing text and a 79 hard limit. These can be broken for
long bits of text such as URLs and references in docstrings that would be
harder to read if split onto multiple lines.

**Docstrings**

All public functions should have a docstring, and
[Numpy-style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)
should be used.

**User documentation**

User documentation is built with Sphinx, which has a
[documentation style guide](https://documentation-style-guide-sphinx.readthedocs.io/en/latest/style-guide.html).
Euphonic's documentation uses .rst extensions which are not recommended by
Sphinx, but the other recommendations (line length, indentation etc.) should be
adhered to where possible.
