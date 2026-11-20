Point of Sale is a fast screen for shops and cashiers, working directly with inventory and accounts.

## Setting up the cashier

1. Create a **POS Profile** with the Warehouse, Price List, payment methods, and accounts.
2. Specify the users allowed to use it.
3. Open **POS Opening Entry** and enter the opening drawer balance.

## Selling

- Choose Items by touch or with a barcode scanner.
- Add the Customer or sell to a cash Customer.
- Choose the payment method (cash, card, mixed).
- Print the receipt.

## Closing the shift

On closing, the system compares the expected cash with the actual cash and shows the difference, then creates a consolidated invoice of the shift's sales.

## Returns

Open the invoice and create a return, and the Item goes back to the Warehouse and the amount is refunded.

## Item barcodes

The barcode scanner looks the number up in the **Barcodes** table of the Item, so every item you sell needs a barcode recorded.

- Open the **Item Barcodes** page from the Item list (Menu > Item Barcodes) or at `/item-barcodes`.
- Choose an Item Group (or All) and press **Check** to see how many items have no barcode.
- Press **Preview** to see the numbers that would be created without changing anything, then **Create barcodes** to apply them. Each item gets an in-store EAN-13 number starting with 2 (the range reserved for shops, so it never clashes with a manufacturer's barcode), saved in the Item. Up to 1000 items per run, for Stock Managers only.
- **Printing labels:** from the same page choose the size (62x38, 50x30, 40x25 mm or an A4 sheet), the copies and the price list; or select items in the Item list and choose **Print Barcode Labels**; or open one Item and choose **Actions > Print Barcode Label**. The label shows the item name, the barcode and the price.

Notes: an item without a barcode is printed with its item code instead (it works in code search but is not a real barcode). Template items with variants get no barcode, their variants do. A barcode the supplier already gave is never replaced.
