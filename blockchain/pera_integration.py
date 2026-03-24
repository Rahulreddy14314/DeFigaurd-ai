"""
Pera Wallet Deep Link Integration for DeFiGuard
Creates Algorand transactions and generates QR codes for mobile wallet signing
Uses base64 encoding and msgpack for transaction serialization
"""

import base64
import qrcode
from io import BytesIO
from datetime import datetime
from typing import Tuple, Optional

try:
    import msgpack
    import algosdk
    from algosdk import transaction
    ALGOSDK_AVAILABLE = True
except ImportError:
    ALGOSDK_AVAILABLE = False


class PeraDeepLinkGenerator:
    """
    Generates Pera Wallet deep links for:
    1. Wallet connection (initial QR)
    2. Alert signing on Algorand blockchain
    
    Supports 0-ALGO transactions with note field containing alert data
    """
    
    # Algorand Testnet Configuration
    ALGOD_SERVER = "https://testnet-api.algonode.cloud"
    ALGOD_TOKEN = ""
    ALGOD_PORT = ""
    
    # Pera Wallet Connection
    PERA_CONNECT_URL = "https://wallet.perawallet.app/connect"
    
    @staticmethod
    def validate_algorand_address(address: str) -> bool:
        """Validate Algorand address format (58 characters)"""
        return isinstance(address, str) and len(address) == 58
    
    @staticmethod
    def generate_wallet_connection_qr() -> Optional[bytes]:
        """
        Generate QR code for wallet connection (connection request, not transaction)
        User scans this to connect phone wallet to web app
        
        Returns:
            QR code PNG bytes
        """
        try:
            connection_uri = PeraDeepLinkGenerator.PERA_CONNECT_URL
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(connection_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            
            return buf.getvalue()
        except Exception as e:
            print(f"QR generation error: {str(e)}")
            return None
    
    @staticmethod
    def get_wallet_connection_deep_link() -> str:
        """Get the Pera Wallet connection deep link"""
        return PeraDeepLinkGenerator.PERA_CONNECT_URL
    
    @staticmethod
    def create_alert_transaction(
        sender_address: str,
        alert_message: str,
        risk_score: int,
        asset_name: str
    ) -> Optional['algosdk.transaction.PaymentTxn']:
        """
        Create a 0-ALGO self-payment transaction with alert data in note field
        
        Args:
            sender_address: Valid 58-char Algorand address
            alert_message: Alert text to include in transaction
            risk_score: Risk score (0-100)
            asset_name: Name of analyzed asset
            
        Returns:
            Transaction object or None if failed
        """
        if not ALGOSDK_AVAILABLE:
            return None
            
        try:
            # Initialize Algorand client
            algod_client = algosdk.v2client.algod.AlgodClient(
                PeraDeepLinkGenerator.ALGOD_TOKEN,
                PeraDeepLinkGenerator.ALGOD_SERVER,
                PeraDeepLinkGenerator.ALGOD_PORT
            )
            
            # Get suggested parameters
            params = algod_client.suggested_params()
            
            # Create note with alert details
            timestamp = datetime.now().isoformat()
            note_content = (
                f"🛡️ DeFiGuard Alert\n"
                f"Asset: {asset_name}\n"
                f"Risk Score: {risk_score}/100\n"
                f"Alert: {alert_message[:150]}\n"
                f"Time: {timestamp}"
            )
            
            # Encode note as bytes (max 1024 bytes)
            note_bytes = note_content.encode('utf-8')[:1024]
            
            # Create 0-ALGO self-payment transaction
            txn = transaction.PaymentTxn(
                sender=sender_address,
                sp=params,
                receiver=sender_address,
                amt=0,
                note=note_bytes
            )
            
            return txn
            
        except Exception as e:
            print(f"Transaction creation error: {str(e)}")
            return None
    
    @staticmethod
    def encode_transaction_to_base64(txn) -> Optional[str]:
        """
        Encode transaction using msgpack + base64 for deep linking
        
        Args:
            txn: AlgoSDK transaction object
            
        Returns:
            Base64-encoded transaction string
        """
        if not ALGOSDK_AVAILABLE or txn is None:
            return None
            
        try:
            # Convert transaction to dictionary
            txn_dict = txn.dictify()
            
            # Serialize using msgpack
            msgpacked = msgpack.packb(txn_dict, use_bin_type=True)
            
            # Encode as base64
            encoded = base64.b64encode(msgpacked).decode('utf-8')
            
            return encoded
            
        except Exception as e:
            print(f"Transaction encoding error: {str(e)}")
            return None
    
    @staticmethod
    def generate_pera_deep_link(encoded_txn: str) -> str:
        """
        Generate Pera Wallet deep link URI
        
        Args:
            encoded_txn: Base64-encoded transaction
            
        Returns:
            Pera Wallet URI scheme (perawallet://wc?uri=...)
        """
        return f"perawallet://wc?uri={encoded_txn}"
    
    @staticmethod
    def generate_qr_code_image(link: str, box_size: int = 10) -> bytes:
        """
        Generate QR code PNG image from deep link
        
        Args:
            link: Deep link URL or URI scheme
            box_size: Size of QR code boxes
            
        Returns:
            PNG image bytes
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=box_size,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to PNG bytes
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            
            return buf.getvalue()
            
        except Exception as e:
            print(f"QR code generation error: {str(e)}")
            return None
    
    @classmethod
    def generate_blockchain_log_qr(
        cls,
        sender_address: str,
        alert_message: str,
        risk_score: int,
        asset_name: str
    ) -> Tuple[Optional[str], Optional[bytes], Optional[str]]:
        """
        Complete workflow: Create transaction -> Encode -> Generate link -> Generate QR
        
        Args:
            sender_address: User's Algorand address
            alert_message: Alert text
            risk_score: Risk score
            asset_name: Asset name
            
        Returns:
            Tuple of (deep_link, qr_code_bytes, error_message)
        """
        # Validate address
        if not cls.validate_algorand_address(sender_address):
            return None, None, "Invalid Algorand address (must be 58 characters)"
        
        # Create transaction
        txn = cls.create_alert_transaction(sender_address, alert_message, risk_score, asset_name)
        if txn is None:
            return None, None, "Failed to create transaction"
        
        # Encode transaction
        encoded_txn = cls.encode_transaction_to_base64(txn)
        if encoded_txn is None:
            return None, None, "Failed to encode transaction"
        
        # Generate deep link
        deep_link = cls.generate_pera_deep_link(encoded_txn)
        
        # Generate QR code
        qr_image = cls.generate_qr_code_image(deep_link)
        if qr_image is None:
            return None, None, "Failed to generate QR code"
        
        return deep_link, qr_image, None


class AlertBlockchainLogger:
    """
    Logs DeFiGuard alerts to Algorand blockchain via Pera Wallet
    Two-stage flow:
    1. Connect wallet using QR (no address required)
    2. Log alert to blockchain (uses connected wallet address)
    """
    
    def __init__(self):
        self.generator = PeraDeepLinkGenerator()
        self.last_logged_alert = None
        self.connected_address = None
    
    def get_wallet_connection_qr(self) -> dict:
        """
        Generate wallet connection QR code
        
        Returns:
            Dict with qr_code_bytes and deep_link
        """
        qr_image = self.generator.generate_wallet_connection_qr()
        deep_link = self.generator.get_wallet_connection_deep_link()
        
        return {
            'success': True,
            'qr_code': qr_image,
            'deep_link': deep_link,
            'message': 'Scan QR code to connect wallet'
        }
    
    def set_connected_address(self, address: str) -> bool:
        """
        Set the connected wallet address (called after wallet connects)
        
        Args:
            address: The address received from Pera Wallet connection
            
        Returns:
            True if valid address set, False otherwise
        """
        if self.generator.validate_algorand_address(address):
            self.connected_address = address
            return True
        return False
    
    def is_wallet_connected(self) -> bool:
        """Check if wallet is currently connected"""
        return self.connected_address is not None
    
    def get_connected_address(self) -> Optional[str]:
        """Get the connected wallet address"""
        return self.connected_address
    
    def log_alert_to_blockchain(
        self,
        alert_data: dict
    ) -> dict:
        """
        Log an alert to blockchain using connected wallet address
        
        Args:
            alert_data: Dict with 'message', 'risk_score', 'asset'
            
        Returns:
            Dict with status, deep_link, qr_code_bytes, error
        """
        # Check if wallet is connected
        if not self.connected_address:
            return {
                'success': False,
                'error': 'Wallet not connected. Please scan QR code first.',
                'deep_link': None,
                'qr_code': None
            }
        
        sender_address = self.connected_address
        alert_message = alert_data.get('message', 'DeFiGuard Alert')
        risk_score = alert_data.get('risk_score', 0)
        asset_name = alert_data.get('asset', 'Unknown')
        
        deep_link, qr_image, error = self.generator.generate_blockchain_log_qr(
            sender_address,
            alert_message,
            risk_score,
            asset_name
        )
        
        if error:
            return {
                'success': False,
                'error': error,
                'deep_link': None,
                'qr_code': None
            }
        
        self.last_logged_alert = {
            'address': sender_address,
            'alert': alert_message,
            'risk_score': risk_score,
            'asset': asset_name,
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'error': None,
            'deep_link': deep_link,
            'qr_code': qr_image,
            'timestamp': self.last_logged_alert['timestamp']
        }
