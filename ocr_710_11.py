"""OCR the scanned union submission CB(3)710/2026(11), sc103cb3-710-11-c.pdf.
PaddleOCR's package init pulls in langchain (for a RAG retriever we don't use) and
the installed langchain is too new (langchain.docstore etc. removed). Stub any
missing langchain* submodule so the import succeeds; OCR itself doesn't need it.
ponytail: stub via meta-path finder, not by downgrading the user's langchain.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("CPU_NUM_THREADS", "1")
os.environ.setdefault("FLAGS_use_mkldnn", "0")
import sys, types, importlib.abc, importlib.machinery

class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, name, path, target=None):
        root = name.split(".")[0]
        if root in ("langchain", "langchain_community"):
            return importlib.machinery.ModuleSpec(name, self)
        return None
    def create_module(self, spec):
        m = types.ModuleType(spec.name)
        m.__path__ = []  # mark as package so submodule imports keep resolving
        return m
    def exec_module(self, module):
        # any attribute access returns a fresh dummy class
        module.__getattr__ = lambda n: type(str(n), (), {})
sys.meta_path.insert(0, _StubFinder())

import fitz  # PyMuPDF
from paddleocr import PaddleOCR

PDF = "submissions/sc103cb3-710-11-c.pdf"
OUT = "submissions/md/sc103cb3-710-11-c.md"
DPI = 220

ocr = PaddleOCR(
    lang="chinese_cht",
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

doc = fitz.open(PDF)
pages_text = []
import tempfile, os
tmp = tempfile.mkdtemp()
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=DPI)
    img_path = os.path.join(tmp, f"p{i:02d}.png")
    pix.save(img_path)
    res = ocr.predict(img_path)
    lines = []
    for r in res:
        d = r if isinstance(r, dict) else getattr(r, "json", {})
        texts = d.get("rec_texts") or []
        lines.extend(t for t in texts if t and t.strip())
    pages_text.append("\n".join(lines))
    print(f"page {i+1}/{doc.page_count}: {sum(len(l) for l in lines)} chars", flush=True)

body = "\n\n".join(f"<!-- page {i+1} -->\n{t}" for i, t in enumerate(pages_text))
header = "立法會CB(3)710/2026(11)號文件 — 汽車交通運輸業總工會\n（PaddleOCR chinese_cht 自動辨識，掃描本，未經人手校對）\n\n"
open(OUT, "w", encoding="utf-8").write(header + body + "\n")
print("WROTE", OUT, "total chars:", len(header + body))
