"""
Mock data for e-Fatura MCP Server
Used when real GİB credentials are not available
"""

from datetime import datetime, timedelta
from typing import Any

# Mock invoices for demonstration
MOCK_INVOICES = [
    {
        "ettn": "550e8400-e29b-41d4-a716-446655440001",
        "belgeNumarasi": "ABC2024000001",
        "belgeTarihi": "01/12/2024",
        "gonderenUnvan": "Demo Teknoloji A.Ş.",
        "aliciUnvan": "Örnek Müşteri Ltd. Şti.",
        "toplamTutar": "15000.00",
        "paraBirimi": "TRY",
        "onayDurumu": "Onaylandı"
    },
    {
        "ettn": "550e8400-e29b-41d4-a716-446655440002",
        "belgeNumarasi": "ABC2024000002",
        "belgeTarihi": "02/12/2024",
        "gonderenUnvan": "Demo Teknoloji A.Ş.",
        "aliciUnvan": "Test Şirketi A.Ş.",
        "toplamTutar": "8500.50",
        "paraBirimi": "TRY",
        "onayDurumu": "Onaylandı"
    },
    {
        "ettn": "550e8400-e29b-41d4-a716-446655440003",
        "belgeNumarasi": "ABC2024000003",
        "belgeTarihi": "03/12/2024",
        "gonderenUnvan": "Demo Teknoloji A.Ş.",
        "aliciUnvan": "Proje Danışmanlık Ltd.",
        "toplamTutar": "22000.00",
        "paraBirimi": "TRY",
        "onayDurumu": "Beklemede"
    },
    {
        "ettn": "550e8400-e29b-41d4-a716-446655440004",
        "belgeNumarasi": "ABC2024000004",
        "belgeTarihi": "04/12/2024",
        "gonderenUnvan": "Demo Teknoloji A.Ş.",
        "aliciUnvan": "Yazılım Geliştirme A.Ş.",
        "toplamTutar": "45000.00",
        "paraBirimi": "TRY",
        "onayDurumu": "Onaylandı"
    },
    {
        "ettn": "550e8400-e29b-41d4-a716-446655440005",
        "belgeNumarasi": "ABC2024000005",
        "belgeTarihi": "05/12/2024",
        "gonderenUnvan": "Demo Teknoloji A.Ş.",
        "aliciUnvan": "E-Ticaret Platformu Ltd.",
        "toplamTutar": "12500.75",
        "paraBirimi": "TRY",
        "onayDurumu": "Onaylandı"
    },
]


class MockGIBEarsivClient:
    """
    Mock GİB e-Arşiv API client for demonstration
    Returns sample data without requiring real credentials

    This allows users to:
    - Test the MCP server functionality
    - See how tools work in Claude Desktop
    - Understand the data structure

    When real credentials are added, the server automatically
    switches to the real GIBEarsivClient
    """

    def __init__(self, username: str = "demo", password: str = "demo", environment: str = "test"):
        self.username = username
        self.password = password
        self.environment = environment
        self.token = "mock_token_12345"

    def get_token(self) -> str:
        """Return mock token"""
        return self.token

    def ensure_token(self):
        """Ensure we have a token (mock always has one)"""
        pass

    def get_invoices(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get mock invoices

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of invoices

        Returns:
            List of mock invoice dictionaries
        """
        # Return mock data (limited by limit parameter)
        return MOCK_INVOICES[:limit]

    def get_invoice_html(self, invoice_uuid: str) -> str | None:
        """
        Get mock invoice HTML

        Args:
            invoice_uuid: Invoice UUID

        Returns:
            Mock HTML content
        """
        # Find invoice
        invoice = next((inv for inv in MOCK_INVOICES if inv["ettn"] == invoice_uuid), None)

        if not invoice:
            return None

        # Return mock HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fatura - {invoice['belgeNumarasi']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .info {{ margin: 20px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>e-Arşiv Fatura</h1>
                <p class="label">Fatura No: {invoice['belgeNumarasi']}</p>
            </div>
            <div class="info">
                <p><span class="label">Tarih:</span> {invoice['belgeTarihi']}</p>
                <p><span class="label">Satıcı:</span> {invoice['gonderenUnvan']}</p>
                <p><span class="label">Alıcı:</span> {invoice['aliciUnvan']}</p>
                <p><span class="label">Toplam Tutar:</span> {invoice['toplamTutar']} {invoice['paraBirimi']}</p>
                <p><span class="label">Durum:</span> {invoice['onayDurumu']}</p>
            </div>
            <p style="color: #666; font-size: 12px; margin-top: 40px;">
                Bu bir demo faturadır. Gerçek GİB kimlik bilgileriyle giriş yapıldığında
                gerçek fatura bilgileri görüntülenecektir.
            </p>
        </body>
        </html>
        """
        return html

    def get_invoice_download_url(self, invoice_uuid: str) -> str:
        """
        Get mock download URL

        Args:
            invoice_uuid: Invoice UUID

        Returns:
            Mock download URL
        """
        base_url = "https://earsivportaltest.efatura.gov.tr" if self.environment == "test" else "https://earsivportal.efatura.gov.tr"
        return f"{base_url}/earsiv-services/download?token=mock_token&ettn={invoice_uuid}&belgeTip=FATURA&onayDurumu=Onaylandı&cmd=EARSIV_PORTAL_BELGE_INDIR"

    def find_invoice(
        self,
        date: str,
        invoice_number: str | None = None,
        invoice_uuid: str | None = None
    ) -> dict[str, Any] | None:
        """
        Find mock invoice by number or UUID

        Args:
            date: Invoice date (not used in mock)
            invoice_number: Invoice number (optional)
            invoice_uuid: Invoice UUID (optional)

        Returns:
            Mock invoice data or None
        """
        # Search by UUID
        if invoice_uuid:
            return next((inv for inv in MOCK_INVOICES if inv["ettn"] == invoice_uuid), None)

        # Search by number
        if invoice_number:
            return next((inv for inv in MOCK_INVOICES if inv["belgeNumarasi"] == invoice_number), None)

        return None

    def create_draft_invoice(self, invoice_data: dict[str, Any]) -> str | None:
        """
        Create mock draft invoice

        Args:
            invoice_data: Invoice data

        Returns:
            Mock invoice UUID
        """
        # Generate mock UUID
        import uuid
        mock_uuid = str(uuid.uuid4())

        # In real implementation, this would be added to database
        # For mock, just return the UUID
        return mock_uuid

    def sign_draft_invoice(self, invoice_uuid: str) -> bool:
        """
        Sign mock draft invoice

        Args:
            invoice_uuid: Invoice UUID to sign

        Returns:
            Always True for mock
        """
        return True

    def cancel_draft_invoice(self, invoice_uuid: str, reason: str) -> bool:
        """
        Cancel mock draft invoice

        Args:
            invoice_uuid: Invoice UUID to cancel
            reason: Cancellation reason

        Returns:
            Always True for mock
        """
        return True
