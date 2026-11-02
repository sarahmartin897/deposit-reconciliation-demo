"""
Deposit Reconciliation Demo
---------------------------
Matches store cash deposits against bank records, ties late bank adjustments
back to the original deposit, and produces a weekly open-items report.

All data in the data/ folder is made up for demonstration purposes.
The rules this script follows are written out in plain language in rules.md.

How to run:
    python reconcile.py                      (uses the demo run date)
    python reconcile.py --run-date 2026-11-02

No extra installs needed: this uses only what comes with Python.
"""

import argparse
import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

# ---- Settings (these mirror rules.md) ------------------------------------

CHANGE_VARIANCE_LIMIT = 1.00   # shortages under this amount get written off
DAYS_BEFORE_OVERDUE = 3        # business days to wait for a bank credit
DEMO_RUN_DATE = "2026-11-02"   # a Monday, so the cut-off is Friday Oct 30

DATA = Path(__file__).parent / "data"
OUTPUT = Path(__file__).parent / "output"


# ---- Small helpers --------------------------------------------------------

def read_csv(filename):
    """Read a CSV file into a list of dictionaries (one per row)."""
    with open(DATA / filename, newline="") as f:
        return list(csv.DictReader(f))


def to_date(text):
    return date.fromisoformat(text)


def money(amount):
    return f"${amount:,.2f}"


def business_days_between(start, end):
    """Count weekdays after `start` up to and including `end`."""
    days, current = 0, start
    while current < end:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday to Friday
            days += 1
    return days


def friday_before(run_date):
    """The Friday immediately before the run date (the weekly cut-off)."""
    current = run_date - timedelta(days=1)
    while current.weekday() != 4:  # 4 = Friday
        current -= timedelta(days=1)
    return current


# ---- Step 1: match each deposit to its bank credit ------------------------

def check_credit(deposit, credits_by_bag, run_date):
    """Return (status, needs_action) for the bank credit on one deposit."""
    credit = credits_by_bag.get(deposit["bag_id"])
    declared = float(deposit["declared_amount"])

    if credit is None:
        age = business_days_between(to_date(deposit["deposit_date"]), run_date)
        if age > DAYS_BEFORE_OVERDUE:
            return f"Missing credit ({age} business days old)", True
        return "In transit", True

    credited = float(credit["credit_amount"])
    if round(credited - declared, 2) != 0:
        difference = credited - declared
        direction = "less" if difference < 0 else "more"
        return (f"Credit amount mismatch: bank credited {money(abs(difference))} "
                f"{direction} than declared"), True

    return "Credited in full", False


# ---- Step 2: tie each bank adjustment back to its deposit -----------------

def classify_adjustment(adjustment):
    """Apply the shortage/overage policy to one bank adjustment."""
    amount = float(adjustment["amount"])
    if adjustment["type"] == "Overage adjustment":
        return f"Overage of {money(amount)}: review with store", True
    if amount < CHANGE_VARIANCE_LIMIT:
        return f"Change variance of {money(amount)}: write off", False
    return f"Missing bill ({money(amount)}): store to investigate", True


# ---- Step 3: run everything and build the reports -------------------------

def reconcile(run_date):
    deposits = read_csv("store_deposits.csv")
    credits = read_csv("bank_credits.csv")
    adjustments = read_csv("bank_adjustments.csv")

    credits_by_bag = {c["bag_id"]: c for c in credits}
    deposits_by_bag = {d["bag_id"]: d for d in deposits}

    # Group adjustments by the bag they belong to, and catch any orphans.
    adjustments_by_bag = defaultdict(list)
    unmatched_adjustments = []
    for adj in adjustments:
        if adj["bag_id"] in deposits_by_bag:
            adjustments_by_bag[adj["bag_id"]].append(adj)
        else:
            unmatched_adjustments.append(adj)

    results = []
    for dep in deposits:
        notes = []
        credit_status, needs_action = check_credit(dep, credits_by_bag, run_date)
        notes.append(credit_status)

        for adj in adjustments_by_bag.get(dep["bag_id"], []):
            note, adj_needs_action = classify_adjustment(adj)
            notes.append(f"{note} (posted {adj['posted_date']})")
            needs_action = needs_action or adj_needs_action

        results.append({**dep, "status": "; ".join(notes),
                        "needs_action": "Yes" if needs_action else "No"})

    return results, unmatched_adjustments


