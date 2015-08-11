from setuptools import setup, find_packages

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

setup(
    name="lsstx",
    version="0.0.2",
    description="Experimental interfaces for LSST DM software stack",
    license="GPL",
    author="LSST DM Team",
    author_email="dm-devel@lists.lsst.org",
    packages=find_packages(exclude=['tests']),
    test_suite="tests",

    setup_requires=[
        # python setup.py flake8
        # to check the code
        "flake8",
        # For the astropy.time module
        "astropy",
    ],
)
