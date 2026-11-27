"""Demo foundation: a parent company with subsidiaries in Egypt, Saudi Arabia and the UAE, each with branches
(cost center + warehouse), departments and employees, plus customers, suppliers and items.

    bench --site mysite.localhost execute ledgerx.demo.foundation.run

Take a backup first (bench --site mysite.localhost backup --with-files). Restoring that backup is how the demo is removed.
Idempotent: running again adds only what is missing. Every step commits on its own and reports its result."""
import frappe
from frappe.utils import add_days, add_years, nowdate

from ledgerx.shared import run_each

GROUP = ("LedgerX Group", "LXG", "EGP", "Egypt")
COUNTRIES = [
	# company, abbr, currency, country, rate to EGP, territory, branches
	("LedgerX Egypt", "LXE", "EGP", "Egypt", 1.0, "Egypt", ["Cairo", "Alexandria", "Giza"]),
	("LedgerX Saudi", "LXS", "SAR", "Saudi Arabia", 13.0, "Saudi Arabia", ["Riyadh", "Jeddah", "Dammam"]),
	("LedgerX UAE", "LXA", "AED", "United Arab Emirates", 13.3, "United Arab Emirates", ["Dubai", "Abu Dhabi"]),
]
DEPARTMENTS = ["Sales", "Accounts", "Operations", "HR"]
DESIGNATIONS = ["Branch Manager", "Accountant", "Sales Executive", "Storekeeper", "Receptionist"]
FIRST = {"Egypt": ["Ahmed", "Mohamed", "Mona", "Sara", "Omar", "Heba", "Khaled", "Nour"],
	"Saudi Arabia": ["Faisal", "Abdullah", "Noura", "Reem", "Salman", "Lama", "Fahad", "Dana"],
	"United Arab Emirates": ["Hamad", "Rashid", "Mariam", "Latifa", "Saeed", "Aisha", "Majid", "Shamma"]}
LAST = ["Hassan", "Ali", "Ibrahim", "Saleh", "Mansour", "Nasser", "Farouk", "Khalil"]
ITEMS = [("LX-LAPTOP", "Laptop 15 inch", 18000), ("LX-PRINTER", "Office Printer", 6500), ("LX-DESK", "Office Desk", 3200), ("LX-CHAIR", "Office Chair", 1800),
	("LX-PAPER", "Paper Box A4", 250), ("LX-INK", "Ink Cartridge", 420)]
CUSTOMERS = ["Delta Trading", "Nile Retail", "Gulf Supplies", "Pearl Hospitality", "Horizon Clinics", "Sunrise Schools", "Atlas Motors", "Palm Real Estate"]
SUPPLIERS = ["Prime Distribution", "Orient Imports", "Metro Wholesale", "Sahara Logistics"]


def _say(msg):
	print(msg)


def _company(row):
	name, abbr, cur, country = row[:4]
	if frappe.db.exists("Company", name):
		return
	d = {"doctype": "Company", "company_name": name, "abbr": abbr, "default_currency": cur, "country": country,
		"create_chart_of_accounts_based_on": "Standard Template", "chart_of_accounts": "Standard with Numbers"}
	if name == GROUP[0]:
		d["is_group"] = 1
	else:
		d["parent_company"] = GROUP[0]
	frappe.get_doc(d).insert(ignore_permissions=True)


def _currency(row):
	_n, _a, cur, _c, rate = row[:5]
	if cur == "EGP" or frappe.db.exists("Currency Exchange", {"from_currency": cur, "to_currency": "EGP", "date": nowdate()}):
		return
	if frappe.db.exists("Currency", cur):
		frappe.db.set_value("Currency", cur, "enabled", 1)
	frappe.get_doc({"doctype": "Currency Exchange", "date": nowdate(), "from_currency": cur, "to_currency": "EGP", "exchange_rate": rate}).insert(ignore_permissions=True)
	frappe.get_doc({"doctype": "Currency Exchange", "date": nowdate(), "from_currency": "EGP", "to_currency": cur, "exchange_rate": round(1 / rate, 6)}).insert(ignore_permissions=True)


def _lookups(_x):
	for d in DESIGNATIONS:
		if not frappe.db.exists("Designation", d):
			frappe.get_doc({"doctype": "Designation", "designation_name": d}).insert(ignore_permissions=True)
	for t in [c[5] for c in COUNTRIES]:
		if not frappe.db.exists("Territory", t):
			frappe.get_doc({"doctype": "Territory", "territory_name": t, "parent_territory": "All Territories"}).insert(ignore_permissions=True)
	for g in ("Commercial",):
		if not frappe.db.exists("Customer Group", g):
			frappe.get_doc({"doctype": "Customer Group", "customer_group_name": g, "parent_customer_group": "All Customer Groups"}).insert(ignore_permissions=True)
	for g in ("Distributor",):
		if not frappe.db.exists("Supplier Group", g):
			frappe.get_doc({"doctype": "Supplier Group", "supplier_group_name": g, "parent_supplier_group": "All Supplier Groups"}).insert(ignore_permissions=True)
	if not frappe.db.exists("Item Group", "Demo Goods"):
		frappe.get_doc({"doctype": "Item Group", "item_group_name": "Demo Goods", "parent_item_group": "All Item Groups"}).insert(ignore_permissions=True)


