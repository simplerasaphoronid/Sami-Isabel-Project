#!/usr/bin/env python
# coding: utf-8

# ## Sami and Isabel's Shade and Rest Analysis
# 
# ### Background:
# Shade access is a public health and an equity issue. Without sufficient shade, transit dependent commuters are forced to wait for the bus amidst intense heat. The City of Los Angeles, like many cities, is expected to see an increase in the number of days of extreme heat. Visits to emergency rooms (ER) because of heatwaves and heat strokes are increasing. Considering the forecasts of extreme heat days, it is the responsibility of planners and architects to ensure that public spaces are well-equipped with shade. In addition, transit infrastructures-such as benches at bus stops for rest-are important aspects of safe travel. 
# 
# ### Driving Questions:
# This research will provide answers to the following questions:
# 1. How does access to shade in Los Angeles vary across the Metro 20 bus route?
# 2. How does access to transit infrastructures, particularly bus stop benches, vary across the Metro 20 route?
# 2. To what extent does access to shade across the Metro 20 bus route vary by median household income of census tracts?
# 
# 

# ## Data
# 
# ### Data Sets
# 1. [Metro Bus Stops data set](https://api.metro.net/agencies/lametro/routes/20/stops/) to plot Route 20 along with bus stops
# 2. [City of LA Bus Stops/Benches](https://geohub.lacity.org/datasets/bus-stop-benches) to look at the infrastructre at the stop
# 3. [Street Tree Data provided by City of LA](data.lacity.org) to identify which bus stops are near shade trees
# 
# ### Data Exploration
# (In the next few lines of codes, we will import required datasets and conduct initial exploration as well as create few charts)

# #### Exploring Bus Stops Along Route 20

# Let's first import our bus stop data for route 20 

# In[1]:


import requests
from pandas.io.json import json_normalize
import pandas as pd

url = "https://api.metro.net/agencies/lametro/routes/20/stops/"
df = pd.read_json(url)
df


# Let's see what our data actually looks like

# In[2]:


df = pd.DataFrame(df['items'].tolist())
df


# We pulled the API data from metro for all bus stops in the 20 route. 
# Next lets do some basic exploratory analysis.

# In[3]:


df.dtypes


# In[4]:


latitude = df.latitude.mean()
longitude = df.longitude.mean()
latitude, longitude


# In[5]:


import folium
#initialize map
m = folium.Map(location=[latitude,longitude], tiles='CartoDB dark_matter', zoom_start=10)


# In[6]:


for index, row in df.iterrows():
    folium.CircleMarker([row.latitude,row.longitude],
                  radius=1, 
                  popup=row.display_name, 
                  tooltip=row.display_name,
                  fill= True
                 ).add_to(m)
m


# [Map1] What we have above is a map of bus stops along route 20. 

# #### Exploring Benches along Route 20

# Note that, because not all bus stops have benches, we are using separate dataset for bus stop benches.

# In[7]:


import geopandas as gpd


# In[8]:


benches=gpd.read_file('../gdata/Bus_Stop_Benches.shp')


# In[9]:


benches.dtypes


# In[10]:


benches.head()


# In[11]:


benches.shape


# Looks like this dataset is not too big and does not require that much cleaning. Also, notice that we have info on benches by Council Districts too. That might be interesting to analyze too! 

# In[12]:


import plotly.express as px


# In[13]:


px.bar(benches,
       x='AREA',
       title='Number of bus stop benches by Council Districts',
       labels={'AREA':'Council District','count':'Number of benches'}
      )


# [Chart 1] What we have above is a plot of benches in the city of LA by council districts.

# Notice how CD-07, CD06, CD-09 for example have so few bus stop benches. Another way to analyze this is by looking at benches by larger areas of the city

# In[14]:


px.bar(benches,
       x='CITY_SITE',
       title='Number of bus stop benches by Area of the city',
       labels={'CITY_SITE':'Area of the city','count':'Number of benches'}
      )


# [Chart 2]  What we have above is a plot of benches in the city of LA by area of the city

# Those charts were cool. Would be helpful to see spatial distribution of benches too. 

# In[15]:


fig = px.scatter_mapbox(benches,
                        lat='LATITUDE',
                        lon='LONGITUDE',
                        mapbox_style="carto-darkmatter")
fig.show()


# [Map2] What we have above is a map of all bus stop benches in the city of LA

# The map above is cool. But our research question is analyzing bus stop benches and trees along route 20. 
# Perhaps we can overlay the two maps (bus stops and bus stop benches) to see access to benches for route 20.

# Notice that our bus stops data was not in geodataframe. Lets convert it to geodataframe

# In[16]:


stops = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))


