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
Experimental reimplementation of afwImage.

Work in progress. Documentation is not meant to be complete.

"""
import numpy as np
import lsst.afw.image as afwImage
from . import geom
from . import _helper as h
from copy import deepcopy


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

        if "_external" in kwargs and kwargs["_external"] is not None:
            self._swig_object = kwargs["_external"]
            return

        # Need to extract dtype from keyword args and then forward on to low-level
        # constructor
        dtype = h.determine_dtype(kwargs)
        self._swig_object = self._create_ExposureX(dtype, *args, **kwargs)

    @classmethod
    def _create_ExposureX(cls, dtype, *args, **kwargs):
        lut = {
            np.float32: afwImage.ExposureF,
            np.float64: afwImage.ExposureD,
            np.int32: afwImage.ExposureI,
            }
        return h.new_swig_object(dtype, lut, *args, **kwargs)

    @property
    def bbox(self):
        # Note that getBBox() has a form that takes an ImageOrigin argument
        # but that can not be a property. See get_bbox_with_origin()
        bb = self._swig_object.getBBox()
        return geom.Box2I(_external=bb)

    @property
    def calib(self):
        return self._swig_object.getCalib()

    @property
    def detector(self):
        return self._swig_object.getDetector()

    @property
    def filter(self):
        return self._swig_object.getFilter()

    @property
    def height(self):
        return self._swig_object.getHeight()

    @property
    def info(self):
        return self._swig_object.getInfo()

    @property
    def masked_image(self):
        return MaskedImage(_external=self._swig_object.getMaskedImage())

    @property
    def metadata(self):
        return self._swig_object.getMetadata()

    @property
    def psf(self):
        return self._swig_object.getPsf()

    @property
    def wcs(self):
        return self._swig_object.getWcs()

    @property
    def width(self):
        return self._swig_object.getWidth()

    @property
    def x0(self):
        return self._swig_object.getX0()

    @property
    def xy0(self):
        p = self._swig_object.getXY0()
        return geom.Point2I(_external=p)

    @property
    def y0(self):
        return self._swig_object.getY0()

    @calib.setter
    def calib(self, calib):
        self._swig_object.setCalib(calib)

    @detector.setter
    def detector(self, detector):
        self._swig_object.setDetector(detector)

    @filter.setter
    def filter(self, filter):
        self._swig_object.setCalib(filter)

    @masked_image.setter
    def masked_image(self, maskedImage):
        self._swig_object.setMaskedImage(maskedImage._swig_object)

    @metadata.setter
    def metadata(self, metadata):
        self._swig_object.setMetadata(metadata)

    @psf.setter
    def psf(self, psf):
        self._swig_object.setPsf(psf)

    @wcs.setter
    def wcs(self, wcs):
        self._swig_object.setWcs(wcs)

    @xy0.setter
    def xy0(self, origin):
        self._swig_object.setXY0(origin._swig_object)

    def get_bbox_with_origin(self, origin):
        bb = self._swig_object.getBBox(origin._swig_object)
        return geom.Box2I(_external=bb)

    def has_psf(self):
        return self._swig_object.hasPsf()

    def has_wcs(self):
        return self._swig_object.hasWcs()

    def write_fits(self, *args):
        self._swig_object.writeFits(*args)

    def __deepcopy__(self, memo):
        # Construct an empty object that we can fill explicitly
        copy = type(self)(empty=True)
        copy._swig_object = self._swig_object.clone()
        return copy

    @classmethod
    def read_fits(cls, *args, **kwargs):
        dtype = h.determine_dtype(kwargs)
        new = cls(empty=True)
        new._swig_object = cls._create_ExposureX(dtype, *args)
        return new


class Image(object):

    def __init__(self, *args, **kwargs):
        if "_external" in kwargs and kwargs["_external"] is not None:
            self._swig_object = kwargs["_external"]
            return
        raise NotImplementedError("Can not yet init a new Image object")

    def __getitem__(self, slice):
        a = self._swig_object.getArray()
        return a[slice]

    def __setitem__(self, slice, item):
        a = self._swig_object.getArray()
        a[slice] = item


class MaskedImage(object):

    def __init__(self, *args, **kwargs):
        if "_external" in kwargs and kwargs["_external"] is not None:
            self._swig_object = kwargs["_external"]
            return
        dtype = h.determine_dtype(kwargs)
        self._swig_object = self._create_MaskedImageX(dtype, *args, **kwargs)

    @classmethod
    def _create_MaskedImageX(cls, dtype, *args, **kwargs):
        lut = {
            np.float32: afwImage.MaskedImageF,
            np.float64: afwImage.MaskedImageD,
            np.int32: afwImage.MaskedImageI,
            np.uint32: afwImage.MaskedImageU,
            }
        return h.new_swig_object(dtype, lut, *args, **kwargs)

    def __getitem__(self, slice):
        """
        Support slicing of a MaskedImage. Returns the slice of each numpy array
        as a tuple.
        """
        arrays = self._swig_object.getArrays()
        return (a[slice] for a in arrays)

    def __setitem__(self, slice, values):
        """
        Given a tuple of replacement values (data, variance, mask) assign them to
        the sliced MaskedImage arrays.
        """
        arrays = self._swig_object.getArrays()
        for a, v in zip(arrays, values):
            a[slice] = v

    @property
    def arrays(self):
        """
        Numpy arrays for image, mask and variance, returned as tuple.
        """
        return self._swig_object.getArrays()

    @property
    def image(self):
        return Image(_external=self._swig_object.getImage(noThrow=True))

    @property
    def mask(self):
        return Image(_external=self._swig_object.getMask(noThrow=True))

    @property
    def variance(self):
        return Image(_external=self._swig_object.getVariance(noThrow=True))

    @property
    def bbox(self):
        # Note that getBBox() has a form that takes an ImageOrigin argument
        # but that can not be a property. See get_bbox_with_origin()
        bb = self._swig_object.getBBox()
        return geom.Box2I(_external=bb)

    @property
    def dimensions(self):
        e = self._swig_object.getDimensions()
        return geom.Extent2I(_external=e)

    def get_bbox_with_origin(self, origin):
        bb = self._swig_object.getBBox(origin._swig_object)
        return geom.Box2I(_external=bb)

    def __deepcopy__(self, memo):
        # Construct an empty object that we can fill explicitly
        copy = type(self)(empty=True)
        copy._swig_object = self._swig_object.clone()
        return copy


class ExposureInfo(object):
    """
    Information about an Exposure
    """
    def __init__(self, wcs=None, psf=None, calib=None, filter=None,
                 detector=None, metadata=None, coadd_inputs=None,
                 info=None, copy_metadata=False,):
        """
        C++ constructor takes:

        Wcs, Psf, Calib, geom.Detector, Filter, daf.base.PropertySet, CoaddInputs
        Wcs, Psf, Calib, geom.Detector, Filter, daf.base.PropertySet
        Wcs, Psf, Calib, geom.Detector
        Wcs, Psf, Calib
        Wcs, Psf
        Wcs
        None
        ExposureInfo, copyMetadata=bool

        Indicating that we can branch on whether the first argument is a Wcs
        or an ExposureInfo or not there at all, and otherwise count the number
        of arguments. ExposureInfo does not seem to be used much in Python code.

        In simple case, forward on to C++ constructor. We know how to do that
        so instead try to implement natively. None of the arguments to the
        constructor are wrapped yet, so all are still C++ SWIGged.

        For the initializer we have the following options:

        Option 1: Just count the arguments, check first for type.
        Option 2: ExposureInfo( wcs=wcs, cal=calib, det=detector, filt=filter...)

        Choose option 2 for this experiment as Option 1 is already in use.
        """
        self.wcs = None
        self.psf = None
        self.detector = None
        self.calib = None
        self.metadata = None
        self.filter = None
        self.coadd_inputs = None

        if info is None:
            self.wcs = wcs
            self.psf = psf
            self.detector = detector
            self.calib = calib
            self.metadata = metadata
            self.filter = filter
            self.coadd_inputs = coadd_inputs
        else:
            # Copy info. These are usually SWIGged objects
            for attr, value in info.__dict__.items():
                if value is not None:
                    # Only clone if clone is implemented, else copy reference.
                    # Some objects are immutable so no need to clone
                    # in .cc file, Calib is deep copied using a copy constructor
                    # but that interface is not exposed to Python.
                    # lsst.daf.base.PropertySet has deepCopy() rather than clone()
                    # and we may not always want to deep copy that.
                    if hasattr(value, "clone"):
                        value = value.clone()
                    elif hasattr(value, "deepCopy"):
                        # Deep copy unless this is metadata and we have been told not to
                        if attr == "metadata" and not copy_metadata:
                            pass
                        else:
                            value = value.deepCopy()
                    self.__dict__[attr] = value

    def has_calib(self):
        """
        Indicate whether a calib attribute has been set.
        Should this be a property itself?
        """
        return self.calib is not None

    def has_coadd_inputs(self):
        """
        Indicate whether a coadd_inputs attribute has been set.
        """
        return self.coadd_inputs is not None

    def has_detector(self):
        """
        Indicate whether a detector attribute has been set.
        """
        return self.detector is not None

    def has_psf(self):
        """
        Indicate whether a psf attribute has been set.
        """
        return self.psf is not None

    def has_wcs(self):
        """
        Indicate whether a wcs attribute has been set.
        """
        return self.wcs is not None


class ExposurePy(object):

    def __init__(self, *args, **kwargs):
        """
        Initialise an ExposurePy object. The question is whether
        we use keyword arguments such as "mi=masked_image" or
        whether we check the type of each argument in a list trying
        to work out what the user wanted.

        Current ExposureX constructor has:

        2 integers, optional WCS
        Extent object, optional WCS
        No arguments
        BBox object, optional WCS
        MaskedImage, optional WCS
        filename, optional BBox and origin
        FITS file object, optional BBox and origin
        Another Exposure object, optional BBox, origin and deepcopy flag.

        So check first argument for integer, Extent, BBox, MaskedImage, string, etc

        Python 3 allows "__init__(self, *args, wcs=None...)" but Python 2 does not.
        This means that for Python2 we have to use **kwargs which has the disadvantage
        of (1) not being self-documenting as to what the optional arguments are, and
        (2) requiring more cruft in the code itself.

        Optional arguments:

        wcs
        bbox
        origin
        conform_masks
        deep

        ei1 = ExposureInfo(32, 64, wcs=WCS)
        ei2 = ExposureInfo(ei1, deep=True)
        """
        if len(args) == 0:
            return

        deep = False
        if deep in kwargs:
            deep = kwargs["deep"]

        if isinstance(args[0], "ExposurePy"):
            mi = args[0].masked_image
            if deep:
                mi = deepcopy(mi)
            self.masked_image = mi
        else:
            self.masked_image = MaskedImage(*args)


def make_exposure(*args):
    """
    Create an Exposure object from the supplied arguments.

    exposure = make_exposure(mi)
    """
    # Convert the argument list to swig arguments as required
    newargs = h.swigify(args)
    _swig_object = afwImage.makeExposure(*newargs)
    return Exposure(_external=_swig_object)
