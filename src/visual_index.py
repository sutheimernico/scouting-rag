"""Cycle 5: visual retrieval over stat-sheet images (ColQwen2, late interaction).

Pages are embedded once into multi-vector representations (one vector per
image patch); queries score against pages via MaxSim:

    score(Q, P) = sum_i max_j (q_i · p_j)

At 84 pages, brute-force MaxSim in torch is trivial, transparent and
testable — no vector DB needed for the visual path. Page embeddings are
cached to data/visual_index.pt.

Retrieval results carry "page_id" (= doc_id of the golden set's image
ground truth), which the eval matcher already understands.

    python -m src.visual_index build
    python -m src.visual_index search "xAG Perzentil Grimaldo"
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parent.parent
SHEETS_DIR = REPO_ROOT / "data" / "statsheets"
INDEX_FILE = REPO_ROOT / "data" / "visual_index.pt"

MODEL_NAME = "vidore/colqwen2-v1.0"

_model = None
_processor = None


def get_model():
    """Lazy load; bf16 halves RAM on CPU, falls back to fp32 if unsupported."""
    global _model, _processor
    if _model is None:
        from colpali_engine.models import ColQwen2, ColQwen2Processor

        dtype = torch.bfloat16
        try:
            torch.zeros(2, dtype=dtype) @ torch.zeros(2, dtype=dtype)
        except RuntimeError:
            dtype = torch.float32
        _model = ColQwen2.from_pretrained(MODEL_NAME, torch_dtype=dtype, device_map="cpu").eval()
        _processor = ColQwen2Processor.from_pretrained(MODEL_NAME)
        torch.set_grad_enabled(False)
    assert _model is not None and _processor is not None
    return _model, _processor


def maxsim(query_emb: torch.Tensor, page_embs: list[torch.Tensor]) -> list[float]:
    """MaxSim scores of one query against many pages.

    query_emb: (q_tokens, dim); each page: (p_patches, dim).
    """
    scores = []
    q = query_emb.float()
    for page in page_embs:
        sim = q @ page.float().T  # (q_tokens, p_patches)
        scores.append(float(sim.max(dim=1).values.sum()))
    return scores


def build() -> None:
    from PIL import Image

    model, processor = get_model()
    files = sorted(SHEETS_DIR.glob("*.png"))
    print(f"embedding {len(files)} pages ...", flush=True)
    embeddings: list[torch.Tensor] = []
    t0 = time.monotonic()
    for i, path in enumerate(files, 1):
        image = Image.open(path)
        batch = processor.process_images([image])
        emb = model(**batch).squeeze(0)  # (patches, dim)
        embeddings.append(emb.to(torch.float16).cpu())
        if i % 10 == 0:
            rate = i / (time.monotonic() - t0)
            print(f"  {i}/{len(files)} ({rate:.2f} pages/s)", flush=True)
    torch.save(
        {"page_ids": [f"statsheets/{p.name}" for p in files], "embeddings": embeddings},
        INDEX_FILE,
    )
    print(f"saved -> {INDEX_FILE} in {time.monotonic() - t0:.0f}s")


class VisualIndex:
    def __init__(self) -> None:
        data = torch.load(INDEX_FILE, weights_only=True)
        self.page_ids: list[str] = data["page_ids"]
        self.embeddings: list[torch.Tensor] = data["embeddings"]

    def search(self, query: str, k: int = 10) -> list[dict]:
        model, processor = get_model()
        batch = processor.process_queries([query])
        query_emb = model(**batch).squeeze(0)
        scores = maxsim(query_emb, self.embeddings)
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [{"page_id": self.page_ids[i], "doc_id": self.page_ids[i], "score": scores[i]} for i in order]


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "search":
        index = VisualIndex()
        for hit in index.search(" ".join(sys.argv[2:]), k=5):
            print(f"  {hit['score']:.1f} {hit['page_id']}")
    else:
        raise SystemExit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
