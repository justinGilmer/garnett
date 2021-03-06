# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
# Demonstration with the cube example
from __future__ import print_function
from __future__ import division
import hoomd
from hoomd import deprecated, hpmc

import numpy as np
import garnett

hoomd.context.initialize()

# vertices of a cube
verts = [[-1, -1, -1], [-1, -1, 1], [-1, 1, 1], [-1, 1, -1],
         [1, -1, -1], [1, -1, 1], [1, 1, 1], [1, 1, -1]]

with hoomd.context.SimulationContext():
    try:
        system = deprecated.init.read_xml('cube.xml')
    except RuntimeError:
        snapshot = hoomd.data.make_snapshot(N=4, box=hoomd.data.boxdim(L=10, dimensions=3))
        np.copyto(snapshot.particles.position, np.array([
                [2, 0, 0],
                [4, 0, 0],
                [0, 4, 0],
                [0, 0, 4],
            ]))
        system = hoomd.init.read_snapshot(snapshot)
        deprecated.dump.xml(hoomd.group.all(), 'cube.xml', all=True)

    mc = hpmc.integrate.convex_polyhedron(seed=452784, d=0.2, a=0.4)
    mc.shape_param.set('A', vertices=verts)
    pos = deprecated.dump.pos(filename='cube.pos', period=10)
    mc.setup_pos_writer(pos)
    hoomd.run(1000)

with hoomd.context.SimulationContext():

    with garnett.read('cube.pos') as traj:
        snapshot = traj[-1].to_hoomd_snapshot()
        system = hoomd.init.read_snapshot(snapshot)

    mc = hpmc.integrate.convex_polyhedron(seed=452784, d=0.2, a=0.4)
    mc.shape_param.set('A', vertices=verts)
    hoomd.dump.gsd(filename='cube.gsd', group=hoomd.group.all(), period=10)
    hoomd.run(1000)
