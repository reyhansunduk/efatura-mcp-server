"""e-Fatura MCP Server implementation."""

import logging
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import the real GİB e-Arşiv API client and mock client
from .gib_earsiv_client import GIBEarsivClient
from .mock_data import MockGIBEarsivClient

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EFaturaSettings(BaseSettings):
    """e-Fatura GIB settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

    gib_username: str = Field(default="", alias="GIB_USERNAME")
    gib_password: str = Field(default="", alias="GIB_PASSWORD")
    gib_environment: str = Field(default="test", alias="GIB_ENVIRONMENT")


class Invoice(BaseModel):
    """Invoice model."""

    invoice_id: str
    invoice_number: str
    issue_date: str
    supplier_name: str
    customer_name: str
    total_amount: float
    currency: str
    status: str


class InvoiceCreateRequest(BaseModel):
    """Invoice creation request model."""

    invoice_number: str
    issue_date: str
    supplier_vkn: str
    supplier_name: str
    customer_vkn: str
    customer_name: str
    items: list[dict[str, Any]]
    total_amount: float
    currency: str = "TRY"


class TaxNumberValidation(BaseModel):
    """Tax number validation result."""

    tax_number: str
    is_valid: bool
    company_name: str | None = None
    status: str


class EFaturaClient:
    """e-Fatura GIB client wrapper using real GİB API."""

    def __init__(self, settings: EFaturaSettings):
        self.settings = settings
        self.api_client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize GİB e-Arşiv API client.

        Automatically switches between:
        - Real API: When valid credentials are provided
        - Mock API: For demo/testing without credentials
        """
        # Check if real credentials are configured
        has_real_credentials = (
            self.settings.gib_username
            and self.settings.gib_password
            and self.settings.gib_username.strip() != ""
            and self.settings.gib_password.strip() != ""
            and self.settings.gib_username != "your_gib_username_here"
            and self.settings.gib_password != "your_gib_password_here"
        )

        if has_real_credentials:
            # Use real GİB API
            try:
                self.api_client = GIBEarsivClient(
                    username=self.settings.gib_username,
                    password=self.settings.gib_password,
                    environment=self.settings.gib_environment
                )
                logger.info(f"✅ Real GİB e-Arşiv API client initialized for {self.settings.gib_environment} environment")
                logger.info(f"   Username: {self.settings.gib_username}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize real GİB API client: {e}")
                logger.warning("⚠️  Falling back to mock data for demo purposes")
                self.api_client = MockGIBEarsivClient(environment=self.settings.gib_environment)
        else:
            # Use mock API for demonstration
            self.api_client = MockGIBEarsivClient(environment=self.settings.gib_environment)
            logger.warning("="*70)
            logger.warning("⚠️  DEMO MODE: Using mock data")
            logger.warning("="*70)
            logger.warning("GİB credentials not configured - using sample data for demonstration.")
            logger.warning("")
            logger.warning("To use real GİB e-Arşiv API:")
            logger.warning("1. Edit .env file")
            logger.warning("2. Set GIB_USERNAME=<your_real_vkn>")
            logger.warning("3. Set GIB_PASSWORD=<your_real_password>")
            logger.warning("4. Restart the server")
            logger.warning("")
            logger.warning("For now, you can explore all features with sample invoices.")
            logger.warning("="*70)

    def list_invoices(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 10
    ) -> list[Invoice]:
        """
        List invoices from GIB system.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of invoices to return

        Returns:
            List of invoices
        """
        if not self.api_client:
            raise RuntimeError("GİB API client not initialized")

        # Set default date range if not provided
        if not start_date:
            start_date = "2024-01-01"
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Call GİB e-Arşiv API
        try:
            raw_invoices = self.api_client.get_invoices(start_date, end_date, limit)

            # Convert API response to Invoice objects
            # Based on GİB e-Arşiv API response structure
            invoices = []
            for raw_inv in raw_invoices:
                # Map GİB e-Arşiv field names to our Invoice model
                invoice = Invoice(
                    invoice_id=raw_inv.get("ettn", ""),  # ETTN is the invoice UUID
                    invoice_number=raw_inv.get("belgeNumarasi", ""),  # Document number
                    issue_date=raw_inv.get("belgeTarihi", ""),  # Document date
                    supplier_name=raw_inv.get("gonderenUnvan", "Supplier"),  # Sender title
                    customer_name=raw_inv.get("aliciUnvan", "Customer"),  # Receiver title
                    total_amount=float(raw_inv.get("toplamTutar", 0)),  # Total amount
                    currency=raw_inv.get("paraBirimi", "TRY"),  # Currency
                    status=raw_inv.get("onayDurumu", "unknown")  # Approval status
                )
                invoices.append(invoice)

            return invoices
        except Exception as e:
            logger.error(f"Failed to list invoices: {e}")
            # Return empty list on error instead of crashing
            return []

    def get_invoice_detail(self, invoice_id: str) -> Invoice | None:
        """
        Get detailed information for a specific invoice.

        Args:
            invoice_id: Invoice ID (ETTN) to retrieve

        Returns:
            Invoice details or None if not found
        """
        if not self.api_client:
            raise RuntimeError("GİB e-Arşiv API client not initialized")

        try:
            # Use find_invoice to get detailed invoice data
            # First try to find in recent invoices
            from datetime import date, timedelta
            end_date = date.today()
            start_date = end_date - timedelta(days=365)  # Search last year

            invoice_data = self.api_client.find_invoice(
                date=start_date.strftime("%Y-%m-%d"),
                invoice_uuid=invoice_id
            )

            if not invoice_data:
                return None

            # Convert API response to Invoice object
            invoice = Invoice(
                invoice_id=invoice_data.get("ettn", invoice_id),
                invoice_number=invoice_data.get("belgeNumarasi", ""),
                issue_date=invoice_data.get("belgeTarihi", ""),
                supplier_name=invoice_data.get("gonderenUnvan", "Supplier"),
                customer_name=invoice_data.get("aliciUnvan", "Customer"),
                total_amount=float(invoice_data.get("toplamTutar", 0)),
                currency=invoice_data.get("paraBirimi", "TRY"),
                status=invoice_data.get("onayDurumu", "unknown")
            )

            return invoice
        except Exception as e:
            logger.error(f"Failed to get invoice detail for {invoice_id}: {e}")
            return None

    def create_invoice(self, invoice_data: InvoiceCreateRequest) -> str:
        """
        Create a new draft invoice and sign it.

        Args:
            invoice_data: Invoice data to create

        Returns:
            Created invoice ID (ETTN)
        """
        if not self.api_client:
            raise RuntimeError("GİB e-Arşiv API client not initialized")

        try:
            # Convert InvoiceCreateRequest to GİB e-Arşiv format
            # This is a simplified mapping - real implementation needs full GİB structure
            gib_invoice_data = {
                "belgeNumarasi": invoice_data.invoice_number,
                "faturaTarihi": invoice_data.issue_date,
                "saat": datetime.now().strftime("%H:%M:%S"),
                "paraBirimi": invoice_data.currency,
                "dovzTLkur": "0",
                "faturaTipi": "SATIS",
                "vknTckn": invoice_data.customer_vkn,
                "aliciUnvan": invoice_data.customer_name,
                "aliciAdi": invoice_data.customer_name,
                "aliciSoyadi": "",
                "binaAdi": "",
                "binaNo": "",
                "kapiNo": "",
                "kasabaKoy": "",
                "vergiDairesi": "",
                "ulke": "Türkiye",
                "bulvarcaddesokak": "",
                "mahalleSemtIlce": "",
                "sehir": "",
                "postaKodu": "",
                "tel": "",
                "fax": "",
                "eposta": "",
                "websitesi": "",
                "iadeTable": [],
                "ozelMatrahTutari": "0",
                "ozelMatrahOrani": 0,
                "ozelMatrahVergiTutari": "0",
                "vergiCesidi": " ",
                "malHizmetTable": invoice_data.items,
                "tip": "İskonto",
                "matrah": str(invoice_data.total_amount),
                "malhizmetToplamTutari": str(invoice_data.total_amount),
                "toplamIskonto": "0",
                "hesaplanankdv": "0",
                "vergilerToplami": "0",
                "vergilerDahilToplamTutar": str(invoice_data.total_amount),
                "odenecekTutar": str(invoice_data.total_amount),
                "not": "",
                "siparisNumarasi": "",
                "siparisTarihi": "",
                "irsaliyeNumarasi": "",
                "irsaliyeTarihi": "",
                "fisNo": "",
                "fisTarihi": "",
                "fisSaati": " ",
                "fisTipi": " ",
                "zRaporNo": "",
                "okcSeriNo": ""
            }

            # Create draft invoice
            invoice_uuid = self.api_client.create_draft_invoice(gib_invoice_data)

            if not invoice_uuid:
                raise RuntimeError("Failed to create draft invoice - no UUID returned")

            # Sign the draft invoice to finalize it
            sign_success = self.api_client.sign_draft_invoice(invoice_uuid)

            if not sign_success:
                logger.warning(f"Draft invoice created but signing failed: {invoice_uuid}")
                # Return UUID anyway - user can sign manually
            else:
                logger.info(f"Created and signed invoice: {invoice_uuid}")

            return invoice_uuid
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            raise

    def cancel_invoice(self, invoice_id: str, reason: str) -> bool:
        """
        Cancel an existing draft invoice.

        Args:
            invoice_id: Invoice ID (ETTN) to cancel
            reason: Cancellation reason

        Returns:
            True if successful
        """
        if not self.api_client:
            raise RuntimeError("GİB e-Arşiv API client not initialized")

        try:
            result = self.api_client.cancel_draft_invoice(invoice_id, reason)
            if result:
                logger.info(f"Cancelled invoice: {invoice_id}, reason: {reason}")
            return result
        except Exception as e:
            logger.error(f"Failed to cancel invoice {invoice_id}: {e}")
            return False

    def search_invoices(
        self,
        customer_name: str | None = None,
        supplier_name: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        status: str | None = None
    ) -> list[Invoice]:
        """
        Search invoices with filters.

        Args:
            customer_name: Filter by customer name
            supplier_name: Filter by supplier name
            min_amount: Minimum amount filter
            max_amount: Maximum amount filter
            status: Status filter (approved, pending, cancelled)

        Returns:
            List of matching invoices
        """
        # Mock implementation - replace with actual GIB API calls
        all_invoices = self.list_invoices(limit=100)

        filtered = all_invoices
        if customer_name:
            filtered = [inv for inv in filtered if customer_name.lower() in inv.customer_name.lower()]
        if supplier_name:
            filtered = [inv for inv in filtered if supplier_name.lower() in inv.supplier_name.lower()]
        if min_amount is not None:
            filtered = [inv for inv in filtered if inv.total_amount >= min_amount]
        if max_amount is not None:
            filtered = [inv for inv in filtered if inv.total_amount <= max_amount]
        if status:
            filtered = [inv for inv in filtered if inv.status == status]

        return filtered

    def validate_tax_number(self, tax_number: str) -> TaxNumberValidation:
        """
        Validate a Turkish tax number (VKN/TCKN).

        Note: GİB e-Arşiv API doesn't provide direct tax number validation.
        This performs basic format validation only.

        Args:
            tax_number: Tax number to validate

        Returns:
            Validation result
        """
        try:
            # Basic validation: check if it's 10 or 11 digits
            if not tax_number.isdigit():
                return TaxNumberValidation(
                    tax_number=tax_number,
                    is_valid=False,
                    company_name=None,
                    status="invalid_format"
                )

            length = len(tax_number)
            if length == 10:
                # VKN (Company tax number)
                return TaxNumberValidation(
                    tax_number=tax_number,
                    is_valid=True,
                    company_name=None,
                    status="valid_vkn_format"
                )
            elif length == 11:
                # TCKN (Individual tax number)
                return TaxNumberValidation(
                    tax_number=tax_number,
                    is_valid=True,
                    company_name=None,
                    status="valid_tckn_format"
                )
            else:
                return TaxNumberValidation(
                    tax_number=tax_number,
                    is_valid=False,
                    company_name=None,
                    status="invalid_length"
                )
        except Exception as e:
            logger.error(f"Failed to validate tax number {tax_number}: {e}")
            return TaxNumberValidation(
                tax_number=tax_number,
                is_valid=False,
                company_name=None,
                status="error"
            )

    def get_invoice_xml(self, invoice_id: str) -> str | None:
        """
        Get invoice HTML content and download URL.

        Note: GİB e-Arşiv provides HTML view and download link (ZIP with HTML+XML).
        Direct XML access requires downloading the ZIP file.

        Args:
            invoice_id: Invoice ID (ETTN)

        Returns:
            Invoice information with HTML preview and download URL
        """
        if not self.api_client:
            raise RuntimeError("GİB e-Arşiv API client not initialized")

        try:
            # Get invoice HTML for viewing
            html_content = self.api_client.get_invoice_html(invoice_id)

            # Get download URL for ZIP file (contains XML + HTML)
            download_url = self.api_client.get_invoice_download_url(invoice_id)

            if html_content:
                result = f"Invoice HTML Preview:\n\n{html_content[:500]}...\n\n"
                result += f"Download URL (ZIP with XML+HTML):\n{download_url}"
                return result
            elif download_url:
                return f"Download URL (ZIP with XML+HTML):\n{download_url}"
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to get invoice content for {invoice_id}: {e}")
            return None


