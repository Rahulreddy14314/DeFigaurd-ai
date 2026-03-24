# DeFiGuard AI Configuration
# This file contains default settings for the application

# Application Settings
APP_NAME = "DeFiGuard AI"
APP_VERSION = "1.0.0"
APP_MODE = "MVP"  # Can be: MVP, DEMO, PRODUCTION

# Market Data Settings
DEFAULT_ASSET = "bitcoin"
SUPPORTED_ASSETS = ["bitcoin", "ethereum"]
API_TIMEOUT = 5  # seconds
USE_MOCK_DATA_FALLBACK = True

# Agent Settings
AGENTS_ENABLED_BY_DEFAULT = {
    "Risk Analyzer": True,
    "Whale Tracker": True,
    "Smart Contract Guard": True,
    "Opportunity Scout": True
}

# Decision Engine Settings
RISK_SCORE_HIGH = 75  # Above this = SELL
RISK_SCORE_MEDIUM_HIGH = 60  # Between 60-75 = HOLD
RISK_SCORE_MEDIUM = 40  # Between 40-60 = HOLD
RISK_SCORE_LOW = 30  # Below 30 = BUY

CONFIDENCE_THRESHOLD = 70  # Minimum confidence for strong signals

# Blockchain Settings
BLOCKCHAIN_NETWORK = "simulation"  # Options: simulation, testnet, mainnet
USE_BLOCKCHAIN_SIMULATION = True
MAX_TRANSACTION_SIZE = 1000  # bytes

# UI Settings
THEME = "light"
SHOW_ADVANCED_METRICS = True
REFRESH_INTERVAL = 5  # seconds

# Logging Settings
LOG_LEVEL = "INFO"  # Can be: DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/defiguard.log"
KEEP_ALERT_HISTORY = True
MAX_ALERT_HISTORY = 100

# Demo Settings
DEMO_MODE_ENABLED = True
SIMULATE_MARKET_EVENTS = True
AVAILABLE_EVENTS = [
    "whale_sell",
    "price_crash", 
    "bull_run",
    "regulatory_news",
    "adoption_news"
]

# Market Event Impacts
EVENT_IMPACTS = {
    "whale_sell": -8,
    "price_crash": -15,
    "bull_run": 12,
    "regulatory_news": -5,
    "adoption_news": 10
}

# API Endpoints
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
ALGOD_URL = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Feature Flags
FEATURES = {
    "blockchain_logging": True,
    "market_simulation": True,
    "agent_hub": True,
    "report_download": True,
    "advanced_analytics": False,  # Future feature
    "telegram_alerts": False,  # Future feature
    "discord_alerts": False,  # Future feature
}

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Performance Settings
ENABLE_CACHING = True
CACHE_TTL = 300  # seconds (5 minutes)
PARALLEL_AGENT_EXECUTION = True

print("✅ Configuration loaded successfully!")
