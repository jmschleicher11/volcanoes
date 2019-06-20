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
    
## Previoualy generated data which include volcanoes with their info, and the
    ## dates of known eruptions
volcanoes = pd.read_csv('../Data/all_volcano_data.csv')
eruptions = pd.read_csv('../Data/all_eruption_data.csv')

eruptions = eruptions.dropna(subset=['eruption_years']).reset_index()
volcanoes = volcanoes[volcanoes['time_period'] == 'H'].reset_index()

eruptions['eruption_years'] = \
    [ast.literal_eval(item) for item in eruptions['eruption_years']]

## Get a dataframe of all eruption years, separate into new and ongoing
## eruptions, and merge on volcanoes dataframe
years = eruption_years(eruptions)
years['match'] = years['year'].diff().eq(1)
volcano_eruptions = volcanoes.merge(years, on='id', how='left')


## Plotting the eruptions
year_0 = 1900

fig=plt.figure(figsize=[6, 6])

## Plot basemap of world and all holocene volcanoes. This will be constant in 
## the animation
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

def eruption_locs(year, df):
    '''
    Identify locations of new vs. erupting volcanoes to plot
    '''
    new_erupting = df[(df['year'] == year) & (df['match'] == 0)]
    new_long = np.array(new_erupting['longitude'])
    new_lat = np.array(new_erupting['latitude'])
    
    ongoing_erupting = df[(df['year'] == year) & (df['match'] == 1)]
    ongoing_long = np.array(ongoing_erupting['longitude'])
    ongoing_lat = np.array(ongoing_erupting['latitude'])
    
    return (new_long, new_lat, ongoing_long, ongoing_lat)
    
new_long, new_lat, ongoing_long, ongoing_lat = \
                                    eruption_locs(year_0, volcano_eruptions)

## Plot both new eruptions (solid markers) and ongoing eruptions (open markers)
ongoing_points = my_map.plot(ongoing_long, ongoing_lat, markersize=5, 
                             marker='^', linestyle='', markerfacecolor='white',
                             markeredgecolor='red', markeredgewidth=1)[0]
new_points = my_map.plot(new_long, new_lat, markersize=6, marker='^', 
                     linestyle='', color='r')[0]

def init():
    new_points.set_data([], [])
    ongoing_points.set_data([], [])
    return new_points, ongoing_points,

def erupting(year):
    
    plt.title(year)    
    new_long, new_lat, ongoing_long, ongoing_lat = \
                                    eruption_locs(year, volcano_eruptions)
    
    new_x, new_y = my_map(new_long, new_lat)
    new_points.set_data(new_x, new_y)
    
    ongoing_x, ongoing_y = my_map(ongoing_long, ongoing_lat)
    ongoing_points.set_data(ongoing_x, ongoing_y)
    
    return new_points, ongoing_points,

ani = animation.FuncAnimation(plt.gcf(), erupting, init_func=init,
                              frames=np.arange(year_0, 2020), blit=False, 
                              repeat=False)

plt.show()
ani.save(filename="../Data/figures/eruptions.mp4", fps=3, bitrate=1500, 
         dpi=300)