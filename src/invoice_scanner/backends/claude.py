import shutil
import subprocess
from pathlib import Path

from invoice_scanner.backends import Backend


def _claude_bin() -> str:
    return shutil.which("claude") or "claude"


def make(model: str | None = None) -> Backend:
    def run(pdf: Path, instruction: str) -> str:
        cmd = [_claude_bin(), "-p", "--allowedTools", "Read"]
        if model:
            cmd += ["--model", model]
        prompt = f"Read the PDF at {pdf}.\n{instruction}"
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"claude -p failed ({proc.returncode}): {proc.stderr.strip()}")
        return proc.stdout

    return run


run = make()
