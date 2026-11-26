"""Find DocType, Report and Workspace names declared by more than one LedgerX app (their names are global on a site).

Usage:  python3 tools/check_doctype_clashes.py <folder holding the app checkouts or the bench apps folder>
Exit code 1 when a clash exists, so it can run before every release.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ledgerx.shared import doctype_clashes  # noqa: E402


def names_by_app(root):
	out = {}
	for repo in sorted(glob.glob(os.path.join(root, "*"))):
		app = os.path.basename(repo).replace("-", "_")  # a checkout folder and a bench app folder are the same app
		if app in out:
			continue
		if not (app.startswith("ledgerx") or app == "payment_network"):
			continue
		names = set()
		for kind, pat in (("DocType", "doctype"), ("Report", "report"), ("Workspace", "workspace")):
			for f in glob.glob(os.path.join(repo, "**", pat, "*", "*.json"), recursive=True):
				try:
					d = json.load(open(f))
				except Exception:
					continue
				n = d.get("name") if kind != "Report" else d.get("report_name") or d.get("name")
				if n and d.get("doctype") == kind:
					names.add(f"{kind}: {n}")
		out[app] = names
	return out


if __name__ == "__main__":
	root = sys.argv[1] if len(sys.argv) > 1 else "."
	clashes = doctype_clashes(names_by_app(root))
	for name, apps in sorted(clashes.items()):
		print(f"{name}  <-  {', '.join(apps)}")
	print(f"{len(clashes)} clash(es)")
	sys.exit(1 if clashes else 0)