def write_status_file(results):
    """Every deposit with its final status, for anyone who wants the detail."""
    OUTPUT.mkdir(exist_ok=True)
    with open(OUTPUT / "deposit_status.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


def write_weekly_report(results, unmatched, run_date):
    """The Monday open-items report, grouped by store."""
    cutoff = friday_before(run_date)
    open_items = [r for r in results
                  if r["needs_action"] == "Yes"
                  and to_date(r["deposit_date"]) <= cutoff]
    write_offs = [r for r in results if "write off" in r["status"]]
    total_declared = sum(float(r["declared_amount"]) for r in results)

    lines = [
        "# Weekly Open Deposits Report",
        "",
        f"**Run date:** {run_date:%A, %B %d, %Y}  ",
        f"**Cut-off:** deposits dated on or before {cutoff:%A, %B %d, %Y}",
        "",
        "## Summary",
        "",
        "| | |",
        "|---|---|",
        f"| Deposits reviewed | {len(results)} ({money(total_declared)}) |",
        f"| Reconciled, no action needed | {sum(r['needs_action'] == 'No' for r in results)} |",
        f"| Open items needing action | {len(open_items)} |",
        f"| Change variances written off | {len(write_offs)} |",
        f"| Bank adjustments with no matching deposit | {len(unmatched)} |",
        "",
        "## Open Items by Store",
        "",
    ]

    by_store = defaultdict(list)
    for item in open_items:
        by_store[f"Store {item['store_number']} – {item['store_name']}"].append(item)

    if not by_store:
        lines.append("No open items. Everything is reconciled.")
    for store in sorted(by_store):
        lines += [f"### {store}", "",
                  "| Deposit date | Bag ID | Declared | Status |",
                  "|---|---|---|---|"]
        for item in by_store[store]:
            lines.append(f"| {item['deposit_date']} | {item['bag_id']} | "
                         f"{money(float(item['declared_amount']))} | {item['status']} |")
        lines.append("")

    if write_offs:
        lines += ["## Written Off Under Policy (no action needed)", "",
                  "| Store | Bag ID | Detail |", "|---|---|---|"]
        for item in write_offs:
            lines.append(f"| {item['store_number']} | {item['bag_id']} | {item['status']} |")
        lines.append("")

    if unmatched:
        lines += ["## Bank Adjustments Needing Research", "",
                  "These could not be tied to any deposit on file.", "",
                  "| Posted | Bag ID on adjustment | Amount | Type |",
                  "|---|---|---|---|"]
        for adj in unmatched:
            lines.append(f"| {adj['posted_date']} | {adj['bag_id']} | "
                         f"{money(float(adj['amount']))} | {adj['type']} |")
        lines.append("")

    (OUTPUT / "weekly_report.md").write_text("\n".join(lines))
    return len(open_items)


def main():
    parser = argparse.ArgumentParser(description="Run the deposit reconciliation.")
    parser.add_argument("--run-date", default=DEMO_RUN_DATE,
                        help="Date to run as, YYYY-MM-DD (default: demo date)")
    run_date = to_date(parser.parse_args().run_date)

    results, unmatched = reconcile(run_date)
    write_status_file(results)
    open_count = write_weekly_report(results, unmatched, run_date)

    print(f"Reconciled {len(results)} deposits as of {run_date}.")
    print(f"{open_count} open items. Report saved to output/weekly_report.md")


if __name__ == "__main__":
    main()
