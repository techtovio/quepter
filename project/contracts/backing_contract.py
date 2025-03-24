from .hedera_client import client
from hedera import ContractExecuteTransaction, ContractFunctionParameters, Hbar

BACKING_CONTRACT_ID = os.getenv('BACKING_CONTRACT_ID')

def back_project(backer_address: str, project_address: str, amount: float):
    try:
        transaction = (
            ContractExecuteTransaction()
            .setContractId(BACKING_CONTRACT_ID)
            .setGas(100_000)
            .setFunction(
                "backProject",
                ContractFunctionParameters()
                .addAddress(backer_address)
                .addAddress(project_address)
                .addUint256(int(amount * 10**8))
            )
            .setPayableAmount(Hbar.fromTinybars(int(amount * 10**8)))
        )
        
        response = transaction.execute(client)
        receipt = response.getReceipt(client)
        return receipt.status.toString()

    except Exception as e:
        raise Exception(f"Backing failed: {str(e)}")
