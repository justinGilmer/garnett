# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import unittest
import os
import json
import numpy as np
import garnett
from tempfile import TemporaryDirectory

try:
    import gtar
except ImportError:
    GTAR = False
else:
    GTAR = True


@unittest.skipIf(not GTAR, 'GetarFileReader requires the gtar module.')
class BaseGetarFileReaderTest(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = TemporaryDirectory(prefix='garnett_getar_tmp')
        self.addCleanup(self.tmp_dir.cleanup)
        self.getar_file_fn = os.path.join(self.tmp_dir.name, 'sample.tar')

    def setup_sample(self, N, dim=3):
        self.position = np.random.rand(N, 3)
        self.orientation = np.random.rand(N, 4)
        self.velocity = np.random.rand(N, 3)
        self.mass = np.random.rand(N)
        self.charge = np.random.rand(N)
        self.diameter = np.random.rand(N)
        self.moment_inertia = np.random.rand(N, 3)
        self.angmom = np.random.rand(N, 4)
        self.image = np.random.randint(-1000, 1000, size=(N, 3), dtype=np.int32)
        types = N // 2 * [0] + (N - N // 2) * [1]
        type_names = ['A', 'B']
        self.box = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
        self.types = [type_names[t] for t in types]
        if dim == 2:
            self.position[:, 2] = 0
            self.velocity[:, 2] = 0

        with gtar.GTAR(self.getar_file_fn, 'w') as traj:
            traj.writePath('frames/0/position.f32.ind', self.position)
            traj.writePath('frames/0/orientation.f32.ind', self.orientation)
            traj.writePath('frames/0/velocity.f32.ind', self.velocity)
            traj.writePath('frames/0/mass.f32.ind', self.mass)
            traj.writePath('frames/0/charge.f32.ind', self.charge)
            traj.writePath('frames/0/diameter.f32.ind', self.diameter)
            traj.writePath('frames/0/moment_inertia.f32.ind', self.moment_inertia)
            traj.writePath('frames/0/angular_momentum_quat.f32.ind', self.angmom)
            traj.writePath('frames/0/box.f32.ind', self.box)
            traj.writePath('frames/0/image.i32.ind', self.image)
            traj.writePath('type.u32.ind', types)
            traj.writePath('type_names.json', json.dumps(type_names))

    def read_trajectory(self):
        reader = garnett.reader.GetarFileReader()
        self.getarfile = open(self.getar_file_fn, 'rb')
        self.addCleanup(self.getarfile.close)
        return reader.read(self.getarfile)

    def test_read_3d(self):
        N = 100
        self.setup_sample(N, dim=3)
        traj = self.read_trajectory()
        self.assertEqual(len(traj), 1)
        frame = traj[0]
        self.assertEqual(len(frame), N)
        self.assertEqual(frame.box, garnett.trajectory.Box(1.0, 1.0, 1.0))
        self.assertEqual(frame.box.dimensions, 3)
        np.testing.assert_allclose(frame.position, self.position)
        np.testing.assert_allclose(frame.orientation, self.orientation)
        np.testing.assert_allclose(frame.velocity, self.velocity)
        np.testing.assert_allclose(frame.mass, self.mass)
        np.testing.assert_allclose(frame.charge, self.charge)
        np.testing.assert_allclose(frame.diameter, self.diameter)
        np.testing.assert_allclose(frame.moment_inertia, self.moment_inertia)
        np.testing.assert_allclose(frame.angmom, self.angmom)
        np.testing.assert_array_equal(frame.image, self.image)
        self.assertEqual(frame.types, self.types)

    def test_read_2d(self):
        N = 100
        self.setup_sample(N, dim=2)
        traj = self.read_trajectory()
        self.assertEqual(len(traj), 1)
        frame = traj[0]
        self.assertEqual(len(frame), N)
        self.assertEqual(frame.box, garnett.trajectory.Box(1.0, 1.0, 1.0, dimensions=2))
        self.assertEqual(frame.box.dimensions, 2)
        np.testing.assert_allclose(frame.position, self.position)
        np.testing.assert_allclose(frame.orientation, self.orientation)
        np.testing.assert_allclose(frame.velocity, self.velocity)
        np.testing.assert_allclose(frame.mass, self.mass)
        np.testing.assert_allclose(frame.charge, self.charge)
        np.testing.assert_allclose(frame.diameter, self.diameter)
        np.testing.assert_allclose(frame.moment_inertia, self.moment_inertia)
        np.testing.assert_allclose(frame.angmom, self.angmom)
        np.testing.assert_array_equal(frame.image, self.image)
        self.assertEqual(frame.types, self.types)


@unittest.skipIf(not GTAR, 'GetarFileReader requires the gtar module.')
class NoTypesGetarFileReaderTest(BaseGetarFileReaderTest):
    """This test makes sure that when angle (or other non-particle) types
    are stored in a file, they do not get interpreted as particle
    types."""

    def setup_sample(self, N, dim=3):
        self.position = np.random.rand(N, 3)
        self.orientation = np.random.rand(N, 4)
        self.velocity = np.random.rand(N, 3)
        self.mass = np.random.rand(N)
        self.charge = np.random.rand(N)
        self.diameter = np.random.rand(N)
        self.moment_inertia = np.random.rand(N, 3)
        self.angmom = np.random.rand(N, 4)
        self.image = np.random.randint(-1000, 1000, size=(N, 3), dtype=np.int32)
        self.box = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
        self.types = N*['A']
        if dim == 2:
            self.position[:, 2] = 0
            self.velocity[:, 2] = 0

        with gtar.GTAR(self.getar_file_fn, 'w') as traj:
            traj.writePath('frames/0/position.f32.ind', self.position)
            traj.writePath('frames/0/orientation.f32.ind', self.orientation)
            traj.writePath('frames/0/velocity.f32.ind', self.velocity)
            traj.writePath('frames/0/mass.f32.ind', self.mass)
            traj.writePath('frames/0/charge.f32.ind', self.charge)
            traj.writePath('frames/0/diameter.f32.ind', self.diameter)
            traj.writePath('frames/0/moment_inertia.f32.ind', self.moment_inertia)
            traj.writePath('frames/0/angular_momentum_quat.f32.ind', self.angmom)
            traj.writePath('frames/0/box.f32.ind', self.box)
            traj.writePath('frames/0/image.i32.ind', self.image)
            traj.writePath('angle/type.u32.ind', [0])
            traj.writePath('angle/type_names.json', '["Angle_A"]')


if __name__ == '__main__':
    unittest.main()
