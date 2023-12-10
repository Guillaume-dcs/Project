msg = "hello"
print(msg)

import numpy as np
import pandas as pd
import datetime
from datetime import date

today = datetime.date.today()
test = {"date" : today, "price" : 100}
df = pd.DataFrame.from_dict(test, 'index', columns=["value"])
print(df)