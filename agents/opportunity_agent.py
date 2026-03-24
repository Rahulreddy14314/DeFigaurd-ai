"""Opportunity detection agent."""

from datetime import UTC, datetime


class OpportunityAgent:
    """Looks for momentum and token opportunity signals."""

    def __init__(self) -> None:
        self.name = "Opportunity Agent"

    def analyze(self, market_data: dict) -> dict:
        price_change_7d = float(market_data.get("price_change_7d", 0))
        momentum_score = float(market_data.get("momentum_score", 0))
        trending_score = float(market_data.get("trending_score", 0))

        if price_change_7d >= 12 and momentum_score >= 65:
            signal = "Bullish"
            score_impact = 18
            reason = (
                f"Momentum is strong with {price_change_7d:.2f}% 7d growth and "
                f"momentum score {momentum_score:.0f}."
            )
            alert_type = "Opportunity"
        elif price_change_7d >= 5 or trending_score >= 60:
            signal = "Watchlist"
            score_impact = 38
            reason = (
                f"Token is trending with score {trending_score:.0f}. "
                "Upside exists, but confirmation is still developing."
            )
            alert_type = "Opportunity"
        elif price_change_7d <= -10:
            signal = "Weak"
            score_impact = 70
            reason = "Momentum has reversed sharply, so opportunity conditions are weak right now."
            alert_type = "Warning"
        else:
            signal = "Neutral"
            score_impact = 48
            reason = "No compelling price momentum or trending catalyst is active."
            alert_type = "Warning"

        confidence = min(95, 58 + int(max(momentum_score, trending_score) * 0.35))
        return {
            "agent_name": self.name,
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "score_impact": score_impact,
            "type": alert_type,
            "timestamp": datetime.now(UTC).isoformat(),
        }
