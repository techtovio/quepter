import os
import sys
from dotenv import load_dotenv
from hiero_sdk_python.client.network import Network
from hiero_sdk_python.client.client import Client
from hiero_sdk_python.account.account_id import AccountId
from hiero_sdk_python.account.account_create_transaction import AccountCreateTransaction
from hiero_sdk_python.crypto.private_key import PrivateKey
from hiero_sdk_python.tokens.token_create_transaction import TokenCreateTransaction
from hiero_sdk_python.tokens.token_associate_transaction import TokenAssociateTransaction
from hiero_sdk_python.tokens.token_dissociate_transaction import TokenDissociateTransaction
from hiero_sdk_python.tokens.token_mint_transaction import TokenMintTransaction
from hiero_sdk_python.transaction.transfer_transaction import TransferTransaction
from hiero_sdk_python.tokens.token_delete_transaction import TokenDeleteTransaction
from hiero_sdk_python.tokens.token_freeze_transaction import TokenFreezeTransaction
from hiero_sdk_python.response_code import ResponseCode
from hiero_sdk_python.consensus.topic_create_transaction import TopicCreateTransaction
from hiero_sdk_python.consensus.topic_message_submit_transaction import TopicMessageSubmitTransaction
from hiero_sdk_python.consensus.topic_update_transaction import TopicUpdateTransaction
from hiero_sdk_python.consensus.topic_delete_transaction import TopicDeleteTransaction
from hiero_sdk_python.consensus.topic_id import TopicId
from hiero_sdk_python.query.topic_info_query import TopicInfoQuery
from hiero_sdk_python.query.account_balance_query import CryptoGetAccountBalanceQuery

load_dotenv()


def load_operator_credentials():
    """Load operator credentials from environment variables."""
    try:
        operator_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
        operator_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
    except Exception as e:
        print(f"Error parsing operator credentials: {e}")
        sys.exit(1)
    return operator_id, operator_key


def create_new_account(client, initial_balance=100000000):
    new_account_private_key = PrivateKey.generate()
    new_account_public_key = new_account_private_key.public_key()

    transaction = AccountCreateTransaction(
        key=new_account_public_key,
        initial_balance=initial_balance,
        memo="Recipient Account"
    )
    transaction.freeze_with(client)
    transaction.sign(client.operator_private_key)

    try:
        receipt = transaction.execute(client)
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

    return new_account_id, new_account_private_key


def query_balance(client, account_id):
    balance = CryptoGetAccountBalanceQuery(account_id=account_id).execute(client)
    print(f"Account {account_id} balance: {balance.hbars}")
    return balance

def create_token(client, operator_id, admin_key, supply_key, freeze_key):
    transaction = TokenCreateTransaction(
        token_name="Quepter",
        token_symbol="QPT",
        decimals=2,
        initial_supply=100_000_000,
        treasury_account_id=operator_id,
        admin_key=admin_key,
        supply_key=supply_key,
        freeze_key=freeze_key
    )
    transaction.freeze_with(client)
    transaction.sign(client.operator_private_key)
    transaction.sign(admin_key)

    try:
        receipt = transaction.execute(client)
    except Exception as e:
        print(f"Token creation failed: {str(e)}")
        sys.exit(1)

    if not receipt.tokenId:
        print("Token creation failed: Token ID not returned in receipt.")
        sys.exit(1)

    token_id = receipt.tokenId
    print(f"Token creation successful. Token ID: {token_id}")
    return token_id


def main():
    operator_id, operator_key = load_operator_credentials()
    admin_key = PrivateKey.generate()
    supply_key = PrivateKey.generate()
    freeze_key = PrivateKey.generate()
    print(f'ADMIN_KEY={admin_key}  -  SUPPLY_KEY={supply_key}   -   FREEZE_KEY={freeze_key}')
    network_type = os.getenv('NETWORK')
    network = Network(network=network_type)
    client = Client(network)
    client.set_operator(operator_id, operator_key)

    token_id_1 = create_token(client, operator_id, admin_key, supply_key, freeze_key)

if __name__ == "__main__":
    main()