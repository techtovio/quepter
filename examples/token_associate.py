import os
import sys
from dotenv import load_dotenv

from hiero_sdk_python import (
    Client,
    AccountId,
    PrivateKey,
    Network,
    TokenId,
    TokenAssociateTransaction,
)

load_dotenv()

def associate_token():
    network = Network(network='testnet')
    client = Client(network)

    recipient_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
    recipient_id_new = AccountId.from_string(os.getenv('RECIPIENT_ID'))
    recipient_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
    token_id = TokenId.from_string(os.getenv('Token_ID'))  # Update as needed

    client.set_operator(recipient_id, recipient_key)

    transaction = (
        TokenAssociateTransaction()
        .set_account_id(recipient_id_new)
        .add_token_id(token_id)
        .freeze_with(client)
        .sign(recipient_key)
    )

    try:
        receipt = transaction.execute(client)
        print("Token association successful.")
    except Exception as e:
        print(f"Token association failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    associate_token()
