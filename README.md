# invoice-scanner

Extract structured expense data from invoice/receipt PDFs with an LLM — via a **pluggable backend**. Ships two:

- **`claude`** — shells out to `claude -p` (Claude Code), which reads the PDF with its Read tool. Zero API key wiring if you already use Claude Code.
- **`ollama`** — sends rendered PDF pages to a **local** vision model. Nothing about your expenses leaves the machine.

Amounts stay in the invoice's own currency (no FX conversion — that's the consumer's job). Every extraction carries an overall `confidence`, a per-field `field_confidence` and per-field `evidence` (the invoice text each value was read from), so a review step can flag the low-confidence ones before they hit a ledger.

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

Example against a bundled sample:

```bash
$ invoice-scan samples/github_usd.pdf --backend claude
{
  "supplier": "GitHub, Inc.",
  "supplier_tax_id": "",
  "date": "2026-02-15",
  "description": "GitHub Team subscription (1 month)",
  "category": "Software subscription",
  "currency": "USD",
  "net_amount": "40.0",
  "vat_rate": "0.0",
  "payment_method": "card",
  "confidence": 0.95,
  "field_confidence": {"supplier": 0.99, "supplier_tax_id": 0.4, "...": 0.99},
  "evidence": {"supplier": "GitHub, Inc.", "supplier_tax_id": "", "...": "..."}
}
```

## Review (human in the loop)

`--review` puts a human checkpoint between the model and your records. It shows every field with its confidence and source text, prompts only the fields below `--threshold` (default 0.8, least confident first), then lets you edit any other field before accepting. JSON is printed only on accept; `q` (or Ctrl-D) rejects with exit code 1 and no output. Prompts go to stderr, so `invoice-scan x.pdf --review > expense.json` works.

```bash
$ invoice-scan samples/hetzner_eur.pdf --review > expense.json
  supplier         0.99  Hetzner Online GmbH   <- "Hetzner Online GmbH"
  ...
! category         0.65  Hosting
  vat_rate         0.99  0.19   <- "VAT 19%: EUR 2.38"
category [Hosting]: Cloud hosting
Field to edit, Enter to accept, q to reject:
```

Every accepted review is appended to a corrections log (`~/.local/share/invoice-scanner/corrections.jsonl`, override with `--log`): extracted vs final values, which fields were flagged and which you edited. Ask it which fields need the most fixing:

```bash
$ invoice-scan --stats
42 reviews, 11 with edits

field            edits   rate  missed
category             7    17%       2
vat_rate             3     7%       3

missed = edited although the model was confident (not flagged)
```

A high `missed` count means the model is overconfident on that field. Raise `--threshold` or improve the prompt for it.

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
