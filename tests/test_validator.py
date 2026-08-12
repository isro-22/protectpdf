import pymupdf
from core.models import ProtectionConfig, PrintMode, WatermarkConfig
from core.protect import protect_pdf
from core.validator import validate_pdf

def sample_pdf():
    d=pymupdf.open(); p=d.new_page(); p.insert_text((50,50),"HELLO"); return d.tobytes()

def test_validator_reports_encryption_and_ocg():
    out=protect_pdf(sample_pdf(), ProtectionConfig(owner_password="owner", print_mode=PrintMode.BLANK_EXPERIMENTAL), WatermarkConfig(False))
    r=validate_pdf(out, password="owner")
    assert r["pdf_valid"] and r["encryption_ok"] and r["print_blank_ocg_present"]

def test_validator_reports_watermark_after_authentication():
    out=protect_pdf(sample_pdf(), ProtectionConfig(owner_password="owner"), WatermarkConfig(True, text="SECRET", rotation=0))
    r=validate_pdf(out, watermark_text="SECRET", password="owner")
    assert r["watermark_text_found"] is True
