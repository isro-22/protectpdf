from pathlib import Path
import pymupdf
from .models import ProtectionConfig, PrintMode
from .watermark import apply_watermark
from .print_protection import make_print_blank_pdf


def permission_flags(config: ProtectionConfig) -> int:
    flags = int(pymupdf.PDF_PERM_ACCESSIBILITY)
    if config.print_mode == PrintMode.ALLOW:
        flags |= int(pymupdf.PDF_PERM_PRINT | pymupdf.PDF_PERM_PRINT_HQ)
    elif config.print_mode == PrintMode.BLANK_EXPERIMENTAL:
        # Printing is permitted at PDF permission level; the page content is
        # assigned to an OCG whose print usage state is OFF.
        flags |= int(pymupdf.PDF_PERM_PRINT | pymupdf.PDF_PERM_PRINT_HQ)
    if not config.disable_copy:
        flags |= int(pymupdf.PDF_PERM_COPY)
    if not config.disable_annotation:
        flags |= int(pymupdf.PDF_PERM_ANNOTATE)
    if not config.disable_edit:
        flags |= int(pymupdf.PDF_PERM_MODIFY | pymupdf.PDF_PERM_ASSEMBLE | pymupdf.PDF_PERM_FORM)
    return flags


def protect_pdf(input_bytes: bytes, config: ProtectionConfig, watermark=None, document_id="") -> bytes:
    doc = pymupdf.open(stream=input_bytes, filetype="pdf")
    if doc.needs_pass:
        raise ValueError("Input PDF is password protected. Decrypt it before processing.")
    apply_watermark(doc, watermark, document_id) if watermark else None

    if config.print_mode == PrintMode.BLANK_EXPERIMENTAL:
        doc = make_print_blank_pdf(doc)

    owner = config.owner_password or "generated-owner-password"
    user = config.user_password or ""
    out = doc.tobytes(
        garbage=4,
        deflate=True,
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw=owner,
        user_pw=user,
        permissions=permission_flags(config),
    )
    doc.close()
    return out
