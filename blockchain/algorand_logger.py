"""Algorand alert logger backed by AlgoKit TestNet submission."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from algosdk import account
from algokit_utils import AlgoAmount, AlgorandClient, PaymentParams, SigningAccount, TestNetDispenserApiClient


class AlgorandLogger:
    """Logs DeFiGuard alerts using AlgoKit and real Algorand transactions by default."""

    def __init__(self, log_path: str = "logs/blockchain_alerts.json") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.account_cache_path = self.log_path.parent / "algokit_runtime_account.json"
        self.network = os.getenv("ALGORAND_NETWORK", "testnet").lower()
        self.algorand_client: AlgorandClient | None = None
        self.sender_address: str | None = None

    def log_alert(self, alert: dict, wallet_address: str = "ALGO-DEMO-WALLET-01") -> dict:
        if self.algorand_client is None:
            self.algorand_client = self._build_algokit_client()
        if self.sender_address is None:
            self.sender_address = self._resolve_sender_address()
        payload = {
            "wallet_address": wallet_address,
            "message": alert["title"],
            "risk_score": alert["risk_score"],
            "decision": alert["decision"],
            "timestamp": alert["timestamp"],
            "details": alert["explanation"],
        }
        receipt = self._submit_algokit_transaction(payload)
        self._append_receipt(receipt)
        return receipt

    def _build_algokit_client(self) -> AlgorandClient:
        if self.network == "mainnet":
            client = AlgorandClient.mainnet()
        elif self.network == "localnet":
            client = AlgorandClient.default_localnet()
        else:
            client = AlgorandClient.testnet()

        signer = self._load_or_create_signer(client)
        client.set_signer_from_account(signer)
        return client

    def _load_or_create_signer(self, client: AlgorandClient) -> SigningAccount:
        private_key = os.getenv("ALGORAND_PRIVATE_KEY")
        sender_address = os.getenv("ALGORAND_SENDER_ADDRESS")
        if private_key:
            resolved_address = sender_address or account.address_from_private_key(private_key)
            return SigningAccount(private_key=private_key, address=resolved_address)

        if self.account_cache_path.exists():
            cached = json.loads(self.account_cache_path.read_text(encoding="utf-8"))
            return SigningAccount(private_key=cached["private_key"], address=cached["address"])

        signer = client.account.random()
        self.account_cache_path.write_text(
            json.dumps({"private_key": signer.private_key, "address": signer.address}, indent=2),
            encoding="utf-8",
        )

        if self.network == "testnet":
            dispenser = TestNetDispenserApiClient(auth_token=os.getenv("ALGOKIT_DISPENSER_TOKEN"))
            client.account.ensure_funded_from_testnet_dispenser_api(
                signer,
                dispenser,
                min_spending_balance=AlgoAmount.from_algo(0.2),
                min_funding_increment=AlgoAmount.from_algo(1),
            )
        return signer

    def _resolve_sender_address(self) -> str:
        configured = os.getenv("ALGORAND_SENDER_ADDRESS")
        if configured:
            return configured
        if self.account_cache_path.exists():
            cached = json.loads(self.account_cache_path.read_text(encoding="utf-8"))
            return cached["address"]
        private_key = os.getenv("ALGORAND_PRIVATE_KEY")
        if private_key:
            return account.address_from_private_key(private_key)
        raise RuntimeError("Unable to resolve Algorand sender address for alert logging.")

    def _submit_algokit_transaction(self, payload: dict) -> dict:
        assert self.algorand_client is not None
        assert self.sender_address is not None
        note = self._build_note(payload).encode("utf-8")
        result = self.algorand_client.send.payment(
            PaymentParams(
                sender=self.sender_address,
                receiver=self.sender_address,
                amount=AlgoAmount.from_micro_algo(0),
                note=note,
            )
        )
        message_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        return {
            "transaction_id": result.tx_id or (result.tx_ids[0] if result.tx_ids else "UNKNOWN"),
            "message_hash": message_hash,
            "network": self.network,
            "timestamp": datetime.now(UTC).isoformat(),
            "payload": payload,
            "status": "confirmed",
            "note": note.decode("utf-8"),
            "mode": "algokit-live",
            "sender_address": self.sender_address,
        }

    def _append_receipt(self, receipt: dict) -> None:
        receipts = []
        if self.log_path.exists():
            try:
                receipts = json.loads(self.log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                receipts = []
        receipts.append(receipt)
        self.log_path.write_text(json.dumps(receipts, indent=2), encoding="utf-8")

    def _build_note(self, payload: dict) -> str:
        compact = {
            "message": payload["message"],
            "risk_score": payload["risk_score"],
            "timestamp": payload["timestamp"],
        }
        return json.dumps(compact)

    def list_receipts(self) -> list[dict]:
        if not self.log_path.exists():
            return []
        try:
            return json.loads(self.log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
