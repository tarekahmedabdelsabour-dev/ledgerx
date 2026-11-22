"""LedgerX Assistant: an in-app AI helper that explains the application and answers from live data.

Everything here is read-only and works as the person who asks: data tools go through the same permission
checks the desk uses, so a question about something the user may not open is answered with a refusal.
Only `tools.py` and `client.py` touch the framework or the network; the rest is plain Python and unit-tested.
"""
