"""Hoomd-blue XML-file reader for the Glotzer Group, University of Michigan.

Authors: Carl Simon Adorf

.. code::

    reader = HoomdBlueXMLFileReader()
    with open('hoomdblue.xml') as xmlfile:
        return reader.read(xmlfile)
"""

import logging
import warnings
import xml.etree.ElementTree as ET

import numpy as np

from .trajectory import _RawFrameData, Frame, Trajectory
from .errors import ParserError


logger = logging.getLogger(__name__)


class HoomdBlueXMLFrame(Frame):

    def __init__(self, root):
        self.root = root
        super(HoomdBlueXMLFrame, self).__init__()

    def read(self):
        "Read the frame data from the stream."
        raw_frame = _RawFrameData()
        config = self.root.find('configuration')
        raw_frame.box = np.asarray(_get_box_matrix(config.find('box')))
        raw_frame.positions = list(_parse_positions(config.find('position')))
        orientations = config.find('orientation')
        if orientations is None:
            raw_frame.orientations = [[1, 0, 0, 0]] * len(raw_frame.positions)
        else:
            raw_frame.orientations = list(_parse_orientations(orientations))
        raw_frame.types = list(_parse_types(config.find('type')))
        return raw_frame

    def __str__(self):
        return "HoomdBlueXMLFrame(root={})".format(self.root)


class HoomdBlueXMLFileReader(object):
    """Read hoomdblue-xml-files."""

    def read(self, stream):
        """Read text stream and return a trajectory instance.

        :param stream: The stream, which contains the xmlfile.
        :type stream: A file-like textstream.
        """
        # Index the stream
        try:
            frames = [HoomdBlueXMLFrame(ET.fromstring(stream.read()))]
        except ET.ParseError as error:
            raise ParserError(error)
        logger.info("Read {} frames.".format(len(frames)))
        return Trajectory(frames)


def _get_box_matrix(box):
    assert box is not None

    def _get(name, default=None):
        v = box.get(name)
        if v is None and default is None:
            raise KeyError(name)
        elif v is None:
            return float(default)
        else:
            return float(v)
    return [
        [_get('lx'), _get('xy', 0) * _get('ly'), _get('xz', 0) * _get('lz')],
        [0.0, _get('ly'), _get('yz', 0) * _get('lz')],
        [0.0, 0.0, _get('lz')]
    ]


def _parse_positions(positions):
    for i, position in enumerate(positions.text.splitlines()[1:]):
        yield [float(x) for x in position.split()]
    if i + 1 != int(positions.attrib['num']):
        warnings.warn("Number of positions inconsistent.")


def _parse_orientations(orientations):
    for i, orientation in enumerate(orientations.text.splitlines()[1:]):
        yield [float(x) for x in orientation.split()]
    if i + 1 != int(orientations.attrib['num']):
        warnings.warn("Number of orientations inconsistent.")


def _parse_types(types):
    for i, type in enumerate(types.text.splitlines()[1:]):
        yield str(type)
    if i + 1 != int(types.attrib['num']):
        warnings.warn("Number of types inconsistent.")
