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

def search_data(data, tgt_lat, tgt_lng, radius):
    for d in data:
        try:
            print coords.dist((tgt_lat, tgt_lng), get_latlng(d))
        except:
            print 'failed on ' + str(d)
            sys.exit(1)
    #return [d for d in data if coords.dist((tgt_lat, tgt_lng), get_latlng(d)) < radius]
    return None

#############################################################
# Flask interface
#############################################################

app = Flask(__name__)

# read data from a csv, storing as a json
data = read_csv_as_json('./data.csv')

# filter out results without a lat or lng
data = [d for d in data if len(d['Latitude']) > 0 and len(d['Longitude']) > 0]

@app.route('/api/v1/test')
def tasks():
        args = request.args
        eargs = [('lat',    True,  float),
                 ('lng',    True,  float),
                 ('radius', True,  float),
                 ('type',   False, str),
                 ('status', False, str),
                 ('food',   False, str)]

        # check the type of mandatory-ness of our args
        pargs = dict()
        for tag, mandatory, etype in eargs:
            if tag in args:
                try:
                    val = etype(args[tag])
                    pargs[tag] = val
                except:
                    return 'Argument ' + tag + ' malformed', 400
            elif mandatory:
                return 'Missing required arg ' + tag, 400

        # Search our data based on location arguments
        sdata = search_data(data, pargs['lat'], pargs['lng'], pargs['radius'])

        return 'yay it worked'

if __name__ == '__main__':


    app.run(debug = True)
