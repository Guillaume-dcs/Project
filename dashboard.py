from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from Prices import EntsoeData

df = EntsoeData().data
day = EntsoeData().start
df = df.set_index("name")

fig = px.choropleth(df, geojson=df.geometry, locations=df.index, color="DAH", 
                    color_continuous_scale="Reds")
fig.add_scattergeo(
    locations=df.index, 
    text=df.DAH,
    mode='text')
fig.update_geos(fitbounds="locations", visible=True)
fig.update_layout(title_text = "DAH results {}".format(day.strftime("%Y/%m/%d")))

fig.show()