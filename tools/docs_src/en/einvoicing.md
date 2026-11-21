The E-Invoicing app sends your Sales Invoices to a tax system and keeps the answer on the invoice. Find it on the desktop as the **E-Invoicing** tile (route `/desk/e-invoicing`). It works for **Egypt** (Tax Authority), **Saudi Arabia** (ZATCA / Fatoora), the **UAE** (Peppol through an accredited service provider) and, through a configurable connector, any other system in any country.

## Set up once

1. **E-Invoice Connection**: one per company. Choose the system and the environment (start with Test), and fill the seller block: tax number, commercial register, address. It must match what the authority has on file.
2. On every **Item** set the e-invoice code and type; on every **UOM** the unit code; on the **Customer** the tax number and buyer type.
3. Egypt: client id and secret from the taxpayer portal, the activity code and a signing service for the digital seal. Saudi: press the four onboarding steps. UAE: your provider's address and credentials. Other countries: choose **Custom API** and describe the request.

## Sending

When a Sales Invoice (or a return, which is sent as a credit note) is submitted, the app creates an **E-Invoice Submission** and sends it in the background. The invoice shows the status and the authority's reference. If the system is down the app tries again every 10 minutes. On the invoice, **E-Invoicing > Preview E-Invoice** shows exactly what would be sent, and **Send to the Tax Authority** sends it by hand.

The submission keeps the request and the answer. Statuses: Pending, Submitted (received, waiting for validation), Accepted, Rejected (fix the data and **Send Again**), Failed (technical problem, retried), Cancelled. The report **Unsent E-Invoices** lists invoices that were not accepted yet.

## Cancelling

Egypt: cancelling the invoice cancels it at the authority first (within the period the authority allows). Saudi Arabia and the UAE do not allow cancelling a sent invoice: the app stops the cancel and you issue a credit note.

## Saudi onboarding

On the connection, in order: **1. Generate Certificate Request**, type the one-time code from the portal, **2. Get Compliance Certificate**, **3. Run Compliance Checks**, **4. Get Production Certificate**. Do all of this on Simulation first.

## Important

The app follows the authorities' published specifications and is tested with simulated answers. Run it against each authority's test environment and fix any difference before sending real invoices.
