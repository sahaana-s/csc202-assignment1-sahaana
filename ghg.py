import sys
import unittest
import math
from typing import *
from dataclasses import dataclass
sys.setrecursionlimit(10**6)

calpoly_email_addresses = ["ssridh20@calpoly.edu"]

@dataclass(frozen=True)
class GlobeRect:
    lo_lat: float          
    hi_lat: float          
    west_long: float       
    east_long: float       
    # NOTE: per spec, we don't enforce "lo_lat < hi_lat" here;
    # tests/functions may raise ValueError on zero area where relevant.

@dataclass(frozen=True)
class Region:
    rect: GlobeRect
    name: str
    terrain: Literal["ocean", "mountains", "forest", "other"]

@dataclass(frozen=True)
class RegionCondition:
    region: Region
    year: int
    pop: int                
    ghg_rate: float    

EARTH_RADIUS_KM = 6371.0     

def emissions_per_capita(rc: RegionCondition) -> float:
    if rc.pop == 0:
        raise ValueError("Population is zero - emissions per capita undefined")
    return rc.ghg_rate / rc.pop

def area(gr: GlobeRect) -> float:
    y1 = math.radians(gr.lo_lat)
    y2 = math.radians(gr.hi_lat)
    d = math.radians((gr.east_long - gr.west_long) % 360.0)  # 0..2π, equal longs -> 0
    return (EARTH_RADIUS_KM ** 2) * abs(math.sin(y2) - math.sin(y1)) * d

def emissions_per_square_km(rc: RegionCondition) -> float:
    a = area(rc.region.rect)
    if a == 0:
        raise ValueError("Area is zero - emissions per square km undefined")
    return rc.ghg_rate / a


def densest(rcs: List[RegionCondition]) -> str:
    if not rcs:
        raise ValueError("Empty list - no regions to compare.")
    # density = people / km^2
    best_name = None
    best_density = -1.0
    for rc in rcs:
        a = area(rc.region.rect)
        # If area is zero, skip (or treat as infinitely dense)
        if a == 0:
            continue
        density = rc.pop / a
        if density > best_density:
            best_density = density
            best_name = rc.region.name
    if best_name is None:
        raise ValueError("All regions had zero area.")
    return best_name

TERRAIN_GROWTH: Dict[str, float] = {
    "ocean": 0.0001,
    "mountains": 0.0005,
    "forest": -0.00001,
    "other": 0.00003,
}

def growth_factor(terrain: str, years: int) -> float:
    r = TERRAIN_GROWTH[terrain]
    # compound annually
    return (1.0 + r) ** years

def project_condition(rc: RegionCondition, n: int) -> RegionCondition:
    if n == 0:
        return rc

    factor = growth_factor(rc.region.terrain, n)
    new_pop_float = rc.pop * factor
    new_pop = max(0, int(round(new_pop_float)))
    new_ghg = rc.ghg_rate * factor

    return RegionCondition(
        region = rc.region,
        year = rc.year + n,
        pop = new_pop,
        ghg_rate = new_ghg
    )


## EXAMPLES ##

# 1) major metro A (New York City-ish)
nyc_rect = GlobeRect(
    lo_lat=40.4, hi_lat=41.2,    # ~ NYC metro band
    west_long=-74.5, east_long=-73.5
)
nyc_region = Region(rect=nyc_rect, name="New York City Metro", terrain="other")
nyc_condition = RegionCondition(region=nyc_region, year=2020, pop=19_000_000, ghg_rate=170_000_000.0)

# 2) major metro B (Tokyo)
tokyo_rect = GlobeRect(
    lo_lat=35.4, hi_lat=36.2,
    west_long=139.2, east_long=140.2
)
tokyo_region = Region(rect=tokyo_rect, name="Tokyo Metro", terrain="other")
tokyo_condition = RegionCondition(region=tokyo_region, year=2020, pop=37_000_000, ghg_rate=250_000_000.0)

# 3) substantial fraction of an ocean (Pacific slice; crosses the antimeridian)
pacific_slice_rect = GlobeRect(
    lo_lat=-10.0, hi_lat=10.0,    # equatorial band
    west_long=170.0, east_long=-170.0  # 20° span eastward across the 180° meridian
)
pacific_region = Region(rect=pacific_slice_rect, name="Pacific Equatorial Slice", terrain="ocean")
pacific_condition = RegionCondition(region=pacific_region, year=2020, pop=50_000, ghg_rate=2_000_000.0)

