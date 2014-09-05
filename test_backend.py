#!/usr/bin/python

import unittest, copy, requests, json, sys

#host='http://localhost:5000'
host='http://ec2.sfflux.com:4444'
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
class BadArguments(unittest.TestCase):

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

    # start_lat expects a float, passing an empty val should fail
    def testEmptyLat(self):
        p = copy.deepcopy(def_param)
        p['start_lat'] = ''
        self.expectError(p, 400)

    # Sort is a string, but only accepts certain values, a diff value should fail
    def testMalformedSort(self):
        p = copy.deepcopy(def_param)
        p['sort'] = 'potatoe'
        self.expectError(p, 400)

#######################################################
# Test that other types of requests fail
#######################################################
class BadRequests(unittest.TestCase):

    # Post not allowed, only get
    def testPost(self):
        response = requests.post(endpoint)
        self.assertEqual(response.status_code, 405)

    # Put not allowed, only get
    def testPut(self):
        response = requests.put(endpoint)
        self.assertEqual(response.status_code, 405)

    # Delete not allowed, only get
    def testDelete(self):
        response = requests.delete(endpoint)
        self.assertEqual(response.status_code, 405)

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

    # A pagination test.  We query a large data set with 13-item pages
    #   page=0 should return 13 results
    #   following pages should return <= 13 results
    #   after our first < 13 result, the next page should be empty
    def testPagination(self):
        p = copy.deepcopy(def_param)
        numTotal = len(get_results(p))
        runningSum = 0

        page = 0
        perpage = 13
        runningSum = 0
        p['perpage'] = perpage

        # We expect 10 results on the initial page
        p['page'] = page
        num = self.get_num_returned(p)
        self.assertEqual(num, perpage)
        runningSum += num

        # we expect a pattern of 10 pages consistently
        while True:
            page += 1
            p['page'] = page
            num = self.get_num_returned(p)
            self.assertLessEqual(num, perpage)
            runningSum += num
            if num < perpage:
                break

        # now, on the next page, there should be nothing
        page += 1
        p['page'] = page
        num = self.get_num_returned(p)
        self.assertEqual(num, 0)
        runningSum += num

        self.assertEqual(runningSum, numTotal)

#######################################################
# Test the filter functionality
#######################################################
class FilterTests(unittest.TestCase):

    # Verify that when we filter to facility type, we only get results
    # with that type back. Each subset should be less than our full set
    def testFilterType(self):
        p = copy.deepcopy(def_param)

        numTotal = len(get_results(p))
        runningSum = 0

        for t in ["Truck", "Push Cart"]:
            p['type'] = t
            res = get_results(p)
            numRes = len(res)
            runningSum += numRes
            for r in res:
                self.assertEqual(r['FacilityType'], t)
                self.assertLessEqual(numRes, numTotal)

        self.assertLessEqual(runningSum, numTotal)

    # Verify that when we filter to permit status, we only get results
    # with that type back. Each subset should be less than our full set
    def testFilterType(self):
        p = copy.deepcopy(def_param)

        numTotal = len(get_results(p))
        runningSum = 0

        for s in ["APPROVED", "POSTAPPROVED", "REQUEST", "EXPIRED", "ONHOLD"]:
            p['status'] = s
            res = get_results(p)
            numRes = len(res)
            runningSum += numRes
            for r in res:
                self.assertEqual(r['Status'], s)
                self.assertLessEqual(numRes, numTotal)

        self.assertLessEqual(runningSum, numTotal)

    # Verify that when we filter by food items, we only get results
    # whose food items include the search string
    def testFilterFood(self):
        p = copy.deepcopy(def_param)

        numTotal = len(get_results(p))

        # test we can find a common food
        p['food'] = 'Sandwich'
        res = get_results(p)
        for r in res:
            good = 'Sandwich'.lower() in r['FoodItems'].lower()
            self.assertEqual(good, 1)
        self.assertLessEqual(len(res), numTotal)

        # test that a non-existant food returns nothing
        p['food'] = 'chocolate frosted sugar bombs'
        res = get_results(p)
        self.assertEqual(len(res), 0)

#######################################################
# Simple stress test of multiple calls
#######################################################
class StressTests(unittest.TestCase):

    # TODO can I send this in parallel, or at least non-blocking?
    def testStress(self):
        p = copy.deepcopy(def_param)

        for i in range(5):
            r = make_call(p)
            code = r.status_code
            self.assertEqual(code, 200)

if __name__ == '__main__':
    unittest.main()
