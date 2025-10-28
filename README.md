# e-Fatura MCP Server

[English](#english) | [Türkçe](#türkçe)

---

## English

### Overview

e-Fatura MCP Server is a Model Context Protocol (MCP) server that provides integration with the Turkish Tax Authority (GIB) e-Invoice (e-Fatura) system. This server enables AI assistants and applications to interact with the e-Fatura system through standardized MCP tools.

### Features

- List e-Fatura invoices with optional date filtering
- Retrieve detailed invoice information
- SOAP client integration with GIB e-Fatura web services
- Pydantic models for type-safe data handling
- Comprehensive test coverage

### Available Tools

#### `list_invoices`
List e-Fatura invoices from the GIB system.

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of invoices to return (default: 10)

**Returns:** List of invoices with basic information

#### `get_invoice_detail`
Get detailed information for a specific e-Fatura invoice.

**Parameters:**
- `invoice_id` (required): Invoice ID to retrieve details for

**Returns:** Detailed invoice information including supplier, customer, amounts, and status

### Installation

1. Clone the repository:
```bash
git clone https://github.com/reyhansunduk/efatura-mcp-server.git
cd efatura-mcp-server
```

2. Install dependencies:
```bash
pip install -e .
```

Or install with development dependencies:
```bash
pip install -e ".[dev]"
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Configure your GIB credentials in `.env`:
```env
GIB_USERNAME=your_gib_username
GIB_PASSWORD=your_gib_password
GIB_ENVIRONMENT=test  # or "production"
```

### Usage

#### Running the Server

Start the MCP server:
```bash
python -m efatura_mcp.server
```

#### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "efatura": {
      "command": "python",
      "args": ["-m", "efatura_mcp.server"],
      "cwd": "/path/to/efatura-mcp-server"
    }
  }
}
```

### Development

#### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=efatura_mcp --cov-report=html
```

#### Code Quality

Format code:
```bash
black src tests
```

Run linter:
```bash
ruff check src tests
```

Type checking:
```bash
mypy src
```

### Project Structure

```
efatura-mcp-server/
├── src/
│   └── efatura_mcp/
│       ├── __init__.py
│       └── server.py          # Main MCP server implementation
├── tests/
│   ├── __init__.py
│   └── test_server.py         # Unit tests
├── .env.example               # Environment variables template
├── .gitignore
├── pyproject.toml             # Project configuration
└── README.md
```

### Requirements

- Python 3.10+
- mcp >= 0.9.0
- zeep >= 4.2.1
- lxml >= 5.0.0
- python-dotenv >= 1.0.0
- pydantic >= 2.5.0

### License

MIT License

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Türkçe

### Genel Bakış

e-Fatura MCP Server, Türkiye Gelir İdaresi Başkanlığı (GİB) e-Fatura sistemi ile entegrasyon sağlayan bir Model Context Protocol (MCP) sunucusudur. Bu sunucu, yapay zeka asistanlarının ve uygulamalarının e-Fatura sistemi ile standartlaştırılmış MCP araçları üzerinden etkileşimde bulunmasını sağlar.

### Özellikler

- e-Fatura faturalarını listeleme (opsiyonel tarih filtreleme ile)
- Detaylı fatura bilgilerini alma
- GİB e-Fatura web servisleri ile SOAP entegrasyonu
- Tip güvenli veri işleme için Pydantic modelleri
- Kapsamlı test kapsama alanı

### Mevcut Araçlar

#### `list_invoices`
GİB sisteminden e-Fatura faturalarını listeler.

**Parametreler:**
- `start_date` (opsiyonel): Başlangıç tarihi (YYYY-MM-DD formatında)
- `end_date` (opsiyonel): Bitiş tarihi (YYYY-MM-DD formatında)
- `limit` (opsiyonel): Döndürülecek maksimum fatura sayısı (varsayılan: 10)

**Döndürür:** Temel bilgilerle birlikte fatura listesi

#### `get_invoice_detail`
Belirli bir e-Fatura faturası için detaylı bilgi alır.

**Parametreler:**
- `invoice_id` (zorunlu): Detayları alınacak fatura ID'si

**Döndürür:** Tedarikçi, müşteri, tutarlar ve durum bilgilerini içeren detaylı fatura bilgisi

### Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/yourusername/efatura-mcp-server.git
cd efatura-mcp-server
```

2. Bağımlılıkları yükleyin:
```bash
pip install -e .
```

Veya geliştirme bağımlılıkları ile:
```bash
pip install -e ".[dev]"
```

3. Örnek dosyadan `.env` dosyası oluşturun:
```bash
cp .env.example .env
```

4. `.env` dosyasında GİB kimlik bilgilerinizi yapılandırın:
```env
GIB_USERNAME=gib_kullanici_adiniz
GIB_PASSWORD=gib_sifreniz
GIB_ENVIRONMENT=test  # veya "production"
```

### Kullanım

#### Sunucuyu Çalıştırma

MCP sunucusunu başlatın:
```bash
python -m efatura_mcp.server
```

#### Claude Desktop ile Kullanım

Claude Desktop yapılandırmanıza ekleyin (`~/Library/Application Support/Claude/claude_desktop_config.json` macOS'ta):

```json
{
  "mcpServers": {
    "efatura": {
      "command": "python",
      "args": ["-m", "efatura_mcp.server"],
      "cwd": "/path/to/efatura-mcp-server"
    }
  }
}
```

### Geliştirme

#### Testleri Çalıştırma

```bash
pytest
```

Kapsama raporu ile:
```bash
pytest --cov=efatura_mcp --cov-report=html
```

#### Kod Kalitesi

Kodu biçimlendir:
```bash
black src tests
```

Linter çalıştır:
```bash
ruff check src tests
```

Tip kontrolü:
```bash
mypy src
```

### Proje Yapısı

```
efatura-mcp-server/
├── src/
│   └── efatura_mcp/
│       ├── __init__.py
│       └── server.py          # Ana MCP sunucu implementasyonu
├── tests/
│   ├── __init__.py
│   └── test_server.py         # Birim testler
├── .env.example               # Ortam değişkenleri şablonu
├── .gitignore
├── pyproject.toml             # Proje yapılandırması
└── README.md
```

### Gereksinimler

- Python 3.10+
- mcp >= 0.9.0
- zeep >= 4.2.1
- lxml >= 5.0.0
- python-dotenv >= 1.0.0
- pydantic >= 2.5.0

### Lisans

MIT License

### Katkıda Bulunma

Katkılar memnuniyetle karşılanır! Lütfen Pull Request göndermekten çekinmeyin.

---

## Support / Destek

For issues and questions, please open an issue on GitHub.

Sorunlar ve sorular için lütfen GitHub'da bir issue açın.
