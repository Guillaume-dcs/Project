import plotly.express as px
import pandas as pd
from Prices import EntsoePrices
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

df = EntsoePrices().data
day = EntsoePrices().start
df = df.set_index("name")

fig = px.choropleth(df, geojson=df.geometry, locations=df.index, color="DAH", 
                    color_continuous_scale="Reds", hover_name=df.DAH)
labels = px.scatter_geo(df, geojson=df.geometry, locations=df.index, text=df.DAH, opacity=0)
fig.add_trace(labels.data[0])
fig.update_geos(fitbounds="locations", visible=True)
fig.update_layout(title_text = "DAH results {}".format(day.strftime("%Y/%m/%d")), title_x=0.5)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='European Electricity Markets', style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            dcc.Graph(figure=fig)], style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(figure=fig)], style={'width': '49%', 'display': 'inline-block'})
    ])
])

if __name__ == '__main__':
    app.run(debug=True)
