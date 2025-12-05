# e-Fatura MCP Server

Türkiye Gelir İdaresi Başkanlığı (GİB) e-Arşiv Fatura sistemi ile entegrasyon sağlayan MCP sunucusu.

[English](#english) | [Türkçe](#türkçe)

---

## English

### Features

- 📋 List and search e-Invoices
- 🔍 Get invoice details and XML
- ✏️ Create and cancel invoices
- ✅ Validate Turkish tax numbers (VKN/TCKN)
- 🎭 **Demo mode** - Test without real credentials
- 🔒 **Production ready** - Auto-switching between demo and real API

### Quick Start

#### 1. Install

```bash
git clone https://github.com/reyhansunduk/efatura-mcp-server.git
cd efatura-mcp-server
pip install -e .
```

#### 2. Demo Mode (No credentials needed)

The server works immediately with mock data:

```bash
python -m efatura_mcp.server
```

For test: `⚠️ DEMO MODE: Using mock data`

#### 3. Use with Claude Desktop

Create config file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "efatura": {
      "command": "python",
      "args": ["-m", "efatura_mcp.server"],
      "cwd": "C:\\path\\to\\efatura-mcp-server"
    }
  }
}
```

#### 4. Test in Claude Desktop

Ask Claude:
```
List invoices
```

You should see 5 demo invoices!

### Switch to Real GİB API

When ready to use real data:

1. Edit `.env` file:
```env
GIB_USERNAME=your_vkn_here
GIB_PASSWORD=your_password_here
GIB_ENVIRONMENT=test
```

2. Restart the server

The server automatically switches to real API when credentials are provided.

### Available MCP Tools

The server provides 7 MCP tools that Claude can use:

#### 1. `list_invoices`
List e-Fatura invoices from GIB system.

**Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Max invoices to return (default: 10)

**Example:** "Show me invoices from last month"

#### 2. `get_invoice_detail`
Get detailed information for a specific invoice.

**Parameters:**
- `invoice_id` (required): Invoice ID/UUID

**Example:** "Show details for invoice ABC2024000001"

#### 3. `get_invoice_xml`
Get invoice HTML/XML content in UBL-TR format.

**Parameters:**
- `invoice_id` (required): Invoice ID/UUID

**Example:** "Get XML for invoice ABC2024000001"

#### 4. `create_invoice`
Create new e-Fatura invoice in GIB system.

**Parameters:**
- `invoice_number`, `issue_date`, `supplier_vkn`, `supplier_name`
- `customer_vkn`, `customer_name`, `items[]`, `total_amount`
- `currency` (optional, default: TRY)

**Example:** "Create invoice for 1000 TRY to customer XYZ"

#### 5. `cancel_invoice`
Cancel an existing invoice.

**Parameters:**
- `invoice_id` (required): Invoice ID to cancel
- `reason` (required): Cancellation reason

**Example:** "Cancel invoice ABC2024000001 due to error"

#### 6. `search_invoices`
Search invoices with filters.

**Parameters:**
- `customer_name`, `supplier_name` (optional)
- `min_amount`, `max_amount` (optional)
- `status` (optional): approved, pending, cancelled

**Example:** "Find invoices over 10000 TRY", "Show pending invoices"

#### 7. `validate_tax_number`
Validate Turkish tax number (VKN/TCKN).

**Parameters:**
- `tax_number` (required): 10 or 11 digit tax number

**Example:** "Validate tax number 1234567890"

### Getting GİB Credentials

**Get Credentials:** Use your company's existing e-Fatura credentials
- Portal: https://earsivportal.efatura.gov.tr (production)
- Test Portal: https://earsivportaltest.efatura.gov.tr (test)

### Project Structure

```
efatura-mcp-server/
├── src/
│   └── efatura_mcp/
│       ├── server.py           # Main MCP server
│       ├── gib_earsiv_client.py # Real GİB API client
│       └── mock_data.py        # Demo data
├── .env                        # Credentials (gitignored)
├── .env.example               # Template
└── README.md
```

See [SECURITY.md](SECURITY.md) for complete guidelines.

### Requirements

- Python 3.10+
- Claude Desktop (or any MCP client)

Dependencies are auto-installed with `pip install -e .`

### License

MIT

---

## Türkçe


### Özellikler

- 📋 e-Faturaları listele ve ara
- 🔍 Fatura detayları ve XML al
- ✏️ Fatura oluştur ve iptal et
- ✅ Vergi numarası doğrula (VKN/TCKN)
- 🎭 **Demo modu** - Gerçek credentials olmadan test et
- 🔒 **Production hazır** - Demo ve gerçek API arası otomatik geçiş

### Hızlı Başlangıç

#### 1. Kurulum

```bash
git clone https://github.com/reyhansunduk/efatura-mcp-server.git
cd efatura-mcp-server
pip install -e .
```

#### 2. Demo Modu (Credential gerekmez)

Sunucu hemen mock data ile çalışır:

```bash
python -m efatura_mcp.server
```

Test için: `⚠️ DEMO MODE: Using mock data`

#### 3. Claude Desktop ile Kullan

Config dosyası oluştur:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "efatura": {
      "command": "python",
      "args": ["-m", "efatura_mcp.server"],
      "cwd": "C:\\Users\\..\\efatura-mcp-server"
    }
  }
}
```

