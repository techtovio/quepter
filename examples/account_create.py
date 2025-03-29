import os
import sys
from dotenv import load_dotenv

from hiero_sdk_python import (
    Client,
    Network,
    AccountId,
    PrivateKey,
    AccountCreateTransaction,
    ResponseCode,
)

load_dotenv()

def create_new_account():
    network = Network(network='testnet')
    client = Client(network)

    operator_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
    operator_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
    client.set_operator(operator_id, operator_key)

    new_account_private_key = PrivateKey.generate()
    new_account_public_key = new_account_private_key.public_key()

    transaction = (
        AccountCreateTransaction()
        .set_key(new_account_public_key)
        .set_initial_balance(100000000)  # 1 HBAR in tinybars
        .set_account_memo("My new account")
        .freeze_with(client)
    )

    transaction.sign(operator_key)

    try:
        receipt = transaction.execute(client)
        print(f"Transaction status: {receipt.status}")

        if receipt.status != ResponseCode.SUCCESS:
            status_message = ResponseCode.get_name(receipt.status)
            raise Exception(f"Transaction failed with status: {status_message}")

        new_account_id = receipt.accountId
        if new_account_id is not None:
            print(f"Account creation successful. New Account ID: {new_account_id}")
            print(f"New Account Private Key: {new_account_private_key.to_string()}")
            print(f"New Account Public Key: {new_account_public_key.to_string()}")
        else:
            raise Exception("AccountID not found in receipt. Account may not have been created.")

    except Exception as e:
        print(f"Account creation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_new_account()
