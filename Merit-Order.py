import pandas as pd
from Models import Model
import matplotlib.pyplot as plt
import random

ng_fleet = {0.63:1631, 0.57:2265, 0.53:3804, 0.48:796, 0.39:561}
coal_fleet = {0.57:1084, 0.43:1777, 0.38:660}
fleet = {}
for ng_eff, coal_eff in zip(ng_fleet, coal_fleet):
    fleet["NG {}".format(ng_eff)] = ng_fleet[ng_eff]
    fleet["Coal {}".format(coal_eff)] = coal_fleet[coal_eff]
df = Model().get_data()
df_merit_order = {}
df_real_price = {}
df_expected_price = {}

for i in range(df.shape[0]):
    inputs = df.iloc[i]
    load_forecast = inputs.load
    ren_forecast = inputs.ren
    clean_ng_price_open = inputs.Clean_TTF
    clean_coal_price_open = inputs.Clean_coal
    ng_marginal_costs = {eff:clean_ng_price_open / eff for eff in ng_fleet.keys()}
    coal_marginal_costs = {eff:clean_coal_price_open / eff for eff in coal_fleet.keys()}
    ng_marginal_costs = sorted(ng_marginal_costs.items(), key=lambda x: x[1])
    coal_marginal_costs = sorted(coal_marginal_costs.items(), key=lambda x: x[1])
    residual_load = load_forecast - ren_forecast
    merit_order = {ren_forecast:0}
    count_ng = 0
    count_coal = 0
    while residual_load > 0:
        if count_ng < len(ng_marginal_costs) and count_coal < len(coal_marginal_costs):
            cheapest_ng = ng_marginal_costs[count_ng]
            cheapest_coal = coal_marginal_costs[count_coal]
            if cheapest_ng[1] <= cheapest_coal[1]:
                count_ng +=1
                merit_order[ng_fleet[cheapest_ng[0]]] = cheapest_ng[1]
                residual_load = residual_load - ng_fleet[cheapest_ng[0]]
            else:
                count_coal +=1
                merit_order[coal_fleet[cheapest_coal[0]]] = cheapest_coal[1]
                residual_load = residual_load - coal_fleet[cheapest_coal[0]]
        if count_ng >= len(ng_marginal_costs) and count_coal < len(coal_marginal_costs):
            cheapest_coal = coal_marginal_costs[count_coal]
            count_coal +=1
            merit_order[coal_fleet[cheapest_coal[0]]] = cheapest_coal[1]
            residual_load = residual_load - coal_fleet[cheapest_coal[0]]
        if count_ng < len(ng_marginal_costs) and count_coal >= len(coal_marginal_costs):
            cheapest_ng = ng_marginal_costs[count_ng]
            count_ng +=1
            merit_order[ng_fleet[cheapest_ng[0]]] = cheapest_ng[1]
            residual_load = residual_load - ng_fleet[cheapest_ng[0]]
        if count_ng >= len(ng_marginal_costs) and count_coal >= len(coal_marginal_costs):
            residual_load = 0

    df_merit_order[inputs.name] = merit_order
    df_real_price[inputs.name] = inputs.PW_NL_DAH
    df_expected_price[inputs.name] = list(merit_order.values())[-1]

df_real_price = pd.DataFrame.from_dict(df_real_price, orient="index")
df_real_price.columns = ["Actual PW NL"]
df_expected_price = pd.DataFrame.from_dict(df_expected_price, orient="index")
df_expected_price.columns = ["Expected PW NL"]
df_prices = pd.concat([df_expected_price, df_real_price], axis=1)
df_prices_peak = df_prices[(df_prices.index.hour >= 8) & (df_prices.index.hour < 20)]

def plot_merit_order(df, df_merit_order, df_prices, date):
    merit_order = df_merit_order[date]
    df_merit = pd.DataFrame.from_dict(merit_order, orient="index").reset_index()
    df_merit.columns = ["Capacity", "Marginal Cost"]
    df_merit = df_merit.set_index("Marginal Cost").cumsum()
    load = [df[df.index == date]["load"]] * df_merit.shape[0]
    plt.plot(list(df_merit["Capacity"]), list(df_merit.index), label="Supply")
    plt.plot(load, list(df_merit.index), label="Demand")
    plt.plot(load[0], df_prices[df_prices.index == date]["Expected PW NL"], "bx", label= "Expected PW NL")
    plt.plot(load[0], df_prices[df_prices.index == date]["Actual PW NL"], "rx", label = "Actual PW NL")
    plt.title("Merit-Order {}".format((date+pd.DateOffset(days=1)).strftime("%Y-%m-%d %H:%M")))
    plt.xlabel("Capacity")
    plt.ylabel("Marginal Cost")
    plt.legend()
    plt.show()

print("hello")
