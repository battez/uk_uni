import folium
print(folium.__version__)
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
insts = df.index.tolist()

# fuzzy threshold for non identical strings
threshold = 90 
unfound = 0 # count number we cannot match for this threshold

# MAPS and their params
zoom_start = 6
map_osm = folium.Map(location=[53.5074, -0.1 ], zoom_start=zoom_start)
map_alt = folium.Map(location=[53.5074, -0.1 ], zoom_start=zoom_start)
marker_cluster = folium.MarkerCluster("UK Universities and Student Numbers").add_to(map_osm)




# import data
with open(locs_uk_unis, 'rb') as csvfile:

    rows = csv.DictReader(csvfile, delimiter=',')
    radius = 20
    population = ' N/A'
    fill_color = '#bb3333'
    
    for row in rows:
        if row['Name'] in insts:
            found = True
        else:
            
            found = False

            for inst in insts:
                if(fuzz.token_set_ratio(row['Name'], inst) >= threshold):
                    found = True
                    row['Name'] = inst
                    break 
            if not found:
                # TODO log these and correct etc, and we obv. do not show on map:
                print 'not found----------------------->'
                unfound += 1
                print str(unfound)
                # fix for strange unicode chars in the names:
                print unicode(row['Name'], 'utf-8')
                continue

        fill_color = '#33bb33'
        population = df.loc[row['Name']]['Total students'].replace(',', '')
        radius = math.ceil(float(population)  / 5000.0 )
      
        # if radius is too small just dont show this:
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
            fill_color=fill_color, fill_opacity=0.5).add_to(map_alt)
        
    # output both maps
    map_osm.save('unis_clustered.html')
    map_alt.save('unis_relative.html')