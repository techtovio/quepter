from hedera import (
    AccountId,
    Client,
    PrivateKey,
    ContractExecuteTransaction,
    ContractFunctionParameters,
    Hbar
)
import os

# Load Hedera credentials from environment
HEDERA_ACCOUNT_ID = os.getenv('HEDERA_ACCOUNT_ID')
HEDERA_PRIVATE_KEY = os.getenv('HEDERA_PRIVATE_KEY')

# Initialize Hedera client
client = Client.forTestnet()
client.setOperator(AccountId.fromString(HEDERA_ACCOUNT_ID), PrivateKey.fromString(HEDERA_PRIVATE_KEY))
