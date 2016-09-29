'''
    script to combine two csv sources on UK Unis and plot on a map, 
    along with their populations (in popups)
'''

import folium
# print(folium.__version__)
import csv
import math
import pandas as pd

# using this to tally institution names up from two data sources
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# data set-up:
locs_uk_unis = 'uk_universities_locations.csv' # lats longs and names
dfin = pd.read_csv('uni_popns.csv')
df = dfin.set_index(['Institution'])
institutions = df.index.tolist()

# fuzzy threshold for non identical strings
threshold = 90 
unfound = 0 # count number we cannot match for this threshold

# MAPS and their params
zoom_start = 6

map_osm = folium.Map(location=[53.5074, -0.1 ], zoom_start=zoom_start, tiles="Cartodb Positron")
output_osm = 'unis_clustered.html'
marker_cluster = folium.MarkerCluster("UK Universities and Student Numbers").add_to(map_osm)

map_alt = folium.Map(location=[53.5074, -0.1 ], zoom_start=7)
output_alt = 'unis_relative.html'

# import data
with open(locs_uk_unis, 'rb') as csvfile:

    rows = csv.DictReader(csvfile, delimiter=',')

    # set up default Folium marker values
    radius = 20
    scale_value = 5
    population = ' N/A'
    fill_color = '#33bb33'
    
    for row in rows:
        ''' 
        build a marker for the clustered set 
        and a marker for the other map:
        '''

        # if we have a straight string match:
        if row['Name'] in institutions:
            found = True
        else:
            # use fuzzy matches to find a few more:
            found = False

            for inst in institutions:

                if(fuzz.token_set_ratio(row['Name'], inst) >= threshold):
                    found = True
                    row['Name'] = inst
                    break 

            if not found:
                # TODO log these and correct etc, and we obv. do not show on map
                unfound += 1

                # fix for strange unicode chars in the names:
                print str(unfound) + ': ' + unicode(row['Name'], 'utf-8')
                continue


        population = df.loc[row['Name']]['Total students'].replace(',', '')
        radius = math.ceil(float(population)  / scale_value )
      
        # if radius is too small just dont show this marker:
        if radius == 0:
            continue

        # fix for strange unicode chars in the names:
        row['Name'] = unicode(row['Name'], 'utf-8')
        popup = row['Name'] + ' // Students:' + population

        # add for clustered-per-zoom-level view
        folium.Marker(location=[row['lat'], row['lon']], \
            popup=popup).add_to(marker_cluster)

        # and make a alt. map circle marker, with radius rel. to population:
        folium.CircleMarker(location=[row['lat'], row['lon']], \
            radius=radius, popup=popup, \
            fill_color=fill_color, fill_opacity=0.25).add_to(map_alt)
        

    # output both maps
    map_osm.save(output_osm)
    map_alt.save(output_alt)
