Project
==============
SF Food Trucks - Backend

Hosted Locations
==============
* Docs     : http://sfflux.com/foodtrucks/documentation.html
* Code     : https://github.com/sr228822/foodtrucks
* API      : https://ec2.sfflux.com/api/v1/foodtrucks
* FrontEnd : http://sfflux.com/foodtrucks/map.html
* Tests    : https://github.com/sr228822/foodtrucks/blob/master/test_backend.py
* Resume   : http://www.sfflux.com/misc/sam_russell_resume_june_2014.pdf

Reasoning, Trade-offs, Assumptions
==============
I had quite a bit of difficulty with this challenge.  As indicated by my resume and on our call, prior to this I had very little experience working with a web stack.  The challenge clearly relies on a level of experience with both the technical and design aspects of a web-stack.  As such I found myself spending a large percentage of time learning the technical aspects, and worrying about the design aspects.  I've outlined a few key points in depth below, but in general I would hope that you evaluate my work with the consideration that, although I have a strong background in programming and I am a quick learner, much of this was new to me.

## Scope
The biggest design point I was unsure of was scope.  The project description is extremely vague (so much so that it must be intentional).  I did my best to try and create an API with a scope broad enough to showcase my talent, but within the time I had to work on this challenge.

## Data-set Size
The food truck data-set is very small.  This allows us to read the entire data-set into memory, and lazily duplicate it for the sake of code simplicity.  Were this a larger data set this would not be acceptible, and we would need an implementation which stored the full data-set on disk, read it in in portions, and filtered without duplication.  A simple way to do this would be to bin the data-set by locations and read in only the bin you need for this query.

## Data-set refresh
The food truck data-set does not change very often, perhaps 3-5 modifications per-week.  As such it would be inefficient to re-read the data-set for every incoming request.  However it is not completely static, so we must periodically refresh it.  I configured my flask backend to refresh the data-set from the sfgov.org webiste once per day, and use this "cached" data to answer queries.

Resources Used
==============
## Backend
    Flask for web framework
    Used one function from http://flask.pocoo.org/snippets/56 for header decoration (marked inline)

## Frontend
    Google Maps API v3
    Used code example from several Google Maps API
        https://developers.google.com/maps/documentation/javascript/examples/infowindow-simple
        https://developers.google.com/maps/documentation/javascript/examples/places-searchbox

## Documentation
    I took a lot of html/css from the uber api to format my documentation

