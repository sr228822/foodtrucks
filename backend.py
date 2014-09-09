#!/usr/bin/python

import sys, csv, json, copy
from flask import Flask, request, make_response, current_app
from datetime import timedelta
from functools import update_wrapper

#############################################################
# Local helper functions
#############################################################

def read_fresh_data():
    f = open('./data.json')
    dat = json.loads(f.read())
    f.close()
    seen = []
    res = []
    for chunk in dat:
        processed = dict()

        # Throw out duplicated object-id's
        lid = chunk['objectid']
        if lid in seen:
            continue
        seen.append(lid)
        processed['locationid'] = lid

        # To be a valid entry, we need a valid lat/lng
        try:
            processed['latitude'] = float(chunk['latitude'])
            processed['longitude'] = float(chunk['longitude'])
        except:
            continue

        # Copy the remaining fields we care about
        for key in ['applicant', 'address', 'facilitytype', 'status', 'locationdescription', 'fooditems']:
            if key in chunk:
                processed[key] = chunk[key]

        res.append(processed)

    return res

# Helper to allow Cross-domain access
#  Code taken from http://flask.pocoo.org/snippets/56/ , not written
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

#############################################################
# Flask interface
#############################################################

app = Flask(__name__)

# on launch, pull fresh data from sfgov.org
CONST_ORIG_DATA = read_fresh_data()

# since we can't declare data as const, lets access it through
#  an explicit deepcopy.  Expensive but safe
def alldata():
    return copy.deepcopy(CONST_ORIG_DATA)

@app.route('/')
def hello_world():
    return 'Hello Flask World!'

@app.route('/api/v1/foodtrucks')
@crossdomain(origin='*')
def tasks():
        args = request.args
        #          TAG         Req    Type   Default
        eargs = [('start_lat', True,  float, None),
                 ('start_lng', True,  float, None),
                 ('end_lat',   True,  float, None),
                 ('end_lng',   True,  float, None),
                 ('type',      False, str,   None),
                 ('status',    False, str,   None),
                 ('food',      False, str,   None),
                 ('page',      False, int,   0),
                 ('perpage',   False, int,   50),
                 ('sort',      False, str,   'locationid')]

        # Process our raw arguments (args) into process arguments (pargs) using our
        #  table of expectations (eargs).
        #  This will handle errors for missing-required-args, or malformed args
        #  By the end of this block we have a trustworth pargs dict we can query
        pargs = dict()
        for tag, req, etype, defv in eargs:
            # store a default value if present
            if (defv != None):
                pargs[tag] = defv
            # If arg was passed in, check it's type by attempted casting
            if tag in args:
                try:
                    val = etype(args[tag])
                    # if our cast succeeded, store our processed argument
                    pargs[tag] = val
                except:
                    # cast failed is a malformed argument
                    return 'Argument ' + tag + ' malformed', 400
            elif req:
                # if arg was missing but required, error
                return 'Missing required arg ' + tag, 400

        # Request a full copy of the data
        fdata = alldata()

        # Search our data based on location arguments
        fdata = [d for d in fdata if (pargs['start_lat'] < d['latitude'] < pargs['end_lat']) and (pargs['start_lng'] < d['longitude'] < pargs['end_lng'])]

        # Filer data based on what filters we got
        if 'type' in pargs:
            fdata = [d for d in fdata if d['facilitytype'] == pargs['type']]

        if 'status' in pargs:
            fdata = [d for d in fdata if d['status'] == pargs['status']]

        if 'food' in pargs:
            fdata = [d for d in fdata if 'fooditems' in d and pargs['food'].lower() in d['fooditems'].lower()]

        # Sort.  We have stored a default sort so this should be fine
        if pargs['sort'] == 'locationid':
            fdata = sorted(fdata, key=lambda d: d['locationid'])
        elif pargs['sort'] == 'alphabetic':
            fdata = sorted(fdata, key=lambda d: d['applicant'])
        else:
            return 'Unrecognized sort option ' + pargs['sort'], 400

        # Paginate, again we have default pagination
        pagestart = pargs['page'] * pargs['perpage']
        pageend = pagestart + pargs['perpage']

        rdata = fdata[pagestart:pageend]

        res = dict()
        res['num_found'] = len(fdata)
        res['num_returned'] = len(rdata)
        res['results'] = rdata

        #return json.dumps(res)
        return json.dumps(res)

if __name__ == '__main__':
    app.run(debug = False)
