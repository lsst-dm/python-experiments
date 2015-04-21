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


"""
Experimental reimplementation of afwImage.ExposureX.

Work in progress. Documentation is not meant to be complete.

"""
import numpy as np
import lsst.afw.image as afwImage
from . import geom


class Exposure (object):

    def __init__(self, *args, **kwargs):
        """
        Constructor for an exposure. Currently forwards on arguments to corresponding afw ExposureX
        constructor.

        Current constructors:

        width, height, wcs=
        width, height
        dimensions=, wcs=
        dimensions=
        None
        bbox, wcs=
        bbox
        maskedImage, wcs=
        maskedImage
        fileName, bbox=, origin=PARENT, conformMasks=False
        fileName, bbox=, origin=PARENT
        fileName, bbox=
        fileName
        manager, bbox=, origin=PARENT, conformMasks=False
        manager, bbox=, origin=PARENT
        manager, bbox=
        manager
        fitsfile, bbox=, origin=PARENT, conformMasks=False
        fitsfile, bbox=, origin=PARENT
        fitsfile, bbox=
        fitsfile
        src, deep=False
        src,
        src, bbox, origin=PARENT, deep=False
        src, bbox, origin=PARENT
        src, bbox

        exposure = afwExperiment.Exposure( 100, 100, wcs )
        exposure = afwExperiment.Exposure( Extent(100, 100) )
        exposure = afwExperiment.Exposure( dtype=float32 )
        """
        # Check to see if this is an empty object
        if "empty" in kwargs and kwargs["empty"]:
            return

        # Need to extract dtype from keyword args and then forward on to low-level
        # constructor
        dtype = self._determine_dtype(kwargs)
        self._Exposure = self._create_ExposureX(dtype, *args, **kwargs)

    @classmethod
    def _create_ExposureX(cls, dtype, *args, **kwargs):

        # Object translation
        if isinstance(args[0], geom.ExtentBase):
            args = list(args)
            args[0] = args[0]._swig_object

        lut = dict({
            np.float32: afwImage.ExposureF,
            np.float64: afwImage.ExposureD,
            np.int32: afwImage.ExposureI,
            })
        if dtype in lut:
            return lut[dtype](*args, **kwargs)
        raise ValueError("Unsupported data type for exposure")

    @classmethod
    def _determine_dtype(cls, options):
        if "dtype" in options:
            dtype = options["dtype"]
            del options["dtype"]
        else:
            dtype = np.float32
        return dtype

    @property
    def bbox(self):
        # Note that getBBox() has a form that takes an ImageOrigin argument
        # but that can not be a property. See get_bbox_with_origin()
        bb = self._Exposure.getBBox()
        return geom.Box2I(_external=bb)

    @property
    def calib(self):
        return self._Exposure.getCalib()

    @property
    def detector(self):
        return self._Exposure.getDetector()

    @property
    def filter(self):
        return self._Exposure.getFilter()

    @property
    def height(self):
        return self._Exposure.getHeight()

    @property
    def info(self):
        return self._Exposure.getInfo()

    @property
    def masked_image(self):
        return self._Exposure.getMaskedImage()

    @property
    def metadata(self):
        return self._Exposure.getMetadata()

    @property
    def psf(self):
        return self._Exposure.getPsf()

    @property
    def wcs(self):
        return self._Exposure.getWcs()

    @property
    def width(self):
        return self._Exposure.getWidth()

    @property
    def x0(self):
        return self._Exposure.getX0()

    @property
    def xy0(self):
        p = self._Exposure.getXY0()
        return geom.Point2I(_external=p)

    @property
    def y0(self):
        return self._Exposure.getY0()

    @calib.setter
    def calib(self, calib):
        self._Exposure.setCalib(calib)

    @detector.setter
    def detector(self, detector):
        self._Exposure.setDetector(detector)

    @filter.setter
    def filter(self, filter):
        self._Exposure.setCalib(filter)

    @masked_image.setter
    def masked_image(self, maskedImage):
        self._Exposure.setMaskedImage(maskedImage)

    @metadata.setter
    def metadata(self, metadata):
        self._Exposure.setMetadata(metadata)

    @psf.setter
    def psf(self, psf):
        self._Exposure.setPsf(psf)

    @wcs.setter
    def wcs(self, wcs):
        self._Exposure.setWcs(wcs)

    @xy0.setter
    def xy0(self, origin):
        self._Exposure.setXY0(origin._swig_object)

    def get_bbox_with_origin(self, origin):
        bb = self._Exposure.getBBox(origin._swig_object)
        return geom.Box2I(_external=bb)

    def has_psf(self):
        return self._Exposure.hasPsf()

    def has_wcs(self):
        return self._Exposure.hasWcs()

    def write_fits(self, *args):
        self._Exposure.writeFits(*args)

    def __deepcopy__(self, memo):
        # Construct an empty object that we can fill explicitly
        copy = type(self)(empty=True)
        copy._Exposure = self._Exposure.clone()
        return copy

    @classmethod
    def read_fits(cls, *args, **kwargs):
        dtype = cls._determine_dtype(kwargs)
        new = cls(empty=True)
        new._Exposure = cls._create_ExposureX(dtype, *args)
        return new
