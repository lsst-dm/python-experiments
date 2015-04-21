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

import lsstx.geom as geom
import numpy as np
import copy

# Needed until we fix repr()
from lsstx.geom import Box2D, Point2D, Extent2D, Extent3D


class TestExtent(unittest.TestCase):

    def test_Typed2(self):
        ei = geom.Extent2I(1, 2)
        self.assertEqual(ei.x, 1)
        self.assertEqual(ei.y, 2)
        e2 = copy.deepcopy(ei)
        self.assertEqual(ei, e2)

        # Create D from I
        ed = geom.Extent2D(ei)
        self.assertEqual(ed.x, 1)
        self.assertEqual(ed.y, 2)

        # Test the methods
        ed1 = geom.Extent2D(3.5, 0)

        self.assertAlmostEqual(ed1.compute_norm(), 3.5, 10)
        self.assertAlmostEqual(ed1.compute_squared_norm(), 12.25, 10)
        self.assertRaises(TypeError, ei.compute_norm)
        self.assertEqual(ei.compute_squared_norm(), 5)

        ei1 = geom.Extent2I(1, 2)
        ei2 = geom.Extent2I(3, 4)
        self.assertEqual(ei1.x, 1)
        self.assertEqual(ei1.y, 2)
        self.assertEqual(ei2.x, 3)
        self.assertEqual(ei2.y, 4)
        ei1.swap(ei2)
        self.assertEqual(ei1.x, 3)
        self.assertEqual(ei1.y, 4)
        self.assertEqual(ei2.x, 1)
        self.assertEqual(ei2.y, 2)

        # Can not create I from D though
        self.assertRaises(NotImplementedError, geom.Extent2I, ed)

        # Create object using repr. TODO: Fix prefix
        r = eval(repr(ed))
        self.assertEqual(r, ed)

    def test_Typed3(self):
        ei = geom.Extent3I(1, 2, 3)
        self.assertEqual(ei.x, 1)
        self.assertEqual(ei.y, 2)
        self.assertEqual(ei.z, 3)
        e2 = copy.deepcopy(ei)
        self.assertEqual(ei, e2)

        # Create D from I
        ed = geom.Extent3D(ei)
        self.assertEqual(ed.x, 1)
        self.assertEqual(ed.y, 2)
        self.assertEqual(ed.z, 3)

        # Test the methods
        ed1 = geom.Extent3D(0, 3.5, 0)

        self.assertAlmostEqual(ed1.compute_norm(), 3.5, 10)
        self.assertAlmostEqual(ed1.compute_squared_norm(), 12.25, 10)
        self.assertRaises(TypeError, ei.compute_norm)
        self.assertEqual(ei.compute_squared_norm(), 14)

        ei1 = geom.Extent3I(1, 2, 3)
        ei2 = geom.Extent3I(4, 5, 6)
        self.assertEqual(ei1.x, 1)
        self.assertEqual(ei1.y, 2)
        self.assertEqual(ei1.z, 3)
        self.assertEqual(ei2.x, 4)
        self.assertEqual(ei2.y, 5)
        self.assertEqual(ei2.z, 6)
        ei1.swap(ei2)
        self.assertEqual(ei1.x, 4)
        self.assertEqual(ei1.y, 5)
        self.assertEqual(ei1.z, 6)
        self.assertEqual(ei2.x, 1)
        self.assertEqual(ei2.y, 2)
        self.assertEqual(ei2.z, 3)

        # Can not create I from D though
        self.assertRaises(NotImplementedError, geom.Extent3I, ed)

        # Create object using repr. TODO: Fix prefix
        r = eval(repr(ed))
        self.assertEqual(r, ed)

    def test_Untyped(self):
        ed = geom.Extent(1, 2, 3)
        self.assertIsInstance(ed, geom.Extent3I)
        ed = geom.Extent(1, 2, 3.)
        self.assertIsInstance(ed, geom.Extent3D)
        ed = geom.Extent(1, 2)
        self.assertIsInstance(ed, geom.Extent2I)
        ed = geom.Extent(1, 2.)
        self.assertIsInstance(ed, geom.Extent2D)
        ed = geom.Extent2(3.6)
        self.assertIsInstance(ed, geom.Extent2D)
        self.assertAlmostEqual(ed.y, 3.6, 14)
        ed = geom.Extent3(3)
        self.assertIsInstance(ed, geom.Extent3I)
        self.assertEqual(ed.z, 3)

        self.assertRaises(ValueError, geom.Extent, ed)
        self.assertRaises(ValueError, geom.Extent, 42)

        ed = geom.Extent((1, 2))
        self.assertSequenceEqual(ed, (1, 2))


