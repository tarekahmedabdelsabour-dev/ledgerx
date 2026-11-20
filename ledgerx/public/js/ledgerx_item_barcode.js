// Item barcodes: label printing from the Item form and list, and a link to the barcode tools page.
(function () {
	frappe.ui.form.on("Item", {
		refresh(frm) {
			if (frm.is_new()) return;
			frm.add_custom_button(__("Print Barcode Label"), () => window.open("/item-labels?items=" + encodeURIComponent(frm.doc.name) + "&size=62x38", "_blank"), __("Actions"));
		},
	});
	const ls = (frappe.listview_settings["Item"] = frappe.listview_settings["Item"] || {});
	const prev = ls.onload;
	ls.onload = function (listview) {
		if (prev) prev.call(this, listview);
		listview.page.add_action_item(__("Print Barcode Labels"), () => {
			const names = listview.get_checked_items(true);
			if (!names.length) return;
			window.open("/item-labels?items=" + encodeURIComponent(names.join(",")) + "&size=62x38", "_blank");
		});
		listview.page.add_menu_item(__("Item Barcodes"), () => window.open("/item-barcodes", "_blank"));
	};
})();
