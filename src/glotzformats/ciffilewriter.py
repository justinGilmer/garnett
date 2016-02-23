"""cif-file writer for the Glotzer Group, University of Michigan.

Author: Julia Dschemuchadse, Carl Simon Adorf

.. code::

    writer = CifFileWriter()

    # write to screen:
    write.write(trajetory)

    # write to file:
    with open('a_ciffile.pos', 'w') as ciffile:
        writer.write(trajectory, ciffile)
"""

import io
import sys
import logging
import math
from collections import defaultdict

import numpy as np

logger = logging.getLogger(__name__)
PYTHON_2 = sys.version_info[0] == 2


def _determine_unitcell(box):
    lengths = np.array([box.Lx, box.Ly, box.Lz])  # a, b, c
    gamma = math.degrees(
        np.arccos(
            box.xy / math.sqrt(1 + box.xy**2)))
    beta = math.degrees(
        np.arccos(
            box.xz / math.sqrt(1 + box.xz**2 + box.yz**2)))
    alpha = math.degrees(
        np.arccos(
            (box.xy * box.xz + box.yz) /
            (math.sqrt(1 + box.xy**2) * math.sqrt(1 + box.xz**2 + box.yz**2))))
    angles = np.array([alpha, beta, gamma])
    return lengths, angles


class CifFileWriter(object):
    """Write cif-files from a trajectory instance."""

    def _write_frame(self, frame, file, data, occupancy):
        def _write(msg='', end='\n'):
            if PYTHON_2:
                file.write(unicode(msg + end))  # noqa
            else:
                file.write(msg + end)
        unitcell_lengths, unitcell_angles = _determine_unitcell(frame.box)
        # write title
        _write("data_" + data)
        # _write("data_" + os.path.splitext(ciffilename)[0])

        # write unit cell parameters
        _write("_cell_length_a                 {}".format(unitcell_lengths[0]))
        _write("_cell_length_b                 {}".format(unitcell_lengths[1]))
        _write("_cell_length_c                 {}".format(unitcell_lengths[2]))
        _write("_cell_angle_alpha              {}".format(unitcell_angles[0]))
        _write("_cell_angle_beta               {}".format(unitcell_angles[1]))
        _write("_cell_angle_gamma              {}".format(unitcell_angles[2]))
        _write()

        # write symmetry - P1
        _write("_symmetry_space_group_name_H-M   " + "'P 1'")
        _write("_symmetry_Int_Tables_number      " + str(1))
        _write()

        # write header for particle positions
        _write("loop_")
        _write("_atom_site_label")
        _write("_atom_site_type_symbol")
        _write("_atom_site_occupancy")
        _write("_atom_site_fract_x")
        _write("_atom_site_fract_y")
        _write("_atom_site_fract_z")

        # write header particle positions
        type_counter = defaultdict(int)
        n_digits = len(str(len(frame.positions)))
        l = "{ptype}{pnum:0"+str(n_digits)+"d} {ptype} {occ:3.2f} {position}"
        for i, (position, particle_type) in enumerate(zip(frame.positions, frame.types)):
            _write(l.format(
                pnum=type_counter[particle_type],
                ptype=particle_type,
                occ=occupancy,
                position=' '.join((str(p) for p in position))))
            type_counter[particle_type] += 1

    def write(self, trajectory, file=sys.stdout,
              data='simulation', occupancy=1.0):
        """Serialize a trajectory into cif-format and write it to file.

        :param trajectory: The trajectory to serialize
        :type trajectory: :class:`~glotzformats.trajectory.Trajectory`
        :param file: A file-like object."""
        for i, frame in enumerate(trajectory):
            self._write_frame(
                frame=frame,
                file=file,
                data='{}_frame_{}'.format(data, i),
                occupancy=occupancy)
            logger.debug("Wrote frame {}.".format(i + 1))
        logger.info("Wrote {} frames.".format(i + 1))

    def dump(self, trajectory):
        """Serialize trajectory into cif-format.

        :param trajectory: The trajectory to serialize.
        :type trajectory: :class:`~glotzformats.trajectory.Trajectory`
        :rtype: str"""
        f = io.StringIO()
        self.write(trajectory, f)
        return f.getvalue()
