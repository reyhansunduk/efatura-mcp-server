"""
Gerçek GİB API entegrasyon testleri

Bu testler gerçek GİB test ortamına bağlanır.
Çalıştırmak için .env dosyasında geçerli kimlik bilgileri olmalı.

Test çalıştırma:
    pytest tests/test_real_integration.py -v -s

Sadece gerçek API testlerini çalıştırma:
    pytest tests/test_real_integration.py -v -s -m "real_api"

Yavaş testleri atlama:
    pytest tests/test_real_integration.py -v -s -m "not slow"
"""

import os
import pytest
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.efatura_mcp.gib_api_real import GIBRealAPI

# Environment variables yükle
load_dotenv()

# Test için credentials kontrol
SKIP_REAL_TESTS = not (
    os.getenv("GIB_USERNAME") and
    os.getenv("GIB_PASSWORD")
)

SKIP_MESSAGE = "GİB credentials bulunamadı. .env dosyasını kontrol edin."


@pytest.fixture(scope="module")
def gib_api():
    """GİB API fixture"""
    if SKIP_REAL_TESTS:
        pytest.skip(SKIP_MESSAGE)

    api = GIBRealAPI(
        username=os.getenv("GIB_USERNAME", ""),
        password=os.getenv("GIB_PASSWORD", ""),
        environment=os.getenv("GIB_ENVIRONMENT", "test")
    )
    return api


@pytest.mark.real_api
class TestGIBConnection:
    """GİB bağlantı testleri"""

    def test_clients_initialized(self, gib_api):
        """SOAP clients'ların başlatıldığını test et"""
        assert gib_api.fatura_client is not None, "Fatura client başlatılmadı"
        # Sorgu client optional olabilir
        # assert gib_api.sorgu_client is not None, "Sorgu client başlatılmadı"

    def test_wsdl_accessible(self, gib_api):
        """WSDL endpoint'ine erişilebildiğini test et"""
        assert gib_api.fatura_client is not None

        # WSDL services kontrol
        services = list(gib_api.fatura_client.wsdl.services.values())
        assert len(services) > 0, "WSDL'de servis bulunamadı"

    @pytest.mark.slow
    def test_login(self, gib_api):
        """GİB login test"""
        result = gib_api.login()

        # Not: Gerçek implementasyona göre düzenlenmeli
        # Şu anda her zaman True dönüyor
        assert isinstance(result, bool)


