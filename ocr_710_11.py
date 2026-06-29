"""OCR scanned/image submission PDFs with Unlimited-OCR (Baidu's doc VLM).

Uses the device-agnostic fork `sabafallah/Unlimited-OCR-Universal` so it runs on
Apple Silicon without a GPU. Quality is markedly better than the old PaddleOCR pass
(correct zh-Hant, headings vs. body, citations) — see git history for the PaddleOCR
version if you ever need it back.

Setup (one-time, isolated venv — keeps these heavy deps out of the global env):
    python3 -m venv .venv-ocr
    .venv-ocr/bin/pip install torch "transformers==4.57.1" pymupdf pillow einops \
        addict matplotlib requests torchvision easydict
    # transformers MUST be 4.57.1 — 5.x removed is_torch_fx_available and the
    # fork's DeepSeek-V2 code won't import.

Run (CPU + float32 is the only config that both fits 19 GB RAM and stays accurate):
    .venv-ocr/bin/python ocr_710_11.py                                  # default 710-11
    .venv-ocr/bin/python ocr_710_11.py submissions/sc103cb3-XXX-c.pdf   # any scanned PDF

~2 min/page on an M3 Pro CPU. For a big batch, use ocr_modal.py (same model, GPU, ~10x).

ponytail: default device=cpu, NOT mps — mps float32 OOM-kills on 19 GB and mps bf16
produces degenerate output (the fork's own caveat). cpu uses unified RAM + swap and
stays correct. Override with OCR_DEVICE=cuda on a GPU box.
"""
import os, sys, re, time, glob, tempfile

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")           # avoid the xet writer bug
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
import fitz  # PyMuPDF
from transformers import AutoModel, AutoTokenizer

MODEL_ID = "sabafallah/Unlimited-OCR-Universal"
DEFAULT_PDF = "submissions/sc103cb3-710-11-c.pdf"
DPI = 220
PROMPT = "<image>Free OCR."

_t0 = time.time()
def log(m): print(f"[{time.time() - _t0:7.1f}s] {m}", flush=True)

DEVICE = os.environ.get("OCR_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.bfloat16 if DEVICE == "cuda" else torch.float32

log(f"loading model on {DEVICE} ({DTYPE}); first run downloads ~6.7 GB")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModel.from_pretrained(
    MODEL_ID, trust_remote_code=True, dtype=DTYPE, attn_implementation="eager",
).eval().to(DEVICE)
log("model loaded")


def read_result(out_dir):
    """infer(save_results=True) writes the parsed markdown here; filename undocumented."""
    files = sorted(f for f in glob.glob(os.path.join(out_dir, "**", "*"), recursive=True)
                   if os.path.isfile(f) and f.lower().endswith((".md", ".mmd", ".txt")))
    text = "\n\n".join(open(f, encoding="utf-8").read() for f in files)
    # drop the model's image placeholders (e.g. logos) — no images saved, text-only archive
    return re.sub(r"!\[[^\]]*\]\([^)]*\)\s*", "", text)


def ocr_pdf(pdf_path):
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    out_md = f"submissions/md/{stem}.md"
    doc = fitz.open(pdf_path)
    log(f"{stem}: {doc.page_count} pages @ {DPI} DPI")
    tmp = tempfile.mkdtemp()
    pages = []
    for i in range(doc.page_count):
        img = os.path.join(tmp, f"p{i:03d}.png")
        doc[i].get_pixmap(dpi=DPI).save(img)
        out_dir = tempfile.mkdtemp()
        ret = model.infer(
            tokenizer, prompt=PROMPT, image_file=img, output_path=out_dir,
            base_size=1024, image_size=640, crop_mode=True, max_length=32768,
            no_repeat_ngram_size=35, ngram_window=128, save_results=True)
        text = (read_result(out_dir) or (str(ret) if ret else "")).strip()
        pages.append(text)
        log(f"  page {i+1}/{doc.page_count}: {len(text)} chars")

    header = ("立法會掃描本 — Unlimited-OCR 自動辨識，未經人手校對\n"
              f"（來源 {os.path.basename(pdf_path)}）\n\n")
    body = "\n\n".join(f"<!-- page {i+1} -->\n{t}" for i, t in enumerate(pages))
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(header + body + "\n")
    log(f"WROTE {out_md} ({len(header + body)} chars)")


for pdf in (sys.argv[1:] or [DEFAULT_PDF]):
    ocr_pdf(pdf)
