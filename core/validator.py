import pymupdf


def validate_pdf(data: bytes, watermark_text: str | None = None, expect_encrypted=True, password: str | None = None) -> dict:
    result = {}
    doc = pymupdf.open(stream=data, filetype="pdf")
    result["pdf_valid"] = doc.page_count > 0
    result["page_count"] = doc.page_count
    result["encrypted"] = bool(doc.metadata.get("encryption")) or doc.xref_get_key(-1, "Encrypt")[0] != "null"
    result["needs_password"] = bool(doc.needs_pass)
    if doc.needs_pass and password:
        result["authenticated"] = doc.authenticate(password) > 0
    else:
        result["authenticated"] = not doc.needs_pass
    if expect_encrypted:
        result["encryption_ok"] = result["encrypted"]
    else:
        result["encryption_ok"] = True
    if watermark_text and not doc.needs_pass:
        text = "\n".join(page.get_text() for page in doc)
        result["watermark_text_found"] = watermark_text in text
    else:
        result["watermark_text_found"] = None
    result["permissions"] = int(doc.permissions) if not doc.needs_pass else None
    result["print_allowed"] = bool(doc.permissions & pymupdf.PDF_PERM_PRINT) if not doc.needs_pass else None
    ocgs = doc.get_ocgs() if not doc.needs_pass else {}
    result["ocg_count"] = len(ocgs)
    result["print_blank_ocg_present"] = any("Screen Content - Print Hidden" in str(v.get("name", "")) for v in ocgs.values())
    doc.close()
    return result
