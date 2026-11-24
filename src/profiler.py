"""Run workloads across the experiment matrix and record telemetry."""

from __future__ import annotations

import datetime
import json
import os
import statistics

from .engine import Engine


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 2) if values else None


def _iqr(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return round(q3 - q1, 2)


class Profiler:
    def __init__(self, config: dict, prompts: dict, results_dir: str):
        self.config = config
        self.all_workloads = prompts.get("workloads", prompts)
        self.results_dir = results_dir
        self.raw_dir = os.path.join(results_dir, "raw")
        self.repeats = int(config.get("repeats", 3))
        self.warmup = bool(config.get("warmup", True))

    def run(self) -> list[dict]:
        os.makedirs(self.raw_dir, exist_ok=True)
        rows = []
        for experiment in self.config["experiments"]:
            engine = Engine(experiment, self.config, self.raw_dir).start()
            try:
                selected = experiment.get("workloads")
                workloads = (
                    [w for w in self.all_workloads if w["name"] in selected]
                    if selected
                    else self.all_workloads
                )
                for workload in workloads:
                    rows.append(self._measure(engine, experiment, workload))
            finally:
                engine.stop()

        path = os.path.join(self.results_dir, "results.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(
                {"generated_at": datetime.datetime.now().isoformat(timespec="seconds"), "results": rows},
                handle,
                indent=2,
            )
        return rows

    def _measure(self, engine: Engine, experiment: dict, workload: dict) -> dict:
        messages = [{"role": "user", "content": workload["prompt"]}]
        max_tokens = workload.get("max_tokens", 128)

        # One untimed pass settles mmap page faults and CPU clocks.
        if self.warmup:
            engine.chat(messages, max_tokens)
        samples = [self._sample(engine, messages, max_tokens) for _ in range(self.repeats)]

        speeds = [s["decode_tps"] for s in samples if s["decode_tps"] is not None]
        prefills = [s["prefill_tps"] for s in samples if s["prefill_tps"] is not None]
        accepts = [s["acceptance_pct"] for s in samples if s["acceptance_pct"] is not None]
        speculation = experiment.get("speculation") or {}

        return {
            "experiment": experiment["name"],
            "quantization": experiment.get("quantization", "unknown"),
            "speculation": speculation.get("method", "none") if speculation.get("enabled") else "none",
            "n_ctx": experiment.get("n_ctx", 0),
            "workload": workload["name"],
            "workload_type": workload.get("type", "text"),
            "prefill_tps": _median(prefills),
            "prefill_tps_iqr": _iqr(prefills),
            "decode_tps": _median(speeds),
            "decode_tps_iqr": _iqr(speeds),
            "acceptance_pct": _median(accepts),
            "rss_mb": round(max(s["rss_mb"] for s in samples), 1),
            "runs": samples,
        }

    def _sample(self, engine: Engine, messages: list[dict], max_tokens: int) -> dict:
        response = engine.chat(messages, max_tokens)
        timings = response.get("timings", {})
        predicted_n = timings.get("predicted_n", 0)
        draft_n = timings.get("draft_n", 0)
        accepted_n = timings.get("draft_n_accepted", 0)
        # Fewer than 8 decode tokens is an early-EOS outlier, not a speed.
        decode_tps = round(timings.get("predicted_per_second", 0.0), 2) if predicted_n >= 8 else None
        return {
            "decode_tps": decode_tps,
            "prefill_tps": round(timings.get("prompt_per_second", 0.0), 2),
            "acceptance_pct": round(accepted_n / draft_n * 100, 1) if draft_n else None,
            "decode_tokens": predicted_n,
            "rss_mb": round(engine.rss_mb(), 1),
        }
