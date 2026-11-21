The Pharmacy app runs a chain of pharmacies on the same stock, accounts, buying and HR as the rest of LedgerX. Find it on the desktop as the **Pharmacy** tile (route `/desk/pharmacy`). Nothing is kept twice: a sale is a Sales Invoice, a transfer is a Stock Entry, a purchase is a Purchase Order.

## Set up once

1. **Pharmacy Settings**: company, public price list, near-expiry days, whether controlled drugs need a prescription.
2. **Pharmacy Branch**: one per branch, with its sales warehouse, an expired-stock warehouse, cost center, license and manager. Tick **Central Store** for the main store.
3. **Item**: tick **Pharmacy Product**, then fill the class (prescription, OTC, controlled, cosmetic...), active ingredient, strength, form and **Public Price**. The item becomes batch and expiry tracked, and the price is kept in the public price list.
4. Receive stock with a **Purchase Receipt**: each line asks for a batch number and its expiry date.
5. **Insurance Company** (its customer account is created for you) and **Insurance Plan**: the share the insurer pays, the most and least the patient pays, and whether cosmetics are covered.

## Selling: Pharmacy Dispense

Choose the branch and the patient (or leave the walk-in customer), scan or pick the items. The price comes from the public price list and the screen shows the stock, the nearest expiry and a warning when a batch is close to expiry. With an insurance plan the screen shows what the patient pays and what the insurer pays.

When you **Submit**, batches are chosen first-expiry-first-out and an expired batch is never sold. The app creates the **Sales Invoice** (stock out), the **Payment Entry** for what the patient paid and a **Journal Entry** moving the insurer's share to the insurance company's account. Cancelling the dispense cancels all three.

Controlled drugs need the prescription number, the doctor and the patient's national ID. This is checked on every Sales Invoice, so it also protects sales made from the normal POS. Each sale is written to the read-only **Controlled Drug Log**.

## Moving stock: Pharmacy Transfer

- **Branch Transfer**: from one branch to another. **Get Items > Fill from What the Branch Needs** fills what the receiving branch is short of, limited by what the sender can spare.
- **Move to Expired Stock**: moves expired batches to the branch's expired-stock warehouse. **Fill from Expired Batches** lists them.
- **Write Off**: removes the stock against the stock adjustment account.

## Buying: Pharmacy Purchase Plan

Record the **Supplier Offer** of each company: price, discount, minimum quantity, "buy 10 get 1 free", dates. In the **Pharmacy Purchase Plan** choose the receiving store and press **Plan > Load Needs**: stock, orders on the way and the sales of the last days of the chosen branches are counted, and the quantity is rounded up to the pack. For every item the cheapest effective offer (free units counted) is chosen. Untick rows you do not want, then **Create Purchase Orders**: one draft order per supplier.

## Chronic patients: Refill Plan

A refill plan says that a patient takes a medicine every N days. The status (upcoming, due soon, overdue) moves with time, the branch manager gets a daily reminder, and every dispense of that medicine to that patient updates the plan. The **Refills Due** report is the call list.

## Reports

**Expiry Report**, **Drug Alternatives** (same active ingredient, price and stock), **Branch Performance**, **Controlled Drug Register**, **Insurance Receivable** (what each insurer owes, by age) and **Refills Due**.

## Limits

The calculations are covered by automated tests. Review the first invoices, payments and stock entries created by the app before relying on them, and check the insurance journal entry on the insurer's customer account.