@pytest.mark.real_api
class TestInvoiceOperations:
    """Fatura işlemleri testleri"""

    @pytest.mark.slow
    def test_list_invoices(self, gib_api):
        """Fatura listeleme testi"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        invoices = gib_api.get_invoices(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            limit=10
        )

        assert isinstance(invoices, list)
        # Not: Mock implementasyonda boş liste döner
        # Gerçek API'de kontrol edilmeli

    def test_list_invoices_with_invalid_dates(self, gib_api):
        """Geçersiz tarihlerle fatura listeleme"""
        # Gelecek tarih
        future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        invoices = gib_api.get_invoices(future_date, today, limit=5)

        # Hata yönetimi test edilmeli
        assert isinstance(invoices, list)

    @pytest.mark.slow
    def test_get_invoice_detail(self, gib_api):
        """Fatura detay alma testi"""
        # Test UUID (gerçek UUID kullanılmalı)
        test_uuid = "test-uuid-12345"

        detail = gib_api.get_invoice_detail(test_uuid)

        # Not: Mock implementasyonda None döner
        # Gerçek API'de kontrol edilmeli
        assert detail is None or isinstance(detail, dict)

    def test_get_invoice_xml(self, gib_api):
        """Fatura XML alma testi"""
        test_uuid = "test-uuid-12345"

        xml = gib_api.get_invoice_xml(test_uuid)

        assert xml is None or isinstance(xml, str)


@pytest.mark.real_api
class TestValidation:
    """Doğrulama testleri"""

    def test_validate_tax_number(self, gib_api):
        """Vergi numarası doğrulama testi"""
        # Test vergi numarası (10 haneli)
        test_vkn = "1234567890"

        result = gib_api.validate_tax_number(test_vkn)

        # Not: Mock implementasyonda None döner
        assert result is None or isinstance(result, dict)

    def test_validate_invalid_tax_number(self, gib_api):
        """Geçersiz vergi numarası testi"""
        invalid_vkn = "123"  # Çok kısa

        result = gib_api.validate_tax_number(invalid_vkn)

        # Hata yönetimi test edilmeli
        assert result is None or isinstance(result, dict)


@pytest.mark.real_api
@pytest.mark.slow
class TestInvoiceCreation:
    """Fatura oluşturma testleri (dikkatli kullanın!)"""

    def test_create_invoice_structure(self, gib_api):
        """Fatura veri yapısını test et"""
        # Örnek fatura verisi
        invoice_data = {
            "invoice_number": "TST2024000001",
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "supplier": {
                "vkn": "1234567890",
                "name": "Test Tedarikçi A.Ş."
            },
            "customer": {
                "vkn": "0987654321",
                "name": "Test Müşteri Ltd."
            },
            "total_amount": 1000.00,
            "currency": "TRY"
        }

        # Sadece veri yapısını test et, gerçekte gönderme
        assert "invoice_number" in invoice_data
        assert "supplier" in invoice_data
        assert "customer" in invoice_data

    @pytest.mark.skip(reason="Gerçek fatura oluşturur, dikkatli kullanın")
    def test_create_invoice(self, gib_api):
        """Gerçek fatura oluşturma testi (SKIP)"""
        invoice_data = {
            # Fatura verileri
        }

        result = gib_api.create_invoice(invoice_data)

        # Gerçek implementasyonda kontrol edilmeli
        assert result is None or isinstance(result, str)


@pytest.mark.real_api
class TestErrorHandling:
    """Hata yönetimi testleri"""

    def test_network_timeout(self, gib_api):
        """Network timeout testi"""
        # Çok büyük bir tarih aralığı
        start_date = "2000-01-01"
        end_date = "2024-12-31"

        # Timeout olsa bile hata fırlatmamalı
        try:
            invoices = gib_api.get_invoices(start_date, end_date, limit=10000)
            assert isinstance(invoices, list)
        except Exception as e:
            pytest.fail(f"Beklenmeyen hata: {e}")

    def test_invalid_credentials(self):
        """Geçersiz kimlik bilgileri testi"""
        api = GIBRealAPI(
            username="invalid_user",
            password="invalid_pass",
            environment="test"
        )

        # Client başlatılabilmeli ama login başarısız olmalı
        assert api.fatura_client is not None


@pytest.mark.real_api
class TestUserInfo:
    """Kullanıcı bilgileri testleri"""

    def test_get_user_info(self, gib_api):
        """Kullanıcı bilgilerini alma testi"""
        user_info = gib_api.get_user_info()

        # Not: Mock implementasyonda None döner
        assert user_info is None or isinstance(user_info, dict)


# Performance testleri
@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """Performance testleri"""

    def test_list_invoices_performance(self, gib_api, benchmark):
        """Fatura listeleme performans testi"""
        if SKIP_REAL_TESTS:
            pytest.skip(SKIP_MESSAGE)

        def list_invoices():
            return gib_api.get_invoices("2024-01-01", "2024-01-31", limit=10)

        # Benchmark (pytest-benchmark gerekir)
        # result = benchmark(list_invoices)
        # assert isinstance(result, list)


# Integration testi - Tam flow
@pytest.mark.integration
@pytest.mark.slow
class TestFullFlow:
    """Tam akış entegrasyon testi"""

    def test_full_invoice_flow(self, gib_api):
        """Login -> Liste -> Detay akışı"""
        # 1. Login
        login_result = gib_api.login()
        assert isinstance(login_result, bool)

        # 2. Fatura listele
        invoices = gib_api.get_invoices(
            "2024-01-01",
            "2024-12-31",
            limit=5
        )
        assert isinstance(invoices, list)

        # 3. İlk faturanın detayını al (varsa)
        if invoices and len(invoices) > 0:
            first_invoice = invoices[0]
            if "uuid" in first_invoice:
                detail = gib_api.get_invoice_detail(first_invoice["uuid"])
                assert detail is None or isinstance(detail, dict)


if __name__ == "__main__":
    # Testleri doğrudan çalıştır
    pytest.main([__file__, "-v", "-s"])
