import wapi
import pandas as pd
import matplotlib.pyplot as plt

session = wapi.Session(client_id='oY3v6aYjMU_dD0cpmHBa30ViFIj3Epc_', 
                       client_secret='SRXqj1bp335.jToEPS2YBC.5JQb9ReCTYIB7aABindLmdytQn3yX0xQrhubB.9eTEF_.stlQ_O0lymDNv1_jSM-.83kYRYxBIVxc')

tickers = {"PW NL Consumption" : 'con nl fwd mw cet h f', "NG Production" : 'pro nl thermal gas fwd mw cet h f',
           "Coal Production" : 'pro nl thermal coal fwd mw cet h f', "Wind Production" : 'pro nl wnd fwd mw cet h f',
           "Solar Production" : 'pro nl spv fwd mw cet h f', "Nuclear Production" : 'pro nl nuc fwd mw cet h f',
           "Biomass Production" : 'pro nl thermal biomass fwd mw cet h f'}

NL_borders = {"be" : "Belgium", "de" : "Germany", "dk1" : "Denmark DK1", "no2" : "Norway NO2", "uk" : "UK"}

NL_power_exchanges = pd.DataFrame()
for country in list(NL_borders.keys()):
    country_curve = session.get_curve(name="exc {}>nl com fwd mw cet h f".format(country))
    NL_power_exchanges[NL_borders[country]] = country_curve.get_latest(frequency="D", function="AVERAGE").to_pandas().to_frame() / 1000
NL_power_exchanges = NL_power_exchanges.round(2)

NL_power_production = pd.DataFrame()
NL_power_consumption = pd.DataFrame()
for item in list(tickers.keys()):
    item_curve = session.get_curve(name=tickers[item])
    item_ts = item_curve.get_latest(frequency="D", function="AVERAGE")
    if "Production" in item:
        NL_power_production[item] = item_ts.to_pandas().to_frame() / 1000
    else:
        NL_power_consumption[item] = item_ts.to_pandas().to_frame() / 1000
NL_power_production = NL_power_production.round(2)
NL_power_consumption = NL_power_consumption.round(2)

NL_PW_forwards = session.get_curve(27136).get_latest(frequency="D", function="AVERAGE").to_pandas().to_frame()
NL_PW_forwards.columns = ["PW NL Forwards"]
NL_NG_forwards = session.get_curve(27089).get_latest(frequency="D", function="AVERAGE").to_pandas().to_frame() * 3.6
NL_Coal_forwards = session.get_curve(27102).get_latest(frequency="D", function="AVERAGE").to_pandas().to_frame() * 3.6
NL_EUA_forwards = session.get_curve(27111).get_latest(frequency="D", function="AVERAGE").to_pandas().to_frame() * 1000

NL_NG_clean_forwards = pd.concat([NL_NG_forwards, 0.185 * NL_EUA_forwards], axis=1).sum(axis=1)
NL_NG_clean_forwards.columns = ["Clean NG Forwards"]
NL_Coal_clean_forwards = pd.concat([NL_Coal_forwards, 0.340 * NL_EUA_forwards], axis=1).sum(axis=1)
NL_Coal_clean_forwards.columns = ["Clean Coal Forwards"]
NG_ratios = (NL_NG_clean_forwards / NL_PW_forwards.T).T
NG_ratios.columns = ["NG Efficiency"]
Coal_ratios = (NL_Coal_clean_forwards / NL_PW_forwards.T).T
Coal_ratios.columns = ["Coal Efficiency"]

efficiencies = pd.concat([NL_power_production, NG_ratios, Coal_ratios], axis=1)
NG_marginal_efficiencies = efficiencies[(efficiencies["NG Production"] > 0) & (efficiencies["Coal Production"] == 0)]["NG Efficiency"]
NG_marginal_volumes = efficiencies[(efficiencies["NG Production"] > 0) & (efficiencies["Coal Production"] == 0)]["NG Production"]
NG_marginal = pd.concat([NG_marginal_efficiencies, NG_marginal_volumes], axis=1).round(2)

