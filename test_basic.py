import unittest
from ghg import calpoly_email_addresses, GlobeRect, Region, RegionCondition, example_region_conditions, densest, project_condition, area, emissions_per_capita, emissions_per_square_km

# please note: these are not real tests! They don't include
# expected results, and they don't actually test that the
# given functions and methods *work*, they just test to make
# sure that the given methods and functions actually exist,
# and run when called with the right # and kind of arguments.

# your test cases must be better than these! Each of your tests
# should include an assertion containing an expected result.

# Also: you can edit this file, but it's probably not a good idea;
# deleting these tests, for instance, would result in "all tests
# passed" from GitHub... but then your code would fail terribly
# against the post-handin test cases. So just don't edit this file.

class MyTests(unittest.TestCase):

    def test_email_name(self):
        self.assertEqual(type(calpoly_email_addresses),list)
        self.assertGreater(len(calpoly_email_addresses),0)
        for email in calpoly_email_addresses:
            self.assertRegex(email,r'^[a-zA-Z0-9]+@calpoly\.edu$')

    def test_GlobeRectExistence(self):
        gr1 = GlobeRect(3.0,4.0,5.0,6.0)
        self.assertEqual(gr1.lo_lat, 3.0)
        self.assertEqual(gr1.hi_lat, 4.0)
        self.assertEqual(gr1.west_long, 5.0)
        self.assertEqual(gr1.east_long, 6.0)

    def test_Region_existence(self):
        gr1 = GlobeRect(3.0,4.0,5.0,6.0)
        r1 = Region(gr1, "bogo", "ocean")
        self.assertEqual(r1.rect,gr1)
        self.assertEqual(r1.name,"bogo")
        self.assertEqual(r1.terrain,"ocean")

    def test_RegionCondition_existence(self):
        gr1 = GlobeRect(3.0, 4.0, 5.0, 6.0)
        r1 = Region(gr1, "bogo", "ocean")
        rc1 = RegionCondition(r1, 2000, 1, 0.01)
        self.assertEqual(rc1.region,r1)
        self.assertEqual(rc1.year, 2000)
        self.assertEqual(rc1.pop, 1)
        self.assertEqual(rc1.ghg_rate, 0.01)

    def test_example_region_conditions(self):
        self.assertEqual(len(example_region_conditions),4)
        for rc in example_region_conditions:
            self.assertEqual(type(rc),RegionCondition)

    def test_emissions_per_capita(self):
        gr1 = GlobeRect(3.0, 4.0, 5.0, 6.0)
        r1 = Region(gr1, "bogo", "ocean")
        self.assertEqual(type(emissions_per_capita(RegionCondition(r1, 2000, 1, 0.00))),float)

    def test_area(self):
        gr1 = GlobeRect(3.0, 4.0, 5.0, 6.0)
        self.assertEqual(type(area(gr1)),float)

    def test_emissions_per_square_km(self):
        gr1 = GlobeRect(3.0, 4.0, 5.0, 6.0)
        r1 = Region(gr1, "bogo", "ocean")
        emissions_per_square_km(RegionCondition(r1, 2000, 1, 0.00))

    def test_densest(self):
        gr1 = GlobeRect(3.0, 4.0, 5.0, 6.0)
        r1 = Region(gr1, "bogo", "ocean")
        rc1 = RegionCondition(r1, 2000, 1, 0.00)
        self.assertEqual(type(densest([rc1])),str)

    def test_project_condition(self):
        gr1 = GlobeRect(3.0, 4.0, 5.0, 6.0)
        r1 = Region(gr1, "bogo", "ocean")
        rc1 = RegionCondition(r1, 2000, 1, 0.00)
        self.assertEqual(type(project_condition(rc1,0)),RegionCondition)


if (__name__ == '__main__'):
    unittest.main()
