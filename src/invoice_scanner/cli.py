import argparse
import sys
from pathlib import Path

from invoice_scanner.backends import get_backend
from invoice_scanner.corrections import DEFAULT_LOG, log_review, read_log, render_stats
from invoice_scanner.extract import extract
from invoice_scanner.review import DEFAULT_THRESHOLD, flagged_fields, review


def _ask(prompt: str) -> str:
    # Prompts go to stderr so stdout stays clean JSON for piping.
    print(prompt, end="", file=sys.stderr, flush=True)
    line = sys.stdin.readline()
    if not line:
        raise EOFError
    return line


def _show(text: str) -> None:
    print(text, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract structured expense data from a PDF.")
    parser.add_argument("pdf", type=Path, nargs="?", help="path to the invoice/receipt PDF")
    parser.add_argument("--backend", default="claude", help="backend name (claude, ollama, ...)")
    parser.add_argument("--model", default=None, help="model override for the backend")
    parser.add_argument("--categories", default=None, help="comma-separated allowed categories")
    parser.add_argument(
        "--review", action="store_true", help="confirm/edit fields before output; logs corrections"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"review prompts fields below this confidence (default {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--log", type=Path, default=DEFAULT_LOG, help=f"corrections log (default {DEFAULT_LOG})"
    )
    parser.add_argument(
        "--stats", action="store_true", help="show which fields get corrected most, then exit"
    )
    args = parser.parse_args()

    if args.stats:
        print(render_stats(read_log(args.log)))
        return 0
    if args.pdf is None:
        parser.error("pdf is required unless --stats is given")
    if not args.pdf.is_file():
        print(f"not a file: {args.pdf}", file=sys.stderr)
        return 2

    categories = [c.strip() for c in args.categories.split(",")] if args.categories else None
    backend = get_backend(args.backend, args.model)
    expense = extract(args.pdf, backend, categories)

    if args.review:
        try:
            final = review(expense, _ask, _show, args.threshold)
        except (EOFError, KeyboardInterrupt):
            final = None
        if final is None:
            print("\nrejected, nothing written", file=sys.stderr)
            return 1
        log_review(
            args.log,
            pdf=args.pdf,
            backend=args.backend,
            model=args.model,
            extracted=expense,
            final=final,
            flagged=flagged_fields(expense, args.threshold),
        )
        expense = final

    print(expense.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
