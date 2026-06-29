"""Run baidu/Unlimited-OCR on a cloud GPU via Modal — the model's native CUDA/bf16
config, so none of the local Apple-Silicon problems (OOM, bf16-on-MPS garbage) apply.

ONE-TIME SETUP (on your Mac):
    pip install modal
    modal token new          # opens browser, links your Modal account (free tier covers this)

RUN (renders pages locally? no — sends the PDF bytes to the GPU, writes .md back here):
    modal run ocr_modal.py                                   # default 710-11 doc
    modal run ocr_modal.py --pdf submissions/sc103cb3-688-1-50-ec.pdf
    modal run ocr_modal.py --pdf submissions/foo.pdf --prompt "<image>document parsing."

Cost: L4 ~= $0.80/hr, scales to zero between runs. First run downloads the 6.7 GB
model into a persistent Modal Volume (cached for all later runs). A 14-page doc ~3 min.

ponytail: per-page infer (not infer_multi) — robust to any page failing, and these
submissions are short letters; long-horizon multi-page mode buys nothing here.
"""
import os
import re
import modal

MODEL_ID = "baidu/Unlimited-OCR"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "torch", "transformers==4.57.1", "pymupdf", "pillow", "einops",
        "addict", "matplotlib", "requests", "torchvision", "easydict",
    )
    # transformers MUST be 4.57.1 — 5.x removed is_torch_fx_available and the
    # model's DeepSeek-V2 code won't import.
)

hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
app = modal.App("unlimited-ocr")


@app.cls(gpu="L4", image=image, volumes={"/root/.cache/huggingface": hf_cache},
         timeout=3600, scaledown_window=120)
class OCR:
    @modal.enter()
    def load(self):
        import torch
        from transformers import AutoModel, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        # native config on real CUDA: bf16 + eager attn (skips the flash-attn build).
        self.model = AutoModel.from_pretrained(
            MODEL_ID, trust_remote_code=True, torch_dtype=torch.bfloat16,
            attn_implementation="eager",
        ).eval().cuda()
        hf_cache.commit()  # persist downloaded weights to the Volume

    @modal.method()
    def ocr(self, pdf_bytes: bytes, dpi: int = 220,
            prompt: str = "<image>Free OCR.") -> str:
        import fitz, tempfile, os, glob
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        tmp = tempfile.mkdtemp()
        pages = []
        for i in range(doc.page_count):
            img = os.path.join(tmp, f"p{i:03d}.png")
            doc[i].get_pixmap(dpi=dpi).save(img)
            out_dir = tempfile.mkdtemp()
            ret = self.model.infer(
                self.tok, prompt=prompt, image_file=img, output_path=out_dir,
                base_size=1024, image_size=640, crop_mode=True, max_length=32768,
                no_repeat_ngram_size=35, ngram_window=128, save_results=True)
            files = sorted(f for f in glob.glob(os.path.join(out_dir, "**", "*"),
                                                recursive=True)
                           if os.path.isfile(f) and f.lower().endswith((".md", ".mmd", ".txt")))
            text = ("\n\n".join(open(f, encoding="utf-8").read() for f in files)
                    or (str(ret) if ret else ""))
            text = re.sub(r"!\[[^\]]*\]\([^)]*\)\s*", "", text).strip()  # drop image placeholders
            pages.append(text)
            print(f"page {i+1}/{doc.page_count}: {len(text)} chars", flush=True)

        header = ("立法會掃描本 — Unlimited-OCR (GPU/bf16) 自動辨識，未經人手校對\n\n")
        body = "\n\n".join(f"<!-- page {i+1} -->\n{t}" for i, t in enumerate(pages))
        return header + body + "\n"


@app.local_entrypoint()
def main(pdf: str = "submissions/sc103cb3-710-11-c.pdf",
         prompt: str = "<image>Free OCR.", dpi: int = 220):
    data = open(pdf, "rb").read()
    text = OCR().ocr.remote(data, dpi=dpi, prompt=prompt)
    out = f"submissions/md/{os.path.splitext(os.path.basename(pdf))[0]}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nWROTE {out} ({len(text)} chars)")
    print("----- first 1500 chars -----")
    print(text[:1500])
