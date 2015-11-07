"""
This is a collection of samples, parsers and writers for formats
used in the Glotzer Group at the University of Michigan, Ann Arbor."""


from . import formats
from . import reader
from . import writer
from . import samples
from . import trajectory

VERSION = '0.1.3'
VERSION_TUPLE = (0, 1, 3)

__all__ = ['formats', 'reader', 'writer', 'samples', 'trajectory']
