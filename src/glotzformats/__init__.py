"""
This is a collection of samples, parsers and writers for formats
used in the Glotzer Group at the University of Michigan, Ann Arbor."""


from . import formats
from . import reader
from . import writer
from . import samples
from . import trajectory

__version__ = '0.2.1rc1'

__all__ = ['formats', 'reader', 'writer', 'samples', 'trajectory']
