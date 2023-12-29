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
        self.client = EntsoePandasClient(api_key="8541cf44-934e-4596-b999-aff4afbe7dde")

        self.start = pd.Timestamp(pd.Timestamp.today().strftime("%Y%m%d"), 
                                    tz='Europe/Brussels')
        self.end = self.start + pd.DateOffset(days=1)

    def get_data(self):
        dict_country_codes = Countries.Country().codes

        def get_DAH_price(country_code, start, end):
            return self.client.query_day_ahead_prices(country_code, start=start, end=end)[:-1]
        
        def get_wind_solar(country_code, start, end):
            return self.client.query_wind_and_solar_forecast(country_code, start=start, 
                                                             end=end, psr_type=None) / 1000
        
        def get_load(country_code, start, end):
            return self.client.query_load_forecast(country_code, start=start, end=end) / 1000

        dict_country_DAH = {country : get_DAH_price(dict_country_codes[country], 
                                                    self.start, self.end).mean(axis=0).round(2) 
                                                    for country in dict_country_codes.keys()}
        df_avgDAH = pd.DataFrame.from_dict(dict_country_DAH, orient="index").reset_index()
        df_avgDAH.columns = ["name", "DAH"]

        dict_country_wind_solar = {country : get_wind_solar(dict_country_codes[country], 
                                                    self.start, self.end).mean(axis=0).round(2) 
                                                    for country in dict_country_codes.keys()}
        df_avg_wind_solar = pd.DataFrame.from_dict(dict_country_wind_solar, orient="index").reset_index()
        df_avg_wind_solar = df_avg_wind_solar.fillna(0)
        df_avg_wind_solar["wind"] = df_avg_wind_solar["Wind Offshore"] + df_avg_wind_solar["Wind Onshore"]
        df_avg_wind_solar = df_avg_wind_solar.drop(columns=["Wind Offshore", "Wind Onshore"])
        df_avg_wind_solar.columns = ["name", "solar", "wind"]

        dict_country_load = {country : get_load(dict_country_codes[country], 
                                                    self.start, self.end).mean(axis=0).round(2) 
                                                    for country in dict_country_codes.keys()}
        df_avg_load = pd.DataFrame.from_dict(dict_country_load, orient="index").reset_index()
        df_avg_load.columns = ["name", "load"]

        world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
        europe=world[world.continent=="Europe"]
        europe=europe[(europe.name!="Russia") & (europe.name!="Iceland")]
        polygon = Polygon([(-25,35), (40,35), (40,75),(-25,75)])
        europe=geopandas.clip(europe, polygon) 
        selected_countries=europe[europe.name.isin(list(df_avgDAH.name))]
        selected_countries=selected_countries.merge(df_avgDAH,on="name",how="left")
        selected_countries=selected_countries.merge(df_avg_wind_solar,on="name",how="left")
        selected_countries=selected_countries.merge(df_avg_load,on="name",how="left")
        selected_countries=selected_countries.drop(columns=["pop_est", "continent", "iso_a3", 
                                                            "gdp_md_est"])
        return selected_countries

