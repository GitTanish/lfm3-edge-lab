"""Run workloads across the experiment matrix and record telemetry."""

from __future__ import annotations

import datetime
import json
import os

from .engine import Engine


def _tokens_per_second(count: float, ms: float) -> float:
    return count / (ms / 1000) if ms else 0.0


class Profiler:
    def __init__(self, config: dict, prompts: dict, results_dir: str):
        self.config = config
        self.all_workloads = prompts.get("workloads", prompts)
        self.results_dir = results_dir
        self.raw_dir = os.path.join(results_dir, "raw")

    def run(self) -> list[dict]:
        os.makedirs(self.raw_dir, exist_ok=True)
        rows = []
        for experiment in self.config["experiments"]:
            engine = Engine(experiment, self.config, self.raw_dir).start()
            try:
                # First request loads the prompt cache and kernels; exclude it.
                if self.config.get("warmup", True):
                    engine.complete("hello", 8)
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
        response = engine.complete(workload["prompt"], workload.get("max_tokens", 128))
        timings = response.get("timings", {})
        prompt_n, prompt_ms = timings.get("prompt_n", 0), timings.get("prompt_ms", 0)
        predicted_n, predicted_ms = timings.get("predicted_n", 0), timings.get("predicted_ms", 0)
        draft_n = timings.get("draft_n", 0)
        accepted_n = timings.get("draft_n_accepted", 0)
        speculation = experiment.get("speculation") or {}
        # A 1-token EOS response has ~0 ms decode; its rate is meaningless.
        decode_tps = round(_tokens_per_second(predicted_n, predicted_ms), 2) if predicted_n > 1 and predicted_ms >= 1 else None

        return {
            "experiment": experiment["name"],
            "quantization": experiment.get("quantization", "unknown"),
            "speculation": speculation.get("method", "none") if speculation.get("enabled") else "none",
            "n_ctx": experiment.get("n_ctx", 0),
            "workload": workload["name"],
            "workload_type": workload.get("type", "text"),
            "prompt_tokens": prompt_n,
            "prefill_ms": round(prompt_ms, 2),
            "prefill_tps": round(_tokens_per_second(prompt_n, prompt_ms), 2),
            "decode_tokens": predicted_n,
            "decode_tps": decode_tps,
            "acceptance_rate": round(accepted_n / draft_n, 3) if draft_n else None,
            "rss_mb": round(engine.rss_mb(), 1),
        }