NG_capacities = {}
for efficiency in set(NG_marginal["NG Efficiency"]):
    NG_capacities[efficiency] = NG_marginal[NG_marginal["NG Efficiency"] == efficiency].min()["NG Production"]
NG_capacities = pd.DataFrame.from_dict(NG_capacities, orient="index")
NG_capacities.columns = ["Capacity"]
NG_cumulative_capacities = NG_capacities.sort_values(by="Capacity")
NG_capacities = NG_cumulative_capacities - NG_cumulative_capacities.shift()
NG_capacities = NG_capacities.fillna(NG_cumulative_capacities.iloc[0])[NG_capacities > 0].dropna()

Coal_marginal_efficiencies = efficiencies[(efficiencies["NG Efficiency"] >= efficiencies["Coal Efficiency"]) & (efficiencies["Coal Production"] > 0)]["Coal Efficiency"]
Coal_marginal_volumes = efficiencies[(efficiencies["NG Efficiency"] >= efficiencies["Coal Efficiency"]) & (efficiencies["Coal Production"] > 0)]["Coal Production"]
Coal_marginal = pd.concat([Coal_marginal_efficiencies, Coal_marginal_volumes], axis=1).round(2)

Coal_capacities = {}
for efficiency in set(Coal_marginal["Coal Efficiency"]):
    Coal_capacities[efficiency] = Coal_marginal[Coal_marginal["Coal Efficiency"] == efficiency].min()["Coal Production"]
Coal_capacities = pd.DataFrame.from_dict(Coal_capacities, orient="index")
Coal_capacities.columns = ["Capacity"]
Coal_cumulative_capacities = Coal_capacities.sort_values(by="Capacity")
Coal_capacities = Coal_cumulative_capacities - Coal_cumulative_capacities.shift()
Coal_capacities = Coal_capacities.fillna(Coal_cumulative_capacities.iloc[0])[Coal_capacities > 0].dropna()

df_merit_order = {}
df_real_price = {}
df_expected_price = {}

for i in range(efficiencies.shape[0]):
    load_forecast = round(float(NL_power_consumption.iloc[i]), 2) 
    wind_forecast = round(float(NL_power_production["Wind Production"].iloc[i]), 2)
    solar_forecast = round(float(NL_power_production["Solar Production"].iloc[i]), 2) * 1.25 #TenneT does not measure small scale SPV. 
    nuclear_forecast = round(float(NL_power_production["Nuclear Production"].iloc[i]), 2)
    biomass_forecast = round(float(NL_power_production["Biomass Production"].iloc[i]), 2)
    exchanges_forecast = round(float(NL_power_exchanges.iloc[i].sum()), 2)
    clean_ng_price_forecast = round(float(NL_NG_clean_forwards.iloc[i]), 2)
    clean_coal_price_forecast = round(float(NL_Coal_clean_forwards.iloc[i]), 2)
    ng_marginal_costs = {eff:round(clean_ng_price_forecast / eff, 2) for eff in NG_capacities.index}
    coal_marginal_costs = {eff:round(clean_coal_price_forecast / eff, 2) for eff in Coal_capacities.index}
    ng_marginal_costs = sorted(ng_marginal_costs.items(), key=lambda x: x[1])
    coal_marginal_costs = sorted(coal_marginal_costs.items(), key=lambda x: x[1])
    residual_load = load_forecast - wind_forecast - solar_forecast - nuclear_forecast - biomass_forecast - exchanges_forecast
    merit_order = {wind_forecast:0, solar_forecast:0, nuclear_forecast:0, biomass_forecast:0}
    count_ng = 0
    count_coal = 0
    while residual_load > 0:
        if count_ng < len(ng_marginal_costs) and count_coal < len(coal_marginal_costs):
            cheapest_ng = ng_marginal_costs[count_ng]
            cheapest_coal = coal_marginal_costs[count_coal]
            if cheapest_ng[1] <= cheapest_coal[1]:
                merit_order[("NG_{}".format(count_ng), round(float(NG_capacities[NG_capacities.index == cheapest_ng[0]].values), 2))] = cheapest_ng[1]
                residual_load = residual_load - float(NG_capacities[NG_capacities.index == cheapest_ng[0]].values)
                count_ng +=1
            else:
                merit_order[("Coal_{}".format(count_coal), round(float(Coal_capacities[Coal_capacities.index == cheapest_coal[0]].values), 2))] = cheapest_coal[1]
                residual_load = residual_load - float(Coal_capacities[Coal_capacities.index == cheapest_coal[0]].values)
                count_coal +=1
        elif count_ng >= len(ng_marginal_costs) and count_coal < len(coal_marginal_costs):
            cheapest_coal = coal_marginal_costs[count_coal]
            merit_order[("Coal_{}".format(count_coal), round(float(Coal_capacities[Coal_capacities.index == cheapest_coal[0]].values), 2))] = cheapest_coal[1]
            residual_load = residual_load - float(Coal_capacities[Coal_capacities.index == cheapest_coal[0]].values)
            count_coal +=1
        elif count_ng < len(ng_marginal_costs) and count_coal >= len(coal_marginal_costs):
            cheapest_ng = ng_marginal_costs[count_ng]
            merit_order[("NG_{}".format(count_ng), round(float(NG_capacities[NG_capacities.index == cheapest_ng[0]].values), 2))] = cheapest_ng[1]
            residual_load = residual_load - float(NG_capacities[NG_capacities.index == cheapest_ng[0]].values)
            count_ng +=1
        elif count_ng >= len(ng_marginal_costs) and count_coal >= len(coal_marginal_costs):
            merit_order[(count_ng, round(residual_load, 2))] = list(merit_order.values())[-1]
            residual_load = 0

    df_merit_order[efficiencies.iloc[i].name] = merit_order
    df_real_price[efficiencies.iloc[i].name] = float(NL_PW_forwards.iloc[i])
    df_expected_price[efficiencies.iloc[i].name] = list(merit_order.values())[-1]

