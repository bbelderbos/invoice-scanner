import base64
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

from invoice_scanner.backends import Backend

DEFAULT_MODEL = os.environ.get("INVOICE_SCANNER_OLLAMA_MODEL", "llama3.2-vision")
DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
_MAX_PAGES = 4


def _pdf_to_png_b64(pdf: Path) -> list[str]:
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise RuntimeError(
            "ollama backend needs PyMuPDF: pip install 'invoice-scanner[ollama]'"
        ) from e
    images = []
    with fitz.open(pdf) as doc:
        for page in doc[:_MAX_PAGES]:
            pix = page.get_pixmap(dpi=150)
            images.append(base64.b64encode(pix.tobytes("png")).decode())
    return images


def make(model: str | None = None) -> Backend:
    model = model or DEFAULT_MODEL

    def run(pdf: Path, instruction: str) -> str:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": instruction, "images": _pdf_to_png_b64(pdf)}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
        req = Request(
            f"{DEFAULT_HOST}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode())
        return body["message"]["content"]

    return run


run = make()
