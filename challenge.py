#!/usr/bin/python

import sys, csv
from pprint import pprint
from flask import Flask
from flask import request
import coords

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

@app.route('/api/v1/test')
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
                 ('perpage',   False, int,   50)]

        # check the type of mandatory-ness of our args
        pargs = dict()
        for tag, req, etype, defv in eargs:
            # store a default value if present
            if defv:
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
        sdata = search_data(data, pargs['start_lat'], pargs['start_lng'], pargs['end_lat'], pargs['end_lng'])

        return 'yay it worked, got ' + str(len(sdata))

if __name__ == '__main__':


    app.run(debug = True)
