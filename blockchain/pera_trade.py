"""Pera Wallet mobile trade helpers."""

from __future__ import annotations

import json
from io import BytesIO
from urllib.parse import quote

import qrcode
from algosdk import encoding


class PeraTradeHelper:
    """Builds Pera Wallet mobile deep links and QR codes for trade intents."""

    DEMO_SETTLEMENT_ADDRESS = "7N54HZSGBRQF7FW6YNC6F5H42AT5OXN3F5OQDAXF6H6PDFHNXIEBCJFHOY"
    SUPPORTED_SETTLEMENT_ASSETS = {
        "ALGO": {"asset_id": None, "decimals": 6, "label": "ALGO"},
        "USDCA-TestNet": {"asset_id": 10458941, "decimals": 6, "label": "USDCA-TestNet"},
        "Custom TestNet ASA": {"asset_id": "custom", "decimals": 6, "label": "Custom TestNet ASA"},
    }

    @staticmethod
    def is_valid_address(address: str) -> bool:
        return bool(address) and encoding.is_valid_address(address)

    @classmethod
    def build_trade_payload(
        cls,
        action: str,
        tracked_asset: str,
        settlement_asset: str,
        amount: float,
        risk_score: int,
        custom_asset_id: int | None = None,
        custom_decimals: int = 6,
        custom_label: str | None = None,
    ) -> dict:
        asset_config = cls.SUPPORTED_SETTLEMENT_ASSETS[settlement_asset]
        asset_id = asset_config["asset_id"]
        decimals = asset_config["decimals"]
        settlement_label = asset_config["label"]

        if asset_id == "custom":
            asset_id = custom_asset_id
            decimals = custom_decimals
            settlement_label = custom_label or settlement_label

        amount_in_base_units = int(round(amount * (10 ** decimals)))
        note_payload = {
            "app": "DeFiGuard AI",
            "action": action,
            "tracked_asset": tracked_asset,
            "settlement_asset": settlement_label,
            "risk_score": risk_score,
            "amount": amount,
        }
        return {
            "receiver": cls.DEMO_SETTLEMENT_ADDRESS,
            "amount_in_base_units": amount_in_base_units,
            "asset_id": asset_id,
            "note": json.dumps(note_payload, separators=(",", ":")),
            "display_amount": amount,
            "settlement_label": settlement_label,
        }

    @classmethod
    def build_pera_url(
        cls,
        action: str,
        tracked_asset: str,
        settlement_asset: str,
        amount: float,
        risk_score: int,
        custom_asset_id: int | None = None,
        custom_decimals: int = 6,
        custom_label: str | None = None,
    ) -> str:
        payload = cls.build_trade_payload(
            action=action,
            tracked_asset=tracked_asset,
            settlement_asset=settlement_asset,
            amount=amount,
            risk_score=risk_score,
            custom_asset_id=custom_asset_id,
            custom_decimals=custom_decimals,
            custom_label=custom_label,
        )
        params = [f"amount={payload['amount_in_base_units']}"]
        if payload["asset_id"] is not None:
            params.append(f"asset={payload['asset_id']}")
        params.append(f"xnote={quote(payload['note'], safe='')}")
        query = "&".join(params)
        return f"perawallet://{payload['receiver']}?{query}"

    @staticmethod
    def generate_qr_bytes(link: str) -> bytes:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=3,
        )
        qr.add_data(link)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
