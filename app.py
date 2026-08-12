import hashlib
import streamlit as st
from core.models import ProtectionConfig, PrintMode, WatermarkConfig
from core.protect import protect_pdf
from core.validator import validate_pdf

st.set_page_config(page_title="PDF DRM Protector", page_icon="🔐", layout="wide")
st.title("🔐 PDF DRM Protector")
st.caption("Cross-platform PDF protection for macOS and Windows")

uploaded = st.file_uploader("Upload PDF", type=["pdf"])
if uploaded:
    data = uploaded.getvalue()
    c1,c2,c3=st.columns(3)
    import pymupdf
    d=pymupdf.open(stream=data,filetype="pdf")
    c1.metric("Pages", d.page_count); c2.metric("Size", f"{len(data)/1024:.1f} KB"); c3.metric("SHA-256", hashlib.sha256(data).hexdigest()[:12])
    d.close()

    st.subheader("Watermark")
    wm_enabled=st.checkbox("Enable watermark", value=False)
    wm_text=st.text_input("Watermark text", "CONFIDENTIAL", disabled=not wm_enabled)
    a,b,c=st.columns(3)
    opacity=a.slider("Opacity",0.05,1.0,0.20,0.05,disabled=not wm_enabled)
    size=b.slider("Font size",12,96,48,disabled=not wm_enabled)
    rotation=c.select_slider("Rotation", options=[0, 90, 180, 270], value=0, disabled=not wm_enabled)
    x,y,z=st.columns(3)
    add_id=x.checkbox("Add document ID",False,disabled=not wm_enabled)
    add_ts=y.checkbox("Add timestamp",False,disabled=not wm_enabled)
    username=z.text_input("Username",disabled=not wm_enabled)
    document_id=st.text_input("Document ID", "DOC-001")

    st.subheader("Protection")
    mode=st.radio("Print protection", ["Block printing", "Print blank (experimental)", "Allow printing"], index=0)
    print_mode={"Block printing":PrintMode.BLOCK,"Print blank (experimental)":PrintMode.BLANK_EXPERIMENTAL,"Allow printing":PrintMode.ALLOW}[mode]
    u1,u2=st.columns(2)
    user_pass=u1.text_input("User password (optional)",type="password")
    owner_pass=u2.text_input("Owner password",type="password",value="owner-change-me")
    q1,q2,q3=st.columns(3)
    disable_copy=q1.checkbox("Disable copy",True); disable_edit=q2.checkbox("Disable edit",True); disable_ann=q3.checkbox("Disable annotation",True)

    if st.button("🔐 Protect PDF", type="primary"):
        if not owner_pass:
            st.error("Owner password is required.")
        else:
            try:
                wm=WatermarkConfig(wm_enabled,wm_text,opacity,size,rotation,add_id,add_ts,username)
                cfg=ProtectionConfig(user_pass,owner_pass,disable_copy,disable_edit,disable_ann,print_mode)
                result=protect_pdf(data,cfg,wm,document_id)
                st.session_state["result"]=result
                st.session_state["report"]=validate_pdf(result, wm_text if wm_enabled else None, password=owner_pass)
                st.success("PDF processed. Review the validation report below.")
            except Exception as e:
                st.exception(e)

    if "report" in st.session_state:
        st.subheader("Validation")
        r=st.session_state["report"]
        st.json(r)
        if print_mode==PrintMode.BLANK_EXPERIMENTAL:
            st.warning("Print-blank is experimental and viewer-dependent. The structural OCG test is not a universal physical print guarantee.")
        st.download_button("⬇️ Download protected PDF",st.session_state["result"],file_name=f"{uploaded.name.rsplit(".",1)[0]}_protected.pdf",mime="application/pdf")
else:
    st.info("Upload a PDF to begin.")
