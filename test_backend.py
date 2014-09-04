#!/usr/bin/python

import unittest, copy, requests, json, sys

host='http://localhost:5000'
apiroute = '/api/v1/foodtrucks'
endpoint = host + apiroute

# A set of default params which should return a large set of results
def_param = { 'start_lat': 36.6,
              'end_lat'  : 37.8,
              'start_lng': -122.6,
              'end_lng'  : -122.2,
              'perpage'  : 5000,
              'page'     : 0
            }

# A helper method to make the actual call through requests
def make_call(myparams):
    response = requests.get(endpoint, params=myparams)
    return response

# A helper method which results just the resulst dict from the call
def get_results(p):
    r = make_call(p)
    js = json.loads(r.text)
    return js["results"]

#######################################################
# Some simple sanity checks on geo filtering
#######################################################
class BasicTests(unittest.TestCase):

    # A basic call with our def params which should succeed
    def testBasicCall(self):
        # Make a simple call
        p = copy.deepcopy(def_param)
        r = make_call(p)
        assert r

        # check for a successfull error code
        code = r.status_code
        self.assertEquals(code, 200)

        # check the json data
        js = json.loads(r.text)
        assert js
        numf = js["num_found"]
        numr = js["num_returned"]
        res = js["results"]

        # since this is our default all-encompasing request, we expect everything
        self.assertGreater(numf, 0)
        self.assertGreater(numr, 0)
        self.assertEqual(numf, numr)
        self.assertEqual(numr, len(res))

    # Create a query which should succeed but return nothing due to zero-area box
    def testEmptyResults(self):
        p = copy.deepcopy(def_param)
        # this should make our box contain nothing
        p['end_lat'] = p['start_lat']

        r = make_call(p)
        assert r

        # check for a successfull error code
        code = r.status_code
        self.assertEquals(code, 200)

        # check the json data
        js = json.loads(r.text)
        assert js
        numf = js["num_found"]
        numr = js["num_returned"]
        res = js["results"]

        # since this is our default all-encompasing request, we expect everything
        self.assertEqual(numf, 0)
        self.assertEqual(numr, 0)
        self.assertEqual(len(res), 0)

#######################################################
# Check for some simple errors in the params
#######################################################
class ExpectingErrors(unittest.TestCase):

    # A helper method to assert that we received an error code
    def expectError(self, p, ecode):
        r = make_call(p)
        code = r.status_code
        self.assertEqual(code, ecode)

    # start_lat is a mandatory parameter, lacking it should fail
    def testMissingLat(self):
        p = copy.deepcopy(def_param)
        del p['start_lat']
        self.expectError(p, 400)

    # start_lat expects a float, passing a string should fail
    def testMalformedLat(self):
        p = copy.deepcopy(def_param)
        p['start_lat'] = 'potatoe'
        self.expectError(p, 400)

    # Sort is a string, but only accepts certain values, a diff value should fail
    def testMalformedSort(self):
        p = copy.deepcopy(def_param)
        p['sort'] = 'potatoe'
        self.expectError(p, 400)

#######################################################
# Test the sorting functionality
#######################################################
class SortTests(unittest.TestCase):

    # Verifying that sorting by locationid produces sequentially increasing loc ids
    def testSortLocationId(self):
        p = copy.deepcopy(def_param)
        p["sort"] = "locationid"
        res = get_results(p)

        lastid = -1
        for r in res:
            thisid = r["locationid"]
            # using strictly greater also checks for duplicate locationids
            self.assertGreater(thisid, lastid)
            lastid = thisid

    # Verify that sorting by alphabetic produces sequentially increasing applicant names
    def testSortAlphabetic(self):
        p = copy.deepcopy(def_param)
        p["sort"] = "alphabetic"
        res = get_results(p)

        lastname = ""
        for r in res:
            thisname = r["Applicant"]
            # duplicate names are okay
            self.assertGreaterEqual(thisname, lastname)
            lastname = thisname

#######################################################
# Test the pagination functionality
#######################################################
class PaginateTests(unittest.TestCase):

    # A helper method which returns the number of results found
    def get_num_returned(self, p):
        r = make_call(p)

        # check the json data
        js = json.loads(r.text)
        numf = js["num_found"]
        numr = js["num_returned"]
        res = js["results"]
        self.assertEqual(numr, len(res))
        return numr

    # A pagination test.  We query a large data set with 10-item pages
    #   page=0 should return 10 results
    #   following pages should return <= 10 results
    #   after our first < 10 result, the next page should be empty
    def testPagination(self):
        p = copy.deepcopy(def_param)
        page = 0
        p['perpage'] = 10

        # We expect 10 results on the initial page
        p['page'] = page
        num = self.get_num_returned(p)
        self.assertEqual(num, 10)

        # we expect a pattern of 10 pages consistently
        while True:
            page += 1
            p['page'] = page
            num = self.get_num_returned(p)
            self.assertLessEqual(num, 10)
            if num < 10:
                break

        # now, on the next page, there should be nothing
        page += 1
        p['page'] = page
        num = self.get_num_returned(p)
        self.assertEqual(num, 0)

#######################################################
# Test the filter functionality
#######################################################
class FilterTests(unittest.TestCase):

    # Verify that when we filter to facility type, we only get results
    # with that type back. Each subset should be less than our full set
    def testFilterType(self):
        p = copy.deepcopy(def_param)

        numTotal = len(get_results(p))

        p['type'] = 'Truck'
        res = get_results(p)
        for r in res:
            self.assertEqual(r['FacilityType'], 'Truck')
            numTrucks = len(res)

        p['type'] = 'Push Cart'
        res = get_results(p)
        for r in res:
            self.assertEqual(r['FacilityType'], 'Push Cart')
            numPush = len(res)

        self.assertLessEqual(numTrucks, numTotal)
        self.assertLessEqual(numPush, numTotal)

    # Verify that when we filter by food items, we only get results
    # whose food items include the search string
    def testFilterFood(self):
        p = copy.deepcopy(def_param)

        # test we can find a common food
        p['food'] = 'Sandwich'
        res = get_results(p)
        for r in res:
            good = 'Sandwich'.lower() in r['FoodItems'].lower()
            self.assertEqual(good, 1)

        # test that a fictional non-existant food returns nothing
        p['food'] = 'chocolate frosted sugar bombs'
        res = get_results(p)
        self.assertEqual(len(res), 0)

if __name__ == '__main__':
    unittest.main()
