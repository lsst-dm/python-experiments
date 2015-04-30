 Python/C++ Interface investigations
 ===

Following a discussion with the Astropy team it was decided that we would consider whether the Python/C++ boundary in the LSST software stack is currently in the correct location. At present, the default situation is for much of the core LSST code to be written in C++ and then provide a SWIG interface for use from Python. This is done so that other C++ code can use the infrastructure libraries interchangeably without having to know that Python is involved at all. This approach leads to two obvious shortcomings when the code is given to someone expecting that the primary language is Python:

1. The default SWIGged Python interfaces do not look "pythonic" in the sense that:

    * Attributes are implemented by explicit getter and setter methods rather than looking like attributes.
    * The constructors tend to be highly complex but also opaque, using `*args` rather than named arguments.
    * Python objects stringify in ways that make them impenetrable to someone who does not have a C++ background:
    ```python
    >>> mi = afwImage.MaskedImageD(5, 4)
    >>> print(repr(mi))
    <lsst.afw.image.imageLib.MaskedImageD; proxy of <Swig Object of type 'boost::shared_ptr< lsst::afw::image::MaskedImage< double,lsst::afw::image::MaskPixel,lsst::afw::image::VariancePixel > > *' at 0x10ab0b480> >
    ```

    * The Python documentation is almost non-existent and very unfriendly to a Python programmer, resulting in the APIs being presented with very little support text and using C++ language concepts. See for example this Python documentation for the `lsst.afw.image.ExposureD.getInfo()` method:
    ```
    getInfo(self, *args)
       getInfo(ExposureD self) -> boost::shared_ptr< lsst::afw::image::ExposureInfo >
       getInfo(ExposureD self) -> boost::shared_ptr< lsst::afw::image::ExposureInfo const >
    ```

2. Classes that are commonly used by Python programmers in astronomy, such as Astropy coordinates and Pandas for table manipulation, are almost impossible to use in relation to LSST software as this functionality is implemented independently in C++.

The current default is for library code to be written in C++ and then SWIGged in order to ensure that the code can be called from C++ and Python and, nominally, to ensure maximum performance. The work described in this document addresses whether we should adopt a "Python First" philosophy in the LSST data management software.

Plan
---

The investigation consisted of 3 phases:

1. Determine the feasibility of wrapping the SWIG interfaces in Python code to present a more Pythonic view of the world to the public interfaces.
2. Take a simple C++ object and reimplement it in Python with the aim of pushing the C++ boundary lower into the stack.
3. Compare performance of cython/numba with native C++.

Wrapping the SWIG
---

The easiest way to hide the C++ is to provide Python "shim" classes around all the SWIG-generated Python classes. For example converting:
```python
e = afwGeom.Extent2I(3, 5)
x = e.getX()
y = e.getY()

exp = afwImage.ExposureD(e)
bbox = exp.getBbox()
area = bbox.getArea()

mi = exp.getMaskedImage()
var = mi.getVariance()
```

to

```python
e = geom.Extent(3, 5)
x = e.x
y = e.y

exp = image.Exposure(e, dtype=np.float64)
bbox = exp.bbox
area = bbox.area

mi = exp.masked_image
var = mi.variance
var[0:2,3:5] = np.array([[1,2],[3,4]])
```

Proof of concept wrappers have been written for `Exposure`, `Extent`, `Point`, `Box`, `MaskedImage`, and `CoordinateExpr`.

Some notes:

* All wrappers use the same attribute name to store the internal SWIGged object. This allows the C++ object to be extracted from the argument list when it is known that the arguments are to be passed to a C++ object.
* As an experiment two different schemes are used for dealing with data types. In `Exposure` the data type is passed in to the constructor using the standard numpy convention. The returned object is a generic `Exposure` containing a SWIGged object of the relevant type (e.g. `ExposureD`). In the second approach the `Extent` and `Point` constructors determine their data type and dimensionality from the supplied arguments but return a typed object of `Extent2I`, `Point3D` etc.
* The code uses PEP8 coding conventions and therefore does not use camel case for method names: `compute_squared_norm` versus `computeSquaredNorm`.


For code examples and an initial implementation see <https://github.com/lsst-dm/python-experiments>.

Reimplementing Exposure
---

To be filled.

Cython/Numba
---

Numba: <http://numba.pydata.org>

Cython: <http://cython.org>

See for example:

* <https://jakevdp.github.io/blog/2013/06/15/numba-vs-cython-take-2/> from 2013.
* <http://continuum.io/blog/numba_performance> also from 2013
* <http://eng.climate.com/2015/04/09/numba-vs-cython-how-to-choose/>

The main issue for LSST is whether the critical performance sections of the code base can be self-contained rather than being tightly integrated into the stack as a whole. One example is convolution of an Image by a PSF. Is there any expectation that a PSF could be defined in pure python code? How do we handle PSFs that vary across the image and so must therefore be calculated dynamically? Even if the PSF is a simple numpy array and the image is a numpy array, how much faster is the C++ implementation than a cython/numba implementation?

Summary
---

The fundamental question is whether the LSST software can be 95% python, with C/C++ limited to key performance areas? Does there have to be any WCS handling in C/C++ or can it be kept entirely in Python? Can the project become a Python project, built with setuptools, documented in Sphinx and distributed on pypi?
