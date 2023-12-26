from entsoe import EntsoePandasClient
import pandas as pd
import matplotlib.pyplot as plt
import Countries
client = EntsoePandasClient(api_key="8541cf44-934e-4596-b999-aff4afbe7dde")

start = pd.Timestamp('20231225', tz='Europe/Brussels')
end = pd.Timestamp('20231226', tz='Europe/Brussels')

list_country_codes = Countries.Country().codes
country_code = 'NO_1'

def get_DAH_price(country_code, start, end):
    return client.query_day_ahead_prices(country_code, start=start, end=end)[:-1]