# 4) includes Cal Poly SLO, excludes San Jose, Santa Barbara, Bakersfield, and too much ocean
# Cal Poly ~ 35.3N, -120.7E (west)
slo_rect = GlobeRect(
    lo_lat=35.0, hi_lat=35.6,
    west_long=-121.0, east_long=-120.3  # slight coastal slice; some ocean but "not too much"
)
slo_region = Region(rect=slo_rect, name="San Luis Obispo Area (incl. Cal Poly)", terrain="other")
slo_condition = RegionCondition(region=slo_region, year=2020, pop=280_000, ghg_rate=1_800_000.0)

# required list in this order:
example_region_conditions: List[RegionCondition] = [
    nyc_condition,
    tokyo_condition,
    pacific_condition,
    slo_condition,
]

# put all test cases in the "Tests" class.
class Tests(unittest.TestCase):
    def test_example_1(self):
        self.assertEqual(14,14)

    def test_emissions_per_capita_float(self):
        epc = emissions_per_capita(nyc_condition)
        # expected ~ 170e6 / 19e6 ≈ 8.947...
        self.assertAlmostEqual(epc, 170_000_000.0 / 19_000_000.0, delta=1e-9)

    def test_area_basic_equatorial_band(self):
        # pacific_slice_rect is lo=-10, hi=10, west=170, east=-170 (20° span)
        rect = pacific_slice_rect
        y1 = math.radians(rect.lo_lat)
        y2 = math.radians(rect.hi_lat)
        d = math.radians((rect.east_long - rect.west_long) % 360.0)  # 20° in radians
        expected = (EARTH_RADIUS_KM ** 2) * abs(math.sin(y2) - math.sin(y1)) * d
        self.assertAlmostEqual(area(rect), expected, delta=1e-6)

    def test_area_zero_when_same_longitude(self):
        rect = GlobeRect(lo_lat=0.0, hi_lat=10.0, west_long=50.0, east_long=50.0)
        self.assertEqual(area(rect), 0.0)

    def test_emissions_per_square_km_raises_on_zero_area(self):
        zero_rect = GlobeRect(lo_lat=10.0, hi_lat=10.0, west_long=0.0, east_long=10.0)
        rc = RegionCondition(region=Region(zero_rect, "ZeroLat", "other"), year=2020, pop=1_000, ghg_rate=10_000.0)
        with self.assertRaises(ValueError):
            emissions_per_square_km(rc)

    def test_densest_from_examples(self):
        # not asserting which one in case rectangles are tweaked later;
        # just ensure it returns one of the names and doesn't crash
        name = densest(example_region_conditions)
        self.assertIn(name, [rc.region.name for rc in example_region_conditions])

    def test_projection_growth_other(self):
        # terrain "other" growth 0.003% annually => factor = (1 + 0.00003)^years
        years = 50
        rc0 = slo_condition
        factor = (1.0 + 0.00003) ** years
        projected = project_condition(rc0, years)
        self.assertEqual(projected.year, rc0.year + years)
        # population rounded to nearest int
        self.assertEqual(projected.pop, int(round(rc0.pop * factor)))
        # ghg scales proportionally with same factor (float compare with delta)
        self.assertAlmostEqual(projected.ghg_rate, rc0.ghg_rate * factor, delta=1e-7)

    def test_projection_ocean_tiny_growth(self):
        years = 200
        rc0 = pacific_condition
        factor = (1.0 + 0.0001) ** years
        projected = project_condition(rc0, years)
        self.assertEqual(projected.pop, int(round(rc0.pop * factor)))
        self.assertAlmostEqual(projected.ghg_rate, rc0.ghg_rate * factor, delta=1e-7)

    def test_emissions_per_capita_raises_when_zero_pop(self):
        rc = RegionCondition(region=nyc_region, year=2020, pop=0, ghg_rate=1.0)
        with self.assertRaises(ValueError):
            emissions_per_capita(rc)

    def test_longitude_wrap_340_degrees(self):
        # west=-170 to east=170 spans 340° eastward
        rect = GlobeRect(lo_lat=0.0, hi_lat=10.0, west_long=-170.0, east_long=170.0)
        expected = (EARTH_RADIUS_KM ** 2) * (math.sin(math.radians(10.0)) - math.sin(0.0)) * math.radians(340.0)
        self.assertAlmostEqual(area(rect), expected, delta=1e-6)


if (__name__ == '__main__'):
    unittest.main()
