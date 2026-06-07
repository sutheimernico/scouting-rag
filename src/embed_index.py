"""BGE-M3 dense indexing + retrieval via embedded Qdrant (cycle 1).

Cycle 1 uses the dense vectors only; sparse/multivector come with their
own cycles so deltas stay attributable. Qdrant runs in embedded mode
(local path, no server) — adequate at ~4.3k chunks.

CLI:
    python -m src.embed_index build          # encode corpus + build index
    python -m src.embed_index search "..."   # smoke-test a query
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.corpus import Chunk, load_corpus

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = REPO_ROOT / "data" / "qdrant"
COLLECTION = "scouting_dense_v1"
EMB_DIM = 1024  # BGE-M3 dense dimension
BATCH_SIZE = 16  # CPU-friendly

_model = None


def get_model():
    """Lazy singleton — loading BGE-M3 takes ~10s and ~2.5 GB RAM."""
    global _model
    if _model is None:
        from FlagEmbedding import BGEM3FlagModel

        _model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=False)  # CPU: fp32
    return _model


def encode_dense(texts: list[str]) -> list[list[float]]:
    out = get_model().encode(texts, batch_size=BATCH_SIZE, max_length=1024)
    return [v.tolist() for v in out["dense_vecs"]]


class DenseIndex:
    def __init__(self, path: Path = INDEX_DIR, collection: str = COLLECTION) -> None:
        self.client = QdrantClient(path=str(path))
        self.collection = collection

    def build(self, chunks: list[Chunk]) -> None:
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
        self.client.create_collection(
            self.collection,
            vectors_config=VectorParams(size=EMB_DIM, distance=Distance.COSINE),
        )
        t0 = time.monotonic()
        for start in range(0, len(chunks), 128):
            batch = chunks[start : start + 128]
            vectors = encode_dense([c.text for c in batch])
            points = [
                PointStruct(
                    id=start + i,
                    vector=vectors[i],
                    payload={
                        "chunk_id": c.chunk_id,
                        "doc_id": c.doc_id,
                        "text": c.text,
                        "source_class": c.source_class,
                    },
                )
                for i, c in enumerate(batch)
            ]
            self.client.upsert(self.collection, points)
            done = start + len(batch)
            rate = done / (time.monotonic() - t0)
            print(f"  indexed {done}/{len(chunks)} ({rate:.1f} chunks/s)", flush=True)

    def search(self, query: str, k: int = 10) -> list[dict]:
        [vector] = encode_dense([query])
        hits = self.client.query_points(self.collection, query=vector, limit=k).points
        return [{**(h.payload or {}), "score": h.score} for h in hits]


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        chunks = load_corpus()
        print(f"building dense index over {len(chunks)} chunks ...")
        t0 = time.monotonic()
        DenseIndex().build(chunks)
        print(f"done in {time.monotonic() - t0:.0f}s -> {INDEX_DIR}")
    elif cmd == "search":
        index = DenseIndex()
        for hit in index.search(" ".join(sys.argv[2:]), k=5):
            print(f"  {hit['score']:.3f} [{hit['doc_id']}] {hit['text'][:110]}")
    else:
        raise SystemExit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
