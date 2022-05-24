import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import json

etherscan_key = "57GBAHGQSE3CMYNZQY81V1N32YJZNCCUNZ"
moralis_key = "pkhgpCPTU5AFiwXHrTwNCVXBIPfS3HZBLpOp1YOc8SOKxA8dUSVCEt9sg8hFjokU"

params = {
    'chain': 'eth',
}

headers = {
    'accept': 'application/json',
    'X-API-Key': moralis_key,
}


def etherscan_get(url):
    return requests.get(url, verify=True).text


def get_multi_balance(addr_list):
    response = etherscan_get(
        f"https://api.etherscan.io/api?module=account&action=balancemulti&address={addr_list}&tag=latest&apikey={etherscan_key}"
    )
    return json.loads(response)


def moralis_get(url, params=params):
    response = requests.get(url, params=params, headers=headers)
    return response.text, response.status_code


def get_block(interest_addr):
    response, _ = moralis_get(
        f"https://deep-index.moralis.io/api/v2/{interest_addr}")
    return json.loads(response)


def get_balance(interest_addr):
    response, _ = moralis_get(
        f"https://deep-index.moralis.io/api/v2/{interest_addr}/balance")
    return json.loads(response)


def get_nft_addr(contract_addr):
    response, _ = moralis_get(
        f"https://deep-index.moralis.io/api/v2/nft/{contract_addr}/owners")
    return json.loads(response)


def get_erc20_addr(interest_addr):
    response, _ = moralis_get(
        f"https://deep-index.moralis.io/api/v2/{interest_addr}/erc20")
    return json.loads(response)


def get_erc20_price(token_addr):
    response, status = moralis_get(
        f"https://deep-index.moralis.io/api/v2/erc20/{token_addr}/price")
    return json.loads(response), status


def get_nft_transfer_data(contract_addr):
    response, _ = moralis_get(
        f"https://deep-index.moralis.io/api/v2/nft/{contract_addr}/transfers")
    return json.loads(response)


def get_current_nft_holder(interest_addr, contract_addr):
    response, _ = moralis_get(
        f"https://deep-index.moralis.io/api/v2/{interest_addr}/nft/{contract_addr}"
    )
    return json.loads(response)


def get_address_nft(interest_addr):
    response, _ = moralis_get(
        f"https://deep-index.moralis.io/api/v2/{interest_addr}/nft")
    return json.loads(response)


def get_nft_lowest_price(contract_addr, price_params):
    response, status_code = moralis_get(
        f"https://deep-index.moralis.io/api/v2/nft/{contract_addr}/lowestprice",
        price_params)
    return json.loads(response), status_code


def BarChart(df, title):
    fig = px.bar(df,
                 x=df.keys()[0],
                 y=df.keys()[1],
                 title=title,
                 template="plotly_dark")
    fig.update_layout(autosize=False,
                      width=500,
                      height=500,
                      margin=dict(l=50, r=50, b=100, t=100, pad=4),
                      plot_bgcolor='rgba(0, 0, 0, 0)')

    return fig


def TableChart(df):
    fig = go.Figure(data=[
        go.Table(header=dict(values=df.columns),
                 cells=dict(values=df.values.T))
    ])

    return fig


def lineChart(df, title):
    fig = px.line(df,
                  x=df.keys()[0],
                  y=df.keys()[1],
                  title=title,
                  template="plotly_dark")
    fig.update_layout(autosize=False,
                      width=500,
                      height=500,
                      margin=dict(l=50, r=50, b=100, t=100, pad=4),
                      plot_bgcolor='rgba(0, 0, 0, 0)')
    return fig


def pieChart(df, title):
    fig = px.pie(df,
                 values=df.keys()[0],
                 names=df.keys()[1],
                 title=title,
                 template="plotly_dark")
    fig.update_layout(
        autosize=False,
        width=500,
        height=500,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        plot_bgcolor='rgba(0, 0, 0, 0)',
    )

    return fig


def get_wallet_nft_table(interest_addr, days=100):
    result_list = get_address_nft(interest_addr)["result"]

    nft_dict = {}
    for result in result_list:
        if result["name"] not in nft_dict:
            nft_dict[result["name"]] = [
                result["token_address"],
                int(result["amount"])
            ]
        else:
            nft_dict[result["name"]][1] += int(result["amount"])

    price_params = {'chain': 'eth', 'marketplace': 'opensea', 'days': days}

    for nft in nft_dict:
        price_result, status_code = get_nft_lowest_price(
            nft_dict[nft][0], price_params)
        if (status_code == 200):
            nft_dict[nft].append(int(price_result["price"]) / 10**18)
        else:
            nft_dict[nft].append(0)

    NFT_info_list = []
    for nft in nft_dict:
        new_dict = {}
        new_dict["name"] = nft
        new_dict["token_address"] = nft_dict[nft][0]
        new_dict["amount"] = nft_dict[nft][1]
        new_dict["price"] = nft_dict[nft][2]
        NFT_info_list.append(new_dict)

    df = pd.DataFrame(NFT_info_list)
    return TableChart(df)


