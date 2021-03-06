'''
    plot some Twitter Places on a Folium map
'''
import csv
import math
import pandas as pd
import os.path

# Map related:
import folium

import branca.colormap as cm

from folium.plugins import FloatImage
url = 'img/accu-snow-weather-sm.jpg'


# data set-up:
locs = 'places_grouped.csv' # lats longs and names
dfin = pd.read_csv(locs)
df = dfin.set_index(['_id'])
all = df.index.tolist()
# print(df.head(3))
# print(df.columns)
# print(df.describe())
with_states = df['place.0.name'].str.contains('\s[A-Z][A-Z]$', na=False, regex=True)
num_states = with_states.sum()  

# states = df[df[1].str.extract('\s[A-Z][A-Z]$')].sum()  

# MAPS and their params
filename = os.path.basename(__file__)
output_osm = filename.split('.')[0] + '.html'
zoom_start = 7
centre = [df['place.0.bounding_box.coordinates.0.0.1'].mean(), df['place.0.bounding_box.coordinates.0.1.0'].mean()] # Pennsylvania-ish
df = df.sort_values(['place.0.place_type'], ascending=[True])

# Setup the map: 
fmap = folium.Map(location=centre, max_zoom=30, zoom_start=zoom_start, control_scale=True, tiles="stamenterrain")

# box styles
styles = {'opacity' : 0.2, 'color' : '#323232', 'fill_color':'red' }
threshold = 5000 # max no of count we will allow
adjust_scale_color = 100
linear = cm.LinearColormap(['green', 'yellow', 'red'], vmin=1, vmax=round(threshold/adjust_scale_color)) # 'yellow',
linear.caption = 'Tweet intensity (scaled)' 

# for point marker size
radius = 10 

# different place_types for Places.
colors = {'admin' : 'black', 'city' : 'purple' , 'poi' : '#318633' , 'neighborhood' : 'blue', 'country' : 'white'}
idx = 0
remove = ['country']


feature_groups = colors.copy()
# make this have a group for each place_type so they can all be toggled. 
for key, value in feature_groups.items():
    if key not in remove:
        feature_groups[key] = folium.FeatureGroup(name='enable place_type: ' + key)

marker_cluster = folium.MarkerCluster("enable place_type: point-of-interest").add_to(fmap)

# fixme - will calculate the color based on the count (tweet intensity)
for row in df.itertuples():
    idx += 1

    # popup text
    index, count, name, place_type = row[:4]

    # skip some values that just screw up the map
    if (not isinstance(place_type, str)) or (not isinstance(name, str)) or\
     (place_type in remove) or (name[-6:] == 'Canada') or (count > threshold):
        continue # i.e. omit all these ones
    
    # bounding box corners for every Place
    bottom_left = list()
    top_right = list()
    
    # boxes coords:
    bottom_left.append(row[5])
    bottom_left.append(row[4])
    top_right.append(row[9])
    top_right.append(row[8])
    
    # now build markers for map and their popups:
    string = '%s: %d tweets. Type:%s' % (name, count, place_type)
    if bottom_left[0] != top_right[0]:
        marker = folium.features.RectangleMarker(
            bounds=[bottom_left, top_right],
            color=colors[place_type],
            fill_color=linear(count),
            fill_opacity=styles['opacity'],
            popup=string)
    else:
        # icon=folium.Icon(color='red', icon='info-sign')
        # sometimes the Places are point coordinates!
        marker = folium.RegularPolygonMarker(
            location=bottom_left,
            radius=radius,
            color=colors[place_type],
            weight=0,
            fill_color=linear(count),
            number_of_sides=6,
            popup=string)

    if(place_type == 'poi'):
        marker.add_to(marker_cluster)
    else:
        feature_groups[place_type].add_child(marker)


fmap.add_child(linear) 
for key, feature_group in feature_groups.items():
    if (key not in remove) and (key is not 'poi'):
        fmap.add_child(feature_group)
# folium.TileLayer('openstreetmap').add_to(fmap)
folium.TileLayer('Cartodb Positron').add_to(fmap)
folium.LayerControl(collapsed=False).add_to(fmap)

# todo: add in choro layer with states totals as per:
# https://nbviewer.jupyter.org/github/python-visualization/folium/blob/master/examples/Quickstart.ipynb
# need to make a df from States from full_name last letters to do this.
# output both maps
FloatImage(url, bottom=3, right=1).add_to(fmap)
fmap.save(output_osm)
    
