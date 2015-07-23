from __future__ import print_function, division, absolute_import
import re
from enum import Enum, unique

from astropy.time import Time, TimeUnix, TimeFromEpoch, TimeDelta

"""
Reimplementation of some of daf_base.DateTime using astropy.time
to investigate callability from C++.
"""


@unique
class Timescale(Enum):
    TAI = 0
    UTC = 1
    TT = 2


@unique
class DateSystem(Enum):
    JD = 0
    MJD = 1
    EPOCH = 2  # Assumes Julian Epoch

class TimeTAISinceUnix(TimeUnix):
    """
    Unix time: TAI seconds from 1970-01-01 00:00:00 UTC.

    Required because TimeUnix always uses 86400 seconds per day
    so is not real UTC on leap days.
    """
    name = 'taiunix'
    epoch_scale = 'tai'

class TimeTTSinceUnix(TimeUnix):
    """
    Unix time: TT seconds from 1970-01-01 00:00:00 UTC.

    Required because TimeUnix always uses 86400 seconds per day
    so is not real UTC on leap days.
    """
    name = 'ttunix'
    epoch_scale = 'tt'

class TimeUTCSinceUnix(TimeUnix):
    """
    Unix time: TAI seconds from 1970-01-01 00:00:00 UTC.

    Required because TimeUnix always uses 86400 seconds per day
    so is not real UTC on leap days.
    """
    name = 'utcunix'
    epoch_scale = 'utc'

class TimeLSSTNano(TimeFromEpoch):
    """
    Nanoseconds since unix epoch. Low precision.
    """
    name = "lsstnsec"
    unit = 1.0e-9 / 86400.
    epoch_val = 40587.0
    epoch_val2 = None
    epoch_scale = "utc"
    epoch_format = "mjd"

