"""Smart contract guard agent."""

from datetime import UTC, datetime


class SmartContractGuardAgent:
    """Simulates contract anomaly detection."""

    def __init__(self) -> None:
        self.name = "Smart Contract Guard"

    def analyze(self, market_data: dict) -> dict:
        anomaly_score = int(market_data.get("contract_anomaly_score", 0))
        audit_status = market_data.get("audit_status", "unknown")
        suspicious_contract = bool(market_data.get("suspicious_contract", False))

        if suspicious_contract or anomaly_score >= 75:
            signal = "High"
            score_impact = 92
            reason = (
                f"Suspicious contract behavior detected with anomaly score {anomaly_score}/100. "
                f"Audit status: {audit_status}."
            )
        elif anomaly_score >= 45:
            signal = "Medium"
            score_impact = 68
            reason = (
                f"Contract risk signals are elevated. Monitoring score is {anomaly_score}/100 "
                f"and audit status is {audit_status}."
            )
        else:
            signal = "Low"
            score_impact = 24
            reason = f"No major contract anomalies detected. Audit status remains {audit_status}."

        confidence = min(98, 62 + int(anomaly_score * 0.35))
        return {
            "agent_name": self.name,
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "score_impact": score_impact,
            "type": "Risk" if score_impact >= 60 else "Warning",
            "timestamp": datetime.now(UTC).isoformat(),
        }
