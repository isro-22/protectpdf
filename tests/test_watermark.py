import pymupdf
from core.models import WatermarkConfig
from core.watermark import apply_watermark

def test_watermark_is_optional():
    doc = pymupdf.open(); page = doc.new_page(); page.insert_text((50, 50), "HELLO")
    apply_watermark(doc, WatermarkConfig(enabled=False), "DOC-1")
    assert "CONFIDENTIAL" not in page.get_text()

def test_watermark_enabled_adds_text():
    doc = pymupdf.open(); page = doc.new_page(); page.insert_text((50, 50), "HELLO")
    apply_watermark(doc, WatermarkConfig(enabled=True, text="SECRET", rotation=0), "DOC-1")
    assert "SECRET" in page.get_text()
