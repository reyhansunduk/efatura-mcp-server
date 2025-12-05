"""
GİB e-Arşiv Portal API Client
Based on https://github.com/f/fatura implementation
Uses username/password authentication with token-based API access
"""

import requests
import logging
from datetime import datetime
from typing import Any, Optional
import uuid

logger = logging.getLogger(__name__)


class GIBEarsivClient:
    """
    GİB e-Arşiv Portal API Client

    Authenticates with username/password and uses token-based API access.
    Based on the working implementation from https://github.com/f/fatura
    """

    # API Base URLs
    BASE_URLS = {
        "test": "https://earsivportaltest.efatura.gov.tr",
        "production": "https://earsivportal.efatura.gov.tr"
    }

    # API Endpoints
    ENDPOINTS = {
        "token": "/earsiv-services/assos-login",
        "invoices": "/earsiv-services/portal/getUserInvoiceData",
        "invoice_html": "/earsiv-services/portal/getInvoiceView",
        "download": "/earsiv-services/download",
        "create_draft": "/earsiv-services/portal/createDraftInvoice",
        "sign": "/earsiv-services/portal/signDraftInvoice",
        "cancel": "/earsiv-services/portal/cancelDraftInvoice",
    }

    def __init__(self, username: str, password: str, environment: str = "test"):
        """
        Initialize GİB e-Arşiv client

        Args:
            username: GİB username (VKN or TCKN)
            password: GİB password
            environment: "test" or "production"
        """
        self.username = username
        self.password = password
        self.environment = environment
        self.base_url = self.BASE_URLS.get(environment, self.BASE_URLS["test"])
        self.token = None
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        logger.info(f"GİB e-Arşiv client initialized for {environment}")

    def _make_request(self, endpoint: str, data: dict = None, method: str = "POST") -> dict:
        """
        Make HTTP request to GİB API

        Args:
            endpoint: API endpoint path
            data: Request payload
            method: HTTP method (GET/POST)

        Returns:
            Response JSON
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "POST":
                response = self.session.post(url, data=data)
            else:
                response = self.session.get(url, params=data)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise

    def get_token(self) -> str:
        """
        Authenticate and get access token

        Returns:
            Access token string

        Raises:
            Exception if authentication fails
        """
        logger.info("Authenticating with GİB e-Arşiv...")

        # Prepare authentication payload
        payload = {
            "assoscmd": "anologin",
            "rtype": "json",
            "userid": self.username,
            "sifre": self.password,
            "sifre2": self.password,
            "parola": "1"  # This is part of the protocol
        }

        try:
            response = self._make_request(self.ENDPOINTS["token"], payload)

            # Check if authentication was successful
            if response.get("userid"):
                self.token = response.get("token")
                logger.info("✅ Authentication successful")
                return self.token
            else:
                error_msg = response.get("error", "Unknown authentication error")
                logger.error(f"❌ Authentication failed: {error_msg}")
                raise Exception(f"Authentication failed: {error_msg}")

        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            raise

    def ensure_token(self):
        """Ensure we have a valid token, get new one if needed"""
        if not self.token:
            self.get_token()

    def get_invoices(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get invoices for date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of invoices

        Returns:
            List of invoices
        """
        self.ensure_token()

        # Convert dates to DD/MM/YYYY format
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        payload = {
            "cmd": "EARSIV_PORTAL_TASLAKLARI_GETIR",
            "callid": str(uuid.uuid4()),
            "pageName": "RG_BASITFATURA",
            "token": self.token,
            "jp": {
                "baslangic": start_dt.strftime("%d/%m/%Y"),
                "bitis": end_dt.strftime("%d/%m/%Y"),
                "hangiTip": "5000/30000"  # Invoice type filter
            }
        }

        try:
            response = self._make_request(self.ENDPOINTS["invoices"], payload)

            if response.get("data"):
                invoices = response["data"]
                logger.info(f"✅ Retrieved {len(invoices)} invoices")
                return invoices[:limit]
            else:
                logger.warning("No invoices found for date range")
                return []

        except Exception as e:
            logger.error(f"Failed to get invoices: {e}")
            return []

    def get_invoice_html(self, invoice_uuid: str) -> Optional[str]:
        """
        Get invoice HTML for viewing/printing

        Args:
            invoice_uuid: Invoice UUID

        Returns:
            HTML content or None
        """
        self.ensure_token()

        payload = {
            "cmd": "EARSIV_PORTAL_FATURA_GOSTER",
            "callid": str(uuid.uuid4()),
            "pageName": "RG_TASLAKLAR",
            "token": self.token,
            "jp": {
                "ettn": invoice_uuid
            }
        }

        try:
            response = self._make_request(self.ENDPOINTS["invoice_html"], payload)

            if response.get("data"):
                return response["data"]
            return None

        except Exception as e:
            logger.error(f"Failed to get invoice HTML: {e}")
            return None

    def get_invoice_download_url(self, invoice_uuid: str) -> Optional[str]:
        """
        Get download URL for signed invoice (ZIP with HTML and XML)

        Args:
            invoice_uuid: Invoice UUID

        Returns:
            Download URL or None
        """
        # The download URL format based on fatura.js
        download_url = f"{self.base_url}{self.ENDPOINTS['download']}?token={self.token}&ettn={invoice_uuid}&belgeTip=FATURA&onayDurumu=Onaylandı&cmd=EARSIV_PORTAL_BELGE_INDIR"

        return download_url

    def find_invoice(
        self,
        date: str,
        invoice_number: Optional[str] = None,
        invoice_uuid: Optional[str] = None
    ) -> Optional[dict[str, Any]]:
        """
        Find specific invoice by date and number or UUID

        Args:
            date: Invoice date (YYYY-MM-DD)
            invoice_number: Invoice number (optional)
            invoice_uuid: Invoice UUID (optional)

        Returns:
            Invoice data or None
        """
        # Get all invoices for that date
        invoices = self.get_invoices(date, date, limit=1000)

        # Filter by number or UUID
        for invoice in invoices:
            if invoice_uuid and invoice.get("ettn") == invoice_uuid:
                return invoice
            if invoice_number and invoice.get("belgeNumarasi") == invoice_number:
                return invoice

        return None

    def create_draft_invoice(self, invoice_data: dict[str, Any]) -> Optional[str]:
        """
        Create a draft invoice

        Args:
            invoice_data: Invoice data structure

        Returns:
            Invoice UUID or None
        """
        self.ensure_token()

        payload = {
            "cmd": "EARSIV_PORTAL_FATURA_OLUSTUR",
            "callid": str(uuid.uuid4()),
            "pageName": "RG_BASITFATURA",
            "token": self.token,
            "jp": invoice_data
        }

        try:
            response = self._make_request(self.ENDPOINTS["create_draft"], payload)

            if response.get("data"):
                invoice_uuid = response["data"]
                logger.info(f"✅ Draft invoice created: {invoice_uuid}")
                return invoice_uuid
            return None

        except Exception as e:
            logger.error(f"Failed to create draft invoice: {e}")
            return None

    def sign_draft_invoice(self, invoice_uuid: str) -> bool:
        """
        Sign a draft invoice (finalize it)

        Args:
            invoice_uuid: Draft invoice UUID

        Returns:
            True if successful
        """
        self.ensure_token()

        payload = {
            "cmd": "EARSIV_PORTAL_FATURA_IMZALA",
            "callid": str(uuid.uuid4()),
            "pageName": "RG_TASLAKLAR",
            "token": self.token,
            "jp": {
                "imzalanacaklar": [invoice_uuid]
            }
        }

        try:
            response = self._make_request(self.ENDPOINTS["sign"], payload)

            if response.get("data"):
                logger.info(f"✅ Invoice signed: {invoice_uuid}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to sign invoice: {e}")
            return False

    def cancel_draft_invoice(self, invoice_uuid: str, reason: str) -> bool:
        """
        Cancel a draft invoice

        Args:
            invoice_uuid: Invoice UUID to cancel
            reason: Cancellation reason

        Returns:
            True if successful
        """
        self.ensure_token()

        payload = {
            "cmd": "EARSIV_PORTAL_FATURA_SIL",
            "callid": str(uuid.uuid4()),
            "pageName": "RG_TASLAKLAR",
            "token": self.token,
            "jp": {
                "silinecekler": [invoice_uuid],
                "aciklama": reason
            }
        }

        try:
            response = self._make_request(self.ENDPOINTS["cancel"], payload)

            if response.get("data"):
                logger.info(f"✅ Invoice cancelled: {invoice_uuid}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to cancel invoice: {e}")
            return False


# Test code
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Test authentication
    client = GIBEarsivClient(
        username=os.getenv("GIB_USERNAME", ""),
        password=os.getenv("GIB_PASSWORD", ""),
        environment=os.getenv("GIB_ENVIRONMENT", "test")
    )

    try:
        # Get token
        token = client.get_token()
        print(f"✅ Token obtained: {token[:20]}...")

        # Get invoices
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        invoices = client.get_invoices(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

        print(f"✅ Found {len(invoices)} invoices")

        if invoices:
            print("\nFirst invoice:")
            print(f"  UUID: {invoices[0].get('ettn')}")
            print(f"  Number: {invoices[0].get('belgeNumarasi')}")
            print(f"  Date: {invoices[0].get('belgeTarihi')}")
            print(f"  Amount: {invoices[0].get('toplamTutar')}")

    except Exception as e:
        print(f"❌ Error: {e}")
