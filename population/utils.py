import functools
import string
import random
import time

from typing import Optional

import pyproj

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from shapely.ops import transform
from shapely.geometry import Point, Polygon


PROJ_WGS84 = pyproj.Proj('+proj=longlat +datum=WGS84')
LON_LAT_BOUNDS = Polygon.from_bounds(
    xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0
)


def generate_request_id() -> str:
    """
    Generates requestId value for the payload.
    Resulting values is: current date (should be eq to JS' Date.now()) + random str with len 8.
    Returns
    -------
    str: request id
    """
    random_str = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits + string.ascii_lowercase
        ) for _ in range(8)
    )

    current_time_str = str(int(time.time() * 1000))

    return current_time_str + random_str


def generate_pes_v3_request_payload(lat: float, lon: float, radius: float) -> Optional[dict]:
    """
    Generates request payload required to use external api "https://sedac.ciesin.columbia.edu/arcgis/rest/.

    Parameters
    ----------
    lat: longitude value
    lon: longitude value
    radius: radius value

    Returns
    -------
    dict: payload if payload was constructed successsfully, None otherwise
    """

    def _calculate_geodesic_point_buffer():
        """
        Calculates Azimuthal equidistant projection and writes resulting polygons into a list.
        """
        aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon}'

        project = functools.partial(
            pyproj.transform,
            pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
            PROJ_WGS84
        )
        buf = Point(0, 0).buffer(radius * 1000)  # distance in metres

        return transform(project, buf).exterior.coords[:]
    try:
        buffer = _calculate_geodesic_point_buffer()
        payload = map(list, buffer)
    except (ValueError, TypeError) as exc:
        # logger or smth should go here to inform about the issue
        return

    return {
        "Input_Data": {
            "polygon": payload,
            "variables": [
                "gpw-v4-population-count-rev10_2000",
                "gpw-v4-population-count-rev10_2005",
                "gpw-v4-basic-demographic-characteristics-rev10_atotpopbt-count",
                "gpw-v4-population-count-rev10_2015", "gpw-v4-population-count-rev10_2020",
                "gpw-v4-basic-demographic-characteristics-rev10_a000-014bt-count",
                "gpw-v4-basic-demographic-characteristics-rev10_a015-064bt-count",
                "gpw-v4-basic-demographic-characteristics-rev10_a065plusbt-count",
                "gpw-v4-data-quality-indicators-rev10_mean-adminunitarea",
                "gpw-v4-land-water-area-rev10_landareakm"
            ],
            "statistics": ["SUM", "MEAN"],
            "requestId": generate_request_id(),
        }
    }


@dataclass_json
@dataclass(order=True, init=True)
class CoordinatePoint:
    """Coordinate point for longitude and latitude"""

    longitude: float
    latitude: float
    units: str = "degrees"

    lon_lat_bounds = LON_LAT_BOUNDS

    def __post_init__(self):
        self.longitude %= 360
        if self.longitude >= 180:
            self.longitude -= 360

    @property
    def point(self) -> Point:
        """
        Property to return Point instance with given coordinates.
        Returns
        -------
        Point: point instance
        """
        return Point(self.longitude, self.latitude)

    def is_valid(self) -> bool:
        """
        Validate whether latitude and longitude point is valid and
         can be located in the bounds of the WGS84 CRS.
        Returns
        -------
        bool: True if valid, False otherwise
        """
        return self.lon_lat_bounds.intersects(self.point)
