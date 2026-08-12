import hashlib
import streamlit as st
from core.models import ProtectionConfig, PrintMode, WatermarkConfig
from core.protect import protect_pdf
from core.validator import validate_pdf

st.set_page_config(page_title="PDF Protector", page_icon="🔐", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --apple-blue: #0071e3;
        --apple-blue-hover: #0077ed;
        --apple-text: #1d1d1f;
        --apple-gray: #86868b;
        --apple-bg: #f5f5f7;
        --apple-border: #e5e5e7;
    }
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
            "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }
    .block-container {
        max-width: 880px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }
    h1, h2, h3 {
        color: var(--apple-text) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    [data-testid="stCaptionContainer"] {
        color: var(--apple-gray) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        border: 1px solid var(--apple-border) !important;
        box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
        background: #ffffff;
        padding: 0.25rem 0.5rem;
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: 980px;
        padding: 0.55rem 1.8rem;
        font-weight: 500;
        border: none;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="primary"], .stDownloadButton > button {
        background: var(--apple-blue);
        color: white;
    }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
        background: var(--apple-blue-hover);
        color: white;
        transform: scale(1.02);
    }
    div[data-testid="stMetric"] {
        background: var(--apple-bg);
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
    }
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 16px;
        border: 2px dashed #d2d2d7;
        background: var(--apple-bg);
    }
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: 10px !important;
    }
    hr {
        border-color: var(--apple-border);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center; padding: 0.5rem 0 2rem;">
        <div style="font-size:2.75rem; line-height:1;">🔐</div>
        <h1 style="margin: 0.4rem 0 0.2rem;">PDF Protector</h1>
        <p style="color: var(--apple-gray); font-size: 1.05rem; margin: 0;">
            Protect, watermark, and lock down your PDFs — simply and securely.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    uploaded = st.file_uploader("Upload a PDF to get started", type=["pdf"])

if uploaded:
    data = uploaded.getvalue()

    st.write("")
    with st.container(border=True):
        import pymupdf
        d = pymupdf.open(stream=data, filetype="pdf")
        c1, c2, c3 = st.columns(3)
        c1.metric("Pages", d.page_count)
        c2.metric("Size", f"{len(data) / 1024:.1f} KB")
        c3.metric("SHA-256", hashlib.sha256(data).hexdigest()[:12])
        d.close()

    st.write("")
    with st.container(border=True):
        st.subheader("Watermark")
        wm_enabled = st.checkbox("Enable watermark", value=False)
        wm_text = st.text_input("Watermark text", "CONFIDENTIAL", disabled=not wm_enabled)
        a, b, c = st.columns(3)
        opacity = a.slider("Opacity", 0.05, 1.0, 0.20, 0.05, disabled=not wm_enabled)
        size = b.slider("Font size", 12, 96, 48, disabled=not wm_enabled)
        rotation = c.select_slider("Rotation", options=[0, 90, 180, 270], value=0, disabled=not wm_enabled)
        x, y, z = st.columns(3)
        add_id = x.checkbox("Add document ID", False, disabled=not wm_enabled)
        add_ts = y.checkbox("Add timestamp", False, disabled=not wm_enabled)
        username = z.text_input("Username", disabled=not wm_enabled)
        document_id = st.text_input("Document ID", "DOC-001")

    st.write("")
    with st.container(border=True):
        st.subheader("Protection")
        mode = st.radio(
            "Print protection",
            ["Block printing", "Print blank (experimental)", "Allow printing"],
            index=0,
        )
        print_mode = {
            "Block printing": PrintMode.BLOCK,
            "Print blank (experimental)": PrintMode.BLANK_EXPERIMENTAL,
            "Allow printing": PrintMode.ALLOW,
        }[mode]
        u1, u2 = st.columns(2)
        user_pass = u1.text_input("User password (optional)", type="password")
        owner_pass = u2.text_input("Owner password", type="password", value="owner-change-me")
        q1, q2, q3 = st.columns(3)
        disable_copy = q1.checkbox("Disable copy", True)
        disable_edit = q2.checkbox("Disable edit", True)
        disable_ann = q3.checkbox("Disable annotation", True)

    st.write("")
    _, btn_col, _ = st.columns([1, 1, 1])
    protect_clicked = btn_col.button("🔐 Protect PDF", type="primary", use_container_width=True)

    if protect_clicked:
        if not owner_pass:
            st.error("Owner password is required.")
        else:
            try:
                wm = WatermarkConfig(wm_enabled, wm_text, opacity, size, rotation, add_id, add_ts, username)
                cfg = ProtectionConfig(user_pass, owner_pass, disable_copy, disable_edit, disable_ann, print_mode)
                result = protect_pdf(data, cfg, wm, document_id)
                st.session_state["result"] = result
                st.session_state["report"] = validate_pdf(result, wm_text if wm_enabled else None, password=owner_pass)
                st.success("PDF processed. Review the validation report below.")
            except Exception as e:
                st.exception(e)

    if "report" in st.session_state:
        st.write("")
        with st.container(border=True):
            st.subheader("Validation")
            r = st.session_state["report"]
            st.json(r)
            if print_mode == PrintMode.BLANK_EXPERIMENTAL:
                st.warning("Print-blank is experimental and viewer-dependent. The structural OCG test is not a universal physical print guarantee.")
            st.download_button(
                "⬇️ Download protected PDF",
                st.session_state["result"],
                file_name=f"{uploaded.name.rsplit('.', 1)[0]}_protected.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
else:
    st.info("Upload a PDF above to begin.")

st.write("")
st.divider()
st.markdown(
    """
    <div style="text-align:center; opacity:0.7; font-size:0.85rem; line-height:1.6;">
        <strong>PDF Protector</strong> — Cross-platform PDF protection and watermarking tool<br>
        Developed and maintained by <strong>Muhammad Isro</strong><br>
        © 2026 Muhammad Isro. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True,
)
