import plotly.express as px
import pandas as pd
from ENTSOE_data import EntsoeData
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

entsoe = EntsoeData()
df = entsoe.get_data()
day = entsoe.start
df = df.set_index("name").round(2)

fig = px.choropleth(df, geojson=df.geometry, locations=df.index, color="DAH", 
                    color_continuous_scale="Reds", hover_name=df.DAH)
labels = px.scatter_geo(df, geojson=df.geometry, locations=df.index, text=df.DAH, opacity=0)
fig.add_trace(labels.data[0])
fig.update_geos(fitbounds="locations", visible=True)
fig.update_layout(title_text = "Avg DAH results €/MWh {}".format(day.strftime("%Y/%m/%d")), title_x=0.5)

fig_wind = px.choropleth(df, geojson=df.geometry, locations=df.index, color="wind", 
                    color_continuous_scale="Greens", hover_name=df.wind)
labels = px.scatter_geo(df, geojson=df.geometry, locations=df.index, text=df.wind, opacity=0)
fig_wind.add_trace(labels.data[0])
fig_wind.update_geos(fitbounds="locations", visible=True)
fig_wind.update_layout(title_text = "Avg Wind forecast GW {}".format(day.strftime("%Y/%m/%d")), title_x=0.5)

fig_solar = px.choropleth(df, geojson=df.geometry, locations=df.index, color="solar", 
                    color_continuous_scale="oranges", hover_name=df.wind)
labels = px.scatter_geo(df, geojson=df.geometry, locations=df.index, text=df.solar, opacity=0)
fig_solar.add_trace(labels.data[0])
fig_solar.update_geos(fitbounds="locations", visible=True)
fig_solar.update_layout(title_text = "Avg Solar forecast GW {}".format(day.strftime("%Y/%m/%d")), title_x=0.5)

fig_load = px.choropleth(df, geojson=df.geometry, locations=df.index, color="load", 
                    color_continuous_scale="greys", hover_name=df.wind)
labels = px.scatter_geo(df, geojson=df.geometry, locations=df.index, text=df.load, opacity=0)
fig_load.add_trace(labels.data[0])
fig_load.update_geos(fitbounds="locations", visible=True)
fig_load.update_layout(title_text = "Avg Load forecast GW {}".format(day.strftime("%Y/%m/%d")), title_x=0.5)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='European Electricity Markets', style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            dcc.Graph(figure=fig)], style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(figure=fig_wind)], style={'width': '49%', 'display': 'inline-block'})
    ]),

    html.Div([
    html.Div([
        dcc.Graph(figure=fig_solar)], style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(figure=fig_load)], style={'width': '49%', 'display': 'inline-block'})
    ])
])

if __name__ == '__main__':
    app.run(debug=True)