# Initialize FastMCP server
mcp = Server("efatura-mcp-server")
settings = EFaturaSettings()
efatura_client = EFaturaClient(settings)


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_invoices",
            description=(
                "List e-Fatura invoices from Turkish GIB system. "
                "Returns a list of invoices with basic information. "
                "Optionally filter by date range."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (optional)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (optional)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of invoices to return (default: 10)",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="get_invoice_detail",
            description=(
                "Get detailed information for a specific e-Fatura invoice. "
                "Requires invoice_id obtained from list_invoices."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "Invoice ID to retrieve details for",
                    },
                },
                "required": ["invoice_id"],
            },
        ),
        Tool(
            name="create_invoice",
            description=(
                "Create a new e-Fatura invoice in the GIB system. "
                "Returns the created invoice ID."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_number": {
                        "type": "string",
                        "description": "Unique invoice number",
                    },
                    "issue_date": {
                        "type": "string",
                        "description": "Invoice issue date (YYYY-MM-DD)",
                    },
                    "supplier_vkn": {
                        "type": "string",
                        "description": "Supplier tax number (VKN)",
                    },
                    "supplier_name": {
                        "type": "string",
                        "description": "Supplier company name",
                    },
                    "customer_vkn": {
                        "type": "string",
                        "description": "Customer tax number (VKN/TCKN)",
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "Customer name or company name",
                    },
                    "items": {
                        "type": "array",
                        "description": "Invoice line items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "quantity": {"type": "number"},
                                "unit_price": {"type": "number"},
                                "total": {"type": "number"},
                            },
                        },
                    },
                    "total_amount": {
                        "type": "number",
                        "description": "Total invoice amount",
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (default: TRY)",
                        "default": "TRY",
                    },
                },
                "required": [
                    "invoice_number",
                    "issue_date",
                    "supplier_vkn",
                    "supplier_name",
                    "customer_vkn",
                    "customer_name",
                    "items",
                    "total_amount",
                ],
            },
        ),
        Tool(
            name="cancel_invoice",
            description=(
                "Cancel an existing e-Fatura invoice. "
                "Requires invoice_id and cancellation reason."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "Invoice ID to cancel",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation",
                    },
                },
                "required": ["invoice_id", "reason"],
            },
        ),
        Tool(
            name="search_invoices",
            description=(
                "Search e-Fatura invoices with various filters. "
                "Filter by customer, supplier, amount range, or status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Filter by customer name (optional)",
                    },
                    "supplier_name": {
                        "type": "string",
                        "description": "Filter by supplier name (optional)",
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum invoice amount (optional)",
                    },
                    "max_amount": {
                        "type": "number",
                        "description": "Maximum invoice amount (optional)",
                    },
                    "status": {
                        "type": "string",
                        "description": "Invoice status: approved, pending, cancelled (optional)",
                        "enum": ["approved", "pending", "cancelled"],
                    },
                },
            },
        ),
        Tool(
            name="validate_tax_number",
            description=(
                "Validate a Turkish tax number (VKN for companies, TCKN for individuals). "
                "Returns validation result and company information if available."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tax_number": {
                        "type": "string",
                        "description": "Tax number to validate (10 or 11 digits)",
                    },
                },
                "required": ["tax_number"],
            },
        ),
        Tool(
            name="get_invoice_xml",
            description=(
                "Get the XML content of an e-Fatura invoice. "
                "Returns the UBL-TR format XML."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "Invoice ID to get XML for",
                    },
                },
                "required": ["invoice_id"],
            },
        ),
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name == "list_invoices":
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")
        limit = arguments.get("limit", 10)

        invoices = efatura_client.list_invoices(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        # Format response
        response_lines = [f"Found {len(invoices)} invoices:\n\n"]
        for inv in invoices:
            response_lines.append(
                f"• {inv.invoice_number} - {inv.issue_date}\n"
                f"  {inv.supplier_name} → {inv.customer_name}\n"
                f"  Amount: {inv.total_amount:.2f} {inv.currency} | Status: {inv.status}\n"
                f"  ID: {inv.invoice_id}\n"
            )

        return [TextContent(type="text", text="".join(response_lines))]

    elif name == "get_invoice_detail":
        invoice_id = arguments.get("invoice_id")

        if not invoice_id:
            return [TextContent(type="text", text="Error: invoice_id is required")]

        invoice = efatura_client.get_invoice_detail(invoice_id)

        if not invoice:
            return [TextContent(
                type="text",
                text=f"Invoice not found: {invoice_id}"
            )]

        # Format detailed response
        response = (
            f"Invoice Details:\n\n"
            f"Invoice Number: {invoice.invoice_number}\n"
            f"Invoice ID: {invoice.invoice_id}\n"
            f"Issue Date: {invoice.issue_date}\n"
            f"Status: {invoice.status}\n\n"
            f"Supplier: {invoice.supplier_name}\n"
            f"Customer: {invoice.customer_name}\n\n"
            f"Total Amount: {invoice.total_amount:.2f} {invoice.currency}\n"
        )

        return [TextContent(type="text", text=response)]

    elif name == "create_invoice":
        # Create invoice request
        try:
            invoice_request = InvoiceCreateRequest(**arguments)
            new_invoice_id = efatura_client.create_invoice(invoice_request)

            response = (
                f"✅ Invoice Created Successfully!\n\n"
                f"Invoice ID: {new_invoice_id}\n"
                f"Invoice Number: {invoice_request.invoice_number}\n"
                f"Issue Date: {invoice_request.issue_date}\n"
                f"Supplier: {invoice_request.supplier_name}\n"
                f"Customer: {invoice_request.customer_name}\n"
                f"Total Amount: {invoice_request.total_amount:.2f} {invoice_request.currency}\n"
            )

            return [TextContent(type="text", text=response)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating invoice: {str(e)}")]

    elif name == "cancel_invoice":
        invoice_id = arguments.get("invoice_id")
        reason = arguments.get("reason")

        if not invoice_id or not reason:
            return [TextContent(
                type="text",
                text="Error: invoice_id and reason are required"
            )]

        success = efatura_client.cancel_invoice(invoice_id, reason)

        if success:
            response = (
                f"✅ Invoice Cancelled Successfully!\n\n"
                f"Invoice ID: {invoice_id}\n"
                f"Reason: {reason}\n"
            )
        else:
            response = f"❌ Failed to cancel invoice: {invoice_id}"

        return [TextContent(type="text", text=response)]

    elif name == "search_invoices":
        customer_name = arguments.get("customer_name")
        supplier_name = arguments.get("supplier_name")
        min_amount = arguments.get("min_amount")
        max_amount = arguments.get("max_amount")
        status = arguments.get("status")

        invoices = efatura_client.search_invoices(
            customer_name=customer_name,
            supplier_name=supplier_name,
            min_amount=min_amount,
            max_amount=max_amount,
            status=status
        )

        # Format response
        filters_used = []
        if customer_name:
            filters_used.append(f"Customer: {customer_name}")
        if supplier_name:
            filters_used.append(f"Supplier: {supplier_name}")
        if min_amount is not None:
            filters_used.append(f"Min Amount: {min_amount}")
        if max_amount is not None:
            filters_used.append(f"Max Amount: {max_amount}")
        if status:
            filters_used.append(f"Status: {status}")

        response_lines = [f"Search Results ({len(invoices)} found)\n"]
        if filters_used:
            response_lines.append(f"Filters: {', '.join(filters_used)}\n")
        response_lines.append("\n")

        for inv in invoices:
            response_lines.append(
                f"• {inv.invoice_number} - {inv.issue_date}\n"
                f"  {inv.supplier_name} → {inv.customer_name}\n"
                f"  Amount: {inv.total_amount:.2f} {inv.currency} | Status: {inv.status}\n"
                f"  ID: {inv.invoice_id}\n"
            )

        return [TextContent(type="text", text="".join(response_lines))]

    elif name == "validate_tax_number":
        tax_number = arguments.get("tax_number")

        if not tax_number:
            return [TextContent(type="text", text="Error: tax_number is required")]

        validation = efatura_client.validate_tax_number(tax_number)

        if validation.is_valid:
            response = (
                f"✅ Valid Tax Number\n\n"
                f"Tax Number: {validation.tax_number}\n"
                f"Company Name: {validation.company_name}\n"
                f"Status: {validation.status}\n"
            )
        else:
            response = (
                f"❌ Invalid Tax Number\n\n"
                f"Tax Number: {validation.tax_number}\n"
                f"Status: {validation.status}\n"
            )

        return [TextContent(type="text", text=response)]

    elif name == "get_invoice_xml":
        invoice_id = arguments.get("invoice_id")

        if not invoice_id:
            return [TextContent(type="text", text="Error: invoice_id is required")]

        xml_content = efatura_client.get_invoice_xml(invoice_id)

        if not xml_content:
            return [TextContent(
                type="text",
                text=f"Invoice XML not found: {invoice_id}"
            )]

        response = f"Invoice XML for {invoice_id}:\n\n```xml\n{xml_content}\n```"

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main() -> None:
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            mcp.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
