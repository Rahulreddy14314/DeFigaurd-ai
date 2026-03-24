"""Simulation and alert storage utilities."""

from __future__ import annotations

import random
from datetime import UTC, datetime


class MarketSimulator:
    """Creates demo events for the hackathon flow."""

    def __init__(self) -> None:
        self.events = [
            {
                "label": "Whale Sell-Off",
                "price_impact_percent": -12,
                "summary": "A cluster of large wallets sent tokens to exchanges.",
                "updates": {
                    "price_change_24h": -12,
                    "liquidity_change_24h": -10,
                    "volatility_index": 21,
                    "large_transfers": 6,
                    "whale_direction": "sell",
                    "contract_anomaly_score": 58,
                    "momentum_score": 24,
                },
            },
            {
                "label": "Price Drop Cascade",
                "price_impact_percent": -18,
                "summary": "Liquidation pressure spread across lending pools.",
                "updates": {
                    "price_change_24h": -18,
                    "liquidity_change_24h": -16,
                    "volatility_index": 28,
                    "large_transfers": 4,
                    "whale_direction": "sell",
                    "contract_anomaly_score": 72,
                    "suspicious_contract": True,
                    "momentum_score": 20,
                },
            },
            {
                "label": "Opportunity Rally",
                "price_impact_percent": 11,
                "summary": "Momentum and social trend signals turned decisively positive.",
                "updates": {
                    "price_change_24h": 11,
                    "price_change_7d": 19,
                    "liquidity_change_24h": 8,
                    "volatility_index": 9,
                    "large_transfers": 3,
                    "whale_direction": "buy",
                    "contract_anomaly_score": 18,
                    "momentum_score": 82,
                    "trending_score": 88,
                },
            },
        ]

    def simulate_market_shock(self, snapshot: dict) -> tuple[dict, dict]:
        event = random.choice(self.events)
        updated = dict(snapshot)
        updated.update(event["updates"])
        updated["current_price"] = round(
            snapshot["current_price"] * (1 + event["price_impact_percent"] / 100),
            4,
        )
        updated["price_history"] = snapshot["price_history"][:-1] + [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "price": updated["current_price"],
            }
        ]
        return updated, {
            "label": event["label"],
            "summary": event["summary"],
            "price_impact_percent": event["price_impact_percent"],
            "timestamp": datetime.now(UTC).isoformat(),
        }


class AlertStore:
    """Stores alerts in memory for the Streamlit session."""

    def __init__(self) -> None:
        self._alerts: list[dict] = []

    def create_alert(self, decision: dict) -> dict:
        alert = dict(decision["alerts"][0])
        self._alerts.insert(0, alert)
        return alert

    def list_alerts(self) -> list[dict]:
        return list(self._alerts)
