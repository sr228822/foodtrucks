#!/usr/bin/python

from flask import Flask
from flask import request

#############################################################
# Local helper functions
#############################################################

def read_csv(pth):
    f = open(pth)
    allrows = f.read().rstrip().split('\n')
    f.close()
    headings = allrows[0].split(',')
    res = []
    for row in allrows[1:]:
        cols = row.split(',')
        res.append(cols)
    return (headings, res)

#############################################################
# Flask interface
#############################################################

app = Flask(__name__)

headings, data = read_csv('./data.csv')

@app.route('/api/v1/test')
def tasks():
        args = request.args
        mandatory_args = ['lat', 'lng', 'radius']

        # Check and retrieve the mandatory args
        for a in mandatory_args:
            if a not in args:
                return 'Missing required arg ' + a, 400
        try:
            lat = float(args['lat'])
            lng = float(args['lng'])
            readius = float(args['radius'])
        except:
            return 'Required arg malformed', 400

        return 'yay it worked'

if __name__ == '__main__':


    app.run(debug = True)
