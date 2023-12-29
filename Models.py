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
front_TTF = yf.download(front_TTF_ticker, start=start, end=start, progress=False)["Open"].round(2)
front_coal_ticker = "MTF={}".format(get_front_month_ticker(start))
front_coal = yf.download(front_coal_ticker, start=start, end=start, progress=False)["Open"].round(2)
eua = yf.download("CO2.L", start=start, end=start, progress=False)["Open"].round(2)
DAH_NL = entsoe.client.query_day_ahead_prices("NL", start=start, end=end)[:-1]
load = entsoe.client.query_load_forecast("NL", start=start, end=end)
df = pd.concat([DAH_NL, load], axis=1).dropna()
df.columns = ["DAH_NL", "load"]
df["TTF"] = float(front_TTF)
df["coal"] = float(front_coal)
df["eua"] = float(eua)
df["CSS_51"] = df["DAH_NL"] - df["TTF"] / 0.51 - df["eua"] / 0.51 * 0.185
df["CSS_51"] = df["CSS_51"].round(2)
df["CSS_60"] = df["DAH_NL"] - df["TTF"] / 0.60 - df["eua"] / 0.60 * 0.185
df["CSS_60"] = df["CSS_60"].round(2)
print(df)
