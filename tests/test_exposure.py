#!/usr/bin/env python2

from __future__ import absolute_import, division, print_function

# LSST Data Management System
# Copyright 2015 AURA/LSST
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import unittest
import lsstx.image as image
import lsstx.geom as geom
import numpy as np
import copy


class TestExposure(unittest.TestCase):

    def test_Basic(self):
        exp = image.Exposure(32, 40, dtype=np.int32)
        self.assertEqual(exp.height, 40)
        self.assertEqual(exp.width, 32)
        self.assertFalse(exp.has_wcs())
        xy0 = exp.xy0
        self.assertIsInstance(xy0, geom.Point2I)
        self.assertEqual(exp.x0, 0)
        self.assertEqual(exp.y0, 0)

        xy1 = geom.Point2I(5, 10)
        exp.xy0 = xy1
        self.assertEqual(exp.x0, 5)
        self.assertEqual(exp.y0, 10)

        deep = copy.deepcopy(exp)
        self.assertEqual(deep.x0, 5)
        self.assertEqual(deep.height, 40)

        exp2 = image.Exposure(geom.Extent(2, 3), dtype=np.float64)
        self.assertEqual(exp2.width, 2)
        self.assertEqual(exp2.height, 3)

        bb = exp2.bbox
        self.assertIsInstance(bb, geom.Box2I)
        self.assertEqual(bb.area, 6)


if __name__ == '__main__':
    unittest.main()
