"""Streamlit MVP for DeFiGuard AI."""

from datetime import UTC, datetime

import pandas as pd
import streamlit as st

from agents.contract_agent import SmartContractGuardAgent
from agents.opportunity_agent import OpportunityAgent
from agents.risk_agent import RiskAnalyzerAgent
from agents.whale_agent import WhaleTrackerAgent
from blockchain.algorand_logger import AlgorandLogger
from blockchain.pera_trade import PeraTradeHelper
from engine.decision_engine import DecisionEngine
from generate_pitch import generate_pitch_summary
from utils.data_fetcher import DataFetcher
from utils.simulator import AlertStore, MarketSimulator


st.set_page_config(
    page_title="DeFiGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        :root {
            --bg-deep: #07111b;
            --bg-panel: rgba(10, 18, 31, 0.82);
            --bg-panel-soft: rgba(15, 23, 42, 0.68);
            --text-main: #e6eef8;
            --text-soft: #97a9c3;
            --line-soft: rgba(148, 163, 184, 0.16);
            --accent-cyan: #38bdf8;
            --accent-blue: #60a5fa;
            --safe: #22c55e;
            --safe-soft: rgba(34, 197, 94, 0.18);
            --warn: #f59e0b;
            --warn-soft: rgba(245, 158, 11, 0.18);
            --risk: #ef4444;
            --risk-soft: rgba(239, 68, 68, 0.18);
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(14, 165, 233, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(245, 158, 11, 0.10), transparent 24%),
                linear-gradient(160deg, #06131f 0%, #0b1726 45%, #101a2c 100%);
            color: var(--text-main);
        }
        .stApp, .stMarkdown, .stText, p, li, label, span, div {
            color: var(--text-main);
        }
        a {
            color: #8bdcff !important;
        }
        code {
            color: #f8fbff !important;
            background: rgba(15, 23, 42, 0.95) !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08111c 0%, #0d1b2a 100%);
            border-right: 1px solid var(--line-soft);
        }
        [data-testid="stSidebar"] * {
            color: var(--text-main);
        }
        h1, h2, h3, h4 {
            color: #f5f9ff;
            letter-spacing: -0.02em;
        }
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(12, 21, 36, 0.95), rgba(9, 15, 26, 0.92));
            border: 1px solid var(--line-soft);
            border-radius: 18px;
            padding: 0.85rem 1rem;
            box-shadow: 0 12px 28px rgba(2, 6, 23, 0.2);
        }
        [data-testid="stMetricLabel"] {
            color: var(--text-soft);
        }
        [data-testid="stMetricValue"] {
            color: #f8fbff;
        }
        [data-testid="stMetricDelta"] {
            color: #d8e7f7;
        }
        .stButton > button {
            border-radius: 14px;
            border: 1px solid rgba(56, 189, 248, 0.24);
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(13, 30, 46, 0.95));
            color: #ecf7ff;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 12px 24px rgba(2, 6, 23, 0.2);
        }
        .stButton > button:hover {
            border-color: rgba(56, 189, 248, 0.42);
            transform: translateY(-1px);
            box-shadow: 0 16px 28px rgba(2, 6, 23, 0.28);
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0ea5e9, #2563eb);
            border-color: rgba(125, 211, 252, 0.4);
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background: rgba(9, 16, 27, 0.88);
            color: #f8fbff !important;
            border: 1px solid var(--line-soft);
            border-radius: 12px;
        }
        .stTextInput input::placeholder {
            color: #9db1cb !important;
        }
        .stSelectbox [data-baseweb="select"] * {
            color: #f8fbff !important;
        }
        .stSelectbox [data-baseweb="select"] svg {
            fill: #b8d7f2 !important;
        }
        .stNumberInput input {
            color: #f8fbff !important;
            background: rgba(9, 16, 27, 0.88) !important;
        }
        .stRadio label, .stRadio div[role="radiogroup"] label, .stToggle label {
            color: #edf6ff !important;
        }
        .stCaption, [data-testid="stCaptionContainer"] {
            color: #a7bdd8 !important;
        }
        [data-testid="stMarkdownContainer"] p {
            color: var(--text-main);
        }
        [data-testid="stDataFrame"] {
            border: 1px solid var(--line-soft);
            border-radius: 18px;
            overflow: hidden;
        }
        [data-testid="stDataFrame"] * {
            color: #eef6ff !important;
        }
        [data-testid="stDataFrame"] [role="columnheader"] * {
            color: #8fd8ff !important;
            font-weight: 700 !important;
        }
        [data-testid="stAlertContainer"] * {
            color: #eef6ff !important;
        }
        .stSuccess, .stWarning, .stInfo, .stError {
            border-radius: 14px;
        }
        .hero {
            padding: 28px;
            border-radius: 24px;
            border: 1px solid rgba(125, 211, 252, 0.16);
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.18), transparent 30%),
                linear-gradient(135deg, rgba(12, 24, 40, 0.96), rgba(10, 16, 28, 0.92));
            box-shadow: 0 24px 52px rgba(2, 6, 23, 0.34);
            margin-bottom: 1rem;
        }
        .glass-card {
            padding: 18px;
            border-radius: 18px;
            border: 1px solid var(--line-soft);
            background: var(--bg-panel);
            box-shadow: 0 12px 30px rgba(2, 6, 23, 0.22);
        }
        .metric-safe {
            border-left: 5px solid var(--safe);
            background:
                linear-gradient(135deg, var(--safe-soft), rgba(10, 18, 31, 0.94)),
                var(--bg-panel);
        }
        .metric-warn {
            border-left: 5px solid var(--warn);
            background:
                linear-gradient(135deg, var(--warn-soft), rgba(10, 18, 31, 0.94)),
                var(--bg-panel);
        }
        .metric-risk {
            border-left: 5px solid var(--risk);
            background:
                linear-gradient(135deg, var(--risk-soft), rgba(10, 18, 31, 0.94)),
                var(--bg-panel);
        }
        .agent-safe {
            border-top: 3px solid var(--safe);
            background: linear-gradient(180deg, var(--safe-soft), rgba(10, 18, 31, 0.94));
        }
        .agent-warn {
            border-top: 3px solid var(--warn);
            background: linear-gradient(180deg, var(--warn-soft), rgba(10, 18, 31, 0.94));
        }
        .agent-risk {
            border-top: 3px solid var(--risk);
            background: linear-gradient(180deg, var(--risk-soft), rgba(10, 18, 31, 0.94));
        }
        .agent-opportunity {
            border-top: 3px solid var(--accent-cyan);
            background: linear-gradient(180deg, rgba(56, 189, 248, 0.16), rgba(10, 18, 31, 0.94));
        }
        .alert-risk {
            border-left: 4px solid var(--risk);
            background: linear-gradient(135deg, var(--risk-soft), rgba(10, 18, 31, 0.9));
            padding: 14px;
            border-radius: 14px;
            margin-bottom: 10px;
        }
        .alert-opportunity {
            border-left: 4px solid var(--safe);
            background: linear-gradient(135deg, var(--safe-soft), rgba(10, 18, 31, 0.9));
            padding: 14px;
            border-radius: 14px;
            margin-bottom: 10px;
        }
        .alert-warning {
            border-left: 4px solid var(--warn);
            background: linear-gradient(135deg, var(--warn-soft), rgba(10, 18, 31, 0.9));
            padding: 14px;
            border-radius: 14px;
            margin-bottom: 10px;
        }
        .small-label {
            color: var(--accent-blue);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .section-title {
            margin-top: 0.25rem;
            margin-bottom: 0.75rem;
            color: #f5f9ff;
        }
        .hero-kicker {
            display: inline-block;
            padding: 0.38rem 0.7rem;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.2);
            color: #c6edff;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .decision-pill {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.84rem;
            margin-top: 0.25rem;
        }
        .pill-buy {
            background: var(--safe-soft);
            color: #8af0a7;
        }
        .pill-hold {
            background: var(--warn-soft);
            color: #ffd575;
        }
        .pill-sell {
            background: var(--risk-soft);
            color: #ff9999;
        }
        .trade-shell {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 1rem;
            align-items: start;
        }
        .trade-card {
            padding: 18px;
            border-radius: 18px;
            border: 1px solid var(--line-soft);
            background: linear-gradient(180deg, rgba(8, 16, 28, 0.96), rgba(10, 18, 31, 0.9));
        }
        .trade-note {
            color: var(--text-soft);
            font-size: 0.95rem;
            line-height: 1.5;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


ASSETS = {
    "Algorand": "algorand",
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Solana": "solana",
    "Chainlink": "chainlink",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "Cardano": "cardano",
    "Dogecoin": "dogecoin",
    "Tron": "tron",
    "Avalanche": "avalanche-2",
    "Polkadot": "polkadot",
    "Polygon": "matic-network",
    "Uniswap": "uniswap",
    "Litecoin": "litecoin",
    "Shiba Inu": "shiba-inu",
    "Toncoin": "the-open-network",
    "Near": "near",
    "Aptos": "aptos",
    "Arbitrum": "arbitrum",
    "Optimism": "optimism",
    "Sui": "sui",
    "Pepe": "pepe",
    "Bonk": "bonk",
    "Render": "render-token",
    "Maker": "maker",
    "Aave": "aave",
    "Curve DAO": "curve-dao-token",
    "Jupiter": "jupiter-exchange-solana",
    "Injective": "injective-protocol",
}

AGENT_REGISTRY = {
    "Risk Analyzer": RiskAnalyzerAgent(),
    "Whale Tracker": WhaleTrackerAgent(),
    "Smart Contract Guard": SmartContractGuardAgent(),
    "Opportunity Agent": OpportunityAgent(),
}


def _init_state() -> None:
    if "active_agents" not in st.session_state:
        st.session_state.active_agents = {name: True for name in AGENT_REGISTRY}
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "agent_results" not in st.session_state:
        st.session_state.agent_results = []
    if "market_snapshot" not in st.session_state:
        st.session_state.market_snapshot = None
    if "alert_feed" not in st.session_state:
        st.session_state.alert_feed = []
    if "blockchain_logger" not in st.session_state:
        st.session_state.blockchain_logger = AlgorandLogger()
    if "alert_store" not in st.session_state:
        st.session_state.alert_store = AlertStore()
    if "last_chain_receipt" not in st.session_state:
        st.session_state.last_chain_receipt = None
    if "last_event" not in st.session_state:
        st.session_state.last_event = None


def format_timestamp(timestamp: str | None) -> str:
    if not timestamp:
        return "-"
    return datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def build_market_chart(history: list[dict]) -> pd.DataFrame:
    if not history:
        return pd.DataFrame(columns=["price"])
    df = pd.DataFrame(history)
    df["time"] = pd.to_datetime(df["timestamp"])
    return df.set_index("time")[["price"]]


def get_risk_css(score: int) -> str:
    if score >= 70:
        return "metric-risk"
    if score >= 40:
        return "metric-warn"
    return "metric-safe"


def get_agent_css(signal: str) -> str:
    normalized = signal.lower()
    if normalized in {"high", "weak"}:
        return "agent-risk"
    if normalized in {"medium", "watchlist"}:
        return "agent-warn"
    if normalized in {"bullish"}:
        return "agent-opportunity"
    return "agent-safe"


def get_decision_pill_css(decision: str) -> str:
    if decision == "BUY":
        return "pill-buy"
    if decision == "SELL":
        return "pill-sell"
    return "pill-hold"


def run_pipeline(asset_id: str, market_data: dict) -> tuple[list[dict], dict]:
    enabled_agents = [
        AGENT_REGISTRY[name]
        for name, enabled in st.session_state.active_agents.items()
        if enabled
    ]

    agent_results = [agent.analyze(market_data) for agent in enabled_agents]
    decision = DecisionEngine().evaluate(
        agent_results=agent_results,
        market_data=market_data,
        asset_id=asset_id,
    )
    return agent_results, decision


def push_alerts(decision: dict) -> None:
    store: AlertStore = st.session_state.alert_store
    alert = store.create_alert(decision)
    st.session_state.alert_feed = store.list_alerts()
    st.session_state.analysis_result = decision


def render_alert_feed(alerts: list[dict]) -> None:
    if not alerts:
        st.info("No alerts yet. Run analysis or simulate an event to populate the feed.")
        return

    for alert in alerts[:6]:
        css_class = {
            "Risk": "alert-risk",
            "Opportunity": "alert-opportunity",
        }.get(alert["type"], "alert-warning")
        bullets = "".join(f"<li>{item}</li>" for item in alert["explanation"])
        st.markdown(
            f"""
            <div class="{css_class}">
                <div class="small-label">{alert["type"]} • {format_timestamp(alert["timestamp"])}</div>
                <h4 style="margin: 0.3rem 0 0.5rem 0;">{alert["title"]}</h4>
                <ul style="margin: 0; padding-left: 1.2rem;">{bullets}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_agent_panel(agent_results: list[dict]) -> None:
    if not agent_results:
        st.info("Agent outputs will appear here after analysis.")
        return

    columns = st.columns(len(agent_results))
    for col, result in zip(columns, agent_results):
        with col:
            badge = result["signal"]
            confidence = result["confidence"]
            agent_css = get_agent_css(badge)
            st.markdown(
                f"""
                <div class="glass-card {agent_css}">
                    <div class="small-label">{result["agent_name"]}</div>
                    <h4 style="margin: 0.35rem 0;">{badge}</h4>
                    <p style="margin: 0 0 0.35rem 0;"><strong>Confidence:</strong> {confidence}%</p>
                    <p style="margin: 0;">{result["reason"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_wallet_overview(snapshot: dict) -> None:
    wallet = snapshot["wallet"]
    st.markdown("#### Wallet Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Wallet Address", wallet["address"])
    c2.metric("Portfolio Value", f"${wallet['portfolio_value_usd']:,.2f}")
    c3.metric("24h PnL", f"{wallet['daily_pnl_percent']:+.2f}%")
    if wallet.get("is_live_sync"):
        st.success("Live Algorand wallet sync active")
        st.caption(f"Apps Local State: {wallet.get('apps_local_state', 0)}")
    else:
        st.warning("Using mock wallet portfolio. Enter a valid Algorand wallet address for live sync.")

    holdings = pd.DataFrame(wallet["holdings"])
    st.dataframe(holdings, width="stretch", hide_index=True)


def render_protocol_monitor(snapshot: dict) -> None:
    st.markdown("### On-Chain Monitor")
    onchain_wallet = snapshot.get("onchain_wallet")
    if not onchain_wallet:
        st.info("Enter a valid Algorand wallet address to activate live wallet sync, protocol monitoring, and liquidation risk checks.")
        return

    liquidation = snapshot.get("liquidation_risk", {})
    cols = st.columns(3)
    cols[0].metric("ALGO Balance", onchain_wallet["algo_balance"])
    cols[1].metric("Recent Transactions", len(onchain_wallet["recent_transactions"]))
    cols[2].metric("Liquidation Risk", liquidation.get("level", "low").upper())

    st.markdown(
        f"""
        <div class="glass-card">
            <p><strong>Liquidation Risk Reason:</strong> {liquidation.get("reason", "No liquidation warning.")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    protocol_cols = st.columns(3)
    for column, key in zip(protocol_cols, ["folks_finance", "tinyman", "pact"]):
        protocol = snapshot.get("protocol_activity", {}).get(key, {})
        with column:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="small-label">{protocol.get('name', key)}</div>
                    <p><strong>Active Positions:</strong> {protocol.get('active_positions', 0)}</p>
                    <p><strong>Recent Interactions:</strong> {protocol.get('recent_interactions', 0)}</p>
                    <p><strong>Tracked App IDs:</strong> {", ".join(map(str, protocol.get('configured_app_ids', []))) or "None configured"}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_pitch() -> None:
    pitch = generate_pitch_summary()
    st.markdown("#### Hackathon Pitch")
    st.markdown(
        f"""
        <div class="glass-card">
            <p><strong>Problem:</strong> {pitch["problem"]}</p>
            <p><strong>Solution:</strong> {pitch["solution"]}</p>
            <p><strong>Unique features:</strong> {" | ".join(pitch["unique_features"])}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_pera_trade_panel(selected_asset: str, decision: dict | None, snapshot: dict) -> None:
    st.markdown("### Pera Wallet Mobile Trade")

    default_action = decision["decision"] if decision and decision["decision"] in {"BUY", "SELL"} else "BUY"
    action = st.radio(
        "Trade Action",
        ["BUY", "SELL"],
        index=0 if default_action == "BUY" else 1,
        horizontal=True,
        key="pera_trade_action",
    )
    settlement_asset = st.selectbox(
        "Settlement Asset",
        list(PeraTradeHelper.SUPPORTED_SETTLEMENT_ASSETS.keys()),
        key="pera_settlement_asset",
    )
    custom_asset_id = None
    custom_decimals = 6
    custom_label = None
    if settlement_asset == "Custom TestNet ASA":
        custom_cols = st.columns(3)
        with custom_cols[0]:
            custom_asset_id = int(
                st.number_input(
                    "TestNet ASA ID",
                    min_value=1,
                    value=10458941,
                    step=1,
                    key="pera_custom_asset_id",
                )
            )
        with custom_cols[1]:
            custom_decimals = int(
                st.number_input(
                    "Decimals",
                    min_value=0,
                    max_value=18,
                    value=6,
                    step=1,
                    key="pera_custom_decimals",
                )
            )
        with custom_cols[2]:
            custom_label = st.text_input(
                "Token Label",
                value="Custom TestNet ASA",
                key="pera_custom_asset_label",
            ).strip() or "Custom TestNet ASA"
    amount = st.number_input(
        "Amount",
        min_value=0.1,
        value=5.0,
        step=0.1,
        key="pera_trade_amount",
    )

    risk_score = decision["risk_score"] if decision else snapshot["baseline_risk_score"]
    trade_link = PeraTradeHelper.build_pera_url(
        action=action,
        tracked_asset=selected_asset,
        settlement_asset=settlement_asset,
        amount=amount,
        risk_score=risk_score,
        custom_asset_id=custom_asset_id,
        custom_decimals=custom_decimals,
        custom_label=custom_label,
    )
    qr_bytes = PeraTradeHelper.generate_qr_bytes(trade_link)
    settlement_display = custom_label or settlement_asset

    st.markdown(
        """
        <div class="trade-shell">
            <div class="trade-card">
                <div class="small-label">How It Works</div>
                <p class="trade-note">
                    Scan the QR code in Pera Wallet on your phone or open the deep link on mobile.
                    The wallet will open a pre-filled transaction carrying the DeFiGuard trade intent in the note field.
                </p>
                <p class="trade-note">
                    For this MVP, the flow creates a mobile-ready settlement request on Algorand TestNet.
                    The note includes the AI action, tracked asset, amount, and risk score for transparency.
                </p>
            </div>
            <div class="trade-card">
                <div class="small-label">Settlement</div>
                <p class="trade-note"><strong>Receiver:</strong> {receiver}</p>
                <p class="trade-note"><strong>Asset:</strong> {settlement_asset}</p>
                <p class="trade-note"><strong>Tracked market:</strong> {tracked_asset}</p>
                <p class="trade-note"><strong>Action:</strong> {action}</p>
            </div>
        </div>
        """.format(
            receiver=PeraTradeHelper.DEMO_SETTLEMENT_ADDRESS,
            settlement_asset=settlement_display,
            tracked_asset=selected_asset,
            action=action,
        ),
        unsafe_allow_html=True,
    )

    trade_cols = st.columns([0.9, 1.1])
    with trade_cols[0]:
        st.image(qr_bytes, caption="Scan in Pera Wallet mobile", width=260)
    with trade_cols[1]:
        st.markdown("#### Mobile Steps")
        st.markdown(
            "\n".join(
                [
                    "1. Open Pera Wallet on your phone.",
                    "2. Tap the QR scanner and scan the code shown here.",
                    "3. Review the pre-filled transaction details.",
                    "4. Approve the transaction to submit the DeFiGuard trade request.",
                ]
            )
        )
        st.markdown(f"[Open in Pera Wallet]({trade_link})")
        st.code(trade_link, language="text")
        st.caption(
            "This MVP uses a pre-filled Algorand TestNet transaction so users can approve the action from Pera mobile. Use Custom TestNet ASA for any test token you control or have opted into."
        )


_init_state()
fetcher = DataFetcher()

with st.sidebar:
    st.title("DeFiGuard AI")
    selected_asset = st.selectbox("Tracked Asset", list(ASSETS.keys()))
    wallet_address = st.text_input(
        "Wallet Address",
        value="ALGO-DEMO-WALLET-01",
        help="Mock wallet is enough for the MVP demo.",
    )

    st.markdown("### Agent Hub")
    for name in AGENT_REGISTRY:
        st.session_state.active_agents[name] = st.toggle(
            name,
            value=st.session_state.active_agents[name],
        )

    if st.button("Run Live Analysis", width="stretch", type="primary"):
        market_snapshot = fetcher.get_market_snapshot(
            asset_id=ASSETS[selected_asset],
            wallet_address=wallet_address,
        )
        st.session_state.market_snapshot = market_snapshot
        agent_results, decision = run_pipeline(ASSETS[selected_asset], market_snapshot)
        st.session_state.agent_results = agent_results
        push_alerts(decision)
        st.session_state.last_chain_receipt = None

    if st.button("Simulate Market Event", width="stretch"):
        base_snapshot = st.session_state.market_snapshot or fetcher.get_market_snapshot(
            asset_id=ASSETS[selected_asset],
            wallet_address=wallet_address,
        )
        simulated_snapshot, event_info = MarketSimulator().simulate_market_shock(base_snapshot)
        st.session_state.market_snapshot = simulated_snapshot
        st.session_state.last_event = event_info
        agent_results, decision = run_pipeline(ASSETS[selected_asset], simulated_snapshot)
        st.session_state.agent_results = agent_results
        push_alerts(decision)
        st.session_state.last_chain_receipt = None

    st.markdown("### Demo Notes")
    st.caption("CoinGecko is used when available. The app falls back to deterministic demo data if the API is unavailable.")


st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Autonomous Multi-Agent Risk Intelligence System</div>
        <h1 style="margin: 0.4rem 0 0.6rem 0;">DeFiGuard AI</h1>
        <p style="margin: 0; max-width: 860px; color: #d7e6f6;">
            Monitor wallet exposure, detect DeFi risks, surface momentum opportunities,
            and optionally log explainable alerts to Algorand TestNet for transparent audit trails.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.last_event:
    event = st.session_state.last_event
    st.warning(
        f"Demo event triggered: {event['label']} | impact {event['price_impact_percent']}% | {event['summary']}"
    )

snapshot = st.session_state.market_snapshot or fetcher.get_market_snapshot(
    asset_id=ASSETS[selected_asset],
    wallet_address=wallet_address,
)
chart_df = build_market_chart(snapshot["price_history"])

left, right = st.columns([1.5, 1])
with left:
    render_wallet_overview(snapshot)
    st.markdown("#### Market Trend")
    st.line_chart(chart_df, width="stretch")

with right:
    decision = st.session_state.analysis_result
    risk_score = decision["risk_score"] if decision else snapshot["baseline_risk_score"]
    decision_label = decision["decision"] if decision else "HOLD"
    css = get_risk_css(risk_score)
    st.markdown(
        f"""
        <div class="glass-card {css}">
            <div class="small-label">Risk Meter</div>
            <h2 style="margin: 0.3rem 0 0.4rem 0;">{risk_score}/100</h2>
            <div class="decision-pill {get_decision_pill_css(decision_label)}">{decision_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=False):
        st.markdown("#### What Should I Do?")
        if st.button("Explain Action", width="stretch"):
            if decision:
                st.info(decision["summary"])
            else:
                st.info("Run a live analysis first so the collaboration engine can recommend an action.")

        if decision and st.button("Log Latest Alert On Algorand", width="stretch"):
            try:
                receipt = st.session_state.blockchain_logger.log_alert(
                    decision["alerts"][0],
                    wallet_address=wallet_address,
                )
                st.session_state.last_chain_receipt = receipt
            except Exception as exc:
                st.session_state.last_chain_receipt = None
                st.error(f"Live Algorand logging failed: {exc}")

        if st.session_state.last_chain_receipt:
            receipt = st.session_state.last_chain_receipt
            st.success(
                f"Alert logged via {receipt.get('mode', 'simulation')} on {receipt['network']} with tx id `{receipt['transaction_id']}`"
            )
            st.caption(
                f"Hash: {receipt['message_hash']} | Timestamp: {format_timestamp(receipt['timestamp'])}"
            )


st.markdown("### Agent Insights")
render_agent_panel(st.session_state.agent_results)

if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    st.markdown("### Decision Engine")
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Risk Score", result["risk_score"])
    c2.metric("Decision", result["decision"])
    c3.metric("Signal Confidence", f"{result['confidence']}%")
    st.markdown(
        f"""
        <div class="glass-card">
            <p><strong>Summary:</strong> {result["summary"]}</p>
            <p><strong>Reasoning:</strong></p>
            <ul>{"".join(f"<li>{point}</li>" for point in result["explanation_points"])}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Alerts Feed")
render_alert_feed(st.session_state.alert_feed)

st.markdown("### Market Snapshot")
snapshot_cols = st.columns(4)
snapshot_cols[0].metric("Asset Price", f"${snapshot['current_price']:,.4f}")
snapshot_cols[1].metric("24h Change", f"{snapshot['price_change_24h']:+.2f}%")
snapshot_cols[2].metric("Liquidity Change", f"{snapshot['liquidity_change_24h']:+.2f}%")
snapshot_cols[3].metric("Large Transfers", snapshot["large_transfers"])

render_pitch()
render_pera_trade_panel(selected_asset, st.session_state.analysis_result, snapshot)
render_protocol_monitor(snapshot)

with st.expander("Sample Output"):
    sample = st.session_state.analysis_result or {
        "risk_score": 58,
        "decision": "HOLD",
        "summary": "Mixed risk and opportunity signals suggest monitoring rather than acting immediately.",
        "alerts": [
            {
                "type": "Warning",
                "title": "Sample DeFi alert",
                "timestamp": datetime.now(UTC).isoformat(),
                "explanation": [
                    "Whale activity is elevated.",
                    "Momentum is positive but contract caution remains.",
                ],
            }
        ],
    }
    st.json(sample)