# In[17]:


base = stops.plot(figsize=(10,10),color='white', edgecolor='red')
ax = benches.plot(ax=base, color='blue', markersize=4)


# [Map 3]What we have above is a map of bus stops for route 20 (marked in red) and a map of bus stop benches as the base map. 

# What we'd like to have is a map of bus stop benches just for the route 20. Let's switch base map layers and maybe we can fix that?

# In[18]:


base = benches.plot(figsize=(10,10),color='white', edgecolor='red')
ax = stops.plot(ax=base, color='blue', markersize=4)


# Never mind. We didn't get a map of bus stops just zoomed in for our bus route...

# [Insert some codes to try here to make it work]

# So far we explored bus stop data and bus stop benches data. Next, let's bring our tree data for shade analysis

# #### Exploring the Street Tree Data 

# In[20]:


from sodapy import Socrata
from pandas.io.json import json_normalize


# In[21]:


#Creating a socrata client
# connect to the data portal
client = Socrata("data.lacity.org", None)

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("vt5t-mscf",
                    locarea ='WILSHIRE BL',
                    limit = 4000)

# Convert to pandas DataFrame
dft = pd.DataFrame.from_records(results)
# print it with .sample, which gives you random rows
dft.sample(2)


# In[23]:


dft.info()


# In[25]:


dft['x'] = dft.x.astype(float)
dft['y'] = dft.y.astype(float)


# In[26]:


pdf = dft[['trees_id','cd','common','botanical','dbh','x','y']]


# In[27]:


xdf = pdf.rename(columns={'x': 'latitude', 'y': 'longitude'})


# In[28]:


xdf.head()


# With few codes above, we create two new columns called latitude and longitude

# In[29]:


xdf.isna().any()


# In[30]:


px.scatter(xdf,
           x='latitude',
           y='longitude'
          )


# Hmm, what is this plot? Let's try something to show trees along our route

# In[31]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[32]:


xdf.shape


# In[33]:


xdf.sort_values(by='latitude', ascending = False)


# I have a problem with (0,0) coordinates

# In[34]:


#figuring out how to delete trees with latitude 0.00
new = xdf.drop([130, 313, 126, 125, 127, 128, 129, 397, 192, 61, 60, 
                1502, 1454, 1235, 1234, 1893, 1908, 1909, 1500, 1501, 1235])


# In[35]:


new.shape


# In[36]:


new.sort_values(by='latitude', ascending = False)


# Now that trees with (0,0) coordinates are set, lets map it!

# In[38]:


px.scatter(new,
           x='latitude',
           y='longitude'
          )


# [Map 4] What we have above shows trees along route 20. 

# We know palm trees don't really give that much shade. Maybe lets remove that from our analysis too. 

# In[39]:


new.sort_values(by='common', ascending = True)


# In[40]:


dft = new

shade = dft[~dft['common'].str.contains('PALM')]


# In[41]:


shade.shape


# In[42]:


shade[shade['common'].str.contains('NULL')]


# In[43]:


shade = shade[~shade['common'].str.contains('NULL')]
shade.shape


# In[44]:


shade = shade[~shade['common'].str.contains('OTHER')]
shade.shape


# In[45]:


shade.sort_values(by='common', ascending = True)


# In[46]:


shade = shade[~shade['common'].str.contains('VACANT')]
shade.shape


# In[47]:


shade.sort_values(by='common', ascending = True)


# In[48]:


px.scatter(new,
           x='latitude',
           y='longitude'
          )


# In[49]:


px.bar(shade,
       x='cd',
       title='Number of shade trees by Council Districts',
       labels={'cd':'Council Districts','count':'Number of shade trees'}
      )


# In[50]:


comp = new[~new['common'].str.contains('VACANT')]
comp.shape


# In[51]:


comp = comp[~comp['common'].str.contains('OTHER')]
comp.shape


# In[52]:


comp = comp[~comp['common'].str.contains('NULL')]
comp.shape


# In[53]:


palms = comp[comp['common'].str.contains('PALM')]


# In[55]:


notpalms = comp[~comp['common'].str.contains('PALM')]
len (notpalms)


# In[56]:


len(palms)


# Soo, we now know that along our route, the ratio of palm trees to shade trees is 351:1692. 

# Now, we can map just shade trees along route 20

# In[57]:


px.scatter(new,
           x='latitude',
           y='longitude'
          )


# [Map 4] What we have above shows shade trees along route 20!

# What'd be super cool is an overlay of trees and routes. Maybe we will come back to this by finals?

# In[ ]:





# ### Division of labor

# In[ ]:


Isabel-Work with tree data
Sami-Work with bus stops and bus benches data 

