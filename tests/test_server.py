"""Tests for e-Fatura MCP Server."""

import pytest
from unittest.mock import Mock, patch

from efatura_mcp.server import (
    EFaturaClient,
    EFaturaSettings,
    Invoice,
    call_tool,
    list_tools,
)


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return EFaturaSettings(
        gib_username="test_user",
        gib_password="test_pass",
        gib_environment="test"
    )


@pytest.fixture
def efatura_client(mock_settings):
    """Create EFaturaClient instance for testing."""
    with patch('efatura_mcp.server.Client'):
        return EFaturaClient(mock_settings)


class TestEFaturaClient:
    """Test EFaturaClient class."""

    def test_list_invoices_default(self, efatura_client):
        """Test listing invoices with default parameters."""
        invoices = efatura_client.list_invoices()

        assert len(invoices) == 10
        assert all(isinstance(inv, Invoice) for inv in invoices)
        assert invoices[0].invoice_id == "INV-00001"

    def test_list_invoices_with_limit(self, efatura_client):
        """Test listing invoices with custom limit."""
        invoices = efatura_client.list_invoices(limit=5)

        assert len(invoices) == 5

    def test_list_invoices_with_dates(self, efatura_client):
        """Test listing invoices with date range."""
        invoices = efatura_client.list_invoices(
            start_date="2024-01-01",
            end_date="2024-01-31",
            limit=3
        )

        assert len(invoices) == 3
        assert all(isinstance(inv, Invoice) for inv in invoices)

    def test_get_invoice_detail(self, efatura_client):
        """Test getting invoice details."""
        invoice = efatura_client.get_invoice_detail("INV-00001")

        assert invoice is not None
        assert isinstance(invoice, Invoice)
        assert invoice.invoice_id == "INV-00001"
        assert invoice.currency == "TRY"
        assert invoice.total_amount > 0


class TestMCPTools:
    """Test MCP tool implementations."""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that tools are registered correctly."""
        tools = await list_tools()

        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "list_invoices" in tool_names
        assert "get_invoice_detail" in tool_names

    @pytest.mark.asyncio
    async def test_call_list_invoices_tool(self):
        """Test calling list_invoices tool."""
        result = await call_tool("list_invoices", {"limit": 5})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found" in result[0].text
        assert "invoices" in result[0].text

    @pytest.mark.asyncio
    async def test_call_list_invoices_with_dates(self):
        """Test calling list_invoices tool with date parameters."""
        result = await call_tool(
            "list_invoices",
            {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "limit": 3
            }
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found" in result[0].text

    @pytest.mark.asyncio
    async def test_call_get_invoice_detail_tool(self):
        """Test calling get_invoice_detail tool."""
        result = await call_tool(
            "get_invoice_detail",
            {"invoice_id": "INV-00001"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Invoice Details" in result[0].text
        assert "INV-00001" in result[0].text

    @pytest.mark.asyncio
    async def test_call_get_invoice_detail_missing_id(self):
        """Test calling get_invoice_detail without invoice_id."""
        result = await call_tool("get_invoice_detail", {})

        assert len(result) == 1
        assert "Error" in result[0].text
        assert "required" in result[0].text

    @pytest.mark.asyncio
    async def test_call_unknown_tool(self):
        """Test calling an unknown tool."""
        result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0].text


class TestInvoiceModel:
    """Test Invoice model."""

    def test_invoice_creation(self):
        """Test creating an Invoice instance."""
        invoice = Invoice(
            invoice_id="TEST-001",
            invoice_number="2024000001",
            issue_date="2024-01-15",
            supplier_name="Test Supplier",
            customer_name="Test Customer",
            total_amount=1000.50,
            currency="TRY",
            status="approved"
        )

        assert invoice.invoice_id == "TEST-001"
        assert invoice.total_amount == 1000.50
        assert invoice.currency == "TRY"
        assert invoice.status == "approved"

    def test_invoice_model_validation(self):
        """Test Invoice model validation."""
        with pytest.raises(Exception):
            # Missing required fields should raise validation error
            Invoice(invoice_id="TEST-001")
