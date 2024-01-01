import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from ENTSOE_data import EntsoeData
import matplotlib.pyplot as plt

class Model:

    def __init__(self):
        self.entsoe = EntsoeData()
        self.start = self.entsoe.start
        self.end = self.entsoe.end

    def get_front_month_ticker(self, start):
        months_mapping = {1 : "F", 2 : "G", 3 : "H", 4 : "J", 5 : "K", 6 : "M", 7 : "N", 8 : "Q", 
                        9 : "U", 10 : "V", 11 : "X", 12 : "Z"}
        today_month = start.month
        if today_month == 12:
            return months_mapping[1]
        else:
            return months_mapping[today_month]

    def get_data(self):
        front_TTF_ticker = "TTF={}".format(self.get_front_month_ticker(self.start)) 
        front_TTF = yf.download(front_TTF_ticker, start=self.start-pd.DateOffset(months=12), end=self.start, progress=False)["Open"].round(2)
        front_coal_ticker = "MTF={}".format(self.get_front_month_ticker(self.start))
        front_coal = yf.download(front_coal_ticker, start=self.start-pd.DateOffset(months=12), end=self.start, progress=False)["Open"].round(2)
        eua = yf.download("CO2.L", start=self.start-pd.DateOffset(months=12), end=self.start, progress=False)["Open"].round(2)
        DAH_NL = self.entsoe.client.query_day_ahead_prices("NL", start=self.start-pd.DateOffset(months=12), end=self.end)[:-1]
        ren = self.entsoe.client.query_wind_and_solar_forecast("NL", start=self.start-pd.DateOffset(months=12), end=self.end, psr_type=None).sum(axis=1)
        load = self.entsoe.client.query_load_forecast("NL", start=self.start-pd.DateOffset(months=12), end=self.end)
        # gen = self.entsoe.client.query_generation("NL", start=self.start-pd.DateOffset(months=1), end=self.end)
        # net_pos = self.entsoe.client.query_net_position("NL", start=self.start-pd.DateOffset(months=1), end=self.end)
        # gen_NG = gen['Fossil Gas']['Actual Aggregated']
        # gen_coal = gen['Fossil Hard coal']['Actual Aggregated']
        # gen_ren = gen['Wind Offshore']['Actual Aggregated'] + gen['Wind Onshore']['Actual Aggregated'] + gen['Solar']['Actual Aggregated']
        # df = pd.concat([DAH_NL, gen_NG, gen_coal, gen_ren, ren, load, net_pos], axis=1).dropna()
        df = pd.concat([DAH_NL, ren, load], axis=1).dropna()
        df.index = df.index - pd.Timedelta("1 day")
        front_TTF.index = front_TTF.index.tz_localize(tz="Europe/Amsterdam")
        front_coal.index = front_coal.index.tz_localize(tz="Europe/Amsterdam")
        eua.index = eua.index.tz_localize(tz="Europe/Amsterdam")
        df = pd.concat([df, front_TTF, front_coal, eua], axis=1).ffill()
        df = df.dropna()
        df.columns = ["PW_NL_DAH", "ren", "load", "TTF", "Coal", "EUA"]
        # df.columns = ["PW_NL_DAH", "gen_NG_D+1", "gen_coal_D+1", "gen_ren_D+1", "ren", "load", "net_pos", "TTF", "Coal", "EUA"]
        df["Clean_TTF"] = (df["TTF"] + 0.185 * df["EUA"]).round(2)
        df["Clean_coal"] = (df["Coal"] / 8.141 + 0.340 * df["EUA"]).round(2)
        return df

        # ratio_TTF = (df["Clean_TTF"] / df["PW_NL_DAH"]).round(2)
        # ratio_TTF = ratio_TTF[(ratio_TTF >= 0) & (ratio_TTF <=1)]
        # train_set_TTF = ratio_TTF.values[:-100].reshape(-1, 1)
        # test_set = ratio_TTF.values[100:].reshape(-1, 1)
        # kmeans_TTF = KMeans(10).fit(train_set_TTF)
        # centers_TTF = kmeans_TTF.cluster_centers_.round(2)
        # unique, counts = np.unique(kmeans_TTF.labels_, return_counts=True)
        # frequency_TTF = dict()
        # for item in range(len(centers_TTF)):
        #     frequency_TTF[centers_TTF[item][0]] = counts[item] / sum(counts)
        # frequency_TTF = pd.DataFrame.from_dict(frequency_TTF, orient="index")
        # frequency_TTF.columns = ["frequency"]
        # ng_efficiencies = list(frequency_TTF.nlargest(10, "frequency").index)

        # ratio_coal = (df["Clean_coal"] / df["PW_NL_DAH"]).round(2)
        # ratio_coal = ratio_coal[(ratio_coal >= 0) & (ratio_coal <=1)]
        # train_set = ratio_coal.values[:-100].reshape(-1, 1)
        # test_set = ratio_coal.values[100:].reshape(-1, 1)
        # kmeans_coal = KMeans(10).fit(train_set)
        # centers_coal = kmeans_coal.cluster_centers_.round(2)
        # unique, counts = np.unique(kmeans_coal.labels_, return_counts=True)
        # frequency_coal = dict()
        # for item in range(len(centers_coal)):
        #     frequency_coal[centers_coal[item][0]] = counts[item] / sum(counts)
        # frequency_coal = pd.DataFrame.from_dict(frequency_coal, orient="index")
        # frequency_coal.columns = ["frequency"]
        # coal_efficiencies = list(frequency_coal.nlargest(10, "frequency").index)

        # ng_capacities = dict()
        # for ng_efficiency in ng_efficiencies:
        #     df["css_{}".format(ng_efficiency)] = df["PW_NL_DAH"] - df["Clean_TTF"] / ng_efficiency
        #     css_positive = df[df["css_{}".format(ng_efficiency)] >= 0]["css_{}".format(ng_efficiency)]
        #     ng_capacities[ng_efficiency] = float(df[df["css_{}".format(ng_efficiency)] == css_positive.min()]["gen_NG_D+1"])
        # ng_capacities = pd.DataFrame.from_dict(ng_capacities, orient="index").sort_index()

        # coal_capacities = dict()
        # for coal_efficiency in coal_efficiencies:
        #     df["cds_{}".format(coal_efficiency)] = df["PW_NL_DAH"] - df["Clean_coal"] / coal_efficiency
        #     cds_positive = df[df["cds_{}".format(coal_efficiency)] >= 0]["cds_{}".format(coal_efficiency)]
        #     coal_capacities[coal_efficiency] = float(df[df["cds_{}".format(coal_efficiency)] == cds_positive.min()]["gen_coal_D+1"])
        # coal_capacities = pd.DataFrame.from_dict(coal_capacities, orient="index").sort_index()



    # extract 3 years of hourly PW DAH prices + daily (spot or front month otherwise) open TTF EUA and Coal
    # plot histogram for each hour PW DAH / Clean TTF
    # some peaks should appear --> gas was marginal during those hours
    # K-means algo to classify those clusters i.e to find the efficiencies of marginal NG plants
    # Retrieve the hours, days, months, open TTF, open EUA, open Coal, forecasted load, forecasted REN... of those hours
    # Train a random forest to associate a vector of inputs as described above to a cluster
    # Compute the expected power price using the efficiency and available TTF and EUA prices
    # Backtest
    # Do same with coal

