# Lucky Strike operations

## Admin operational commands
- `/pending` lists pending manual deposit/withdrawal requests.
- `/approve REQUEST_ID` approves a pending request.
- `/reject REQUEST_ID` rejects a request and refunds a held withdrawal.
- `/backup` creates and sends a database backup.
- `/stats` shows dashboard statistics.

Manual payment remains intentional: the bot does not claim a payment was received until an administrator verifies it.
