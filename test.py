#!/usr/bin/python

import unittest, copy, requests, json

endpoint = 'http://localhost:5000/api/v1/foodtrucks'

# A set of default params which should return a large list
def_param = { 'start_lat': 36.6,
              'end_lat'  : 37.8,
              'start_lng': -122.6,
              'end_lng'  : -122.2,
              'perpage'  : 5000,
              'page'     : 0
            }

def make_call(myparams):
    response = requests.get(endpoint, params=myparams)
    return response

#######################################################
# Some simple sanity checks on a plain successfull call
#######################################################
class BasicTests(unittest.TestCase):
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
    def expectError(self, p, ecode):
        r = make_call(p)
        code = r.status_code
        self.assertEqual(code, ecode)

    def testMissingLat(self):
        p = copy.deepcopy(def_param)
        del p['start_lat']
        self.expectError(p, 400)

    def testMalformedLat(self):
        p = copy.deepcopy(def_param)
        p['start_lat'] = 'potatoe'
        self.expectError(p, 400)

    def testMalformedSort(self):
        p = copy.deepcopy(def_param)
        p['sort'] = 'potatoe'
        self.expectError(p, 400)

#######################################################
# Test the sorting functionality
#######################################################
class SortTests(unittest.TestCase):
    def get_results(sefl, p):
        r = make_call(p)

        # check the json data
        js = json.loads(r.text)
        return js["results"]

    def testLocationId(self):
        p = copy.deepcopy(def_param)
        p["sort"] = "locationid"
        res = self.get_results(p)

        lastid = -1
        # using strictly greater also checks for duplicate locationids
        for r in res:
            thisid = r["locationid"]
            self.assertGreater(thisid, lastid)
            lastid = thisid

    def testLocationId(self):
        p = copy.deepcopy(def_param)
        p["sort"] = "alphabetic"
        res = self.get_results(p)

        lastname = ""
        for r in res:
            thisname = r["Applicant"]
            self.assertGreaterEqual(thisname, lastname)
            lastname = thisname

#######################################################
# Test the pagination functionality
#######################################################
class PaginateTests(unittest.TestCase):
    def get_num_returned(self, p):
        r = make_call(p)

        # check the json data
        js = json.loads(r.text)
        numf = js["num_found"]
        numr = js["num_returned"]
        res = js["results"]
        self.assertEqual(numr, len(res))
        return numr

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
            p['page'] = page
            page += 1
            num = self.get_num_returned(p)
            self.assertLessEqual(num, 10)
            if num < 10:
                break

        # now, on the next page, there should be nothing
        p['page'] = page
        num = self.get_num_returned(p)
        self.assertEqual(num, 0)

if __name__ == '__main__':
    unittest.main()