#### 4. Claude Desktop'ta Test Et

Claude'a sor:
```
Faturaları listele
```

Faturalar listelenecektir.

### Gerçek GİB API'ye Geç

Gerçek veri kullanmaya hazır olduğunda:

1. `.env` dosyasını düzenle:
```env
GIB_USERNAME=vkn_buraya
GIB_PASSWORD=sifre_buraya
GIB_ENVIRONMENT=test
```

2. Sunucuyu yeniden başlat

Sunucu credentials verildiğinde otomatik olarak gerçek API'ye geçer.

### Mevcut MCP Araçları

Sunucu Claude'un kullanabileceği 7 MCP aracı sağlar:

#### 1. `list_invoices`
GİB sisteminden e-Faturaları listeler.

**Parametreler:**
- `start_date` (opsiyonel): Başlangıç tarihi (YYYY-MM-DD)
- `end_date` (opsiyonel): Bitiş tarihi (YYYY-MM-DD)
- `limit` (opsiyonel): Max fatura sayısı (varsayılan: 10)

**Örnek:** "Geçen ayki faturaları göster"

#### 2. `get_invoice_detail`
Belirli bir faturanın detaylı bilgilerini getirir.

**Parametreler:**
- `invoice_id` (zorunlu): Fatura ID/UUID

**Örnek:** "ABC2024000001 faturasının detaylarını göster"

#### 3. `get_invoice_xml`
Fatura HTML/XML içeriğini UBL-TR formatında getirir.

**Parametreler:**
- `invoice_id` (zorunlu): Fatura ID/UUID

**Örnek:** "ABC2024000001 faturasının XML'ini getir"

#### 4. `create_invoice`
GİB sisteminde yeni e-Fatura oluşturur.

**Parametreler:**
- `invoice_number`, `issue_date`, `supplier_vkn`, `supplier_name`
- `customer_vkn`, `customer_name`, `items[]`, `total_amount`
- `currency` (opsiyonel, varsayılan: TRY)

**Örnek:** "XYZ müşterisine 1000 TRY fatura oluştur"

#### 5. `cancel_invoice`
Mevcut faturayı iptal eder.

**Parametreler:**
- `invoice_id` (zorunlu): İptal edilecek fatura ID
- `reason` (zorunlu): İptal sebebi

**Örnek:** "ABC2024000001 faturasını hata nedeniyle iptal et"

#### 6. `search_invoices`
Filtrelerle fatura ara.

**Parametreler:**
- `customer_name`, `supplier_name` (opsiyonel)
- `min_amount`, `max_amount` (opsiyonel)
- `status` (opsiyonel): approved, pending, cancelled

**Örnek:** "10000 TL üzeri faturaları bul", "Beklemedeki faturaları göster"

#### 7. `validate_tax_number`
Türk vergi numarasını doğrula (VKN/TCKN).

**Parametreler:**
- `tax_number` (zorunlu): 10 veya 11 haneli vergi numarası

**Örnek:** "1234567890 vergi numarasını doğrula"

### GİB Credentials Nasıl Alınır

**Nasıl Yapılır:** Şirketinin mevcut e-Fatura credentials'ını kullan
- Portal: https://earsivportal.efatura.gov.tr (canlı)
- Test Portal: https://earsivportaltest.efatura.gov.tr (test)

### Proje Yapısı

```
efatura-mcp-server/
├── src/
│   └── efatura_mcp/
│       ├── server.py           # Ana MCP sunucu
│       ├── gib_earsiv_client.py # Gerçek GİB API client
│       └── mock_data.py        # Demo verisi
├── .env                        #  credentials'ın (gitignored)
├── .env.example               # Şablon
└── README.md
```

Tam rehber için [SECURITY.md](SECURITY.md)'ye bak.


### Gereksinimler

- Python 3.10+
- Claude Desktop (veya herhangi bir MCP client)

Bağımlılıklar `pip install -e .` ile otomatik kurulur.

### Lisans

MIT

---

## Support / Destek

For issues and questions, please open an issue on GitHub.

Sorunlar ve sorular için lütfen GitHub'da bir issue açın.
