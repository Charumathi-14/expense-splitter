# SCOPE

## What is implemented

- Backend API with Django and Django REST Framework.
- Login module with token-based authentication.
- Group management and group membership tracking.
- Expense creation and participant share handling.
- Settlement recording with payer and receiver.
- CSV import endpoint with row-level issue detection.
- Balance calculation for groups, including USD conversion and split logic.
- Frontend login page and CSV upload page.

## Known limitations

- Frontend currently includes login and import flow only; additional UI for group and expense management can be built.
- Import uses `created user` informational issues for new row creators.
- Currency conversion uses a fixed USD rate from settings.

## Database schema

- `accounts_user`
- `accounts_authtoken`
- `groups_group`
- `groups_groupmember`
- `expenses_expense`
- `expenses_expenseparticipant`
- `settlements_settlement`
- `imports_importbatch`
- `imports_importissue`
