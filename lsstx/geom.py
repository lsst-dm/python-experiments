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
Experimental reimplementation of afwGeom.

Work in progress. Documentation is not meant to be complete.

"""
import lsst.afw.geom as afwGeom
from . import _helper as h


class CoordinateExpr(object):
    """
    List of boolean values indicating which coordinates met a particular
    expression.
    """

    def __init__(self, ndims, val=False, _external=None):
        """
        Initialise a CoordinateExpr object with N booleans

        c = CoordinateExpr(2, val=False)

        Once created, the values can be modified using standard list
        syntax:

        >>> c = CoordinateExpr(2)
        >>> c[1] = True
        >>> print(c)
        (False, True)
        """
        if _external is not None:
            self._swig_object = _external
        elif ndims == 2:
            self._swig_object = afwGeom.CoordinateExpr2(val)
        elif ndims == 3:
            self._swig_object = afwGeom.CoordinateExpr3(val)
        else:
            raise ValueError("Unsupported dimensionality of {} requested".format(ndims))
        return

    @property
    def dimensions(self):
        """
        Number of dimensions in object.
        """
        return len(self)

    @property
    def x(self):
        """
        Value of first coordinate flag.
        """
        return self[0]

    @property
    def y(self):
        """
        Value of second coordinate flag.
        """
        return self[1]

    @property
    def z(self):
        """
        Value of third coordinate flag if the dimensionality is 3.

        Raises AttributeError if this object has 2 dimensions.
        """
        if self.dimensions == 3:
            return self[2]
        else:
            raise AttributeError("z attribute does not exist")

    @x.setter
    def x(self, x):
        self[0] = x

    @y.setter
    def y(self, y):
        self[1] = y

    @z.setter
    def z(self, z):
        if self.dimensions == 3:
            self[2] = z
        else:
            raise AttributeError("z attribute does not exist")

    def _as_tuple(self):
        """
        Convert the swig object integer list into a tuple
        of booleans.
        """
        return tuple(bool(v) for v in self._swig_object)

    def all_true(self):
        """
        Returns the logical "and" of all coordinate booleans.
        Returns True if all are true, False otherwise.

        combo = cexp.all_true()
        """
        return reduce(lambda x, y: x and y, self._as_tuple())

    def __str__(self):
        """
        String representation of the object. Rendered as a
        list of booleans.
        """
        return "{}".format(self._as_tuple())

    def __len__(self):
        """
        Dimensionality of the object.
        """
        return len(self._swig_object)

    def __setitem__(self, k, v):
        """
        This obect can be used as a sequence.

        ce[1] = False
        ce[0] = True
        """
        self._swig_object[k] = v

    def __getitem__(self, k):
        """
        This object can be used as a sequence.

        print(ce[0])
        """
        v = self._swig_object[k]
        return bool(v)

    def __invert__(self):
        """
        This object can support the ~ operator.
        """
        new = self._swig_object.not_()
        return self.__class__(0, _external=new)

    def __and__(self, rhs):
        """
        This object can support the & operator.
        """
        new = self._swig_object.and_(rhs._swig_object)
        return self.__class__(0, _external=new)

    def __or__(self, rhs):
        """
        This object can support the | operator.
        """
        new = self._swig_object.or_(rhs._swig_object)
        return self.__class__(0, _external=new)

    def __deepcopy__(self, memo):
        """
        This object can be deep copied using copy.deepcopy().
        """
        copy = type(self)(0, self._swig_object.clone())
        return copy


class PointExtent(object):
    """
    Helper routines that are useful for Point and Extent
    constructors.
    """
    # These are all mutable objects
    __hash__ = None

    @classmethod
    def _determine_typedims(cls, *args, **kwargs):
        """
        Helper routine to determine the requested data type and dimensionality
        from arguments supplied to an Extent or Point constructor.

        Dimensionality can be over-ridden using the "_dims" keyword argument.

        Float arguments map to "D" type, integer arguments map to "I" type.

        ndims, dtype, args = cls._determine_typedims(*args, **kwargs)

        The args tuple is returned as it may be modified if a tuple or list
        is found in the supplied arguments.
        """
        argc = len(args)

        ndims = 0
        dtype = None

        if "_dims" in kwargs:
            ndims = kwargs["_dims"]

        if argc == 1:
            result = cls._check_firstarg(args[0])
            if result:
                ndims, dtype, newargs = result
                args = newargs
            elif isinstance(args[0], (tuple, list)):  # Should check for __getitem__ and iterable and !str?
                dtype = cls._determine_dtype(*args[0])
                args = args[0]
                ndims = len(args)
            elif isinstance(args[0], (float, int)):
                dtype = cls._determine_dtype(args[0])
        elif argc == 2 or argc == 3:
            ndims = argc
            dtype = cls._determine_dtype(*args)
        else:
            raise ValueError("Incorrect number of arguments ({}) to Extent constructor".format(argc))
        return ndims, dtype, args

    @classmethod
    def _determine_dtype(cls, *args):
        """
        Returns "D" if any of the supplied arguments are type float.
        Returns "I" if all arguments are type int.

        dtype = cls._determine_dtype(1, 2, 3.4)

        Raises ValueError if other types are found.
        """
        # Assume int, use double if any double present
        dtype = "I"
        for i in args:
            t = type(i).__name__
            if t == "int":
                pass
            elif t == "float":
                dtype = "D"
                break
            else:
                raise ValueError("Unsupported type found {}".format(t))
        return dtype

    @classmethod
    def _determine_class(cls, ndims, dtype, class2I, class2D, class3I, class3D):
        """
        Converts a dimensinality and data type into a python class from one of the
        four supplied.

        class = cls._determine_class(2, "D", Extent2I, Extent2D, Extent3I, Extent3D)

        Raises ValueError if the dimensionality and data type are not recognized.
        """
        newclass = None
        if ndims == 2 and dtype == "I":
            newclass = class2I
        elif ndims == 2 and dtype == "D":
            newclass = class2D
        elif ndims == 3 and dtype == "I":
            newclass = class3I
        elif ndims == 3 and dtype == "D":
            newclass = class3D
        else:
            raise ValueError("Can not determine constructor class from inferred dimensionality or data type")
        # print("{}{} -> {}".format(ndims, dtype, newclass))
        return newclass

    @classmethod
    def _from_swig_object(cls, swig_object):
        """
        Internal routine to construct a Python object from a SWIG object.
        Examines type of SWIG object to determine corresponding Python constructor.

        obj = cls._from_swig_object(swig_object)
        """
        # Bit of a hack
        name = type(swig_object).__name__
        lut = {
            "Extent2D": Extent2D,
            "Extent2I": Extent2I,
            "Point2D": Point2D,
            "Point2I": Point2I,
            "Extent3D": Extent3D,
            "Extent3I": Extent3I,
            "Point3D": Point3D,
            "Point3I": Point3I
            }
        if name in lut:
            return lut[name](_external=swig_object)
        raise ValueError("Unrecognized object type {} from {}".format(type(swig_object), swig_object))


class Point(PointExtent):

    def __new__(cls, *args, **kwargs):
        """
        Create a new Point object. Generic constructor for Point objects,
        returning specific objects based on the supplied arguments.

        Create a Point3I:
          Point(1, 2, 3)
          Point((1, 2, 3))

        Create a Point2D:
          Point(1., 2.)
          Point((1., 2.))

        The dimensionality is determined from the number of arguments and the
        data type determined from the type of the arguments.

        The generic form can not be used to construct an object with a single
        scalar as the dimensionality can not be determined. Also, a pre-existing
        PointNX object can not be supplied as the output type can not be determined
        from the input type.
        """
        # Have to determine which of 2I, 2D, 3D or 3I objects is required
        ndims, dtype, args = cls._determine_typedims(*args, **kwargs)
        newclass = cls._determine_class(ndims, dtype, Point2I, Point2D, Point3I, Point3D)

        # Since we are returning an object that is of a different
        # class then we must explicitly call __init__
        newone = object.__new__(newclass)
        newone.__init__(*args)
        return newone

    @classmethod
    def _check_firstarg(cls, arg0):
        """
        Check that the first argument in the generic constructor is okay.
        """
        if isinstance(arg0, PointBase):
            raise ValueError("Use specific PointNX constructor or deepcopy to create Point from Point")


class ExtentPointBase(object):
    # These are all mutable objects
    __hash__ = None

    def __init__(self, constructor, *args, **kwargs):
        """
        Initialize the object using the supplied SWIG object constructor
        and arguments. Uses the supplied SWIG object if the keyword "_external"
        is given with a SWIG object.
        """
        # if we are being given a swig object directly we use it
        if "_external" in kwargs and kwargs["_external"] is not None:
            self._swig_object = kwargs["_external"]
            return

        # print("In {}.__init__ with {}".format(type(self), constructor))
        # Handle the case where we have an explicit sequence
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        # Convert args to C++ objects
        newargs = h.swigify(args)

        # Call the C++ constructor
        self._swig_object = constructor(*newargs)

    @property
    def dimensions(self):
        """
        Dimensionality of object.
        """
        return self._dimensions

    @property
    def x(self):
        """
        x coordinate.
        """
        return self._swig_object.getX()

    @property
    def y(self):
        """
        y coordinate.
        """
        return self._swig_object.getY()

    @property
    def z(self):
        """
        z coordinate if the dimensionality is 3.

        Raises AttributeError if this is a 2d object.
        """
        if self.dimensions == 3:
            return self._swig_object.getZ()
        else:
            raise AttributeError("z attribute does not exist")

    @x.setter
    def x(self, x):
        self._swig_object.setX(x)

    @y.setter
    def y(self, y):
        self._swig_object.setX(y)

    @z.setter
    def z(self, z):
        if self.dimensions == 3:
            return self._swig_object.setZ(z)
        else:
            raise AttributeError("z attribute does not exist")

    def swap(self, other):
        """
        Swap the coordinate values of two objects.

        ep1.swap(ep2)
        """
        self._swig_object.swap(other._swig_object)

    def ge(self, other):
        """
        Compare two objects and return a CoordinateExpre object indicating which
        coordinates in the primary object are greater than or equal to the corresponding
        coordinates in the supplied object.
        """
        return CoordinateExpr(0, _external=self._swig_object.ge(other._swig_object))

    def gt(self, other):
        """
        Compare two objects and return a CoordinateExpre object indicating which
        coordinates in the primary object are greater than the corresponding
        coordinates in the supplied object.
        """
        return CoordinateExpr(0, _external=self._swig_object.gt(other._swig_object))

    def le(self, other):
        """
        Compare two objects and return a CoordinateExpre object indicating which
        coordinates in the primary object are less than or equal to the corresponding
        coordinates in the supplied object.
        """
        return CoordinateExpr(0, _external=self._swig_object.le(other._swig_object))

    def lt(self, other):
        """
        Compare two objects and return a CoordinateExpre object indicating which
        coordinates in the primary object are less than the corresponding
        coordinates in the supplied object.
        """
        return CoordinateExpr(0, _external=self._swig_object.lt(other._swig_object))

    def __deepcopy__(self, memo):
        """
        Implement copy.deepcopy() support.
        """
        # Construct an empty object that we can fill explicitly
        copy = type(self)()
        copy._swig_object = self._swig_object.clone()
        return copy

    def __str__(self):
        """
        Returns a string formatted version of the object.
        """
        return "{}".format(self._swig_object)

    def __repr__(self):
        """
        Returns a representation of the object that can be used to recreate
        the object.
        """
        return "{}{}".format(type(self).__name__, self)

    def __eq__(self, other):
        """
        Implementation of the equality operator.
        """
        if not hasattr(other, "_swig_object"):
            return False
        return self._swig_object == other._swig_object

    def __ne__(self, other):
        """
        Implementation of the not equal operator.
        """
        return self._swig_object != other._swig_object

    def __lt__(self, other):
        """
        Returns true if all coordinates are less than those
        in the supplied object.
        """
        ce = self.lt(other)
        return ce.all_true()

    def __gt__(self, other):
        """
        Returns true if all coordinates are greater than those
        in the supplied object.
        """
        ce = self.gt(other)
        return ce.all_true()

    def __le__(self, other):
        """
        Returns true if all coordinates are less than or equal to those
        in the supplied object.
        """
        ce = self.le(other)
        return ce.all_true()

    def __ge__(self, other):
        """
        Returns true if all coordinates are greater than or equal to those
        in the supplied object.
        """
        ce = self.ge(other)
        return ce.all_true()

    def __iadd__(self, other):
        """
        Support +=
        """
        self._swig_object += other._swig_object
        return self

    def __add__(self, other):
        """
        Add an Extent to a Point and return a new Point.
        Add an Extent to an Extent and return a new Extent.
        """
        new = self._swig_object + other._swig_object
        return self.__class__(_external=new)

    def __isub__(self, other):
        """
        In place subraction (-=).
        """
        self._swig_object -= other._swig_object
        return self

    def __sub__(self, other):
        """
        Subtract and return a new object.
        """
        new = self._swig_object - other._swig_object
        # Return can be Extent or Point depending on type of other
        cls = Point
        if "Extent" in new.__class__.__name__:
            cls = Extent
        return cls._from_swig_object(new)

    def __len__(self):
        """
        Return the length/dimensionality of the object.
        """
        return len(self._swig_object)

    def __getitem__(self, k):
        """
        Implement sequence item retrieve by index.
        """
        return self._swig_object[k]

    def __setitem__(self, k, v):
        """
        Implement sequence item setting by index.
        """
        self._swig_object[k] = v


class PointBase(ExtentPointBase):

    def distance_squared(self, other):
        """
        Return the distance squared between two points.
        """
        return self._swig_object.distanceSquared(other._swig_object)

    def scale(self, factor):
        """
        Scale a point by the supplied numeric factor.
        """
        self._swig_object.scale(factor)

    def shift(self, offset):
        """
        Shift a Point by the supplied Extent.
        """
        self._swig_object.shift(offset._swig_object)


class Point2(Point):

    def __new__(cls, *args, **kwargs):
        """
        Create an Point object with dimensionality 2.
        """
        kwargs = {"_dims": 2}
        # Not allowed to use python3 super()
        return super(Point2, cls).__new__(cls, *args, **kwargs)


class Point3(Point):

    def __new__(cls, *args):
        """
        Create an Point object with dimensionality 3.
        """
        kwargs = {"_dims": 3}
        return super(Point3, cls).__new__(cls, *args, **kwargs)


class Point2D(PointBase):

    def __init__(self, *args, **kwargs):
        """
        Initialize a Point2D object.

        Arguments are forwarded to the SWIG constructor.

        Keyword argument "_external" can be used to supply an explicit SWIG
        object.
        """
        self._dimensions = 2
        self._dtype = "D"
        super(Point2D, self).__init__(afwGeom.Point2D, *args, **kwargs)


class Point2I(PointBase):

    def __init__(self, *args, **kwargs):
        """
        Initialize a Point2I object.

        Arguments are forwarded to the SWIG constructor.

        Keyword argument "_external" can be used to supply an explicit SWIG
        object.
        """
        self._dimensions = 2
        self._dtype = "I"
        super(Point2I, self).__init__(afwGeom.Point2I, *args, **kwargs)


class Point3D(PointBase):

    def __init__(self, *args, **kwargs):
        """
        Initialize a Point3D object.

        Arguments are forwarded to the SWIG constructor.

        Keyword argument "_external" can be used to supply an explicit SWIG
        object.
        """
        self._dimensions = 3
        self._dtype = "D"
        super(Point3D, self).__init__(afwGeom.Point3D, *args, **kwargs)


class Point3I(PointBase):

    def __init__(self, *args, **kwargs):
        """
        Initialize a Point3I object.

        Arguments are forwarded to the SWIG constructor.

        Keyword argument "_external" can be used to supply an explicit SWIG
        object.
        """
        self._dimensions = 3
        self._dtype = "I"
        super(Point3I, self).__init__(afwGeom.Point3I, *args, **kwargs)


class Extent(PointExtent):

    @classmethod
    def _check_firstarg(cls, arg0):
        dtype = None
        ndims = None
        newargs = None
        if isinstance(arg0, ExtentBase):
            raise ValueError("Use specific ExtentNX constructor or deepcopy to create Extent from Extent",
                             cls, type(arg0), repr(arg0))
        elif isinstance(arg0, PointBase):
            ndims = arg0.dimensions
            dtype = arg0._dtype
            newargs = (arg0._swig_object)
        if dtype is not None:
            return (ndims, dtype, newargs)

    def __new__(cls, *args, **kwargs):
        """
        Generic constructor for Extent objects deriving the type and dimensionality
        from the arguments. The class of the returned object depends on the arguments.

        Supports following constructors:

        Point -- the resultant Extent will have the same type and dimensionality as the Point.
        x, y
        xy tuple

        The following constructors can not be used and require explict type or
        dimensionality:

        scalar -- need to specify the dimensionality. Use Extent2() or Extent3().

        Extent -- need to specify the type of the new Extent as the type does not need
        to match. This form can only be used with a ExtentNX constructor explcitly.

        """
        # print("CLASS IS {}".format(cls))
        # Have to determine which of 2I, 2D, 3D or 3I objects is required
        ndims, dtype, args = cls._determine_typedims(*args, **kwargs)
        newclass = cls._determine_class(ndims, dtype, Extent2I, Extent2D,
                                        Extent3I, Extent3D)

        # Since we are returning an object that is of a different
        # class then we must explicitly call __init__
        newone = object.__new__(newclass)
        newone.__init__(*args)
        return newone


class Extent2(Extent):

    def __new__(cls, *args, **kwargs):
        kwargs["_dims"] = 2
        # Not allowed to use python3 super()
        # print("In Extent2.__new__")
        return super(Extent2, cls).__new__(cls, *args, **kwargs)


class Extent3(Extent):

    def __new__(cls, *args):
        kwargs = {"_dims": 3}
        return super(Extent3, cls).__new__(cls, *args, **kwargs)


class ExtentBase(ExtentPointBase):
    def compute_squared_norm(self):
        return self._swig_object.computeSquaredNorm()


class ExtentI(ExtentBase):

    def compute_norm(self):
        raise TypeError("Cannot compute norm of integer extent")


class ExtentD(ExtentBase):

    def compute_norm(self):
        return self._swig_object.computeNorm()

    def compute_squared_norm(self):
        return self._swig_object.computeSquaredNorm()


class Extent2D(ExtentD):

    def __init__(self, *args, **kwargs):
        self._dimensions = 2
        self._dtype = "D"
        super(Extent2D, self).__init__(afwGeom.Extent2D, *args, **kwargs)


class Extent2I(ExtentI):

    def __init__(self, *args, **kwargs):
        self._dimensions = 2
        self._dtype = "I"
        super(Extent2I, self).__init__(afwGeom.Extent2I, *args, **kwargs)


class Extent3D(ExtentD):

    def __init__(self, *args, **kwargs):
        self._dimensions = 3
        self._dtype = "D"
        super(Extent3D, self).__init__(afwGeom.Extent3D, *args, **kwargs)


class Extent3I(ExtentI):

    def __init__(self, *args, **kwargs):
        self._dimensions = 3
        self._dtype = "I"
        super(Extent3I, self).__init__(afwGeom.Extent3I, *args, **kwargs)


class BoxBase(object):
    # These are all mutable objects
    __hash__ = None

    def __init__(self, constructor, *args, **kwargs):
        # if we are being given a swig object directly we use it
        if "_external" in kwargs and kwargs["_external"] is not None:
            self._swig_object = kwargs["_external"]
            return

        # print("In {}.__init__ with {}".format(type(self), constructor))
        newargs = h.swigify(args)

        # Call the C++ constructor
        self._swig_object = constructor(*newargs)

    @property
    def area(self):
        return self._swig_object.getArea()

    @property
    def center(self):
        p2x = self._swig_object.getCenter()
        return Point._from_swig_object(p2x)

    @property
    def center_x(self):
        return self._swig_object.getCenterX()

    @property
    def center_y(self):
        return self._swig_object.getCenterY()

    @property
    def corners(self):
        vec = self._swig_object.getCorners()
        return tuple([Point._from_swig_object(v) for v in vec])

    @property
    def dimensions(self):
        return Extent._from_swig_object(self._swig_object.getDimensions())

    @property
    def height(self):
        return self._swig_object.getHeight()

    @property
    def max(self):
        return Point._from_swig_object(self._swig_object.getMax())

    @property
    def max_x(self):
        return self._swig_object.getMaxX()

    @property
    def max_y(self):
        return self._swig_object.getMaxY()

    @property
    def min(self):
        return Point._from_swig_object(self._swig_object.getMin())

    @property
    def min_x(self):
        return self._swig_object.getMinX()

    @property
    def min_y(self):
        return self._swig_object.getMinY()

    @property
    def width(self):
        return self._swig_object.getWidth()

    def clip(self, other):
        self._swig_object.clip(other._swig_object)

    def contains(self, other):
        return self._swig_object.contains(other._swig_object)

    def flip_lr(self, x_extent):
        self._swig_object.flipLR(x_extent)

    def flip_tb(self, y_extent):
        self._swig_object.flipTB(y_extent)

    def grow(self, buffer):
        self._swig_object.grow(buffer)

    def include(self, point_or_other):
        self._swig_object.include(point_or_other)

    def is_empty(self):
        return self._swig_object.isEmpty()

    def overlaps(self, other):
        return self._swig_object.overlaps(other)

    def set(self, other):
        return self._swig_object.set(other)

    def shift(self, offset):
        self._swig_object.shift(offset._swig_object)

    def swap(self, other):
        self._swig_object.swap(other._swig_object)

    def __str__(self):
        return "{}".format(self._swig_object)

    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, repr(self.min),
                                   repr(self.max))

    def __ne__(self, rhs):
        return self._swig_object != rhs._swig_object

    def __eq__(self, rhs):
        return self._swig_object == rhs._swig_object


class Box2D(BoxBase):

    def __init__(self, *args, **kwargs):
        self._dtype = "I"
        super(Box2D, self).__init__(afwGeom.Box2D, *args, **kwargs)


class Box2I(BoxBase):

    def __init__(self, *args, **kwargs):
        self._dtype = "I"
        super(Box2I, self).__init__(afwGeom.Box2I, *args, **kwargs)
