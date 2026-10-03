import pymupdf

INVOICES = [
    {
        "file": "hetzner_eur.pdf",
        "lines": [
            "Hetzner Online GmbH",
            "Industriestr. 25, 91710 Gunzenhausen, Germany",
            "VAT ID: DE812871812",
            "",
            "INVOICE  R0012345678",
            "Invoice date: 2026-03-01",
            "",
            "Description: Cloud server CX22 (monthly)",
            "Net amount: EUR 12.50",
            "VAT 19%: EUR 2.38",
            "Total: EUR 14.88",
            "",
            "Paid by credit card.",
        ],
    },
    {
        "file": "github_usd.pdf",
        "lines": [
            "GitHub, Inc.",
            "88 Colin P Kelly Jr St, San Francisco, CA 94107, USA",
            "",
            "Receipt  GH-2026-0042",
            "Date: 2026-02-15",
            "",
            "GitHub Team subscription (1 month)",
            "Amount: USD 40.00",
            "VAT: USD 0.00",
            "Total charged: USD 40.00",
            "",
            "Payment method: card ending 4242",
        ],
    },
    {
        "file": "officesupplies_gbp.pdf",
        "lines": [
            "Ryman Stationery Ltd",
            "203 Oxford Street, London W1D 2LE, United Kingdom",
            "VAT Reg No: GB238049283",
            "",
            "Tax Invoice  INV-8891",
            "Invoice date: 2026-01-09",
            "",
            "Notebooks, pens and printer paper",
            "Net: GBP 34.20",
            "VAT @ 20%: GBP 6.84",
            "Amount due: GBP 41.04",
            "",
            "Paid via bank transfer.",
        ],
    },
    {
        "file": "cowork_ambiguous.pdf",
        "lines": [
            "Maple Desk Co-working",
            "Toronto",
            "",
            "Receipt #551",
            "03/04/26",
            "",
            "Hot desk day pass x2",
            "Subtotal: $40.00",
            "HST: $5.20",
            "Total: $45.20",
            "",
            "Thanks for working with us!",
        ],
    },
]


def main() -> None:
    for inv in INVOICES:
        doc = pymupdf.open()
        page = doc.new_page()
        text = "\n".join(inv["lines"])
        page.insert_text((72, 96), text, fontsize=12, fontname="helv")
        out = f"{__file__.rsplit('/', 1)[0]}/{inv['file']}"
        doc.save(out)
        doc.close()
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
