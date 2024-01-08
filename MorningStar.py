import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import BDay

#MS API
import requests
import io
#MS login
LoginDetails = requests.auth.HTTPBasicAuth('euli-sege@airliquide.com', 'brkGovTexY')

def GetICEPrices(feed, key_type, key, col = "Price", start_date = date.today() - relativedelta(years=2), end_date = date.today()):
    url = 'https://mp.morningstarcommodity.com/lds/feeds/{}/ts?'.format(feed)

    # Define parameters (different variables) you want to retrieve from that feed
    params  = {
                key_type: key,
                'cols': [col], 
                'fromDateTime': start_date, 
                'toDateTime': end_date
                }
    # Pull data
    temp = requests.get(url, params=params, auth=LoginDetails)
    temp = temp.text
    data = pd.read_csv(io.StringIO(temp))
    # Rename columns
    data.columns = ['date', 'Price']

    # Convert quote timestamps in datetime objects
    data['date'] = pd.to_datetime(data['date'], utc = True)

    # Get rid of the timezone info
    data['date'] = data['date'].dt.tz_localize(None)
    
    # Set 'datetime' as index
    data.set_index('date', drop=True, inplace=True)

    # Handle NaNs    
    data.dropna()

    return data

def get_ICE_fwd_curve(feed = "ICE_EuroFutures_continuous", key_type = "Contract", hub = "DPB", next_months = 24, start_date = date.today() - timedelta(days=1), end_date = date.today()):
  data = pd.DataFrame()
  temp_name = pd.Timestamp.today()
  for month in range(1, next_months + 1):
    if month < 10:
      key = hub + "_00{}_Month".format(month)
    else:
      key = hub + "_0{}_Month".format(month)
    temp_data = GetICEPrices(feed, key_type, key, col = "Settlement_Price", start_date = start_date, end_date = end_date)
    temp_name = temp_name + pd.DateOffset(months=1) 
    contract_name = pd.Timestamp(temp_name.year, temp_name.month, 1, 0, 0)
    temp_data.columns = [contract_name]
    data = pd.concat([data, temp_data], axis = 1)
  return data.T 

