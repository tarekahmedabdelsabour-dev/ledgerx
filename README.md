# LedgerX

Custom branding and interface layer for ERPNext (Frappe **v16 stable**; v17 develop also works) —
Arabic and English, light and dark.
LedgerX is a separate Frappe app that sits on top of ERPNext, so the ERPNext fork stays
untouched and you can keep merging upstream updates.

**What it changes:** logo and favicon, the color system (primary actions, links, focus,
sidebar, borders, dark mode), the login page, the website/portal header, the browser tab title,
Arabic/RTL typography, and the branding records (Website Settings, Navbar Settings) which it
re-applies after every `bench migrate`.

## Watermark (logo + name)

- **Pages (desk):** a faint, click-through LedgerX logo + name tiled in the background, light and
  dark variants. It never blocks buttons or menus and is hidden when you print a desk page.
  Turn it off by setting `--lx-watermark-image: none;` in `ledgerx/public/css/ledgerx.css`.
- **Printouts and PDFs:** a Print Style called **LedgerX** (a copy of Frappe's default "Redesign" plus the
  watermark) is created on install/migrate and activated if the site is still on the default style.
  It covers the whole sheet on every page. To stop using it: *Print Settings → Print Style*.
  A style you chose yourself is never overwritten.
- Strength and spacing: `tools/make_watermark.py`, then `bench migrate`.

## New bench on the stable version (v16)

Needs Python 3.14 and Node 24+ (the same tools Frappe 17 needs).

```bash
cd ~
bench init --frappe-branch version-16 frappe-bench-v16
cd frappe-bench-v16
bench new-site mysite.localhost
bench get-app erpnext --branch version-16
bench --site mysite.localhost install-app erpnext
```

## Install LedgerX (WSL / bench)

Run these inside your bench folder (the one that already has `erpnext` installed):

```bash
cd ~/frappe-bench

# from GitHub (after you push this folder to a repo)
bench get-app https://github.com/<your-user>/ledgerx

# or from a local folder that is a git repo
bench get-app /path/to/ledgerx

bench --site <your-site> install-app ledgerx
bench --site <your-site> migrate
bench --site <your-site> clear-cache
bench restart        # or just stop/start `bench start`
```

Then hard-refresh the browser (Ctrl+Shift+R). CSS and JS edits after that need only a refresh —
no `bench build`.

## Where to change things

| What | File |
| --- | --- |
| Colors, fonts, radius (desk) | `ledgerx/public/css/ledgerx.css` — the `--lx-*` tokens at the top |
| Login page and website | `ledgerx/public/css/ledgerx_web.css` |
| Logos / favicon | `ledgerx/public/images/` (SVG, plus PNG for emails and print) |
| Names applied to settings records | `ledgerx/install.py` (`BRANDING`) |
| Asset hooks, app name, apps-screen tile | `ledgerx/hooks.py` |
| Arabic strings | `ledgerx/translations/ar.csv` |
| Watermark strength / spacing | `tools/make_watermark.py` (regenerates the SVG tiles and `ledgerx_print.css`) |
| Print watermark rules | `ledgerx/public/css/ledgerx_print.css` (applied by `install.py` on migrate) |

## Palette

| Role | Hex |
| --- | --- |
| Navy (identity, headings) | `#071A3A`, `#0B2A5B` |
| Teal (primary actions, links, focus) | `#0F766E`, `#14B8A6` |
| Gold (accent, the X) | `#F5A524`, `#FFD166` |

## Known limits

- The ERPNext tile on the apps screen keeps ERPNext's own name and logo, because it is declared
  in `erpnext/hooks.py`. To rename it, edit `app_title` and the `logo` entries in your fork's
  `erpnext/hooks.py` (a small, rarely-conflicting change).
- The Cairo/Tajawal fonts are used only if installed on the device; otherwise Arabic falls back to
  Segoe UI / Tahoma. To guarantee the same font everywhere, self-host Cairo under `public/fonts/`.

## نبذة بالعربي

LedgerX تطبيق Frappe منفصل فوق ERPNext بيغيّر الهوية البصرية بالكامل (اللوجو، الألوان، صفحة
الدخول، الوضع الليلي، الخطوط العربية) من غير ما يلمس كود ERPNext الأصلي، فتقدر تحدّث الـ fork
براحتك. خطوات التنصيب على WSL فوق في قسم Install.
