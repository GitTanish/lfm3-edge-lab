"""Build the Markdown summary and PNG roofline chart from profiler output."""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLUMNS = [
    ("experiment", "Experiment"),
    ("quantization", "Quant"),
    ("speculation", "Spec"),
    ("n_ctx", "Ctx"),
    ("workload_type", "Workload"),
    ("prefill_tps", "Prefill tok/s"),
    ("decode_tps", "Decode tok/s"),
    ("decode_tps_iqr", "IQR"),
    ("acceptance_pct", "Accept %"),
    ("rss_mb", "RSS MB"),
]


def _load(results_dir: str) -> list[dict]:
    with open(os.path.join(results_dir, "results.json"), encoding="utf-8") as handle:
        return json.load(handle)["results"]


def _markdown(rows: list[dict], path: str) -> None:
    lines = [
        "# Benchmark results",
        "",
        f"{len(rows)} measurements across {len({r['experiment'] for r in rows})} configurations.",
        "",
        "| " + " | ".join(title for _, title in COLUMNS) + " |",
        "| " + " | ".join("---" for _ in COLUMNS) + " |",
    ]
    for row in rows:
        cells = []
        for key, _ in COLUMNS:
            value = row.get(key)
            cells.append("—" if value is None else str(value))
        lines.append("| " + " | ".join(cells) + " |")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def _roofline(rows: list[dict], config: dict, path: str) -> None:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["experiment"], []).append(row)

    figure, axes = plt.subplots(figsize=(8, 5))
    for name, group in grouped.items():
        rows = [r for r in group if r["decode_tps"] is not None]
        if not rows:
            continue
        rss = sum(r["rss_mb"] for r in group) / len(group)
        decode = sum(r["decode_tps"] for r in rows) / len(rows)
        iqr = sum(r["decode_tps_iqr"] or 0.0 for r in rows) / len(rows)
        axes.errorbar(rss, decode, yerr=iqr / 2, fmt="o", capsize=4, label=name, zorder=3)

    bandwidth = config.get("memory_bandwidth_gbs")
    if bandwidth:
        ceiling_rss = [r["rss_mb"] for r in rows]
        if ceiling_rss:
            low, high = min(ceiling_rss) * 0.9, max(ceiling_rss) * 1.1
            x = [low, high]
            axes.plot(x, [bandwidth * 1000 / mb for mb in x], "--", color="grey", label="bandwidth roofline")

    axes.set(xlabel="Resident memory (MB)", ylabel="Decode throughput (tok/s)", title="Decode roofline")
    axes.grid(alpha=0.3)
    axes.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def generate(config: dict, results_dir: str) -> list[str]:
    rows = _load(results_dir)
    markdown_path = os.path.join(results_dir, "report.md")
    chart_path = os.path.join(results_dir, "roofline.png")
    _markdown(rows, markdown_path)
    _roofline(rows, config, chart_path)
    return [markdown_path, chart_path]
