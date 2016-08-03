"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""

import re
import time
import struct
import logging

from json import JSONEncoder

# other stuff
from google.protobuf.internal import encoder
from geopy.geocoders import GoogleV3
from s2sphere import LatLng, Angle, Cap, RegionCoverer, math

log = logging.getLogger(__name__)

def f2i(float):
  return struct.unpack('<Q', struct.pack('<d', float))[0]

def f2h(float):
  return hex(struct.unpack('<Q', struct.pack('<d', float))[0])

def h2f(hex):
  return struct.unpack('<d', struct.pack('<Q', int(hex,16)))[0]

def to_camel_case(value):
  return ''.join(word.capitalize() if word else '_' for word in value.split('_'))

# JSON Encoder to handle bytes
class JSONByteEncoder(JSONEncoder):
    def default(self, o):
        return o.decode('utf-8')

def get_pos_by_name(location_name):
    prog = re.compile("^(\-?\d+\.\d+)?,\s*(\-?\d+\.\d+?)$")
    res = prog.match(location_name)
    latitude, longitude, altitude = None, None, None
    if res:
        latitude, longitude, altitude = float(res.group(1)), float(res.group(2)), 0
    else:
        geolocator = GoogleV3()
        loc = geolocator.geocode(location_name, timeout=10)
        if loc:
            log.info("Location for '%s' found: %s", location_name, loc.address)
            log.info('Coordinates (lat/long/alt) for location: %s %s %s', loc.latitude, loc.longitude, loc.altitude)
            latitude, longitude, altitude = loc.latitude, loc.longitude, loc.altitude
        else:
            return None

    return (latitude, longitude, altitude)

EARTH_RADIUS = 6371 * 1000
def get_cell_ids(lat, long, radius=1000):
    # Max values allowed by server according to this comment:
    # https://github.com/AeonLucid/POGOProtos/issues/83#issuecomment-235612285
    if radius > 1500:
        radius = 1500  # radius = 1500 is max allowed by the server
    region = Cap.from_axis_angle(LatLng.from_degrees(lat, long).to_point(), Angle.from_degrees(360*radius/(2*math.pi*EARTH_RADIUS)))
    coverer = RegionCoverer()
    coverer.min_level = 15
    coverer.max_level = 15
    cells = coverer.get_covering(region)
    cells = cells[:100]  # len(cells) = 100 is max allowed by the server
    return sorted([x.id() for x in cells])

def get_time_ms():
    return int(round(time.time() * 1000))

def get_format_time_diff(low, high, ms = True):
    diff = (high - low)
    if ms:
        m, s = divmod(diff / 1000, 60)
    else:
        m, s = divmod(diff, 60)
    h, m = divmod(m, 60)
    
    return (h, m, s)
