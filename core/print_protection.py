import io
import pymupdf
from PIL import Image

PRINT_NOTICE_TEXT = "This document cannot be printed."


def _enable_print_autostate(doc: pymupdf.Document, content_ocg: int, notice_ocg: int) -> None:
    """Register an OCG usage-application (/AS) entry for the Print event.

    An OCG's own /Usage/Print/PrintState dictionary is only advisory: per the
    PDF spec (ISO 32000-1 8.11.4.4), conforming readers only apply it
    automatically if the OCG configuration dictionary (/OCProperties/D) also
    carries a matching /AS (application state) entry for that event. Without
    this, Acrobat/Preview/Chrome etc. keep the content visible when printing,
    which is why printed output previously still showed the real page.
    """
    catalog = doc.pdf_catalog()
    as_entry = (
        "[ "
        f"<< /Event /Print /OCGs [ {content_ocg} 0 R ] /Category [ /Print ] >> "
        f"<< /Event /Print /OCGs [ {notice_ocg} 0 R ] /Category [ /Print ] >> "
        "]"
    )
    doc.xref_set_key(catalog, "OCProperties/D/AS", as_entry)


def make_print_blank_pdf(source: pymupdf.Document) -> pymupdf.Document:
    """Create a rasterized PDF that renders normally on screen but is meant to
    print as a blank page bearing a "cannot be printed" notice.

    Two OCGs are used:
      - content: visible on screen, PrintState OFF (hidden when printing).
      - notice: hidden on screen, PrintState ON (shown only when printing).

    This is deliberately experimental: OCG print-usage auto-state is only
    honored by readers that implement it (e.g. Adobe Acrobat/Reader). Readers
    that ignore OCG print semantics entirely (many browser-embedded viewers)
    will still print the real content. The PDF permission flags for this mode
    intentionally still allow printing, since the goal is a blank/notice
    printout rather than a disabled print button - use "Block printing" for a
    hard permission-level block. The validator checks PDF structure, not a
    universal physical print result.
    """
    out = pymupdf.open()
    content_ocg = out.add_ocg("Screen Content - Print Hidden", on=True, intent="View", usage="Artwork")
    out.xref_set_key(content_ocg, "Usage/Print", "<< /PrintState /OFF >>")

    notice_ocg = out.add_ocg("Print Blocked Notice", on=False, intent="View", usage="Artwork")
    out.xref_set_key(notice_ocg, "Usage/Print", "<< /PrintState /ON >>")

    _enable_print_autostate(out, content_ocg, notice_ocg)

    for page in source:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.8, 1.8), alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        new_page = out.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=buf.getvalue(), oc=content_ocg)
        new_page.insert_textbox(
            new_page.rect,
            PRINT_NOTICE_TEXT,
            fontsize=24,
            fontname="helv",
            color=(0, 0, 0),
            align=pymupdf.TEXT_ALIGN_CENTER,
            oc=notice_ocg,
        )
    source.close()
    return out
