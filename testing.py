import pandas as pd
import requests
import json

convert = (lambda balance: float(balance) / 1e18)

""" To get All Owners of the NFT. """
headers = {
    'accept': 'application/json',
    'X-API-Key': 'pkhgpCPTU5AFiwXHrTwNCVXBIPfS3HZBLpOp1YOc8SOKxA8dUSVCEt9sg8hFjokU',
}

params = {
    'chain': 'eth',
    'format': 'decimal',
}

response = requests.get('https://deep-index.moralis.io/api/v2/nft/0x90cfCE78f5ED32f9490fd265D16c77a8b5320Bd4/owners', headers=headers, params=params)

with open('Holder_address.json', 'w') as outfile:
    outfile.write(response.text)

""" Get the Balance in the wallet of each owners """
headers = {
    'accept': 'application/json',
    'X-API-Key': 'pkhgpCPTU5AFiwXHrTwNCVXBIPfS3HZBLpOp1YOc8SOKxA8dUSVCEt9sg8hFjokU',
}

params = {
    'chain': 'eth',
}

owner_list = []
owner_result = pd.DataFrame(columns=["account", "balance"])
for result in json.loads(response.text)["result"]:
    if(len(owner_list)<20):
        owner_list.append(result["owner_of"])
    else:
        owner_addr = ",".join(owner_list)
        url = f"https://api.etherscan.io/api?module=account&action=balancemulti&address={owner_addr}&tag=latest&apikey=57GBAHGQSE3CMYNZQY81V1N32YJZNCCUNZ"
        response = requests.get(url, verify=True)
        result = json.loads(response.text)["result"]
        result = pd.DataFrame(result, columns=["account", "balance"])
        owner_result = pd.concat([owner_result, result], ignore_index=True)
        owner_list = []

owner_result["Hold"] = owner_result.value_counts().values
print(owner_result)
# owner_result["balance"] = float(owner_result["balance"])/ 1e18
# with open('holders_balance.json', 'w') as outfile:
    # outfile.write(json.dumps(sort_result))

""" Get all token balance of one account """
# for result in json.loads(response.text)["result"]:
#     print(result["token_id"])
#     owner_addr = result["owner_of"]
#     url = f"https://api.ethplorer.io/getAddressInfo/{owner_addr}?apiKey=EK-2MKYK-SE7nJY3-W5LCS"
#     response = requests.get(url, verify=True)
#     with open('Owner Token balance.json', 'a') as outfile:
#         outfile.write(response.text)
    # print(response.text)
    
# url = f"https://api.ethplorer.io/getAddressInfo/{addr}?apiKey=freekey"

# response = requests.get(url, verify=True)
# print(response.text["result"])

# https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress=0x9e1c80662d04b2c94dce0a46e5b1f5b48ce97e26&address=0x95ebe7d8089d4c8bcee0bde19c9e867cbeeefd00&tag=latest&apikey=57GBAHGQSE3CMYNZQY81V1N32YJZNCCUNZ
# url = "https://api.etherscan.io/api?module=account&action=balancemulti&address=0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a,0x63a9975ba31b0b9626b34300f7f627147df1f526,0x198ef1ec325a96cc354c7266a038be8b5c558f67&tag=latest&apikey=57GBAHGQSE3CMYNZQY81V1N32YJZNCCUNZ"