def _branches(row):
	"""Branch records (HR), a cost center and a warehouse per branch, departments per company."""
	name, abbr, _cur, _country, _rate, _terr, branches = row
	for dpt in DEPARTMENTS:
		if not frappe.db.exists("Department", f"{dpt} - {abbr}"):
			frappe.get_doc({"doctype": "Department", "department_name": dpt, "company": name, "parent_department": "All Departments"}).insert(ignore_permissions=True)
	root_cc = frappe.db.get_value("Cost Center", {"company": name, "is_group": 1, "parent_cost_center": ["in", ["", None]]}, "name")
	for b in branches:
		if not frappe.db.exists("Branch", f"{b} ({abbr})"):
			frappe.get_doc({"doctype": "Branch", "branch": f"{b} ({abbr})"}).insert(ignore_permissions=True)
		if not frappe.db.exists("Cost Center", f"{b} - {abbr}"):
			frappe.get_doc({"doctype": "Cost Center", "cost_center_name": b, "company": name, "parent_cost_center": root_cc, "is_group": 0}).insert(ignore_permissions=True)
		if not frappe.db.exists("Warehouse", f"{b} Store - {abbr}"):
			frappe.get_doc({"doctype": "Warehouse", "warehouse_name": f"{b} Store", "company": name}).insert(ignore_permissions=True)


def _employees(row):
	name, abbr, _cur, country, _rate, _terr, branches = row
	firsts = FIRST[country]
	i = 0
	for b in branches:
		for n in range(3):
			i += 1
			first, last = firsts[(i + n) % len(firsts)], LAST[(i * 3 + n) % len(LAST)]
			full = f"{first} {last}"
			if frappe.db.exists("Employee", {"employee_name": full, "company": name}):
				continue
			frappe.get_doc({"doctype": "Employee", "first_name": first, "last_name": last, "gender": "Female" if first in ("Mona", "Sara", "Heba", "Nour", "Noura", "Reem", "Lama", "Dana", "Mariam", "Latifa", "Aisha", "Shamma") else "Male",
				"date_of_birth": add_years(nowdate(), -(25 + (i * 2) % 15)), "date_of_joining": add_days(nowdate(), -(200 + i * 20)), "company": name,
				"branch": f"{b} ({abbr})", "department": f"{DEPARTMENTS[i % len(DEPARTMENTS)]} - {abbr}", "designation": DESIGNATIONS[0] if n == 0 else DESIGNATIONS[1 + (i + n) % (len(DESIGNATIONS) - 1)],
				"status": "Active"}).insert(ignore_permissions=True)


def _masters(_x):
	for code, title, price in ITEMS:
		if not frappe.db.exists("Item", code):
			frappe.get_doc({"doctype": "Item", "item_code": code, "item_name": title, "item_group": "Demo Goods", "stock_uom": "Nos", "is_stock_item": 1,
				"standard_rate": price, "valuation_rate": round(price * 0.7, 2)}).insert(ignore_permissions=True)
	for i, c in enumerate(CUSTOMERS):
		if not frappe.db.exists("Customer", c):
			frappe.get_doc({"doctype": "Customer", "customer_name": c, "customer_type": "Company", "customer_group": "Commercial", "territory": COUNTRIES[i % 3][5]}).insert(ignore_permissions=True)
	for s in SUPPLIERS:
		if not frappe.db.exists("Supplier", s):
			frappe.get_doc({"doctype": "Supplier", "supplier_name": s, "supplier_group": "Distributor", "supplier_type": "Company"}).insert(ignore_permissions=True)


def run():
	_say("Foundation demo data")
	steps = []
	for label, fn, items in (("Group company", _company, [GROUP + (1.0, "", [])]), ("Subsidiary companies", _company, COUNTRIES), ("Exchange rates", _currency, COUNTRIES),
		("Groups and designations", _lookups, [1]), ("Branches, cost centers, warehouses", _branches, COUNTRIES), ("Employees", _employees, COUNTRIES), ("Items, customers, suppliers", _masters, [1])):
		done, failed = run_each(items, fn, f"Demo foundation: {label}")
		steps.append((label, len(done), len(failed)))
		_say(f"  {label}: {len(done)} ok, {len(failed)} failed")
	if any(f for _l, _d, f in steps):
		_say("Some steps failed. Open Error Log (titles start with 'Demo foundation') and send me the errors.")
	else:
		_say("Done. Next: the module demo data.")
