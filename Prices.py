from entsoe import EntsoePandasClient
import pandas as pd
import matplotlib.pyplot as plt
import Countries
import geopandas
from shapely.geometry import Polygon
import warnings
warnings.filterwarnings(action="ignore")

class EntsoeData:

    def __init__(self):
        client = EntsoePandasClient(api_key="8541cf44-934e-4596-b999-aff4afbe7dde")

        # If the auction for the next day (around noon) is finished then
        if pd.Timestamp.today().hour > 14:
            self.start = pd.Timestamp(pd.Timestamp.today().strftime("%Y%m%d"), 
                                tz='Europe/Brussels') + pd.DateOffset(days=1)
            self.end = self.start + pd.DateOffset(days=1)
        else:
            self.start = pd.Timestamp(pd.Timestamp.today().strftime("%Y%m%d"), 
                                      tz='Europe/Brussels')
            self.end = self.start + pd.DateOffset(days=1)
        dict_country_codes = Countries.Country().codes

        def get_DAH_price(country_code, start, end):
            return client.query_day_ahead_prices(country_code, start=start, end=end)[:-1]

        dict_country_DAH = {country : get_DAH_price(dict_country_codes[country], 
                                                    self.start, self.end) 
                            for country in dict_country_codes.keys()}
        df_DAH = pd.DataFrame.from_dict(dict_country_DAH)
        df_avgDAH = df_DAH.mean(axis=0).round(2)
        df_avgDAH = pd.DataFrame({"name" : df_avgDAH.index, "DAH" : df_avgDAH.values})

        world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
        europe=world[world.continent=="Europe"]
        europe=europe[(europe.name!="Russia") & (europe.name!="Iceland")]
        # Create a custom polygon
        polygon = Polygon([(-25,35), (40,35), (40,75),(-25,75)])

        europe=geopandas.clip(europe, polygon) 
        selected_countries=europe[europe.name.isin(list(df_DAH.columns))]
        selected_countries=selected_countries.merge(df_avgDAH,on="name",how="left")
        selected_countries=selected_countries.drop(columns=["pop_est", "continent", "iso_a3", 
                                                            "gdp_md_est"])
        lat = [list(selected_countries.geometry[i].centroid.coords)[0][0]
                    for i in range(len(selected_countries))]
        lon = [list(selected_countries.geometry[i].centroid.coords)[0][1]
                    for i in range(len(selected_countries))]
        selected_countries["lat"] = lat
        selected_countries["lon"] = lon
        self.data = selected_countries

    def plot_data(self):

        self.data.plot("DAH",cmap="Reds",edgecolor="black")

        plt.rcParams["figure.figsize"]=(10,10)
        plt.rcParams["font.size"]=10
        for i in range(len(self.data)):
            plt.text(self.data.lat[i], self.data.lon[i],
                      "%.2f" % self.data.DAH[i])
        plt.title("DAH results {}".format(self.start.strftime("%Y/%m/%d")))
        plt.axis('off')
        plt.show()
