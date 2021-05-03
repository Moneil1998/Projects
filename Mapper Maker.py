import sys
sys.path.append(r'/Users/admin/Documents/5222/5222/gisalgs')
from geom.shapex import *
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from geom.paths import *

is_polygon_shp = False
while not is_polygon_shp:
    fname = input("Enter a shapefile name: ")
    #fname = r'/Users/admin/Documents/5222/5222/gisalgs/data/uscnty48area.shp' 
    try:
        mapdata = shapex(fname)
    except Exception as e:
        print('Error:', e)
        print('Make sure your enter a valid shapefile')
        continue
    shp_type = mapdata[0]['geometry']['type']
    if shp_type in ['Polygon', 'MultiPolygon']:
        is_polygon_shp = True
    else:
        print('Make sure it is a polygon or multipolygon shapefile')
    print()

shp=shapex(fname)

attribute = input("Enter your attribute: ")
numOfClasses = int(input("Enter the number classes (Max:8 Classes): "))



_, ax = plt.subplots()
title=input("Enter a title: ")
ax.set_title(title)
temp=[]
for i in range(len(shp)):
    temp.append(shp[i]['properties'][attribute])
temp.sort(reverse=True)

lenOfClass = len(temp)//int(numOfClasses)
def interval(x, n): 
    for i in range(0, len(x), n):  
        yield x[i:i + n] 
  
con = list(interval(temp, lenOfClass)) 

colors=['#800026', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#ffffcc']

polygon=[]
for i in range(0, len(shp)):
    
    if shp[i]['geometry']['type']=='Polygon':
        polygon=shp[i]['geometry']['coordinates']
    else:
        
        multipolygon=shp[i]['geometry']['coordinates']
        for poly in multipolygon:
            polygon.append(poly[0])

    bound = shp.bounds
    xmin = bound[0]
    xmax = bound[2]
    ymin = bound[1]
    ymax = bound[3]
    xmin, xmax, ymin, ymax
    x = xmin
    delta = 0.1
    xticks = []
    while x < xmax:
        xticks.append(x)
        x += delta
    y = ymin
    yticks = []
    while y < ymax:
        yticks.append(y)
        y += delta
    xticks, yticks
    
    path1 = make_path(polygon)

    for l in range(len(con)):
        if shp[i]['properties'][attribute] in con[l]:
            patch = PathPatch(path1, facecolor=colors[l],fill=True)

    ax.add_patch(patch)
   
print('\n')
print('LEGEND:')
for i in range(len(con)-1):
    print("{} {} - {}".format(colors[i], con[i][0], con[i][-1]))


ax.set_ylim([ymin, ymax])
ax.set_xlim([xmin, xmax])
ax.axis('equal')
plt.show()





