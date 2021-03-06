#!/usr/bin/env python
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import sys
import glob
import logging
from importlib.util import find_spec

import garnett

GTAR = find_spec('gtar')
GSD = find_spec('gsd')


def test_read(file, template=None):
    with garnett.read(file, template=template) as traj:
        for frame in traj:
            frame.load()
            print(frame)


def main():
    if GTAR:
        for fn in glob.glob('../samples/*.tar'):
            test_read(fn)

    if GSD:
        for fn in glob.glob('../samples/*.gsd'):
            test_read(fn)

    for fn in glob.glob('../samples/*.dcd'):
        test_read(fn)

    for fn in glob.glob('../samples/*.xml'):
        test_read(fn)

    for fn in glob.glob('../samples/*.pos'):
        test_read(fn)

    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
