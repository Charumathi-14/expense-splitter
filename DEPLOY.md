Frontend deployment
- The frontend is a Vite React app in the `frontend/` folder. A GitHub Action `deploy-frontend.yml` builds `frontend` and publishes `frontend/dist` to GitHub Pages on push to `main`.

To enable GitHub Pages for the repository:
- In the repository Settings → Pages, set source to `gh-pages` branch (the action will push there).

Backend deployment (recommended options)

1) Render (recommended for simplicity)
- Create a new Web Service on Render, connect your GitHub repo, and select the `backend/` folder as the root (or use a Dockerfile).
- Set the build command: `pip install -r requirements.txt && python manage.py migrate --noinput` (adjust for your environment)
- Set the start command: `gunicorn expense_manager.wsgi:application --bind 0.0.0.0:$PORT`
- Add environment variables: `DEBUG=False`, `SECRET_KEY`, database config if using managed DB, etc.

2) Heroku (alternative)
- Create a `Procfile` with: `web: gunicorn expense_manager.wsgi:application`
- Ensure `requirements.txt` exists and a `runtime.txt` if needed.
- Use `git push heroku main` to deploy.

3) Docker (portable)
- Create a Dockerfile that installs Python dependencies, collects static files, runs migrations, and starts Gunicorn. Deploy the image to any container service (AWS ECS, GCP Cloud Run, Render, etc.).

Notes
- You will need to ensure static files are served (collectstatic + a static file host or via the web server).
- The GitHub Actions created here publishes only the static frontend to GitHub Pages. Backend requires a hosting service as above.
