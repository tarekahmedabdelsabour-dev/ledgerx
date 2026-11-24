The Hospital app runs anything from one small clinic to a group of hospitals on the same stock, accounts, buying and HR as the rest of LedgerX. Find it on the desktop as the **Hospital** tile (route `/desk/hospital`). Nothing is kept twice: a bill creates Sales Invoices, a payment is a Payment Entry, medicines and theatre consumables are Stock Entries, and doctor fees are paid through a Purchase Invoice.

## Set up once

1. **Hospital Settings**: company, price list, bed cut-off hour, follow-up days and fee, the account for rejected insurance claims (optional).
2. **Hospital Branch**: one per hospital or clinic, with its company, cost center, pharmacy and theatre warehouses and price list. Give each user their branches (User Permissions); a user sees only those branches.
3. **Department**, **Ward**, **Hospital Bed** (each bed points at the service charged per day) and **Operating Room**.
4. **Hospital Service**: consultation, procedure, laboratory, radiology, surgery, bed day. Each creates its Item and price. A **Lab Test Template** with the same name as a laboratory service holds its parameters and reference ranges.
5. **Hospital Doctor**: user, supplier (to pay fees), branches, weekly schedule, time off and fee rules.
6. **Hospital Insurer** and **Hospital Insurance Plan** (see Insurance below).

## Front desk

Register the patient in **Hospital Patient**: the national ID gives the birth date and gender, and allergies show as a banner on the patient and the visit. **Patient Appointment** offers the doctor's free slots; **Check In** gives a queue number and posts the consultation fee (a follow-up within the allowed days costs the reduced percentage).

## Clinic

**Start Visit** opens the **Patient Encounter**: complaint, diagnoses, prescriptions, laboratory, radiology and procedure orders. The screen warns about a possible allergy or a duplicate medicine; it never blocks the doctor. **Complete Visit** sends the orders and locks the visit. **Vital Signs** highlights values outside the normal range.

## Inpatients

**Inpatient Admission** puts the patient in an available bed. Use **Transfer**, **Receive Deposit** and **Discharge**. A bed day is charged each time the stay passes the cut-off hour set in the settings; days already charged never change. Nurses add **Nursing Notes** and record **Medication Administration** (given, held, refused; a dose not recorded in two hours becomes Missed).

## Laboratory and radiology

A **Lab Order** has one result sheet per test. **Collect Samples** opens the sheets; the reference range is picked by the patient's age and sex; a critical value alerts the ordering doctor. **Mark Resulted**, then **Verify** locks it. A **Radiology Order** moves Ordered, Scheduled, Performed, Reported, Verified.

## Theatre, emergency and pharmacy

- **Surgery Booking** checks the room and the doctors for clashes, keeps the pre-op checklist and, on **Complete Surgery**, issues the consumables from stock and posts the procedure, team, theatre time and consumables as charges.
- **Emergency Visit**: triage level 1 to 5 sets the colour and the waiting target; the queue shows the sickest and longest waiting first. Assign a doctor, close the visit or **Admit to a Bed**.
- **Medication Dispense** takes batches first-expiry-first-out, issues the Stock Entry and posts the charges. A return is possible while the charge is still unbilled.

## Billing and insurance

Every service becomes a **Hospital Charge** (unbilled). In **Hospital Bill** press **Get Unbilled Charges**: each line is split between the insurer and the patient by the plan (rule for the service, then for the service type, then the general rule; co-pay, caps, annual limit; lines without an approval stay with the patient). **Submit** creates the patient's Sales Invoice (deposits are applied) and the insurer's Sales Invoice; **Receive Payment** creates the Payment Entry. Cancelling the bill cancels both invoices and returns the charges.

An **Insurance Claim** gathers the insurer's bills of a period. **Send Claim**, then **Register Payment** (spread over the oldest invoices first) and **Record Rejection** (written off to the account in the settings).

## Doctor fees

Each doctor has fee rules (percentage or fixed, per service or service type, for cash or insured). A **Doctor Statement** loads the fees of a period, allows a deduction with a note, and **Approve** locks those lines to it. **Create Payable** posts a Purchase Invoice to the doctor's supplier.

## Reports

Daily Census, Bed Occupancy, Revenue Analysis, Unbilled Charges, Insurance Receivable (by age), Appointments Summary, Lab Turnaround, Emergency Waiting Times, Theatre Utilisation, Branch Comparison, Medication Dispensing, Doctor Fees Due.

## Limits

The calculations are covered by automated tests. Run a full day on dummy data and review the first invoices, payments and stock entries before using real patients. The warnings are aids for the clinical team, not diagnoses.
