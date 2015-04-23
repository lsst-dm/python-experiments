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
Helper routines for lsstx
"""
import numpy as np


def swigify(args):
    """
    Convert the argument list to swig arguments as required.
    """
    newargs = []
    for a in args:
        if hasattr(a, '_swig_object'):
            newargs.append(a._swig_object)
        else:
            newargs.append(a)
    return newargs


def determine_dtype(options):
    """
    Look for a "dtype" key in the supplied dict. If found, return the value
    of that key and delete it from the dict. Returns a default value of
    np.float32.
    """
    if "dtype" in options:
        dtype = options["dtype"]
        del options["dtype"]
    else:
        dtype = np.float32
    return dtype


def new_swig_object(dtype, lut, *args, **kwargs):
    """
    Instantiate an object of type determined by the look up table
    dict. "dtype" must be a member of "lut". The args and kwargs are
    forwarded to the constructor.
    """
    # Object translation
    args = swigify(args)

    if dtype in lut:
        return lut[dtype](*args, **kwargs)
    raise ValueError("Unsupported data type for exposure")
