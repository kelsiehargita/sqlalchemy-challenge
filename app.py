# import dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from flask import Flask, jsonify
import numpy as np

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

date_filter = Measurement.date >= '2016-08-23'
station_filter = Measurement.station == 'USC00519281'

# flask setup
app = Flask(__name__)


# home page
# list all routes that are available
@app.route("/")
def home():
    return (
        f"Climate API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def prcp():

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).filter(date_filter).order_by(Measurement.date).all()

    session.close()

    precipitation_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_data.append(prcp_dict)

    return jsonify(precipitation_data)

# return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query((Measurement.station), func.count(Measurement.station).label('station_count')).\
        group_by(Measurement.station).\
        order_by(desc('station_count')).all()

    session.close()

    station_data = []
    for station, station_count in results:
        station_dict = {}
        station_dict["station_id"] = station
        station_dict["station_observation_count"] = station_count
        station_data.append(station_dict)

    return jsonify(station_data)

# query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(station_filter).filter(date_filter).all()

    session.close()

    tobs_dict = {}
    tobs_dict["minimum_temp"] = results[0][0]
    tobs_dict["maximum_temp"] = results[0][1]
    tobs_dict["average_temp"] = results[0][2]

    return jsonify(tobs_dict)

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def date_start(start):
    start_date = start

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    start_dict = {}
    start_dict["_start_date"] = start_date
    start_dict["minimum_temp"] = results[0][0]
    start_dict["average_temp"] = results[0][1]
    start_dict["maximum_temp"] = results[0][2]
    
    return jsonify(start_dict)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start,end):

    start_date = start
    end_date = end

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    start_end_dict = {}
    start_end_dict["end_date"] = end_date
    start_end_dict["start_date"] = start_date
    start_end_dict["minimum_temp"] = results[0][0]
    start_end_dict["average_temp"] = results[0][1]
    start_end_dict["maximum_temp"] = results[0][2]
    
    return jsonify(start_end_dict)

if __name__ == "__main__":
    app.run(debug=True)