Operations Research is a decision-support module connected to the other apps. It reads your live data (items, BOMs, stock, Work Orders, Sales Orders, Purchase requests, prices) and recommends decisions in six areas. Find it on the desktop as the **Operations Research** tile (route `/desk/operations-research`).

## Common flow

1. Create the plan you need and choose the **Company**.
2. From the **Plan** menu press **Load Data**: your data is read into editable tables.
3. Review and edit the numbers as you see fit.
4. From **Plan** press **Solve**.
5. Read the **Result** block: Status, **Independently Verified**, the summary and the **Read before using** list of assumptions and warnings.

If you edit the inputs after solving, the result goes back to **Draft** until you press **Solve** again.

The **Create ... (draft)** buttons create a **draft** document for you to review and submit; nothing is posted automatically. A plan that is not verified cannot create documents, and the status **Needs Attention** asks you to confirm first.

## The six plans

### Product Mix Plan
What to make to maximise total margin under limited materials and workstation hours. You can require **whole units**. The plan shows the **value of one more unit** of each resource; the resource with the highest value is the bottleneck. Draft: **Production Plan**.

### Reorder Plan
Computes the ABC class, economic order quantity, safety stock for the service level you choose, the reorder point, and a next-month forecast. The forecast method is picked by back-test among moving average, exponential smoothing, trend and seasonal. Draft: **Material Request**.

### Distribution Plan
The cheapest shipping of one item from warehouses with stock to warehouses with open transfer requests. Lane costs are entered by hand, or computed as cost per km from Address coordinates. You can block specific lanes, and unmet demand is reported. Draft: **Stock Entry** (Material Transfer).

### Route Plan
Delivery routes from open Sales Orders by vehicle capacity, with the stop order, total km, a lower bound and the % gap. Distance is straight-line, not road distance. This plan creates no draft.

### Schedule Plan
The order of operations of open Work Orders on workstations, with start and end per operation. It takes the best of several dispatch rules and shows a lower bound and the gap. Working days are counted as consecutive calendar days. This plan creates no draft.

### Supplier Allocation Plan
Splits the purchase need across suppliers at least cost, respecting supplier capacity, minimum order, maximum share per supplier, longest lead time, minimum quality score, budget and a cost per extra supplier. If one supplier takes everything, it shows the extra cost if that supplier fails. Draft: **Purchase Orders**, one per supplier.

## Coordinates

**Address** has new fields **Latitude** and **Longitude**. Routes and distribution need them: customers through their address, warehouses through an address linked to the warehouse.

## Roles

**Research Manager** and **Research Analyst**.

## Honest limits

- Results are optimal **for your data and the model**, and the model is a simplification of reality.
- Product mix, supplier allocation and shipping use exact methods.
- Routes and scheduling are strong heuristics that show a lower bound and a gap; this is not a proof of optimality.
- Forecasts are statistical and come with an error warning.
- Wrong input gives wrong output, so always read the **Read before using** list.
- Every result is re-checked by independent code (feasibility, and for linear problems an optimality certificate) before it is called verified.

> ! The tool supports your decision, it does not replace it: review the draft before you submit it.
