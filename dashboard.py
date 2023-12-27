import plotly.express as px
import pandas as pd
from Prices import EntsoeData

df = EntsoeData().data
day = EntsoeData().start
df = df.set_index("name")

fig = px.choropleth(df, geojson=df.geometry, locations=df.index, color="DAH", 
                    color_continuous_scale="Reds", hover_name=df.DAH)
labels = px.scatter_geo(df, geojson=df.geometry, locations=df.index, text=df.DAH, opacity=0)
fig.add_trace(labels.data[0])
fig.update_geos(fitbounds="locations", visible=True)
fig.update_layout(title_text = "DAH results {}".format(day.strftime("%Y/%m/%d")))
fig.show()