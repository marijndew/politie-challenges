from bs4 import BeautifulSoup
from dateutil.parser import parse
import re
import datetime
import pandas as pd

# DEFINE FUCTION TO CALCULATE DISTANCE BETWEEN TWO SETS OF COORDINATES
from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
  # convert decimal degrees to radians 
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  # haversine formula 
  dlon = lon2 - lon1 
  dlat = lat2 - lat1 
  a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a)) 
  r = 6371 # radius of earth in kilometers.
  return c * r

# READING IN DATA OF PERSON 1
data1 = BeautifulSoup(open('GPS 1.gpx').read())
data1_list = []
count = 0
for i in data1.findAll('wpt'):
    lat = re.search('(?<=lat=").*(?=" )', str(i)).group(0)
    lon = re.search('(?<=lon=").*(?=")', str(i)).group(0)
    tim = parse(re.search('(?<=<time>).*(?=</time>)', str(i)).group(0), fuzzy=True)
    data1_list.append((lat, lon, tim))
    count += 1

# READING IN DATA OF PERSON 2
data2 = BeautifulSoup(open('GPS 2.gpx').read())
data2_list = []
count = 0
for i in data2.findAll('wpt'):
    lat = re.search('(?<=lat=").*(?=" )', str(i)).group(0)
    lon = re.search('(?<=lon=").*(?=")', str(i)).group(0)
    tim = parse(re.search('(?<=<time>).*(?=</time>)', str(i)).group(0), fuzzy=True)
    data2_list.append((lat, lon, tim))
    count += 1

# CREATING THE LIST WITH TIMESTAMPS FOR EVERY THIRTY SECONDS IN THE DATASET TIMESPAN
base = data2_list[0][2] # first datapoint in the set
last = data2_list[-1][2] # last datapoint in the set
half_minutes_elapsed = round((last-base).total_seconds() / 30) # nr of half-minutes between first and last data
date_list = [base + datetime.timedelta(minutes=0.5*x) for x in range(half_minutes_elapsed)]

# INITIALIZE PANDAS DATAFRAME
df = pd.DataFrame()
df['time'] = date_list # setting timestamps as "index"

# FILLING IN THE COORDINATES IN THE DATAFRAME 
coords_1 = []
coords_2 = []
count = 0
for i in df["time"]:

# person 1
    for j in range(len(data1_list)):
        timedelta = (i - data1_list[j][2]).total_seconds()/30
        if timedelta < 1 and timedelta > -1: # checking if datapoint time matches "index" time (<30 second margin)
            coords_1.append(data1_list[j])
            break
    if len(coords_1) < count + 1: # if no datapoint available set empty string
        coords_1.append('')

# person 2
    for j in range(len(data2_list)):
        timedelta = (i - data2_list[j][2]).total_seconds()/30
        if timedelta < 1 and timedelta > -1: # checking if datapoint time matches "index" time (<30 second margin)
            coords_2.append(data2_list[j])
            break
    if len(coords_2) < count + 1: # if no datapoint available set empty string
        coords_2.append('')

    count += 1

df["coords_1"] = coords_1
df["coords_2"] = coords_2

# CALCULATING DISTANCE BETWEEN THE TWO PERSONS WHEN BOTH HAVE DATA FOR TIME SLOT (30-second range)
distance = [haversine(float(df['coords_1'][i][0]),float(df['coords_1'][i][1]),float(df['coords_2'][i][0]),float(df['coords_2'][i][1])) if len(df["coords_1"][i]) > 1 and len(df["coords_2"][i]) > 1 else '' for i in range(df.shape[0]) ]
df["distance"] = distance

# print csv for visual overview
df.to_csv('df-30-secs.csv', index=True)

# get "distance" column for all rows in dataframe which have a value there that is NOT empty string. Then take the minimum value of that
min_distance = df.loc[df["distance"] != '',"distance"].min()
# get locations of both persons at minimum distance
closest_locations = df.loc[df["distance"] == min_distance,["coords_1", "coords_2"]]
closest_locations.iloc[0,0] # returns ('52.360530743552246', '4.87452832871918', datetime.datetime(2019, 11, 5, 15, 51, 59, tzinfo=tzutc()))
closest_locations.iloc[0,1] # returns ('52.3631370179605', '4.880431704948705', datetime.datetime(2019, 11, 5, 15, 52, 13, tzinfo=tzutc()))

# The ANSWER IS 52.3605, 4.8745 (the coordinates of person 1 at 15h51s59)