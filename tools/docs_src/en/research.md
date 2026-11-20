Operations Research is a decision-support module connected to the other apps. It reads your live data (items, BOMs, stock, Work Orders, Sales Orders, Purchase requests, prices) and recommends decisions and analyses questions in thirteen areas. Find it on the desktop as the **Operations Research** tile (route `/desk/operations-research`).

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

After the plan is solved, two more buttons appear:

- **What-if**: fill the table of **Scenarios**. Each row changes a resource, a product margin, a max quantity or a min quantity by a %. Rows with the same scenario name apply together. Each scenario is solved again from scratch and shows the total margin, the change against the current plan and which products change. The same button fills **Can Fall To / Can Rise To** for each bottleneck resource (the range in which the value of one more unit stays valid) and for each product margin (the range in which the plan stays the best).
- **Risk Simulation**: margins and resources vary by the % you choose (300 simulations by default, fixed seed, so the same input gives the same answer). It shows the worst realistic, typical and best realistic total margin, in what % of cases the current plan would still be possible, and the average loss from not re-planning.

Editing scenarios or risk settings does not reset the plan's result.

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

## Analysis plans

These plans answer a question and create no documents. The flow is the common flow above: **Plan > Load Data** where it exists, then **Plan > Solve**, then read **Read before using**.

### Break Even Analysis
Answers: how much must I sell to cover my costs, and how safe is my profit?

- **Fixed costs** table for the period. A row can have an optional **Account** link: **Load Data** fills the amount from the ledger for the same period. Untick **Paid in Cash** for items such as depreciation.
- **Products** table: **Load Data** reads price, cost at sale and quantity from the sales invoices of the history period. The quantities also set the sales mix.
- Also enter the target profit and the capacity.
- Shows: break-even units and revenue, total and per product; units and revenue for the target profit; cash break-even; margin of safety %; operating leverage; profit at expected sales; the chance of a loss and the 5% / typical / 95% profit from a risk simulation (prices, costs and volume vary by the chosen %, 2000 trials, fixed seed so the same input gives the same answer); and a sensitivity table (price, variable cost, fixed costs and volume at +/-10% and +/-20%).
- Limits: variable cost is the stock cost at sale (add direct labour and commissions yourself); a constant sales mix is assumed; costs are linear.

### Investment Analysis
Answers: is this investment worth its cost?

- Enter the cash flows by year (year 0 = now, outflows negative) and the required return. Empty years count as zero.
- Shows: net present value, internal rate of return, payback, discounted payback, profitability index, accept / reject, and optionally the risk (the chance that NPV is negative).
- Note: several sign changes in the cash flows can give several IRRs; rely on the NPV.

### Make or Buy Analysis
Answers: is it cheaper to make the item or to buy it?

- Enter the yearly volume and, for making and for buying, the fixed cost and the cost per unit. **Load Data** reads the default BOM cost and the buying price.
- Shows: the cost of each option, the cheaper option, the saving, and the volume at which both cost the same and which side is cheaper above and below it.

### Lease or Buy Analysis
Answers: is leasing or owning cheaper over the period?

- Enter the purchase price, the value at the end, the yearly running cost, the yearly lease payment, the years and the discount rate.
- Shows: the cost of each option in today's money and the equivalent yearly cost.
- Limits: payments are at year end; no tax or inflation.

### Profitability Analysis
Answers: where do I really make (or lose) money?

- Choose **Item**, **Customer** or **Item Group** and a period.
- Shows: revenue, cost (stock cost at sale), margin, margin %, share of profit and a class: **A** (makes 80% of the profit), **B**, **C**, or **L** (loses money).
- **Check Stock Health** classifies stock as **Dead / Slow / Overstocked / Healthy** from days without movement and days of cover, and shows the money tied up.

### Pricing Analysis
Answers: what is the best price for one item?

- Enter the cost, the current price and the monthly quantity, and the price elasticity. **Load Data** estimates the elasticity from 12 months of sales when the price varied enough, and shows the fit; otherwise enter your own.
- Shows: the best price (constant-elasticity or linear demand model, within your price limits and capacity) and the profit gain. The **discount test** shows the extra volume needed to keep the same profit and the expected profit change.
- Limit: elasticity is assumed constant near today's price.

### Decision Review
Answers: were my earlier plans right?

- It compares earlier plans with what happened: **Reorder Plan** (forecast vs the demand of the next 30 days), **Product Mix Plan** (planned vs produced quantity) and **Supplier Allocation Plan** (planned price vs the Purchase Order price).
- Shows: average error %, bias %, tracking signal and a verdict: **Reliable**, **Usable with a buffer** or **Unreliable**.
- Only plans old enough are checked.

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
- Risk simulations assume independent normal variation of each input; real inputs often move together.
- The review depends on the age of the plans: a recent plan cannot be checked yet.
- Every new analysis states a **Read before using** list: read it before you rely on the result.
> ! The tool supports your decision, it does not replace it: review the draft before you submit it.
