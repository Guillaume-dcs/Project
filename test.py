from entsoe import EntsoePandasClient
import pandas as pd
import matplotlib.pyplot as plt
client = EntsoePandasClient(api_key="8541cf44-934e-4596-b999-aff4afbe7dde")

start = pd.Timestamp('20231210', tz='Europe/Brussels')
end = pd.Timestamp('20231223', tz='Europe/Brussels')
country_code = 'NO_1'  # Belgium
country_code_from = 'FR'  # France
country_code_to = 'DE_LU' # Germany-Luxembourg
type_marketagreement_type = 'A01'
contract_marketagreement_type = "A01"
process_type = 'A51'

# methods that return Pandas Series
df = client.query_day_ahead_prices(country_code, start=start, end=end)
load = client.query_load(country_code, start=start, end=end)
generation = client.query_generation(country_code, start=start, end=end, psr_type=None)
#generation.plot()
#load.plot()
#plt.show()
#print(client.query_aggregate_water_reservoirs_and_hydro_storage(country_code, start=start, end=end))
print(client.query_crossborder_flows(country_code_from, country_code_to, start=start, end=end))

#print(client.query_installed_generation_capacity(country_code, start=start, end=end, psr_type=None))