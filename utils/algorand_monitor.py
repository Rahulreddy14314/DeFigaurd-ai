"""Live Algorand wallet and protocol monitoring helpers."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

from algosdk import encoding
from algosdk.v2client import indexer


class AlgorandOnChainMonitor:
    """Fetches real wallet, transaction, and protocol activity from Algorand indexer."""

    DEFAULT_NETWORK = "testnet"
    DEFAULT_INDEXERS = {
        "testnet": "https://testnet-idx.algonode.cloud",
        "mainnet": "https://mainnet-idx.algonode.cloud",
    }
    TINYMAN_VALIDATOR_APP_IDS = {
        "testnet": {148607000},
        "mainnet": {1002541853},
    }

    def __init__(self, network: str | None = None) -> None:
        self.network = (network or os.getenv("ALGORAND_NETWORK", self.DEFAULT_NETWORK)).lower()
        self.indexer_client = indexer.IndexerClient(
            os.getenv("ALGORAND_INDEXER_TOKEN", ""),
            os.getenv("ALGORAND_INDEXER_SERVER", self.DEFAULT_INDEXERS.get(self.network, self.DEFAULT_INDEXERS["testnet"])),
        )

    @staticmethod
    def is_valid_address(address: str) -> bool:
        return bool(address) and encoding.is_valid_address(address)

    def get_wallet_snapshot(self, address: str) -> dict | None:
        if not self.is_valid_address(address):
            return None
        try:
            account_info = self.indexer_client.account_info(address)["account"]
            transactions = self.indexer_client.search_transactions_by_address(address=address, limit=25)["transactions"]
            assets = account_info.get("assets", [])[:8]
            wallet_assets = [
                {
                    "asset_id": asset.get("asset-id"),
                    "amount": asset.get("amount", 0),
                    "is_frozen": asset.get("is-frozen", False),
                }
                for asset in assets
            ]
            protocol_activity = self._protocol_activity(account_info, transactions)
            liquidation = self._liquidation_assessment(account_info, transactions, protocol_activity)

            return {
                "address": address,
                "algo_balance": round(account_info.get("amount", 0) / 1_000_000, 6),
                "min_balance": round(account_info.get("min-balance", 0) / 1_000_000, 6),
                "assets": wallet_assets,
                "apps_local_state": len(account_info.get("apps-local-state", [])),
                "recent_transactions": [
                    {
                        "id": txn.get("id"),
                        "round_time": txn.get("round-time"),
                        "tx_type": txn.get("tx-type"),
                        "sender": txn.get("sender"),
                    }
                    for txn in transactions[:10]
                ],
                "protocol_activity": protocol_activity,
                "liquidation_risk": liquidation,
            }
        except Exception:
            return None

    def _protocol_activity(self, account_info: dict, transactions: list[dict]) -> dict:
        folks_app_ids = self._read_env_app_ids("FOLKS_PROTOCOL_APP_IDS")
        pact_app_ids = self._read_env_app_ids("PACT_PROTOCOL_APP_IDS")
        tinyman_app_ids = self.TINYMAN_VALIDATOR_APP_IDS.get(self.network, set())

        local_app_ids = {app.get("id") for app in account_info.get("apps-local-state", [])}
        recent_app_ids = {
            txn.get("application-transaction", {}).get("application-id")
            for txn in transactions
            if txn.get("application-transaction")
        }

        return {
            "folks_finance": self._build_protocol_result("Folks Finance", folks_app_ids, local_app_ids, recent_app_ids),
            "tinyman": self._build_protocol_result("Tinyman", tinyman_app_ids, local_app_ids, recent_app_ids),
            "pact": self._build_protocol_result("Pact", pact_app_ids, local_app_ids, recent_app_ids),
        }

    def _liquidation_assessment(self, account_info: dict, transactions: list[dict], protocol_activity: dict) -> dict:
        folks = protocol_activity["folks_finance"]
        if folks["active_positions"] == 0:
            return {"level": "low", "reason": "No active Folks Finance position detected from configured protocol app IDs."}

        last_day = datetime.now(UTC) - timedelta(days=1)
        recent_app_calls = 0
        for txn in transactions:
            round_time = txn.get("round-time")
            if not round_time:
                continue
            tx_time = datetime.fromtimestamp(round_time, UTC)
            if tx_time >= last_day and txn.get("application-transaction"):
                recent_app_calls += 1

        level = "medium" if recent_app_calls > 0 else "warning"
        reason = (
            "Wallet is opted into Folks Finance app state, so borrowing exposure may exist. "
            "Review loan health directly in Folks if market stress increases."
        )
        return {
            "level": level,
            "reason": reason,
            "recent_app_calls_24h": recent_app_calls,
            "active_positions": folks["active_positions"],
        }

    @staticmethod
    def _read_env_app_ids(env_name: str) -> set[int]:
        raw = os.getenv(env_name, "").strip()
        if not raw:
            return set()
        return {int(value.strip()) for value in raw.split(",") if value.strip().isdigit()}

    @staticmethod
    def _build_protocol_result(name: str, app_ids: set[int], local_app_ids: set[int], recent_app_ids: set[int]) -> dict:
        matched_local = sorted(app_ids.intersection(local_app_ids))
        matched_recent = sorted(app_ids.intersection(recent_app_ids))
        return {
            "name": name,
            "configured_app_ids": sorted(app_ids),
            "active_positions": len(matched_local),
            "recent_interactions": len(matched_recent),
            "matched_local_app_ids": matched_local,
            "matched_recent_app_ids": matched_recent,
        }
