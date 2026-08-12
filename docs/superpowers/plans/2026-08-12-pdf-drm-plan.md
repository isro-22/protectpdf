# PDF DRM Streamlit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cross-platform Streamlit app for watermark-optional PDF protection with AES-256 encryption, permissions, and an experimental print-blank OCG mode, plus automated PDF validation.

**Architecture:** PyMuPDF is the single PDF engine. Watermarking is added as page content when enabled. Standard mode uses PDF permissions/encryption; print-blank mode rasterizes each page into an Optional Content Group whose PDF print usage state is OFF, so compatible viewers can display it but omit it during printing. The validator checks PDF integrity, encryption, permissions, watermark presence, and OCG structure; it does not falsely claim universal print-blank support.

**Tech Stack:** Python 3.11+, Streamlit, PyMuPDF, Pillow, pytest.

## Global Constraints

- Cross-platform: macOS and Windows.
- Watermark is optional.
- AES-256 encryption is used when encryption is enabled.
- Standard print blocking and experimental print-blank are separate modes.
- Print-blank is explicitly compatibility-dependent and must be reported as experimental.
- No physical printer is required for automated structural tests.
- No original PDF is modified in place.

---

### Task 1: PDF processing primitives

**Files:**
- Create: `core/models.py`
- Create: `core/watermark.py`
- Create: `core/protect.py`
- Test: `tests/test_watermark.py`
- Test: `tests/test_protect.py`

- [ ] **Step 1: Write failing tests** for optional watermark, AES encryption, and print permissions.
- [ ] **Step 2: Run tests and confirm expected failures.**
- [ ] **Step 3: Implement minimal PyMuPDF processing.**
- [ ] **Step 4: Run tests and confirm pass.**
- [ ] **Step 5: Commit `feat: add pdf protection primitives`.**

### Task 2: Experimental print-blank layer

**Files:**
- Create: `core/print_protection.py`
- Test: `tests/test_print_protection.py`

- [ ] **Step 1: Write failing test for a Print Blank OCG and PrintState OFF usage dictionary.**
- [ ] **Step 2: Run and confirm failure.**
- [ ] **Step 3: Implement rasterized page insertion into an OCG and add `/Usage << /Print << /PrintState /OFF >> >>`.**
- [ ] **Step 4: Run tests and confirm pass.**
- [ ] **Step 5: Commit `feat: add experimental print blank layer`.**

### Task 3: Validation and Streamlit UI

**Files:**
- Create: `core/validator.py`
- Create: `app.py`
- Create: `tests/test_validator.py`
- Create: `README.md`

- [ ] **Step 1: Write failing validator tests.**
- [ ] **Step 2: Run and confirm failure.**
- [ ] **Step 3: Implement validator and Streamlit workflow.**
- [ ] **Step 4: Run full test suite.**
- [ ] **Step 5: Commit `feat: add streamlit ui and validator`.**

### Task 4: Cross-platform packaging and verification

**Files:**
- Create: `run_mac.command`
- Create: `run_windows.bat`
- Create: `.gitignore`

- [ ] **Step 1: Add platform launchers.**
- [ ] **Step 2: Run `pytest -q`.**
- [ ] **Step 3: Run a Streamlit import smoke test.**
- [ ] **Step 4: Inspect generated PDF structure with PyMuPDF.**
- [ ] **Step 5: Commit `chore: add cross platform launchers`.**
