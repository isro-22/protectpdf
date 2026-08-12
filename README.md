# PDF Protector

Cross-platform Streamlit app for watermark-optional PDF protection.

## Features

- Optional diagonal watermark with opacity, size and rotation.
- Optional document ID and timestamp.
- AES-256 PDF encryption using PyMuPDF.
- Separate user and owner passwords.
- Copy/edit/annotation restrictions.
- Print blocking.
- Experimental print-blank mode using a rasterized page inside a PDF Optional Content Group (OCG) with `/PrintState /OFF`.
- Structural validation report.

## Important print-blank limitation

The PDF specification supports Optional Content Groups with print usage settings, and PyMuPDF supports OCG creation and encryption. However, PDF viewers are not required to honor every OCG print behavior identically. Therefore the app reports print-blank as experimental rather than claiming universal DRM.

## Run on macOS

```bash
./run_mac.command
```

or:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run on Windows

Double-click `run_windows.bat`, or:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
pytest -q
```

## Manual compatibility test

For the experimental print-blank mode, open the generated PDF in Adobe Acrobat/Reader, macOS Preview, Chrome, and Edge where available. Compare the on-screen view with the result of printing/saving through each viewer's PDF workflow. The automated validator only proves the PDF structure and permissions, not universal printer behavior.

## Copyright

© 2026 Muhammad Isro. Built by Muhammad Isro.
