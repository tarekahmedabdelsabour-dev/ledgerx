Manufacturing is a standalone module with its own **Factory** tile on the desktop. It holds production, quality, reports and setup in one place, with barcode scanning for operations, stages and production lines.

## Sections

| Section | Contents |
|---|---|
| Production | Work Orders, Job Cards, Production Plan, BOMs, the operator screen, the scan log |
| Quality | Quality Inspection, Non Conformance, Actions, Goals, Reviews, Feedback, Procedures and Templates |
| Reports | Line Efficiency, Waste, Operator Productivity, Production Cost, and the standard manufacturing reports |
| Setup | Production Lines, Workstations, Operations, Routings, Waste Reasons, Factory Settings |

## Production lines and stations

Create a **Production Line**, add its stations in order and set the target output per hour. Every station and every line gets a barcode automatically.

## Operator screen

Open `/factory` on a phone or a scanner PC:

1. Scan the **employee badge** (employee ID or badge code), then the **station barcode**.
2. Scan the **Job Card**: the required and completed quantities appear.
3. Press **Start**; you can **Pause** and **Resume**.
4. Press **Finish** and enter the good quantity, the scrap and its reason.
5. When the whole quantity is done the Job Card is submitted automatically; if a quality inspection is needed you see why.

Any scanner that types the code and presses Enter works; Chrome on Android can scan with the camera. A code like `ITEM*12` means quantity 12.

## Materials and finished product

Open a **Work Order** by scanning it: scan the raw materials and the system checks they belong to the BOM and do not exceed the required quantity, then press **Post Material Issue**. To receive the product enter the quantity and press **Receive Finished Product**.

## Quality

- Turn on **Quality inspection required** on the operation in the Work Order, or make it a rule for every Job Card in **Factory Settings**.
- The **Quality Check** button on the screen creates the inspection and opens its link.

## Waste and cost

Scrap is recorded with the Job Card and its reason. The **Production Cost** report shows materials, operating cost and the actual unit cost against the BOM cost.

## Printing labels

From a Job Card, Work Order, Workstation, Employee or Item form: **Barcode -> Print Barcode Label**. From a list, select several records and print them together.

> ! Material issue and receipt use the standard Stock Entries, so any rule there (batches, serial numbers, required Job Cards) shows up as it is.
