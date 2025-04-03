import os
import sys
from dotenv import load_dotenv

from hiero_sdk_python import (
    Client,
    AccountId,
    PrivateKey,
    TopicCreateTransaction,
    Network,
)

load_dotenv()

def create_topic():
    network = Network(network='testnet')
    client = Client(network)

    operator_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
    operator_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))

    client.set_operator(operator_id, operator_key)

    transaction = (
        TopicCreateTransaction(
            memo="Healthra Insurance",
            admin_key=operator_key.public_key()
        )
        .freeze_with(client)
        .sign(operator_key)
    )

    try:
        receipt = transaction.execute(client)
        if receipt and receipt.topicId:
            print(f"Topic created with ID: {receipt.topicId}")
        else:
            print("Topic creation failed: Topic ID not returned in receipt.")
            sys.exit(1)
    except Exception as e:
        print(f"Topic creation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_topic()
