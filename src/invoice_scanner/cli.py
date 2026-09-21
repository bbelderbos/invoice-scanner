import argparse
import sys
from pathlib import Path

from invoice_scanner.backends import get_backend
from invoice_scanner.extract import extract


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract structured expense data from a PDF.")
    parser.add_argument("pdf", type=Path, help="path to the invoice/receipt PDF")
    parser.add_argument("--backend", default="claude", help="backend name (claude, ollama, ...)")
    parser.add_argument("--model", default=None, help="model override for the backend")
    parser.add_argument("--categories", default=None, help="comma-separated allowed categories")
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"not a file: {args.pdf}", file=sys.stderr)
        return 2

    categories = [c.strip() for c in args.categories.split(",")] if args.categories else None
    backend = get_backend(args.backend, args.model)
    expense = extract(args.pdf, backend, categories)
    print(expense.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