def get_wallet_nft_plot(interest_addr, contract_addr):
    transaction = get_nft_transfer_data(contract_addr)["result"]
    transaction.reverse()

    result_list = get_current_nft_holder(interest_addr,
                                         contract_addr)["result"]
    current_num = len(result_list)

    balance = [0]
    time = []
    for response in transaction:
        if (response["to_address"] == interest_addr.lower()):
            balance.append(balance[-1] + int(response["amount"]))
            time.append(response['block_timestamp'])
        elif (response["from_address"] == interest_addr.lower()):
            balance.append(balance[-1] - int(response["amount"]))
            time.append(response['block_timestamp'])
    new_balance = [b + current_num for b in balance]
    new_balance = new_balance[1:]

    df = pd.DataFrame({
        "time": time,
        "balance": new_balance,
    })
    return lineChart(df, 'Balance of NFT')


def get_balance_plot(interest_addr):
    result_list = get_block(interest_addr)["result"]
    result_list.reverse()

    balance = [0]
    time = []
    for response in result_list:
        if (response["to_address"] == interest_addr.lower()):
            balance.append(balance[-1] + int(response["value"]) / 1e18)
            time.append(response['block_timestamp'])
        elif (response["from_address"] == interest_addr.lower()):
            balance.append(balance[-1] - int(response["value"]) / 1e18)
            time.append(response['block_timestamp'])

    curr_balance = int(get_balance(interest_addr)["balance"]) / 1e18
    init = curr_balance - balance[-1]
    new_balance = [b + init for b in balance]
    new_balance = new_balance[1:]

    df = pd.DataFrame({
        "time": time,
        "balance": new_balance,
    })
    return lineChart(df, 'Balance of account')


def get_wallet_erc20_plot(interest_addr):
    erc20_list = get_erc20_addr(interest_addr)

    erc20_price = []
    erc20_liquidity = []
    for res in erc20_list:
        price_dict, status = get_erc20_price(res["token_address"])
        if (status == 200):
            result = price_dict["nativePrice"]
            price = int(result["value"]) / 10**result["decimals"]
            erc20_price.append(price)
            erc20_liquidity.append(res)

    erc20_name = [erc20["name"] for erc20 in erc20_liquidity]
    erc20_num = [
        int(erc20["balance"]) / 10**erc20["decimals"]
        for erc20 in erc20_liquidity
    ]
    # erc20_addr = [erc20["token_address"] for erc20 in erc20_liquidity]
    erc20_value = [price * num for (price, num) in zip(erc20_price, erc20_num)]

    table_df = pd.DataFrame({
        "Erc20": erc20_name,
        "Erc20 Holding Num": erc20_num,
        "Erc20 Price": erc20_price
    })
    fig_table = TableChart(table_df)

    bar_df = pd.DataFrame({"Name": erc20_name, "Value": erc20_value})
    fig_bar = BarChart(bar_df, "Erc20 token value (Eth)")

    return fig_table, fig_bar


def get_balance_distribution(contract_addr,
                             Threshold_list=[0, 1, 5, 10, 50, 100, 10000]):
    holder_list = get_nft_addr(contract_addr)["result"]
    owner_list = []
    owner_result = []
    for result in holder_list:
        if (len(owner_list) < 20):
            owner_list.append(result["owner_of"])
        else:
            owner_addr = ",".join(owner_list)
            result = get_multi_balance(owner_addr)["result"]
            owner_result.extend(result)
            owner_list = []

    pd_owner_result = pd.DataFrame(owner_result)
    owner_value_count = pd_owner_result.value_counts(
        subset="account").to_frame().reset_index()
    owner_value_count.columns = ["account", "counts"]
    pd_unique_owner = pd_owner_result.drop_duplicates(ignore_index=True)

    pd_owner = pd_unique_owner.merge(owner_value_count, on="account")
    pd_owner["balance"] = pd_owner["balance"].astype(float) / 1e18

    stat_dict = []
    prev = 0

    for threshold in Threshold_list:
        stat_dict.append(np.sum(pd_owner["balance"] <= threshold) - prev)
        prev += stat_dict[-1]

    df = pd.DataFrame({"counts": stat_dict, "balance": Threshold_list})
    return pieChart(df, 'Distribution of Holder balance')


if __name__ == "__main__":
    interest_addr = "0x1919db36ca2fa2e15f9000fd9cdc2edcf863e685"
    contract_addr = "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"

    balance_plot = get_balance_plot(interest_addr)
    balance_plot.show()
    distribution_plot = get_balance_distribution(contract_addr)
    distribution_plot.show()
    erc20_table_plot, erc20_bar_plot = get_wallet_erc20_plot(interest_addr)
    erc20_table_plot.show()
    erc20_bar_plot.show()

    nft_table_plot = get_wallet_nft_table(interest_addr)
    nft_table_plot.show()
    
    erc20_line_plot = get_wallet_nft_plot(interest_addr, contract_addr)
    erc20_line_plot.show()