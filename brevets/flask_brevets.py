"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import os
import logging
import requests
import json
from datetime import datetime

###
# Globals
###
app = flask.Flask(__name__)
API_PORT = os.environ["API_PORT"]
API_ADDR = os.environ["API_ADDR"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    brevet_dist_km = request.args.get('brevet_dist_km', 200, type=int)
    begin_date = request.args.get('begin_date', '2021-01-01T00:00', type=str)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    # FIXME!
    # Right now, only the current time is passed as the start time
    # and control distance is fixed to 200
    # You should get these from the webpage!
    
    open_time = acp_times.open_time(km, brevet_dist_km, arrow.get(begin_date)).format('YYYY-MM-DDTHH:mm')
    app.logger.debug("DID IT HAPPEN???")
    close_time = acp_times.close_time(km, brevet_dist_km, arrow.get(begin_date)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/_store_data", methods = ["POST"])
def _store_data():
    app.logger.debug("We make it here")
    """
    Stores brevet data into a mongodb
    """
    #length = request.args.get('brevet_dist_km', 200, type=int)
    #start_date = request.args.get('begin_date',type=str)
    #controls = request.args.get('controls', [], type=list)
    input_json = request.get_json()
    length = input_json["brevet_dist_km"]
    start_date = input_json["begin_date"]
    checkpoints = input_json["checkpoints"]

    app.logger.debug("we make it here 2")
    _id = requests.post(API_URL + "brevets", json = {"length": length,"start_time": start_date, "checkpoints": checkpoints}).json()
    app.logger.debug(f"Here is data: {_id}")
    return _id
    

@app.route("/_get_data")
def _get_data():
    """
    Retrieves data from a mongodb
    """
    all_data = requests.get(API_URL + "brevets").json()
    data_end = all_data[-1]
    
    return flask.jsonify(result={"length": data_end["length"], "start_time": data_end["start_time"], "checkpoints": data_end["checkpoints"]})

#############

app.debug = os.environ["DEBUG"]
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(os.environ["PORT"]))
    app.run(port=os.environ["PORT"], host="0.0.0.0")
