#!/usr/bin/python

import sys, csv, json
from flask import Flask, request

#############################################################
# Local helper functions
#############################################################

def autoparse(v):
    try:
        vi = int(v)
        return vi
    except:
        pass
    try:
        vf = float(v)
        return vf
    except:
        pass
    return v

def read_csv_as_json(pth):
    res = []
    with open(pth, 'rU') as f:
        reader = csv.reader(f)
        col_lab = reader.next()
        for row in reader:
            row_json = dict()
            for i in range(len(col_lab)):
                row_json[col_lab[i]] = autoparse(row[i])
            res.append(row_json)
    return res

def get_latlng(d):
    return (float(d['Latitude']), float(d['Longitude']))

def search_data(data, start_lat, start_lng, end_lat, end_lng):
    return [d for d in data if (start_lat < d['Latitude'] < end_lat) and (start_lng < d['Longitude'] < end_lng)]

#############################################################
# Flask interface
#############################################################

app = Flask(__name__)

# read data from a csv, storing as a json
data = read_csv_as_json('./data.csv')

# filter out results without a lat or lng
data = [d for d in data if type(d['Latitude']) == float and type(d['Longitude']) == float]

@app.route('/api/v1/foodtrucks')
def tasks():
        args = request.args
        # Args    TAG        Req    Type   Default
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

        # check the type of mandatory-ness of our args
        pargs = dict()
        for tag, req, etype, defv in eargs:
            # store a default value if present
            if (defv != None):
                pargs[tag] = defv
            # If arg was passed in, check it's type
            if tag in args:
                try:
                    val = etype(args[tag])
                    pargs[tag] = val
                except:
                    return 'Argument ' + tag + ' malformed', 400
            elif req:
                # if arg was missing but required, error
                return 'Missing required arg ' + tag, 400

        # Search our data based on location arguments
        fdata = search_data(data, pargs['start_lat'], pargs['start_lng'],
                                  pargs['end_lat'], pargs['end_lng'])

        # Filer data based on what filters we got
        if 'type' in pargs:
            fdata = [d for d in fdata if d['FacilityType'] == pargs['type']]

        if 'status' in pargs:
            fdata = [d for d in fdata if d['Status'] == pargs['status']]

        if 'food' in pargs:
            fdata = [d for d in fdata if pargs['food'].lower() in d['FoodItems']]

        # Sort.  We have stored a default sort so this should be fine
        if pargs['sort'] == 'locationid':
            fdata = sorted(fdata, key=lambda d: d['locationid'])
        elif pargs['sort'] == 'alphabetic':
            fdata = sorted(fdata, key=lambda d: d['Applicant'])
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


    app.run(debug = True)
