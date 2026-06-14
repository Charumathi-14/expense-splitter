# AI_USAGE

## Tools used
- Copilot for code generation and repository navigation.
- Terminal and file tools to inspect and modify files.

## Prompts used
- "Build an import endpoint for expenses_export.csv with row-level anomalies."
- "Create a minimal React login page and CSV upload page." 
- "Switch Django local development to SQLite." 

## Errors caught
1. AI suggested importing `ImportIssue` with the wrong relative module path; this was fixed manually.
2. The initial frontend lacked a Vite proxy configuration, which would have made API calls fail from the dev server.
3. The backend settings used PostgreSQL while the repository included `db.sqlite3`; I changed it to SQLite for easier local run.
