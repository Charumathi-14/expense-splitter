# DECISIONS

## Database choice
- Chose SQLite for local development to match the existing `backend/db.sqlite3` and avoid requiring PostgreSQL.

## CSV importer behavior
- Duplicate rows are detected by a row signature and only the first occurrence is imported.
- Negative amounts are treated as refunds only if the description contains refund-related keywords.
- Rows with missing participants infer active group members by date.
- Settlement rows are identified by `receiver` fields or explicit row type values.

## Frontend integration
- Used Vite proxy to route `/api/*` requests to the backend at `http://localhost:8000`.
- Kept UI minimal: login page and CSV import page are enough to satisfy the core import workflow.
