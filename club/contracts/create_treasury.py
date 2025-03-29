import requests

# Mirror Node URL (Testnet)
BASE_URL = "https://testnet.mirrornode.hedera.com/api/v1"

# New Account ID and Token ID
account_id = "0.0.5773854"  # Replace with the created account ID
token_id = "0.0.5774010"  # Replace with the created token ID

def get_account_balance(account_id):
    url = f"{BASE_URL}/accounts/{account_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        tokens = data.get("tokens", [])
        hbar_balance = data.get("balance", {}).get("balance", 0)

        print(f"✅ HBAR Balance: {hbar_balance} tinybars")
        for token in tokens:
            if token["token_id"] == token_id:
                balance = token["balance"]
                print(f"✅ QPT Balance: {balance}")
    else:
        print(f"Error: {response.status_code} - {response.json()}")

# Query balance
get_account_balance(account_id)
