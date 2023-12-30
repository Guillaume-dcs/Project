import yfinance as yf
import pandas as pd

from ENTSOE_data import EntsoeData

entsoe = EntsoeData()
start = entsoe.start
end = entsoe.end

def get_front_month_ticker(start):
    months_mapping = {1 : "F", 2 : "G", 3 : "H", 4 : "J", 5 : "K", 6 : "M", 7 : "N", 8 : "Q", 
                      9 : "U", 10 : "V", 11 : "X", 12 : "Z"}
    today_month = start.month
    if today_month == 12:
        return months_mapping[1]
    else:
        return months_mapping[today_month]

front_TTF_ticker = "TTF={}".format(get_front_month_ticker(start)) 
front_TTF = yf.download(front_TTF_ticker, start=start-pd.DateOffset(months=1), end=start, progress=False)["Open"].round(2)
front_coal_ticker = "MTF={}".format(get_front_month_ticker(start))
front_coal = yf.download(front_coal_ticker, start=start-pd.DateOffset(months=1), end=start, progress=False)["Open"].round(2)
eua = yf.download("CO2.L", start=start-pd.DateOffset(months=1), end=start, progress=False)["Open"].round(2)
DAH_NL = entsoe.client.query_day_ahead_prices("NL", start=start-pd.DateOffset(months=1), end=end)[:-1]
# load = entsoe.client.query_load_forecast("NL", start=start, end=end)
# df = pd.concat([DAH_NL, load], axis=1).dropna()
# df.columns = ["DAH_NL", "load"]
df = pd.DataFrame(DAH_NL, columns=["PW_NL_DAH"])
df.index = df.index - pd.Timedelta("1 day")
front_TTF.index = front_TTF.index.tz_localize(tz="Europe/Amsterdam")
front_coal.index = front_coal.index.tz_localize(tz="Europe/Amsterdam")
eua.index = eua.index.tz_localize(tz="Europe/Amsterdam")
df = pd.concat([df, front_TTF, front_coal, eua], axis=1).ffill()
df = df.dropna()
df.columns = ["PW_NL_DAH", "TTF", "Coal", "EUA"]
df["Clean_TTF"] = (df["TTF"] + 0.185 * df["EUA"]).round(2)
ratio = (df["Clean_TTF"] / df["PW_NL_DAH"]).round(2)
ratio = ratio[(ratio >= 0) & (ratio <=1)]
print(ratio)

# extract 3 years of hourly PW DAH prices + daily (spot or front month otherwise) open TTF EUA and Coal
# plot histogram for each hour PW DAH / Clean TTF
# some peaks should appear --> gas was marginal during those hours
# K-means algo to classify those clusters i.e to find the efficiencies of marginal NG plants
# Retrieve the hours, days, months, open TTF, open EUA, open Coal, forecasted load, forecasted REN... of those hours
# Train a random forest to associate a vector of inputs as described above to a cluster
# Compute the expected power price using the efficiency and available TTF and EUA prices
# Backtest
# Do same with coal

