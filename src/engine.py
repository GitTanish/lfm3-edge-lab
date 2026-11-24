"""llama-server lifecycle, health checks and RSS memory sampling."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request

import psutil


def _http_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _post(url: str, payload: dict, timeout: float = 300.0) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class Engine:
    """One llama-server process for one experiment."""

    def __init__(self, experiment: dict, config: dict, log_dir: str):
        self.experiment = experiment
        self.config = config
        self.port = int(config.get("port", 8080))
        self.log_dir = log_dir
        self.proc: subprocess.Popen | None = None
        self._log = None

    @property
    def base_url(self) -> str:
        return f"http://{self.config.get('host', '127.0.0.1')}:{self.port}"

    def start(self, timeout: float = 180.0) -> "Engine":
        import os

        os.makedirs(self.log_dir, exist_ok=True)
        log_path = os.path.join(self.log_dir, f"{self.experiment['name']}.log")
        self._log = open(log_path, "w", encoding="utf-8")

        cmd = [
            self.config.get("server_bin", "llama-server"),
            "-m", self.experiment["model"],
            "--host", self.config.get("host", "127.0.0.1"),
            "--port", str(self.port),
            "-c", str(self.experiment.get("n_ctx", 4096)),
            "-ngl", str(self.experiment.get("n_gpu_layers", 0)),
        ]
        speculation = self.experiment.get("speculation") or {}
        if speculation.get("enabled"):
            cmd += [
                "--spec-type", speculation.get("method", "ngram-simple"),
                "--spec-draft-n-max", str(speculation.get("num_tokens", 3)),
            ]
            if self.experiment.get("draft_model"):
                cmd += ["-md", self.experiment["draft_model"]]

        self.proc = subprocess.Popen(cmd, stdout=self._log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(f"llama-server exited early; see {log_path}")
            if _http_ok(self.base_url + "/health"):
                return self
            time.sleep(0.5)
        self.stop()
        raise TimeoutError(f"llama-server not healthy after {timeout}s; see {log_path}")

    def complete(self, prompt: str, max_tokens: int = 128) -> dict:
        return _post(
            self.base_url + "/completion",
            {
                "prompt": prompt,
                "n_predict": max_tokens,
                "temperature": 0,
                "stream": False,
                "cache_prompt": False,
                "timings_per_token": True,
            },
        )

    def chat(self, messages: list[dict], max_tokens: int = 160) -> dict:
        return _post(
            self.base_url + "/v1/chat/completions",
            {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0,
                "chat_template_kwargs": {"enable_thinking": False},
                "timings_per_token": True,
            },
        )

    def rss_mb(self) -> float:
        """Resident set of the server and its children, in MB."""
        if self.proc is None:
            return 0.0
        try:
            root = psutil.Process(self.proc.pid)
            procs = [root, *root.children(recursive=True)]
            return sum(p.memory_info().rss for p in procs if p.is_running()) / 1e6
        except psutil.Error:
            return 0.0

    def stop(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        if self._log is not None:
            self._log.close()
            self._log = None
