# DeFiGuard AI

DeFiGuard AI is a Streamlit MVP for a hackathon that monitors DeFi market conditions with four AI-style agents, combines their signals into an explainable action, and optionally logs alerts to an Algorand TestNet style audit trail.

## What It Includes

- `Risk Analyzer Agent` for volatility and downside detection
- `Whale Tracker Agent` for large transfer monitoring
- `Smart Contract Guard Agent` for suspicious contract activity
- `Opportunity Agent` for trend and momentum signals
- `Decision Engine` that produces a final risk score from `0-100`
- `Agent Hub` to toggle agents on and off
- `Demo Mode` to simulate whale sell-offs and price-drop cascades
- `Algorand Logger` that stores alert receipts with simulated TestNet transaction IDs
- `AlgoKit Integration` for real Algorand logging when credentials are configured
- `Pera Wallet Mobile Trade Panel` with QR code and deep link handoff
- `Pitch Summary` panel for demo presentations

## Project Structure

```text
DEFIguard/
├── app.py
├── generate_pitch.py
├── requirements.txt
├── agents/
│   ├── contract_agent.py
│   ├── opportunity_agent.py
│   ├── risk_agent.py
│   └── whale_agent.py
├── blockchain/
│   └── algorand_logger.py
├── engine/
│   └── decision_engine.py
└── utils/
    ├── data_fetcher.py
    └── simulator.py
```

## Run Locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the MVP:

```bash
streamlit run app.py
```

The app runs at [http://localhost:8501](http://localhost:8501).

## Demo Flow

1. Enter a wallet address or keep the mock address.
2. Select an asset and leave the four agents enabled.
3. Click `Run Live Analysis`.
4. Review the risk meter, agent insights, and alerts feed.
5. Click `Simulate Market Event` to trigger instant warnings or opportunities.
6. Click `Log Latest Alert On Algorand` to generate a simulated on-chain receipt.
7. Use the `Pera Wallet Mobile Trade` section to scan a QR code and open a pre-filled mobile trade request in Pera Wallet.

## Enable Real AlgoKit Logging

Set these environment variables before running the app:

```powershell
$env:ALGORAND_PRIVATE_KEY="your_testnet_private_key"
$env:ALGORAND_SENDER_ADDRESS="your_testnet_address"
$env:ALGORAND_NETWORK="testnet"
```

Then launch the app:

```powershell
venv\Scripts\python.exe -m streamlit run app.py
```

Behavior:

- If `ALGORAND_PRIVATE_KEY` is present, the app uses `algokit-utils` to send a self-payment with the alert encoded in the transaction note.
- If credentials are missing, the logger can create a cached TestNet runtime account and attempt to fund it through the AlgoKit TestNet dispenser.

## Pera Wallet Mobile Flow

- The app generates a Pera Wallet mobile deep link and QR code.
- Scanning the QR from the Pera mobile app opens a pre-filled Algorand TestNet transaction.
- The transaction note contains the DeFiGuard trade intent, tracked asset, amount, and risk score.
- This MVP is a mobile trade-request flow, which is ideal for hackathon demos without building a full DEX settlement backend.
- Supported TestNet settlement options include `ALGO`, `USDCA-TestNet`, and `Custom TestNet ASA` for any Algorand TestNet token by ASA ID.

## Live On-Chain Monitoring

Enter a valid Algorand wallet address in the app to activate:

- live wallet balance sync from Algorand indexer
- recent transaction monitoring
- protocol interaction tracking
- liquidation-risk warnings for configured lending exposure

Optional protocol-specific environment variables:

```powershell
$env:FOLKS_PROTOCOL_APP_IDS="..."
$env:PACT_PROTOCOL_APP_IDS="..."
```

Defaults:

- Tinyman monitoring includes a built-in validator app id for TestNet/MainNet
- Folks Finance and Pact monitoring activate when their app ids are configured

## Sample Output

```json
{
  "asset": "algorand",
  "risk_score": 63,
  "decision": "HOLD",
  "confidence": 77,
  "summary": "Signals are mixed, so the safest action is to monitor conditions and wait for confirmation.",
  "alerts": [
    {
      "type": "Warning",
      "title": "ALGORAND HOLD signal",
      "risk_score": 63,
      "decision": "HOLD",
      "timestamp": "2026-03-23T10:15:00",
      "explanation": [
        "Elevated volatility detected.",
        "Large transfers are rising.",
        "No major contract anomalies detected.",
        "Token is trending but confirmation is still developing."
      ]
    }
  ]
}
```

## Notes

- CoinGecko is used when available.
- If external API requests fail, the app falls back to deterministic demo data so the MVP still works.
- Algorand logging writes receipts to `logs/blockchain_alerts.json`.
- Without TestNet credentials, the logger stays in simulation mode.
