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

# Some tests use SWIGged objects
import lsst.afw.image as afwImage

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

    def test_MaskedImage(self):
        exp = image.Exposure(32, 40, dtype=np.float32)
        e = image.make_exposure(exp.masked_image)

        self.assertEqual(e.width, 32)
        self.assertEqual(e.height, 40)

        mi = image.MaskedImage(64, 128)
        e.masked_image = mi
        self.assertEqual(e.width, 64)
        self.assertEqual(e.height, 128)

        data, mask, var = mi[0,0]
        self.assertEqual(data, 0)

        arrays = mi.arrays
        self.assertEqual(len(arrays), 3)

        mi[0,0] = (1, 2, 3)
        data, mask, var = mi[0,0]
        self.assertEqual(data, 1)
        self.assertEqual(mask, 2)
        self.assertEqual(var, 3)

        extent = mi.dimensions
        self.assertIsInstance(extent, geom.Extent2I)

        var_as_image = mi.variance
        var_as_image[1:3,1:3] = np.array([[2,4],[5,6]])
        self.assertEqual(var_as_image[2,2], 6)


    def test_ExposureInfo(self):
        cal = afwImage.Calib()
        ei = image.ExposureInfo(calib=cal)
        ei2 = image.ExposureInfo(info=ei)
        self.assertTrue(ei2.has_calib())
        self.assertFalse(ei2.has_wcs())


if __name__ == '__main__':
    unittest.main()
