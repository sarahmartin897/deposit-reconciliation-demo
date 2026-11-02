# Deposit Reconciliation Demo

A working, simplified version of the daily deposit reconciliation I built for a multi-location restaurant group. It matches store cash deposits against bank records, ties late bank adjustments back to the original deposit, and produces a weekly report of open items by store.

> **All data in this repo is made up.** Store names, bag IDs and amounts are fictional. The real process runs on company data that stays private.

📄 **[See the report it produces →](output/weekly_report.md)**

---

## The problem

Every day, each store sends a cash deposit to the bank. Someone has to confirm every deposit actually arrived, and for the right amount. The hard part isn't the daily matching. It's the shortage adjustments the bank posts **days or weeks later**, long after anyone remembers which deposit they belong to.

Done by hand, that meant several spreadsheets, a lot of searching, and open items that were easy to lose track of.

## How it works

1. **Rules first.** The process is written out in plain language in [rules.md](rules.md): how deposits are matched, when a missing credit becomes overdue, and how shortages are handled. The script follows those rules exactly, so results are consistent every run.
2. **Match deposits to bank credits** using the bag ID on each deposit bag. Missing or mismatched credits get flagged.
3. **Tie late adjustments back to the original deposit.** Shortages under $1.00 are written off as change variances (an approved company policy). Shortages of $1.00 or more go to the store to investigate. Adjustments that don't match any deposit are flagged for research.
4. **Build the Monday report** of everything still open, grouped by store, with a Friday cut-off.

## What's in the sample data

The sample covers 5 fictional stores over two weeks (50 deposits) and includes the situations that come up in real life:

| Situation | Example in the data |
|---|---|
| Deposit never credited by the bank | Store 103, Oct 21 |
| Deposit still in transit | Store 104, Oct 30 |
| Bank credited the wrong amount | Store 102, Oct 23 |
| Small shortage written off under policy | Stores 101 and 105 |
| Missing bill sent to the store | Stores 102 and 103 |
| Overage (store sent extra) | Store 104, Oct 22 |
| Bank adjustment with no matching deposit | Bag B109-1015 |

## Files

| File | What it is |
|---|---|
| [rules.md](rules.md) | The reconciliation rules in plain language |
| [reconcile.py](reconcile.py) | The script that runs the reconciliation |
| [data/](data/) | Sample store deposits, bank credits and bank adjustments |
| [output/weekly_report.md](output/weekly_report.md) | The weekly open-items report |
| output/deposit_status.csv | Every deposit with its final status (created when you run the script) |

## Try it yourself

You only need Python installed. No extra packages.

```
python reconcile.py
```

## How I built it

I designed the process and wrote the rules from years of doing this reconciliation by hand, then used AI (Claude) to turn those rules into working code and refine it. The real version runs daily across nine locations and also handles the bank's report formats, a master deposit log and the debit matching against armored car service reports.

---

Part of my [portfolio](https://github.com/sarahmartin897/portfolio) · [LinkedIn](https://www.linkedin.com/in/sarahmartin897)
