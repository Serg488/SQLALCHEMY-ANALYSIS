# Import the dependencies.
import numpy as np
from datetime import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurements = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the SQL-Alchemy APP API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of Precipitation Data for the last 12 months"""
    # Query the last 12 months of Precipitation
    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= "2016-08-24").all()

    session.close()

    # Convert the list to Dictionary
    return convert_to_dict(results)

# Convert the list to Dictionary with date as key and prcp as value
def convert_to_dict(results):
    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp  # Use date as key and prcp as value
    
    return jsonify(prcp_dict)



@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Stations"""
    # Query all Stations
    results = session.query(Station.station).order_by(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all TOBs"""
    # Query all tobs

    results = session.query(Measurements.date,  Measurements.tobs,Measurements.prcp).filter(Measurements.date >= '2016-08-23').filter(Measurements.station=='USC00519281').order_by(Measurements.date).all()

    session.close()

    # Convert the list to Dictionary
    all_tobs = []
    for prcp, date,tobs in results:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg and max tobs for a start date"""
    # Query all tobs

    results = session.query(func.min(Measurements.tobs).label('TMIN'), func.max(Measurements.tobs).label('TMAX'), func.avg(Measurements.tobs.label('TAVG'))).filter(Measurements.date >= start_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of start_date_tobs
    start_date_tobs = []
    for min, avg, max in results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min_temp"] = min
        start_date_tobs_dict["avg_temp"] = avg
        start_date_tobs_dict["max_temp"] = max
        start_date_tobs.append(start_date_tobs_dict) 
    return jsonify(start_date_tobs)


@app.route("/api/v1.0/<start_date>/<end_date>")
def Start_end_date(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg and max tobs for start and end dates"""
    # Query to get min, max, and avg temperatures
    results = session.query(
        func.min(Measurements.tobs), 
        func.max(Measurements.tobs),
        func.avg(Measurements.tobs)
    ).filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()

    session.close()

    # Create a dictionary from the row data
    start_end_tobs = []
    for min_temp, avg_temp, max_temp in results:
        start_end_tobs_dict = {
            "min_temp": min_temp,
            "avg_temp": avg_temp,
            "max_temp": max_temp
        }
        start_end_tobs.append(start_end_tobs_dict) 

    return jsonify(start_end_tobs)

# Run the Flask application in debug mode if code is correct
if __name__ == '__main__':
    app.run(debug=True)