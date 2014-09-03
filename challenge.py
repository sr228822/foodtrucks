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

        return 'yay it worked'

if __name__ == '__main__':


    app.run(debug = True)
