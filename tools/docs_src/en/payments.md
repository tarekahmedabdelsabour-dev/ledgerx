Electronic payments and a network of field agents: wallets, cash custody, commissions, settlements, approvals, and a full audit log.

## How money moves

Company bank ← Manager wallet ← Supervisor wallet ← Agent wallet ← the agent sells a service to the Customer and receives cash ← hands the cash to the supervisor, then to the manager, then to the company treasury.

## Wallet balances

Each wallet has three balances calculated from a transaction log that cannot be edited or deleted:

| Balance | Meaning |
|---|---|
| Available | The balance that services can be sold with |
| Commission | What the agent has earned and not yet settled |
| Cash on hand | What they have collected from Customers and not yet handed over |

## Operations

- **Balance transfer** between wallets according to the chain of command.
- **Selling a service** from the agent's page on mobile, with a PIN.
- **Cash settlement** upon handover.
- **Refund** is a reverse operation that needs a supervisor or manager other than the requester.

## Security

- A balance changes only through the transaction log, with a lock that prevents spending the money twice.
- Repeating a request with the same identifier returns the same result without a second execution.
- A wrong PIN is counted, and the account is locked after the specified number.
- Provider notifications are accepted only with a valid signature.
- Entries created by the module are not cancelled manually; reverse the operation instead.

## Reports

Performance of agents and supervisors, accrued commissions, open custody, and more.
