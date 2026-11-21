The Malls app manages a commercial mall on the same accounts, receivables and customers as the rest of LedgerX. Find it on the desktop as the **Malls** tile (route `/desk/malls`). Nothing is kept twice: rent is a Sales Invoice to the tenant's customer account, and collection is a normal Payment Entry.

## Set up once

1. **Mall Settings**: company, tax template, days until an invoice is due, late fee grace days and percentage, and the billing items (rent, service charge, marketing fund, utilities, turnover rent, expense recovery, late fee). The items are created for you.
2. **Mall**: name, cost center, opening date. Then its **Floors** and **Units** (number, area, category, asking rent). A unit is Vacant, Reserved, Occupied, Fit-out or Maintenance; Occupied and Fit-out follow the lease.
3. **Mall Tenant**: legal name, brand, tax ID, commercial register. A customer account is created for you.

## Leasing: Mall Lease

Pick the tenant and the units, the dates and the **Rent Model**:

- **Fixed Amount per Month** (or per sqm per month),
- **Percentage of Sales**,
- **Higher of Fixed and Percentage**: the percentage rent is billed only for the part above the fixed rent.

Add the yearly rent increase, the service charge, the marketing fund percentage, the deposit and any **Rent-free Periods** (fit-out, incentives). Two leases cannot cover the same unit on the same dates. After **Submit**, use **Terminate** or **Renew** (creates a draft renewal).

## Meters, sales and visitors

- **Utility Meter** and **Meter Reading**: the consumption is read against the previous reading and billed once.
- **Tenant Sales**: monthly gross sales and returns. Sales are **Declared** until a mall manager or accountant marks them **Verified**. Turnover rent is billed only on verified sales.
- **Footfall**: visitors per day or month, to measure sales per visitor.

## Billing: Mall Billing Run

Choose the mall and the month, then **Prepare Charges**: rent (with increases and free periods day by day), service charge, marketing fund, turnover rent of the previous month, unbilled meter readings, expense recovery and late fees. Review and untick lines, then **Create Invoices** (one draft Sales Invoice per lease) and **Submit Invoices**. A lease and month already invoiced is skipped.

## Common-area expenses: CAM Allocation

Enter the expenses to recover (or **Load Expenses** from the mall's accounts). They are shared by area times days in force; vacant space is borne by the landlord unless you untick it.

## Reports

Rent Roll, Occupancy, Tenant Aging, Tenant Sales Performance, Lease Expiry, Footfall and Sales, Billing and Collection. Every day the app updates unit status, reminds about leases ending soon and about tenants who have not reported sales.

## Roles

Mall Manager, Leasing Officer, Mall Accountant, Mall Operations.
