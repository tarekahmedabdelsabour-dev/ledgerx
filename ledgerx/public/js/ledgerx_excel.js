// Excel and CSV everywhere.
//
// - Every template / export dialog that offers a file type opens on "Excel".
// - Every place that downloads a table as CSV (child-table "Download", chart export, ...) asks
//   "Excel or CSV" and defaults to Excel.
// - Every upload box that accepts only CSV also accepts an Excel (.xlsx) file. Files that the
//   browser reads itself are converted by the server (ledgerx.api.excel); files that go to the
//   server are read by it directly (ledgerx/excel_compat.py).
// Nothing is removed: CSV keeps working exactly as before.
(function () {
	"use strict";

	function when(test, fn, tries) {
		var n = 0;
		(function tick() {
			var v;
			try { v = test(); } catch (e) { v = null; }
			if (v) return fn(v);
			if (++n < (tries || 400)) setTimeout(tick, 100);
		})();
	}

	function saveBlob(blob, name) {
		var a = document.createElement("a");
		a.href = URL.createObjectURL(blob);
		a.download = name;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		setTimeout(function () { URL.revokeObjectURL(a.href); }, 5000);
	}

	function b64ToBlob(b64, type) {
		var bin = atob(b64), bytes = new Uint8Array(bin.length);
		for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
		return new Blob([bytes], { type: type });
	}

	var XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

	// 1. Template / export dialogs open on Excel (Data Import "Download Template", bulk edit, ...)
	when(function () {
		return frappe.data_import && frappe.data_import.DataExporter && frappe.data_import.DataExporter.prototype;
	}, function (proto) {
		if (proto.__lx_excel) return;
		var orig = proto.make_dialog;
		proto.make_dialog = function (filetype) {
			return orig.call(this, filetype || "Excel");
		};
		proto.__lx_excel = true;
	});

	// 2. Table downloads: Excel or CSV
	when(function () {
		return frappe.tools && frappe.tools.downloadify;
	}, function (orig) {
		if (orig.__lx_excel) return;
		var wrapped = function (data, roles, title) {
			var args = arguments, self = this;
			if (roles && roles.length) return orig.apply(self, args); // permission message stays as it was
			var d = new frappe.ui.Dialog({
				title: __("Download"),
				fields: [{
					fieldtype: "Select", fieldname: "file_type", label: __("File Type"),
					options: ["Excel", "CSV"], default: "Excel",
				}],
				primary_action_label: __("Download"),
				primary_action: function (v) {
					d.hide();
					if (v.file_type === "CSV") return orig.apply(self, args);
					frappe.call({
						method: "ledgerx.api.excel.rows_to_xlsx",
						type: "POST",
						args: { rows: JSON.stringify(data), sheet_name: title || "Sheet1" },
						freeze: true,
					}).then(function (r) {
						if (r && r.message) saveBlob(b64ToBlob(r.message, XLSX_TYPE), (title || "export") + ".xlsx");
					});
				},
			});
			d.show();
		};
		wrapped.__lx_excel = true;
		frappe.tools.downloadify = wrapped;
	});

	// 3. Upload boxes that only accept CSV also accept .xlsx
	var CSV = /(^|\.)csv$/i, XLSX = /xlsx$/i;
	when(function () {
		return frappe.ui && frappe.ui.FileUploader;
	}, function (Orig) {
		if (Orig.__lx_excel) return;

		function prepare(opts) {
			var r = opts && opts.restrictions, t = r && r.allowed_file_types;
			if (!t || !t.some(function (x) { return CSV.test(x); }) || t.some(function (x) { return XLSX.test(x); })) return opts;
			var o = Object.assign({}, opts, {
				restrictions: Object.assign({}, r, { allowed_file_types: t.concat([".xlsx"]) }),
			});
			if (o.as_dataurl && typeof o.on_success === "function") {
				var ok = o.on_success;
				o.on_success = function (file) {
					var self = this, args = arguments;
					if (file && XLSX.test(file.name || file.file_name || "") && file.dataurl) {
						frappe.call({
							method: "ledgerx.api.excel.xlsx_to_csv_dataurl",
							type: "POST",
							args: { dataurl: file.dataurl },
							freeze: true,
							freeze_message: __("Reading the Excel file..."),
						}).then(function (r) {
							if (!r || !r.message) return;
							file.dataurl = r.message;
							ok.apply(self, args);
						});
					} else {
						ok.apply(self, args);
					}
				};
			}
			return o;
		}

		var Wrapped = class extends Orig {
			constructor(opts) { super(prepare(opts)); }
		};
		Wrapped.UploadOptions = Orig.UploadOptions;
		Wrapped.__lx_excel = true;
		frappe.ui.FileUploader = Wrapped;
	});
})();