class DateTime(object):
    # The Python API requires the enums are class attributes of DateTime
    JD = DateSystem.JD
    MJD = DateSystem.MJD
    EPOCH = DateSystem.EPOCH
    TAI = Timescale.TAI
    UTC = Timescale.UTC
    TT = Timescale.TT
    _EPOCH_INTEGER_LEAP = 63072000
    DEBUG = False

    @classmethod
    def now(self):
        t = Time.now()
        t.precision = 9
        return DateTime(t)

    @classmethod
    def _import_date_system(cls, system):
        """
        Determine the date system. Return argument if it is already
        a DateSystem enum, create one if we are given an integer (which
        can happen via C++). We have no way to enforce that python users
        specify arguments with proper enums.
        """
        if isinstance(system, DateSystem):
            return system
        sys_lut = { 0: DateSystem.JD, 1: DateSystem.MJD, 2: DateSystem.EPOCH }
        if system in sys_lut:
            return sys_lut[system]
        raise ValueError("Supplied date systen value ({}) is not valid".format(system))

    @classmethod
    def _import_scale(cls, scale):
        """
        Determine the time scale. Return argument if it is already
        a Timescale enum, create one if we are given an integer (which
        can happen via C++). We have no way to enforce that python users
        specify arguments with proper enums.
        """
        if isinstance(scale, Timescale):
            return scale
        scale_lut = { 0: Timescale.TAI, 1: Timescale.UTC, 2: Timescale.TT }
        if scale in scale_lut:
            return scale_lut[scale]
        raise ValueError("Supplied scale value ({}) is not valid".format(scale))

    @classmethod
    def _scale_to_astropy(cls, scale):
        """
        Convert a Timescale enum to the equivalent astropy string.
        """
        if not isinstance(scale, Timescale):
            raise ValueError("Supplied timescale is not a Timescale enum")
        return scale.name.lower()

    @classmethod
    def _system_to_astropy(cls, system):
        """
        Convert a DateSystem enum to the equivalent astropy string.
        """
        if not isinstance(system, DateSystem):
            raise ValueError("Supplied system is not a DateSystem enum")
        if system in (DateSystem.MJD, DateSystem.JD):
            sysstr = system.name.lower()
        elif system is DateSystem.EPOCH:
            sysstr = "jyear"
        else:
            raise ValueError("Supplied system enum is not recognized: {}".format(system))
        return sysstr

    def _in_timescale(self, scale):
        if scale is Timescale.UTC:
            t = self._internal.utc
        elif scale is Timescale.TAI:
            t = self._internal.tai
        elif scale is Timescale.TT:
            t = self._internal.tt
        else:
            raise ValueError("Unexpected time scale provided: {}".format(scale))
        return t

    def _in_format(self, t, system):
        if system is DateSystem.MJD:
            f = t.mjd
        elif system is DateSystem.JD:
            f = t.jd
        elif system is DateSystem.EPOCH:
            f = t.jyear
        else:
            raise ValueError("Unexpected data system provided: {}".format(system))
        return f

    # Python2 does not let us use (*arg, system=X, scale=Y) argument style
    def __init__(self, *args, **kwargs):
        """
        Position arguments:
        nsecs: (int) nanoseconds since epoch (uses scale)
        date: (double) date in system (uses system and scale)
        year, month, day, hr, min, sec (uses scale)
        iso8601: (string) ISO string format in UTC only

        Optional arguments:
        system: Defaults to DateSystem.MJD
        scale: Defaults to Timescale.TAI

        Can also take an Astropy Time object, which will be copied.

        If no arguments are supplied the constructor will assume 0 nanoseconds.
        """
        if self.DEBUG:
            print("Entering DateTime constructor with {} arguments".format(len(args)))
            print("Args", args)
        if len(args):
            if isinstance(args[0], Time):
                self._internal = args[0].copy(format="mjd")
                return
        else:
            # Assume 0 nanoseconds if no arguments at al
            args = [0]

        # Support scale= and also explicit system+scale arguments
        if len(args) == 2 or len(args) == 7:
            # Just have a scale
            args = list(args)
            kwargs["scale"] = self._import_scale(args.pop())
        elif len(args) == 3 or len(args) == 8:
            args = list(args)
            kwargs["scale"] = self._import_scale(args.pop())
            kwargs["system"] = self._import_date_system(args.pop())

        if "system" not in kwargs:
            kwargs["system"] = DateSystem.MJD
        if "scale" not in kwargs:
            kwargs["scale"] = Timescale.TAI

        # We are going to work out the three arguments for the astropy Time constructor
        format = "isot"
        scale = self._scale_to_astropy(kwargs["scale"])
        time_arg = None
        fraction = None
        if self.DEBUG:
            print("Arg:", args[0], "Scale=",scale)
        if len(args) == 1:
            # in current compatibility scheme have to look for string vs float vs int types
            if isinstance(args[0], basestring):
                time_arg = args[0]
                scale = "utc"
                # daf_base supports a compact string form that is not supported
                # directly by Astropy: YYYYMMDDTHHMMSSZ, optional with decimal fraction
                # we have to translate it before it hits astropy
                matcher = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(\.\d+)?Z")
                matched = matcher.search(time_arg)
                if matched:
                    parts = matched.groups()
                    time_arg = "{0}-{1}-{2}T{3}:{4}:{5}".format(*parts[0:6])
                    if parts[6] is not None:
                        time_arg += parts[6]
            elif isinstance(args[0], long) or isinstance(args[0], int):
                # Astropy does not have a nanosec representation
                # for now we risk losing precision
                # "unix" does not work properly for leap days (the extra second is spread out over the day)
                # so we have to work out the TAI delta and specify
                # TAI epoch seconds

                # Fractions of seconds will be tracked separately as Astropy does not handle
                # nanosecond integers natively.

                nsecs = args[0]
                fraction = int(str(abs(nsecs))[-9:])
                fracpositive = False if nsecs < 0 else True
                time_arg = int(nsecs/1e9)
                if kwargs["scale"] is Timescale.TAI:
                    format = "taiunix"
                elif kwargs["scale"] is Timescale.UTC:
                    format = "taiunix"
                    ttmp = Time(time_arg, format="unix", scale="utc")
                    deltat = ttmp.taiunix - ttmp.unix
                    # Massive hack here: since "unix" seconds are not real seconds
                    # on leap days we have to force deltat to be an integer. This
                    # is broken before 1972. Need to obtain actual TAI-UTC offset from astropy.time.
                    if time_arg > DateTime._EPOCH_INTEGER_LEAP:
                        deltat = int(deltat + 0.5)
                    time_arg += deltat
                elif kwargs["scale"] is Timescale.TT:
                    format = "ttunix"
                else:
                    raise ValueError("Unsupported timescale argument")

            elif isinstance(args[0], float):
                format = self._system_to_astropy(kwargs["system"])
                time_arg = args[0]
            else:
                raise ValueError("Can not work out what first argument is for DateTime: {}".format(args[0]))
        elif len(args) == 6:
            # Put content into an ISO 8601 string and use that
            time_arg = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}".format(*args)
            format = "isot"
        else:
            raise ValueError("Unexpected number of arguments in DateTime constructor")
        if self.DEBUG:
            print("Time Arg: {0!r}".format(time_arg))
        self._internal = Time(time_arg, format=format, scale=scale, precision=9)

        # Handle fractional nanoseconds. Experiment with two approaches. For
        # positive fractions we reparse an ISO format date. For negative
        # fractions we use a TimeDelta object.
        if fraction is not None and fraction != 0:
            t = self._internal
            if fracpositive:
                t.precision = 0
                isostring = "{}.{:09d}".format(t.isot, fraction)
                if self.DEBUG:
                    print("Adjusting fractional seconds as string: {}", isostring)
                self._internal = Time(isostring, format="isot", scale=scale, precision=9)
            else:
                secs = float("0.{:09d}".format(fraction))
                ts = scale if scale != "utc" else "tai"
                td = TimeDelta(secs, format="sec", scale=ts)
                if self.DEBUG:
                    print("Adjusting fractional seconds negative: {}", td)
                self._internal -= td

        if self.DEBUG:
            print("Internal: ",repr(self._internal.copy(format="isot").utc))
            print("Internal: ",repr(self._internal.copy(format="isot").tai))
            print("Internal: ",repr(self._internal.copy(format="isot").tt))
            print("Internal: ",repr(self._internal.copy(format="mjd")))
            print("Internal: ",repr(self._internal.copy(format="unix")))
            print("Internal: ",repr(self._internal.copy(format="taiunix")))
            print("Internal: ",repr(self._internal.copy(format="utcunix")))
        return

    def nsecs(self, *args):
        """
        Return the nanosecs in epoch.

        Follow the LSST convention where TAI is simply the actual number
        of elapsed seconds since epoch but UTC does not include leap seconds
        in the count.

        TT not yet supported
        """
        if self.DEBUG:
            print("Entering nsecs() method:", args)
        if len(args) and args[0] is Timescale.TT:
            raise ValueError("nsecs() does not yet support TT timescale")

        if len(args):
            scale = self._import_scale(args[0])
        else:
            scale = Timescale.TAI

        # Asking for the unix epoch numbers in nanosecond precision
        # is prone to error. So we get the integer part and then
        # request the fractional second by stringifying and relying on
        # astropy time internals to handle precision.
        t = self._internal.copy(format="mjd")

        if scale is Timescale.TAI:
            integer = int(t.taiunix)
        elif scale is Timescale.UTC:
            integer = int(t.unix)
        else:
            raise ValueError("Unexpected timescale in nsecs call")

        # We always ask for the ISO form in TAI after 1972 as we are solely interested
        # in the fractional seconds and the offset is an integer. Prior to 1972 we use
        # UTC and hope for the best.
        t.precision = 9
        if t.unix > DateTime._EPOCH_INTEGER_LEAP:
            iso = t.tai.isot
        else:
            iso = t.utc.isot
        if self.DEBUG:
            print("NSECS String:", iso, " >> ", integer, ".", iso[20:29])
        return long(str(integer) + iso[20:29] + "L")

    def get(self, *args):
        """
        Return floating point representation of time.
        Optional positional arguments:
        system
        scale

        system must be present for scale to be specified.
        """
        scale = Timescale.TAI
        system = DateSystem.MJD
        if len(args) == 2:
            scale = self._import_scale(args[1])
        if len(args):
            system = self._import_date_system(args[0])

        # First get a Time object in the right timescale
        t = self._in_timescale(scale)

        # Now we need to format it properly based on the system
        return self._in_format(t, system)

    def mjd(self, *args):
        """
        Return MJD of supplied time scale. scale defaults to TAI.
        """
        scale = Timescale.TAI
        if len(args):
            scale = args[0]

        t = self._in_timescale(scale)
        return t.mjd

    def __eq__(self, rhs):
        return self._internal == rhs._internal

    def __ne__(self, rhs):
        return self._internal != rhs._internal

    def __str__(self):
        t = self._internal.copy(format="isot").utc
        t.precision = 9
        iso = t.isot
        # daf_base seems to want the Z added if we have a UTC time
        if t.scale == "utc":
            iso = iso + "Z"
        return iso

    def __repr__(self):
        # We report with TAI nanoseconds
        return "{}({})".format(self.__class__.__name__, self.nsecs(Timescale.TAI))

    def toString(self):
        return str(self)

    def toPython(self, timescale=None):
        """Convert a DateTime to Python's datetime

        @param timescale  Timescale for resultant datetime
        """
        import datetime
        nsecs = self.nsecs(timescale) if timescale is not None else self.nsecs()
        return datetime.datetime.utcfromtimestamp(nsecs/10**9)

