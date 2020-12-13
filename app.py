# ## Step 2 - Climate App

# Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

from flask import Flask, jsonify
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
    

engine = create_engine("sqlite:///sqlalchemy-challenge/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
inspector = inspect(engine)
Measurement = Base.classes.measurement
m_columns = inspector.get_columns('measurement')
Station = Base.classes.station
s_columns = inspector.get_columns('station')
M = Measurement
S = Station     
# * Use Flask to create your routes.
app = Flask(__name__)
# ### Routes

# * `/`
@app.route('/')
#   * Home page.
def home_page():
    #   * List all routes that are available.
    return (
        f"Welcome to my climate analysis homepage! <br/>"
        f"Available routes inclue: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
# * `/api/v1.0/precipitation`
def precipitation():
    session = Session(engine)
    percip = session.query(M.date, M.prcp).order_by(M.date).all()
    session.close()
    return jsonify(percip)
#   * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

#   * Return the JSON representation of your dictionary.

@app.route("/api/v1.0/stations")
# * `/api/v1.0/stations`
def stations():
    session = Session(engine)
    stations = session.query(S.name).all()
    session.close()
    #   * Return a JSON list of stations from the dataset.
    return jsonify(stations)
    

@app.route("/api/v1.0/tobs")
  # * `/api/v1.0/tobs`
def tobs():
    session = Session(engine)
    last_12_months = (dt.date(2017, 8, 23) - dt.timedelta(days=365))
    sel = [Measurement.date, Measurement.prcp]
    last_12_percip = session.query(*sel).filter(Measurement.date >= last_12_months).group_by(Measurement.date).all()
    session.close()
    #   * Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(last_12_percip)
  
  
@app.route('/api/v1.0/<start>', endpoint='start')
# * `/api/v1.0/<start>` 
def start(start):
    start = '2010-11-23'
    
    session = Session(engine)
    #   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    before_start = pd.DataFrame(columns=('Date', 'Min Temp', 'Avg Temp', 'Max Temp'))
    before_start['Date'] = pd.date_range(start='2010-01-01', end=start)

    j=0
    for i in before_start['Date'].astype(str):
        data = session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) == i).all()
        before_start['Min Temp'][j] = data[0][0]
        before_start['Avg Temp'][j] = data[0][1]
        before_start['Max Temp'][j] = data[0][2]
        j+=1
    session.close()
    results = before_start.to_json(orient='index', date_format='iso')
    return jsonify(results)
    
    





# and `/api/v1.0/<start>/<end>
@app.route('/api/v1.0/<start>/<end>', endpoint='start_end')
# * `/api/v1.0/<start>` 
def start_end(start=None, end=None):
    session = Session(engine)
    #   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    before_start = pd.DataFrame(columns=('Date', 'Min Temp', 'Avg Temp', 'Max Temp'))
    before_start['Date'] = pd.date_range(start=start, end=end)

    j=0
    for i in before_start['Date'].astype(str):
        data = session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) == i).all()
        before_start['Min Temp'][j] = data[0][0]
        before_start['Avg Temp'][j] = data[0][1]
        before_start['Max Temp'][j] = data[0][2]
        j+=1
    session.close()
    results = before_start.to_json(orient='index', date_format='iso')
    return jsonify(results)









if __name__ == '__main__':
    app.run(debug=True)