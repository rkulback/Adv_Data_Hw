import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///test.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#create name
app = Flask(__name__)

#define routes - first route lists all other routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/passengers"
        f"/api/v1.0/tobs"
        f"/api/v1.0/start"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    #write a query to find one year prior to the last_date
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    last_year_data = (session.query(Measurement.date, Measurement.prcp)
                  .filter(Measurement.date > str(query_date))
                  .order_by(Measurement.date).all())

    measurement_date = []
    measurement_prcp = []


    for row in last_year_data:
        measurement_date.append(row[0])
        measurement_prcp.append(row[1])
    
    combined_data = list(zip(measurement_date, measurement_prcp))

    prcp_dict = {i:x for i,x in combined_data}

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    
    station_names = session.query(Station.name).all()

    name_list = []

    for station in station_names:
        name_list.append(station)

    return jsonify(name_list)

@app.route("/api/v1.0/tobs")
def tobs():

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    tobs_data = (session.query(Measurement.date, Measurement.tobs)
                  .filter(Station.station == Measurement.station)
                .filter(Measurement.date > str(query_date))
                .all())

    tobs_list = []

    for row in tobs_data:
        tobs_list.append(row[0])
        tobs_list.append(row[1])
    
    return jsonify(tobs_list)

# unable to get this part to run like the assignment wants. i had values per the assignment on the 
# first part, but can't figure out how to get user input to influence the search just yet
# I ran out of time to look into how to use input to run a search
# will keep trying and resubmit if possible!

@app.route("/api/v1.0/start")
def temp_page():

    station_leader = station_count = (session.query(Station.name,
                               Measurement.station,
                              func.count(Measurement.tobs))
                .filter(Station.station == Measurement.station)
                .group_by(Station.name)
                .order_by(func.count(Measurement.tobs).desc())
                .first())

    highest_temp = (session.query(Station.name,
                              func.max(Measurement.tobs),
                             Measurement.date)
                .filter(Station.station == Measurement.station)
                .filter(Measurement.station == str(station_leader[1]))
                .all())

    lowest_temp = (session.query(Station.name,
                              func.min(Measurement.tobs),
                             Measurement.date)
                .filter(Station.station == Measurement.station)
                .filter(Measurement.station == str(station_leader[1]))
                .all())

    average_temp = (session.query(Station.name,
                              func.avg(Measurement.tobs),
                             Measurement.date)
                .filter(Station.station == Measurement.station)
                .filter(Measurement.station == str(station_leader[1]))
                .all())



    return (
    f"The highest recorded temp from {highest_temp[0][0]} station was {highest_temp[0][1]} degrees on {highest_temp[0][2]}."
    f"The lowest recorded temp from {lowest_temp[0][0]} station was {lowest_temp[0][1]} degrees on {lowest_temp[0][2]}."
    f"The average recorded temp for the {lowest_temp[0][0]} station was {average_temp[0][1]} degrees."
    )

if __name__ == "__main__":
    app.run(debug=True)