df_real_price = pd.DataFrame.from_dict(df_real_price, orient="index")
df_real_price.columns = ["Actual PW NL"]
df_expected_price = pd.DataFrame.from_dict(df_expected_price, orient="index")
df_expected_price.columns = ["Expected PW NL"]
df_prices = pd.concat([df_expected_price, df_real_price], axis=1).round(2)

def plot_merit_order(NL_power_consumption, NL_power_exchanges, df_merit_order, df_prices, date):
    merit_order = df_merit_order[date]
    exchanges_forecast = round(NL_power_exchanges[NL_power_exchanges.index == date].sum(axis=1).values[0], 2)
    df_merit = pd.DataFrame.from_dict(merit_order, orient="index")
    new_index = []
    for item in df_merit.index:
        try:
            new_index.append(item[1])
        except:
            new_index.append(item)
    df_merit.index = new_index
    df_merit = df_merit.reset_index()
    df_merit.columns = ["Capacity", "Marginal Cost"]
    df_merit = df_merit.set_index("Marginal Cost").cumsum()
    load = [NL_power_consumption[NL_power_consumption.index == date].values[0][0] - exchanges_forecast] * df_merit.shape[0]
    plt.plot(list(df_merit["Capacity"]), list(df_merit.index), label="Supply")
    plt.plot(load, list(df_merit.index), label="Demand")
    plt.plot(load[0], df_prices[df_prices.index == date]["Expected PW NL"], "bx", label= "Expected PW NL")
    plt.plot(load[0], df_prices[df_prices.index == date]["Actual PW NL"], "rx", label = "Actual PW NL")
    plt.title("Merit-Order {}".format(date.strftime("%Y-%m")))
    plt.xlabel("Capacity")
    plt.ylabel("Marginal Cost")
    plt.legend()
    plt.show()

def monthly_merit_order(NL_power_consumption, NL_power_exchanges, df_merit_order, df_prices, month, year):
    [plot_merit_order(NL_power_consumption, NL_power_exchanges, df_merit_order, df_prices, date) for date in df_prices.index if date.month == month and date.year == year]


print("hello")