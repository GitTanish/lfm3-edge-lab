"""Single-command entrypoint: profile the matrix, then build the report."""

import argparse
import json
import os

from src.profiler import Profiler
from src.report import generate

ROOT = os.path.dirname(os.path.abspath(__file__))


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=os.path.join(ROOT, "configs/experiments.json"))
    parser.add_argument("--prompts", default=os.path.join(ROOT, "prompts/workloads.json"))
    parser.add_argument("--results", default=os.path.join(ROOT, "results"))
    parser.add_argument("--report-only", action="store_true", help="Rebuild report from existing results.json")
    args = parser.parse_args()

    config = _load(args.config)
    os.makedirs(args.results, exist_ok=True)
    if not args.report_only:
        Profiler(config, _load(args.prompts), args.results).run()
    print("Wrote " + ", ".join(generate(config, args.results)))


if __name__ == "__main__":
    main()
