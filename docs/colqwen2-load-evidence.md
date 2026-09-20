# Cycle 5 / ColQwen2: weight-loading evidence

Committed diagnostic evidence for the cycle-5 close (`results.md`, cycle-5
section). Captured 2026-09-20 on the retrieval re-run, environment unchanged
from the original cycle-5 run: `colpali_engine==0.3.16`,
`transformers==5.10.2`, CPU only.

**Finding in one line:** loading `vidore/colqwen2-v1.0` in this environment
silently drops *the entire LoRA fine-tune of the language backbone* plus the
backbone's embedding table and final norm, because the checkpoint names the
backbone `model.*` while the instantiated architecture expects
`language_model.*`. What actually ran was an untuned Qwen2-VL backbone with a
randomly initialized embedding table — not ColQwen2.

## 1. What transformers reports on load (verbatim)

```
[transformers] ColQwen2 LOAD REPORT from: vidore/colqwen2-base
Key                                | Status
-----------------------------------+------------
model.embed_tokens.weight          | UNEXPECTED
model.norm.weight                  | UNEXPECTED
language_model.embed_tokens.weight | MISSING
language_model.norm.weight         | MISSING
```

```
[transformers] ColQwen2 LOAD REPORT from: vidore/colqwen2-v1.0
Key                                                                   | Status
----------------------------------------------------------------------+------------
model.layers.{0...27}.self_attn.{q,k,v,o}_proj.lora_{A,B}.default.weight | UNEXPECTED
model.layers.{0...27}.mlp.{gate,up,down}_proj.lora_{A,B}.default.weight  | UNEXPECTED
language_model.layers.{0...27}.self_attn.{q,k,v,o}_proj.lora_{A,B}.default.weight | MISSING
language_model.layers.{0...27}.mlp.{gate,up,down}_proj.lora_{A,B}.default.weight  | MISSING
```

That is **14 tensor families × 28 layers = 392 LoRA tensors** reported missing
and newly initialized — every adapter weight of the retrieval fine-tune on the
language side. `custom_text_proj` (the projection head, which sits outside the
backbone) is *not* in either list: it loads correctly, which is why the model
still produces plausibly-shaped multi-vector output and nothing crashes.

## 2. Layer statistics of the loaded model

Measured by inspecting the loaded state dict directly (original cycle-5 run,
reproduced twice — once inside the eval harness, once via a standalone
`python -m src.visual_index search` call):

| Parameter | mean | std | Interpretation |
|---|---|---|---|
| `language_model.norm.weight` | 1.0 | 0.0 | all-ones vector — the default init of an RMSNorm, never a trained value |
| `language_model.embed_tokens.weight` | ~0 | 0.0200 | the textbook default init std for an embedding layer |

These two numbers are the check a fix has to pass: after a successful remap,
neither may hold.

## 3. Where the mismatch comes from (checkpoint side)

Reading the safetensors headers directly — no model instantiation needed:

```python
import json, struct
def keys(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        return list(json.loads(f.read(n)))
```

| Checkpoint | tensors | backbone prefix used |
|---|---|---|
| `vidore/colqwen2-base` (`model-0000{1,2}-of-00002.safetensors`) | 731 | `model.*` (plus `visual.*`, `custom_text_proj.*`) |
| `vidore/colqwen2-v1.0` (`adapter_model.safetensors`) | 394 | `base_model.model.model.layers.*` (PEFT naming over the same `model.*` backbone) |

The instantiated `ColQwen2` under `transformers==5.10.2` exposes the backbone
as `language_model.*`. Pip's metadata (`transformers<6.0.0,>=5.3.0`) cannot
catch this: it is a runtime key-naming drift, not a version-range violation.

## 4. The specified fix (not applied — see the cycle-5 close)

A state-dict key-remapping shim at load time in `src/visual_index.py`:
for every checkpoint key `model.<rest>` whose counterpart
`language_model.<rest>` exists in the instantiated model's state dict, assign
the tensor under the expected name before the weights are used. Deliberately
**not** a global `transformers` downgrade: the same virtualenv also serves
`bge-reranker-v2-m3` (`AutoModelForSequenceClassification`) and BGE-M3, and
breaking cycles 1–4's tooling to rescue cycle 5 is the wrong trade.

Verification a fix must pass, in order:

1. The two layer statistics in section 2 must no longer hold.
2. Both LOAD REPORTs must come back empty.
3. A 3–5 page spot-check embedding run must produce MaxSim scores that
   separate the correct page from the rest.
4. Only then is the ~8.2 h full re-index worth starting — the cached
   `data/visual_index.pt` was built with the broken weights and is unusable.

## 5. Note on checkpoint drift

The Hugging Face cache resolved `vidore/colqwen2-v1.0` to a newer repository
revision on 2026-09-20 than on the original run (`2b6ac8fb…` vs
`83a0134c…`). The weight blob is byte-identical in both snapshots
(`adapter_model.safetensors` resolves to the same blob hash); only auxiliary
files (chat templates, processor config) changed. The re-run is therefore
comparable to the original one.
