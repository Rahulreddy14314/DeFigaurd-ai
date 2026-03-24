"""Whale tracker agent."""

from datetime import UTC, datetime


class WhaleTrackerAgent:
    """Flags whale transactions and market impact."""

    def __init__(self) -> None:
        self.name = "Whale Tracker"

    def analyze(self, market_data: dict) -> dict:
        transfers = int(market_data.get("large_transfers", 0))
        whale_direction = market_data.get("whale_direction", "neutral")
        wallet_concentration = float(market_data.get("wallet_concentration", 0))

        if whale_direction == "sell" and transfers >= 3:
            signal = "High"
            score_impact = min(95, 55 + transfers * 8)
            reason = (
                f"{transfers} large outbound whale transfers detected. "
                f"Concentration risk is {wallet_concentration:.1f}% and could amplify sell pressure."
            )
            alert_type = "Risk"
        elif whale_direction == "buy" and transfers >= 3:
            signal = "Bullish"
            score_impact = max(18, 45 - transfers * 5)
            reason = (
                f"{transfers} large inbound accumulation flows detected. "
                f"Whales appear to be supporting price levels."
            )
            alert_type = "Opportunity"
        elif transfers >= 2:
            signal = "Medium"
            score_impact = 58
            reason = "Large transfers are rising and may lead to short-term market instability."
            alert_type = "Warning"
        else:
            signal = "Low"
            score_impact = 32
            reason = "Whale activity is calm and no outsized transfers are dominating the market."
            alert_type = "Warning"

        confidence = min(96, 60 + transfers * 7)
        return {
            "agent_name": self.name,
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "score_impact": score_impact,
            "type": alert_type,
            "timestamp": datetime.now(UTC).isoformat(),
        }
