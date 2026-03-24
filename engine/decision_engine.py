"""Decision engine for combining agent outputs."""

from datetime import UTC, datetime


class DecisionEngine:
    """Combines agent outputs into a single explainable decision."""

    def evaluate(self, agent_results: list[dict], market_data: dict, asset_id: str) -> dict:
        if not agent_results:
            return self._empty_result(asset_id)

        risk_score = int(
            round(sum(result["score_impact"] for result in agent_results) / len(agent_results))
        )
        confidence = int(
            round(sum(result["confidence"] for result in agent_results) / len(agent_results))
        )
        explanation_points = [result["reason"] for result in agent_results]

        if risk_score >= 72:
            decision = "SELL"
            alert_type = "Risk"
            summary = "Multiple agents agree that downside risk is elevated and defensive action is recommended."
        elif risk_score <= 34:
            decision = "BUY"
            alert_type = "Opportunity"
            summary = "Risk remains controlled while momentum signals suggest a favorable entry setup."
        else:
            decision = "HOLD"
            alert_type = "Warning"
            summary = "Signals are mixed, so the safest action is to monitor conditions and wait for confirmation."

        alert = {
            "type": alert_type,
            "title": f"{asset_id.upper()} {decision} signal",
            "risk_score": risk_score,
            "decision": decision,
            "timestamp": datetime.now(UTC).isoformat(),
            "explanation": explanation_points,
        }

        return {
            "asset": asset_id,
            "risk_score": risk_score,
            "decision": decision,
            "confidence": confidence,
            "summary": summary,
            "explanation_points": explanation_points,
            "alerts": [alert],
            "market_context": {
                "price": market_data.get("current_price"),
                "price_change_24h": market_data.get("price_change_24h"),
                "liquidity_change_24h": market_data.get("liquidity_change_24h"),
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _empty_result(self, asset_id: str) -> dict:
        return {
            "asset": asset_id,
            "risk_score": 50,
            "decision": "HOLD",
            "confidence": 0,
            "summary": "No active agents were enabled, so no reliable action can be recommended.",
            "explanation_points": ["Enable at least one agent to generate analysis."],
            "alerts": [],
            "timestamp": datetime.now(UTC).isoformat(),
        }
