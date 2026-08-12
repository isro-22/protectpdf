from datetime import datetime, timezone
import pymupdf
from .models import WatermarkConfig

def apply_watermark(doc: pymupdf.Document, config: WatermarkConfig, document_id: str = "") -> None:
    if not config.enabled:
        return
    text = config.text.strip() or "CONFIDENTIAL"
    extras = []
    if config.add_document_id and document_id:
        extras.append(f"ID: {document_id}")
    if config.add_timestamp:
        extras.append(datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"))
    if config.username.strip():
        extras.append(f"USER: {config.username.strip()}")
    footer = " • ".join(extras)
    for page in doc:
        rect = page.rect
        # Rotated diagonal watermark. Opacity is represented by the PDF graphics state.
        page.insert_textbox(
            pymupdf.Rect(rect.width * 0.08, rect.height * 0.40, rect.width * 0.92, rect.height * 0.60),
            text,
            fontsize=config.font_size,
            fontname="helv",
            color=(0.55, 0.55, 0.55),
            align=pymupdf.TEXT_ALIGN_CENTER,
            rotate=(int(config.rotation) // 90) * 90 % 360,
            overlay=True,
            fill_opacity=max(0.0, min(1.0, config.opacity)),
            stroke_opacity=0,
        )
        if footer:
            page.insert_text(
                (rect.x0 + 18, rect.y1 - 18), footer,
                fontsize=8, fontname="helv", color=(0.45, 0.45, 0.45),
                fill_opacity=max(0.0, min(1.0, config.opacity)),
                overlay=True,
            )
