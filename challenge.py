#!/usr/bin/python

from flask import Flask
from flask import request
import coords

#############################################################
# Local helper functions
#############################################################

def read_csv_as_json(pth, desired_fields):
    f = open(pth)
    allrows = f.read().rstrip().split('\n')
    f.close()
    headings = allrows[0].split(',')
    res = []
    for row in allrows[1:]:
        cols = row.split(',')
        row_json = dict()
        for i in range(len(headings)):
            if headings[i] in desired_fields:
                row_json[headings[i]] = cols[i]
        res.append(row_json)
    return res

def search_data(data, lat, lng, radius):
    return None

#############################################################
# Flask interface
#############################################################

app = Flask(__name__)

# read data from a csv, storing as a json
desired_fields = ['locationid', 'Applicant', 'FacilityType', 'LocationDescription', 'Address', 'Status', 'Latitude', 'Longitude']
data = read_csv_as_json('./data.csv', desired_fields)

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
