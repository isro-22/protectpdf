import pymupdf
from core.models import ProtectionConfig, PrintMode, WatermarkConfig
from core.protect import protect_pdf

def sample_pdf():
    d=pymupdf.open(); p=d.new_page(); p.insert_text((50,50),"SECRET CONTENT"); return d.tobytes()

def test_aes256_protection_requires_password():
    out=protect_pdf(sample_pdf(), ProtectionConfig(user_password="user", owner_password="owner", print_mode=PrintMode.BLOCK), WatermarkConfig(False))
    d=pymupdf.open(stream=out, filetype="pdf")
    assert d.is_encrypted and d.needs_pass
    assert d.authenticate("user") > 0
    assert d.permissions & pymupdf.PDF_PERM_PRINT == 0

def test_print_allow_sets_print_permission():
    out=protect_pdf(sample_pdf(), ProtectionConfig(owner_password="owner", print_mode=PrintMode.ALLOW), WatermarkConfig(False))
    d=pymupdf.open(stream=out, filetype="pdf"); d.authenticate("owner")
    assert d.permissions & pymupdf.PDF_PERM_PRINT
