# Reconciliation Rules

These are the standing rules the reconciliation follows every time it runs. Writing them down was the first and most important step of this project: once the rules existed in plain language, they could be turned into a repeatable process.

## 1. Match every deposit to a bank credit
- Each store deposit is matched to the bank's credit using the **bag ID** printed on the deposit bag.
- The bank's credit should equal the amount the store declared. If it doesn't, the deposit is flagged as a **credit amount mismatch** so it can be raised with the bank.

## 2. Deposits with no bank credit
- If a deposit is **more than 3 business days old** and still has no credit, it is flagged as **missing (overdue)** and needs to be followed up with the bank or armored car service.
- If it is 3 business days old or less, it is **in transit** and simply stays on the open list.

## 3. Tie every late bank adjustment back to its deposit
Banks often post shortage or overage adjustments days or weeks after the original deposit. Every adjustment is tied back to the original deposit using its bag ID.
- **Shortage under $1.00:** treated as a **change variance** and written off. (This threshold was proposed and approved as company policy.)
- **Shortage of $1.00 or more:** treated as a **missing bill** and sent to the store manager to investigate.
- **Overage:** the store sent more than it declared. Noted for review with the store.
- **No matching deposit:** the adjustment can't be tied to any bag on file and needs research.

## 4. Weekly open-items report
- Run every Monday after the daily reconciliation.
- The cut-off is the **Friday immediately before** the run date.
- Lists every deposit dated on or before the cut-off that still needs action, grouped by store.
