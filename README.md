# invoice-scanner

Extract structured expense data from invoice/receipt PDFs with an LLM — via a **pluggable backend**. Ships two:

- **`claude`** — shells out to `claude -p` (Claude Code), which reads the PDF with its Read tool. Zero API key wiring if you already use Claude Code.
- **`ollama`** — sends rendered PDF pages to a **local** vision model. Nothing about your expenses leaves the machine.

Amounts stay in the invoice's own currency (no FX conversion — that's the consumer's job). Every extraction carries a `confidence` score and a list of `uncertain_fields`, so a review step can flag the low-confidence ones before they hit a ledger.

## Install

```bash
uv pip install -e .            # claude backend only
uv pip install -e '.[ollama]'  # + local Ollama backend (pulls PyMuPDF)
```

## CLI

```bash
invoice-scan invoice.pdf --backend claude
invoice-scan invoice.pdf --backend ollama --model llama3.2-vision
invoice-scan invoice.pdf --categories software,hosting,office
```

The Ollama backend needs a running daemon and a **vision** model:

```bash
ollama serve
ollama pull llama3.2-vision   # or qwen2.5vl, minicpm-v, ...
```

## Library

```python
from pathlib import Path
from invoice_scanner import extract, get_backend

expense = extract(Path("invoice.pdf"), get_backend("ollama"), categories=["hosting"])
print(expense.model_dump())
```

## Write your own backend

A backend is just `Callable[[Path, str], str]` — `(pdf, instruction) -> raw_model_text`. Register it via an entry point and it's discoverable by name:

```toml
[project.entry-points."invoice_scanner.backends"]
myvendor = "my_pkg.backend:make"
```

The entry point is a `make(model: str | None = None) -> Backend` factory, so `--model` flows through. A `Backend` is `Callable[[Path, str], str]` — `(pdf, instruction) -> raw_model_text`.
