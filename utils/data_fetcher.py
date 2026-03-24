"""Market and wallet data helpers."""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

import requests

from utils.algorand_monitor import AlgorandOnChainMonitor


class DataFetcher:
    """Fetches market data with a deterministic offline fallback."""

    def __init__(self) -> None:
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 8
        self.onchain_monitor = AlgorandOnChainMonitor()
        self._fallback = {
            "algorand": {
                "current_price": 0.21,
                "price_change_24h": -2.8,
                "price_change_7d": 5.2,
                "volume_24h": 98000000,
                "market_cap": 1800000000,
                "liquidity_change_24h": -3.4,
                "volatility_index": 8.5,
                "large_transfers": 2,
                "whale_direction": "neutral",
                "wallet_concentration": 39,
                "contract_anomaly_score": 28,
                "suspicious_contract": False,
                "audit_status": "verified",
                "momentum_score": 61,
                "trending_score": 58,
            },
            "bitcoin": {
                "current_price": 68450.0,
                "price_change_24h": -6.2,
                "price_change_7d": 7.5,
                "volume_24h": 32000000000,
                "market_cap": 1300000000000,
                "liquidity_change_24h": -5.7,
                "volatility_index": 14.0,
                "large_transfers": 4,
                "whale_direction": "sell",
                "wallet_concentration": 45,
                "contract_anomaly_score": 22,
                "suspicious_contract": False,
                "audit_status": "verified",
                "momentum_score": 54,
                "trending_score": 72,
            },
            "ethereum": {
                "current_price": 3520.0,
                "price_change_24h": 4.4,
                "price_change_7d": 13.8,
                "volume_24h": 18000000000,
                "market_cap": 420000000000,
                "liquidity_change_24h": 2.1,
                "volatility_index": 9.4,
                "large_transfers": 3,
                "whale_direction": "buy",
                "wallet_concentration": 34,
                "contract_anomaly_score": 18,
                "suspicious_contract": False,
                "audit_status": "verified",
                "momentum_score": 74,
                "trending_score": 81,
            },
            "solana": {
                "current_price": 186.0,
                "price_change_24h": -9.7,
                "price_change_7d": -12.5,
                "volume_24h": 5100000000,
                "market_cap": 81000000000,
                "liquidity_change_24h": -11.4,
                "volatility_index": 18.2,
                "large_transfers": 5,
                "whale_direction": "sell",
                "wallet_concentration": 41,
                "contract_anomaly_score": 61,
                "suspicious_contract": False,
                "audit_status": "monitoring",
                "momentum_score": 31,
                "trending_score": 44,
            },
            "chainlink": {
                "current_price": 19.4,
                "price_change_24h": 2.2,
                "price_change_7d": 9.1,
                "volume_24h": 540000000,
                "market_cap": 11200000000,
                "liquidity_change_24h": 1.7,
                "volatility_index": 7.2,
                "large_transfers": 2,
                "whale_direction": "buy",
                "wallet_concentration": 32,
                "contract_anomaly_score": 15,
                "suspicious_contract": False,
                "audit_status": "verified",
                "momentum_score": 69,
                "trending_score": 63,
            },
        }

    def get_market_snapshot(self, asset_id: str, wallet_address: str) -> dict:
        live_data = self._fetch_live_market_data(asset_id)
        price_history = self._build_price_history(asset_id, live_data["current_price"])
        wallet = self._build_wallet_overview(wallet_address, asset_id, live_data["current_price"])
        onchain_wallet = self.onchain_monitor.get_wallet_snapshot(wallet_address)
        protocol_activity = onchain_wallet["protocol_activity"] if onchain_wallet else {}
        liquidation_risk = onchain_wallet["liquidation_risk"] if onchain_wallet else {"level": "low", "reason": "No Algorand wallet sync active."}
        snapshot = {
            **live_data,
            "asset_id": asset_id,
            "wallet": wallet,
            "price_history": price_history,
            "onchain_wallet": onchain_wallet,
            "protocol_activity": protocol_activity,
            "liquidation_risk": liquidation_risk,
            "baseline_risk_score": int(
                min(100, max(15, abs(live_data["price_change_24h"]) * 5 + max(0, -live_data["liquidity_change_24h"]) * 2))
            ),
        }
        return snapshot

    def _fetch_live_market_data(self, asset_id: str) -> dict:
        fallback = dict(self._fallback.get(asset_id, self._fallback["algorand"]))
        url = f"{self.base_url}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": asset_id,
            "price_change_percentage": "7d",
        }
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if not data:
                return fallback
            market = data[0]
            fallback["current_price"] = float(market.get("current_price", fallback["current_price"]))
            fallback["price_change_24h"] = float(
                market.get("price_change_percentage_24h", fallback["price_change_24h"])
            )
            fallback["price_change_7d"] = float(
                market.get("price_change_percentage_7d_in_currency", fallback["price_change_7d"])
            )
            fallback["market_cap"] = float(market.get("market_cap", fallback["market_cap"]))
            fallback["volume_24h"] = float(market.get("total_volume", fallback["volume_24h"]))
            fallback["volatility_index"] = round(abs(fallback["price_change_24h"]) * 1.7, 2)
            fallback["liquidity_change_24h"] = round(fallback["price_change_24h"] * 0.8, 2)
            return fallback
        except Exception:
            return fallback

    def _build_price_history(self, asset_id: str, current_price: float) -> list[dict]:
        random.seed(asset_id)
        points = []
        price = current_price * 0.92
        start = datetime.now(UTC) - timedelta(days=7)
        for hour in range(42):
            drift = random.uniform(-0.025, 0.03)
            price = max(0.0001, price * (1 + drift))
            points.append(
                {
                    "timestamp": (start + timedelta(hours=4 * hour)).isoformat(),
                    "price": round(price, 4),
                }
            )
        points[-1]["price"] = round(current_price, 4)
        return points

    def _build_wallet_overview(self, wallet_address: str, asset_id: str, current_price: float) -> dict:
        onchain_wallet = self.onchain_monitor.get_wallet_snapshot(wallet_address)
        if onchain_wallet:
            holdings = [
                {
                    "token": "ALGO",
                    "balance": onchain_wallet["algo_balance"],
                    "value_usd": round(onchain_wallet["algo_balance"] * current_price, 2),
                }
            ]
            for asset in onchain_wallet["assets"][:5]:
                holdings.append(
                    {
                        "token": f"ASA-{asset['asset_id']}",
                        "balance": asset["amount"],
                        "value_usd": 0.0,
                    }
                )
            portfolio_value = sum(item["value_usd"] for item in holdings)
            return {
                "address": wallet_address,
                "portfolio_value_usd": round(portfolio_value, 2),
                "daily_pnl_percent": round((current_price % 7) - 3, 2),
                "holdings": holdings,
                "is_live_sync": True,
                "apps_local_state": onchain_wallet["apps_local_state"],
            }

        units = 1250 if asset_id == "algorand" else 2.4 if asset_id == "bitcoin" else 12.8
        holdings = [
            {
                "token": asset_id.upper(),
                "balance": round(units, 4),
                "value_usd": round(units * current_price, 2),
            },
            {
                "token": "USDC",
                "balance": 1850.0,
                "value_usd": 1850.0,
            },
        ]
        portfolio_value = sum(item["value_usd"] for item in holdings)
        return {
            "address": wallet_address,
            "portfolio_value_usd": round(portfolio_value, 2),
            "daily_pnl_percent": round((current_price % 7) - 3, 2),
            "holdings": holdings,
            "is_live_sync": False,
        }
