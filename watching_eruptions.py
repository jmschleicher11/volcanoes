"""
Plotting volcanoes erupting through the years
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import ast

from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('../Data/')


def eruption_years(df):
    lens = [len(item) if type(item) == list else 1 for item in 
            df['eruption_years']]
    years = [[item] if type(item) != list else item for item in 
             df['eruption_years']]
    return pd.DataFrame( {"id" : np.repeat(df['id'].values,lens), 
                          "year" : np.concatenate(years)})
    

volcanoes = pd.read_csv('../Data/all_volcano_data.csv')
eruptions = pd.read_csv('../Data/all_eruption_data.csv')

eruptions = eruptions.dropna(subset=['eruption_years']).reset_index()
volcanoes = volcanoes[volcanoes['time_period'] == 'H'].reset_index()

eruptions['eruption_years'] = \
    [ast.literal_eval(item) for item in eruptions['eruption_years']]
    
years = eruption_years(eruptions)

volcano_eruptions = volcanoes.merge(years, on='id', how='left')


## Plotting the eruptions
year_0 = 2000

fig=plt.figure(figsize=[6, 6])


my_map = Basemap(llcrnrlon=-180.,llcrnrlat=-80.,\
    urcrnrlon=180.,urcrnrlat=85.,\
    rsphere=(6378137.00,6356752.3142),\
    resolution='l',\
    projection='merc',\
    lat_0=40.,lon_0=-20.,lat_ts=20.)

my_map.drawcoastlines(linewidth=0.5)
my_map.fillcontinents(color='0.9')
x, y = my_map(np.array(volcano_eruptions['longitude']), 
              np.array(volcano_eruptions['latitude']))
ax = plt.plot(x, y, markersize=5, marker='.', linestyle='')

erupting = volcano_eruptions[volcano_eruptions['year'] == year_0]
long = np.array(erupting['longitude'])
lat = np.array(erupting['latitude'])
points = my_map.plot(long, lat, markersize=8, marker='^', linestyle='', 
                     color='r')[0]

def init():
    points.set_data([], [])
    return points,

def erupting(year):
    
    plt.title(year)
    erupting = volcano_eruptions[volcano_eruptions['year'] == year]
    long = np.array(erupting['longitude'])
    lat = np.array(erupting['latitude'])
    
    x, y = my_map(long, lat)
    points.set_data(x, y)
    return points,

ani = animation.FuncAnimation(plt.gcf(), erupting, init_func=init,
                              frames=np.arange(year_0, 2020), blit=False, 
                              repeat=False)

plt.show()
