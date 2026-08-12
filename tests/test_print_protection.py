import pymupdf
from core.models import ProtectionConfig, PrintMode, WatermarkConfig
from core.protect import protect_pdf
from core.validator import validate_pdf

def sample_pdf():
    d=pymupdf.open(); p=d.new_page(); p.insert_text((50,50),"SECRET CONTENT"); return d.tobytes()

def test_print_blank_mode_creates_print_hidden_ocg():
    out=protect_pdf(sample_pdf(), ProtectionConfig(owner_password="owner", print_mode=PrintMode.BLANK_EXPERIMENTAL), WatermarkConfig(False))
    d=pymupdf.open(stream=out, filetype="pdf"); d.authenticate("owner")
    ocgs=d.get_ocgs()
    assert any(v.get("name")=="Screen Content - Print Hidden" for v in ocgs.values())
    assert any(v.get("name")=="Print Blocked Notice" for v in ocgs.values())
    raw="\n".join(d.xref_object(x, compressed=False) for x in ocgs)
    assert "/PrintState /OFF" in raw
    assert "/PrintState /ON" in raw

def test_print_blank_mode_registers_auto_state_for_print_event():
    # Without a /D/AS entry, readers ignore each OCG's own /Usage/Print
    # dictionary and keep printing the real content (ISO 32000-1 8.11.4.4).
    out=protect_pdf(sample_pdf(), ProtectionConfig(owner_password="owner", print_mode=PrintMode.BLANK_EXPERIMENTAL), WatermarkConfig(False))
    d=pymupdf.open(stream=out, filetype="pdf"); d.authenticate("owner")
    catalog=d.pdf_catalog()
    as_raw=d.xref_get_key(catalog, "OCProperties/D/AS")[1].replace(" ","")
    assert "/Event/Print" in as_raw
    assert "/Category[/Print]" in as_raw

def test_print_blank_mode_hides_content_and_shows_notice_when_print_event_applied():
    out=protect_pdf(sample_pdf(), ProtectionConfig(owner_password="owner", print_mode=PrintMode.BLANK_EXPERIMENTAL), WatermarkConfig(False))
    d=pymupdf.open(stream=out, filetype="pdf"); d.authenticate("owner")
    ocgs=d.get_ocgs()
    content=[x for x,v in ocgs.items() if v.get("name")=="Screen Content - Print Hidden"][0]
    notice=[x for x,v in ocgs.items() if v.get("name")=="Print Blocked Notice"][0]
    # Screen (default) state: rasterized content image visible, notice hidden.
    assert len(d[0].get_images()) == 1
    assert "This document cannot be printed." not in d[0].get_text()
    # Simulate the print event applying each OCG's PrintState.
    d.set_layer(-1, on=[notice], off=[content])
    data2=d.tobytes(garbage=0, deflate=False, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    d2=pymupdf.open(stream=data2, filetype="pdf"); d2.authenticate("owner")
    printed_text=d2[0].get_text()
    assert "This document cannot be printed." in printed_text

