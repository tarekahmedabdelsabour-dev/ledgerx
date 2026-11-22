LedgerX Assistant is a round icon at the bottom corner of every screen (desktop, CRM and HR). Click it, ask in Arabic or English, and it explains how any page works or builds a report from your data. It can read and explain only: it never creates, changes or deletes anything. It tells you the steps to do that yourself.

## What you can ask

- **How things work**: "How do I create a sales invoice?", "What does the Journal Entry page do?". It answers from this guide.
- **Reports**: "Total sales this month", "Top 10 customers", "Sales per month this year", "Open purchase orders". Answers come as a table in the chat. Use the **Excel** button on a table to download it, and ask for a chart ("as a chart") to see a simple bar, line or pie chart.
- **A record**: "Show invoice SINV-0001".
- **The page you are on**: "Explain this page". The assistant knows which page is open.

## Permissions

The assistant works with your own permissions, exactly like you: your roles, your user permissions and your field-level access. If you ask about something you are not allowed to see, it replies **"This is outside your permissions"** and shows nothing about it. It also does not explain guide pages of modules you do not have. Passwords, keys and tokens are never shown to anyone through it.

## Set up (administrator)

1. Create an API key in the Claude console (console.anthropic.com).
2. Open **LedgerX AI Settings** from the search bar. Paste the key in **Claude API Key** (it is stored encrypted and never shown again), tick **Enabled** and save.
3. Optional: choose the model, the daily question limit per user, the largest table size, a role that may use it, and extra notes about your business.
4. Refresh the page. The icon appears for the users who are allowed.

Every question is recorded in **LedgerX AI Log** (who asked, the question, the answer, the size). Only a System Manager can open it.

## Good to know

- Each question is sent to Claude (Anthropic) together with the parts of your data it needs to answer, and the provider bills the API usage to your key. Do not enable it if your policy forbids sending business data to an external service.
- Check important numbers against the standard reports before you act on them. The assistant can misread a question; it states the filters it used so you can see them.
- If the key is rejected or the server has no internet, the chat says so in one line.
