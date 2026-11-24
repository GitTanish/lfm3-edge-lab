# lfm3-edge-lab

Empirical CPU inference and quantization profiler for **Liquid AI's LFM3-1.7B** tri-hybrid architecture (`13x Gated Short Conv + 5x Sliding-Window GQA + 6x Global GQA`) running on memory-constrained consumer hardware (**11th-Gen Intel Core i3, 8GB RAM**) via `llama.cpp`.

## What This Benchmarks
1. **QAD vs. PTQ on CPU:** Compares Liquid AI's Quantization-Aware Distilled `Q4_0` checkpoint against standard Post-Training Quantized `Q4_K_M` and `Q8_0` across decode throughput (`tok/s`), prefill speed, and peak RSS memory.
2. **Tri-Hybrid KV Cache Scaling:** Measures RAM footprint growth from `2K` to `32K` context tokens, verifying how capping 18/24 layers to fixed ring buffers prevents swap thrashing on an 8GB laptop.
3. **Speculative Lookup Gain:** Evaluates `ngram-simple` / prompt-lookup speculation on structured JSON and tool-calling workloads versus open-ended generation.

## Setup

### 1. Install `llama.cpp` (Windows)
```powershell
winget install --id ggml.llamacpp --exact --source winget
```

### 2. Install Python Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Download LFM3-1.7B GGUF Checkpoints
```powershell
hf download LiquidAI/LFM3-1.7B-GGUF `
  LFM3-1.7B-QAD-Q4_0.gguf `
  LFM3-1.7B-Q4_K_M.gguf `
  LFM3-1.7B-Q8_0.gguf --local-dir ./models
```

### 4. Run the Benchmark Suite
```powershell
python main.py
```

## Results

Measured on the target i3 / 8GB machine with `llama-server` b12648 (Vulkan build, `-ngl 0`). Full table: [`results/report.md`](results/report.md).

| Config | Decode tok/s | RSS MB |
| --- | --- | --- |
| QAD Q4_0 2K | 8.1–10.1 | 1,318–1,348 |
| PTQ Q4_K_M 2K | 12.9–13.4 | 1,370–1,400 |
| PTQ Q8_0 2K | 9.0–9.2 | 2,113–2,137 |

- **KV scaling (QAD, 2K→32K):** RSS grows 1,318 → 1,730 MB (~412 MB for 30K extra context), with decode holding ~11.2–11.5 tok/s on the JSON workload.
- **Speculative lookup:** `ngram-simple` acceptance was 59.8% on repetitive tool calls (16.3 vs 8.8 tok/s baseline) but only 2.6% on JSON (no gain). Prompt-lookup speculation pays off when output reuses long prompt n-grams.
- **Q8_0 reasoning** emitted EOS on the first token, so its decode rate is reported as `—`.

![Decode roofline](results/roofline.png)

These are single-run numbers; run-to-run variance was visible (roughly ±20% on the 2K JSON rows), so re-run `python main.py` before drawing fine-grained conclusions.