class TestPoint(unittest.TestCase):

    def test_Typed2(self):
        pi = geom.Point2I(1, 2)
        self.assertEqual(pi.x, 1)
        self.assertEqual(pi.y, 2)
        p2 = copy.deepcopy(pi)
        self.assertEqual(pi, p2)

        # Create D from I
        pd = geom.Point2D(pi)
        self.assertEqual(pd.x, 1)
        self.assertEqual(pd.y, 2)

        # Create I from D
        pi = geom.Point2I(pd)
        self.assertEqual(pi.x, 1)
        self.assertEqual(pi.y, 2)

        # Test the methods
        pi1 = geom.Point2I(1, 2)
        pi2 = geom.Point2I(3, 4)
        self.assertEqual(pi1.x, 1)
        self.assertEqual(pi1.y, 2)
        self.assertEqual(pi2.x, 3)
        self.assertEqual(pi2.y, 4)
        pi1.swap(pi2)
        self.assertEqual(pi1.x, 3)
        self.assertEqual(pi1.y, 4)
        self.assertEqual(pi2.x, 1)
        self.assertEqual(pi2.y, 2)

        pi1 = geom.Point2I(3, 0)
        pi2 = geom.Point2I(0, 4)
        self.assertEqual(pi1.distance_squared(pi2), 25)

        pi1.scale(2)
        pi2.scale(2)
        self.assertEqual(pi1.distance_squared(pi2), 100)

        ei = geom.Extent(1, 1)
        pi1.shift(ei)
        pi2.shift(ei)
        self.assertEqual(pi1.distance_squared(pi2), 100)

        # Create object using repr. TODO: Fix prefix
        r = eval("geom."+repr(pd))
        self.assertEqual(r, pd)

    def test_Typed3(self):
        pi = geom.Point3I(1, 2, 3)
        self.assertEqual(pi.x, 1)
        self.assertEqual(pi.y, 2)
        self.assertEqual(pi.z, 3)
        p2 = copy.deepcopy(pi)
        self.assertEqual(pi, p2)

        # Create D from I
        pd = geom.Point3D(pi)
        self.assertEqual(pd.x, 1)
        self.assertEqual(pd.y, 2)
        self.assertEqual(pd.z, 3)

        # Create I from D
        pi = geom.Point3I(pd)
        self.assertEqual(pi.x, 1)
        self.assertEqual(pi.y, 2)
        self.assertEqual(pi.z, 3)

        # Test the methods
        pi1 = geom.Point3I(1, 2, 0)
        pi2 = geom.Point3I(3, 4, 6)
        self.assertEqual(pi1.x, 1)
        self.assertEqual(pi1.y, 2)
        self.assertEqual(pi1.z, 0)
        self.assertEqual(pi2.x, 3)
        self.assertEqual(pi2.y, 4)
        self.assertEqual(pi2.z, 6)
        pi1.swap(pi2)
        self.assertEqual(pi1.x, 3)
        self.assertEqual(pi1.y, 4)
        self.assertEqual(pi2.x, 1)
        self.assertEqual(pi2.y, 2)
        self.assertEqual(pi1.z, 6)
        self.assertEqual(pi2.z, 0)

        pi1 = geom.Point3I(3, 0, 0)
        pi2 = geom.Point3I(0, 0, 4)
        self.assertEqual(pi1.distance_squared(pi2), 25)

        pi1.scale(2)
        pi2.scale(2)
        self.assertEqual(pi1.distance_squared(pi2), 100)

        ei = geom.Extent(1, 1, 1)
        pi1.shift(ei)
        pi2.shift(ei)
        self.assertEqual(pi1.distance_squared(pi2), 100)

        # Create object using repr. TODO: Fix prefix
        r = eval("geom."+repr(pd))
        self.assertEqual(r, pd)

    def test_Untyped(self):
        pd = geom.Point(1, 2, 3)
        self.assertIsInstance(pd, geom.Point3I)
        pd = geom.Point(1, 2, 3.)
        self.assertIsInstance(pd, geom.Point3D)
        pd = geom.Point(1, 2)
        self.assertIsInstance(pd, geom.Point2I)
        pd = geom.Point(1, 2.)
        self.assertIsInstance(pd, geom.Point2D)

        self.assertRaises(ValueError, geom.Point, pd)
        self.assertRaises(ValueError, geom.Point, geom.Extent(1, 2))

    def test_Operators(self):
        p = geom.Point(1, 2)
        pb = geom.Point(3, 2)
        self.assertNotEqual(p, pb)
        o = geom.Extent(3, 2)
        p += o
        self.assertEqual(p.x, 4)
        self.assertEqual(p.y, 4)

        p -= o
        self.assertEqual(p.x, 1)
        self.assertEqual(p.y, 2)

        p2 = p + o
        self.assertGreater(p2, p)
        self.assertGreaterEqual(p2, p)
        self.assertNotEqual(p2, p)

        a = geom.Point(5, 7)
        b = geom.Point(6, 7)
        self.assertGreaterEqual(b, a)
        self.assertGreaterEqual(p2, p)
        self.assertGreater(p2, p)
        self.assertLessEqual(p, p2)
        self.assertLess(p, p2)

        p3 = p - pb
        self.assertIsInstance(p3, geom.ExtentBase)
        self.assertSequenceEqual(p3, (-2, 0))

        p3 = p3 + pb
        self.assertEqual(p3, p)

        ce = b.gt(a)
        self.assertSequenceEqual(ce, (True, False))
        self.assertTrue(ce.x)
        self.assertFalse(ce.y)
        self.assertEqual(ce.dimensions, 2)

        ce2 = ~ce
        self.assertSequenceEqual(ce2, (False, True))

        ce3 = ce | ce2
        self.assertSequenceEqual(ce3, (True, True))

        ce3 = ce & ce2
        self.assertSequenceEqual(ce3, (False, False))

        c = geom.CoordinateExpr(3, val=True)
        self.assertTrue(c.all_true())
        c = geom.CoordinateExpr(3, val=False)
        self.assertFalse(c.all_true())


class TestBox(unittest.TestCase):

    def test_BasicBox(self):
        p1 = geom.Point(0., 0.)
        p2 = geom.Point(3., 4.)
        bd = geom.Box2D(p1, p2)
        self.assertIsInstance(bd, geom.Box2D)

        e1 = geom.Extent(3., 4.)
        bd2 = geom.Box2D(p1, e1)
        self.assertIsInstance(bd2, geom.Box2D)
        self.assertEqual(bd, bd2)

        bd3 = geom.Box2D(p2, e1)
        self.assertNotEqual(bd, bd3)

        self.assertEqual(bd2.dimensions, e1)
        self.assertEqual(bd2.area, 12)
        self.assertSequenceEqual(bd.center, (1.5, 2))
        self.assertEqual(bd.center_x, 1.5)
        self.assertEqual(bd.center_y, 2.0)

        # Create object using repr.
        r = eval(repr(bd))
        self.assertEqual(r, bd)


if __name__ == '__main__':
    unittest.main()
