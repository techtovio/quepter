import os
from django.core.management.base import BaseCommand
from club.models import Club
from hiero_sdk_python import (
    Client,
    Network,
    AccountId,
    PrivateKey,
    AccountCreateTransaction,
    TokenAssociateTransaction,
    ResponseCode
)
from dotenv import load_dotenv
load_dotenv()

class Command(BaseCommand):
    help = "Assign wallets and associate QPT tokens for existing clubs without wallets"

    def handle(self, *args, **kwargs):
        network = os.getenv('NETWORK')
        operator_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
        operator_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
        qpt_token_id = AccountId.from_string(os.getenv('Token_ID'))

        if not all([network, operator_id, operator_key, qpt_token_id]):
            self.stdout.write(self.style.ERROR("Missing required environment variables."))
            return

        client = Client(Network(network))
        client.set_operator(operator_id, operator_key)

        clubs_without_wallet = Club.objects.filter(app_id__isnull=True)

        if not clubs_without_wallet.exists():
            self.stdout.write(self.style.SUCCESS("✅ All clubs have wallets assigned."))
            return

        self.stdout.write(self.style.WARNING(f"Assigning wallets for {clubs_without_wallet.count()} clubs..."))

        for club in clubs_without_wallet:
            try:
                # ✅ Generate wallet keys
                private_key = PrivateKey.generate()
                public_key = private_key.public_key()

                # ✅ Create wallet
                transaction = (
                    AccountCreateTransaction()
                    .set_key(public_key)
                    .set_initial_balance(0)
                    .set_account_memo(f"Club {club.name} Wallet")
                    .freeze_with(client)
                )

                transaction.sign(operator_key)
                receipt = transaction.execute(client)

                if receipt.status != ResponseCode.SUCCESS:
                    raise ValueError(f"Failed to create wallet for {club.name}: {receipt.status.to_string()}")

                # ✅ Assign wallet details to club
                club.app_id = str(receipt.accountId)
                club.public_key = public_key.to_string_raw()
                club.encoded_private_key = club.encrypt_key(private_key.to_string_raw())
                club.save()

                # ✅ Associate QPT token
                transaction = (
                    TokenAssociateTransaction()
                    .set_account_id(club.app_id)
                    .add_token_id(qpt_token_id)
                    .freeze_with(client)
                    .sign(private_key)
                )

                receipt = transaction.execute(client)
                if receipt.status != ResponseCode.SUCCESS:
                    status_message = ResponseCode.get_name(receipt.status)
                    raise Exception(f"Token association failed with status: {status_message}")

                self.stdout.write(self.style.SUCCESS(f"✅ Wallet and QPT token associated for {club.name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error for {club.name}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Wallet assignment complete!")) 