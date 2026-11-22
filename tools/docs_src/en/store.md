The Store app is an online store and a website that run on the same stock, prices, customers, orders and invoices as the rest of LedgerX. Find its management screens on the desktop as the **Store** tile (route `/desk/store`). Customers use the public pages: `/store`, `/shop`, `/cart`, `/checkout`, `/my-orders`, `/news`, `/contact-us`.

## Set up once

1. **Store Settings**: store name and colors, the company, the price list, the warehouses that fill online orders, the shipping fee (with its income account), the payment methods and your contact details.
2. **Item Group**: tick *Show in the Online Store* on the categories to show.
3. **Item**: tick *Show in the Online Store* on every product. A product needs a price in the store price list and stock in the chosen warehouses (or *Sell even when out of stock*). Tick *Feature on the Home Page* to put it first.
4. To make the store the home page of the website, tick that option in Store Settings.

## Orders

A customer adds products to the cart and checks out as a guest or signed in. The app creates or reuses the **Customer**, **Contact** and **Address**, then makes a **Sales Order**, and the order page shows its status. Your team gets a task for each new order. From there the normal flow applies: Delivery Note, Sales Invoice, Payment Entry. Prices, stock and tax are checked again on the server when the order is placed, so an old cart cannot sell something that is gone.

## Payment

- **Cash on delivery**.
- **Bank transfer or wallet**: the customer sees your instructions. When the money arrives press **Store > Record Payment** on the Sales Order: it creates the Payment Entry.
- **Online payment** through Paymob: the order is marked paid only when the signed callback arrives and the amount matches. Online orders not paid within 24 hours are marked Failed.

## Pharmacy, cars and rooms

Over-the-counter pharmacy products can be sold; prescription and controlled drugs never are, and expired batches are not counted in stock. Cars (ready for sale) can be shown with a **test drive** request that creates the showroom's Test Drive and a Lead. Hotel rooms can be shown with a **booking request** that creates a Lead; your team confirms availability.

## Website

**Store Page** holds pages you write (about, services, policies) and can show them in the menu. **Store Post** holds the news you write; published posts show under News. The contact form creates a **Store Inquiry** and a lead in the CRM (a CRM Lead when the CRM app is installed).

## Important

The store is tested with simulated data. Place test orders and run a Paymob test payment on a copy of the site before opening it to customers.
