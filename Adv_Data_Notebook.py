#import modules in cells 1 through 4

%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import datetime as dt

# Python and SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# Create engine to read the SQL file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# View classes that automap found
Base.classes.keys()

#identify datatypes in measurement

inspector = inspect(engine)
columns = inspector.get_columns('measurement')
for c in columns:
    print(c['name'], c['type'])

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from Python to the DB
session = Session(engine)

# Display the row's columns and data in dictionary form
first_row_measurement = session.query(Measurement).first()
first_row_measurement.__dict__

#write a script to identify the last year's worth of data; save the data to individual lists
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

#write a query to find one year prior to the last_date

query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#iterate through the data; store into lists

last_year_data = (session.query(Measurement.date, Measurement.prcp)
                  .filter(Measurement.date > str(query_date))
                  .order_by(Measurement.date).all())

measurement_date = []
measurement_prcp = []


for row in last_year_data:
    measurement_date.append(row[0])
    measurement_prcp.append(row[1])
    
combined_data = list(zip(measurement_date, measurement_prcp))

#create a pandas dataframe to store the information; clean the data

combined_data_df = pd.DataFrame(combined_data, columns=('date', 'precipitation'))

cleaned_df = combined_data_df.dropna()

indexed_df = cleaned_df.set_index('date')

indexed_df.head()

#plot the data from the dataframe
import matplotlib.dates as mdates


plt.plot(measurement_date, measurement_prcp)
plt.legend('precipitation')
plt.xlabel('Date')

plt.show()

#design a query to calculate the total number of stations
#first step is to figure out what the data looks like, and how the data is formatted

#identify datatypes in station

inspector = inspect(engine)
columns = inspector.get_columns('station')
for c in columns:
    print(c['name'], c['type'])

# Display the station row's columns and data in dictionary form
first_row_station = session.query(Station).first()
first_row_station.__dict__

#count the total number of stations

station_entries = (session.query(
                    func.count(Station.name))
                  .all())
                                
print(f"There are {station_entries[0]} stations in the Station dataset.")

#create a query to find the most active stations
#use functions such as min, max, count, and average as needed

station_count = (session.query(Station.name,
                               Measurement.station,
                              func.count(Measurement.tobs))
                .filter(Station.station == Measurement.station)
                .group_by(Station.name)
                .order_by(func.count(Measurement.tobs).desc())
                .all()
                )

station_count_df = pd.DataFrame(station_count, columns=('Name', 'Station', 'Total Observations'))

station_count_df

#use similar query to above to identify the station w/ highest observation count;
#save the results into a variable to be used below

station_leader = station_count = (session.query(Station.name,
                               Measurement.station,
                              func.count(Measurement.tobs))
                .filter(Station.station == Measurement.station)
                .group_by(Station.name)
                .order_by(func.count(Measurement.tobs).desc())
                .first())

station_leader[1]


# Display the row's columns and data in dictionary form
first_row_measurement = session.query(Measurement).first()
first_row_measurement.__dict__

#Design a query to retrieve the last 12 months of temperature observation data (tobs)
#Data must come from the station with the highest observation count

annual_data = (session.query(Measurement.tobs)
                  .filter(Station.station == Measurement.station)
                .filter(Measurement.date > str(query_date))
                .filter(Measurement.station == str(station_leader[1]))
                .all())

annual_data

#put data into list so i can plot it

list_annual_data = []

for row in annual_data:
    list_annual_data.append(row[0])
    
print(list_annual_data)

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

print(f"The highest recorded temp from {highest_temp[0][0]} station was {highest_temp[0][1]} degrees on {highest_temp[0][2]}.")
print(f"The lowest recorded temp from {lowest_temp[0][0]} station was {lowest_temp[0][1]} degrees on {lowest_temp[0][2]}.")
print(f"The average recorded temp for the {lowest_temp[0][0]} station was {average_temp[0][1]} degrees.")

#plot annual data into a histogram; set bins = 12

nbins = 12

plt.hist(list_annual_data, bins=nbins)

plt.ylabel('Frequency')
plt.legend('tobs', loc='upper left')


plt.show()
