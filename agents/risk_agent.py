"""Risk analyzer agent."""

from datetime import UTC, datetime


class RiskAnalyzerAgent:
    """Detects volatility spikes and downside risk."""

    def __init__(self) -> None:
        self.name = "Risk Analyzer"

    def analyze(self, market_data: dict) -> dict:
        price_change_24h = float(market_data.get("price_change_24h", 0))
        volatility_index = float(market_data.get("volatility_index", abs(price_change_24h)))
        liquidity_change = float(market_data.get("liquidity_change_24h", 0))
        liquidation_risk = market_data.get("liquidation_risk", {})

        risk_score = min(100, max(5, int(volatility_index * 4 + max(0, -liquidity_change) * 1.8)))
        if liquidation_risk.get("level") in {"medium", "warning"}:
            risk_score = min(100, risk_score + 12)

        if liquidation_risk.get("level") in {"medium", "warning"}:
            signal = "High"
            reason = f"{liquidation_risk.get('reason')} Live protocol stress should be reviewed immediately."
        elif price_change_24h <= -9 or volatility_index >= 18:
            signal = "High"
            reason = (
                f"Severe downside pressure detected with {price_change_24h:.2f}% 24h change "
                f"and volatility index {volatility_index:.1f}."
            )
        elif price_change_24h <= -4 or volatility_index >= 10:
            signal = "Medium"
            reason = (
                f"Elevated volatility detected. Price moved {price_change_24h:.2f}% in 24h "
                f"while liquidity shifted {liquidity_change:.2f}%."
            )
        else:
            signal = "Low"
            reason = "Price action is relatively stable and volatility remains contained."

        confidence = min(97, 55 + int(volatility_index * 2))
        return {
            "agent_name": self.name,
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "score_impact": risk_score,
            "type": "Risk",
            "timestamp": datetime.now(UTC).isoformat(),
        }
