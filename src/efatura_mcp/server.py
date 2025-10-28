"""e-Fatura MCP Server implementation."""

import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from zeep import Client
from zeep.transports import Transport

# Load environment variables
load_dotenv()


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


class EFaturaClient:
    """e-Fatura GIB client wrapper."""

    def __init__(self, settings: EFaturaSettings):
        self.settings = settings
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize SOAP client for GIB."""
        # GIB WSDL endpoints
        wsdl_urls = {
            "test": "https://efaturatest.gib.gov.tr/earsivws/efatura?wsdl",
            "production": "https://efatura.gib.gov.tr/earsivws/efatura?wsdl"
        }

        wsdl_url = wsdl_urls.get(self.settings.gib_environment, wsdl_urls["test"])

        try:
            transport = Transport(timeout=30)
            self.client = Client(wsdl_url, transport=transport)
        except Exception as e:
            print(f"Warning: Could not initialize SOAP client: {e}")
            self.client = None

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
        # Mock implementation - replace with actual GIB API calls
        mock_invoices = [
            Invoice(
                invoice_id=f"INV-{i:05d}",
                invoice_number=f"2024{i:08d}",
                issue_date="2024-01-15",
                supplier_name=f"Tedarikçi Firma {i}",
                customer_name=f"Müşteri Firma {i}",
                total_amount=1000.0 + (i * 100),
                currency="TRY",
                status="approved" if i % 2 == 0 else "pending"
            )
            for i in range(1, min(limit + 1, 11))
        ]

        return mock_invoices

    def get_invoice_detail(self, invoice_id: str) -> Invoice | None:
        """
        Get detailed information for a specific invoice.

        Args:
            invoice_id: Invoice ID to retrieve

        Returns:
            Invoice details or None if not found
        """
        # Mock implementation - replace with actual GIB API calls
        mock_invoice = Invoice(
            invoice_id=invoice_id,
            invoice_number="202400000123",
            issue_date="2024-01-15",
            supplier_name="ABC Tedarik A.Ş.",
            customer_name="XYZ Müşteri Ltd. Şti.",
            total_amount=5432.10,
            currency="TRY",
            status="approved"
        )

        return mock_invoice


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
        response_lines = [f"Found {len(invoices)} invoices:\n"]
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
