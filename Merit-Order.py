import pandas as pd
from Models import Model

ng_fleet = {0.63:1631, 0.57:2265, 0.53:3804, 0.48:796, 0.39:561}
coal_fleet = {0.57:1084, 0.43:1777, 0.38:660}
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
df = pd.concat([df_expected_price, df_real_price], axis=1)


print("hello")
